"""
Milestone Dialog
Dialog for creating and managing case milestones
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QDateEdit, QTextEdit, QListWidget, QListWidgetItem,
    QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont
from typing import List, Dict, Any

from backend.app.database import Database


class MilestoneDialog(QDialog):
    """Dialog for managing milestones."""
    
    milestone_added = Signal()
    
    def __init__(self, case_id: int, parent=None):
        super().__init__(parent)
        self.case_id = case_id
        self.database = Database()
        self.milestones = []
        self._setup_ui()
        self._apply_styles()
        self._load_milestones()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Manage Milestones")
        self.setMinimumSize(700, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("Case Milestones")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #00d4aa;")
        main_layout.addWidget(title)
        
        # Content layout (list + form)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left side - Milestone list
        list_container = QVBoxLayout()
        
        list_label = QLabel("Existing Milestones:")
        list_label.setFont(QFont("Arial", 12, QFont.Bold))
        list_container.addWidget(list_label)
        
        self.milestone_list = QListWidget()
        self.milestone_list.setMinimumWidth(300)
        list_container.addWidget(self.milestone_list)
        
        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.setFixedHeight(35)
        delete_btn.clicked.connect(self._delete_milestone)
        list_container.addWidget(delete_btn)
        
        content_layout.addLayout(list_container)
        
        # Right side - Add milestone form
        form_container = QVBoxLayout()
        
        form_label = QLabel("Add New Milestone:")
        form_label.setFont(QFont("Arial", 12, QFont.Bold))
        form_container.addWidget(form_label)
        
        # Milestone name
        name_label = QLabel("Milestone Name:")
        name_label.setFont(QFont("Arial", 11))
        form_container.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Evidence Collection Started")
        self.name_input.setMinimumHeight(35)
        form_container.addWidget(self.name_input)
        
        # Milestone date
        date_label = QLabel("Date:")
        date_label.setFont(QFont("Arial", 11))
        form_container.addWidget(date_label)
        
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumHeight(35)
        form_container.addWidget(self.date_input)
        
        # Description
        desc_label = QLabel("Description (optional):")
        desc_label.setFont(QFont("Arial", 11))
        form_container.addWidget(desc_label)
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Additional details about this milestone...")
        self.desc_input.setMaximumHeight(100)
        form_container.addWidget(self.desc_input)
        
        # Add button
        add_btn = QPushButton("Add Milestone")
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self._add_milestone)
        form_container.addWidget(add_btn)
        
        form_container.addStretch()
        
        content_layout.addLayout(form_container)
        
        main_layout.addLayout(content_layout)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(120, 40)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
    
    def _apply_styles(self):
        """Apply dialog styles."""
        self.setStyleSheet("""
            QDialog {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QLabel {
                color: #e0e6ed;
            }
            QLineEdit, QTextEdit, QDateEdit {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e6ed;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus {
                border-color: #40e0d0;
            }
            QPushButton {
                background-color: #40e0d0;
                color: #0a1929;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
            QListWidget {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #2a7a8a;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #1a4a5a;
            }
        """)
    
    def _load_milestones(self):
        """Load existing milestones from database."""
        self.milestone_list.clear()
        self.milestones = self.database.get_milestones(self.case_id)
        
        for milestone in self.milestones:
            item_text = f"{milestone['milestone_name']} - {milestone['milestone_date']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, milestone['id'])
            self.milestone_list.addItem(item)
    
    def _add_milestone(self):
        """Add a new milestone."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a milestone name.")
            return
        
        date = self.date_input.date().toString(Qt.ISODate)
        description = self.desc_input.toPlainText().strip()
        
        try:
            self.database.create_milestone(
                self.case_id,
                name,
                date,
                description
            )
            
            # Clear form
            self.name_input.clear()
            self.date_input.setDate(QDate.currentDate())
            self.desc_input.clear()
            
            # Reload list
            self._load_milestones()
            
            # Emit signal
            self.milestone_added.emit()
            
            QMessageBox.information(self, "Success", "Milestone added successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add milestone: {str(e)}")
    
    def _delete_milestone(self):
        """Delete selected milestone."""
        current_item = self.milestone_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a milestone to delete.")
            return
        
        milestone_id = current_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this milestone?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.database.delete_milestone(milestone_id)
                self._load_milestones()
                self.milestone_added.emit()
                QMessageBox.information(self, "Success", "Milestone deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete milestone: {str(e)}")
