from PySide6.QtWidgets import QApplication, QDialog, QProgressBar, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class LoadingWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Chargement")
        self.setGeometry(100, 100, 300, 100)
        
        # Supprimer les boutons de la barre Windows
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        
        if parent:
            # Obtenir la géométrie du parent
            parent_geometry = parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)  # Déplacer la fenêtre

        # Créer la barre de progression
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #f0f0f0;  /* Couleur de fond */
                border: 2px solid #8f8f8f;   /* Bordure */
                border-radius: 5px;          /* Coins arrondis */
                height: 15px;                 /* Hauteur de la barre */
                text-align: center;          /* Aligne le texte au centre */
                color: #000000;              /* Couleur du texte */
            }
            QProgressBar::chunk {
                background-color: #3c8dbc;   /* Couleur de la portion remplie */
                border-radius: 5px;          /* Coins arrondis de la portion remplie */
            }
        """)
        
        # Ajouter un texte explicatif
        self.label = QLabel("Téléchargement en cours...", self)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # Créer une mise en page
        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.label)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

    def update_progress(self, value):
        """Modifie la valeur de la barre de progression."""
        self.progress_bar.setValue(value)
        QApplication.processEvents()
        
    def setText(self, text):
        """Permet de modifier le texte de la fenêtre."""
        self.label.setText(text)