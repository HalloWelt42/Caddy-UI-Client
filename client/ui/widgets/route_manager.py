"""
Route Manager Widget - Verwaltung der Caddy Routes - Vereinheitlichtes Design
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QMessageBox, QHeaderView,
    QDialog, QDialogButtonBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices, QCursor, QColor
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
        self.btn_add = QPushButton(qta.icon('fa5s.plus', color='white'), "Route hinzufügen")
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

        # Einheitliche Zeilenhöhe
        self.table.verticalHeader().setDefaultSectionSize(45)

        # Header anpassen
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 120)  # Einheitliche Breite

        # Alternating row colors
        self.table.setAlternatingRowColors(True)

        # Klick-Event für Domain-Links
        self.table.itemClicked.connect(self.on_item_clicked)
        self.table.itemEntered.connect(self.on_item_entered)
        self.table.setMouseTracking(True)  # Für Hover-Effekt

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

            # Domain als klickbarer Link mit Icon
            domain = route.get("domain", "")
            domain_item = QTableWidgetItem(domain)
            domain_item.setFlags(domain_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # Link Icon hinzufügen
            link_icon = qta.icon('fa5s.external-link-alt', color='#3498db')
            domain_item.setIcon(link_icon)

            # Link-Styling (blau und unterstrichen)
            domain_item.setForeground(QColor('#3498db'))
            font = domain_item.font()
            font.setUnderline(True)
            domain_item.setFont(font)

            # Speichere die URL als Daten
            if domain:
                # Füge https:// hinzu wenn kein Protokoll vorhanden
                if not domain.startswith(('http://', 'https://')):
                    url = f"https://{domain}"
                else:
                    url = domain
                domain_item.setData(Qt.ItemDataRole.UserRole, url)
                domain_item.setToolTip(f"Klicken um {url} zu öffnen")

            self.table.setItem(row, 0, domain_item)

            # Upstream mit Icon
            upstream = route.get("upstream", "")
            upstream_item = QTableWidgetItem(upstream)
            upstream_item.setFlags(upstream_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # Server Icon für Upstream
            server_icon = qta.icon('fa5s.server', color='#7f8c8d')
            upstream_item.setIcon(server_icon)

            self.table.setItem(row, 1, upstream_item)

            # Path mit Icon
            path = route.get("path", "/")
            path_item = QTableWidgetItem(path)
            path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # Route Icon für Path
            path_icon = qta.icon('fa5s.route', color='#7f8c8d')
            path_item.setIcon(path_icon)

            self.table.setItem(row, 2, path_item)

            # Delete Button - konsistent mit Docker Manager
            delete_btn = QPushButton(qta.icon('fa5s.trash', color='#c0392b'), "Löschen")
            delete_btn.setMaximumWidth(100)
            delete_btn.setToolTip(f"Route {domain} löschen")
            delete_btn.clicked.connect(lambda checked, d=route.get("domain"): self.confirm_delete(d))
            self.table.setCellWidget(row, 3, delete_btn)

    def on_item_entered(self, item: QTableWidgetItem):
        """Handle Hover über Tabellen-Items"""
        if item.column() == 0 and item.data(Qt.ItemDataRole.UserRole):
            self.table.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            self.table.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def on_item_clicked(self, item: QTableWidgetItem):
        """Handle Klick auf Tabellen-Items"""
        # Nur für Domain-Spalte (Spalte 0)
        if item.column() == 0:
            url = item.data(Qt.ItemDataRole.UserRole)
            if url:
                # Öffne URL im Browser
                from PySide6.QtCore import QUrl
                QDesktopServices.openUrl(QUrl(url))

    def confirm_delete(self, domain: str):
        """Löschbestätigung anzeigen"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Route löschen")
        msg_box.setText(f"Möchten Sie die Route für '{domain}' wirklich löschen?")
        msg_box.setInformativeText("Diese Aktion kann nicht rückgängig gemacht werden.")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.Cancel)

        # Button-Texte anpassen
        yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
        yes_button.setText("Löschen")
        yes_button.setIcon(qta.icon('fa5s.trash', color='#c0392b'))

        cancel_button = msg_box.button(QMessageBox.StandardButton.Cancel)
        cancel_button.setText("Abbrechen")

        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            self.remove_route.emit(domain)