"""
Docker Container Manager Widget - Vereinheitlichtes Design (mit funktionierendem Dropdown)
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QMenu, QToolButton
)
from PySide6.QtCore import Qt, Signal, QTimer
import qtawesome as qta


class DockerManagerWidget(QWidget):
    """Docker Container Manager Widget"""

    # Signals
    start_container = Signal(str)  # Container ID
    stop_container = Signal(str)  # Container ID
    restart_container = Signal(str)  # Container ID
    refresh_containers = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """UI aufbauen"""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Docker Container Verwaltung")
        title.setObjectName("subtitleLabel")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Refresh Button
        self.btn_refresh = QPushButton(qta.icon('fa5s.sync'), "Aktualisieren")
        self.btn_refresh.clicked.connect(self.refresh_containers.emit)
        header_layout.addWidget(self.btn_refresh)

        layout.addLayout(header_layout)

        # Container Tabelle
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Image", "Status", "Ports", "ID", "Aktionen"
        ])

        # Einheitliche Zeilenhöhe wie bei Routes
        self.table.verticalHeader().setDefaultSectionSize(45)

        # Header anpassen
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 120)  # Gleiche Breite wie Route Manager

        # ID-Spalte verstecken (nur für interne Verwendung)
        self.table.setColumnHidden(4, True)

        # Alternating row colors
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        # Status
        self.status_label = QLabel("Keine Container gefunden")
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        layout.addWidget(self.status_label)

        # Auto-Refresh Timer
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.refresh_containers.emit)
        self.auto_refresh_timer.start(10000)  # Alle 10 Sekunden

    def update_containers(self, containers: list):
        """Container-Tabelle aktualisieren"""
        self.table.setRowCount(0)

        if not containers:
            self.status_label.setText("Keine Container gefunden")
            return

        self.status_label.setText(f"{len(containers)} Container gefunden")

        for container in containers:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Name
            name_item = QTableWidgetItem(container.get("name", ""))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, name_item)

            # Image
            image_item = QTableWidgetItem(container.get("image", ""))
            image_item.setFlags(image_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, image_item)

            # Status
            status = container.get("status", "unknown")
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # Status-Farbe mit Icons
            if status == "running":
                status_icon = qta.icon('fa5s.circle', color='#27ae60')
                status_item.setIcon(status_icon)
                status_item.setText(" Running")
                status_item.setForeground(Qt.GlobalColor.green)
            elif status == "exited":
                status_icon = qta.icon('fa5s.circle', color='#c0392b')
                status_item.setIcon(status_icon)
                status_item.setText(" Stopped")
                status_item.setForeground(Qt.GlobalColor.red)
            else:
                status_icon = qta.icon('fa5s.circle', color='#f39c12')
                status_item.setIcon(status_icon)
                status_item.setText(f" {status.capitalize()}")
                status_item.setForeground(Qt.GlobalColor.yellow)

            self.table.setItem(row, 2, status_item)

            # Ports
            ports = container.get("ports", {})
            ports_text = ", ".join([f"{k}→{v}" for k, v in ports.items()]) if ports else "-"
            ports_item = QTableWidgetItem(ports_text)
            ports_item.setFlags(ports_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, ports_item)

            # Container ID (versteckt)
            id_item = QTableWidgetItem(container.get("id", ""))
            self.table.setItem(row, 4, id_item)

            # Action Button - Dropdown-Menü (jetzt QToolButton!)
            container_id = container.get("id", "")
            container_name = container.get("name", "")

            action_btn = QToolButton()
            action_btn.setText("Aktionen")
            action_btn.setIcon(qta.icon('fa5s.ellipsis-h'))
            action_btn.setPopupMode(QToolButton.InstantPopup)
            action_btn.setMaximumWidth(100)

            # Menü erstellen
            menu = QMenu(action_btn)

            if status == "running":
                stop_action = menu.addAction(
                    qta.icon('fa5s.stop', color='#c0392b'),
                    "Stop"
                )
                stop_action.triggered.connect(
                    lambda checked=False, cid=container_id: self.stop_container.emit(cid)
                )

                restart_action = menu.addAction(
                    qta.icon('fa5s.sync', color='#f39c12'),
                    "Restart"
                )
                restart_action.triggered.connect(
                    lambda checked=False, cid=container_id: self.restart_container.emit(cid)
                )
            else:
                start_action = menu.addAction(
                    qta.icon('fa5s.play', color='#27ae60'),
                    "Start"
                )
                start_action.triggered.connect(
                    lambda checked=False, cid=container_id: self.start_container.emit(cid)
                )

            # Separator und Info
            menu.addSeparator()
            info_action = menu.addAction(
                qta.icon('fa5s.info-circle'),
                f"ID: {container_id[:12]}"
            )
            info_action.setEnabled(False)

            action_btn.setMenu(menu)
            self.table.setCellWidget(row, 5, action_btn)
