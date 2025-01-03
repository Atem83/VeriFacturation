import os
import polars as pl
from .format_import import import_classes, import_names
from .format_invoice import *
from .format_export import *

class Invoice:
    def __init__(self, 
                 filename: str | None = None,
                 customer_key: str = 'C'
                 ):
        
        self._invoices = None
        self.filename = filename
        self.customer_key = customer_key
        self.serial = SerialManager()
    
    @property
    def filename(self):
        """Nom du fichier à importer"""
        return self._filename
    
    @filename.setter
    def filename(self, file):
        if file is None or os.path.isfile(file):
            self._filename = file
        else:
            msg = "Le fichier n'existe pas"
            raise FileNotFoundError(msg)
    
    @property
    def customer_key(self):
        """Préfixe client qui est utilisé pour identifier les comptes clients"""
        return self._customer_key
    
    @customer_key.setter
    def customer_key(self, key):
        self._customer_key = key
    
    @property
    def invoices(self):
        """Liste des factures à contrôler"""
        
        if self._invoices is None:
            msg = (" Il faut initialiser une liste de factures avec " +
                "import_invoices avant d'utiliser cette fonction")
            raise ValueError(msg)
        
        return self._invoices
    
    @invoices.setter
    def invoices(self, df: pl.DataFrame):
        headers = [
            "PieceRef", 
            "EcritureDate", 
            "EcritureLib", 
            "CompteNum", 
            "Debit", 
            "Credit"
        ]
        
        # Vérifie que toutes les colonnes sont trouvées
        for header in headers:
            if header not in df.schema:
                msg = (f"La colonne {header} n'a pas été trouvée")
                raise ValueError(msg)
        
        # Permet de régler les paramètres des variables float
        pl.Config(decimal_separator=",", float_precision=2)

        # Permet d'éviter un nombre anormal de chiffres après la virgule
        df = df.with_columns([pl.col(pl.Float64).round(2),
                            pl.col(pl.Float32).round(2)])

        self._invoices = df
    
    @property
    def remaining(self):
        """Numéros de facture dont le format n'a pas été reconnu"""
        
        df_waste = self.invoices
        for serial in self.serial.serial_list:
            if serial.invoices is None:
                msg = "Il faut utiliser search_pattern avant d'utiliser cette fonction"
                raise ValueError(msg)
                
            df_waste = df_waste.filter(
                ~pl.col("PieceRef").is_in(
                    serial.invoices["PieceRef"]
                    )
                )
        
        return df_waste
    
    @property
    def import_names(self):
        """Nom des classes d'import"""
        return import_names
    
    def import_invoices(self, source: str):
        """Importe une liste de factures sous forme de pl.DataFrame
        
        Parameters
        ----------
        source
            Il y a le choix entre les formats suivants :
            * "CADOR/ComptabilitéExpert (.csv)"
            * "CADOR/ComptabilitéExpert (.xlsx)"
            * "FEC"
        """
        
        if source not in self.import_names:
            msg = f"Le format {source} n'est pas reconnu"
            raise ValueError(msg)
        
        # Appel la méthode d'import choisie par l'utilisateur
        for cls in import_classes:
            if source == cls().name():
                self.invoices = cls(
                    self.filename,
                    self.customer_key
                ).invoices
                break
    
    def search_pattern(self, case_insensitive: bool = True):
        """Filtre les factures en fonction du format de numérotation
        et retourne les numéros correspondants"""
        
        # Détermine si la recherche du pattern est sensible aux majuscules
        if case_insensitive:
            flag = "(?i)"
        else:
            flag = ""
        
        list_remove = [] # Permet de supprimer les serial vide
        
        for serial in self.serial.serial_list:
            # Détermination du pattern à rechercher
            if serial.prefix is None and serial.suffix is None:
                pattern = rf"{flag}^(\d+)$"
            elif serial.prefix is None:
                pattern = rf"{flag}^(\d+){serial.suffix}$"
            elif serial.suffix is None:
                pattern = rf"{flag}^{serial.prefix}(\d+)$"
            else:
                pattern = rf"{flag}^{serial.prefix}(\d+){serial.suffix}$"
            
            # Création de la numérotation en retirant le prefix et suffix
            df = self.invoices.filter(
                pl.col("PieceRef").str.contains(pattern)).with_columns(
                    pl.col("PieceRef").str.extract(pattern, 1).alias("Number")
                    )
            
            # Si le serial ne contient aucune facture, on passe à la boucle suivante
            if len(df) == 0:
                list_remove.append(serial.name)
                continue
            
            # Création de la longueur de la numérotation qui servira plus tard
            # Transformation de la numérotation en format integer
            df = df.select([
                    pl.col("PieceRef"),
                    pl.col("Number").str.len_chars().alias("Length"),
                    pl.col("Number").cast(pl.Int64),
                    pl.col("EcritureDate"),
                    pl.col("EcritureLib"),
                    pl.col("CompteNum"),
                    pl.col("Debit"),
                    pl.col("Credit")
                ])
            
            # Tri des factures en fonction de la numérotation
            df = df.sort(by="Number")
            
            # Remplis automatiquement les numéros de debut et de fin
            if serial.start is None:
                serial.start = int(str(df["Number"].min()))
            if serial.end is None:
                serial.end = int(str(df["Number"].max()))
                
            # Filtre les factures pour ne conserver que celles dans l'intervalle start-end
            # Permet de respecter ces limites si l'utilisateur a indiqué un start ou un end personnalisé
            df = df.filter(
                (pl.col("Number") >= serial.start) & 
                (pl.col("Number") <= serial.end)
            )
            
            # Sauvegarde la liste des factures dans le serial
            serial.invoices = df
        
        # Suppression des serial dont la liste de factures est vide
        for serial in list_remove:
            self.serial.del_serial(serial)

    def search_missing(self):
        """Recherche les numéros de factures manquants dans la liste"""
        
        for serial in self.serial.serial_list:
            if serial.invoices is None:
                msg = "Il faut utiliser search_pattern avant d'utiliser cette fonction"
                raise ValueError(msg)
            
            # Calcul de tous les numéros possibles
            df_control = pl.DataFrame(
                {"Number": range(serial.start, serial.end + 1)}
            )
            
            # Récupère EcritureDate pour chaque valeur de Number
            df_control = df_control.join(
                serial.invoices[["Number", "EcritureDate"]], 
                on="Number", 
                how="left"
            )
            df_control = df_control.select(pl.all().backward_fill())
            df_control = df_control.select(pl.all().forward_fill())
            
            # Recherche des numéros manquants
            df_missing = df_control.filter(
                ~pl.col("Number").is_in(serial.invoices["Number"])
            )
            
            # Ajout de la colonne PieceRef en fonction des numéros manquants
            length = int(serial.invoices["Length"].mode()[0])
            df_missing = df_missing.with_columns(
                PieceRef=(
                    (str(serial.prefix) if serial.prefix is not None else "") + 
                    pl.col("Number").cast(pl.Utf8).str.zfill(length) + 
                    (str(serial.suffix) if serial.suffix is not None else "")
                )
            )
            
            serial.missing = df_missing

    def search_duplicate(self):
        """Recherche les numéros de factures en doublon dans la liste"""
        
        for serial in self.serial.serial_list:
            if serial.invoices is None:
                msg = "Il faut utiliser search_pattern avant d'utiliser cette fonction"
                raise ValueError(msg)
            
            # Compte le nombre d'occurences de chaque numéro
            df_duplicate = serial.invoices["Number"].value_counts(sort=True, name="n")
            df_duplicate = df_duplicate.with_columns(pl.col("n") - 1)
            
            # Récupère un EcritureDate et PieceRef pour chaque valeur de Number
            df_duplicate = df_duplicate.join(
                serial.invoices[["Number", "EcritureDate", "PieceRef"]], 
                on="Number", 
                how="left"
            ).unique("Number").sort(by="Number")
            
            # Ne conserve que les valeurs qui sont en doublon
            serial.duplicate = df_duplicate.filter(pl.col("n") > 0)
    
    def infer_pattern(self, count: int = 3, case_insensitive: bool = True):
        """Retourne un dictionnaire contenant les motifs de numérotations 
        qui ont été déduits.
        
        Args:
            count (int): nombre d'occurences minimum pour considérer qu'il s'agit d'un motif de séquence de factures
            case_insensitive (bool): indique si la recherche est insensible à la casse
        """
        
        if not isinstance(count, int):
            raise TypeError("La variable 'count' n'accepte que des nombres entiers.")
        if not isinstance(case_insensitive, bool):
            raise TypeError("La variable 'case_insensitive' n'accepte que des booleans.")

        df = self.invoices
        
        # Si on veut ignorer la casse, transforme tout en majuscule
        if case_insensitive:
            df = df.with_columns(
                pl.col("PieceRef").str.to_uppercase().alias("PieceRef")
            )

        # Extraire la dernière séquence numérique
        df = df.with_columns(
            pl.col("PieceRef")
            .str.reverse() # inverse la chaine
            .str.extract(r"(\d+)", 1)  # Extrait la première séquence numérique
            .str.reverse()  # Remet la chaine dans le bon ordre
            .alias("last_number")
        )

        # Filtrer pour ne garder que les factures ayant des séquences numériques
        df = df.filter(pl.col("last_number").is_not_null())

        # Extraire l'index de début de la dernière occurence du pattern
        df = df.with_columns([
            (
                pl.col("PieceRef").str.len_chars() - 
                pl.col("PieceRef").str.reverse()
                                  .str.find(pl.col("last_number").str.reverse()) - 
                pl.col("last_number").str.len_chars()
            ).alias("start_index")
        ])
        
        # Extraire l'index de fin de la dernière occurence du pattern
        df = df.with_columns(
            (pl.col("start_index") + pl.col("last_number").str.len_chars()).alias("end_index")
        )

        # Extraire les préfixes et suffixes
        df = df.with_columns(
            pl.col("PieceRef").str.slice(0, pl.col("start_index")).alias("prefix"),
            pl.col("PieceRef").str.slice(pl.col("end_index")).alias("suffix")
        )

        # Remplacer les valeurs vides par None
        df = df.with_columns(
            pl.when(pl.col("prefix") == "")
            .then(None)
            .otherwise(pl.col("prefix"))
            .alias("prefix"),

            pl.when(pl.col("suffix") == "")
            .then(None)
            .otherwise(pl.col("suffix"))
            .alias("suffix")
        )

        # Regrouper les paires préfixes/suffixes uniques
        df = df.group_by(["prefix", "suffix"]).agg(
            pl.col("last_number").cast(pl.Int64).min().alias("start"),
            pl.col("last_number").cast(pl.Int64).max().alias("end"),
            pl.len().alias("count")
        )

        # Conserver les pattern qui ont un certain nombre d'occurences trouvées
        df = df.filter(pl.col("count") >= count).drop("count")

        return df.to_dicts()
        
    def export(self):
        """Exporte les résultats dans un fichier Excel"""
        export_excel(self)
        

