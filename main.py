import sys
from PySide6.QtWidgets import QApplication

from src.gui.main_window import MainWindow

def main():
    """Entry point for duckboard app"""
    app = QApplication(sys.argv)

    #set app metadata
    app.setApplicationName("Duckboard")
    app.setOrganizationName("Duckboard")

    #create main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
