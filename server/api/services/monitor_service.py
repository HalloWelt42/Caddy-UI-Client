"""
Monitoring Service für System-Metriken
"""
import sys
from pathlib import Path
# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import asyncio
import psutil
import time
from typing import Dict, Any, List, Optional
from collections import deque
from datetime import datetime

from server.config.settings import settings

class MonitorService:
    def __init__(self):
        self.metrics_history = deque(maxlen=settings.metrics_history_size)
        self.monitoring_task: Optional[asyncio.Task] = None
        self.request_count = 0
        self.last_request_time = time.time()
        self.response_times = deque(maxlen=100)

    async def start_monitoring(self):
        """Startet den Monitoring-Task"""
        if self.monitoring_task and not self.monitoring_task.done():
            return

        self.monitoring_task = asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self):
        """Stoppt den Monitoring-Task"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self):
        """Hauptschleife für Monitoring"""
        while True:
            try:
                metrics = await self.collect_metrics()
                self.metrics_history.append(metrics)
                await asyncio.sleep(settings.monitor_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(settings.monitor_interval)

    async def collect_metrics(self) -> Dict[str, Any]:
        """Sammelt aktuelle System-Metriken"""
        # CPU und Memory
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()

        # Disk
        disk = psutil.disk_usage('/')

        # Network
        net_io = psutil.net_io_counters()

        # Docker Status prüfen
        docker_running = await self._check_docker_status()

        # Caddy Status prüfen
        caddy_status = await self._check_caddy_status()

        # Request-Metriken
        current_time = time.time()
        time_diff = current_time - self.last_request_time
        requests_per_sec = self.request_count / time_diff if time_diff > 0 else 0

        # Response Time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0

        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "cores": psutil.cpu_count()
            },
            "memory": {
                "percent": memory.percent,
                "used": memory.used,
                "total": memory.total,
                "available": memory.available
            },
            "disk": {
                "percent": disk.percent,
                "used": disk.used,
                "total": disk.total,
                "free": disk.free
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            },
            "services": {
                "docker": docker_running,
                "caddy": caddy_status
            },
            "requests": {
                "count": self.request_count,
                "per_second": round(requests_per_sec, 2),
                "avg_response_time": round(avg_response_time, 2)
            }
        }

    async def _check_docker_status(self) -> bool:
        """Prüft ob Docker läuft"""
        try:
            # Methode 1: Prüfe Docker Desktop Prozess (macOS)
            for proc in psutil.process_iter(['name', 'cmdline']):
                try:
                    # Docker Desktop auf macOS
                    if 'Docker Desktop' in proc.info['name']:
                        return True
                    # Docker Backend Service
                    if 'com.docker.backend' in proc.info['name']:
                        return True
                    # Prüfe cmdline für Docker Desktop
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any('Docker' in str(arg) and 'Desktop' in str(arg) for arg in cmdline):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Methode 2: Versuche Docker API zu erreichen
            try:
                import docker
                client = docker.from_env()
                client.ping()
                client.close()
                return True
            except:
                pass

            return False
        except Exception as e:
            print(f"Docker Status Check Error: {e}")
            return False

    def set_caddy_service(self, service):
        """Setzt die Caddy-Service Referenz (vermeidet zirkuläre Imports)"""
        self._caddy_service = service

    async def _check_caddy_status(self) -> str:
        """Prüft Caddy-Status"""
        try:
            if hasattr(self, '_caddy_service'):
                status = await self._caddy_service.get_status()
                return status.get("status", "unknown")
            return "unknown"
        except:
            return "error"

    def record_request(self):
        """Zählt einen Request"""
        self.request_count += 1

    def record_response_time(self, time_ms: float):
        """Speichert Response-Zeit"""
        self.response_times.append(time_ms)

    async def get_current_metrics(self) -> Dict[str, Any]:
        """Gibt aktuelle Metriken zurück"""
        return await self.collect_metrics()

    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Gibt Metrik-Historie zurück"""
        return list(self.metrics_history)

    async def get_docker_containers(self) -> List[Dict[str, Any]]:
        """Liste der Docker-Container"""
        containers = []

        try:
            import docker

            # Verwende Docker Desktop Socket für macOS
            socket_paths = [
                "unix:///Users/alpha/.docker/run/docker.sock",  # Docker Desktop
                "unix:///var/run/docker.sock",  # Standard
            ]

            client = None
            for socket_path in socket_paths:
                try:
                    # Versuche verschiedene Socket-Pfade
                    if "alpha" in socket_path:
                        # Ersetze alpha mit dem aktuellen User
                        import os
                        socket_path = socket_path.replace("alpha", os.environ.get("USER", "alpha"))

                    client = docker.DockerClient(base_url=socket_path)
                    client.ping()  # Test ob Verbindung funktioniert
                    break
                except:
                    continue

            if not client:
                # Fallback: from_env()
                client = docker.from_env()

            for container in client.containers.list(all=True):
                # Ports formatieren
                ports_dict = {}
                if container.attrs.get('NetworkSettings', {}).get('Ports'):
                    for internal, external in container.attrs['NetworkSettings']['Ports'].items():
                        if external:
                            ports_dict[internal] = f"{external[0]['HostPort']}"

                containers.append({
                    "id": container.short_id,
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else container.image.short_id,
                    "status": container.status,
                    "created": container.attrs['Created'],
                    "ports": ports_dict
                })

            client.close()

        except ImportError:
            print("Docker Python-Bibliothek nicht installiert")
        except Exception as e:
            print(f"Docker Container Error: {e}")
            import traceback
            traceback.print_exc()

        return containers

    async def control_docker_container(self, container_id: str, action: str) -> Dict[str, Any]:
        """Steuert Docker-Container (start/stop/restart)"""
        try:
            import docker
            import os

            # Socket-Pfad für Docker Desktop
            socket_paths = [
                f"unix:///Users/{os.environ.get('USER', 'alpha')}/.docker/run/docker.sock",
                "unix:///var/run/docker.sock",
            ]

            client = None
            for socket_path in socket_paths:
                try:
                    client = docker.DockerClient(base_url=socket_path)
                    client.ping()
                    break
                except:
                    continue

            if not client:
                client = docker.from_env()

            container = client.containers.get(container_id)

            if action == "start":
                container.start()
                message = f"Container {container.name} gestartet"
            elif action == "stop":
                container.stop()
                message = f"Container {container.name} gestoppt"
            elif action == "restart":
                container.restart()
                message = f"Container {container.name} neu gestartet"
            else:
                return {
                    "success": False,
                    "error": f"Unbekannte Aktion: {action}"
                }

            client.close()

            return {
                "success": True,
                "message": message
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Docker-Fehler: {str(e)}"
            }