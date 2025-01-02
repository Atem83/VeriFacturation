import sys
from PySide6.QtWidgets import QApplication
from verifact.gui import App

def run():
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())