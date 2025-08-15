"""
Caddy Service - Installation und Verwaltung
"""
import sys
from pathlib import Path
# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import asyncio
import httpx
import json
import platform
import subprocess
import tarfile
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

from server.config.settings import settings
from shared.utils.paths import CADDY_JSON_CONFIG, CADDY_BINARY, CERTS_DIR

class CaddyStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    NOT_INSTALLED = "not_installed"
    ERROR = "error"

class CaddyService:
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0, read=30.0),
            follow_redirects=True
        )

    async def get_status(self) -> Dict[str, Any]:
        """Caddy-Status abrufen"""
        if not settings.is_caddy_installed:
            return {
                "status": CaddyStatus.NOT_INSTALLED,
                "message": "Caddy ist nicht installiert"
            }

        try:
            # Prüfe ob Caddy läuft via Admin API
            response = await self.client.get(f"{settings.caddy_api_url}/config/")
            if response.status_code == 200:
                return {
                    "status": CaddyStatus.RUNNING,
                    "message": "Caddy läuft",
                    "admin_api": True,
                    "config": response.json() if response.content else {}
                }
        except (httpx.ConnectError, httpx.TimeoutException):
            pass

        # Prüfe ob Prozess läuft
        if self.process and self.process.poll() is None:
            return {
                "status": CaddyStatus.RUNNING,
                "message": "Caddy-Prozess läuft (Admin API nicht erreichbar)",
                "admin_api": False
            }

        return {
            "status": CaddyStatus.STOPPED,
            "message": "Caddy ist gestoppt"
        }

    async def install_caddy(self, progress_callback=None) -> Dict[str, Any]:
        """Caddy für macOS ARM64 installieren"""
        try:
            # Platform Check
            system = platform.system()
            machine = platform.machine()

            print(f"🖥️  System: {system}, Machine: {machine}")

            if system != "Darwin":
                return {
                    "success": False,
                    "error": f"Installation nur für macOS unterstützt (aktuell: {system})"
                }

            if machine != "arm64":
                return {
                    "success": False,
                    "error": f"Installation nur für ARM64 unterstützt (aktuell: {machine})"
                }

            # Download-URL erstellen
            url = settings.caddy_download_url_mac.format(version=settings.caddy_version)
            print(f"📥 Download URL: {url}")

            if progress_callback:
                await progress_callback("Download startet...", 10)

            # Download Caddy
            async with self.client.stream("GET", url, follow_redirects=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))

                with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_file:
                    downloaded = 0
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        tmp_file.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size:
                            progress = 10 + int((downloaded / total_size) * 60)
                            await progress_callback(f"Download: {downloaded}/{total_size} bytes", progress)

                    tmp_path = Path(tmp_file.name)

            if progress_callback:
                await progress_callback("Entpacke Caddy...", 75)

            # Entpacken
            with tarfile.open(tmp_path, "r:gz") as tar:
                # Finde Caddy-Binary im Archiv
                for member in tar.getmembers():
                    if member.name == "caddy" or member.name.endswith("/caddy"):
                        # Extrahiere direkt zum Zielort
                        CADDY_BINARY.parent.mkdir(parents=True, exist_ok=True)

                        with tar.extractfile(member) as source:
                            with open(CADDY_BINARY, "wb") as target:
                                target.write(source.read())

                        # Ausführbar machen
                        CADDY_BINARY.chmod(0o755)
                        break

            # Temp-Datei löschen
            tmp_path.unlink()

            if progress_callback:
                await progress_callback("Installation abgeschlossen", 90)

            # Root-Zertifikat installieren
            await self.install_root_certificate(progress_callback)

            if progress_callback:
                await progress_callback("Fertig!", 100)

            return {
                "success": True,
                "message": f"Caddy {settings.caddy_version} erfolgreich installiert",
                "path": str(CADDY_BINARY)
            }

        except Exception as e:
            print(f"❌ Installationsfehler: {str(e)}")
            return {
                "success": False,
                "error": f"Installationsfehler: {str(e)}"
            }

    async def install_root_certificate(self, progress_callback=None) -> Dict[str, Any]:
        """Root-Zertifikat für lokale HTTPS-Entwicklung installieren"""
        try:
            if progress_callback:
                await progress_callback("Installiere Root-Zertifikat...", 95)

            # Caddy trust für lokale CA
            result = subprocess.run(
                [str(CADDY_BINARY), "trust"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Root-Zertifikat erfolgreich installiert"
                }
            else:
                return {
                    "success": False,
                    "error": f"Zertifikat-Installation fehlgeschlagen: {result.stderr}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Zertifikat-Fehler: {str(e)}"
            }

    async def start(self) -> Dict[str, Any]:
        """Caddy starten"""
        if not settings.is_caddy_installed:
            return {
                "success": False,
                "error": "Caddy ist nicht installiert"
            }

        status = await self.get_status()
        if status["status"] == CaddyStatus.RUNNING:
            return {
                "success": False,
                "error": "Caddy läuft bereits"
            }

        try:
            # Erstelle Standard-Config wenn nicht vorhanden
            if not CADDY_JSON_CONFIG.exists():
                await self.create_default_config()

            # Starte Caddy mit JSON-Config
            self.process = subprocess.Popen(
                [
                    str(CADDY_BINARY),
                    "run",
                    "--config", str(CADDY_JSON_CONFIG),
                    "--adapter", "json"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(settings.project_root)
            )

            # Warte kurz und prüfe Status
            await asyncio.sleep(2)

            if self.process.poll() is None:
                return {
                    "success": True,
                    "message": "Caddy erfolgreich gestartet",
                    "pid": self.process.pid
                }
            else:
                stderr = self.process.stderr.read().decode() if self.process.stderr else ""
                return {
                    "success": False,
                    "error": f"Caddy konnte nicht gestartet werden: {stderr}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Startfehler: {str(e)}"
            }

    async def stop(self) -> Dict[str, Any]:
        """Caddy stoppen"""
        try:
            # Versuche über Admin API
            try:
                response = await self.client.post(f"{settings.caddy_api_url}/stop")
                if response.status_code == 200:
                    self.process = None
                    return {
                        "success": True,
                        "message": "Caddy über Admin API gestoppt"
                    }
            except:
                pass

            # Fallback: Prozess beenden
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()

                self.process = None
                return {
                    "success": True,
                    "message": "Caddy-Prozess beendet"
                }

            return {
                "success": False,
                "error": "Kein laufender Caddy-Prozess gefunden"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Stoppfehler: {str(e)}"
            }

    async def restart(self) -> Dict[str, Any]:
        """Caddy neu starten"""
        stop_result = await self.stop()
        if not stop_result.get("success"):
            # Wenn Stop fehlschlägt, trotzdem versuchen zu starten
            pass

        await asyncio.sleep(1)
        return await self.start()

    async def create_default_config(self) -> None:
        """Erstellt eine Standard-Caddy-Konfiguration"""
        config = {
            "admin": {
                "listen": f"{settings.caddy_admin_host}:{settings.caddy_admin_port}"
            },
            "apps": {
                "http": {
                    "servers": {
                        "srv0": {
                            "listen": [":443"],
                            "routes": []
                        }
                    }
                }
            }
        }

        CADDY_JSON_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        with open(CADDY_JSON_CONFIG, "w") as f:
            json.dump(config, f, indent=2)

    async def add_route(self, domain: str, upstream: str, path: str = "/") -> Dict[str, Any]:
        """Fügt eine neue Route hinzu"""
        try:
            # Aktuelle Config laden
            response = await self.client.get(f"{settings.caddy_api_url}/config/")
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": "Konnte aktuelle Konfiguration nicht laden"
                }

            config = response.json()

            # Neue Route erstellen
            new_route = {
                "match": [{"host": [domain]}],
                "handle": [
                    {
                        "handler": "reverse_proxy",
                        "upstreams": [{"dial": upstream}]
                    }
                ]
            }

            if path != "/":
                new_route["match"][0]["path"] = [path]

            # Route zur Config hinzufügen
            if "apps" not in config:
                config["apps"] = {}
            if "http" not in config["apps"]:
                config["apps"]["http"] = {"servers": {}}
            if "srv0" not in config["apps"]["http"]["servers"]:
                config["apps"]["http"]["servers"]["srv0"] = {"listen": [":443"], "routes": []}

            config["apps"]["http"]["servers"]["srv0"]["routes"].append(new_route)

            # Config updaten
            response = await self.client.put(
                f"{settings.caddy_api_url}/config/",
                json=config
            )

            if response.status_code == 200:
                # Config auch lokal speichern
                with open(CADDY_JSON_CONFIG, "w") as f:
                    json.dump(config, f, indent=2)

                return {
                    "success": True,
                    "message": f"Route {domain} -> {upstream} hinzugefügt"
                }
            else:
                return {
                    "success": False,
                    "error": f"Fehler beim Update: {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Fehler beim Hinzufügen der Route: {str(e)}"
            }

    async def remove_route(self, domain: str) -> Dict[str, Any]:
        """Entfernt eine Route"""
        try:
            response = await self.client.get(f"{settings.caddy_api_url}/config/")
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": "Konnte aktuelle Konfiguration nicht laden"
                }

            config = response.json()

            # Route finden und entfernen
            routes = config.get("apps", {}).get("http", {}).get("servers", {}).get("srv0", {}).get("routes", [])
            original_count = len(routes)

            routes = [
                r for r in routes
                if not (r.get("match", [{}])[0].get("host", [None])[0] == domain)
            ]

            if len(routes) == original_count:
                return {
                    "success": False,
                    "error": f"Route für {domain} nicht gefunden"
                }

            config["apps"]["http"]["servers"]["srv0"]["routes"] = routes

            # Config updaten
            response = await self.client.put(
                f"{settings.caddy_api_url}/config/",
                json=config
            )

            if response.status_code == 200:
                with open(CADDY_JSON_CONFIG, "w") as f:
                    json.dump(config, f, indent=2)

                return {
                    "success": True,
                    "message": f"Route für {domain} entfernt"
                }
            else:
                return {
                    "success": False,
                    "error": f"Fehler beim Update: {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Fehler beim Entfernen der Route: {str(e)}"
            }

    async def get_routes(self) -> List[Dict[str, Any]]:
        """Listet alle konfigurierten Routes auf"""
        try:
            response = await self.client.get(f"{settings.caddy_api_url}/config/")
            if response.status_code != 200:
                return []

            config = response.json()
            routes = config.get("apps", {}).get("http", {}).get("servers", {}).get("srv0", {}).get("routes", [])

            result = []
            for route in routes:
                match = route.get("match", [{}])[0]
                handle = route.get("handle", [{}])[0]

                if handle.get("handler") == "reverse_proxy":
                    upstream = handle.get("upstreams", [{}])[0].get("dial", "")
                    result.append({
                        "domain": match.get("host", [""])[0],
                        "path": match.get("path", ["/"])[0] if "path" in match else "/",
                        "upstream": upstream
                    })

            return result

        except Exception:
            return []

    async def backup_config(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Sichert die aktuelle Konfiguration"""
        try:
            from datetime import datetime

            if not name:
                name = datetime.now().strftime("%Y%m%d_%H%M%S")

            backup_file = settings.backups_dir / f"caddy_config_{name}.json"

            # Aktuelle Config laden
            if CADDY_JSON_CONFIG.exists():
                with open(CADDY_JSON_CONFIG, "r") as f:
                    config = json.load(f)

                with open(backup_file, "w") as f:
                    json.dump(config, f, indent=2)

                return {
                    "success": True,
                    "message": f"Backup erstellt: {backup_file.name}",
                    "path": str(backup_file)
                }
            else:
                return {
                    "success": False,
                    "error": "Keine Konfiguration zum Sichern vorhanden"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Backup-Fehler: {str(e)}"
            }

    async def restore_config(self, backup_name: str) -> Dict[str, Any]:
        """Stellt eine gesicherte Konfiguration wieder her"""
        try:
            backup_file = settings.backups_dir / backup_name

            if not backup_file.exists():
                return {
                    "success": False,
                    "error": f"Backup-Datei nicht gefunden: {backup_name}"
                }

            with open(backup_file, "r") as f:
                config = json.load(f)

            # Config lokal speichern
            with open(CADDY_JSON_CONFIG, "w") as f:
                json.dump(config, f, indent=2)

            # Wenn Caddy läuft, Config neu laden
            status = await self.get_status()
            if status["status"] == CaddyStatus.RUNNING:
                response = await self.client.put(
                    f"{settings.caddy_api_url}/config/",
                    json=config
                )

                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Fehler beim Laden der Config: {response.text}"
                    }

            return {
                "success": True,
                "message": f"Konfiguration wiederhergestellt von: {backup_name}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Restore-Fehler: {str(e)}"
            }