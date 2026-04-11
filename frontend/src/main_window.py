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
import os

from .splash_screen import SplashScreen
from .login_screen import LoginScreen
from .profile_setup import ProfileSetupScreen
from .cases_dashboard import CasesDashboard
from .case_management import CaseManagement
from .evidence_upload import EvidenceUpload
from .metadata_table import MetadataTable
from .timeline_view import TimelineView
from .analytics_dashboard import AnalyticsDashboard
from .new_case_dialog import NewCaseDialog
from .case_home import CaseHome
from backend.app.database import Database


class MainWindow(QMainWindow):
    """Main application window controller."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Evidentia - Digital Forensics Timeline Tool")
        self.setMinimumSize(800, 600)
        # Start with a reasonable default size that will be adjusted to screen
        self.resize(1200, 800)
        
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
        self.stacked_widget.setObjectName("mainStack")
        self.setCentralWidget(self.stacked_widget)
        
        # Create screens
        self.splash_screen = SplashScreen()
        self.login_screen = LoginScreen()
        self.profile_setup = ProfileSetupScreen()
        self.cases_dashboard = CasesDashboard()
        self.case_management = CaseManagement()
        self.case_home = None  # Created when needed
        self.evidence_upload = None  # Created when needed
        self.metadata_table = None  # Created when needed
        self.timeline_view = None  # Created when needed
        self.analytics_dashboard = None  # Created when needed
        
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
        self._set_window_background(None)

    def _set_window_background(self, image_name: str = None):
        """Apply main-window background with optional image."""
        stack_bg = "background-color: #0a1929;"

        if image_name:
            image_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "assets",
                    "images",
                    image_name,
                )
            )
            if os.path.exists(image_path):
                css_path = image_path.replace("\\", "/")
                stack_bg += (
                    f"background-image: url('{css_path}');"
                    "background-position: center;"
                    "background-repeat: no-repeat;"
                )

        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a1929;
            }
            QStackedWidget#mainStack {
        """ + stack_bg + """
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
        # Splash uses main window background image; splash box stays centered on top.
        self._set_window_background("bg_photo_1.png")
        self.stacked_widget.setCurrentWidget(self.splash_screen)
    
    def _show_login(self):
        """Show the login screen and attempt auto-login."""
        self._set_window_background(None)
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
            self._set_window_background(None)
            self.stacked_widget.setCurrentWidget(self.profile_setup)
    
    def _handle_profile_completed(self):
        """Handle profile setup completion — go to cases dashboard."""
        self.statusbar.showMessage(f"Profile set up! Welcome, {self.current_user}")
        self._show_cases_dashboard()
    
    def _show_cases_dashboard(self):
        """Show the cases dashboard screen."""
        self._set_window_background(None)
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
        # Navigate to case workspace hub.
        self._show_case_home()

    def _show_case_home(self):
        """Show the case workspace hub for the selected case."""
        investigator_name = self._get_signed_in_display_name()

        if self.case_home is None:
            self.case_home = CaseHome(self.current_case_id)
            self.case_home.back_to_cases_requested.connect(self._show_cases_dashboard)
            self.case_home.upload_requested.connect(self._show_evidence_upload)
            self.case_home.evidence_requested.connect(self._show_metadata_table)
            self.case_home.timeline_requested.connect(self._show_timeline_view)
            self.case_home.analytics_requested.connect(self._show_analytics_dashboard)
            self.stacked_widget.addWidget(self.case_home)
            self.case_home.set_investigator_name(investigator_name)
        else:
            self.case_home.set_case_id(self.current_case_id)
            self.case_home.set_investigator_name(investigator_name)

        case = self.database.get_case(self.current_case_id)
        if case:
            self.statusbar.showMessage(f"Case workspace: {case['name']}")

        self.stacked_widget.setCurrentWidget(self.case_home)

    def _get_signed_in_display_name(self) -> str:
        """Return display name for the current signed-in user."""
        if self.current_user_id:
            user = self.database.get_user(self.current_user_id)
            if user and user.get('full_name'):
                return user['full_name']
        return self.current_user or "Assigned Investigator"
    
    def _show_evidence_upload(self):
        """Show the evidence upload screen."""
        if self.evidence_upload is None:
            self.evidence_upload = EvidenceUpload(self.current_case_id)
            self.evidence_upload.back_requested.connect(self._show_case_home)
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
            self.metadata_table.back_requested.connect(self._show_case_home)
            self.stacked_widget.addWidget(self.metadata_table)
        else:
            self.metadata_table.set_case_id(self.current_case_id)
        
        # Update status bar
        case = self.database.get_case(self.current_case_id)
        if case:
            self.statusbar.showMessage(f"Viewing metadata for: {case['name']}")
        
        self.stacked_widget.setCurrentWidget(self.metadata_table)
    
    def _show_timeline_view(self):
        """Show the timeline view screen."""
        if self.timeline_view is None:
            from .timeline_view import TimelineView
            self.timeline_view = TimelineView(self.current_case_id)
            self.timeline_view.back_requested.connect(self._show_case_home)
            self.stacked_widget.addWidget(self.timeline_view)
        else:
            self.timeline_view.set_case_id(self.current_case_id)
        
        # Update status bar
        case = self.database.get_case(self.current_case_id)
        if case:
            self.statusbar.showMessage(f"Timeline view for: {case['name']}")
        
        self.stacked_widget.setCurrentWidget(self.timeline_view)
    
    def _show_analytics_dashboard(self):
        """Show the analytics dashboard screen."""
        if self.analytics_dashboard is None:
            self.analytics_dashboard = AnalyticsDashboard(self.current_case_id)
            self.analytics_dashboard.back_requested.connect(self._show_case_home)
            self.stacked_widget.addWidget(self.analytics_dashboard)
        else:
            self.analytics_dashboard.set_case_id(self.current_case_id)
        
        # Update status bar
        case = self.database.get_case(self.current_case_id)
        if case:
            self.statusbar.showMessage(f"Analytics for: {case['name']}")
        
        self.stacked_widget.setCurrentWidget(self.analytics_dashboard)
    
    def _handle_case_created(self, case_id: int):
        """Handle new case creation."""
        self.current_case_id = case_id
        self.statusbar.showMessage(f"Case created (ID: {case_id})")

        # Show case workspace after creation.
        self._show_case_home()
    
    
    def _logout(self):
        """Handle user logout."""
        # Clear user session
        self.current_user = None
        self.current_user_id = None
        self.current_case_id = None
        self.logout_button.setVisible(False)
        
        # Clear saved credentials to prevent auto-login
        self.login_screen._clear_credentials()
        
        # Clear login form fields
        self.login_screen.login_username.clear()
        self.login_screen.login_password.clear()
        self.login_screen.remember_checkbox.setChecked(False)
        
        # Show login screen
        self.stacked_widget.setCurrentWidget(self.login_screen)
        self.statusbar.showMessage("Logged out successfully")
