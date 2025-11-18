from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QLabel, QListWidget, QSplitter, QMessageBox,
    QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont
import time

from src.database.duckdb_manager import DuckDBManager

class QueryExecutorThread(QThread):
    """background thread for executing queries without blocking UI"""
    finished = Signal(object, float)  # result, execution_time
    error = Signal(str)  # error message

    def __init__(self, db_manager, query):
        super().__init__()
        self.db_manager = db_manager
        self.query = query

    def run(self):
        """execute query in background"""
        try:
            start_time = time.time()
            result = self.db_manager.execute_query(self.query)
            execution_time = time.time() - start_time
            self.finished.emit(result, execution_time)
        except Exception as e:
            self.error.emit(str(e))

class QueryEditor(QWidget):
    """sql query editor with history."""
    query_executed = Signal(object, float) # result, execution_time

    def __init__(self, db_manager: DuckDBManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.query_history = []
        self.current_font_size = 11
        self.query_thread = None
        self._init_ui()

    def _init_ui(self):
        "init the ui"
        layout = QVBoxLayout(self)

        #create splitter for editor and history
        splitter = QSplitter(Qt.Horizontal)

        #left side - query editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)

        #title
        title = QLabel("SQL Query Editor")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        editor_layout.addWidget(title)

        #font size controls
        font_controls_layout = QHBoxLayout()
        font_controls_layout.addStretch()

        self.decrease_font_btn = QPushButton("A-")
        self.decrease_font_btn.setFixedWidth(40)
        self.decrease_font_btn.setToolTip("Decrease font size")
        font_controls_layout.addWidget(self.decrease_font_btn)
        self.decrease_font_btn.clicked.connect(self._decrease_font_size)

        self.increase_font_btn = QPushButton("A+")
        self.increase_font_btn.setFixedWidth(40)
        self.increase_font_btn.setToolTip("Increase font size")
        font_controls_layout.addWidget(self.increase_font_btn)
        self.increase_font_btn.clicked.connect(self._increase_font_size)

        editor_layout.addLayout(font_controls_layout)

        #query text area
        self.query_text = QTextEdit()
        self.query_text.setPlaceholderText("Enter SQL query...")
        font = QFont("Courier New", 11)
        self.query_text.setFont(font)
        editor_layout.addWidget(self.query_text)

        #execute button
        self.execute_btn = QPushButton("Execute Query")
        self.execute_btn.clicked.connect(self._execute_query)
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color:white;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3a92ea;                           
            }
            QPushButton:pressed {
                background-color: #1a72ca;                           
            }
        """)
        editor_layout.addWidget(self.execute_btn)

        splitter.addWidget(editor_widget)

        #right side - query history
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)

        history_title = QLabel("Query History")
        history_title.setStyleSheet("font-size: 12px; font-weight: bold; padding: 5px;")
        history_layout.addWidget(history_title)

        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self._load_query_from_history)
        history_layout.addWidget(self.history_list)

        splitter.addWidget(history_widget)

        #set initial splitter sizes (70% editor, 30% hist)
        splitter.setSizes([700,300])

        layout.addWidget(splitter)

    def _execute_query(self):
        """execute the sql query"""
        query = self.query_text.toPlainText().strip()

        if not query:
            QMessageBox.warning(self, "No Query", "Please enter a SQL query.")
            return

        # disable button during execution
        self.execute_btn.setEnabled(False)
        self.execute_btn.setText("Executing...")
        self.window().status_bar.showMessage("Executing query...")

        # store query for history (add after successful execution)
        self.current_query = query

        # execute query in background thread
        self.query_thread = QueryExecutorThread(self.db_manager, query)
        self.query_thread.finished.connect(self._on_query_finished)
        self.query_thread.error.connect(self._on_query_error)
        self.query_thread.start()

    def _on_query_finished(self, result, execution_time):
        """handle successful query execution"""
        # add to history
        self.query_history.append(self.current_query)
        self.history_list.addItem(f"{self.current_query[:50]}..." if len(self.current_query) > 50 else self.current_query)

        # emit signal with results
        self.query_executed.emit(result, execution_time)

        # re-enable button
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute Query")
        self.query_thread = None

    def _on_query_error(self, error_msg):
        """handle query execution error"""
        QMessageBox.critical(self, "Query error", f"Error executing query:\n\n{error_msg}")
        self.window().status_bar.showMessage("Query failed")
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("Execute Query")
        self.query_thread = None

    def _load_query_from_history(self, item):
        """load a query from history into the editor"""
        index = self.history_list.row(item)
        if 0 <= index < len(self.query_history):
            self.query_text.setPlainText(self.query_history[index])

    def _increase_font_size(self):
        """increase the sql editor font size"""
        if self.current_font_size < 24:
            self.current_font_size += 2
            self._update_editor_font()

    def _decrease_font_size(self):
        """decrease the sql editor font size"""
        if self.current_font_size > 8:
            self.current_font_size -= 2
            self._update_editor_font()

    def _update_editor_font(self):
        """apply the current font size to the editor"""
        font = QFont("Courier New", self.current_font_size)
        self.query_text.setFont(font)
