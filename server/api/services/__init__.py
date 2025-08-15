"""
Services Module - Initialisierung und Export
"""
from .caddy_service import CaddyService
from .monitor_service import MonitorService

# Singleton-Instanzen erstellen
caddy_service = CaddyService()
monitor_service = MonitorService()

# Zirkuläre Abhängigkeiten auflösen
monitor_service.set_caddy_service(caddy_service)

# Exportieren
__all__ = ['caddy_service', 'monitor_service']