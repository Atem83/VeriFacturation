from tkinter import filedialog
from invoice import Invoice
import polars as pl

"""
Créer mon fichier de vérification des factures de vente

Auteur : Michaël AUGUSTE
"""

file = filedialog.askopenfilename(title="Sélectionner le journal de vente")
factures = Invoice(file)

factures.import_invoices("CADOR")

find_pattern = factures
patterns = find_pattern.infer_pattern()

for pattern in patterns:
    factures.serial.add_serial(
        prefix=pattern["prefix"], 
        suffix=pattern["suffix"], 
        start=pattern["start"], 
        end=pattern["end"]
        )
factures.search_pattern()
factures.search_missing()
factures.search_duplicate()

factures.export()

# Créer un onglet par serial pour print le dataframe


# Interface graphique : 
# Obliger l'utilisateur à donner des noms uniques aux différentes séquences
# sauf s'il laisse vide, dans ce cas le programme donnera un nom unique

