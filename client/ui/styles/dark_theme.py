"""
Dark Theme für Qt6 Application
"""

DARK_THEME_STYLE = """
/* ============= Global Styles ============= */
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* ============= Main Window ============= */
QMainWindow {
    background-color: #1e1e1e;
}

/* ============= Buttons ============= */
QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #3d3d3d;
    border-color: #4d4d4d;
}

QPushButton:pressed {
    background-color: #252525;
    border-color: #3d3d3d;
}

QPushButton:disabled {
    background-color: #2a2a2a;
    color: #666666;
    border-color: #2d2d2d;
}

/* Primary Button */
QPushButton#primaryButton {
    background-color: #0d7377;
    color: white;
    border: none;
}

QPushButton#primaryButton:hover {
    background-color: #14a085;
}

QPushButton#primaryButton:pressed {
    background-color: #0a5d61;
}

/* Success Button */
QPushButton#successButton {
    background-color: #27ae60;
    color: white;
    border: none;
}

QPushButton#successButton:hover {
    background-color: #2ecc71;
}

/* Danger Button */
QPushButton#dangerButton {
    background-color: #c0392b;
    color: white;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #e74c3c;
}

/* ============= Labels ============= */
QLabel {
    color: #e0e0e0;
    background-color: transparent;
}

QLabel#titleLabel {
    font-size: 24px;
    font-weight: 600;
    color: #ffffff;
    padding: 10px 0;
}

QLabel#subtitleLabel {
    font-size: 16px;
    font-weight: 500;
    color: #b0b0b0;
}

QLabel#statusLabel {
    font-size: 14px;
    padding: 5px 10px;
    border-radius: 4px;
}

/* ============= Line Edits ============= */
QLineEdit {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: #0d7377;
}

QLineEdit:focus {
    border-color: #0d7377;
    outline: none;
}

QLineEdit:disabled {
    background-color: #252525;
    color: #666666;
}

/* ============= Text Edit ============= */
QTextEdit, QPlainTextEdit {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #0d7377;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #0d7377;
}

/* ============= ComboBox ============= */
QComboBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 150px;
}

QComboBox:hover {
    border-color: #4d4d4d;
}

QComboBox:focus {
    border-color: #0d7377;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #e0e0e0;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    selection-background-color: #0d7377;
}

/* ============= Tables ============= */
QTableWidget, QTableView {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    gridline-color: #3d3d3d;
    selection-background-color: #0d7377;
    border-radius: 6px;
}

QTableWidget::item, QTableView::item {
    padding: 8px;
    border: none;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #0d7377;
    color: white;
}

QHeaderView::section {
    background-color: #252525;
    color: #e0e0e0;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #3d3d3d;
    font-weight: 600;
}

/* ============= List Widget ============= */
QListWidget {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    outline: none;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #3d3d3d;
}

QListWidget::item:hover {
    background-color: #3d3d3d;
}

QListWidget::item:selected {
    background-color: #0d7377;
    color: white;
}

/* ============= Group Box ============= */
QGroupBox {
    background-color: #252525;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 10px;
    color: #b0b0b0;
}

/* ============= Tab Widget ============= */
QTabWidget::pane {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #252525;
    color: #b0b0b0;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border-bottom: 2px solid #0d7377;
}

QTabBar::tab:hover {
    background-color: #3d3d3d;
}

/* ============= Progress Bar ============= */
QProgressBar {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    text-align: center;
    color: #e0e0e0;
    height: 25px;
}

QProgressBar::chunk {
    background-color: #0d7377;
    border-radius: 5px;
}

/* ============= Scroll Bars ============= */
QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #4d4d4d;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5d5d5d;
}

QScrollBar:horizontal {
    background-color: #2d2d2d;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #4d4d4d;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #5d5d5d;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
}

/* ============= Menu Bar ============= */
QMenuBar {
    background-color: #252525;
    color: #e0e0e0;
    border-bottom: 1px solid #3d3d3d;
}

QMenuBar::item {
    padding: 8px 12px;
}

QMenuBar::item:selected {
    background-color: #3d3d3d;
}

QMenu {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
}

QMenu::item {
    padding: 8px 20px;
}

QMenu::item:selected {
    background-color: #0d7377;
    color: white;
}

/* ============= Status Bar ============= */
QStatusBar {
    background-color: #252525;
    color: #b0b0b0;
    border-top: 1px solid #3d3d3d;
}

/* ============= Tool Bar ============= */
QToolBar {
    background-color: #252525;
    border: none;
    spacing: 5px;
    padding: 5px;
}

QToolButton {
    background-color: transparent;
    color: #e0e0e0;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 5px;
}

QToolButton:hover {
    background-color: #3d3d3d;
    border-color: #4d4d4d;
}

QToolButton:pressed {
    background-color: #252525;
}

/* ============= Splitter ============= */
QSplitter::handle {
    background-color: #3d3d3d;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* ============= CheckBox ============= */
QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #3d3d3d;
    border-radius: 4px;
    background-color: #2d2d2d;
}

QCheckBox::indicator:checked {
    background-color: #0d7377;
    border-color: #0d7377;
}

QCheckBox::indicator:hover {
    border-color: #4d4d4d;
}

/* ============= Radio Button ============= */
QRadioButton {
    color: #e0e0e0;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #3d3d3d;
    border-radius: 9px;
    background-color: #2d2d2d;
}

QRadioButton::indicator:checked {
    background-color: #0d7377;
    border-color: #0d7377;
}

/* ============= Spin Box ============= */
QSpinBox, QDoubleSpinBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 5px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #0d7377;
}

/* ============= Custom Status Indicators ============= */
.status-running {
    background-color: #27ae60;
    color: white;
}

.status-stopped {
    background-color: #c0392b;
    color: white;
}

.status-not-installed {
    background-color: #95a5a6;
    color: white;
}

.status-error {
    background-color: #e67e22;
    color: white;
}
"""

def apply_dark_theme(app):
    """Wendet das Dark Theme auf die Anwendung an"""
    app.setStyleSheet(DARK_THEME_STYLE)