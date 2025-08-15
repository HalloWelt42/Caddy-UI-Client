async def load_docker_containers(self):
    """Docker Container laden"""
    containers = await self.api_client.get_docker_containers()
    self.docker_manager.update_containers(containers)


async def start_docker_container(self, container_id: str):
    """Docker Container starten"""
    await self.api_client.control_docker_container(container_id, "start")
    await self.load_docker_containers()


async def stop_docker_container(self, container_id: str):
    """Docker Container stoppen"""
    await self.api_client.control_docker_container(container_id, "stop")
    await self.load_docker_containers()


async def restart_docker_container(self, container_id: str):
    """Docker Container neu starten"""
    await self.api_client.control_docker_container(container_id, "restart")
    await self.load_docker_containers()  # Docker Manager Signals
    self.docker_manager.refresh_containers.connect(self.load_docker_containers)
    self.docker_manager.start_container.connect(self.start_docker_container)
    self.docker_manager.stop_container.connect(self.stop_docker_container)
    self.docker_manager.restart_container.connect(self.restart_docker_container)
    """
Hauptfenster der Caddy Manager Anwendung
"""


from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QStatusBar, QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QAction
import qtawesome as qta
import asyncio
from qasync import asyncSlot

from client.ui.widgets.dashboard import DashboardWidget
from client.ui.widgets.route_manager import RouteManagerWidget
from client.ui.widgets.docker_manager import DockerManagerWidget
from client.services.api_client import APIClient


class MainWindow(QMainWindow):
    """Hauptfenster der Anwendung"""

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.setup_ui()
        self.setup_connections()
        self.setup_timers()

        # Initial Status abrufen
        QTimer.singleShot(500, self.initial_load)

    def setup_ui(self):
        """UI aufbauen"""
        self.setWindowTitle("Caddy Manager")
        self.setGeometry(100, 100, 1200, 800)

        # Zentral-Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab Widget
        self.tabs = QTabWidget()

        # Dashboard Tab
        self.dashboard = DashboardWidget()
        self.tabs.addTab(self.dashboard, qta.icon('fa5s.tachometer-alt'), "Dashboard")

        # Routes Tab
        self.route_manager = RouteManagerWidget()
        self.tabs.addTab(self.route_manager, qta.icon('fa5s.route'), "Routes")

        # Docker Tab
        self.docker_manager = DockerManagerWidget()
        self.tabs.addTab(self.docker_manager, qta.icon('fa5b.docker'), "Docker")

        layout.addWidget(self.tabs)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Verbinde mit Server...")

        # Menu Bar
        self.create_menu_bar()

    def create_menu_bar(self):
        """Menu Bar erstellen"""
        menubar = self.menuBar()

        # Datei Menu
        file_menu = menubar.addMenu("Datei")

        backup_action = QAction(qta.icon('fa5s.save'), "Backup erstellen", self)
        backup_action.triggered.connect(self.create_backup)
        file_menu.addAction(backup_action)

        restore_action = QAction(qta.icon('fa5s.upload'), "Backup wiederherstellen", self)
        restore_action.triggered.connect(self.restore_backup)
        file_menu.addAction(restore_action)

        file_menu.addSeparator()

        exit_action = QAction(qta.icon('fa5s.times'), "Beenden", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Ansicht Menu
        view_menu = menubar.addMenu("Ansicht")

        refresh_action = QAction(qta.icon('fa5s.sync'), "Aktualisieren", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_all)
        view_menu.addAction(refresh_action)

        # Hilfe Menu
        help_menu = menubar.addMenu("Hilfe")

        about_action = QAction(qta.icon('fa5s.info-circle'), "Über", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_connections(self):
        """Signal-Slot Verbindungen einrichten"""
        # API Client Signals
        self.api_client.status_updated.connect(self.dashboard.update_caddy_status)
        self.api_client.routes_updated.connect(self.route_manager.update_routes)
        self.api_client.metrics_updated.connect(self.dashboard.update_metrics)
        self.api_client.error_occurred.connect(self.show_error)
        self.api_client.operation_completed.connect(self.show_operation_result)

        # Dashboard Signals
        self.dashboard.install_caddy.connect(self.install_caddy)
        self.dashboard.start_caddy.connect(self.start_caddy)
        self.dashboard.stop_caddy.connect(self.stop_caddy)
        self.dashboard.restart_caddy.connect(self.restart_caddy)

        # Route Manager Signals
        self.route_manager.add_route.connect(self.add_route)
        self.route_manager.remove_route.connect(self.remove_route_wrapper)  # Wrapper verwenden
        self.route_manager.refresh_routes.connect(self.load_routes)

        # Docker Manager Signals
        self.docker_manager.refresh_containers.connect(self.load_docker_containers_wrapper)  # Wrapper
        self.docker_manager.start_container.connect(self.start_docker_container_wrapper)  # Wrapper
        self.docker_manager.stop_container.connect(self.stop_docker_container_wrapper)  # Wrapper
        self.docker_manager.restart_container.connect(self.restart_docker_container_wrapper)  # Wrapper

    def setup_timers(self):
        """Timer für regelmäßige Updates einrichten"""
        # Status Update Timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.safe_update_status)
        self.status_timer.start(5000)  # Alle 5 Sekunden

        # Metrics Update Timer
        self.metrics_timer = QTimer()
        self.metrics_timer.timeout.connect(self.safe_update_metrics)
        self.metrics_timer.start(2000)  # Alle 2 Sekunden

        # Flags für laufende Updates
        self.status_updating = False
        self.metrics_updating = False

    def safe_update_status(self):
        """Sicheres Status-Update ohne Überschneidungen"""
        if not self.status_updating:
            self.status_updating = True
            asyncio.create_task(self._update_status_async())

    async def _update_status_async(self):
        """Async Status Update"""
        try:
            await self.update_status()
        finally:
            self.status_updating = False

    def safe_update_metrics(self):
        """Sicheres Metriken-Update ohne Überschneidungen"""
        if not self.metrics_updating:
            self.metrics_updating = True
            asyncio.create_task(self._update_metrics_async())

    async def _update_metrics_async(self):
        """Async Metrics Update"""
        try:
            await self.update_metrics()
        finally:
            self.metrics_updating = False

    # ============= Async Slots =============

    @asyncSlot()
    async def initial_load(self):
        """Initiale Daten laden"""
        # Verbindung prüfen
        connected = await self.api_client.check_connection()
        if connected:
            self.status_bar.showMessage("Verbunden mit Server", 3000)
            await self.update_status()
            await self.load_routes()
            await self.update_metrics()
            await self.load_docker_containers()  # Docker Container laden
        else:
            self.status_bar.showMessage("Server nicht erreichbar")
            self.show_error("Konnte keine Verbindung zum Server herstellen")

    @asyncSlot()
    async def update_status(self):
        """Caddy Status aktualisieren"""
        await self.api_client.get_caddy_status()

    @asyncSlot()
    async def update_metrics(self):
        """Metriken aktualisieren"""
        await self.api_client.get_metrics()

    @asyncSlot()
    async def load_routes(self):
        """Routes laden"""
        await self.api_client.get_routes()

    @asyncSlot()
    async def install_caddy(self):
        """Caddy installieren"""
        # Timer temporär stoppen um Konflikte zu vermeiden
        self.status_timer.stop()
        self.metrics_timer.stop()

        progress = QProgressDialog("Caddy wird installiert...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setWindowTitle("Installation")
        progress.show()

        try:
            # Verwende normale HTTP-Installation statt WebSocket
            result = await self.api_client.install_caddy()
            progress.close()

            if result.get("success"):
                QMessageBox.information(self, "Erfolg", result.get("message", "Caddy erfolgreich installiert"))
            else:
                QMessageBox.critical(self, "Fehler", result.get("error", "Installation fehlgeschlagen"))

        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Fehler", f"Installationsfehler: {str(e)}")
        finally:
            await self.update_status()
            # Timer wieder starten
            self.status_timer.start(5000)
            self.metrics_timer.start(2000)

    @asyncSlot()
    async def start_caddy(self):
        """Caddy starten"""
        # Timer temporär stoppen
        self.status_timer.stop()
        self.metrics_timer.stop()

        self.status_bar.showMessage("Starte Caddy...")
        try:
            await self.api_client.start_caddy()
        finally:
            # Timer wieder starten
            self.status_timer.start(5000)
            self.metrics_timer.start(2000)

    @asyncSlot()
    async def stop_caddy(self):
        """Caddy stoppen"""
        # Timer temporär stoppen
        self.status_timer.stop()
        self.metrics_timer.stop()

        self.status_bar.showMessage("Stoppe Caddy...")
        try:
            await self.api_client.stop_caddy()
        finally:
            # Timer wieder starten
            self.status_timer.start(5000)
            self.metrics_timer.start(2000)

    @asyncSlot()
    async def restart_caddy(self):
        """Caddy neu starten"""
        # Timer temporär stoppen
        self.status_timer.stop()
        self.metrics_timer.stop()

        self.status_bar.showMessage("Starte Caddy neu...")
        try:
            await self.api_client.restart_caddy()
        finally:
            # Timer wieder starten
            self.status_timer.start(5000)
            self.metrics_timer.start(2000)

    @asyncSlot()
    async def add_route(self, route_data: dict):
        """Route hinzufügen"""
        self.status_bar.showMessage("Füge Route hinzu...")
        await self.api_client.add_route(
            route_data["domain"],
            route_data["upstream"],
            route_data["path"]
        )

    # ============= Docker Management (ohne asyncSlot) =============

    def remove_route_wrapper(self, domain: str):
        """Wrapper für async remove_route"""
        asyncio.create_task(self.remove_route(domain))

    async def remove_route(self, domain: str):
        """Route entfernen"""
        self.status_bar.showMessage(f"Entferne Route {domain}...")
        await self.api_client.remove_route(domain)

    def load_docker_containers_wrapper(self):
        """Wrapper für async load_docker_containers"""
        asyncio.create_task(self.load_docker_containers())

    async def load_docker_containers(self):
        """Docker Container laden"""
        containers = await self.api_client.get_docker_containers()
        self.docker_manager.update_containers(containers)

    def start_docker_container_wrapper(self, container_id: str):
        """Wrapper für async start_docker_container"""
        asyncio.create_task(self.start_docker_container(container_id))

    async def start_docker_container(self, container_id: str):
        """Docker Container starten"""
        await self.api_client.control_docker_container(container_id, "start")
        await self.load_docker_containers()

    def stop_docker_container_wrapper(self, container_id: str):
        """Wrapper für async stop_docker_container"""
        asyncio.create_task(self.stop_docker_container(container_id))

    async def stop_docker_container(self, container_id: str):
        """Docker Container stoppen"""
        await self.api_client.control_docker_container(container_id, "stop")
        await self.load_docker_containers()

    def restart_docker_container_wrapper(self, container_id: str):
        """Wrapper für async restart_docker_container"""
        asyncio.create_task(self.restart_docker_container(container_id))

    async def restart_docker_container(self, container_id: str):
        """Docker Container neu starten"""
        await self.api_client.control_docker_container(container_id, "restart")
        await self.load_docker_containers()

    @asyncSlot()
    async def create_backup(self):
        """Backup erstellen"""
        from PySide6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(
            self, "Backup erstellen",
            "Backup-Name (optional):"
        )

        if ok:
            self.status_bar.showMessage("Erstelle Backup...")
            await self.api_client.backup_config(name if name else None)

    @asyncSlot()
    async def restore_backup(self):
        """Backup wiederherstellen"""
        from PySide6.QtWidgets import QInputDialog

        # Backups laden
        backups = await self.api_client.get_backups()
        if not backups:
            QMessageBox.information(self, "Info", "Keine Backups vorhanden")
            return

        backup_names = [b["name"] for b in backups]
        name, ok = QInputDialog.getItem(
            self, "Backup wiederherstellen",
            "Backup auswählen:", backup_names, 0, False
        )

        if ok and name:
            reply = QMessageBox.question(
                self, "Bestätigung",
                f"Möchten Sie das Backup '{name}' wirklich wiederherstellen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.status_bar.showMessage("Stelle Backup wieder her...")
                await self.api_client.restore_config(name)
                await self.load_routes()

    @asyncSlot()
    async def refresh_all(self):
        """Alle Daten aktualisieren"""
        self.status_bar.showMessage("Aktualisiere...")
        await self.update_status()
        await self.load_routes()
        await self.update_metrics()
        self.status_bar.showMessage("Aktualisiert", 2000)

    # ============= UI Helpers =============

    @Slot(dict)
    def show_operation_result(self, result: dict):
        """Operation-Ergebnis anzeigen"""
        if result.get("success"):
            self.status_bar.showMessage(
                result.get("message", "Operation erfolgreich"), 3000
            )
        else:
            self.show_error(result.get("error", "Operation fehlgeschlagen"))

    @Slot(str)
    def show_error(self, message: str):
        """Fehlermeldung anzeigen"""
        self.status_bar.showMessage(f"Fehler: {message}", 5000)
        QMessageBox.critical(self, "Fehler", message)

    def show_about(self):
        """Über-Dialog anzeigen"""
        QMessageBox.about(
            self,
            "Über Caddy Manager",
            "Caddy Manager v1.0.0\n\n"
            "Eine moderne GUI zur Verwaltung von Caddy Server.\n\n"
            "Entwickelt mit Python, Qt6 und FastAPI."
        )

    def closeEvent(self, event):
        """Beim Schließen aufräumen"""
        # Timer stoppen
        self.status_timer.stop()
        self.metrics_timer.stop()

        # API Client schließen
        asyncio.create_task(self.api_client.close())

        event.accept()