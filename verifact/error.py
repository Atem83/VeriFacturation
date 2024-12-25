import sys
from PySide6.QtWidgets import (QApplication, QDialog, 
                               QVBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import Qt

class ErrorWindow(QDialog):
    def __init__(self, error_message:str = "Une erreur est survenue", error_details:str = ""):
        super().__init__()

        self.setWindowTitle("Erreur")
        self.setGeometry(100, 100, 200, 100)
        self.setModal(True)

        self.layout = QVBoxLayout()
        
        # Message d'erreur simplifié
        self.error_label = QLabel(error_message)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.error_label, alignment=Qt.AlignCenter)

        # Bouton pour afficher le message d'erreur
        self.toggle_button = QPushButton("Afficher le message d'erreur")
        self.toggle_button.clicked.connect(self.toggle_message)
        self.layout.addWidget(self.toggle_button)

        # Message d'erreur détaillé
        self.error_details_label = QLabel(error_details)
        self.error_details_label.setVisible(False)
        self.layout.addWidget(self.error_details_label)

        self.setLayout(self.layout)

        self.expanded = False  # État d'agrandissement

    def toggle_message(self):
        """Affiche ou masque le message d'erreur."""
        
        if self.expanded:
            self.toggle_button.setText("Afficher le message d'erreur")
            self.error_details_label.setVisible(False)
            
            # Dimensions d'origine
            self.setFixedHeight(100)
            self.setFixedWidth(200)
        else:
            self.toggle_button.setText("Masquer le message d'erreur")
            self.error_details_label.setVisible(True)
            
            # Dimensions agrandies
            self.setFixedHeight(100 + self.error_details_label.sizeHint().height())
            self.setFixedWidth(300 + self.error_details_label.sizeHint().width())
        self.expanded = not self.expanded

def run_error(message:str = "", details:str = ""):
    """Lance la fenêtre d'erreur."""
    app = QApplication.instance()
    # Créez une nouvelle instance si nécessaire
    if app is None:
        app = QApplication(sys.argv)

    window = ErrorWindow(str(message), str(details))
    window.exec()