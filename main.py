"""
Evidentia - Digital Forensics Timeline Tool
Main entry point for the application
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from frontend.src.main_window import MainWindow


def main():
    """Initialize and run the Evidentia application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Evidentia")
    app.setOrganizationName("Evidentia Forensics")
    app.setApplicationVersion("1.0")
    
    # Create main window
    window = MainWindow()
    
    # Get available screen geometry (excludes taskbar)
    screen = app.primaryScreen().availableGeometry()
    
    # Calculate responsive window size (80% of available screen, max 1600x1000)
    window_width = min(int(screen.width() * 0.8), 1600)
    window_height = min(int(screen.height() * 0.85), 1000)
    window.resize(window_width, window_height)
    
    # Center the window on screen
    window.move(
        screen.x() + (screen.width() - window.width()) // 2,
        screen.y() + (screen.height() - window.height()) // 2
    )
    
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
