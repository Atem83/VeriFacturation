# Changelog
Tous les changements de ce projet seront documentés ici.

Ce format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## A faire
- Ajout d'un message d'alerte quand aucune facture n'est trouvée ou aucune facture n'a pu être traitée.
- Correction d'un bug de redimensionnement de run_error.
- Enregistrer les changements de paramètres.

## [1.3.1] - 2024-01-03
### Modifications
- Création d'un fichier app.py avec toutes les propriétées de base du gui.
- Création de méthodes pour initialiser les différentes composantes de MainWindow.
- Correction d'un bug lorsqu'une séquence choisie ne contient aucune facture.
- Les séquences ne contenant aucune facture seront désormais ignorées.

## [1.3.0] - 2024-12-20
### Modifications
- Modifications mineures de l'interface "A propos".
- Séparation du fichier gui en plusieurs fichiers.

### Ajouts
- Ajout de la fonctionnalité de recherche et de téléchargement de mises à jour depuis "A propos".

## [1.2.0] - 2024-12-20
### Modifications
- Renommage du format d'import "cador_import" en "cador_xlsx_import".

### Ajouts
- Ajout du format d'import "cador_csv_import".
- Ajout d'une fenêtre d'erreur pour afficher les erreurs d'import.

## [1.1.0] - 2024-12-14
### Modifications
- Si plusieurs comptes clients font partie d'une seule écriture, agrége ces comptes clients en un seul compte pour éviter d'être compté en doublons.
- Refactoring de format_import en Programmation Orientée Objet.
- La fonctionnalité infer_pattern prend désormais en compte le paramètre 'case_insensitive'.

### Ajouts
- Ajout d'exemples de fichiers d'import dans 'sample'.

## [1.0.5] - 2024-12-08
### Modifications
- Correction de bugs mineurs dans les fichiers pour création du projet pip.

## [1.0.0] - 2024-12-08
- Première version de l'application avec toutes les fonctionnalités essentielles.
