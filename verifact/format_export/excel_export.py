import re
import polars as pl
from pathlib import Path
from PySide6.QtCore import QStandardPaths
from xlsxwriter import Workbook
from ..format_invoice import *

def create_df_global(manager: SerialManager, type: str):
    """Compile dans une liste globale les factures manquantes ou les doublons de chaque séquence.

    Args:
        serial_list (SerialManager): liste des séquences de factures
        type (str): 'missing' ou 'duplicate'

    Returns:
        pl.DataFrame: dataframe global contenant la liste 'missing' ou 'duplicate' compilée
    """
    
    modele_df = pl.DataFrame({
            "Janvier": pl.Series(dtype=pl.Utf8),
            "Février": pl.Series(dtype=pl.Utf8),
            "Mars": pl.Series(dtype=pl.Utf8),
            "Avril": pl.Series(dtype=pl.Utf8),
            "Mai": pl.Series(dtype=pl.Utf8),
            "Juin": pl.Series(dtype=pl.Utf8),
            "Juillet": pl.Series(dtype=pl.Utf8),
            "Aout": pl.Series(dtype=pl.Utf8),
            "Septembre": pl.Series(dtype=pl.Utf8),
            "Octobre": pl.Series(dtype=pl.Utf8),
            "Novembre": pl.Series(dtype=pl.Utf8),
            "Décembre": pl.Series(dtype=pl.Utf8)
        })
    
    df_global = modele_df
    
    # Construit les listes mensuelles de factures manquantes et de factures doublons
    for serial in manager.serial_list:
        if type == "missing":
            df = serial.missing
        elif type == "duplicate":
            df = serial.duplicate
        else:
            raise ValueError("type must be 'missing' or 'duplicate'")
        
        # Rajoute des colonnes mensuelles au df
        df = pl.concat([df, modele_df], how="horizontal")
        
        # Répartis les numéros de factures manquants par mois
        df = df.with_columns(
            pl.when(pl.col("EcritureDate").dt.month().eq(1))
                .then("PieceRef")
                .alias("Janvier"),
            pl.when(pl.col("EcritureDate").dt.month().eq(2))
                .then("PieceRef")
                .alias("Février"),
            pl.when(pl.col("EcritureDate").dt.month().eq(3))
                .then("PieceRef")
                .alias("Mars"),
            pl.when(pl.col("EcritureDate").dt.month().eq(4))
                .then("PieceRef")
                .alias("Avril"),
            pl.when(pl.col("EcritureDate").dt.month().eq(5))
                .then("PieceRef")
                .alias("Mai"),
            pl.when(pl.col("EcritureDate").dt.month().eq(6))
                .then("PieceRef")
                .alias("Juin"),
            pl.when(pl.col("EcritureDate").dt.month().eq(7))
                .then("PieceRef")
                .alias("Juillet"),
            pl.when(pl.col("EcritureDate").dt.month().eq(8))
                .then("PieceRef")
                .alias("Aout"),
            pl.when(pl.col("EcritureDate").dt.month().eq(9))
                .then("PieceRef")
                .alias("Septembre"),
            pl.when(pl.col("EcritureDate").dt.month().eq(10))
                .then("PieceRef")
                .alias("Octobre"),
            pl.when(pl.col("EcritureDate").dt.month().eq(11))
                .then("PieceRef")
                .alias("Novembre"),
            pl.when(pl.col("EcritureDate").dt.month().eq(12))
                .then("PieceRef")
                .alias("Décembre")
        )

        # Conserve uniquement les colonnes mensuelles
        df = df.select(modele_df.columns)
        
        # Fusionne le df de cette séquence de numérotation avec le df global
        df_global = pl.concat([df_global, df])

    # Tri les df par ordre croissant des numéros de factures
    df_global = df_global.with_columns(
        [pl.col(col).sort(nulls_last=True) for col in df_global.columns]
    )
    
    # Supprime les lignes ne contenant que des valeurs None
    df_global = df_global.filter(~pl.all_horizontal(pl.all().is_null()))

    return df_global

def create_statistics(invoice):
    """Présente les statistiques des séquences de facturations contrôlées."""
    
    real_invoice_count = 0
    theory_invoice_count = 0
    deviation_count = 0
    missing_count = 0
    duplicate_count = 0
    remaining_count = 0
    
    for serial in invoice.serial.serial_list:
        real_invoice_count += serial.invoices.height
        theory_invoice_count += serial.end - serial.start + 1
        missing_count += serial.missing.height
        duplicate_count += serial.duplicate["n"].sum()
        
    deviation_count += theory_invoice_count - real_invoice_count
    remaining_count = invoice.remaining.height

    # Créer un DataFrame Polars
    df = pl.DataFrame({
        "Titres": [
            "Nb fact. compta", 
            "Nb fact. théorique", 
            "Écarts", 
            "Nb fact. manquantes", 
            "Nb doublons", 
            "Nb fact. non traitées"
            ],
        "Valeurs": [
            real_invoice_count, 
            theory_invoice_count, 
            deviation_count, 
            missing_count, 
            duplicate_count, 
            remaining_count
            ]
    })
    
    return df

def increment_path(filename):
    """Incrémente le nom du fichier de (1) s'il existe déjà
    
    Args:
        filename (str): nom du fichier
    Returns:
        file_path (str) : nouveau nom du fichier
    """
    
    desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
    file_path = Path(desktop_path) / filename
    
    while file_path.exists():
        # Sépare le nom du fichier et son extension
        nom_brut = Path(file_path).stem
        extension = Path(file_path).suffix.lower()
        
        # Chercher le motif de la forme "(x)" à la fin du nom de fichier
        match = re.search(r'(\(\d+\))$', nom_brut)
        
        if match:
            # Extraire le nombre entre parenthèses et l'incrémenter
            numero = int(match.group(1).strip('()')) + 1
            # Remplacer l'ancien numéro par le nouveau
            nouveau_nom = re.sub(r'\(\d+\)$', f'({numero})', nom_brut)
        else:
            # Ajouter "(1)" à la fin du nom du fichier
            nouveau_nom = nom_brut + " (1)"
            
        file_path = Path.home() / "Desktop" / (nouveau_nom + extension)
    
    return file_path

def export_excel(invoice):
    """Exporte sous Excel les résultats des factures manquantes et doublons.
    Args:
        invoice (Invoice): Instance de la classe Invoice
    """
    
    path_wb = increment_path("FACTURES DE VENTE.xlsx")
    
    # Création de l'export sous excel avec polars et xlsxwriter
    with Workbook(path_wb) as wb:
        # - - - - - - - - - - Feuille de synthèse - - - - - - - - - - - - - - -
        ws = wb.add_worksheet("Synthèse")

        # Écrire le titre de la feuille
        title = "VÉRIFICATION DU NOMBRE DE FACTURES DE VENTES"
        format_cell = wb.add_format({'font_size': 16, 'bold': True, 'align': 'center'})
        ws.merge_range("A1:L1", title, format_cell)
        
        # Écrire les statistiques
        dict_col = {
            "Titres": {"align": "left"},
            "Valeurs": {"align": "center"},
        }
        df = create_statistics(invoice)
        df.write_excel(
            workbook=wb,
            worksheet=ws,
            position="A3",
            table_style="TableStyleMedium2",
            column_formats=dict_col,
            include_header=False,
            autofit=True
        )
        
        startLine = 10
        dict_col = {
            "Janvier": {"align": "center"},
            "Février": {"align": "center"},
            "Mars": {"align": "center"},
            "Avril": {"align": "center"},
            "Mai": {"align": "center"},
            "Juin": {"align": "center"},
            "Juillet": {"align": "center"},
            "Aout": {"align": "center"},
            "Septembre": {"align": "center"},
            "Octobre": {"align": "center"},
            "Novembre": {"align": "center"},
            "Décembre": {"align": "center"},
        }
        
        # Écrire la liste des factures manquantes
        df_missing = create_df_global(invoice.serial, "missing")
        if df_missing.height > 0:
            title = "Liste des factures manquantes"
            format_cell = wb.add_format({'font_size': 14, 'bold': True, 'align': 'center'})
            ws.merge_range(f"A{startLine}:L{startLine}", title, format_cell)
        
            df_missing.write_excel(
                workbook=wb,
                worksheet=ws,
                position=f"A{startLine + 1}",
                table_style="TableStyleMedium2",
                column_formats=dict_col,
                header_format={"bold":True, "align":"center"},
                include_header=True,
                autofilter=False,
                autofit=True
            )
            startLine += df_missing.height + 3
        
        # Écrire la liste des doublons de factures
        df_duplicate = create_df_global(invoice.serial, "duplicate")
        if df_duplicate.height > 0:
            title = "Liste des doublons de factures"
            format_cell = wb.add_format({'font_size': 14, 'bold': True, 'align': 'center'})
            ws.merge_range(f"A{startLine}:L{startLine}", title, format_cell)
            
            df_duplicate.write_excel(
                workbook=wb,
                worksheet=ws,
                position=f"A{startLine + 1}",
                table_style="TableStyleMedium2",
                column_formats=dict_col,
                header_format={"bold":True, "align":"center"},
                include_header=True,
                autofilter=False,
                autofit=True
            )
        
        # Je réarrange la longueur de la première colonne à cause du titre
        ws.set_column("A:A", 20)
        
        # - - - - - - - - - - Feuille des factures non traitées - - - - - - - -
        if invoice.remaining.height > 0:
            ws_remaining = wb.add_worksheet("Non traitées")

            # Écrire le titre de la feuille
            title = "FACTURES NON TRAITÉES"
            format_cell = wb.add_format({'font_size': 16, 'bold': True, 'align': 'center'})
            ws_remaining.merge_range("A1:F1", title, format_cell)

            # Modifier l'ordre des colonnes pour l'export
            df_remaining = invoice.remaining.select(
                "EcritureDate",
                "PieceRef",
                "CompteNum",
                "EcritureLib",
                "Debit",
                "Credit"
            )
            
            dict_col = {
            "EcritureDate": {"align": "center"},
            "PieceRef": {"align": "center"},
            "CompteNum": {"align": "center"},
            "EcritureLib": {"align": "left"},
            "Debit": {"align": "center"},
            "Credit": {"align": "center"}
            }
            
            # Écrire la liste des factures non traitées
            df_remaining.write_excel(
                workbook=wb,
                worksheet=ws_remaining,
                position="A3",
                table_style="TableStyleMedium2",
                column_formats=dict_col,
                dtype_formats={pl.Date: "dd/mm/yyyy"},
                header_format={"bold":True, "align":"center"},
                float_precision=2,
                include_header=True,
                autofit=True
            )
            
            # Je réarrange la longueur de la première colonne à cause du titre
            ws_remaining.set_column("A:A", 15)
            
        # - - - - - - - - - - Feuille(s) des séquences de factures - - - - - - -
        for serial in invoice.serial.serial_list:
            ws_serial = wb.add_worksheet(serial.name)
            
            # Écrire le titre de la feuille
            title = "LISTE DES FACTURES DE LA SÉQUENCE : " + serial.name
            format_cell = wb.add_format({'font_size': 16, 'bold': True, 'align': 'center'})
            ws_serial.merge_range("A1:F1", title, format_cell)
            
            # Modifier l'ordre des colonnes pour l'export
            df_invoices = serial.invoices.select(
                "EcritureDate",
                "PieceRef",
                "CompteNum",
                "EcritureLib",
                "Debit",
                "Credit"
            )
            
            # Écrire la liste des factures non traitées
            df_invoices.write_excel(
                workbook=wb,
                worksheet=ws_serial,
                position="A3",
                table_style="TableStyleMedium2",
                column_formats=dict_col,
                dtype_formats={pl.Date: "dd/mm/yyyy"},
                header_format={"bold":True, "align":"center"},
                float_precision=2,
                include_header=True,
                autofit=True
            )
            
            # Je réarrange la longueur de la première colonne à cause du titre
            ws_serial.set_column("A:A", 15)
