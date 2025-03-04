from pathlib import Path
from PySide6.QtWidgets import (
    QFrame, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from verifact.invoice import Invoice
from verifact.error import run_error
import traceback

class MainWindow(QFrame):
    """Fenêtre principale."""
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.app = parent
        layout = QVBoxLayout(self)

        layout.addLayout(self.init_file())
        layout.addLayout(self.init_format())
        layout.addWidget(self.init_auto_serial())
        layout.addWidget(self.init_table_label())
        layout.addWidget(self.init_table())
        layout.addLayout(self.init_create_row())
        layout.addLayout(self.init_move_row())
        layout.addWidget(self.init_exe())

    def init_file(self):
        """Initialise le champ de texte du fichier."""
        file_layout = QHBoxLayout()
        file_label = QLabel("Fichier :")
        self.file_input = QLineEdit()
        msg = ("Vous pouvez glisser-déposer un fichier dans la fenêtre\n" +
               "ou cliquer sur 'Parcourir'")
        self.file_input.setToolTip(msg)
        browse_button = QPushButton("Parcourir")
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(browse_button)
        return file_layout

    def init_format(self):
        """Initialise le champ format du fichier à importer."""
        format_layout = QHBoxLayout()
        format_label = QLabel("Format :")
        self.format_dropdown = QComboBox()
        self.format_dropdown.addItems(Invoice().import_names)
        self.format_dropdown.setToolTip(
            "CADOR : Journal de vente de Cador au format .xlsx ou .csv\n" + 
            "FEC : Fichier des Ecritures Comptables au format .txt")
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_dropdown)
        return format_layout

    def init_auto_serial(self):
        """Initialise le bouton 'Séquence auto'."""
        auto_search_button = QPushButton("Séquence auto")
        auto_search_button.setToolTip(
            "Cliquez ici pour rechercher automatiquement\n" +
            "les séquences de numérotation.")
        auto_search_button.clicked.connect(self.auto_search)
        return auto_search_button

    def init_table_label(self):
        """Initialise le label du tableau."""
        table_label = QLabel("Séquences de numérotation")
        table_label.setAlignment(Qt.AlignCenter)  # Centrer le label
        return table_label

    def init_table(self):
        """Initialise le tableau."""
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
            "Conseil : vérifiez que le numéro soit bien celui de la derniere facture.")

        # Centrer les valeurs dans les cellules et restreindre les colonnes "Début" et "Fin"
        self.table.itemChanged.connect(self.on_item_changed)
        
        return self.table

    def init_create_row(self):
        """Initialise les boutons pour ajouter/supprimer des lignes au tableau."""
        table_create_row_layout = QHBoxLayout()
        add_row_button = QPushButton("Ajouter une ligne")
        add_row_button.clicked.connect(self.add_row)
        self.delete_row_button = QPushButton("Supprimer une ligne")
        self.delete_row_button.clicked.connect(self.delete_row)
        self.delete_row_button.setEnabled(False)  # Désactiver par défaut
        table_create_row_layout.addWidget(add_row_button)
        table_create_row_layout.addWidget(self.delete_row_button)
        return table_create_row_layout

    def init_move_row(self):
        """Initialise les boutons pour bouger des lignes au tableau."""
        table_move_row_layout = QHBoxLayout()
        move_up_button = QPushButton("Déplacer vers le haut")
        move_up_button.clicked.connect(self.move_up)
        move_down_button = QPushButton("Déplacer vers le bas")
        move_down_button.clicked.connect(self.move_down)
        table_move_row_layout.addWidget(move_up_button)
        table_move_row_layout.addWidget(move_down_button)
        return table_move_row_layout

    def init_exe(self):
        """Initialise le bouton 'Exécuter le programme'."""
        launch_search_button = QPushButton("Exécuter le programme")
        launch_search_button.clicked.connect(self.launch_search)
        return launch_search_button

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
            run_error("Veuillez choisir un fichier.\n")
            return
        elif Path(self.file_input.text()).exists() == False:
            run_error("Le fichier n'existe pas.\n")
            return
        
        # Vider le tableau
        self.table.setRowCount(0)  # Supprime toutes les lignes
        self.table.insertRow(0)  # Ajoute une seule ligne vide
        
        # Rechercher le pattern des différentes séquences de facturation
        invoices = Invoice(
            self.file_input.text(),
            self.app.settings.client_root,
            self.app.settings.logs
            )
        invoices.import_invoices(self.format_dropdown.currentText())
        
        try:
            patterns = invoices.infer_pattern(
                count=self.app.settings.min_occurrences,
                case_insensitive=self.app.settings.case_insensitive
                )
        except Exception as e:
            traceback_info = traceback.format_exc()
            msg = "Une erreur est survenue dans la recherche automatique de séquences"
            run_error(message=msg, details=traceback_info)
        
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
            run_error("Veuillez choisir un fichier.\n")
            return
        elif Path(self.file_input.text()).exists() == False:
            run_error("Le fichier n'existe pas.\n")
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
            self.app.settings.client_root,
            self.app.settings.logs
            )
        invoices.import_invoices(self.format_dropdown.currentText())
        for row in data:
            if row[3] is not None:
                row[3] = int(row[3])
            if row[4] is not None:
                row[4] = int(row[4])
            
            try:
                invoices.serial.add_serial(
                    name=row[0],
                    prefix=row[1],
                    suffix=row[2],
                    start=row[3],
                    end=row[4]
                )
            except Exception as e:
                msg = f"""Une erreur est survenue 
                lors de la création de la séquence '{row[0]}'\n"""
                run_error(msg, details=e)
                return
        
        try:
            # Effectuer les recherches
            invoices.search_pattern(self.app.settings.case_insensitive)
            invoices.search_missing()
            invoices.search_duplicate()
            
            # Si aucune facture n'a pu être trouvée
            if invoices.invoices.height == 0:
                msg = (
                    "Aucune facture n'a pu être trouvée.\n\n" +
                    "Vérifiez que la racine client dans les paramètres soit correcte.\n"
                )
                run_error(msg)
                return
            
            # Si aucune facture n'a pu être traitée
            if invoices.remaining.height == invoices.invoices.height:
                msg = (
                    "Aucune facture n'a pu être traitée.\n\n" +
                    "Vérifiez que les préfixes et suffixes choisis soient corrects.\n"
                )
                run_error(msg)
                return
            
            # Si un grand nombre de factures manquantes sont trouvées dans une liste
            for serial in invoices.serial.serial_list:
                if serial.missing.height > 1000:
                    msg = f"Plus de 1000 factures manquantes ont été trouvées dans la séquence '{serial.name}'.\n\n"
                    msg += "Il s'agit probablement d'une erreur de paramétrage.\n\n"
                    msg += "Il vous est conseillé de revérifier les préfixes et suffixes choisis ainsi que les numéros de début et de fin pour chaque liste.\n\n"
                    msg += "Souhaitez-vous tout de même continuer ?"
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Erreur de paramétrage")
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setText(msg)
                    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    msg_box.setButtonText(QMessageBox.Yes, "Continuer")
                    msg_box.setButtonText(QMessageBox.No, "Annuler")
                    msg_box.setDefaultButton(QMessageBox.No)
                    response = msg_box.exec()
                    if response == QMessageBox.No:
                        return
            
            # Exporter les résultats
            invoices.export()
        except Exception as e:
            traceback_info = traceback.format_exc()
            run_error("Une erreur est survenue\n", details=traceback_info)

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
            msg = "La suppression d'une ligne n'est autorisée que s'il y en a au moins deux.\n"
            run_error(msg)

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
                        msg = f"Le nom de la séquence '{value}' est deja utilisé.\n"
                        run_error(msg)
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
                msg = f"Cette colonne accepte uniquement des valeurs numériques.\n"
                run_error(msg)
        
        # Centre le texte dans toutes les cellules
        item.setTextAlignment(Qt.AlignCenter)

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
