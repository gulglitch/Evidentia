"""
Profile Setup Screen
Interactive onboarding screen shown after first login
Lets users select their role and how they plan to use Evidentia
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QLineEdit, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..core.database import Database


class RoleCard(QFrame):
    """Clickable card for role selection."""
    
    clicked = Signal(str)  # role_name
    
    def __init__(self, icon: str, title: str, description: str):
        super().__init__()
        self.title = title
        self._selected = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(280, 160)
        self._setup_ui(icon, title, description)
        self._update_style()
    
    def _setup_ui(self, icon: str, title: str, description: str):
        """Setup the card UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        icon_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #8899aa; background: transparent; border: none;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
    
    def _update_style(self):
        """Update card visual state."""
        if self._selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #163545;
                    border: 2px solid #40e0d0;
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #122a3a;
                    border: 2px solid #1a4a5a;
                    border-radius: 12px;
                }
                QFrame:hover {
                    border-color: #2a7a8a;
                    background-color: #153040;
                }
            """)
    
    def set_selected(self, selected: bool):
        """Set selection state."""
        self._selected = selected
        self._update_style()
    
    def is_selected(self) -> bool:
        return self._selected
    
    def mousePressEvent(self, event):
        """Handle click."""
        self.clicked.emit(self.title)


class UseCard(QFrame):
    """Clickable card for primary use selection."""
    
    clicked = Signal(str)  # use_name
    
    def __init__(self, icon: str, title: str):
        super().__init__()
        self.title = title
        self._selected = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(200, 100)
        self._setup_ui(icon, title)
        self._update_style()
    
    def _setup_ui(self, icon: str, title: str):
        """Setup the card UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(6)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("Segoe UI Emoji", 22))
        icon_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(title_label)
    
    def _update_style(self):
        """Update card visual state."""
        if self._selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #163545;
                    border: 2px solid #40e0d0;
                    border-radius: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #122a3a;
                    border: 2px solid #1a4a5a;
                    border-radius: 10px;
                }
                QFrame:hover {
                    border-color: #2a7a8a;
                    background-color: #153040;
                }
            """)
    
    def set_selected(self, selected: bool):
        self._selected = selected
        self._update_style()
    
    def is_selected(self) -> bool:
        return self._selected
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.title)


class ProfileSetupScreen(QWidget):
    """Profile setup screen shown after first login."""
    
    setup_completed = Signal()  # Emitted when user finishes setup
    
    def __init__(self, user_id: int = None, full_name: str = ""):
        super().__init__()
        self.user_id = user_id
        self.full_name = full_name
        self.database = Database()
        self.selected_role = None
        self.selected_use = None
        self._setup_ui()
        self._apply_styles()
    
    def set_user(self, user_id: int, full_name: str):
        """Set the current user info."""
        self.user_id = user_id
        self.full_name = full_name
        self.welcome_label.setText(f"Welcome to Evidentia, {full_name}!")
    
    def _setup_ui(self):
        """Setup the profile setup UI."""
        # Scrollable main layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(30)
        
        # ── Welcome Header ──
        self.welcome_label = QLabel(f"Welcome to Evidentia, {self.full_name}!")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setFont(QFont("Arial", 28, QFont.Bold))
        self.welcome_label.setStyleSheet("color: #00d4aa;")
        main_layout.addWidget(self.welcome_label)
        
        subtitle = QLabel("Let's personalize your experience. Tell us how you'll use this tool.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet("color: #8899aa;")
        main_layout.addWidget(subtitle)
        
        # ── Role Selection ──
        role_header = QLabel("I am a...")
        role_header.setFont(QFont("Arial", 18, QFont.Bold))
        role_header.setStyleSheet("color: #e0e6ed;")
        main_layout.addWidget(role_header)
        
        role_grid = QHBoxLayout()
        role_grid.setSpacing(20)
        role_grid.setAlignment(Qt.AlignCenter)
        
        self.role_cards = []
        roles = [
            ("🔍", "Forensic Investigator", "Professional digital forensic examiner"),
            ("⚖️", "Legal Professional", "Attorney or legal analyst handling evidence"),
            ("🛡️", "Cybersecurity Analyst", "Security professional & incident responder"),
            ("🎓", "Student / Learner", "Learning digital forensics and analysis"),
        ]
        
        for icon, title, desc in roles:
            card = RoleCard(icon, title, desc)
            card.clicked.connect(self._on_role_selected)
            self.role_cards.append(card)
            role_grid.addWidget(card)
        
        main_layout.addLayout(role_grid)
        
        # ── Primary Use Selection ──
        use_header = QLabel("I primarily want to...")
        use_header.setFont(QFont("Arial", 18, QFont.Bold))
        use_header.setStyleSheet("color: #e0e6ed;")
        main_layout.addWidget(use_header)
        
        use_grid = QHBoxLayout()
        use_grid.setSpacing(20)
        use_grid.setAlignment(Qt.AlignCenter)
        
        self.use_cards = []
        uses = [
            ("📁", "Manage Cases"),
            ("🔬", "Analyze Evidence"),
            ("📊", "Generate Reports"),
            ("📚", "Learn & Train"),
        ]
        
        for icon, title in uses:
            card = UseCard(icon, title)
            card.clicked.connect(self._on_use_selected)
            self.use_cards.append(card)
            use_grid.addWidget(card)
        
        main_layout.addLayout(use_grid)
        
        # ── Organization (Optional) ──
        org_container = QVBoxLayout()
        org_container.setAlignment(Qt.AlignCenter)
        org_container.setSpacing(10)
        
        org_label = QLabel("Organization (optional):")
        org_label.setAlignment(Qt.AlignCenter)
        org_label.setFont(QFont("Arial", 13))
        org_label.setStyleSheet("color: #8899aa;")
        org_container.addWidget(org_label)
        
        self.org_input = QLineEdit()
        self.org_input.setPlaceholderText("e.g. University, Company, Lab...")
        self.org_input.setFixedWidth(400)
        self.org_input.setMinimumHeight(38)
        self.org_input.setFont(QFont("Arial", 13))
        self.org_input.setAlignment(Qt.AlignCenter)
        
        # Wrap input in horizontal layout to center it
        org_input_layout = QHBoxLayout()
        org_input_layout.setAlignment(Qt.AlignCenter)
        org_input_layout.addWidget(self.org_input)
        org_container.addLayout(org_input_layout)
        
        main_layout.addLayout(org_container)
        
        # ── Error label ──
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setFont(QFont("Arial", 12))
        self.error_label.setStyleSheet("color: #ff6b6b;")
        self.error_label.setVisible(False)
        main_layout.addWidget(self.error_label)
        
        # ── Buttons ──
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(20)
        
        # Skip button
        skip_btn = QPushButton("Skip for Now")
        skip_btn.setFont(QFont("Arial", 13))
        skip_btn.setFixedSize(180, 45)
        skip_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8899aa;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #122a3a;
                border-color: #40e0d0;
                color: #e0e6ed;
            }
        """)
        skip_btn.clicked.connect(self._handle_skip)
        button_layout.addWidget(skip_btn)
        
        # Continue button
        continue_btn = QPushButton("Continue ›")
        continue_btn.setFont(QFont("Arial", 13))
        continue_btn.setFixedSize(220, 45)
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #40e0d0;
                color: #0a1929;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
        """)
        continue_btn.clicked.connect(self._handle_continue)
        button_layout.addWidget(continue_btn)
        
        main_layout.addLayout(button_layout)
        
        main_layout.addStretch()
    
    def _apply_styles(self):
        """Apply screen styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QLineEdit {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
                padding: 8px 14px;
                color: #e0e6ed;
            }
            QLineEdit:focus {
                border-color: #40e0d0;
                background-color: #122a3a;
            }
            QLineEdit::placeholder {
                color: #6c7086;
            }
        """)
    
    def _on_role_selected(self, role_name: str):
        """Handle role card selection."""
        self.selected_role = role_name
        for card in self.role_cards:
            card.set_selected(card.title == role_name)
        self.error_label.setVisible(False)
    
    def _on_use_selected(self, use_name: str):
        """Handle use card selection."""
        self.selected_use = use_name
        for card in self.use_cards:
            card.set_selected(card.title == use_name)
        self.error_label.setVisible(False)
    
    def _handle_continue(self):
        """Handle continue button — save preferences."""
        if not self.selected_role:
            self.error_label.setText("Please select your role above")
            self.error_label.setVisible(True)
            return
        
        if not self.selected_use:
            self.error_label.setText("Please select how you plan to use Evidentia")
            self.error_label.setVisible(True)
            return
        
        # Save to database
        if self.user_id:
            self.database.save_user_preferences(
                self.user_id,
                self.selected_role,
                self.org_input.text().strip(),
                self.selected_use
            )
        
        self.setup_completed.emit()
    
    def _handle_skip(self):
        """Handle skip button — go to dashboard without saving preferences."""
        # Save a minimal record so we don't show this screen again
        if self.user_id:
            self.database.save_user_preferences(
                self.user_id,
                "Not specified",
                "",
                "Not specified"
            )
        
        self.setup_completed.emit()
