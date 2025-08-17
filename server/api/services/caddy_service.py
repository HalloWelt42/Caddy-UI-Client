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
import psutil
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

        # Prüfe zuerst ob Caddy via Admin API erreichbar ist
        try:
            response = await self.client.get(f"{settings.caddy_api_url}/config/")
            if response.status_code == 200:
                # Caddy läuft und API ist erreichbar
                # Versuche PID aus Datei zu lesen
                pid = None
                pid_file = settings.data_dir / "caddy.pid"
                if pid_file.exists():
                    try:
                        with open(pid_file, "r") as f:
                            pid = int(f.read().strip())
                    except:
                        pass

                return {
                    "status": CaddyStatus.RUNNING,
                    "message": "Caddy läuft",
                    "admin_api": True,
                    "pid": pid,
                    "config": response.json() if response.content else {}
                }
        except (httpx.ConnectError, httpx.TimeoutException):
            pass

        # Admin API nicht erreichbar, prüfe ob Prozess läuft
        # Methode 1: Gespeicherte PID prüfen
        pid_file = settings.data_dir / "caddy.pid"
        if pid_file.exists():
            try:
                with open(pid_file, "r") as f:
                    pid = int(f.read().strip())

                # Prüfe ob Prozess mit dieser PID existiert
                if psutil.pid_exists(pid):
                    try:
                        proc = psutil.Process(pid)
                        if "caddy" in proc.name().lower():
                            return {
                                "status": CaddyStatus.RUNNING,
                                "message": f"Caddy läuft (PID: {pid}, Admin API nicht erreichbar)",
                                "admin_api": False,
                                "pid": pid
                            }
                    except:
                        pass
            except:
                pass

        # Methode 2: Nach Caddy-Prozessen suchen
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'caddy' in proc.info['name'].lower():
                        cmdline = proc.info.get('cmdline', [])
                        # Prüfe ob es unser Caddy ist (mit unserer Config)
                        if any(str(CADDYFILE) in str(arg) for arg in cmdline):
                            return {
                                "status": CaddyStatus.RUNNING,
                                "message": f"Caddy läuft (PID: {proc.info['pid']})",
                                "admin_api": False,
                                "pid": proc.info['pid']
                            }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except:
            pass

        # Caddy läuft nicht
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

            # Log-Datei für Caddy
            log_file = settings.logs_dir / "caddy.log"
            settings.logs_dir.mkdir(parents=True, exist_ok=True)

            # WICHTIG: Starte Caddy als unabhängigen Prozess
            if platform.system() == "Darwin":  # macOS
                # macOS: Drei Optionen für unabhängige Prozesse

                # Option 1: Einfachste Methode - ohne nohup/setsid
                cmd = [
                    str(CADDY_BINARY),
                    "run",
                    "--config", str(CADDYFILE),
                    "--adapter", "caddyfile"
                ]

                # Versuche zuerst die einfache Methode
                try:
                    with open(log_file, 'a') as log:
                        self.process = subprocess.Popen(
                            cmd,
                            stdout=log,
                            stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL,
                            cwd=str(settings.project_root),
                            start_new_session=True  # Ohne preexec_fn
                        )
                    print(f"✅ Caddy gestartet mit start_new_session")

                except Exception as e1:
                    print(f"⚠️ start_new_session fehlgeschlagen: {e1}, versuche nohup...")

                    # Option 2: Mit nohup (falls verfügbar)
                    try:
                        nohup_cmd = ["/usr/bin/nohup"] + cmd

                        with open(log_file, 'a') as log:
                            self.process = subprocess.Popen(
                                nohup_cmd,
                                stdout=log,
                                stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL,
                                cwd=str(settings.project_root)
                            )
                        print(f"✅ Caddy gestartet mit nohup")

                    except Exception as e2:
                        print(f"⚠️ nohup fehlgeschlagen: {e2}, verwende Standard-Methode...")

                        # Option 3: Standard-Methode ohne special flags
                        with open(log_file, 'a') as log:
                            self.process = subprocess.Popen(
                                cmd,
                                stdout=log,
                                stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL,
                                cwd=str(settings.project_root)
                            )
                        print(f"✅ Caddy gestartet (Standard-Methode)")

            elif platform.system() == "Windows":
                # Windows: CREATE_NEW_PROCESS_GROUP macht Prozess unabhängig
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                DETACHED_PROCESS = 0x00000008

                with open(log_file, 'a') as log:
                    self.process = subprocess.Popen(
                        [
                            str(CADDY_BINARY),
                            "run",
                            "--config", str(CADDYFILE),
                            "--adapter", "caddyfile"
                        ],
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        stdin=subprocess.DEVNULL,
                        cwd=str(settings.project_root),
                        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
                    )
                print(f"✅ Caddy gestartet (Windows, unabhängiger Prozess)")

            else:
                # Linux/Unix: Standard-Methode mit start_new_session
                with open(log_file, 'a') as log:
                    self.process = subprocess.Popen(
                        [
                            str(CADDY_BINARY),
                            "run",
                            "--config", str(CADDYFILE),
                            "--adapter", "caddyfile"
                        ],
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        stdin=subprocess.DEVNULL,
                        cwd=str(settings.project_root),
                        start_new_session=True
                    )
                print(f"✅ Caddy gestartet (Linux, neue Session)")

            # Speichere PID für späteren Zugriff
            pid = self.process.pid
            pid_file = settings.data_dir / "caddy.pid"
            settings.data_dir.mkdir(parents=True, exist_ok=True)
            with open(pid_file, "w") as f:
                f.write(str(pid))

            print(f"✅ Caddy gestartet mit PID: {pid}")

            # Warte kurz und prüfe Status
            await asyncio.sleep(2)

            # Prüfe ob Prozess noch läuft
            if self.process.poll() is None:
                # Zusätzlich prüfen ob Caddy wirklich läuft (via psutil)
                try:
                    if psutil.pid_exists(pid):
                        proc = psutil.Process(pid)
                        if "caddy" in proc.name().lower():
                            return {
                                "success": True,
                                "message": f"Caddy erfolgreich gestartet (PID: {pid})",
                                "pid": pid,
                                "independent": True
                            }
                except:
                    # Fallback: Prozess läuft noch, also nehmen wir an es ist OK
                    return {
                        "success": True,
                        "message": f"Caddy gestartet (PID: {pid})",
                        "pid": pid,
                        "independent": True
                    }

                return {
                    "success": True,
                    "message": f"Caddy gestartet (PID: {pid})",
                    "pid": pid,
                    "independent": True
                }
            else:
                # Prozess ist bereits beendet - lies Logs für Fehlerdetails
                error_msg = "Caddy konnte nicht gestartet werden."

                # Versuche Log-Datei zu lesen für mehr Details
                if log_file.exists():
                    try:
                        with open(log_file, 'r') as f:
                            # Lies die letzten 20 Zeilen
                            lines = f.readlines()
                            last_lines = lines[-20:] if len(lines) > 20 else lines
                            error_msg += f"\n\nLetzte Log-Einträge:\n{''.join(last_lines)}"
                    except:
                        pass

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
            # Methode 1: Über Admin API
            try:
                response = await self.client.post(f"{settings.caddy_api_url}/stop")
                if response.status_code == 200:
                    # Lösche PID-Datei
                    pid_file = settings.data_dir / "caddy.pid"
                    if pid_file.exists():
                        pid_file.unlink()

                    self.process = None
                    return {
                        "success": True,
                        "message": "Caddy über Admin API gestoppt"
                    }
            except:
                pass

            # Methode 2: Über gespeicherte PID
            pid_file = settings.data_dir / "caddy.pid"
            if pid_file.exists():
                try:
                    with open(pid_file, "r") as f:
                        pid = int(f.read().strip())

                    if psutil.pid_exists(pid):
                        proc = psutil.Process(pid)
                        proc.terminate()
                        try:
                            proc.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            proc.kill()

                        pid_file.unlink()
                        self.process = None
                        return {
                            "success": True,
                            "message": f"Caddy-Prozess (PID: {pid}) beendet"
                        }
                except Exception as e:
                    print(f"Fehler beim Stoppen via PID: {e}")

            # Methode 3: Prozess-Object wenn vorhanden
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

            # Methode 4: Nach Caddy-Prozess suchen
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if 'caddy' in proc.info['name'].lower():
                            cmdline = proc.info.get('cmdline', [])
                            if any(str(CADDYFILE) in str(arg) for arg in cmdline):
                                proc.terminate()
                                try:
                                    proc.wait(timeout=5)
                                except psutil.TimeoutExpired:
                                    proc.kill()

                                return {
                                    "success": True,
                                    "message": f"Caddy-Prozess (PID: {proc.info['pid']}) gefunden und beendet"
                                }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as e:
                print(f"Fehler bei Prozess-Suche: {e}")

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
        # Erstelle Caddyfile mit automatischem HTTPS
        caddyfile_content = """# Caddy Configuration
# Admin API
{
    admin localhost:2019
    # Automatisches HTTPS mit Let's Encrypt
    email admin@localhost
    # Lokale CA für Entwicklung
    local_certs
}

# Default site mit automatischem HTTPS
:443 {
    tls internal
    respond "Caddy is running with HTTPS!"
}

# HTTP to HTTPS redirect
:80 {
    redir https://{host}{uri} permanent
}
"""

        CADDYFILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CADDYFILE, "w") as f:
            f.write(caddyfile_content)

        print(f"✅ Standard Caddyfile mit HTTPS erstellt: {CADDYFILE}")

    async def add_route(self, domain: str, upstream: str, path: str = "/") -> Dict[str, Any]:
        """Fügt eine neue Route hinzu"""
        try:
            # Lese aktuelle Caddyfile
            if not CADDYFILE.exists():
                await self.create_default_config()

            with open(CADDYFILE, "r") as f:
                current_config = f.read()

            # Bestimme ob es eine lokale Domain ist
            is_local = domain.endswith('.local') or domain == 'localhost' or '.' not in domain

            # Füge neue Route mit HTTPS hinzu
            if is_local:
                # Lokale Domain mit internem Zertifikat
                new_route = f"""
# Route für {domain}
{domain} {{
    tls internal
    reverse_proxy {upstream}
}}
"""
            else:
                # Öffentliche Domain mit Let's Encrypt
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
                    [str(CADDY_BINARY), "reload", "--config", str(CADDYFILE), "--adapter", "caddyfile"],
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
                "message": f"Route {domain} -> {upstream} mit HTTPS hinzugefügt"
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

            # Backup der Caddyfile
            backup_file = settings.backups_dir / f"caddyfile_{name}.backup"
            settings.backups_dir.mkdir(parents=True, exist_ok=True)

            # Prüfe ob Caddyfile existiert
            if CADDYFILE.exists():
                import shutil
                shutil.copy2(CADDYFILE, backup_file)

                return {
                    "success": True,
                    "message": f"Backup erstellt: {backup_file.name}",
                    "path": str(backup_file),
                    "filename": backup_file.name
                }
            else:
                # Erstelle Default-Config wenn keine existiert
                await self.create_default_config()

                if CADDYFILE.exists():
                    import shutil
                    shutil.copy2(CADDYFILE, backup_file)

                    return {
                        "success": True,
                        "message": f"Default-Config gesichert: {backup_file.name}",
                        "path": str(backup_file),
                        "filename": backup_file.name
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

            # Restore der Caddyfile
            import shutil

            # Backup der aktuellen Config vor dem Restore
            temp_backup = None
            if CADDYFILE.exists():
                temp_backup = CADDYFILE.with_suffix('.backup.tmp')
                shutil.copy2(CADDYFILE, temp_backup)

            try:
                # Restore durchführen
                shutil.copy2(backup_file, CADDYFILE)

                # Wenn Caddy läuft, Config neu laden
                status = await self.get_status()
                if status["status"] == "running":
                    # Caddy reload mit Caddyfile
                    result = subprocess.run(
                        [str(CADDY_BINARY), "reload", "--config", str(CADDYFILE), "--adapter", "caddyfile"],
                        capture_output=True,
                        text=True,
                        cwd=str(settings.project_root)
                    )

                    if result.returncode != 0:
                        # Restore der alten Config bei Fehler
                        if temp_backup and temp_backup.exists():
                            shutil.copy2(temp_backup, CADDYFILE)
                            temp_backup.unlink()

                        return {
                            "success": False,
                            "error": f"Config ungültig: {result.stderr}"
                        }

                # Cleanup temp backup
                if temp_backup and temp_backup.exists():
                    temp_backup.unlink()

                return {
                    "success": True,
                    "message": f"Konfiguration wiederhergestellt von: {backup_name}"
                }

            except Exception as e:
                # Restore der alten Config bei Fehler
                if temp_backup and temp_backup.exists():
                    shutil.copy2(temp_backup, CADDYFILE)
                    temp_backup.unlink()

                return {
                    "success": False,
                    "error": f"Restore-Fehler: {str(e)}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Restore-Fehler: {str(e)}"
            }

    async def list_backups(self) -> List[Dict[str, Any]]:
        """Liste alle Backups auf"""
        try:
            from datetime import datetime

            backups = []
            settings.backups_dir.mkdir(parents=True, exist_ok=True)

            # Suche nach .backup Dateien
            for backup_file in settings.backups_dir.glob("caddyfile_*.backup"):
                stat = backup_file.stat()
                backups.append({
                    "name": backup_file.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "modified_str": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })

            # Sortiere nach Änderungsdatum (neueste zuerst)
            backups.sort(key=lambda x: x["modified"], reverse=True)

            return backups

        except Exception as e:
            print(f"Fehler beim Auflisten der Backups: {e}")
            return []

    async def restore_config(self, backup_name: str) -> Dict[str, Any]:
        """Stellt eine gesicherte Konfiguration wieder her"""
        try:
            backup_file = settings.backups_dir / backup_name

            if not backup_file.exists():
                return {
                    "success": False,
                    "error": f"Backup-Datei nicht gefunden: {backup_name}"
                }

            # GEÄNDERT: Restore der Caddyfile statt JSON
            import shutil
            shutil.copy2(backup_file, CADDYFILE)

            # Wenn Caddy läuft, Config neu laden
            status = await self.get_status()
            if status["status"] == CaddyStatus.RUNNING:
                # Caddy reload mit Caddyfile
                result = subprocess.run(
                    [str(CADDY_BINARY), "reload", "--config", str(CADDYFILE), "--adapter", "caddyfile"],
                    capture_output=True,
                    text=True,
                    cwd=str(settings.project_root)
                )

                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Fehler beim Laden der Config: {result.stderr}"
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