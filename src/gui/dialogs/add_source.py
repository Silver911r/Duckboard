from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton
)

class AddSourceDialog(QDialog):
    """panel for browsing and loading data"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_type = None
        self._init_ui()

    def _init_ui(self):
        """init ui"""
        layout = QVBoxLayout(self)

        self.setWindowTitle("Add Data Source")
        self.setFixedSize(250, 120)
        
        self.from_file_btn = QPushButton("From File...")
        self.from_file_btn.clicked.connect(self._add_file)
        layout.addWidget(self.from_file_btn)

        self.from_url_btn = QPushButton("From URL...")
        self.from_url_btn.clicked.connect(self._add_url)
        layout.addWidget(self.from_url_btn)

    def _add_file(self):
        self.source_type =  'file'
        self.accept()

    def _add_url(self):
        self.source_type =  'url'
        self.accept()

