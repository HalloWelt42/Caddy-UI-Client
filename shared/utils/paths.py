"""
Zentrale Pfadverwaltung - alle Pfade relativ zum Projektroot
"""
from pathlib import Path
import sys

# Projektroot ermitteln (3 Ebenen hoch von dieser Datei)
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()

# Python-Path erweitern für Imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Hauptverzeichnisse
SERVER_DIR = PROJECT_ROOT / "server"
CLIENT_DIR = PROJECT_ROOT / "client"
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Config-Unterverzeichnisse
CADDY_CONFIG_DIR = CONFIG_DIR / "caddy"
APP_CONFIG_DIR = CONFIG_DIR / "app"

# Data-Unterverzeichnisse
BACKUPS_DIR = DATA_DIR / "backups"
LOGS_DIR = DATA_DIR / "logs"
CERTS_DIR = DATA_DIR / "certs"

# Wichtige Dateien
CADDY_JSON_CONFIG = CADDY_CONFIG_DIR / "config.json"
CADDYFILE = CADDY_CONFIG_DIR / "Caddyfile"
APP_SETTINGS = APP_CONFIG_DIR / "settings.json"

# Caddy-Binary (wird bei Installation gesetzt)
CADDY_BINARY = DATA_DIR / "caddy" / "caddy"

def ensure_directories():
    """Erstellt alle notwendigen Verzeichnisse"""
    dirs = [
        CONFIG_DIR, DATA_DIR, ASSETS_DIR,
        CADDY_CONFIG_DIR, APP_CONFIG_DIR,
        BACKUPS_DIR, LOGS_DIR, CERTS_DIR,
        DATA_DIR / "caddy"
    ]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)

def get_relative_path(path: Path) -> str:
    """Gibt einen relativen Pfad zum Projektroot zurück"""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)

# Verzeichnisse beim Import erstellen
ensure_directories()