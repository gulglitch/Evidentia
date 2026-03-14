"""
Login Screen Module
User authentication interface
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class LoginScreen(QWidget):
    """Login and registration screen."""
    
    login_successful = Signal(str)  # username
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 600)
        self.setWindowTitle("Evidentia - Login")
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the login UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo
        logo = QLabel("Evidentia")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("Arial", 28, QFont.Bold))
        layout.addWidget(logo)
        
        # Login form
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Username
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        
        # Remember me
        self.remember_checkbox = QCheckBox("Remember me")
        form_layout.addWidget(self.remember_checkbox)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self._handle_login)
        form_layout.addWidget(self.login_button)
        
        # Sign up link
        signup_layout = QHBoxLayout()
        signup_layout.addStretch()
        signup_label = QLabel("Don't have an account?")
        self.signup_button = QPushButton("Sign Up")
        self.signup_button.clicked.connect(self._show_signup)
        signup_layout.addWidget(signup_label)
        signup_layout.addWidget(self.signup_button)
        signup_layout.addStretch()
        form_layout.addLayout(signup_layout)
        
        layout.addWidget(form_frame)
        
        # Connect Enter key to login
        self.username_input.returnPressed.connect(self._handle_login)
        self.password_input.returnPressed.connect(self._handle_login)
    
    def _apply_styles(self):
        """Apply login screen styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QLabel {
                color: #00d4aa;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #0d2137;
                border: 1px solid #1a4a5a;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                color: #e0e6ed;
            }
            QLineEdit:focus {
                border-color: #40e0d0;
            }
            QPushButton {
                background-color: #40e0d0;
                color: #0a1929;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
            QPushButton:pressed {
                background-color: #00d4aa;
            }
            QCheckBox {
                color: #e0e6ed;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #2a6a7a;
                border-radius: 3px;
                background-color: #0d2137;
            }
            QCheckBox::indicator:checked {
                background-color: #40e0d0;
                border-color: #40e0d0;
            }
            QFrame {
                background-color: #122a3a;
                border: 1px solid #1a4a5a;
                border-radius: 8px;
                padding: 20px;
            }
        """)
    
    def _handle_login(self):
        """Handle login attempt."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            return
        
        # For now, accept any non-empty credentials
        # In a real app, this would validate against a database
        self.login_successful.emit(username)
    
    def _show_signup(self):
        """Show signup form (toggle between login and signup)."""
        # For now, just accept the current inputs as new user
        username = self.username_input.text().strip()
        if username:
            self.login_successful.emit(username)