@echo off
chcp 65001 > nul

::Chemins absolus de l'ancien et du nouveau fichier exécutables
set "old_file_path=%1"
set "new_file_path=%2"

::Récupération des chemins de l'ancien fichier
for %%i in ("%old_file_path%") do set "old_filedir=%%~dpi"
for %%f in ("%old_file_path%") do set "old_filename=%%~nxf"

::Récupération des chemins du nouveau fichier
for %%i in ("%new_file_path%") do set "new_filedir=%%~dpi"
for %%f in ("%new_file_path%") do set "new_filename=%%~nxf"

::Récupération du nouveau chemin du fichier déplacé
set "moved_path=%old_filedir%%new_filename%"

::Fermeture du programme
taskkill /F /IM "%old_filename%"
timeout /t 2

::Suppression de l'ancien fichier exécutable
if exist "%old_file_path%" (
    del "%old_file_path%"
    echo Le fichier a été supprimé : %old_file_path%
) else (
    echo Le fichier n'existe pas : %old_file_path%
)

::Déplacement du nouveau fichier exécutable à l'ancien emplacement
if exist "%new_file_path%" (
    move "%new_file_path%" "%old_filedir%"
    if errorlevel 1 (
        echo Erreur lors du déplacement de %new_file_path% vers %old_filedir%
        echo Code d'erreur : %errorlevel%
    ) else (
        echo Le fichier a été déplacé de %new_file_path% à %old_filedir%
    )
) else (
    echo Le fichier à déplacer n'existe pas : %new_file_path%
)

::Relance le programme
start "" "%moved_path%"

::Suppression du dossier new_filedir
if exist "%new_filedir%" (
    rmdir /s /q "%new_filedir%"
    echo Le dossier a été supprimé : %new_filedir%
) else (
    echo Le dossier n'existe pas : %new_filedir%
)