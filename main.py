import sys
from PySide6.QTWidgets import QApplication

from src.gui.main_window import MainWindow

def main():
    """Entry point for duckboard app"""
    app = QApplication(sys.argv)
    app.setApplicationName("Duckboard")
    app.setOrganizationName("Duckboard")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
