# Caddy Manager - für MAC mit Apple Silicon (M1-M4)

![](./docs/Bildschirmfoto%202025-08-17%20um%2015.08.30.png)
![](./docs/Bildschirmfoto%202025-08-17%20um%2015.08.36.png)
![](./docs/Bildschirmfoto%202025-08-17%20um%2015.08.41.png)


Eine Desktop-Anwendung zur Verwaltung von Caddy Server mit automatischem HTTPS/TLS-Support, Docker-Integration und Echtzeit-Überwachung.

## Funktionen

* **Caddy Server Verwaltung**: Installation, Konfiguration, Start/Stop von Caddy direkt aus der GUI
* **Automatisches HTTPS**: Let's Encrypt für öffentliche Domains, interne Zertifikate für lokale Entwicklung
* **Routenverwaltung**: Hinzufügen, Entfernen und Verwalten von Reverse-Proxy-Routen über eine visuelle Oberfläche
* **Docker-Integration**: Überwachung und Steuerung von Docker-Containern
* **Echtzeit-Überwachung**: Systemmetriken (CPU, RAM) und Servicestatus mit WebSocket-Streaming
* **Plattformübergreifende Architektur**: FastAPI-Backend mit PySide6 (Qt6)-Frontend

## Anforderungen

* Python 3.11 oder höher
* macOS mit Apple Silicon (M1/M2/M3) – derzeit unterstützt
* Docker Desktop (optional, für Container-Verwaltung)

## Installation

```bash
# Repository klonen
git https://github.com/HalloWelt42/Caddy-UI-Client.git caddy-manager
cd caddy-manager

# Virtuelle Umgebung erstellen
python -m venv .venv
source .venv/bin/activate  

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Nutzung

### Schnellstart

**Achtung!** 
Docker muss installiert sein, um die Docker-Integration zu nutzen und gestartet zu werden.


```bash
# Startskript ausführbar machen
chmod +x start.sh

# Backend und Frontend starten
./start.sh

# Oder Komponenten separat starten:
python run_server.py  # Terminal 1: Backend (FastAPI)
python run_client.py  # Terminal 2: Frontend (PySide6)
```

### Verfügbare Befehle

```bash
./start.sh start    # Backend und Frontend starten
./start.sh stop     # Alle Dienste stoppen
./start.sh restart  # Alle Dienste neu starten
./start.sh status   # Servicestatus anzeigen
./start.sh install  # Nur Abhängigkeiten installieren
./start.sh dev      # Entwicklungsmodus mit Terminal-Logging
```

## Projektstruktur

```
caddy-manager/
├── server/          # FastAPI Backend
│   ├── api/         # API-Routen und Services
│   └── config/      # Serverkonfiguration
├── client/          # PySide6 Frontend
│   ├── ui/          # GUI-Komponenten
│   └── services/    # API-Client
├── config/          # Konfigurationsdateien
│   └── caddy/       # Caddyfile-Speicher
├── data/            # Laufzeitdaten
│   ├── caddy/       # Caddy-Binary
│   ├── backups/     # Konfigurations-Backups
│   └── logs/        # Anwendungs-Logs
└── shared/          # Gemeinsame Hilfsfunktionen
```

## API-Dokumentation

Das Backend läuft auf `http://localhost:8000` mit vollständiger OpenAPI-Dokumentation unter `/docs`.

### Zentrale Endpunkte

#### Server-Informationen

* `GET /` - Serverinfo und verfügbare Endpunkte
* `GET /health` - Gesundheitscheck mit Servicestatus

#### Caddy-Verwaltung

* `GET /api/caddy/status` - Caddy-Status abfragen (running/stopped/not\_installed)
* `POST /api/caddy/install` - Caddy-Binary installieren
* `POST /api/caddy/start` - Caddy-Server starten
* `POST /api/caddy/stop` - Caddy-Server stoppen
* `POST /api/caddy/restart` - Caddy-Server neu starten

#### Routenverwaltung

* `GET /api/caddy/routes` - Alle konfigurierten Routen auflisten
* `POST /api/caddy/routes` - Neue Route hinzufügen
* `DELETE /api/caddy/routes/{domain}` - Route nach Domain entfernen

#### Backup & Wiederherstellung

* `POST /api/caddy/backup` - Konfigurations-Backup erstellen
* `POST /api/caddy/restore` - Backup wiederherstellen
* `GET /api/caddy/backups` - Alle verfügbaren Backups auflisten

#### Systemüberwachung

* `GET /api/monitoring/metrics` - Aktuelle Systemmetriken (CPU, RAM, requests/sec)
* `GET /api/monitoring/metrics/history` - Historische Metriken

#### Docker-Verwaltung

* `GET /api/monitoring/docker/containers` - Alle Docker-Container auflisten
* `POST /api/monitoring/docker/containers/{container_id}/{action}` - Container steuern (start, stop, restart)

### WebSocket-Endpunkte (Echtzeit-Updates)

* `WS /api/caddy/install/progress` - Echtzeit-Installationsfortschritt
* `WS /api/monitoring/metrics/stream` - Live-Metriken-Stream

### API-Tests

Eine umfassende Testsuite ist enthalten:

```bash
# Alle API-Tests ausführen
python test_api_endpoints.py

# Test mit eigener Server-URL
python test_api_endpoints.py --url http://localhost:8000

# Interaktiver Testmodus
python test_api_endpoints.py --interactive
```

## Konfiguration

### Umgebungsvariablen

Die Anwendung nutzt eine `.env`-Datei (automatisch beim ersten Start erstellt).

### Caddyfile

Die Caddy-Konfiguration wird automatisch verwaltet, kann aber manuell in `config/caddy/Caddyfile` angepasst werden.

## Entwicklung

### Im Entwicklungsmodus starten

```bash
# Backend mit Auto-Reload
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000

# Frontend mit Debug-Ausgabe
python run_client.py --debug
```

### Projektabhängigkeiten

Kernabhängigkeiten sind:

* **Backend**: FastAPI, uvicorn, httpx, psutil, docker, pydantic
* **Frontend**: PySide6, qasync, QtAwesome
* **Utilities**: orjson, watchdog, python-dotenv

## Bekannte Einschränkungen

* Unterstützt derzeit nur macOS mit Apple Silicon (Phase 1)
* Keine Authentifizierung (für lokale Entwicklung gedacht)
* Einfache Caddyfile-Parser (komplexe Konfigurationen evtl. manuell nötig)
* WebSocket-Fortschrittsanzeige kann in manchen Umgebungen instabil sein

## Geplante Funktionen (Phase 2)

* **Plattformunterstützung**: Windows- und Linux-Kompatibilität
* **Erweiterte Features**:

  * Log-Viewer mit Filterung
  * Konfigurations-Templates
  * Multi-Server-Management
  * Plugin-System
* **UI-Verbesserungen**:

  * Dark-/Light-Mode Umschaltung
  * Eigene Themes
  * Tastenkombinationen
  * Status-Historien-Grafiken

## Fehlerbehebung

### Häufige Probleme

1. **"Caddy not installed" Fehler**

   * Installieren über den Button im Dashboard
   * Oder manuell: `POST /api/caddy/install`

2. **"Connection refused" bei API-Aufrufen**

   * Sicherstellen, dass das Backend läuft: `python run_server.py`
   * Prüfen, ob Port 8000 frei ist

3. **Docker-Container werden nicht angezeigt**

   * Prüfen, ob Docker Desktop läuft
   * Socket-Berechtigungen prüfen

4. **SSL-Zertifikatfehler**

   * `caddy trust` ausführen, um Root-Zertifikat zu installieren
   * Für lokale Domains `.local`-Suffix verwenden

### Debug-Modus

Detailliertes Logging aktivieren:

```bash
# Mit Debug-Skript starten
./debug_start.sh

# Oder Umgebungsvariable setzen
export DEBUG=true
python run_server.py
```

## Mitwirken

Beiträge sind willkommen! Pull Requests können jederzeit eingereicht werden.

### Entwicklungs-Setup

1. Repository forken
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request öffnen

## Lizenz

MIT License

Copyright (c) 2025

Die Software wird ohne Gewährleistung bereitgestellt, inklusive, aber nicht beschränkt auf Marktgängigkeit, Eignung für einen bestimmten Zweck und Nichtverletzung von Rechten. In keinem Fall haften die Autoren oder Rechteinhaber für Ansprüche, Schäden oder andere Verpflichtungen.

## Danksagungen

* [Caddy Server](https://caddyserver.com/) - Der ultimative Server mit automatischem HTTPS
* [FastAPI](https://fastapi.tiangolo.com/) - Modernes Web-API-Framework
* [PySide6](https://doc.qt.io/qtforpython/) - Python-Bindings für Qt6
* [Docker](https://www.docker.com/) - Container-Plattform

## Support

Bei Problemen, Fragen oder Vorschlägen:

* Ein Issue auf GitHub eröffnen
* Die [API-Dokumentation](http://localhost:8000/docs) prüfen
* Die Testsuite als Beispiel nutzen
