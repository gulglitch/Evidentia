"""
New Case Dialog Module
Dialog for creating new investigation cases
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QRadioButton, QButtonGroup,
    QPushButton, QFrame, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class NewCaseDialog(QDialog):
    """Dialog for creating a new case."""
    
    case_created = Signal(int)  # case_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Case")
        self.setFixedSize(600, 580)
        self.setModal(True)
        self.custom_case_types = self._load_custom_case_types()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Create New Investigation Case")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)
        
        # Form
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(20)
        
        # Case Name
        name_label = QLabel("Case Name *")
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter case name")
        self.name_input.setMinimumHeight(40)
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)
        
        # Case Type
        type_label = QLabel("Case Type *")
        type_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        type_container = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.setMinimumHeight(40)
        self._populate_case_types()
        self.type_combo.currentTextChanged.connect(self._on_case_type_changed)
        type_container.addWidget(self.type_combo, 1)
        
        # Add custom type button
        add_type_button = QPushButton("+ Add Custom")
        add_type_button.setMinimumHeight(40)
        add_type_button.setMaximumWidth(120)
        add_type_button.clicked.connect(self._add_custom_case_type)
        type_container.addWidget(add_type_button)
        
        form_layout.addWidget(type_label)
        form_layout.addLayout(type_container)
        
        # Custom case type input (hidden by default)
        self.custom_type_input = QLineEdit()
        self.custom_type_input.setPlaceholderText("Enter custom case type name")
        self.custom_type_input.setMinimumHeight(40)
        self.custom_type_input.setVisible(False)
        form_layout.addWidget(self.custom_type_input)
        
        # Description
        desc_label = QLabel("Description")
        desc_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter case description (optional)")
        self.desc_input.setMaximumHeight(100)
        form_layout.addWidget(desc_label)
        form_layout.addWidget(self.desc_input)
        
        # Priority
        priority_label = QLabel("Priority")
        priority_label.setFont(QFont("Arial", 14, QFont.Bold))
        priority_layout = QHBoxLayout()
        priority_layout.setSpacing(20)
        
        self.priority_group = QButtonGroup()
        priorities = ["Low", "Medium", "High"]
        self.priority_radios = {}
        
        for priority in priorities:
            radio = QRadioButton(priority)
            radio.setFont(QFont("Arial", 14))
            self.priority_group.addButton(radio)
            self.priority_radios[priority] = radio
            priority_layout.addWidget(radio)
        
        # Set Medium as default
        self.priority_radios["Medium"].setChecked(True)
        
        form_layout.addWidget(priority_label)
        form_layout.addLayout(priority_layout)
        
        layout.addWidget(form_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumHeight(40)
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        create_button = QPushButton("Create Case")
        create_button.setMinimumHeight(40)
        create_button.setMinimumWidth(120)
        create_button.clicked.connect(self._create_case)
        create_button.setDefault(True)
        button_layout.addWidget(create_button)
        
        layout.addLayout(button_layout)
        
        # Connect Enter key to create
        self.name_input.returnPressed.connect(self._create_case)
    
    def _load_custom_case_types(self):
        """Load custom case types from database."""
        from ..core.database import Database
        database = Database()
        return database.get_custom_case_types()
    
    def _populate_case_types(self):
        """Populate the case type combo box."""
        self.type_combo.clear()
        
        # Default case types
        default_types = [
            "Financial Fraud",
            "Cybercrime", 
            "Data Breach",
            "Intellectual Property Theft",
            "Corporate Investigation",
            "Personal Investigation"
        ]
        
        self.type_combo.addItems(default_types)
        
        # Add custom case types
        if self.custom_case_types:
            self.type_combo.insertSeparator(len(default_types))
            self.type_combo.addItems(self.custom_case_types)
        
        # Add "Other" option
        self.type_combo.insertSeparator(self.type_combo.count())
        self.type_combo.addItem("Other (Custom)")
    
    def _on_case_type_changed(self, text):
        """Handle case type selection change."""
        # Show custom input if "Other" is selected
        is_other = text == "Other (Custom)"
        self.custom_type_input.setVisible(is_other)
        if is_other:
            self.custom_type_input.setFocus()
    
    def _add_custom_case_type(self):
        """Add a new custom case type."""
        text, ok = QInputDialog.getText(
            self,
            "Add Custom Case Type",
            "Enter custom case type name:",
            QLineEdit.Normal,
            ""
        )
        
        if ok and text.strip():
            custom_type = text.strip()
            
            # Check if it already exists
            if custom_type in self.custom_case_types:
                QMessageBox.information(
                    self,
                    "Already Exists",
                    f"The case type '{custom_type}' already exists."
                )
                return
            
            # Save to database
            from ..core.database import Database
            database = Database()
            if database.add_custom_case_type(custom_type):
                self.custom_case_types.append(custom_type)
                self._populate_case_types()
                # Select the newly added type
                self.type_combo.setCurrentText(custom_type)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Custom case type '{custom_type}' has been added."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to add custom case type."
                )
    
    def _apply_styles(self):
        """Apply dialog styles."""
        self.setStyleSheet("""
            QDialog {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QLabel {
                color: #00d4aa;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: #0d2137;
                border: 1px solid #1a4a5a;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                color: #e0e6ed;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #40e0d0;
            }
            QComboBox {
                background-color: #0d2137;
                border: 1px solid #1a4a5a;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                color: #e0e6ed;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                border: none;
            }
            QRadioButton {
                color: #e0e6ed;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #2a6a7a;
                border-radius: 8px;
                background-color: #0d2137;
            }
            QRadioButton::indicator:checked {
                background-color: #40e0d0;
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
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
            QPushButton:pressed {
                background-color: #00d4aa;
            }
            QFrame {
                background-color: #122a3a;
                border: 1px solid #1a4a5a;
                border-radius: 8px;
                padding: 20px;
            }
        """)
    
    def _create_case(self):
        """Create the new case."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a case name.")
            return
        
        case_type = self.type_combo.currentText()
        
        # If "Other" is selected, use the custom input
        if case_type == "Other (Custom)":
            case_type = self.custom_type_input.text().strip()
            if not case_type:
                QMessageBox.warning(self, "Validation Error", "Please enter a custom case type.")
                return
        
        description = self.desc_input.toPlainText().strip()
        
        # Get selected priority
        priority = "Medium"  # default
        for p, radio in self.priority_radios.items():
            if radio.isChecked():
                priority = p
                break
        
        # Import database here to avoid circular imports
        from ..core.database import Database
        
        database = Database()
        case_id = database.create_case(name, description, case_type)
        
        # Log the case creation
        database.log_activity(case_id, "Case Created", f"New {case_type} investigation started")
        
        self.case_created.emit(case_id)
        self.accept()