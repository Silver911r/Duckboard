from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

from src.database.duckdb_manager import DuckDBManager
from src.gui.file_browser import FileBrowser
from src.gui.query_editor import QueryEditor
from src.gui.results_table import ResultsTable
from src.gui.dashboard_view import DashboardView