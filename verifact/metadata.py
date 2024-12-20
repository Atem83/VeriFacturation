from configparser import ConfigParser
from pathlib import Path

def get_project_metadata():
    """Récupère les métadonnées du projet depuis setup.cfg"""
    config = ConfigParser()
    setup_cfg = Path(__file__).parent.parent / "setup.cfg"
    
    # Lire le fichier avec l'encodage UTF-8
    with open(setup_cfg, "r", encoding="utf-8") as f:
        config.read_file(f)
    
    return {
        "version": config.get("metadata", "version"),
        "author": config.get("metadata", "author"),
        "name": config.get("metadata", "name"),
        "description": config.get("metadata", "description"),
        "url": config.get("metadata", "url"),
        "license": config.get("metadata", "license"),
    }

# Exporte les variables pour un import direct
globals().update(get_project_metadata())
