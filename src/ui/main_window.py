"""
Main Window Module
Primary application window controller for Evidentia
Manages screen flow according to development plan
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QMenuBar, QStatusBar, QLabel,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from .splash_screen import SplashScreen
from .login_screen import LoginScreen
from .dashboard import Dashboard
from .evidence_management import EvidenceManagement
from .new_case_dialog import NewCaseDialog
from ..core.database import Database


class MainWindow(QMainWindow):
    """Main application window controller."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Evidentia - Digital Forensics Timeline Tool")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Initialize core components
        self.database = Database()
        self.current_case_id = None
        self.current_user = None
        
        # Setup UI
        self._setup_ui()
        self._apply_styles()
        
        # Start with splash screen
        self._show_splash()
    
    def _setup_ui(self):
        """Setup the main UI structure."""
        # Central widget with stacked layout for different screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create screens
        self.splash_screen = SplashScreen()
        self.login_screen = LoginScreen()
        self.dashboard = Dashboard()
        self.evidence_management = None  # Created when needed
        
        # Add screens to stack
        self.stacked_widget.addWidget(self.splash_screen)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.dashboard)
        
        # Connect signals
        self.splash_screen.finished.connect(self._show_login)
        self.login_screen.login_successful.connect(self._handle_login)
        self.dashboard.new_case_requested.connect(self._show_new_case_dialog)
        
        # Setup header bar
        self._setup_header()
        
        # Setup status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Welcome to Evidentia")
    
    def _setup_header(self):
        """Setup the global header bar."""
        # Create header widget
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Evidentia logo/title
        title_label = QLabel("Evidentia")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: #00d4aa;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Logout button (hidden initially)
        self.logout_button = QPushButton("Logout")
        self.logout_button.setVisible(False)
        self.logout_button.clicked.connect(self._logout)
        header_layout.addWidget(self.logout_button)
        
        # Set as menu bar replacement
        self.setMenuWidget(header_widget)
    
    def _apply_styles(self):
        """Apply application styles."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a1929;
            }
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QPushButton {
                background-color: #40e0d0;
                color: #0a1929;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
            QStatusBar {
                background-color: #0d2137;
                color: #40e0d0;
                border-top: 1px solid #1a4a5a;
            }
        """)
    
    def _show_splash(self):
        """Show the splash screen."""
        self.stacked_widget.setCurrentWidget(self.splash_screen)
    
    def _show_login(self):
        """Show the login screen."""
        self.stacked_widget.setCurrentWidget(self.login_screen)
    
    def _handle_login(self, username: str):
        """Handle successful login."""
        self.current_user = username
        self.logout_button.setVisible(True)
        self.statusbar.showMessage(f"Welcome, {username}")
        self._show_dashboard()
    
    def _show_dashboard(self):
        """Show the main dashboard."""
        self.stacked_widget.setCurrentWidget(self.dashboard)
    
    def _show_new_case_dialog(self):
        """Show the new case creation dialog."""
        dialog = NewCaseDialog(self)
        dialog.case_created.connect(self._handle_case_created)
        dialog.exec()
    
    def _handle_case_created(self, case_id: int):
        """Handle new case creation."""
        self.current_case_id = case_id
        self.statusbar.showMessage(f"Case created (ID: {case_id})")
        
        # Show evidence management for the new case
        self._show_evidence_management()
    
    def _show_evidence_management(self):
        """Show the evidence management screen."""
        if self.evidence_management is None:
            self.evidence_management = EvidenceManagement(self.current_case_id)
            self.stacked_widget.addWidget(self.evidence_management)
        else:
            self.evidence_management.set_case_id(self.current_case_id)
        
        self.stacked_widget.setCurrentWidget(self.evidence_management)
    
    def _logout(self):
        """Handle user logout."""
        self.current_user = None
        self.current_case_id = None
        self.logout_button.setVisible(False)
        self.statusbar.showMessage("Logged out")
        self._show_login()
