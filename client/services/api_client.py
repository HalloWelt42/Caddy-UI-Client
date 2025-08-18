"""
API Client für die Kommunikation mit dem FastAPI Server - Backup Fix
"""
import httpx
import asyncio
from typing import Dict, Any, List, Optional
from PySide6.QtCore import QObject, Signal
import json
from server.config.settings import settings



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
        # Längere Timeouts für stabilere Verbindung
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,  # Verbindungsaufbau
                read=30.0,  # Lesen der Antwort
                write=10.0,  # Schreiben der Anfrage
                pool=10.0  # Connection Pool
            ),
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10
            )
        )

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
        except httpx.TimeoutException:
            # Bei Timeout - keine Error-Meldung, nur Status unknown
            data = {"status": "unknown", "message": "Timeout - Server antwortet nicht"}
            self.status_updated.emit(data)
            return data
        except httpx.ConnectError:
            # Bei Verbindungsfehler
            data = {"status": "error", "message": "Server nicht erreichbar"}
            self.status_updated.emit(data)
            return data
        except Exception as e:
            # Nur bei unerwarteten Fehlern Error anzeigen
            if "ReadTimeout" not in str(e):
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
            uri = f"{settings.api_websocket}/api/caddy/install/progress"
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
            if response.status_code == 200:
                data = response.json()
                self.operation_completed.emit(data)
                await self.get_caddy_status()  # Status aktualisieren
                return data
            else:
                # Versuche Error-Details zu extrahieren
                try:
                    error_detail = response.json().get("detail", response.text)
                except:
                    error_detail = response.text

                error_msg = f"Start fehlgeschlagen: {error_detail}"
                self.error_occurred.emit(error_msg)
                return {"success": False, "error": error_msg}
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
        except httpx.TimeoutException:
            # Bei Timeout keine Fehlermeldung
            return {}
        except httpx.ConnectError:
            # Bei Verbindungsfehler
            return {}
        except Exception as e:
            # Nur bei unerwarteten Fehlern
            if "ReadTimeout" not in str(e):
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
            uri = f"ws://localhost:8044/api/monitoring/metrics/stream"
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
            # Docker-Fehler nicht als Error anzeigen (könnte einfach nicht installiert sein)
            print(f"Docker nicht verfügbar: {str(e)}")
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

    # ============= Backup/Restore - FIXED =============

    async def backup_config(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Konfiguration sichern - FIXED"""
        try:
            # FIX: Sende korrektes JSON-Format
            # Server erwartet entweder {"name": "string"} oder {"name": null}
            # NICHT {} wenn name None ist

            if name and name.strip():  # Wenn name vorhanden und nicht leer
                payload = {"name": name.strip()}
            else:
                payload = {"name": None}  # Explizit None senden, nicht weglassen

            print(f"Backup Request Payload: {payload}")  # Debug

            response = await self.client.post(
                f"{self.base_url}/api/caddy/backup",
                json=payload,
                headers={"Content-Type": "application/json"}  # Expliziter Content-Type
            )

            print(f"Backup Response Status: {response.status_code}")  # Debug

            if response.status_code == 200:
                data = response.json()
                self.operation_completed.emit(data)
                return data
            else:
                # Detaillierte Fehleranalyse
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        # FastAPI Validation Error Format
                        if isinstance(error_data["detail"], list):
                            errors = []
                            for err in error_data["detail"]:
                                loc = " -> ".join(str(x) for x in err.get("loc", []))
                                msg = err.get("msg", "Unknown error")
                                errors.append(f"{loc}: {msg}")
                            error_msg = "Validation errors:\n" + "\n".join(errors)
                        else:
                            error_msg = str(error_data["detail"])
                    else:
                        error_msg = str(error_data)
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"

                print(f"Backup Error: {error_msg}")  # Debug
                self.error_occurred.emit(f"Backup-Fehler: {error_msg}")
                return {"success": False, "error": error_msg}

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            self.error_occurred.emit(f"Backup-Fehler: {error_msg}")
            return {"success": False, "error": error_msg}
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