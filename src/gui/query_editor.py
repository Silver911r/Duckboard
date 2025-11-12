from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QLabel, QListWidget, QSplitter, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import time

from src.database.duckdb_manager import DuckDBManager

class QueryEditor(QWidget):
    """sql query editor with history."""
    query_executed = Signal(object, float) # result, execution_time

    def __init__(self, db_manager: DuckDBManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.query_history = []
        self.__init_ui()

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
        
        try:
            start_time = time.time()
            result = self.db_manager.execute_query(query)
            execution_time = time.time() - start_time

            #add to hstory
            self.query_history.append(query)
            self.history_list.addItem(f"{query[:50]}..." if len(query) > 50 else query)

            #emit sig with results
            self.query_executed.emit(result, execution_time)
        except Exception as e:
            QMessageBox.critical(self, "Query error", f"Error executing query:\n\n{str(e)}")

    def _load_query_from_history(self, item):
        """load a query from history into the editor"""
        index = self.history_list.row(item)
        if 0 <= index < len(self.query_history):
            self.query_text.setPlainText(self.query_history[index])
