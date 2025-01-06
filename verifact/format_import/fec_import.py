import polars as pl
from typing import List
from .base_import import BaseImport
from verifact.error import run_error

class FECImport(BaseImport):
    def name(self):
        return "FEC"
    
    def validate_format(self):
        if self.path.suffix.lower() != ".txt":
            run_error("Le format FEC nécessite un fichier .txt")
            return False
        return True
    
    def detect_separator(self, lines: List[str]) -> str:
        """Détecte le séparateur utilisé dans le fichier FEC"""
        nb_tab = sum(line.count('\t') for line in lines)
        nb_pipe = sum(line.count('|') for line in lines)

        if nb_tab > nb_pipe:
            return '\t'
        elif nb_pipe > nb_tab:
            return '|'
        else:
            run_error("Séparateur FEC non identifié")
            return ''
    
    def process_file(self):
        # Lecture du fichier pour détecter le séparateur
        with open(self.filename, "r") as file:
            lines = file.readlines()
            
        separator = self.detect_separator(lines)
        if not separator:
            return self.empty_df()

        # Lecture du fichier avec polars
        # infer_schema=False permet de cast tout en String pour éviter des erreurs
        # et on change le type de colonne plus tard
        try:
            df = pl.read_csv(self.filename, separator=separator, infer_schema=False)
        except pl.exceptions.ComputeError:
            try:
                # Correspond à l'encodage des FEC de Sage
                df = pl.read_csv(self.filename, separator=separator, 
                                 encoding='ISO-8859-1', infer_schema=False)
            except Exception as e:
                run_error("Impossible de lire le fichier.", details= str(e))
                return self.empty_df()

        # Retraitement des colonnes "Montant" et "Sens"
        if "Sens" in df.columns and "Montant" in df.columns:
            df = df.with_columns([
                pl.when(pl.col("Sens") == "D")
                .then(pl.col("Montant"))
                .otherwise(pl.lit(0.0))
                .alias("Debit"),
                
                pl.when(pl.col("Sens") == "C")
                .then(pl.col("Montant"))
                .otherwise(pl.lit(0.0))
                .alias("Credit")
            ]).drop(["Montant", "Sens"])

        # Transforme les colonnes en type String
        df = df.cast({
            "EcritureDate": pl.String, 
            "CompteNum": pl.String,
            "CompAuxNum": pl.String,
            "PieceRef": pl.String
            })
        
        # Remplace le compte général par le compte auxiliaire quand il y en a un
        df = df.with_columns(
            pl.when(pl.col("CompAuxNum").is_null() == False)
            .then(pl.col("CompAuxNum"))
            .otherwise(pl.col("CompteNum"))
            .alias("CompteNum")
        )
        
        # Affecte None aux colonnes Date ne contenant que des espaces blancs
        # Permet d'éviter des erreurs dans des FEC avec des espaces dans la date
        df = df.with_columns(
            pl.when(pl.col("EcritureDate").str.strip_chars() == "")
            .then(None)
            .otherwise(pl.col("EcritureDate"))
            .alias("EcritureDate")
        )
        
        # Transforme certains formats de colonnes
        df = df.with_columns(pl.col("EcritureDate").str.to_date("%Y%m%d"))
        df = df.with_columns(pl.col("Debit", "Credit")
                             .str.replace(",", ".")
                             .cast(pl.Float64))

        # Conserve uniquement les colonnes utiles
        df = df.select("PieceRef",
                       "EcritureDate",
                       "EcritureLib",
                       "CompteNum",
                       "Debit",
                       "Credit"
                        )
        
        self._sales = df
