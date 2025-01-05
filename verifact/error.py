import sys
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout, QSizePolicy, QWidget,
                               QMessageBox)
from PySide6.QtCore import Qt

class ErrorWindow(QDialog):
    def __init__(self, error_message:str = "Une erreur est survenue", error_details:str = ""):
        super().__init__()

        self.setWindowTitle("Erreur")
        self.setModal(True)
        self.layout = QVBoxLayout()
        
        # Icone d'erreur
        warning_icon = QMessageBox().standardIcon(QMessageBox.Warning)
        icon_label = QLabel()
        icon_label.setPixmap(warning_icon)
        icon_label.setAlignment(Qt.AlignLeft)
        
        message_layout = QHBoxLayout()
        message_layout.addWidget(icon_label)

        # Message d'erreur simplifié
        error_label = QLabel(error_message)
        error_label.setAlignment(Qt.AlignLeft)
        message_layout.addWidget(error_label)
        self.layout.addLayout(message_layout)

        # Bouton pour afficher le message d'erreur
        self.toggle_button = QPushButton("Afficher le message d'erreur")
        self.toggle_button.clicked.connect(self.toggle_message)
        if error_details != "":
            self.layout.addWidget(self.toggle_button)

        # Message d'erreur détaillé
        self.error_details_label = QLabel(error_details)
        self.error_details_label.setVisible(False)
        self.layout.addWidget(self.error_details_label)

        # Permet de dimensionner en petit le bouton "OK"
        button_layout = QHBoxLayout()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        button_layout.addWidget(spacer)

        # Bouton de fermeture
        close_button = QPushButton("OK")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)
        self.adjustSize()

        # True = fenêtre détaillée, False = fenêtre simplifiée
        self.expanded = False  

    def toggle_message(self):
        """Affiche ou masque le message d'erreur."""
        
        if self.expanded:
            self.toggle_button.setText("Afficher le message d'erreur")
            self.error_details_label.setVisible(False)
            self.adjustSize()
        else:
            self.toggle_button.setText("Masquer le message d'erreur")
            self.error_details_label.setVisible(True)
            self.adjustSize()
        self.expanded = not self.expanded

def run_error(message:str = "", details:str = ""):
    """Lance la fenêtre d'erreur."""
    app = QApplication.instance()
    # Créez une nouvelle instance si nécessaire
    if app is None:
        app = QApplication(sys.argv)

    window = ErrorWindow(str(message), str(details))
    window.exec()