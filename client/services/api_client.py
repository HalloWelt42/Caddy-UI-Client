"""
API Client für die Kommunikation mit dem FastAPI Server
"""
import httpx
import asyncio
from typing import Dict, Any, List, Optional
from PySide6.QtCore import QObject, Signal
import json

class APIClient(QObject):
    """Async API Client mit Qt Signals"""

    # Signals für UI-Updates
    status_updated = Signal(dict)
    routes_updated = Signal(list)
    metrics_updated = Signal(dict)
    error_occurred = Signal(str)
    operation_completed = Signal(dict)
    install_progress = Signal(dict)

    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__()
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def check_connection(self) -> bool:
        """Prüft Verbindung zum Server"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False

    # ============= Caddy Management =============

    async def get_caddy_status(self) -> Dict[str, Any]:
        """Caddy Status abrufen"""
        try:
            response = await self.client.get(f"{self.base_url}/api/caddy/status")
            response.raise_for_status()
            data = response.json()
            self.status_updated.emit(data)
            return data
        except Exception as e:
            self.error_occurred.emit(f"Status-Fehler: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def install_caddy(self) -> Dict[str, Any]:
        """Caddy installieren"""
        try:
            response = await self.client.post(f"{self.base_url}/api/caddy/install", timeout=60.0)
            if response.status_code == 200:
                data = response.json()
                self.operation_completed.emit(data)
                return data
            else:
                # Versuche Error-Details zu extrahieren
                try:
                    error_detail = response.json().get("detail", response.text)
                except:
                    error_detail = response.text

                error_msg = f"Installation fehlgeschlagen: {error_detail}"
                self.error_occurred.emit(error_msg)
                return {"success": False, "error": error_msg}
        except Exception as e:
            self.error_occurred.emit(f"Installations-Fehler: {str(e)}")
            return {"success": False, "error": str(e)}

    async def install_caddy_with_progress(self):
        """Caddy mit WebSocket-Progress installieren"""
        import websockets

        try:
            uri = f"ws://localhost:8000/api/caddy/install/progress"
            async with websockets.connect(uri) as websocket:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)

                    if "complete" in data:
                        self.operation_completed.emit(data["result"])
                        break
                    elif "error" in data:
                        self.error_occurred.emit(data["error"])
                        break
                    else:
                        self.install_progress.emit(data)

        except Exception as e:
            self.error_occurred.emit(f"WebSocket-Fehler: {str(e)}")

    async def start_caddy(self) -> Dict[str, Any]:
        """Caddy starten"""
        try:
            response = await self.client.post(f"{self.base_url}/api/caddy/start")
            response.raise_for_status()
            data = response.json()
            self.operation_completed.emit(data)
            await self.get_caddy_status()  # Status aktualisieren
            return data
        except Exception as e:
            self.error_occurred.emit(f"Start-Fehler: {str(e)}")
            return {"success": False, "error": str(e)}

    async def stop_caddy(self) -> Dict[str, Any]:
        """Caddy stoppen"""
        try:
            response = await self.client.post(f"{self.base_url}/api/caddy/stop")
            response.raise_for_status()
            data = response.json()
            self.operation_completed.emit(data)
            await self.get_caddy_status()  # Status aktualisieren
            return data
        except Exception as e:
            self.error_occurred.emit(f"Stop-Fehler: {str(e)}")
            return {"success": False, "error": str(e)}

    async def restart_caddy(self) -> Dict[str, Any]:
        """Caddy neu starten"""
        try:
            response = await self.client.post(f"{self.base_url}/api/caddy/restart")
            response.raise_for_status()
            data = response.json()
            self.operation_completed.emit(data)
            await self.get_caddy_status()  # Status aktualisieren
            return data
        except Exception as e:
            self.error_occurred.emit(f"Neustart-Fehler: {str(e)}")
            return {"success": False, "error": str(e)}

    # ============= Routes Management =============

    async def get_routes(self) -> List[Dict[str, Any]]:
        """Routes abrufen"""
        try:
            response = await self.client.get(f"{self.base_url}/api/caddy/routes")
            response.raise_for_status()
            data = response.json()
            self.routes_updated.emit(data)
            return data
        except Exception as e:
            self.error_occurred.emit(f"Routes-Fehler: {str(e)}")
            return []

    async def add_route(self, domain: str, upstream: str, path: str = "/") -> Dict[str, Any]:
        """Route hinzufügen"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/caddy/routes",
                json={"domain": domain, "upstream": upstream, "path": path}
            )
            response.raise_for_status()
            data = response.json()
            self.operation_completed.emit(data)
            await self.get_routes()  # Routes aktualisieren
            return data
        except Exception as e:
            self.error_occurred.emit(f"Route-Hinzufügen-Fehler: {str(e)}")
            return {"success": False, "error": str(e)}

    async def remove_route(self, domain: str) -> Dict[str, Any]:
        """Route entfernen"""
        try:
            response = await self.client.delete(f"{self.base_url}/api/caddy/routes/{domain}")
            response.raise_for_status()
            data = response.json()
            self.operation_completed.emit(data)
            await self.get_routes()  # Routes aktualisieren
            return data
        except Exception as e:
            self.error_occurred.emit(f"Route-Entfernen-Fehler: {str(e)}")
            return {"success": False, "error": str(e)}

    # ============= Monitoring =============

    async def get_metrics(self) -> Dict[str, Any]:
        """Aktuelle Metriken abrufen"""
        try:
            response = await self.client.get(f"{self.base_url}/api/monitoring/metrics")
            response.raise_for_status()
            data = response.json()
            self.metrics_updated.emit(data)
            return data
        except Exception as e:
            self.error_occurred.emit(f"Metriken-Fehler: {str(e)}")
            return {}

    async def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Metrik-Historie abrufen"""
        try:
            response = await self.client.get(f"{self.base_url}/api/monitoring/metrics/history")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.error_occurred.emit(f"Historie-Fehler: {str(e)}")
            return []

    async def start_metrics_stream(self, callback):
        """WebSocket Metrik-Stream starten"""
        import websockets

        try:
            uri = f"ws://localhost:8000/api/monitoring/metrics/stream"
            async with websockets.connect(uri) as websocket:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    self.metrics_updated.emit(data)
                    if callback:
                        callback(data)
        except Exception as e:
            self.error_occurred.emit(f"Stream-Fehler: {str(e)}")

    # ============= Docker Management =============

    async def get_docker_containers(self) -> List[Dict[str, Any]]:
        """Docker Container abrufen"""
        try:
            response = await self.client.get(f"{self.base_url}/api/monitoring/docker/containers")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.error_occurred.emit(f"Docker-Fehler: {str(e)}")
            return []

    async def control_docker_container(self, container_id: str, action: str) -> Dict[str, Any]:
        """Docker Container steuern"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/monitoring/docker/containers/{container_id}/{action}"
            )
            response.raise_for_status()
            data = response.json()
            self.operation_completed.emit(data)
            return data
        except Exception as e:
            self.error_occurred.emit(f"Docker-Control-Fehler: {str(e)}")
            return {"success": False, "error": str(e)}

    # ============= Backup/Restore =============

    async def backup_config(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Konfiguration sichern"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/caddy/backup",
                json={"name": name}
            )
            response.raise_for_status()
            data = response.json()
            self.operation_completed.emit(data)
            return data
        except Exception as e:
            self.error_occurred.emit(f"Backup-Fehler: {str(e)}")
            return {"success": False, "error": str(e)}

    async def restore_config(self, backup_name: str) -> Dict[str, Any]:
        """Konfiguration wiederherstellen"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/caddy/restore",
                json={"backup_name": backup_name}
            )
            response.raise_for_status()
            data = response.json()
            self.operation_completed.emit(data)
            return data
        except Exception as e:
            self.error_occurred.emit(f"Restore-Fehler: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_backups(self) -> List[Dict[str, Any]]:
        """Backup-Liste abrufen"""
        try:
            response = await self.client.get(f"{self.base_url}/api/caddy/backups")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.error_occurred.emit(f"Backup-Liste-Fehler: {str(e)}")
            return []

    async def close(self):
        """Client schließen"""
        await self.client.aclose()