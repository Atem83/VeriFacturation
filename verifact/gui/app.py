import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QSplashScreen, QMainWindow
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt
from .menu import MenuBar
from .main import MainWindow
from verifact.settings import Settings
import verifact.metadata as metadata

class App(QMainWindow):
    def __init__(self):
        # Initialisation de QApplication
        self.qapp = QApplication(sys.argv)
        self.splash = QSplashScreen(self.img_splash())
        self.splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.splash.show()
        self.qapp.processEvents()
        
        # Initialisation de QMainWindow
        super().__init__()
        self.setWindowTitle(metadata.name)
        self.setGeometry(200, 200, 360, 400)
        
        # Création de la fenêtre principale
        self.main_frame = MainWindow(self)
        self.setCentralWidget(self.main_frame)
        
        # Création de la barre de menu
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # Initialisation des valeurs des paramètres
        self.settings = Settings()
        self.settings.load()
        
        # Connexion de l'événement de redimensionnement de la fenêtre
        self.resizeEvent = self.on_resize
        
        # Permet à la fenêtre d'accepter les événements de drag-and-drop pour le fichier
        self.setAcceptDrops(True)
        
    def run(self):
        """Exécuter l'application."""
        self.show()
        self.splash.finish(self)
        sys.exit(self.qapp.exec())
        
    def img_splash(self):
        """Retourne le pixmap de la fenêtre de chargement."""
        img = Path(__file__).parent.parent.parent / "images" / "splash.png"
        pixmap = QPixmap(img).scaled(400, 300, Qt.KeepAspectRatio)

        # Modifie la police et couleur du texte
        color = QColor(205, 92, 92)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)

        # Créer un QPainter pour dessiner sur le QPixmap
        painter = QPainter(pixmap)
        painter.setFont(font)
        painter.setPen(color)

        # Dessiner le texte
        text_rect = pixmap.rect()
        text_rect.moveTop(pixmap.rect().top() + 57)  # Décale le texte de x pixels vers le bas
        painter.drawText(text_rect, Qt.AlignHCenter, "Chargement...")
        painter.end()

        return pixmap
        
    def on_resize(self, event):
        """Exécute des actions lorsque la fenêtre principale est redimensionnée."""
        #print(f"Dimensions de la fenêtre : {self.width()}x{self.height()}")
        super().resizeEvent(event)
        self.main_frame.adjust_table_columns()
    
    def dragEnterEvent(self, event):
        """Permet de gérer l'événement de drag & drop.
        On accepte uniquement les fichiers."""
        if event.mimeData().hasUrls():
            event.accept()  # Accepte l'événement de drag
        else:
            event.ignore()  # Ignore si ce n'est pas un fichier
    
    def dropEvent(self, event):
        """Gère l'événement de drop et récupère le fichier déposé."""
        if event.mimeData().hasUrls():
            # Récupérer la première URL du mimeData
            url = event.mimeData().urls()[0]
            # Convertir l'URL en chemin local
            file_path = url.toLocalFile()
            # Mettre le chemin dans le QLineEdit
            self.main_frame.file_input.setText(file_path)
            # Lancer l'auto-search après le drop
            self.main_frame.auto_search()

