"""
Route Manager Widget - Verwaltung der Caddy Routes
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QMessageBox, QHeaderView,
    QDialog, QDialogButtonBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta


class AddRouteDialog(QDialog):
    """Dialog zum Hinzufügen einer neuen Route"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neue Route hinzufügen")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Form
        form_layout = QFormLayout()

        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("z.B. example.local")
        form_layout.addRow("Domain:", self.domain_input)

        self.upstream_input = QLineEdit()
        self.upstream_input.setPlaceholderText("z.B. localhost:3000")
        form_layout.addRow("Upstream:", self.upstream_input)

        self.path_input = QLineEdit("/")
        self.path_input.setPlaceholderText("z.B. /api")
        form_layout.addRow("Pfad:", self.path_input)

        layout.addLayout(form_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def validate_and_accept(self):
        """Validierung und Dialog akzeptieren"""
        if not self.domain_input.text():
            QMessageBox.warning(self, "Fehler", "Bitte Domain eingeben")
            return

        if not self.upstream_input.text():
            QMessageBox.warning(self, "Fehler", "Bitte Upstream eingeben")
            return

        self.accept()

    def get_route_data(self):
        """Route-Daten zurückgeben"""
        return {
            "domain": self.domain_input.text(),
            "upstream": self.upstream_input.text(),
            "path": self.path_input.text() or "/"
        }


class RouteManagerWidget(QWidget):
    """Route Manager Widget"""

    # Signals
    add_route = Signal(dict)  # Route-Daten
    remove_route = Signal(str)  # Domain
    refresh_routes = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """UI aufbauen"""
        layout = QVBoxLayout(self)

        # Titel und Toolbar
        header_layout = QHBoxLayout()

        title = QLabel("Route Verwaltung")
        title.setObjectName("subtitleLabel")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Buttons
        self.btn_add = QPushButton(qta.icon('fa5s.plus'), "Route hinzufügen")
        self.btn_add.setObjectName("primaryButton")
        self.btn_add.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(self.btn_add)

        self.btn_refresh = QPushButton(qta.icon('fa5s.sync'), "Aktualisieren")
        self.btn_refresh.clicked.connect(self.refresh_routes.emit)
        header_layout.addWidget(self.btn_refresh)

        layout.addLayout(header_layout)

        # Tabelle
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Domain", "Upstream", "Pfad", "Aktionen"])

        # Header anpassen
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 100)

        # Alternating row colors
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        # Status-Zeile
        self.status_label = QLabel("Keine Routes konfiguriert")
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        layout.addWidget(self.status_label)

    def show_add_dialog(self):
        """Dialog zum Hinzufügen einer Route anzeigen"""
        dialog = AddRouteDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            route_data = dialog.get_route_data()
            self.add_route.emit(route_data)

    def update_routes(self, routes: list):
        """Route-Tabelle aktualisieren"""
        self.table.setRowCount(0)

        if not routes:
            self.status_label.setText("Keine Routes konfiguriert")
            return

        self.status_label.setText(f"{len(routes)} Route(s) konfiguriert")

        for route in routes:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Domain
            domain_item = QTableWidgetItem(route.get("domain", ""))
            domain_item.setFlags(domain_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, domain_item)

            # Upstream
            upstream_item = QTableWidgetItem(route.get("upstream", ""))
            upstream_item.setFlags(upstream_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, upstream_item)

            # Path
            path_item = QTableWidgetItem(route.get("path", "/"))
            path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, path_item)

            # Delete Button
            delete_btn = QPushButton(qta.icon('fa5s.trash', color='#c0392b'), "")
            delete_btn.setMaximumWidth(80)
            delete_btn.clicked.connect(lambda checked, d=route.get("domain"): self.confirm_delete(d))
            self.table.setCellWidget(row, 3, delete_btn)

    def confirm_delete(self, domain: str):
        """Löschbestätigung anzeigen"""
        reply = QMessageBox.question(
            self,
            "Route löschen",
            f"Möchten Sie die Route für '{domain}' wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.remove_route.emit(domain)