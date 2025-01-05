from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QDialog, QCheckBox
)
from verifact.error import run_error

class SettingsWindow(QDialog):
    """Fenêtre des paramètres."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.menu = parent
        self.setWindowTitle("Paramètres")
        self.setModal(True)
        self.setGeometry(200, 200, 245, 150)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Racine client
        client_layout = QHBoxLayout()
        client_label = QLabel("Racine client :")
        self.client_input = QLineEdit()
        self.client_input.setText(self.menu.app.settings.client_root)
        self.client_input.setToolTip(
            "Racine des comptes clients dans le logiciel.\n"
            "Exemples : Cador = C ; Quadra = 411")
        client_layout.addWidget(client_label)
        client_layout.addWidget(self.client_input)
        layout.addLayout(client_layout)
        
        # Nombre minimum d'occurences
        occurences_layout = QHBoxLayout()
        occurences_label = QLabel("Nombre minimum\nd'occurences d'une séquence :")
        self.occurences_input = QLineEdit()
        self.occurences_input.setText(str(self.menu.app.settings.min_occurrences))
        self.occurences_input.textChanged.connect(self.occ_changed)
        self.occurences_input.setToolTip(
            "Il s'agit du nombre de factures qui doivent partager le préfixe/suffixe choisi\n" +
            "pour considérer une séquence comme valide par 'Séquence auto'.\n\n" +
            "La valeur doit être un entier positif.")
        occurences_layout.addWidget(occurences_label)
        occurences_layout.addWidget(self.occurences_input)
        layout.addLayout(occurences_layout)
        
        # Sensibilité à la casse
        case_layout = QHBoxLayout()
        case_label = QLabel("Séquence insensible à la casse :")
        self.case_toggle = QCheckBox()
        self.case_toggle.setChecked(self.menu.app.settings.case_insensitive)
        self.case_toggle.setToolTip(
            "Si la case est cochée, les préfixes et suffixes seront insensibles à la casse.\n" + 
            "Exemple : FAC001 = fac001")
        case_layout.addWidget(case_label)
        case_layout.addWidget(self.case_toggle)
        layout.addLayout(case_layout)
        
        # Ajouter un espacement supplémentaire
        layout.addSpacing(10)
        
        # Boutons OK et Annuler
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Annuler")
        ok_button.clicked.connect(self.on_ok)
        cancel_button.clicked.connect(self.on_cancel)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
    
    def occ_changed(self, text):
        """Contrôle les valeurs autorisées pour le minimum d'occurences."""
        try:
            text = int(text)
        except ValueError:
            run_error("Le minimum d'occurences doit être un nombre entier.")
            self.occurences_input.setText(
                str(self.menu.app.settings.min_occurrences)
                )
            return
        
        if text < 1:
            run_error("Le minimum d'occurences doit être un nombre entier supérieur à 0.")
            self.occurences_input.setText(
                str(self.menu.app.settings.min_occurrences)
                )
    
    def on_ok(self):
        """Gérer le clic sur OK."""
        self.menu.app.settings.client_root = str(self.client_input.text())
        self.menu.app.settings.min_occurrences = int(self.occurences_input.text())
        self.menu.app.settings.case_insensitive = bool(self.case_toggle.isChecked())
        self.menu.app.settings.save()
        self.accept()
    
    def on_cancel(self):
        """Gérer le clic sur Annuler."""
        self.reject()