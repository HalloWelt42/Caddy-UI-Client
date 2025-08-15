#!/usr/bin/env python
"""
Client Start-Script - im Projektroot ausführen
"""
import sys
from pathlib import Path

# Projekt-Root zum Python-Path hinzufügen
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Client starten
from client.main import main

if __name__ == "__main__":
    print(f"🚀 Starte Caddy Manager Client vom Projektroot: {project_root}")
    main()