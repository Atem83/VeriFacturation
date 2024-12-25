from PySide6.QtWidgets import QMenuBar, QDialog
from .about import AboutWindow
from .settings import SettingsWindow

class MenuBar(QMenuBar):
    """Créer une barre de menus."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Créer le menu Fichier
        file_menu = self.addMenu("&Fichier")
        # Action Ouvrir
        self.open_action = file_menu.addAction("&Ouvrir")
        self.open_action.setShortcut("Ctrl+O")
        # Action Quitter
        self.quit_action = file_menu.addAction("&Quitter")
        self.quit_action.setShortcut("Ctrl+Q")
        
        # Créer le menu Paramètres
        settings_menu = self.addAction("&Paramètres")
        settings_menu.triggered.connect(self.show_settings)
        
        # Créer le menu A propos
        help_menu = self.addAction("À &propos")
        help_menu.triggered.connect(self.show_about)

    def show_about(self):
        """Affiche la boîte de dialogue À propos."""
        about_dialog = AboutWindow(self)
        about_dialog.exec()

    def show_settings(self):
        """Affiche la fenêtre des paramètres."""
        settings_dialog = SettingsWindow(self)
        # Initialiser avec les valeurs actuelles de MainWindow
        settings_dialog.client_input.setText(self.parent.client_root)
        settings_dialog.occurences_input.setText(str(self.parent.min_occurrences))
        settings_dialog.case_toggle.setChecked(self.parent.case_insensitive)
        
        if settings_dialog.exec() == QDialog.Accepted:
            # Mettre à jour les valeurs dans MainWindow
            self.parent.client_root = settings_dialog.client_input.text()
            self.parent.min_occurrences = int(settings_dialog.occurences_input.text())
            self.parent.case_insensitive = settings_dialog.case_toggle.isChecked()