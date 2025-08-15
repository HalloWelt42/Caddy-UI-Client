"""
Caddy Manager Client - Haupteinstiegspunkt
"""
import sys
from pathlib import Path

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from qasync import QEventLoop

from client.ui.windows.main_window import MainWindow
from client.ui.styles.dark_theme import apply_dark_theme


def main():
    """Hauptfunktion"""
    # Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Caddy Manager")
    app.setOrganizationName("CaddyManager")

    # High DPI Support
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    # Dark Theme anwenden
    apply_dark_theme(app)

    # Async Event Loop für Qt
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Hauptfenster
    window = MainWindow()
    window.show()

    # Event Loop starten
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()