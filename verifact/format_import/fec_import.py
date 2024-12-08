import polars as pl
from pathlib import Path
from PySide6.QtWidgets import QMessageBox

def import_FEC(filename, key):
    """Liste les factures de vente d'un FEC"""
    
    if Path(filename).suffix.lower() != ".txt":
        QMessageBox.critical(None, "Erreur de format", 
        "Le format FEC nécessite un fichier .txt")
        return
    
    with open(filename, "r") as file:
        lignes = file.readlines()
        
        # Reconnaissance auto du séparateur du fichier format FEC
        nb_tabulations = sum(ligne.count('\t') for ligne in lignes)
        nb_verticales = sum(ligne.count('|') for ligne in lignes)

        if nb_tabulations > nb_verticales:
            separateur = '\t'
        elif nb_verticales > nb_tabulations:
            separateur = '|'
        else:
            QMessageBox.critical(None, "Erreur de format", 
            "Séparateur FEC non identifié")
            return

    # Permet de changer l'encodage si un problème d'import survient
    # Utile par exemple pour les imports de FEC de Sage
    try:
        df = pl.read_csv(filename, separator=separateur)
    except pl.exceptions.ComputeError:
        df = pl.read_csv(filename, separator=separateur, encoding='ISO-8859-1')
    
    if "Sens" in df.columns and "Montant" in df.columns:
        # Rajout de la colonne Débit
        df = df.with_columns((pl.when(pl.col("Sens") == "D")
                        .then(pl.col("Montant"))
                        .otherwise(pl.lit(0.0))
                        .alias("Debit")
                        ))
        # Rajout de la colonne Crédit
        df = df.with_columns((pl.when(pl.col("Sens") == "C")
                        .then(pl.col("Montant"))
                        .otherwise(pl.lit(0.0))
                        .alias("Credit")
                        ))
        # Suppression des colonnes Montant et Sens
        df = df.drop(["Montant", "Sens"])

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
    
    # Conserve uniquement les comptes clients pour lister les factures
    df = df.filter(pl.col("CompteNum").str.contains(key))
    
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
    
    return df
