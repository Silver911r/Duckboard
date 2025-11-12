from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton,
    QFileDialog, QLabel, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
from pathlib import Path

from src.database.duckdb_manager import DuckDBManager

class FileBrowser(QWidget):
    """panel for browsing and loading data"""
    def __init__(self, db_manager: DuckDBManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._init_ui()
    
    def _init_ui(self):
        """init the ui"""
        layout = QVBoxLayout(self)

        #title
        title = QLabel("Data Sources")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(title)

        #file button
        self.add_file_btn = QPushButton("Add a file...")
        self.add_file_btn.clicked.connect(self._add_file)
        layout.addWidget(self.add_file_btn)

        #loaded table list
        self.tables_list = QListWidget()
        self.tables_list.itemDoubleClicked.connect(self._show_table_info)
        layout.addWidget(self.tables_list)

        #info label
        self.info_label = QLabel("No tables loaded")
        self.info_label.setStyleSheet("font-size: 11px; color: #888; padding: 5px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

    def _add_file(self):
        """open file dialog to add data"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Data File",
            "",
            "Data Files (*.csv *.parquet *.arrow *csv.gz);; CSV Files (*.csv);; Parquet Files (*.parquet);;Arrow Files (*.arrow);;CSV Compressed (*.csv.gz)"
        )

        if file_path:
            try:
                table_name = self.db_manager.load_file(file_path)
                self._refresh_tables_list()
                self.parent().status_bar.showMessage(f"Loaded {table_name} from {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error Loading File", str(e))

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