from PySide6.QtWidgets import QMainWindow
from .menu import MenuBar
from .main import MainWindow
from verifact.settings import Settings
import verifact.metadata as metadata

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(metadata.name)
        self.setGeometry(200, 200, 360, 400)
        
        # Créer la fenêtre principale
        self.main_frame = MainWindow(self)
        self.setCentralWidget(self.main_frame)
        
        # Créer la barre de menu
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # Initialiser les valeurs des paramètres
        self.settings = Settings()
        self.settings.load()
        
        # Connecter l'événement de redimensionnement de la fenêtre
        self.resizeEvent = self.on_resize
        
        # Permet à la fenêtre d'accepter les événements de drag-and-drop pour le fichier
        self.setAcceptDrops(True)
        
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