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
from .profile_setup import ProfileSetupScreen
from .cases_dashboard import CasesDashboard
from .case_management import CaseManagement
from .evidence_management import EvidenceManagement
from .evidence_upload import EvidenceUpload
from .metadata_table import MetadataTable
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
        self.current_user_id = None
        
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
        self.profile_setup = ProfileSetupScreen()
        self.cases_dashboard = CasesDashboard()
        self.case_management = CaseManagement()
        self.evidence_upload = None  # Created when needed
        self.metadata_table = None  # Created when needed
        self.evidence_management = None  # Created when needed
        
        # Add screens to stack
        self.stacked_widget.addWidget(self.splash_screen)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.profile_setup)
        self.stacked_widget.addWidget(self.cases_dashboard)
        self.stacked_widget.addWidget(self.case_management)
        
        # Connect signals
        self.splash_screen.finished.connect(self._show_login)
        self.login_screen.login_successful.connect(self._handle_login)
        self.profile_setup.setup_completed.connect(self._handle_profile_completed)
        self.cases_dashboard.new_case_requested.connect(self._show_case_management)
        self.cases_dashboard.case_selected.connect(self._handle_case_selected)
        self.case_management.case_created.connect(self._handle_case_created)
        self.case_management.back_requested.connect(self._show_cases_dashboard)
        
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
        """Show the login screen and attempt auto-login."""
        # Try auto-login first
        if not self.login_screen.try_auto_login():
            # If auto-login fails, show the login screen
            self.stacked_widget.setCurrentWidget(self.login_screen)
    
    def _handle_login(self, username: str, user_id: int):
        """Handle successful login."""
        self.current_user = username
        self.current_user_id = user_id
        self.logout_button.setVisible(True)
        self.statusbar.showMessage(f"Welcome, {username}")
        
        # Check if profile setup is completed
        if self.database.is_profile_completed(user_id):
            # Profile already set up — go straight to cases dashboard
            self._show_cases_dashboard()
        else:
            # First login — show profile setup screen
            user = self.database.get_user(user_id)
            full_name = user['full_name'] if user else username
            self.profile_setup.set_user(user_id, full_name)
            self.stacked_widget.setCurrentWidget(self.profile_setup)
    
    def _handle_profile_completed(self):
        """Handle profile setup completion — go to cases dashboard."""
        self.statusbar.showMessage(f"Profile set up! Welcome, {self.current_user}")
        self._show_cases_dashboard()
    
    def _show_cases_dashboard(self):
        """Show the cases dashboard screen."""
        self.cases_dashboard.load_cases()
        self.stacked_widget.setCurrentWidget(self.cases_dashboard)
    
    def _show_case_management(self):
        """Show the case management screen."""
        self.stacked_widget.setCurrentWidget(self.case_management)
    
    def _handle_case_selected(self, case_id: int):
        """Handle case selection from dashboard."""
        self.current_case_id = case_id
        case = self.database.get_case(case_id)
        if case:
            self.statusbar.showMessage(f"Opened case: {case['name']}")
        # Navigate to evidence upload or metadata table for this case
        self._show_metadata_table()
    
    def _show_evidence_upload(self):
        """Show the evidence upload screen."""
        if self.evidence_upload is None:
            self.evidence_upload = EvidenceUpload(self.current_case_id)
            self.evidence_upload.back_requested.connect(self._show_case_management)
            self.evidence_upload.upload_completed.connect(self._handle_upload_completed)
            self.stacked_widget.addWidget(self.evidence_upload)
        else:
            self.evidence_upload.set_case_id(self.current_case_id)
        
        # Update status bar with case info
        case = self.database.get_case(self.current_case_id)
        if case:
            self.statusbar.showMessage(f"Uploading evidence for: {case['name']}")
        
        self.stacked_widget.setCurrentWidget(self.evidence_upload)
    
    def _handle_upload_completed(self, total_files: int):
        """Handle evidence upload completion."""
        self.statusbar.showMessage(f"Successfully uploaded {total_files} files")
        # Navigate to metadata table to view the uploaded files
        self._show_metadata_table()
    
    def _show_metadata_table(self):
        """Show the metadata table screen."""
        if self.metadata_table is None:
            self.metadata_table = MetadataTable(self.current_case_id)
            self.metadata_table.back_requested.connect(self._show_evidence_upload)
            self.stacked_widget.addWidget(self.metadata_table)
        else:
            self.metadata_table.set_case_id(self.current_case_id)
        
        # Update status bar
        case = self.database.get_case(self.current_case_id)
        if case:
            self.statusbar.showMessage(f"Viewing metadata for: {case['name']}")
        
        self.stacked_widget.setCurrentWidget(self.metadata_table)
    
    def _handle_case_created(self, case_id: int):
        """Handle new case creation."""
        self.current_case_id = case_id
        self.statusbar.showMessage(f"Case created (ID: {case_id})")
        
        # Show evidence upload screen for the new case
        self._show_evidence_upload()
    
    def _show_evidence_management(self):
        """Show the evidence management screen."""
        if self.evidence_management is None:
            self.evidence_management = EvidenceManagement(self.current_case_id)
            self.evidence_management.back_to_dashboard.connect(self._show_case_management)
            self.stacked_widget.addWidget(self.evidence_management)
        else:
            self.evidence_management.set_case_id(self.current_case_id)
        
        # Update status bar with case info
        case = self.database.get_case(self.current_case_id)
        if case:
            self.statusbar.showMessage(f"Working on Case #{case['id']}: {case['name']}")
        
        self.stacked_widget.setCurrentWidget(self.evidence_management)
    
    def _logout(self):
        """Handle user logout."""
        self.current_user = None
        self.current_user_id = None
        self.current_case_id = None
        self.logout_button.setVisible(False)
        self.statusbar.showMessage("Logged out")
        self._show_login()
