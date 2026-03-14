"""
Evidentia - Digital Forensics Timeline Tool
Main entry point for the application
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.ui.main_window import MainWindow


def main():
    """Initialize and run the Evidentia application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Evidentia")
    app.setOrganizationName("Evidentia Forensics")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Center the window on screen
    screen = app.primaryScreen().geometry()
    window.move(
        (screen.width() - window.width()) // 2,
        (screen.height() - window.height()) // 2
    )
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
