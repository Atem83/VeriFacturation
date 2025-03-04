from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QDialog, QCheckBox, QLineEdit, QTextEdit
)
from verifact.error import run_error

class SettingsWindow(QDialog):
    """Fenêtre des paramètres."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.menu = parent
        self.setWindowTitle("Paramètres")
        self.setModal(True)
        x = self.menu.app.geometry().x()
        y = self.menu.app.geometry().y()
        self.setGeometry(x, y, 260, 230)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.addLayout(self.init_root())
        layout.addLayout(self.init_occurences())
        layout.addLayout(self.init_case())
        layout.addLayout(self.init_update())
        layout.addLayout(self.init_logs())
        layout.addSpacing(10)
        layout.addLayout(self.init_buttons())
    
    def init_root(self):
        """Initialise le champ racine client."""
        msg = "Racine des comptes clients dans le logiciel.\n"
        msg += "Exemples : Cador = C ; Quadra = 411"
        
        # Client label
        client_label = QLabel("Racine client :")
        client_label.setToolTip(msg)
        
        # Client input
        self.client_input = QLineEdit()
        self.client_input.setText(self.menu.app.settings.client_root)
        self.client_input.setToolTip(msg)
        
        # Client layout
        client_layout = QHBoxLayout()
        client_layout.addWidget(client_label)
        client_layout.addWidget(self.client_input)
        return client_layout
    
    def init_occurences(self):
        """Initialise le champ nombre minimum d'occurences."""
        msg = "Il s'agit du nombre de factures qui doivent partager le préfixe/suffixe choisi\n"
        msg += "pour considérer une séquence comme valide par 'Séquence auto'.\n\n"
        msg += "La valeur doit être un entier positif."
        
        # Occurences label
        occurences_label = QLabel("Nombre minimum\nd'occurences d'une séquence :")
        occurences_label.setToolTip(msg)
        
        # Occurences input
        self.occurences_input = QLineEdit()
        self.occurences_input.setText(str(self.menu.app.settings.min_occurrences))
        self.occurences_input.setToolTip(msg)
        
        # Occurences layout
        occurences_layout = QHBoxLayout()
        occurences_layout.addWidget(occurences_label)
        occurences_layout.addWidget(self.occurences_input)
        return occurences_layout
    
    def init_case(self):
        """Initialise le champ sensibilité à la casse."""
        msg = "Si la case est cochée, les préfixes et suffixes seront insensibles à la casse.\n"
        msg += "Exemple : FAC001 = fac001"
        
        # Case label
        case_label = QLabel("Séquence insensible à la casse :")
        case_label.setToolTip(msg)
        
        # Case toggle
        self.case_toggle = QCheckBox()
        self.case_toggle.setChecked(self.menu.app.settings.case_insensitive)
        self.case_toggle.setToolTip(msg)
        
        # Case layout
        case_layout = QHBoxLayout()
        case_layout.addWidget(case_label)
        case_layout.addWidget(self.case_toggle)
        return case_layout
    
    def init_update(self):
        """Initialise le champ mise à jour au démarrage."""
        msg = "Si la case est cochée, le logiciel recherchera automatiquement\n"
        msg += "si une mise à jour est disponible au démarrage."
        
        # Update label
        update_label = QLabel("Mises à jour au démarrage :")
        update_label.setToolTip(msg)
        
        # Update toggle
        self.update_toggle = QCheckBox()
        self.update_toggle.setChecked(self.menu.app.settings.auto_update)
        self.update_toggle.setToolTip(msg)
        
        # Update layout
        update_layout = QHBoxLayout()
        update_layout.addWidget(update_label)
        update_layout.addWidget(self.update_toggle)
        return update_layout
    
    def init_logs(self):
        """Initialise le champ codes journaux."""
        msg = "Codes journaux à conserver.\n"
        msg += "Séparez chaque code par un saut de ligne.\n\n"
        msg += "Ne fonctionne qu'avec les imports FEC."
        
        # Logs label
        logs_label = QLabel("Codes journaux :")
        logs_label.setToolTip(msg)
        
        # Logs input
        self.logs_input = QTextEdit()
        self.logs_input.setPlainText("\n".join(self.menu.app.settings.logs))
        self.logs_input.setToolTip(msg)
        
        # Logs layout
        logs_layout = QHBoxLayout()
        logs_layout.addWidget(logs_label)
        logs_layout.addWidget(self.logs_input)
        return logs_layout
    
    def init_buttons(self):
        """Initialise les boutons OK et Annuler."""
        # OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.on_ok)
        
        # Cancel button
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.on_cancel)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        return buttons_layout
    
    def on_ok(self):
        """Gérer le clic sur OK."""
        try:
            occ = int(self.occurences_input.text())
        except ValueError:
            run_error("Le minimum d'occurences doit être un nombre entier.")
            self.occurences_input.setText(
                str(self.menu.app.settings.min_occurrences)
                )
            return
        
        if occ < 1:
            run_error("Le minimum d'occurences doit être un nombre entier supérieur à 0.")
            self.occurences_input.setText(
                str(self.menu.app.settings.min_occurrences)
                )
            return
        else:
            self.menu.app.settings.client_root = str(self.client_input.text())
            self.menu.app.settings.min_occurrences = occ
            self.menu.app.settings.case_insensitive = bool(self.case_toggle.isChecked())
            self.menu.app.settings.auto_update = bool(self.update_toggle.isChecked())
            self.menu.app.settings.logs = self.logs_input.toPlainText().split("\n")
            self.menu.app.settings.save()
            self.accept()
    
    def on_cancel(self):
        """Gérer le clic sur Annuler."""
        self.reject()