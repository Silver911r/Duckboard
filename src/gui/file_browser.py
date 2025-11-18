from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QListWidget, QPushButton,
    QFileDialog, QLabel, QListWidgetItem, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from pathlib import Path

from src.database.duckdb_manager import DuckDBManager
from src.gui.dialogs.add_source import AddSourceDialog

class FileLoaderThread(QThread):
    """background thread for loading files without blocking UI"""
    finished = Signal(str)  # table_name
    error = Signal(str)  # error message

    def __init__(self, db_manager, file_path, table_name):
        super().__init__()
        self.db_manager = db_manager
        self.file_path = file_path
        self.table_name = table_name

    def run(self):
        """load file in background"""
        try:
            table_name = self.db_manager.load_file(self.file_path, self.table_name)
            self.finished.emit(table_name)
        except Exception as e:
            self.error.emit(str(e))

class FileBrowser(QWidget):
    """panel for browsing and loading data"""
    def __init__(self, db_manager: DuckDBManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.loader_thread = None
        self._init_ui()
    
    def _init_ui(self):
        """init the ui"""
        layout = QVBoxLayout(self)

        #title
        title = QLabel("Data Sources")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(title)

        #file button
        self.add_data_btn = QPushButton("Add Data Source...")
        self.add_data_btn.clicked.connect(self._add_data_source)
        layout.addWidget(self.add_data_btn)

        #loaded table list
        self.tables_list = QListWidget()
        self.tables_list.itemDoubleClicked.connect(self._show_table_info)
        layout.addWidget(self.tables_list)

        #info label
        self.info_label = QLabel("No tables loaded")
        self.info_label.setStyleSheet("font-size: 11px; color: #888; padding: 5px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

    def _add_data_source(self):
        """show dialog to choose data source type"""
        #create the dialog
        dialog = AddSourceDialog(self)
        result = dialog.exec()

        #check if loading file or url
        if result == QDialog.DialogCode.Accepted:
            #check which option they choes
            if dialog.source_type == 'file':
                self._add_file()
            elif dialog.source_type == 'url':
                self._add_url()

    def _add_url(self):
        """prompt user for url and load csv from it"""
        url, ok = QInputDialog.getText(
            self,
            "Load CSV from URL",
            "Enter CSV URL (http:// or https://):",
            text="https://"
        )

        if ok and url:
            #basic validation
            if not (url.startswith('http://') or url.startswith('https://')):
                QMessageBox.warning(self, 'Invalid URL', 'URL must start with http:// or https://')
                return
            
            #prompt user for table name
            #generate default table name from url
            default_name =  "url_data"
            table_name, ok = QInputDialog.getText(
                self,
                "Table Name",
                "Enter a name for this table:",
                text=default_name
            )

            if ok and table_name:
                self.add_data_btn.setEnabled(False)
                self.window().status_bar.showMessage(f"Loading {url}...")
                # load file in background thread
                self.loader_thread = FileLoaderThread(self.db_manager, url, table_name)
                self.loader_thread.finished.connect(self._on_file_loaded)
                self.loader_thread.error.connect(self._on_load_error)
                self.loader_thread.start()

    def _add_file(self):
        """prompt user for file and load"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Data File",
            "",
            "Data Files (*.csv *.parquet *.arrow *csv.gz);; CSV Files (*.csv);; Parquet Files (*.parquet);;Arrow Files (*.arrow);;CSV Compressed (*.csv.gz)"
        )

        if file_path:
            # generate default table name from filename
            path = Path(file_path)
            # handle double extensions like .csv.gz
            name = path.name
            # remove .gz if present
            if name.endswith('.gz'):
                name = name[:-3]
            # remove data file extensions
            for ext in ['.csv', '.parquet', '.arrow']:
                if name.endswith(ext):
                    name = name[:-len(ext)]
                    break
            # sanitize name
            default_name = name.replace(" ", "_").replace("-", "_")

            # prompt user for table name
            table_name, ok = QInputDialog.getText(
                self,
                "Table Name",
                "Enter a name for this table:",
                text=default_name
            )

            if ok and table_name:
                # disable button during loading
                self.add_data_btn.setEnabled(False)
                self.window().status_bar.showMessage(f"Loading {Path(file_path).name}...")

                # load file in background thread
                self.loader_thread = FileLoaderThread(self.db_manager, file_path, table_name)
                self.loader_thread.finished.connect(self._on_file_loaded)
                self.loader_thread.error.connect(self._on_load_error)
                self.loader_thread.start()

    def _on_file_loaded(self, table_name):
        """handle successful file load"""
        self._refresh_tables_list()
        self.window().status_bar.showMessage(f"Loaded {table_name}")
        self.add_data_btn.setEnabled(True)
        self.loader_thread = None

    def _on_load_error(self, error_msg):
        """handle file load error"""
        QMessageBox.critical(self, "Error Loading File", error_msg)
        self.window().status_bar.showMessage("Load failed")
        self.add_data_btn.setEnabled(True)
        self.loader_thread = None

    def _refresh_tables_list(self):
        """refresh the list of tables"""
        self.tables_list.clear()
        tables = self.db_manager.list_tables()

        for table_name in tables:
            item = QListWidgetItem(table_name)
            item.setToolTip(f"Double-click to view schema")
            self.tables_list.addItem(item)

        #update info label
        if tables:
            self.info_label.setText(f"{len(tables)} table(s) loaded")
        else:
            self.info_label.setText("No tables loaded")

    def _show_table_info(self, item: QListWidgetItem):
        """show table schema info"""
        table_name = item.text()

        try:
            stats = self.db_manager.get_table_stats(table_name)

            info_text = f"Table: {table_name}\n\n"
            info_text += f"Rows: {stats['row_count']:,}\n"
            info_text += f"Columns: {stats['column_count']}\n\n"
            info_text += "Schema:\n"

            for col_name, col_type in stats['columns']:
                info_text += f" . {col_name}: {col_type}\n"

            QMessageBox.information(self, f"Table Info: {table_name}", info_text)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not retrieve table info: {str(e)}")