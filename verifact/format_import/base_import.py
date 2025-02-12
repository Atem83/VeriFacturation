from abc import ABC, abstractmethod
from pathlib import Path
from PySide6.QtWidgets import QMessageBox
import polars as pl
from verifact.error import run_error

class BaseImport(ABC):
    def __init__(self, filename: str | None = None, key: str = 'C'):
        self.filename = filename
        self.key = key
        self._sales = None
        
        if self.filename is not None:
            self.path = Path(filename)
            self.import_data()
    
    @abstractmethod
    def name(self) -> str:
        """Nom de l'importateur"""
        pass
    
    @abstractmethod
    def validate_format(self) -> bool:
        """Vérifie si le format du fichier est valide"""
        pass
    
    @abstractmethod
    def process_file(self):
        """Traite le fichier et retourne un dataframe de factures"""
        pass
    
    @property
    def sales_entries(self) -> pl.DataFrame:
        """Liste brute des écritures importées"""
        return self._sales
    
    @property
    def invoices(self) -> pl.DataFrame:
        """Liste des factures extraites des données brutes"""
        df = self.sales_entries
        df = self.num_ecritures(df)
        df = self.aggregate_key(df, self.key)
        return df
    
    def empty_df(self) -> pl.DataFrame:
        """Créer un dataframe vide"""
        return pl.DataFrame(schema={
            "PieceRef": pl.String,
            "EcritureDate": pl.Date,
            "EcritureLib": pl.String,
            "CompteNum": pl.String,
            "Debit": pl.Float64,
            "Credit": pl.Float64
        })
    
    def import_data(self):
        """Méthode principale d'import"""
        if not self.validate_format():
            self._sales = self.empty_df()
            return
            
        try:
            self.process_file()
        except Exception as e:
            run_error("Une erreur est survenue.", details=str(e))
            print(e)
            self._sales = self.empty_df()
            return
    
    def num_ecritures(self, df: pl.DataFrame):
        """Attribue un numéro unique à chaque écriture dans une liste d'écritures.

        Args:
            df (polars.DataFrame): dataframe des écritures

        Returns:
            (polars.DataFrame): dataframe des écritures avec les numéros uniques
        """

        # Calculer le solde cumulatif
        df = df.with_columns(
            (pl.col("Debit") - pl.col("Credit")).cum_sum().alias("solde")
        )

        # Marquer les endroits où le solde revient à zéro
        df = df.with_columns(
            (pl.col("solde").abs() < 1e-3).alias("reset")
        )

        # Décaler le signal de "reset" d'une ligne pour que l'incrément se fasse sur la ligne suivante
        df = df.with_columns(
            pl.col("reset").shift(1).fill_null(False).alias("shifted_reset")
        )

        # Générer un groupe d'incrémentation basé sur les resets décalés
        df = df.with_columns(
            pl.col("shifted_reset").cum_sum().alias("EcritureNum")
        )

        # Incrémentation finale et conversion de EcritureNum en String
        df = df.with_columns(
            (pl.col("EcritureNum") + 1).cast(pl.Utf8).alias("EcritureNum")
        )

        # Ajuster la longueur d'EcritureNum
        df = df.with_columns(
            pl.col("EcritureNum").str.zfill(
                pl.col("EcritureNum").str.len_chars().max()
                )
            )

        # Afficher le DataFrame final sans les colonnes temporaires
        df = df.drop(["solde", "reset", "shifted_reset"])

        return df

    def aggregate_key(self, df: pl.DataFrame, key: str):
        """Fait la somme des comptes clients d'une même facture et d'une même écriture

        Args:
            df (pl.DataFrame): dataframe des écritures comptables
            key (str): clé pour identifier les comptes clients

        Returns:
            pl.DataFrame: dataframe des comptes clients regroupés
        """

        # Groupe par PieceRef et agrège les valeurs débit et crédit
        df = df.group_by(
            [
                "PieceRef",
                "EcritureNum",
                pl.col("CompteNum").str.contains(key).alias("is_key")
            ]
        ).agg(
            pl.col("*").exclude(["Debit", "Credit", "is_key"]).first(),
            pl.col("Debit").sum(),
            pl.col("Credit").sum()
        ).filter(pl.col("is_key")).drop("is_key") # Conserve uniquement les comptes clients

        # Déduit les débits et crédits entre eux lorsqu'ils sont tous les deux mouvementés sur une seule ligne
        df = df.with_columns([
            pl.when(pl.col("Debit") > pl.col("Credit"))
            .then(pl.col("Debit") - pl.col("Credit"))
            .otherwise(0.0)
            .alias("Debit"),

            pl.when(pl.col("Credit") > pl.col("Debit"))
            .then(pl.col("Credit") - pl.col("Debit"))
            .otherwise(0.0)
            .alias("Credit")
        ])

        # Tri le dataframe et retire la colonne EcritureNum
        df = df.sort(by="PieceRef").drop("EcritureNum")

        return df
    
