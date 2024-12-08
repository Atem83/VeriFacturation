import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QWidget, QFileDialog, QMessageBox,
    QMenuBar, QDialog, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence
from verifact.invoice import Invoice
import verifact.metadata as metadata

__version__ = "1.0.0"

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
        
        # Créer le menu Aide
        help_menu = self.addMenu("&Aide")
        # Action À propos
        self.about_action = help_menu.addAction("À &propos")
        self.about_action.triggered.connect(self.show_about)

    def show_about(self):
        """Affiche la boîte de dialogue À propos."""
        QMessageBox.information(
            self,
            "À propos",
            f"Version {metadata.version}\n"
            f"Auteur : {metadata.author}\n\n"
            f"{metadata.description}\n"
            f"{metadata.long_description}"
        )

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

class SettingsWindow(QDialog):
    """Fenêtre des paramètres."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres")
        self.setModal(True)
        self.setGeometry(200, 200, 245, 150)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Racine client
        client_layout = QHBoxLayout()
        client_label = QLabel("Racine client :")
        self.client_input = QLineEdit()
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
        self.case_toggle.setToolTip(
            "Si la case est cochée, les préfixes et suffixes seront insensibles à la casse.\n" + 
            "Exemples : FAC001 = fac001")
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
        
    def on_ok(self):
        """Gérer le clic sur OK."""
        # Vérifier que occurences_input est un entier positif
        try:
            occurences = int(self.occurences_input.text())
            if occurences <= 0:
                raise ValueError("La valeur doit être supérieure à 0")
        except ValueError:
            QMessageBox.warning(
                self,
                "Erreur de saisie",
                "Le nombre minimum d'occurences doit être un entier supérieur à 0."
            )
            self.occurences_input.setText(self.parent().parent.min_occurrences)
            return
            
        self.accept()
        
    def on_cancel(self):
        """Gérer le clic sur Annuler."""
        # Remettre les valeurs par défaut
        self.client_input.setText(self.parent().parent.client_root)
        self.occurences_input.setText(str(self.parent().parent.min_occurrences))
        self.case_toggle.setChecked(self.parent().parent.case_insensitive)
        self.reject()
        
class MainWindow(QMainWindow):
    """Fenêtre principale."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle(metadata.name)
        self.setGeometry(200, 200, 360, 400)
        
        # Initialiser les valeurs des paramètres
        self.client_root = "C"
        self.min_occurrences = 3
        self.case_insensitive = True

        # Connecter l'événement de redimensionnement de la fenêtre
        self.resizeEvent = self.on_resize
        
        # Permet à la fenêtre d'accepter les événements de drag-and-drop pour le fichier
        self.setAcceptDrops(True)

        # Widget principal
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Première ligne : Fichier
        file_layout = QHBoxLayout()
        file_label = QLabel("Fichier :")
        self.file_input = QLineEdit()
        self.file_input.setToolTip(
            "Vous pouvez glisser-déposer un fichier dans la fenêtre\n" +
            "ou cliquer sur 'Parcourir'")
        browse_button = QPushButton("Parcourir")
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(browse_button)
        layout.addLayout(file_layout)

        # Deuxième ligne : Format
        format_layout = QHBoxLayout()
        format_label = QLabel("Format :")
        self.format_dropdown = QComboBox()
        self.format_dropdown.addItems(["CADOR", "FEC"])
        self.format_dropdown.setToolTip(
            "CADOR : Journal de vente de Cador au format .xlsx\n" + 
            "FEC : Fichier des Ecritures Comptables au format .txt")
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_dropdown)
        layout.addLayout(format_layout)

        # Troisième ligne : Bouton Séquence auto
        auto_search_button = QPushButton("Séquence auto")
        auto_search_button.setToolTip(
            "Cliquez ici pour rechercher automatiquement\n" +
            "les séquences de numérotation.")
        auto_search_button.clicked.connect(self.auto_search)
        layout.addWidget(auto_search_button)

        # Quatrième ligne : QTableWidget
        table_label = QLabel("Séquences de numérotation")
        table_label.setAlignment(Qt.AlignCenter)  # Centrer le label
        layout.addWidget(table_label)

        self.table = QTableWidget(1, 5)
        self.table.setHorizontalHeaderLabels(["Nom", "Préfixe", "Suffixe", "Début", "Fin"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # Colonnes redimensionnables
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) # Sélectionne la ligne entière
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setDragDropOverwriteMode(False)
        self.table.setDragDropMode(QAbstractItemView.InternalMove)
        self.table.setDropIndicatorShown(True)
        self.table.setDefaultDropAction(Qt.MoveAction)
        
        self.table.horizontalHeaderItem(0).setToolTip(
            "Nom donné à la séquence de numérotation.\n" + 
            "Si la cellule est vide, un nom par défaut sera donné.")
        self.table.horizontalHeaderItem(1).setToolTip(
            "Suite de caractères se trouvant avant le numéro à incrémenter.\n" + 
            "Si la cellule est vide, on considère que rien ne se trouve avant le numéro.")
        self.table.horizontalHeaderItem(2).setToolTip(
            "Suite de caractères se trouvant après le numéro à incrémenter.\n" + 
            "Si la cellule est vide, on considère que rien ne se trouve après le numéro.")
        self.table.horizontalHeaderItem(3).setToolTip(
            "Premier numéro de facture de la séquence.\n" + 
            "Conseil : vérifiez que le numéro soit bien celui de la première facture.")
        self.table.horizontalHeaderItem(4).setToolTip(
            "Dernier numéro de facture de la séquence.\n" + 
            "Conseil : vérifiez que le numéro soit bien celui de la dernière facture.")
        layout.addWidget(self.table)

        # Centrer les valeurs dans les cellules et restreindre les colonnes "Début" et "Fin"
        self.table.itemChanged.connect(self.on_item_changed)

        # Boutons pour ajouter/supprimer des lignes au tableau
        table_create_row_layout = QHBoxLayout()
        add_row_button = QPushButton("Ajouter une ligne")
        add_row_button.clicked.connect(self.add_row)
        self.delete_row_button = QPushButton("Supprimer une ligne")
        self.delete_row_button.clicked.connect(self.delete_row)
        self.delete_row_button.setEnabled(False)  # Désactiver par défaut
        table_create_row_layout.addWidget(add_row_button)
        table_create_row_layout.addWidget(self.delete_row_button)
        layout.addLayout(table_create_row_layout)
        
        # Boutons pour déplacer les lignes du tableau
        table_move_row_layout = QHBoxLayout()
        move_up_button = QPushButton("Déplacer vers le haut")
        move_up_button.clicked.connect(self.move_up)
        move_down_button = QPushButton("Déplacer vers le bas")
        move_down_button.clicked.connect(self.move_down)
        table_move_row_layout.addWidget(move_up_button)
        table_move_row_layout.addWidget(move_down_button)
        layout.addLayout(table_move_row_layout)
        
        # Créer un raccourci clavier pour la flèche du haut
        self.shortcut_up = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.shortcut_up.activated.connect(self.move_up)
        
        # Créer un raccourci clavier pour la flèche du bas (facultatif)
        self.shortcut_down = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.shortcut_down.activated.connect(self.move_down)

        # Dernière ligne : Bouton Lancer la recherche
        launch_search_button = QPushButton("Exécuter le programme")
        launch_search_button.clicked.connect(self.launch_search)
        layout.addWidget(launch_search_button)

        # Créer la barre de menu
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # Connecter les actions du menu
        self.menu_bar.open_action.triggered.connect(self.browse_file)
        self.menu_bar.quit_action.triggered.connect(self.close)

    def on_resize(self, event):
        """Exécute des actions lorsque la fenêtre principale est redimensionnée."""
        #print(f"Dimensions de la fenêtre : {self.width()}x{self.height()}")
        super().resizeEvent(event)
        self.adjust_table_columns()  # Ajuster les colonnes à chaque redimensionnement

    def browse_file(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Tous les fichiers (*.*)")
        if file_dialog.exec():
            # Récupérer le premier fichier sélectionné
            selected_file = file_dialog.selectedFiles()[0]
            
            # Afficher le chemin dans le champ de texte
            self.file_input.setText(selected_file)
            
            # Lancer l'auto-search automatiquement
            self.auto_search()

    def auto_search(self):
        """Action pour le bouton 'Séquence auto'."""
        if not self.file_input.text():
            self.show_error_popup("Veuillez choisir un fichier.")
            return
        elif Path(self.file_input.text()).exists() == False:
            self.show_error_popup("Le fichier n'existe pas.")
            return
        
        # Vider le tableau
        self.table.setRowCount(0)  # Supprime toutes les lignes
        self.table.insertRow(0)  # Ajoute une seule ligne vide
        
        # Rechercher le pattern des différentes séquences de facturation
        invoices = Invoice(
            self.file_input.text(),
            self.client_root
            )
        invoices.import_invoices(self.format_dropdown.currentText())
        patterns = invoices.infer_pattern(self.min_occurrences)
        
        # Ecrire ces patterns dans le tableau
        for i, pattern in enumerate(patterns):
            # Si la ligne n'existe pas, en insert une nouvelle
            if i + 1 > self.table.rowCount():
                self.table.insertRow(self.table.rowCount())
            
            # Ajouter des valeurs dans les cellules de ma ligne
            self.table.setItem(i, 1, QTableWidgetItem(pattern["prefix"]))
            self.table.setItem(i, 2, QTableWidgetItem(pattern["suffix"]))
            self.table.setItem(i, 3, QTableWidgetItem(str(pattern["start"])))
            self.table.setItem(i, 4, QTableWidgetItem(str(pattern["end"])))
        
        self.update_delete_button_state()

    def launch_search(self):
        """Lance le programme pour contrôler la numérotation des factures."""
        if not self.file_input.text():
            self.show_error_popup("Veuillez choisir un fichier.")
            return
        elif Path(self.file_input.text()).exists() == False:
            self.show_error_popup("Le fichier n'existe pas.")
            return
        
        # Récupérer les pattern de facturation du tableau
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    value = item.text()
                    if value == "":
                        value = None
                    row_data.append(value)
                else:
                    row_data.append(None)
            data.append(row_data)
        
        # Créer mon objet Invoice à partir des informations de l'utilisateur
        invoices = Invoice(
            self.file_input.text(),
            self.client_root
            )
        invoices.import_invoices(self.format_dropdown.currentText())
        for row in data:
            try:
                if row[3] is None:
                    start = None
                else:
                    start = int(row[3])
                if row[4] is None:
                    end = None
                else:
                    end = int(row[4])
                
                invoices.serial.add_serial(
                    name=row[0],
                    prefix=row[1], 
                    suffix=row[2], 
                    start=start, 
                    end=end
                )
            except Exception as e:
                self.show_error_popup(
                    "Une erreur est survenue lors de la création de " +
                    f"la séquence '{row[0]}':\n{e}")
                return
        
        # Effectuer les recherches
        invoices.search_pattern(self.case_insensitive)
        invoices.search_missing()
        invoices.search_duplicate()
        
        # Exporter les résultats
        invoices.export()

    def add_row(self):
        """Ajoute une nouvelle ligne au tableau."""
        inserted_row = self.table.rowCount()
        self.table.insertRow(inserted_row)
        print(f"Ligne {inserted_row + 1} ajoutée au tableau.")
        self.update_delete_button_state()

    def delete_row(self):
        """Supprime la ligne sélectionnée dans le tableau."""
        selected_row = self.table.currentRow()
        # Il doit y avoir plus d'une ligne pour pouvoir supprimer
        if self.table.rowCount() > 1:
            self.table.removeRow(selected_row)
            print(f"Ligne {selected_row + 1} supprimée du tableau.")
        else:
            self.show_error_popup("Il doit y avoir au moins deux lignes dans le tableau.")

        self.update_delete_button_state()

    def on_item_changed(self, item):
        """Réagit aux changements dans les cellules du tableau."""
        col = item.column()
        
        # Vérifier si le nom de la séquence est deja utilisé
        if col == 0 and item.text() != "":
            value = item.text()
            row = item.row()
            for i in range(self.table.rowCount()):
                if i != row:
                    other_item = self.table.item(i, col)
                    if other_item and other_item.text() == value:
                        self.show_error_popup("Ce nom est deja utilisé.")
                        item.setText("")
                        return
        # Restriction des colonnes "Début" et "Fin" à des valeurs numériques
        elif col in [3, 4]:
            try:
                if item.text() != "":
                    value = int(item.text())  # Vérifie si c'est un entier
                    item.setText(str(value))  # Remet au format numérique
            except ValueError:
                item.setText("")  # Remet la cellule à vide
                self.show_error_popup("Cette cellule n'accepte que des valeurs numériques.")
        
        # Centre le texte dans toutes les cellules
        item.setTextAlignment(Qt.AlignCenter)

    def show_error_popup(self, message):
        """Affiche une popup d'erreur."""
        popup = QMessageBox(self)
        popup.setIcon(QMessageBox.Warning)
        popup.setWindowTitle("Erreur")
        popup.setText(message)
        popup.exec()

    def update_delete_button_state(self):
        """Met à jour l'état du bouton de suppression."""
        if self.table.rowCount() > 1:
            self.delete_row_button.setEnabled(True)
        else:
            self.delete_row_button.setEnabled(False)

    def adjust_table_columns(self):
        """Ajuste la largeur des colonnes en fonction de la fenêtre, sans dépasser la taille de la fenêtre."""
        total_width = self.width() - 35  # Prendre en compte les marges de la fenêtre
        column_width = total_width // 5  # Divise l'espace disponible par 4 pour chaque colonne
        for col in range(self.table.columnCount()):
            self.table.setColumnWidth(col, column_width)

    def dragEnterEvent(self, event):
        """Permet de gérer l'événement de drag, ici on accepte uniquement les fichiers."""
        if event.mimeData().hasUrls():
            event.accept()  # Accepte l'événement de drag
        else:
            event.ignore()  # Ignore si ce n'est pas un fichier

    def dropEvent(self, event):
        """Gère l'événement de drop et récupère le fichier déposé."""
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]  # On récupère la première URL du mimeData
            file_path = url.toLocalFile()  # Convertit l'URL en chemin local
            self.file_input.setText(file_path)  # Mets le chemin dans le QLineEdit
            self.auto_search() # lance l'auto-search après le drop

    def move_up(self):
        """Déplace la ligne sélectionnée vers le haut."""
        row = self.table.currentRow()
        if row > 0:  # Vérifie que la ligne n'est pas déjà la première
            self.swap_rows(row, row - 1)  # Échange la ligne avec la ligne au-dessus
            self.table.setCurrentCell(row - 1, 0)  # Re-sélectionne la ligne déplacée vers le haut

    def move_down(self):
        """Déplace la ligne sélectionnée vers le bas."""
        row = self.table.currentRow()
        if row < self.table.rowCount() - 1:  # Vérifie que la ligne n'est pas déjà la dernière
            self.swap_rows(row, row + 1)  # Échange la ligne avec la ligne en dessous
            self.table.setCurrentCell(row + 1, 0)  # Re-sélectionne la ligne déplacée vers le bas

    def swap_rows(self, row1, row2):
        """Échange les lignes row1 et row2 dans le tableau."""
        for col in range(self.table.columnCount()):
            item1 = self.table.item(row1, col)
            item2 = self.table.item(row2, col)

            # Récupérer les valeurs des cellules
            value1 = item1.text() if item1 else ""
            value2 = item2.text() if item2 else ""

            # Supprimer les valeurs avant d'échanger 
            # pour ne pas trigger le message d'erreur de "on_item_changed"
            if item1:
                self.table.setItem(row1, col, QTableWidgetItem(""))
            if item2:
                self.table.setItem(row2, col, QTableWidgetItem(""))
            
            # Échanger les valeurs
            self.table.setItem(row1, col, QTableWidgetItem(value2))
            self.table.setItem(row2, col, QTableWidgetItem(value1))

def run_app():
    """Lance l'interface graphique."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
