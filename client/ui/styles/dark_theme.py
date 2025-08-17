"""
Dark Theme für Caddy Manager - Mit verbesserten Button-States
"""
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt


def apply_dark_theme(app):
    """Dark Theme auf die Anwendung anwenden"""

    # Dark Palette
    dark_palette = QPalette()

    # Window colors
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)

    # Base colors (für Eingabefelder, etc.)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(60, 60, 60))

    # Text colors
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)

    # Button colors
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)

    # Highlight colors
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

    # Disabled colors
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))

    app.setPalette(dark_palette)

    # Stylesheet für spezifische Widgets
    app.setStyleSheet("""
    /* ==================== ALLGEMEINE STYLES ==================== */
    
    QWidget {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-size: 13px;
    }
    
    /* ==================== STANDARD BUTTONS ==================== */
    
    QPushButton {
        background-color: #3a3a3a;
        border: 1px solid #555;
        color: #ffffff;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
        min-height: 20px;
        transition: all 0.3s ease;
    }
    
    QPushButton:hover:!disabled {
        background-color: #4a4a4a;
        border: 1px solid #666;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    QPushButton:pressed:!disabled {
        background-color: #2a2a2a;
        border: 1px solid #444;
        transform: translateY(0px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    QPushButton:disabled {
        background-color: #252525;
        border: 1px solid #333;
        color: #666;
        opacity: 0.6;
    }
    
    QPushButton:focus {
        outline: none;
        border: 2px solid #4a9eff;
    }
    
    /* ==================== PRIMARY BUTTON (Wichtige Aktionen) ==================== */
    
    QPushButton#primaryButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #4a9eff, stop: 1 #2a7dd7);
        border: 1px solid #2a7dd7;
        color: white;
        font-weight: 600;
    }
    
    QPushButton#primaryButton:hover:!disabled {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #5aa5ff, stop: 1 #3a8de7);
        border: 1px solid #3a8de7;
        box-shadow: 0 4px 12px rgba(74, 158, 255, 0.4);
    }
    
    QPushButton#primaryButton:pressed:!disabled {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #2a7dd7, stop: 1 #1a6dc7);
    }
    
    QPushButton#primaryButton:disabled {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #2a4a6a, stop: 1 #1a3a5a);
        border: 1px solid #1a3a5a;
        color: #7a8a9a;
    }
    
    /* ==================== SUCCESS BUTTON (Start, Bestätigen) ==================== */
    
    QPushButton#successButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #27ae60, stop: 1 #229a50);
        border: 1px solid #229a50;
        color: white;
        font-weight: 600;
    }
    
    QPushButton#successButton:hover:!disabled {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #2ecc71, stop: 1 #27ae60);
        border: 1px solid #27ae60;
        box-shadow: 0 4px 12px rgba(39, 174, 96, 0.4);
    }
    
    QPushButton#successButton:pressed:!disabled {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #229a50, stop: 1 #1a7a40);
    }
    
    QPushButton#successButton:disabled {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #1a5a30, stop: 1 #0a4a20);
        border: 1px solid #0a4a20;
        color: #5a8a6a;
    }
    
    /* ==================== DANGER BUTTON (Stop, Löschen) ==================== */
    
    QPushButton#dangerButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #e74c3c, stop: 1 #c0392b);
        border: 1px solid #c0392b;
        color: white;
        font-weight: 600;
    }
    
    QPushButton#dangerButton:hover:!disabled {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #ec7063, stop: 1 #e74c3c);
        border: 1px solid #e74c3c;
        box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
    }
    
    QPushButton#dangerButton:pressed:!disabled {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #c0392b, stop: 1 #a02a1b);
    }
    
    QPushButton#dangerButton:disabled {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #6a2a2a, stop: 1 #5a1a1a);
        border: 1px solid #5a1a1a;
        color: #9a6a6a;
    }
    
    /* ==================== ICON BUTTONS (Nur Icons) ==================== */
    
    QPushButton[text=""] {
        padding: 6px;
        min-width: 30px;
        max-width: 40px;
    }
    
    QPushButton[text=""]:hover:!disabled {
        background-color: #4a4a4a;
    }
    
    /* ==================== TABLE WIDGET BUTTONS ==================== */
    
    QTableWidget QPushButton {
        background-color: #3a3a3a;
        border: 1px solid #4a4a4a;
        padding: 6px 12px;
        margin: 2px;
        border-radius: 4px;
    }
    
    QTableWidget QPushButton:hover:!disabled {
        background-color: #4a4a4a;
        border: 1px solid #5a5a5a;
        transform: none;  /* Kein translateY in Tabellen */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    QTableWidget QPushButton:pressed:!disabled {
        background-color: #2a2a2a;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    QTableWidget QPushButton:disabled {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        color: #4a4a4a;
        opacity: 0.5;
    }
    
    /* ==================== MENU BAR ==================== */
    
    QMenuBar {
        background-color: #2d2d2d;
        border-bottom: 1px solid #555;
    }
    
    QMenuBar::item {
        padding: 5px 10px;
        background: transparent;
    }
    
    QMenuBar::item:selected {
        background-color: #3a3a3a;
        border-radius: 4px;
    }
    
    QMenuBar::item:pressed {
        background-color: #4a4a4a;
    }
    
    QMenu {
        background-color: #2d2d2d;
        border: 1px solid #555;
        border-radius: 6px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 8px 25px;
        border-radius: 4px;
    }
    
    QMenu::item:selected {
        background-color: #3a3a3a;
    }
    
    /* ==================== TAB WIDGET ==================== */
    
    QTabWidget::pane {
        border: 1px solid #555;
        background-color: #2d2d2d;
    }
    
    QTabBar::tab {
        background-color: #2d2d2d;
        color: #aaa;
        padding: 10px 15px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        transition: all 0.3s ease;
    }
    
    QTabBar::tab:selected {
        background-color: #3a3a3a;
        color: white;
        border-bottom: 2px solid #4a9eff;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #353535;
        color: #ddd;
    }
    
    QTabBar::tab:disabled {
        color: #666;
        background-color: #252525;
    }
    
    /* ==================== TABLE WIDGET ==================== */
    
    QTableWidget {
        background-color: #2d2d2d;
        alternate-background-color: #353535;
        gridline-color: #555;
        border: 1px solid #555;
        border-radius: 6px;
    }
    
    QTableWidget::item {
        padding: 5px;
        border: none;
    }
    
    QTableWidget::item:selected {
        background-color: #3a3a3a;
    }
    
    QTableWidget::item:hover {
        background-color: #404040;
    }
    
    QHeaderView::section {
        background-color: #252525;
        color: white;
        padding: 8px;
        border: 1px solid #555;
        font-weight: 600;
    }
    
    QHeaderView::section:hover {
        background-color: #303030;
    }
    
    /* ==================== SCROLLBAR ==================== */
    
    QScrollBar:vertical {
        background: #2d2d2d;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background: #555;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: #666;
    }
    
    QScrollBar::handle:vertical:pressed {
        background: #777;
    }
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    /* ==================== INPUT FIELDS ==================== */
    
    QLineEdit {
        background-color: #3a3a3a;
        border: 1px solid #555;
        padding: 8px;
        border-radius: 4px;
        color: white;
        selection-background-color: #4a9eff;
    }
    
    QLineEdit:focus {
        border: 2px solid #4a9eff;
        background-color: #404040;
    }
    
    QLineEdit:hover {
        background-color: #404040;
        border: 1px solid #666;
    }
    
    QLineEdit:disabled {
        background-color: #2a2a2a;
        color: #666;
        border: 1px solid #444;
    }
    
    /* ==================== STATUS BAR ==================== */
    
    QStatusBar {
        background-color: #252525;
        border-top: 1px solid #555;
        color: #aaa;
        font-size: 12px;
    }
    
    /* ==================== GROUP BOX ==================== */
    
    QGroupBox {
        border: 2px solid #555;
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
        color: #4a9eff;
    }
    
    /* ==================== LABELS ==================== */
    
    QLabel#titleLabel {
        font-size: 24px;
        font-weight: bold;
        color: #4a9eff;
        padding: 10px;
    }
    
    QLabel#subtitleLabel {
        font-size: 18px;
        font-weight: 600;
        color: #ddd;
        padding: 5px;
    }
    
    /* ==================== DIALOG BUTTONS ==================== */
    
    QDialogButtonBox QPushButton {
        min-width: 80px;
    }
    
    /* ==================== PROGRESS DIALOG ==================== */
    
    QProgressDialog {
        background-color: #2d2d2d;
    }
    
    QProgressBar {
        background-color: #3a3a3a;
        border: 1px solid #555;
        border-radius: 4px;
        text-align: center;
        color: white;
    }
    
    QProgressBar::chunk {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                    stop: 0 #4a9eff, stop: 1 #2a7dd7);
        border-radius: 3px;
    }
    
    /* ==================== MESSAGE BOX ==================== */
    
    QMessageBox {
        background-color: #2d2d2d;
    }
    
    QMessageBox QPushButton {
        min-width: 70px;
        min-height: 25px;
    }
    
    /* ==================== TOOLTIPS ==================== */
    
    QToolTip {
        background-color: #3a3a3a;
        color: white;
        border: 1px solid #666;
        padding: 5px;
        border-radius: 4px;
        opacity: 200;
    }
    
    /* ==================== COMBO BOX ==================== */
    
    QComboBox {
        background-color: #3a3a3a;
        border: 1px solid #555;
        padding: 6px;
        border-radius: 4px;
        color: white;
        min-width: 100px;
    }
    
    QComboBox:hover {
        background-color: #404040;
        border: 1px solid #666;
    }
    
    QComboBox:focus {
        border: 2px solid #4a9eff;
    }
    
    QComboBox:disabled {
        background-color: #2a2a2a;
        color: #666;
        border: 1px solid #444;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid #aaa;
        margin-right: 5px;
    }
    
    QComboBox::down-arrow:hover {
        border-top: 6px solid white;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        border: 1px solid #555;
        selection-background-color: #3a3a3a;
        color: white;
    }
    """)