"""
Login Screen Module
User authentication interface with Login and Sign Up forms
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFrame, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtGui import QFont
import os

from backend.app.database import Database


class LoginScreen(QWidget):
    """Login and registration screen."""
    
    login_successful = Signal(str, int)  # username, user_id
    
    def __init__(self):
        super().__init__()
        self.database = Database()
        self.settings = QSettings("Evidentia", "EvidentiApp")
        self.setWindowTitle("Evidentia - Login")
        self._setup_ui()
        self._apply_styles()
        self._load_remembered_credentials()
    
    def _setup_ui(self):
        """Setup the login UI with stacked login/signup forms."""
        # Main layout that centers everything
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)

        # Stacked widget to switch between login and signup
        self.form_stack = QStackedWidget()
        self.form_stack.setFixedSize(450, 600)

        # Create both forms
        self._create_login_form()
        self._create_signup_form()

        main_layout.addWidget(self.form_stack, alignment=Qt.AlignCenter)

    def _create_login_form(self):
        """Create the login form."""
        container = QWidget()
        container.setObjectName("loginContainer")
        container.setStyleSheet("""
            QWidget#loginContainer {
                background-color: #122a3a;
                border: 1px solid #1a4a5a;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 40, 50, 40)

        # Logo
        logo = QLabel("Evidentia")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("Arial", 32, QFont.Bold))
        logo.setStyleSheet("color: #00d4aa; background: transparent; border: none;")
        layout.addWidget(logo)

        # Subtitle
        subtitle = QLabel("Sign in to your account")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 13))
        subtitle.setStyleSheet("color: #8899aa; background: transparent; border: none;")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Username field
        username_label = QLabel("Username:")
        username_label.setFont(QFont("Arial", 13, QFont.Bold))
        username_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(username_label)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Enter your username")
        self.login_username.setMinimumHeight(42)
        self.login_username.setFont(QFont("Arial", 13))
        layout.addWidget(self.login_username)

        # Password field
        password_label = QLabel("Password:")
        password_label.setFont(QFont("Arial", 13, QFont.Bold))
        password_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none; margin-top: 5px;")
        layout.addWidget(password_label)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter your password")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setMinimumHeight(42)
        self.login_password.setFont(QFont("Arial", 13))
        layout.addWidget(self.login_password)

        # Error message label (hidden by default)
        self.login_error = QLabel("")
        self.login_error.setAlignment(Qt.AlignCenter)
        self.login_error.setFont(QFont("Arial", 12))
        self.login_error.setStyleSheet("color: #ff6b6b; background: transparent; border: none;")
        self.login_error.setVisible(False)
        layout.addWidget(self.login_error)

        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setFont(QFont("Arial", 13))
        self.remember_checkbox.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(self.remember_checkbox)

        # Login button
        login_button = QPushButton("Login")
        login_button.setMinimumHeight(45)
        login_button.setFont(QFont("Arial", 15, QFont.Bold))
        login_button.clicked.connect(self._handle_login)
        layout.addWidget(login_button)

        # Sign up link
        signup_layout = QHBoxLayout()
        signup_layout.addStretch()
        signup_label = QLabel("Don't have an account?")
        signup_label.setFont(QFont("Arial", 12))
        signup_label.setStyleSheet("color: #8899aa; background: transparent; border: none;")
        switch_to_signup = QPushButton("Sign Up")
        switch_to_signup.setFont(QFont("Arial", 12))
        switch_to_signup.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #40e0d0;
                border: none;
                text-decoration: underline;
                padding: 5px;
            }
            QPushButton:hover {
                color: #2dd4bf;
            }
        """)
        switch_to_signup.clicked.connect(lambda: self._switch_to_form("signup"))
        signup_layout.addWidget(signup_label)
        signup_layout.addWidget(switch_to_signup)
        signup_layout.addStretch()
        layout.addLayout(signup_layout)

        # Connect Enter key to login
        self.login_username.returnPressed.connect(self._handle_login)
        self.login_password.returnPressed.connect(self._handle_login)

        self.form_stack.addWidget(container)

    def _create_signup_form(self):
        """Create the signup form."""
        container = QWidget()
        container.setObjectName("signupContainer")
        container.setStyleSheet("""
            QWidget#signupContainer {
                background-color: #122a3a;
                border: 1px solid #1a4a5a;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(14)
        layout.setContentsMargins(50, 30, 50, 30)

        # Logo
        logo = QLabel("Evidentia")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("Arial", 28, QFont.Bold))
        logo.setStyleSheet("color: #00d4aa; background: transparent; border: none;")
        layout.addWidget(logo)

        # Subtitle
        subtitle = QLabel("Create a new account")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 13))
        subtitle.setStyleSheet("color: #8899aa; background: transparent; border: none;")
        layout.addWidget(subtitle)

        layout.addSpacing(5)

        # Full Name field
        name_label = QLabel("Full Name *")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        name_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(name_label)

        self.signup_fullname = QLineEdit()
        self.signup_fullname.setPlaceholderText("Enter your full name")
        self.signup_fullname.setMinimumHeight(38)
        self.signup_fullname.setFont(QFont("Arial", 12))
        layout.addWidget(self.signup_fullname)

        # Email field
        email_label = QLabel("Email")
        email_label.setFont(QFont("Arial", 12, QFont.Bold))
        email_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(email_label)

        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("Enter your email (optional)")
        self.signup_email.setMinimumHeight(38)
        self.signup_email.setFont(QFont("Arial", 12))
        layout.addWidget(self.signup_email)

        # Username field
        username_label = QLabel("Username * (min 4 characters)")
        username_label.setFont(QFont("Arial", 12, QFont.Bold))
        username_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(username_label)

        self.signup_username = QLineEdit()
        self.signup_username.setPlaceholderText("Choose a username")
        self.signup_username.setMinimumHeight(38)
        self.signup_username.setFont(QFont("Arial", 12))
        layout.addWidget(self.signup_username)

        # Password field
        password_label = QLabel("Password * (min 6 characters)")
        password_label.setFont(QFont("Arial", 12, QFont.Bold))
        password_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(password_label)

        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Choose a password")
        self.signup_password.setEchoMode(QLineEdit.Password)
        self.signup_password.setMinimumHeight(38)
        self.signup_password.setFont(QFont("Arial", 12))
        layout.addWidget(self.signup_password)

        # Confirm Password field
        confirm_label = QLabel("Confirm Password *")
        confirm_label.setFont(QFont("Arial", 12, QFont.Bold))
        confirm_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(confirm_label)

        self.signup_confirm = QLineEdit()
        self.signup_confirm.setPlaceholderText("Confirm your password")
        self.signup_confirm.setEchoMode(QLineEdit.Password)
        self.signup_confirm.setMinimumHeight(38)
        self.signup_confirm.setFont(QFont("Arial", 12))
        layout.addWidget(self.signup_confirm)

        # Error message label (hidden by default)
        self.signup_error = QLabel("")
        self.signup_error.setAlignment(Qt.AlignCenter)
        self.signup_error.setFont(QFont("Arial", 11))
        self.signup_error.setStyleSheet("color: #ff6b6b; background: transparent; border: none;")
        self.signup_error.setVisible(False)
        self.signup_error.setWordWrap(True)
        layout.addWidget(self.signup_error)

        # Create Account button
        create_button = QPushButton("Create Account")
        create_button.setMinimumHeight(42)
        create_button.setFont(QFont("Arial", 14, QFont.Bold))
        create_button.clicked.connect(self._handle_signup)
        layout.addWidget(create_button)

        # Back to login link
        login_layout = QHBoxLayout()
        login_layout.addStretch()
        login_label = QLabel("Already have an account?")
        login_label.setFont(QFont("Arial", 12))
        login_label.setStyleSheet("color: #8899aa; background: transparent; border: none;")
        switch_to_login = QPushButton("Login")
        switch_to_login.setFont(QFont("Arial", 12))
        switch_to_login.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #40e0d0;
                border: none;
                text-decoration: underline;
                padding: 5px;
            }
            QPushButton:hover {
                color: #2dd4bf;
            }
        """)
        switch_to_login.clicked.connect(lambda: self._switch_to_form("login"))
        login_layout.addWidget(login_label)
        login_layout.addWidget(switch_to_login)
        login_layout.addStretch()
        layout.addLayout(login_layout)

        # Connect Enter key
        self.signup_confirm.returnPressed.connect(self._handle_signup)

        self.form_stack.addWidget(container)

    def _apply_styles(self):
        """Apply login screen styles with background image."""
        # Set background image on the main widget (outside the form containers)
        bg_path = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "bg_photo_2.png")
        if os.path.exists(bg_path):
            self.setStyleSheet(f"""
                LoginScreen {{
                    background-image: url({bg_path.replace(os.sep, '/')});
                    background-position: center;
                    background-repeat: no-repeat;
                    background-color: #0a1929;
                }}
                QWidget#loginContainer, QWidget#signupContainer {{
                    background-color: rgba(18, 42, 58, 0.95);
                    border: 1px solid #1a4a5a;
                    border-radius: 12px;
                }}
                QLineEdit {{
                    background-color: #0d2137;
                    border: 2px solid #1a4a5a;
                    border-radius: 8px;
                    padding: 10px 14px;
                    font-size: 13px;
                    color: #e0e6ed;
                }}
                QLineEdit:focus {{
                    border-color: #40e0d0;
                    background-color: #122a3a;
                }}
                QLineEdit::placeholder {{
                    color: #6c7086;
                }}
                QPushButton {{
                    background-color: #40e0d0;
                    color: #0a1929;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 24px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #2dd4bf;
                }}
                QPushButton:pressed {{
                    background-color: #00d4aa;
                }}
                QCheckBox {{
                    color: #e0e6ed;
                    spacing: 10px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid #2a6a7a;
                    border-radius: 4px;
                    background-color: #0d2137;
                }}
                QCheckBox::indicator:checked {{
                    background-color: #40e0d0;
                    border-color: #40e0d0;
                }}
            """)
        else:
            self.setStyleSheet("""
                LoginScreen {
                    background-color: #0a1929;
                }
                QLineEdit {
                    background-color: #0d2137;
                    border: 2px solid #1a4a5a;
                    border-radius: 8px;
                    padding: 10px 14px;
                    font-size: 13px;
                    color: #e0e6ed;
                }
                QLineEdit:focus {
                    border-color: #40e0d0;
                    background-color: #122a3a;
                }
                QLineEdit::placeholder {
                    color: #6c7086;
                }
                QPushButton {
                    background-color: #40e0d0;
                    color: #0a1929;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 24px;
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
                    spacing: 10px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #2a6a7a;
                    border-radius: 4px;
                    background-color: #0d2137;
                }
                QCheckBox::indicator:checked {
                    background-color: #40e0d0;
                    border-color: #40e0d0;
                }
            """)

    def _switch_to_form(self, form_name: str):
        """Switch between login and signup forms."""
        if form_name == "signup":
            self.form_stack.setCurrentIndex(1)
            self.signup_error.setVisible(False)
            # Clear signup fields
            self.signup_fullname.clear()
            self.signup_email.clear()
            self.signup_username.clear()
            self.signup_password.clear()
            self.signup_confirm.clear()
        else:
            self.form_stack.setCurrentIndex(0)
            self.login_error.setVisible(False)

    def _handle_login(self):
        """Handle login attempt with real database validation."""
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        # Basic validation
        if not username or not password:
            self._show_login_error("Please enter both username and password")
            return
        
        # Authenticate against database
        user = self.database.authenticate_user(username, password)
        
        if user is None:
            self._show_login_error("Invalid username or password")
            return
        
        # Save credentials if remember me is checked
        if self.remember_checkbox.isChecked():
            self._save_credentials(username, password)
        else:
            self._clear_credentials()
        
        # Success — emit signal with username and user_id
        self.login_error.setVisible(False)
        self.login_successful.emit(user['username'], user['id'])

    def _handle_signup(self):
        """Handle signup attempt with validation."""
        full_name = self.signup_fullname.text().strip()
        email = self.signup_email.text().strip()
        username = self.signup_username.text().strip()
        password = self.signup_password.text()
        confirm = self.signup_confirm.text()
        
        # Validate all required fields
        if not full_name:
            self._show_signup_error("Full name is required")
            return
        
        if not username:
            self._show_signup_error("Username is required")
            return
        
        if not password:
            self._show_signup_error("Password is required")
            return
        
        # Check password match
        if password != confirm:
            self._show_signup_error("Passwords do not match")
            return
        
        # Try to create user
        try:
            user_id = self.database.create_user(username, password, full_name, email)
        except ValueError as e:
            self._show_signup_error(str(e))
            return
        
        # Success — show confirmation and switch to login
        self.signup_error.setVisible(False)
        
        QMessageBox.information(
            self,
            "Account Created",
            f"Welcome to Evidentia, {full_name}!\n\nYour account has been created successfully.\nPlease login with your credentials."
        )
        
        # Pre-fill login username and switch to login form
        self.login_username.setText(username)
        self.login_password.clear()
        self._switch_to_form("login")

    def _show_login_error(self, message: str):
        """Show error message on login form."""
        self.login_error.setText(message)
        self.login_error.setVisible(True)

    def _show_signup_error(self, message: str):
        """Show error message on signup form."""
        self.signup_error.setText(message)
        self.signup_error.setVisible(True)
    
    def _save_credentials(self, username: str, password: str):
        """Save login credentials for remember me functionality."""
        self.settings.setValue("remember_me", True)
        self.settings.setValue("username", username)
        self.settings.setValue("password", password)
    
    def _clear_credentials(self):
        """Clear saved login credentials."""
        self.settings.setValue("remember_me", False)
        self.settings.remove("username")
        self.settings.remove("password")
    
    def _load_remembered_credentials(self):
        """Load and auto-fill remembered credentials."""
        remember_me = self.settings.value("remember_me", False, type=bool)
        if remember_me:
            username = self.settings.value("username", "")
            password = self.settings.value("password", "")
            if username and password:
                self.login_username.setText(username)
                self.login_password.setText(password)
                self.remember_checkbox.setChecked(True)
    
    def try_auto_login(self):
        """Attempt auto-login if credentials are remembered."""
        remember_me = self.settings.value("remember_me", False, type=bool)
        if remember_me:
            username = self.settings.value("username", "")
            password = self.settings.value("password", "")
            if username and password:
                # Authenticate
                user = self.database.authenticate_user(username, password)
                if user:
                    # Auto-login successful
                    self.login_successful.emit(user['username'], user['id'])
                    return True
        return False