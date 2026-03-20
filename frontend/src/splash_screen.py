"""
Splash Screen Module
Initial loading screen with Evidentia branding
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap, QPalette, QBrush
import os


class SplashScreen(QWidget):
    """Splash screen with loading animation."""
    
    finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # Don't set fixed size, let it be flexible within the main window
        self._setup_ui()
        self._apply_styles()
        self._start_loading()
    
    def _setup_ui(self):
        """Setup the splash screen UI."""
        # Main layout that centers everything
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Create a container widget to hold the splash content
        container = QWidget()
        container.setFixedSize(500, 350)
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(18, 42, 58, 0.95);
                border: 1px solid #1a4a5a;
                border-radius: 12px;
            }
        """)
        
        # Layout for the container
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Logo/Title
        title = QLabel("Evidentia")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 42, QFont.Bold))
        title.setStyleSheet("color: #00d4aa; background: transparent; border: none;")
        layout.addWidget(title)
        
        # Tagline
        tagline = QLabel("Digital Forensics Made Simple")
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setFont(QFont("Arial", 16))
        tagline.setStyleSheet("color: #8899aa; background: transparent; border: none;")
        layout.addWidget(tagline)
        
        # Loading bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(25)
        layout.addWidget(self.progress_bar)
        
        # Loading text
        self.loading_label = QLabel("Initializing...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setFont(QFont("Arial", 14))
        self.loading_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(self.loading_label)
        
        # Add the container to the main layout
        main_layout.addWidget(container)
    
    def _apply_styles(self):
        """Apply splash screen styles with background image."""
        # Set background image on the main widget (outside the container)
        bg_path = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "bg_photo_3.png")
        if os.path.exists(bg_path):
            # Apply background to the main widget only
            self.setStyleSheet(f"""
                SplashScreen {{
                    background-image: url({bg_path.replace(os.sep, '/')});
                    background-position: center;
                    background-repeat: no-repeat;
                    background-color: #0a1929;
                }}
                QProgressBar {{
                    border: 2px solid #1a4a5a;
                    border-radius: 8px;
                    text-align: center;
                    background-color: #0d2137;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 12px;
                }}
                QProgressBar::chunk {{
                    background-color: #40e0d0;
                    border-radius: 6px;
                }}
            """)
        else:
            self.setStyleSheet("""
                SplashScreen {
                    background-color: #0a1929;
                }
                QProgressBar {
                    border: 2px solid #1a4a5a;
                    border-radius: 8px;
                    text-align: center;
                    background-color: #0d2137;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 12px;
                }
                QProgressBar::chunk {
                    background-color: #40e0d0;
                    border-radius: 6px;
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