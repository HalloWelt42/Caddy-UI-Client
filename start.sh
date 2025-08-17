#!/bin/bash

# ============================================
# Caddy Manager - Start Script
# ============================================
# Startet Backend (FastAPI) und Frontend (PySide6)
# Optional: Installation der Dependencies
# ============================================

set -e  # Bei Fehler abbrechen

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Projekt-Root ermitteln (Verzeichnis des Scripts)
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_ROOT"

# Konfiguration
VENV_DIR=".venv"
BACKEND_PORT=8000
FRONTEND_DELAY=5
PYTHON_MIN_VERSION="3.9"

# PID-Dateien für Prozess-Management
BACKEND_PID_FILE="$PROJECT_ROOT/data/backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/data/frontend.pid"

# ============================================
# Hilfsfunktionen
# ============================================

print_header() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Python-Version prüfen
check_python_version() {
    print_info "Prüfe Python-Version..."

    # Versuche verschiedene Python-Commands
    for cmd in python3 python; do
        if command -v $cmd &> /dev/null; then
            version=$($cmd -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
            major=$(echo $version | cut -d. -f1)
            minor=$(echo $version | cut -d. -f2)

            if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
                PYTHON_CMD=$cmd
                print_success "Python $version gefunden ($cmd)"
                return 0
            fi
        fi
    done

    print_error "Python >= $PYTHON_MIN_VERSION nicht gefunden!"
    echo "Bitte installieren Sie Python 3.9 oder höher."
    exit 1
}

# Virtual Environment erstellen/aktivieren
setup_venv() {
    print_info "Prüfe Virtual Environment..."

    if [ ! -d "$VENV_DIR" ]; then
        print_warning "Virtual Environment nicht gefunden. Erstelle..."
        $PYTHON_CMD -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            print_error "Fehler beim Erstellen der Virtual Environment!"
            exit 1
        fi
        print_success "Virtual Environment erstellt"
    else
        print_success "Virtual Environment gefunden"
    fi

    # Aktivieren
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    else
        print_error "Virtual Environment konnte nicht aktiviert werden!"
        exit 1
    fi
}

# Dependencies installieren
install_dependencies() {
    print_info "Installiere Dependencies..."

    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt nicht gefunden!"
        exit 1
    fi

    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        print_error "Fehler beim Installieren der Dependencies!"
        echo "Versuchen Sie: pip install -r requirements.txt"
        exit 1
    fi

    print_success "Dependencies installiert"
}

# Prüfe ob Dependencies installiert sind
check_dependencies() {
    print_info "Prüfe Dependencies..."

    # Prüfe kritische Packages
    python -c "import fastapi" 2>/dev/null
    if [ $? -ne 0 ]; then
        return 1
    fi

    python -c "import PySide6" 2>/dev/null
    if [ $? -ne 0 ]; then
        return 1
    fi

    print_success "Dependencies sind installiert"
    return 0
}

# Verzeichnisstruktur erstellen
create_directories() {
    print_info "Erstelle Verzeichnisstruktur..."

    mkdir -p "$PROJECT_ROOT/data/logs"
    mkdir -p "$PROJECT_ROOT/data/backups"
    mkdir -p "$PROJECT_ROOT/data/certs"
    mkdir -p "$PROJECT_ROOT/data/caddy"
    mkdir -p "$PROJECT_ROOT/config/app"
    mkdir -p "$PROJECT_ROOT/config/caddy"

    print_success "Verzeichnisse erstellt/geprüft"
}

# Backend starten
start_backend() {
    print_info "Starte Backend (FastAPI)..."

    # Prüfe ob Backend bereits läuft
    if [ -f "$BACKEND_PID_FILE" ]; then
        old_pid=$(cat "$BACKEND_PID_FILE")
        if ps -p $old_pid > /dev/null 2>&1; then
            print_warning "Backend läuft bereits (PID: $old_pid)"
            return 0
        else
            rm -f "$BACKEND_PID_FILE"
        fi
    fi

    # Backend starten
    cd "$PROJECT_ROOT"
    nohup python run_server.py > "$PROJECT_ROOT/data/logs/backend.log" 2>&1 &
    backend_pid=$!

    # PID speichern
    echo $backend_pid > "$BACKEND_PID_FILE"

    # Kurz warten und prüfen ob Prozess läuft
    sleep 2
    if ps -p $backend_pid > /dev/null; then
        print_success "Backend gestartet (PID: $backend_pid)"
        print_info "Backend läuft auf http://localhost:$BACKEND_PORT"

        # Warte bis Backend bereit ist
        print_info "Warte auf Backend-Bereitschaft..."
        for i in {1..10}; do
            if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
                print_success "Backend ist bereit"
                return 0
            fi
            sleep 1
        done
        print_warning "Backend antwortet nicht auf Health-Check, aber Prozess läuft"
    else
        print_error "Backend konnte nicht gestartet werden!"
        print_info "Prüfen Sie: $PROJECT_ROOT/data/logs/backend.log"
        exit 1
    fi
}

# Frontend starten
start_frontend() {
    print_info "Starte Frontend (PySide6) in $FRONTEND_DELAY Sekunden..."
    sleep $FRONTEND_DELAY

    # Prüfe ob Frontend bereits läuft
    if [ -f "$FRONTEND_PID_FILE" ]; then
        old_pid=$(cat "$FRONTEND_PID_FILE")
        if ps -p $old_pid > /dev/null 2>&1; then
            print_warning "Frontend läuft bereits (PID: $old_pid)"
            return 0
        else
            rm -f "$FRONTEND_PID_FILE"
        fi
    fi

    print_info "Starte Frontend..."
    cd "$PROJECT_ROOT"

    # Frontend starten (nicht im Hintergrund für GUI)
    python run_client.py > "$PROJECT_ROOT/data/logs/frontend.log" 2>&1 &
    frontend_pid=$!

    # PID speichern
    echo $frontend_pid > "$FRONTEND_PID_FILE"

    # Kurz warten und prüfen
    sleep 2
    if ps -p $frontend_pid > /dev/null; then
        print_success "Frontend gestartet (PID: $frontend_pid)"
    else
        print_error "Frontend konnte nicht gestartet werden!"
        print_info "Prüfen Sie: $PROJECT_ROOT/data/logs/frontend.log"
        exit 1
    fi
}

# Prozesse stoppen
stop_all() {
    print_header "Stoppe Caddy Manager"

    # Backend stoppen
    if [ -f "$BACKEND_PID_FILE" ]; then
        pid=$(cat "$BACKEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            print_info "Stoppe Backend (PID: $pid)..."
            kill $pid 2>/dev/null || true
            sleep 1
            # Falls immer noch läuft, härter killen
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid 2>/dev/null || true
            fi
            print_success "Backend gestoppt"
        fi
        rm -f "$BACKEND_PID_FILE"
    fi

    # Frontend stoppen
    if [ -f "$FRONTEND_PID_FILE" ]; then
        pid=$(cat "$FRONTEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            print_info "Stoppe Frontend (PID: $pid)..."
            kill $pid 2>/dev/null || true
            sleep 1
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid 2>/dev/null || true
            fi
            print_success "Frontend gestoppt"
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
}

# Status anzeigen
show_status() {
    print_header "Caddy Manager Status"

    # Backend Status
    if [ -f "$BACKEND_PID_FILE" ]; then
        pid=$(cat "$BACKEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            print_success "Backend läuft (PID: $pid)"
        else
            print_error "Backend PID-Datei existiert, aber Prozess läuft nicht"
        fi
    else
        print_info "Backend ist nicht gestartet"
    fi

    # Frontend Status
    if [ -f "$FRONTEND_PID_FILE" ]; then
        pid=$(cat "$FRONTEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            print_success "Frontend läuft (PID: $pid)"
        else
            print_error "Frontend PID-Datei existiert, aber Prozess läuft nicht"
        fi
    else
        print_info "Frontend ist nicht gestartet"
    fi

    # Port-Check
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_success "Port $BACKEND_PORT ist belegt (Backend API)"
    else
        print_info "Port $BACKEND_PORT ist frei"
    fi
}

# Hilfe anzeigen
show_help() {
    echo "Caddy Manager - Start Script"
    echo ""
    echo "Verwendung: $0 [OPTION]"
    echo ""
    echo "Optionen:"
    echo "  start       Startet Backend und Frontend"
    echo "  stop        Stoppt Backend und Frontend"
    echo "  restart     Neustart von Backend und Frontend"
    echo "  status      Zeigt den Status an"
    echo "  install     Installiert alle Dependencies"
    echo "  dev         Startet im Development-Modus (mit Logs im Terminal)"
    echo "  help        Zeigt diese Hilfe an"
    echo ""
    echo "Ohne Option wird standardmäßig 'start' ausgeführt."
}

# ============================================
# Hauptprogramm
# ============================================

print_header "Caddy Manager - Start Script"

# Command-Line-Argument verarbeiten
ACTION=${1:-start}

case $ACTION in
    start)
        # Python prüfen
        check_python_version

        # Virtual Environment
        setup_venv

        # Dependencies prüfen/installieren
        if ! check_dependencies; then
            print_warning "Dependencies fehlen. Installiere..."
            install_dependencies
        fi

        # Verzeichnisse erstellen
        create_directories

        # Services starten
        start_backend
        start_frontend

        print_header "Caddy Manager erfolgreich gestartet!"
        print_info "Backend:  http://localhost:$BACKEND_PORT"
        print_info "Frontend: PySide6 GUI läuft"
        print_info ""
        print_info "Zum Stoppen: $0 stop"
        ;;

    stop)
        stop_all
        print_success "Caddy Manager gestoppt"
        ;;

    restart)
        stop_all
        sleep 2
        $0 start
        ;;

    status)
        show_status
        ;;

    install)
        check_python_version
        setup_venv
        install_dependencies
        create_directories
        print_success "Installation abgeschlossen"
        ;;

    dev)
        # Development-Modus: Logs im Terminal anzeigen
        check_python_version
        setup_venv
        if ! check_dependencies; then
            install_dependencies
        fi
        create_directories

        print_info "Starte im Development-Modus..."
        print_warning "Drücken Sie Ctrl+C zum Beenden"

        # Backend im Hintergrund, Frontend im Vordergrund
        python run_server.py &
        backend_pid=$!
        sleep 3
        python run_client.py

        # Cleanup wenn Frontend beendet wird
        kill $backend_pid 2>/dev/null || true
        ;;

    help|--help|-h)
        show_help
        ;;

    *)
        print_error "Unbekannte Option: $ACTION"
        echo ""
        show_help
        exit 1
        ;;
esac

exit 0