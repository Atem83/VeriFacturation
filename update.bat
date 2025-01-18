@echo off
chcp 65001 > nul

set old_file_path=%1
set new_file_path=%2
echo old : %old_file_path%
echo new : %new_file_path%

for %%i in ("%old_file_path%") do set "old_filedir=%%~dpi"
for %%i in ("%new_file_path%") do set "new_filedir=%%~dpi"

if exist "%old_file_path%" (
    del "%old_file_path%"
    echo Le fichier a été supprimé : %old_file_path%
) else (
    echo Le fichier n'existe pas : %old_file_path%
)
