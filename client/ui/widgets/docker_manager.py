"""
Docker Container Manager Widget
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox
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

        # Zeilenhöhe vergrößern für bessere Button-Sichtbarkeit
        self.table.verticalHeader().setDefaultSectionSize(60)  # 3x größer (default ~20)

        # Header anpassen
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 250)  # Mehr Platz für Buttons

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

            # Status-Farbe
            if status == "running":
                status_item.setForeground(Qt.GlobalColor.green)
            elif status == "exited":
                status_item.setForeground(Qt.GlobalColor.red)
            else:
                status_item.setForeground(Qt.GlobalColor.yellow)

            self.table.setItem(row, 2, status_item)

            # Ports
            ports = container.get("ports", {})
            ports_text = ", ".join([f"{k}:{v}" for k, v in ports.items()]) if ports else "-"
            ports_item = QTableWidgetItem(ports_text)
            ports_item.setFlags(ports_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, ports_item)

            # Container ID (versteckt)
            id_item = QTableWidgetItem(container.get("id", ""))
            self.table.setItem(row, 4, id_item)

            # Action Buttons
            button_layout = QHBoxLayout()
            button_widget = QWidget()

            container_id = container.get("id", "")

            if status == "running":
                stop_btn = QPushButton(qta.icon('fa5s.stop', color='#c0392b'), "Stop")
                stop_btn.clicked.connect(lambda checked, cid=container_id: self.stop_container.emit(cid))
                button_layout.addWidget(stop_btn)

                restart_btn = QPushButton(qta.icon('fa5s.sync'), "Restart")
                restart_btn.clicked.connect(lambda checked, cid=container_id: self.restart_container.emit(cid))
                button_layout.addWidget(restart_btn)
            else:
                start_btn = QPushButton(qta.icon('fa5s.play', color='#27ae60'), "Start")
                start_btn.clicked.connect(lambda checked, cid=container_id: self.start_container.emit(cid))
                button_layout.addWidget(start_btn)

            button_widget.setLayout(button_layout)
            self.table.setCellWidget(row, 5, button_widget)