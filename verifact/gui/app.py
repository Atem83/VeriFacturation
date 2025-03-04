import sys
import re
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from .menu import MenuBar
from .main import MainWindow
from .update import UpdateManager
from verifact.settings import Settings
from verifact.error import run_error
import verifact.metadata as metadata

class App(QMainWindow):
    def __init__(self):
        # Initialisation de QApplication
        self.qapp = QApplication(sys.argv)
        
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
        """Exécution de l'application."""
        self.show()
        self.check_for_updates()
        sys.exit(self.qapp.exec())
        
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

    def extract_repo_info(self, url: str):
        """Extrait le nom d'utilisateur et le nom du repository d'une URL GitHub."""
        pattern = r'https?://(?:www\.)?github\.com/([^/]+)/([^/]+)'
        match = re.match(pattern, url)

        if match:
            repo_owner = match.group(1)
            repo_name = match.group(2)
            return repo_owner, repo_name
        else:
            raise ValueError("URL invalide")
        
    def check_for_updates(self):
        """Vérification des mises à jour."""
        repo_owner, repo_name = self.extract_repo_info(metadata.url)
        
        updater = UpdateManager(repo_owner, repo_name, self)
        reply = None
        
        # Vérification de la disponibilité d'une mise à jour
        if updater.check_updates() and self.settings.auto_update:
            msg = "Une mise à jour est disponible,"
            msg += "\nsouhaitez-vous mettre à jour le logiciel ?"
            reply = QMessageBox.question(
                None, 
                "Information", 
                msg, 
                QMessageBox.Yes | QMessageBox.No
                )
        
        # Téléchargement de la mise à jour
        if updater.check_updates() and reply == QMessageBox.Yes:
            try:
                updater.update_software()
                updater.show_file_location_message(updater.new_filedir)
                self.close()
                sys.exit(self.qapp.exec())
            except Exception as e:
                msg = "Une erreur est survenue lors de la mise à jour"
                run_error(msg, details = e)
                
