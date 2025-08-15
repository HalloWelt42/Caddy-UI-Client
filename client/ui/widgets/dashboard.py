"""
Dashboard Widget - Hauptübersicht mit Status-Anzeigen
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
import qtawesome as qta


class StatusIndicator(QFrame):
    """Status-Indikator Widget"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setMaximumHeight(100)

        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(11)
        self.title_label.setFont(font)

        # Status Icon und Text
        self.status_layout = QHBoxLayout()
        self.status_icon = QLabel()
        self.status_text = QLabel("Unbekannt")
        self.status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_layout.addWidget(self.status_icon, 0, Qt.AlignmentFlag.AlignCenter)
        self.status_layout.addWidget(self.status_text, 1)

        layout.addWidget(self.title_label)
        layout.addLayout(self.status_layout)

        self.set_status("unknown")

    def set_status(self, status: str, text: str = None):
        """Status setzen mit Icon und Farbe"""
        if status == "running":
            icon = qta.icon('fa5s.check-circle', color='#27ae60')
            self.setStyleSheet("""
                StatusIndicator {
                    background-color: #1a4d2e;
                    border: 2px solid #27ae60;
                    border-radius: 8px;
                }
                QLabel { color: #27ae60; }
            """)
            self.status_text.setText(text or "Läuft")

        elif status == "stopped":
            icon = qta.icon('fa5s.stop-circle', color='#c0392b')
            self.setStyleSheet("""
                StatusIndicator {
                    background-color: #4d1a1a;
                    border: 2px solid #c0392b;
                    border-radius: 8px;
                }
                QLabel { color: #c0392b; }
            """)
            self.status_text.setText(text or "Gestoppt")

        elif status == "not_installed":
            icon = qta.icon('fa5s.exclamation-circle', color='#95a5a6')
            self.setStyleSheet("""
                StatusIndicator {
                    background-color: #2c3e50;
                    border: 2px solid #95a5a6;
                    border-radius: 8px;
                }
                QLabel { color: #95a5a6; }
            """)
            self.status_text.setText(text or "Nicht installiert")

        elif status == "error":
            icon = qta.icon('fa5s.times-circle', color='#e67e22')
            self.setStyleSheet("""
                StatusIndicator {
                    background-color: #4d2a1a;
                    border: 2px solid #e67e22;
                    border-radius: 8px;
                }
                QLabel { color: #e67e22; }
            """)
            self.status_text.setText(text or "Fehler")

        else:
            icon = qta.icon('fa5s.question-circle', color='#7f8c8d')
            self.setStyleSheet("""
                StatusIndicator {
                    background-color: #2d2d2d;
                    border: 2px solid #7f8c8d;
                    border-radius: 8px;
                }
                QLabel { color: #7f8c8d; }
            """)
            self.status_text.setText(text or "Unbekannt")

        self.status_icon.setPixmap(icon.pixmap(24, 24))


class MetricDisplay(QGroupBox):
    """Metrik-Anzeige Widget"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setMaximumHeight(120)

        layout = QGridLayout(self)

        # Metrik-Labels
        self.value_label = QLabel("0")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.value_label.setFont(font)

        self.unit_label = QLabel("")
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.value_label, 0, 0)
        layout.addWidget(self.unit_label, 1, 0)

    def set_value(self, value: str, unit: str = ""):
        """Wert und Einheit setzen"""
        self.value_label.setText(value)
        self.unit_label.setText(unit)


class DashboardWidget(QWidget):
    """Haupt-Dashboard Widget"""

    # Signals
    start_caddy = Signal()
    stop_caddy = Signal()
    restart_caddy = Signal()
    install_caddy = Signal()
    start_docker = Signal()
    stop_docker = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """UI aufbauen"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Titel
        title = QLabel("Caddy Manager Dashboard")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Status-Bereich
        status_group = QGroupBox("System Status")
        status_layout = QHBoxLayout(status_group)

        self.caddy_status = StatusIndicator("Caddy Server")
        self.docker_status = StatusIndicator("Docker")
        self.api_status = StatusIndicator("API Server")

        status_layout.addWidget(self.caddy_status)
        status_layout.addWidget(self.docker_status)
        status_layout.addWidget(self.api_status)

        layout.addWidget(status_group)

        # Control Buttons
        control_group = QGroupBox("Steuerung")
        control_layout = QGridLayout(control_group)

        # Caddy Controls
        caddy_label = QLabel("Caddy Server:")
        caddy_label.setStyleSheet("font-weight: bold;")
        control_layout.addWidget(caddy_label, 0, 0)

        self.btn_install = QPushButton(qta.icon('fa5s.download'), "Installieren")
        self.btn_install.setObjectName("primaryButton")
        self.btn_install.clicked.connect(self.install_caddy.emit)
        control_layout.addWidget(self.btn_install, 0, 1)

        self.btn_start = QPushButton(qta.icon('fa5s.play'), "Starten")
        self.btn_start.setObjectName("successButton")
        self.btn_start.clicked.connect(self.start_caddy.emit)
        control_layout.addWidget(self.btn_start, 0, 2)

        self.btn_stop = QPushButton(qta.icon('fa5s.stop'), "Stoppen")
        self.btn_stop.setObjectName("dangerButton")
        self.btn_stop.clicked.connect(self.stop_caddy.emit)
        control_layout.addWidget(self.btn_stop, 0, 3)

        self.btn_restart = QPushButton(qta.icon('fa5s.sync'), "Neustart")
        self.btn_restart.clicked.connect(self.restart_caddy.emit)
        control_layout.addWidget(self.btn_restart, 0, 4)

        # Docker Controls
        docker_label = QLabel("Docker:")
        docker_label.setStyleSheet("font-weight: bold;")
        control_layout.addWidget(docker_label, 1, 0)

        self.btn_docker_start = QPushButton(qta.icon('fa5s.play'), "Starten")
        self.btn_docker_start.setObjectName("successButton")
        self.btn_docker_start.clicked.connect(self.start_docker.emit)
        control_layout.addWidget(self.btn_docker_start, 1, 2)

        self.btn_docker_stop = QPushButton(qta.icon('fa5s.stop'), "Stoppen")
        self.btn_docker_stop.setObjectName("dangerButton")
        self.btn_docker_stop.clicked.connect(self.stop_docker.emit)
        control_layout.addWidget(self.btn_docker_stop, 1, 3)

        layout.addWidget(control_group)

        # Metriken
        metrics_group = QGroupBox("System-Metriken")
        metrics_layout = QHBoxLayout(metrics_group)

        self.cpu_metric = MetricDisplay("CPU")
        self.ram_metric = MetricDisplay("RAM")
        self.requests_metric = MetricDisplay("Requests/Sek")
        self.response_metric = MetricDisplay("Response Time")

        metrics_layout.addWidget(self.cpu_metric)
        metrics_layout.addWidget(self.ram_metric)
        metrics_layout.addWidget(self.requests_metric)
        metrics_layout.addWidget(self.response_metric)

        layout.addWidget(metrics_group)

        # Stretch am Ende
        layout.addStretch()

    def update_caddy_status(self, status_data: dict):
        """Caddy-Status aktualisieren"""
        status = status_data.get("status", "unknown")
        self.caddy_status.set_status(status)

        # Buttons aktivieren/deaktivieren
        if status == "not_installed":
            self.btn_install.setEnabled(True)
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(False)
            self.btn_restart.setEnabled(False)
        elif status == "running":
            self.btn_install.setEnabled(False)
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.btn_restart.setEnabled(True)
        elif status == "stopped":
            self.btn_install.setEnabled(False)
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.btn_restart.setEnabled(False)

    def update_metrics(self, metrics: dict):
        """Metriken aktualisieren"""
        if "cpu" in metrics:
            cpu_percent = metrics["cpu"].get("percent", 0)
            self.cpu_metric.set_value(f"{cpu_percent:.1f}", "%")

        if "memory" in metrics:
            mem_percent = metrics["memory"].get("percent", 0)
            self.ram_metric.set_value(f"{mem_percent:.1f}", "%")

        if "requests" in metrics:
            req_per_sec = metrics["requests"].get("per_second", 0)
            self.requests_metric.set_value(f"{req_per_sec:.2f}", "req/s")

            response_time = metrics["requests"].get("avg_response_time", 0)
            self.response_metric.set_value(f"{response_time:.1f}", "ms")

        if "services" in metrics:
            # Docker Status
            docker_running = metrics["services"].get("docker", False)
            self.docker_status.set_status("running" if docker_running else "stopped")

            # API ist immer running wenn wir Metriken bekommen
            self.api_status.set_status("running")