import requests
import os
import sys
from PySide6.QtWidgets import QMessageBox
from packaging.version import Version
import verifact.metadata as metadata

class UpdateManager:
    def __init__(self, repo_owner, repo_name):
        self.repo_owner = repo_owner
        self.repo_name = repo_name

    def get_latest_release_info(self):
        """
        Récupère les informations de la dernière version publiée sur GitHub, y compris le tag et l'URL du fichier .exe.

        Returns:
            tuple: Un tuple contenant le tag de la dernière version et l'URL du fichier .exe, ou (None, None) si une erreur se produit.
        """
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
            data = response.json()
            tag_name = data.get("tag_name")
            assets = data.get("assets", [])
            exe_url = None
            for asset in assets:
                if asset.get("name", "").lower().endswith(".exe"):
                    exe_url = asset.get("browser_download_url")
                    break
            return tag_name, exe_url
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération de la dernière version depuis GitHub : {e}")
            return None, None

    def check_updates(self):
        """
        Vérifie si une mise à jour est disponible.

        Returns:
            bool: True si une mise à jour est disponible, False sinon.
        """
        latest_tag, exe_url = self.get_latest_release_info()
        
        if not latest_tag or not exe_url:
            return False
        
        latest_version = Version(latest_tag.lstrip('v'))
        current_version = Version(metadata.version)

        return latest_version > current_version

    def update_software(self):
        """Met à jour le logiciel en téléchargeant le fichier .exe depuis GitHub."""
        
        print("Mise à jour du logiciel...")
        _, exe_url = self.get_latest_release_info()
        if not exe_url:
            print("Aucun fichier .exe trouvé dans la dernière version.")
            return
        print(f"Téléchargement de la nouvelle version depuis : {exe_url}")
        response = requests.get(exe_url, stream=True)
        response.raise_for_status()
        # Définir le chemin du dossier et du fichier
        new_filename = str(os.path.basename(exe_url))
        old_file_path = os.path.abspath(sys.executable)
        new_filedir = os.path.join(os.path.dirname(old_file_path), "mise à jour")
        file_path = os.path.join(new_filedir, new_filename)
        # Créer le dossier s'il n'existe pas
        os.makedirs(new_filedir, exist_ok=True)
        
        # Écrire le fichier téléchargé
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Téléchargement de la mise à jour terminé.")
        self.show_file_location_message(new_filedir)
        sys.exit()  # Ferme le programme
    
    def show_file_location_message(self, file_path):
        """Affiche un message informant l'utilisateur de la nouvelle version."""
        msg_box = QMessageBox()
        txt = f"""
        La mise à jour a été téléchargée ici :\n\n{file_path}\n
        Vous pouvez supprimer l'ancienne version.
        """
        msg_box.setWindowTitle("Mise à jour terminée")
        msg_box.setText(txt)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)  # Bouton pour fermer le message

        # Afficher le message
        msg_box.exec()

