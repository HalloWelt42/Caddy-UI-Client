"""
Server-Konfiguration
"""
import sys
from pathlib import Path

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from shared.utils.paths import *


class Settings(BaseSettings):
    # Server-Einstellungen
    host: str = Field(default="127.0.0.1", description="Server Host", alias="HOST")
    port: int = Field(default=8000, description="Server Port",alias="PORT")
    reload: bool = Field(default=True, description="Auto-Reload bei Änderungen")
    api_server: str = Field(default="http://127.0.0.1:8000", description="API Server URL", alias="SERVER")
    api_websocket: str = Field(default="ws://127.0.0.1:8000", description="WebSocket API URL", alias="WEBSOCKET")

    # Caddy-Einstellungen
    caddy_admin_host: str = Field(default="localhost", description="Caddy Admin API Host")
    caddy_admin_port: int = Field(default=2019, description="Caddy Admin API Port")
    caddy_api_url: str = Field(default="http://localhost:2019", description="Caddy Admin API URL")

    # Docker-Einstellungen
    docker_enabled: bool = Field(default=False, description="Docker-Integration aktiviert")
    docker_socket: str = Field(default="unix://var/run/docker.sock", description="Docker Socket")

    # Monitoring
    monitor_interval: int = Field(default=2, description="Monitoring-Intervall in Sekunden")
    metrics_history_size: int = Field(default=100, description="Anzahl gespeicherter Metriken")

    # Pfade (relativ)
    project_root: Path = Field(default=PROJECT_ROOT)
    config_dir: Path = Field(default=CONFIG_DIR)
    data_dir: Path = Field(default=DATA_DIR)
    logs_dir: Path = Field(default=LOGS_DIR)
    backups_dir: Path = Field(default=BACKUPS_DIR)
    certs_dir: Path = Field(default=CERTS_DIR)

    # Caddy-Installation
    caddy_version: str = Field(default="2.8.4", description="Caddy Version")
    caddy_download_url_mac: str = Field(
        default="https://github.com/caddyserver/caddy/releases/download/v{version}/caddy_{version}_mac_arm64.tar.gz"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def caddy_binary_path(self) -> Path:
        """Pfad zur Caddy-Binary"""
        return CADDY_BINARY

    @property
    def is_caddy_installed(self) -> bool:
        """Prüft ob Caddy installiert ist"""
        return self.caddy_binary_path.exists()


# Singleton-Instanz
settings = Settings()