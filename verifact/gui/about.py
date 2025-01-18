from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QDialog, QApplication
    )
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from .update import UpdateManager
from verifact.error import run_error
import verifact.metadata as metadata
import re
import sys
import subprocess

class AboutWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.menu = parent
        self.setWindowTitle("À propos")
        layout = QVBoxLayout()

        self.init_version()
        layout.addLayout(self.layout_version)
        
        self.init_author()
        layout.addLayout(self.layout_author)
        
        self.init_license()
        layout.addLayout(self.layout_license)
        
        self.init_description()
        layout.addSpacing(10)
        layout.addLayout(self.layout_description)

        self.setLayout(layout)
        
    def init_version(self):
        """Ligne 1 contenant le numéro de version et la recherche des màj."""
        self.layout_version = QHBoxLayout()
        version_label = QLabel("Version : ")
        version_text = QLabel(metadata.version)

        # Ajouter le bouton pour vérifier les mises à jour
        self.check_update_button = QPushButton("Vérifier mise à jour")
        self.check_update_button.setStyleSheet(self.style_link())
        self.check_update_button.clicked.connect(self.check_for_updates)
        
        self.layout_version.addWidget(version_label)
        self.layout_version.addWidget(version_text)
        self.layout_version.addWidget(self.check_update_button)
        self.layout_version.setAlignment(Qt.AlignLeft)
        
    def init_author(self):
        """Ligne 2 contenant le nom de l'auteur."""
        self.layout_author = QHBoxLayout()
        author_label = QLabel("Auteur : ")
        author_text = QLabel(metadata.author)

        self.layout_author.addWidget(author_label)
        self.layout_author.addWidget(author_text)
        self.layout_author.setAlignment(Qt.AlignLeft)

    def init_license(self):
        """Ligne 3 contenant la licence et le lien vers le code source."""
        self.layout_license = QHBoxLayout()
        license_label = QLabel("Licence : ")
        license_text = QLabel(metadata.license)
        
        url_button = QPushButton("code source")
        url_button.setStyleSheet(self.style_link())
        url_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(metadata.url)))

        self.layout_license.addWidget(license_label)
        self.layout_license.addWidget(license_text)
        self.layout_license.addWidget(url_button)
        self.layout_license.setAlignment(Qt.AlignLeft)

    def init_description(self):
        """Ligne 4 contenant la description du logiciel."""
        self.layout_description = QHBoxLayout()
        description_text = QLabel(metadata.description)
        self.layout_description.addWidget(description_text)
        
    def style_link(self):
        """Style pour les liens."""
        css = """
            QPushButton {
                border: none;  /* Pas de bordure */
                background: none;  /* Pas d'arrière-plan */
                color: DodgerBlue;  /* Couleur du texte */
                text-decoration: underline;  /* Texte souligné pour ressembler à un lien */
            }
            QPushButton:hover {
                color: RoyalBlue;  /* Couleur du texte au survol */
            }
        """
        return css

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
        """Vérifie les mises à jour et met à jour l'interface utilisateur."""
        
        self.check_update_button.setEnabled(False)
        self.check_update_button.setText("Recherche en cours...")
        QApplication.processEvents()
        
        repo_owner, repo_name = self.extract_repo_info(metadata.url)
        
        updater = UpdateManager(repo_owner, repo_name, self)
        if updater.check_updates():
            self.check_update_button.setText("Téléchargement de la mise à jour")
            QApplication.processEvents()
            try:
                updater.update_software()
                self.check_update_button.setText("Mise à jour terminée")
                
                # Lancement du batch
                if hasattr(sys, 'frozen') and updater.batch_success:
                    print("Valeur de updater.batch_path : ", updater.batch_path)
                    print("Valeur de updater.old_path : ", updater.old_path)
                    print("Valeur de updater.new_path : ", updater.new_path)
                    test = "C:/Users/Atem/Desktop/maj/update.bat"
                    input("Commande interne ?")
                    #subprocess.run([test, updater.old_path, updater.new_path])
                    #subprocess.run(f'start cmd /k "{test} {updater.old_path} {updater.new_path}"', shell=True)

                    with open("C:/Users/Atem/Desktop/output.txt", "w") as output_file:
                        subprocess.run([test, updater.old_path, updater.new_path], stdout=output_file, stderr=subprocess.STDOUT)
                    input("Oui mais non")
                else:
                    updater.show_file_location_message(updater.new_filedir)
                
                self.menu.app.close()
            except Exception as e:
                self.check_update_button.setText("Erreur inattendue lors de la mise à jour")
                run_error("Une erreur est survenue lors de la mise à jour", details = e)
        else:
            self.check_update_button.setText("Logiciel à jour")

        self.check_update_button.setEnabled(True)