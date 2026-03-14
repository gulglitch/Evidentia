"""
Splash Screen Module
Initial loading screen with Evidentia branding
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap


class SplashScreen(QWidget):
    """Splash screen with loading animation."""
    
    finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(600, 400)
        self._setup_ui()
        self._apply_styles()
        self._start_loading()
    
    def _setup_ui(self):
        """Setup the splash screen UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Logo/Title
        title = QLabel("Evidentia")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Bold))
        layout.addWidget(title)
        
        # Tagline
        tagline = QLabel("Digital Forensics Made Simple")
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setFont(QFont("Arial", 14))
        layout.addWidget(tagline)
        
        # Version
        version = QLabel("v1.0 - Iteration 1")
        version.setAlignment(Qt.AlignCenter)
        version.setFont(QFont("Arial", 10))
        layout.addWidget(version)
        
        # Loading bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Loading text
        self.loading_label = QLabel("Initializing...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.loading_label)
    
    def _apply_styles(self):
        """Apply splash screen styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QLabel {
                color: #00d4aa;
            }
            QProgressBar {
                border: 2px solid #1a4a5a;
                border-radius: 5px;
                text-align: center;
                background-color: #0d2137;
            }
            QProgressBar::chunk {
                background-color: #40e0d0;
                border-radius: 3px;
            }
        """)
    
    def _start_loading(self):
        """Start the loading animation."""
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(50)  # Update every 50ms
        self.progress = 0
    
    def _update_progress(self):
        """Update loading progress."""
        self.progress += 2
        self.progress_bar.setValue(self.progress)
        
        # Update loading text
        if self.progress < 30:
            self.loading_label.setText("Loading database...")
        elif self.progress < 60:
            self.loading_label.setText("Initializing components...")
        elif self.progress < 90:
            self.loading_label.setText("Setting up interface...")
        else:
            self.loading_label.setText("Ready!")
        
        if self.progress >= 100:
            self.timer.stop()
            QTimer.singleShot(500, self._finish)  # Wait 500ms then finish
    
    def _finish(self):
        """Finish splash screen and emit signal."""
        self.finished.emit()
        self.close()