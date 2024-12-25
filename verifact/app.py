import sys
from PySide6.QtWidgets import QApplication
from verifact.gui import MainWindow

def app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())