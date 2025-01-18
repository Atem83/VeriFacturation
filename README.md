<h1 align="center">VeriFacturation</h1>

<h3 align="center">Vérifie les numéros de factures manquants et les numéros de factures en doublon.</h3>

<div align="center">
    
  [![PyPI](https://img.shields.io/pypi/v/VeriFacturation?style=flat)](https://pypi.org/project/VeriFacturation)
  <a href="https://opensource.org/license/mit">![License](https://img.shields.io/badge/License-MIT-blue)</a>
  <a href="https://github.com/Atem83/VeriFacturation/archive/refs/heads/main.zip">![Download](https://img.shields.io/badge/Source_Code-Download-blue)</a>
  ![LOC](https://tokei.rs/b1/github/Atem83/VeriFacturation?category=lines)
  
</div>


<div align="center">
    
![VeriFacturation Demo](https://raw.githubusercontent.com/Atem83/VeriFacturation/main/images/image_example.png)

</div>

<br>

<h2 align="center"> Fonctionnalités </h2>

- Tente de deviner les préfixes et suffixes des séquences de factures
- Cherche les factures manquantes de chaque séquence
- Cherche les doublons de chaque séquence
- Exporte les résultats au format Excel

<br>

<h2 align="center"> Formats d'import </h2>

- Fichier Ecritures Comptables (.txt) : "FEC"
- Journal des Ventes de Cador/ComptabilitéExpert d'ACD (.csv) : "CADOR/ComptabilitéExpert (.csv)"
- Journal des Ventes de Cador/ComptabilitéExpert d'ACD (.xlsx) : "CADOR/ComptabilitéExpert (.xlsx)"

<br>

<h2 align="center"> Installation </h2>

<div align="center">

```
pip install VeriFacturation
```

[<img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/Atem83/VeriFacturation?&color=green&label=Source%20Code&logo=Python&logoColor=yellow&style=for-the-badge"  width="300">](https://github.com/Atem83/VeriFacturation/archive/refs/heads/main.zip)


</div>

<br>

<h2 align="center"> Exemples </h2>

```python
import verifact

verifact.App().run()
```

```python
from verifact import Invoice
from tkinter import filedialog

file = filedialog.askopenfilename(title="Sélectionner le journal de vente")
factures = Invoice(file)
factures.import_invoices("CADOR/ComptabilitéExpert (.csv)")

# Fonction optionnelle pour trouver les séquences automaticement
# Il est aussi possible de donner manuellement les séquences des factures
patterns = factures.infer_pattern()

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

```
