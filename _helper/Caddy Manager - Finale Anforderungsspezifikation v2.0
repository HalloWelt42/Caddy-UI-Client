# Caddy Manager - Finale Anforderungsspezifikation v2.0

## Executive Summary
Entwicklung einer robusten, plattformübergreifenden GUI-Anwendung zur Installation, Konfiguration und Verwaltung von Caddy Server mit automatischem HTTPS/TLS-Support, Docker-Integration und Echtzeit-Monitoring.

## Technische Architektur

### Client-Server-Modell
- **Backend**: FastAPI Server (asynchron) auf Host-System
- **Frontend**: Qt6 Desktop-Anwendung (PySide6) mit Dark Mode
- **Kommunikation**: REST API mit JSON-Payloads
- **Async-Handling**: qasync für Qt Event Loop Integration
- **Konfiguration**: Alle Pfade relativ zum Projektverzeichnis

### Deployment-Strategie
- **Phase 1**: macOS mit Apple Silicon (M-Serie)
- **Phase 2**: Cross-Platform (Windows, Linux)
- **Caddy**: Läuft auf Host-System (Docker-Integration optional)
- **Konfiguration**: Caddyfile-basiert (nicht JSON wegen Kompatibilität)

## Kernfunktionalitäten

### 1. Caddy Installation & Management

#### Installation
- **Automatischer Download**: GitHub Releases mit Redirect-Handling
- **Platform Detection**: Automatische Erkennung von OS und Architektur
- **Binary Management**: Installation in `data/caddy/` Verzeichnis
- **Fehlerbehandlung**: Detaillierte Fehlerausgabe bei Installationsproblemen

#### Prozess-Steuerung
- **Start/Stop/Restart**: Vollständige Kontrolle über Caddy-Prozess
- **Status-Monitoring**: Echtzeit-Status über Admin API (Port 2019)
- **Config-Validation**: Prüfung vor Start
- **Error Recovery**: Automatische Fehlerdiagnose mit STDOUT/STDERR

#### SSL/TLS Management
- **Automatisches HTTPS**:
  - Let's Encrypt für öffentliche Domains
  - Interne Zertifikate für lokale Domains (.local, localhost)
- **Root-Zertifikat Installation**: Automatisch bei Installation für CORS-freie Entwicklung
- **HTTP→HTTPS Redirect**: Automatische Weiterleitung von Port 80 auf 443
- **TLS Configuration**: `tls internal` für lokale Entwicklung

### 2. Route Management

#### Route-Konfiguration
- **Domain-basiertes Routing**: Einfache Domain→Upstream Zuordnung
- **HTTPS-Automatik**: Intelligente Erkennung lokaler vs. öffentlicher Domains
- **Reverse Proxy**: Vollständige reverse_proxy Unterstützung
- **Live-Reload**: Änderungen ohne Neustart über `caddy reload`

#### Caddyfile-Management
- **Parser**: Lesen und Schreiben von Caddyfile-Syntax
- **Route CRUD**: Hinzufügen, Bearbeiten, Löschen von Routes
- **Backup/Restore**: Konfigurationssicherung mit Zeitstempel
- **Syntax-Generierung**: Korrekte Caddyfile-Blöcke erstellen

### 3. System Monitoring

#### Metriken
- **System-Ressourcen**: CPU, RAM, Disk, Network (via psutil)
- **Request-Metriken**: Requests/sec, Average Response Time
- **Service-Status**: Caddy, Docker, API Server Status
- **Historie**: Rollierender Buffer mit konfigurierbarer Größe

#### Docker Integration
- **Container-Management**: Start/Stop/Restart von Containern
- **Container-Listing**: Übersicht aller Container mit Status
- **Port-Mapping**: Anzeige der exponierten Ports
- **Auto-Refresh**: Regelmäßige Aktualisierung (10 Sekunden)

### 4. User Interface

#### Design-Prinzipien
- **Dark Mode**: Konsistentes dunkles Theme
- **Icon System**: Font Awesome Icons (keine Emojis)
- **Responsive Layout**: Anpassbare Tabs und Widgets
- **Status-Visualisierung**: Farbcodierte Status-Indikatoren

#### UI-Komponenten
1. **Dashboard**
   - Status-Übersicht (Caddy, Docker, API)
   - System-Metriken (Live-Updates)
   - Quick-Actions (Start/Stop/Restart)

2. **Route Manager**
   - Tabellen-Ansicht aller Routes
   - Add/Edit/Delete Funktionalität
   - Domain-Validierung

3. **Docker Manager**
   - Container-Tabelle mit Live-Status
   - Individuelle Container-Kontrolle
   - Port-Mapping Übersicht

4. **Backup/Restore**
   - Konfigurations-Sicherung
   - Zeitgestempelte Backups
   - Restore mit Bestätigung

## Technische Herausforderungen & Lösungen

### 1. Async Task Management
**Problem**: Timer-Konflikte bei gleichzeitigen async Operations
**Lösung**:
- Mutex-ähnliche Flags für Update-Operations
- Timer-Stops während kritischer Operationen
- Safe-Update-Wrapper für Timer-Callbacks

### 2. Platform-Kompatibilität
**Problem**: Caddy Binary unterschiedlich je nach Platform
**Lösung**:
- Platform-Detection (platform.system(), platform.machine())
- Spezifische Download-URLs pro Platform
- Fehlerbehandlung für nicht-unterstützte Platforms

### 3. SSL/TLS Konfiguration
**Problem**: Browser SSL-Fehler bei lokaler Entwicklung
**Lösung**:
- Automatische `tls internal` für lokale Domains
- Root-CA Installation via `caddy trust`
- Separate Behandlung lokaler vs. öffentlicher Domains

### 4. Config-Format
**Problem**: JSON-Adapter nicht in Standard-Caddy enthalten
**Lösung**:
- Wechsel zu Caddyfile-Format
- Custom Parser für Caddyfile CRUD-Operations
- Adapter-Parameter bei allen Caddy-Befehlen

### 5. API Timeouts
**Problem**: Lange Operations führen zu Timeouts
**Lösung**:
- Erhöhte Timeout-Werte (30s default, 60s für Installation)
- Follow-Redirects aktiviert
- Progress-Callbacks für lange Operations

## Projekt-Struktur

```
caddy-manager/
├── server/
│   ├── api/
│   │   ├── routes/         # API Endpoints
│   │   ├── models/         # Pydantic Models
│   │   └── services/       # Business Logic
│   ├── config/             # Server-Konfiguration
│   └── main.py            # FastAPI App
│
├── client/
│   ├── ui/
│   │   ├── windows/        # Hauptfenster
│   │   ├── widgets/        # UI-Komponenten
│   │   └── styles/         # Dark Theme
│   ├── services/           # API Client
│   └── main.py            # Qt App
│
├── shared/
│   └── utils/
│       └── paths.py        # Zentrale Pfadverwaltung
│
├── config/
│   ├── caddy/             # Caddyfile & Configs
│   └── app/               # App-Settings
│
├── data/
│   ├── caddy/             # Caddy Binary
│   ├── backups/           # Config-Backups
│   ├── certs/             # Zertifikate
│   └── logs/              # Log-Dateien
│
├── run_server.py          # Server-Starter
├── run_client.py          # Client-Starter
└── requirements.txt       # Dependencies
```

## Dependencies

### Backend
- **fastapi** ≥0.115.0 - Web Framework
- **uvicorn[standard]** ≥0.32.0 - ASGI Server
- **httpx** ≥0.27.2 - Async HTTP Client
- **pydantic** ≥2.9.2 - Data Validation
- **psutil** ≥6.1.0 - System Monitoring
- **docker** ≥7.1.0 - Docker API

### Frontend
- **PySide6** ≥6.8.0 - Qt6 Bindings
- **qasync** ≥0.27.1 - Async Qt Integration
- **QtAwesome** ≥1.3.1 - Icon Font
- **websockets** ≥15.0 - WebSocket Support

## Best Practices & Lessons Learned

### Code-Organisation
- **Strikte Trennung**: UI-Logik von Business-Logik
- **Singleton Services**: Zentrale Service-Instanzen
- **Relative Pfade**: Keine absoluten Pfade im Code
- **Error Boundaries**: Umfassende Fehlerbehandlung

### Async-Patterns
- **Keine blockierenden Calls**: Alle I/O async
- **Task-Koordination**: Vermeidung von Race Conditions
- **Progress-Feedback**: User-Feedback bei langen Operations
- **Graceful Shutdown**: Sauberes Cleanup bei Beendigung

### UI/UX Design
- **Konsistenz**: Einheitliche Farben und Icons
- **Feedback**: Sofortiges visuelles Feedback
- **Error Messages**: Klare, actionable Fehlermeldungen
- **Progressive Disclosure**: Komplexität schrittweise zeigen

### Testing & Debugging
- **Verbose Logging**: Detaillierte Server-Logs
- **API Documentation**: Swagger UI auf /docs
- **Error Tracing**: Full Stack Traces bei Fehlern
- **Manual Testing**: Curl-Commands für API-Tests

## Zukünftige Erweiterungen

### Phase 2 Features
- **Multi-Platform Support**: Windows, Linux
- **Docker Compose Integration**: Stack-Management
- **Metriken-Dashboard**: Grafische Darstellung mit Charts
- **Log-Viewer**: Integrierte Log-Anzeige
- **Template System**: Vordefinierte Configurations
- **Multi-Server Management**: Mehrere Caddy-Instanzen
- **WebSocket Monitoring**: Live-Metriken via WebSocket
- **Authentifizierung**: Optional für Production

### Performance-Optimierungen
- **Caching**: Response-Caching für Metriken
- **Batch-Operations**: Bulk-Updates für Routes
- **Connection Pooling**: Wiederverwendung von Connections
- **Lazy Loading**: On-Demand Laden von Komponenten

## Kritische Erfolgsfaktoren

1. **Stabilität**: Robuste Fehlerbehandlung, keine Crashes
2. **Performance**: Schnelle UI-Updates, keine Blockierungen
3. **Usability**: Intuitive Bedienung ohne Dokumentation
4. **Compatibility**: Funktioniert mit Standard-Caddy-Binary
5. **Maintainability**: Sauberer, modularer Code

## Bekannte Einschränkungen

- Installation nur für macOS ARM64 (Phase 1)
- Keine Authentifizierung (Development-Fokus)
- Keine automatischen Tests
- Limitierte Caddyfile-Parser-Fähigkeiten
- Docker Desktop muss separat installiert sein
- WebSocket-Progress nicht auf allen Systemen stabil

## Deployment-Anleitung

### Entwicklungsumgebung
1. Python 3.11+ mit venv
2. `pip install -r requirements.txt`
3. `python run_server.py` (Terminal 1)
4. `python run_client.py` (Terminal 2)

### Production (zukünftig)
1. Server als systemd Service
2. Client als .app Bundle (macOS)
3. Auto-Start Option
4. Update-Mechanismus