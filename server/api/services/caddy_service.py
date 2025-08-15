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
import os
import platform
import subprocess
import tarfile
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

from server.config.settings import settings
from shared.utils.paths import CADDY_JSON_CONFIG, CADDY_BINARY, CERTS_DIR, CADDYFILE


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
            # Stelle sicher, dass Config-Verzeichnis existiert
            CADDYFILE.parent.mkdir(parents=True, exist_ok=True)

            # Erstelle Standard-Config wenn nicht vorhanden
            if not CADDYFILE.exists():
                await self.create_default_config()

            # Prüfe ob die Binary existiert und ausführbar ist
            if not CADDY_BINARY.exists():
                return {
                    "success": False,
                    "error": f"Caddy Binary nicht gefunden: {CADDY_BINARY}"
                }

            if not os.access(CADDY_BINARY, os.X_OK):
                return {
                    "success": False,
                    "error": f"Caddy Binary ist nicht ausführbar: {CADDY_BINARY}"
                }

            print(f"🚀 Starte Caddy mit Caddyfile: {CADDYFILE}")

            # Starte Caddy mit Caddyfile
            self.process = subprocess.Popen(
                [
                    str(CADDY_BINARY),
                    "run",
                    "--config", str(CADDYFILE),
                    "--adapter", "caddyfile"
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
                stdout = self.process.stdout.read().decode() if self.process.stdout else ""
                error_msg = f"Caddy konnte nicht gestartet werden.\nSTDERR: {stderr}\nSTDOUT: {stdout}"
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }

        except Exception as e:
            print(f"❌ Start-Fehler: {str(e)}")
            import traceback
            traceback.print_exc()
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
        # Erstelle Caddyfile statt JSON
        caddyfile_content = """# Caddy Configuration
# Admin API
{
    admin localhost:2019
}

# Default site
:443 {
    respond "Caddy is running!"
}
"""

        CADDYFILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CADDYFILE, "w") as f:
            f.write(caddyfile_content)

        print(f"✅ Standard Caddyfile erstellt: {CADDYFILE}")

    async def add_route(self, domain: str, upstream: str, path: str = "/") -> Dict[str, Any]:
        """Fügt eine neue Route hinzu"""
        try:
            # Lese aktuelle Caddyfile
            if not CADDYFILE.exists():
                await self.create_default_config()

            with open(CADDYFILE, "r") as f:
                current_config = f.read()

            # Füge neue Route hinzu
            new_route = f"""
# Route für {domain}
{domain} {{
    reverse_proxy {upstream}
}}
"""

            # Schreibe aktualisierte Config
            with open(CADDYFILE, "w") as f:
                f.write(current_config + new_route)

            # Reload Caddy wenn es läuft
            status = await self.get_status()
            if status["status"] == CaddyStatus.RUNNING:
                # Caddy reload
                result = subprocess.run(
                    [str(CADDY_BINARY), "reload", "--config", str(CADDYFILE)],
                    capture_output=True,
                    text=True,
                    cwd=str(settings.project_root)
                )

                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Reload fehlgeschlagen: {result.stderr}"
                    }

            return {
                "success": True,
                "message": f"Route {domain} -> {upstream} hinzugefügt"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Fehler beim Hinzufügen der Route: {str(e)}"
            }

    async def remove_route(self, domain: str) -> Dict[str, Any]:
        """Entfernt eine Route"""
        try:
            if not CADDYFILE.exists():
                return {
                    "success": False,
                    "error": f"Caddyfile nicht gefunden"
                }

            with open(CADDYFILE, "r") as f:
                lines = f.readlines()

            # Finde und entferne den Domain-Block
            new_lines = []
            i = 0
            found = False
            while i < len(lines):
                line = lines[i]
                # Prüfe ob dies der gesuchte Domain-Block ist
                if domain in line and "{" in line and not line.strip().startswith("#"):
                    found = True
                    # Überspringe diesen Block
                    while i < len(lines) and "}" not in lines[i]:
                        i += 1
                    i += 1  # Überspringe auch die schließende Klammer
                    continue
                new_lines.append(line)
                i += 1

            if not found:
                return {
                    "success": False,
                    "error": f"Route für {domain} nicht gefunden"
                }

            # Schreibe aktualisierte Config
            with open(CADDYFILE, "w") as f:
                f.writelines(new_lines)

            # Reload Caddy wenn es läuft
            status = await self.get_status()
            if status["status"] == CaddyStatus.RUNNING:
                result = subprocess.run(
                    [str(CADDY_BINARY), "reload", "--config", str(CADDYFILE)],
                    capture_output=True,
                    text=True,
                    cwd=str(settings.project_root)
                )

                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Reload fehlgeschlagen: {result.stderr}"
                    }

            return {
                "success": True,
                "message": f"Route für {domain} entfernt"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Fehler beim Entfernen der Route: {str(e)}"
            }

    async def get_routes(self) -> List[Dict[str, Any]]:
        """Listet alle konfigurierten Routes auf"""
        routes = []

        if not CADDYFILE.exists():
            return routes

        try:
            with open(CADDYFILE, "r") as f:
                lines = f.readlines()

            # Parse Caddyfile für Routes (vereinfacht)
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                # Suche nach Domain-Blöcken
                if line and not line.startswith("#") and "{" in line:
                    domain = line.split("{")[0].strip()
                    # Suche nach reverse_proxy in diesem Block
                    i += 1
                    while i < len(lines) and "}" not in lines[i]:
                        if "reverse_proxy" in lines[i]:
                            upstream = lines[i].replace("reverse_proxy", "").strip()
                            routes.append({
                                "domain": domain,
                                "path": "/",
                                "upstream": upstream
                            })
                            break
                        i += 1
                i += 1

            return routes

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