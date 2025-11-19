from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

from src.database.state_manager import StateManager
from src.database.duckdb_manager import DuckDBManager
from src.gui.file_browser import FileBrowser
from src.gui.query_editor import QueryEditor
from src.gui.results_table import ResultsTable
from src.gui.dashboard_view import DashboardView

class MainWindow(QMainWindow):
    """main application window for Duckboard."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Duckboard - Data Analytics")
        self.setGeometry(100, 100, 1400, 800)

        #initialize state manager
        self.state_manager = StateManager()

        #initialize workspace
        self.workspace_id = self.state_manager.ensure_default_workspace()

        #initialize db manager
        self.db_manager = DuckDBManager()

        #apply theme
        self._apply_dark_theme()

        #setup ui
        self._init_ui()

        #status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _apply_dark_theme(self):
        """apply dark color scheme"""
        palette  = QPalette()
        palette.setColor(QPalette.Window, QColor(30,30,30))
        palette.setColor(QPalette.WindowText, QColor(200, 200, 200))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
        palette.setColor(QPalette.ToolTipBase, QColor(200, 200, 200))
        palette.setColor(QPalette.ToolTipText, QColor(200, 200, 200))
        palette.setColor(QPalette.Text, QColor(200, 200, 200))
        palette.setColor(QPalette.Button, QColor(35, 35, 35))
        palette.setColor(QPalette.ButtonText, QColor(200, 200, 200))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.setPalette(palette)

    def _init_ui(self):
        """init the user interface"""
        #central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        #main layout
        main_layout = QHBoxLayout(central_widget)

        #create main splitter (left panel | center/right panels)
        main_splitter = QSplitter(Qt.Horizontal)

        #left panel - file browser
        self.file_browser = FileBrowser(self.db_manager, self.state_manager, self.workspace_id, self)
        main_splitter.addWidget(self.file_browser)

        #center/right area splitter
        center_right_splitter = QSplitter(Qt.Vertical)

        #center area - for query and dashboard
        self.tab_widget = QTabWidget()

        self.query_editor = QueryEditor(self.db_manager, self.state_manager, self)
        self.dashboard_view = DashboardView(self)

        self.tab_widget.addTab(self.query_editor, "SQL Query")
        self.tab_widget.addTab(self.dashboard_view, "Dashboard")

        center_right_splitter.addWidget(self.tab_widget)

        #bottom panel - results table
        self.results_table = ResultsTable(self)
        center_right_splitter.addWidget(self.results_table)

        #set initial sizes for center/right splitter (60% top, 40%, bottom)
        center_right_splitter.setSizes([600,400])

        main_splitter.addWidget(center_right_splitter)

        #set inital sizes for main splitter (20% left, 80% right)
        main_splitter.setSizes([280,1120])

        main_layout.addWidget(main_splitter)

        #connect signals
        self.query_editor.query_executed.connect(self._on_query_executed)

    def _on_query_executed(self, result, execution_time: float):
        """handle query execution completion"""
        try:
            #display results in table
            self.results_table.display_results(result)

            #update status bar with row count from results table
            row_count = self.results_table.full_result_count
            self.status_bar.showMessage(
                f"Query executed successfully | {row_count:,} rows | {execution_time:.3f}s"
            )
        except Exception as e:
            self.status_bar.showMessage(f"Error: {str(e)}")

    def closeEvent(self, event):
        """handle application close"""
        self.db_manager.close()
        self.state_manager.close()
        event.accept()
