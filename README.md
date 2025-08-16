caddy-manager/
│
├── server/                # Backend (läuft als eigenständiger Prozess)
│   ├── api/               
│   │   ├── routes/        # HTTP-Endpoints definieren
│   │   ├── models/        # Datenmodelle für Request/Response
│   │   └── services/      # Geschäftslogik, Singleton-Pattern
│   ├── config/            # Konfiguration des Servers
│   └── main.py            # Einstiegspunkt, startet FastAPI
│
├── client/                # Frontend (Desktop-Anwendung)
│   ├── ui/               
│   │   ├── windows/       # Hauptfenster der Anwendung
│   │   ├── widgets/       # Wiederverwendbare UI-Komponenten
│   │   └── styles/        # Dark Theme CSS-ähnliche Styles
│   ├── services/          # API-Client für Backend-Kommunikation
│   └── main.py            # Startet Qt-Anwendung
│
├── shared/                # Gemeinsam genutzte Module
│   └── utils/           
│       └── paths.py       # Zentrale Pfadverwaltung (wichtig!)
│
├── config/              # Laufzeit-Konfigurationen
├── data/                # Persistente Daten
└── run_*.py             # Starter-Scripts mit Path-Setup

