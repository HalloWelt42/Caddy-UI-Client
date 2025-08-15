#!/usr/bin/env python
"""
Server Start-Script - im Projektroot ausführen
"""
import sys
from pathlib import Path

# Projekt-Root zum Python-Path hinzufügen
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Server importieren und starten
from server.main import run_server

if __name__ == "__main__":
    print(f"🚀 Starte Server vom Projektroot: {project_root}")
    run_server()