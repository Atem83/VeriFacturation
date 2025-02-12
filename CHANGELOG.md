# Changelog
Tous les changements de ce projet seront documentés ici.

Ce format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## A faire
- Rien pour le moment.

## [1.4.5] - 2025-02-12
### Modifications
- Correction d'un bug qui cumulait les comptes clients des doublons de factures.
- Tri des patterns qui sont affichés automatiquement pour conserver un ordre constant.

## [1.4.4] - 2025-01-25
### Modifications
- Désactivation du splash à l'ouverture de l'application.
- Suppression du fichier batch et de son utilisation à cause de trop nombreux bugs dans les chemins avec des espaces.

## [1.4.3] - 2025-01-19
### Modifications
- Lors d'une mise à jour, supprime l'ancien fichier .exe et déplace le nouveau à la place de l'ancien.
- Recherche automatiquement les mises à jour au démarrage.

## [1.4.2] - 2025-01-12
### Ajouts
- Affiche un splash screen lors du chargement de l'application.
- Affiche une fenêtre avec le % de téléchargement de la mise à jour.

## [1.4.1] - 2025-01-07
### Modifications
- Correction d'un bug d'import lorsque PieceRef n'est pas reconnu comme un dtype pl.String.

## [1.4.0] - 2025-01-05
### Modifications
- Création d'un fichier app.py avec toutes les propriétées de base du gui.
- Création de méthodes pour initialiser les différentes composantes de MainWindow.
- Correction d'un bug lorsqu'une séquence choisie ne contient aucune facture.
- Correction d'un bug de redimensionnement de run_error.
- Modifications mineures de l'interface run_error.

### Ajouts
- Les séquences ne contenant aucune facture seront désormais ignorées.
- Ajout d'un message d'erreur lorsqu'aucune facture n'a pu être traitée.
- Ajout d'un message d'erreur lorsqu'aucune facture n'est trouvée
- Enregistrer les changements de paramètres.

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
- Ajout d'un message d'erreur pour afficher les erreurs d'import.

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
