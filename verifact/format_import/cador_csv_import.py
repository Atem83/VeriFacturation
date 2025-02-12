import polars as pl
from .base_import import BaseImport
from verifact.error import run_error

class CadorCsvImport(BaseImport):
    def name(self):
        return "CADOR/ComptabilitéExpert (.csv)"
    
    def validate_format(self):
        if self.path.suffix.lower() != ".csv":
            run_error("Ce format CADOR nécessite un fichier .csv")
            return False
        return True

    def process_file(self):
        with open(self.filename, mode='r', encoding='ANSI') as file:
            first_line = file.readline()  # Lire la première ligne
        
        # Vérifie que le type de fichier est correct
        if first_line.strip().replace(';','') != 'Edition Journaux':
            run_error("Il ne s'agit pas d'un journal de vente")
            return []
        
        # Je lui donne un schéma pour éviter des erreurs de infer_schema
        schema = {
            "Jour": pl.String,
            "Pièce": pl.String,
            "Libellé de l'écriture": pl.String,
            "Compte": pl.String,
            "Intitulé": pl.String,
            "Débit": pl.Float64,
            "Crédit": pl.Float64
        }
        
        # Importation des données
        df = pl.read_csv(self.filename, separator=";", 
                         skip_rows=1, encoding='ANSI', 
                         decimal_comma=True, schema=schema
                         )
        
        # Renommer les colonnes
        df.columns = [
            "EcritureDate", "PieceRef", "EcritureLib", 
            "CompteNum", "CompteLib", "Debit", "Credit"
            ]
        
        # Listing des mois de l'année
        months = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
            ]

        # Ajouter un compteur de lignes
        df = df.with_row_index(name="Row")

        # Filtrer les mois
        months_condition = pl.lit(False)
        for month in months:
            months_condition |= pl.col("CompteLib").str.starts_with(month)
        results = df.filter(months_condition)
        
        # Ajouter les colonnes Year, MonthNumber, et End
        results = results.with_columns([
            (pl.col("CompteLib").str.slice(-4)).cast(pl.Int64).alias("Year"),
            (pl.lit(None)).alias("MonthNumber").cast(pl.Int64),
            (pl.col("Row")).cast(pl.Int64).alias("Start"),
            (pl.lit(None)).alias("End").cast(pl.Int64)
        ])
        
        # Récupération du nom du mois
        results = results.with_columns(
            pl.col("CompteLib").str.slice(
                0, 
                (pl.col("CompteLib").str.len_chars()) - 5
            ).alias("Month")
        )
        
        # Récupération du numéro de mois
        results = results.with_columns(
            pl.when(pl.col("Month") == "Janvier").then(1)
            .when(pl.col("Month") == "Février").then(2)
            .when(pl.col("Month") == "Mars").then(3)
            .when(pl.col("Month") == "Avril").then(4)
            .when(pl.col("Month") == "Mai").then(5)
            .when(pl.col("Month") == "Juin").then(6)
            .when(pl.col("Month") == "Juillet").then(7)
            .when(pl.col("Month") == "Août").then(8)
            .when(pl.col("Month") == "Septembre").then(9)
            .when(pl.col("Month") == "Octobre").then(10)
            .when(pl.col("Month") == "Novembre").then(11)
            .when(pl.col("Month") == "Décembre").then(12)
            .alias("MonthNumber")
        )
        
        # Mettre à jour 'End'
        for i in range(len(results)):
            current_start = results[i, "Start"]
            
            # La valeur end est la valeur qui précède le start suivant
            end = results.filter(pl.col("Start") > current_start)["Start"].min()
            if end is not None:
                end -= 1
            else:
                end = len(df)
            results[i, "End"] = end
        
        # On conserve les colonnes utiles
        results = results.select(["Month", "MonthNumber", "Year", "Start", "End"])
        results_dict = results.to_dicts()

        # On ne conserve que les lignes qui ont une date pour retirer les totaux et titres
        df = df.with_columns(pl.col("EcritureDate").cast(pl.String))
        df = df.filter(pl.col("EcritureDate").is_not_null())

        # Recréer des dates au format JJ/MM/AAAA
        for result in results_dict:
            df = df.with_columns(
                pl.when(
                (pl.col("Row") >= result["Start"]) & 
                (pl.col("Row") <= result["End"])
                )
                  .then(pl.col("EcritureDate") + 
                        f"/{result["MonthNumber"]}/{result['Year']}"
                        )
                  .otherwise(pl.col("EcritureDate"))
                  .alias("EcritureDate")
            )
        df = df.with_columns(pl.col("EcritureDate")
                               .str.strptime(pl.Date, "%d/%m/%Y")
                            )

        # Donne le dataframe à la variable de classe
        self._sales = df
