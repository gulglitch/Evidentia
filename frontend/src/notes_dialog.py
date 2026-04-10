"""
Notes Dialog
Dialog for adding/editing notes for evidence files
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class NotesDialog(QDialog):
    """Dialog for editing evidence notes."""
    
    def __init__(self, evidence_id: int, current_notes: str = "", parent=None):
        super().__init__(parent)
        self.evidence_id = evidence_id
        self.current_notes = current_notes
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Evidence Notes")
        self.setMinimumSize(500, 400)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel(f"Notes for Evidence #{self.evidence_id}")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #00d4aa;")
        main_layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Add notes to document important findings, observations, or flags:")
        instructions.setFont(QFont("Arial", 11))
        instructions.setStyleSheet("color: #8899aa;")
        instructions.setWordWrap(True)
        main_layout.addWidget(instructions)
        
        # Notes text area
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText(
            "Enter your notes here...\n\n"
            "Examples:\n"
            "- Suspicious file activity detected\n"
            "- Contains sensitive information\n"
            "- Requires further investigation\n"
            "- Related to case #XYZ"
        )
        self.notes_edit.setPlainText(self.current_notes)
        self.notes_edit.setFont(QFont("Arial", 11))
        main_layout.addWidget(self.notes_edit)
        
        # Character count
        self.char_count_label = QLabel(f"Characters: {len(self.current_notes)}/500")
        self.char_count_label.setFont(QFont("Arial", 10))
        self.char_count_label.setStyleSheet("color: #8899aa;")
        self.notes_edit.textChanged.connect(self._update_char_count)
        main_layout.addWidget(self.char_count_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Notes")
        save_btn.setFixedSize(120, 40)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
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
            QTextEdit {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 6px;
                padding: 10px;
                color: #e0e6ed;
                font-size: 12px;
            }
            QTextEdit:focus {
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
        """)
    
    def _update_char_count(self):
        """Update character count label."""
        text = self.notes_edit.toPlainText()
        count = len(text)
        self.char_count_label.setText(f"Characters: {count}/500")
        
        if count > 500:
            self.char_count_label.setStyleSheet("color: #ef4444;")
        else:
            self.char_count_label.setStyleSheet("color: #8899aa;")
    
    def get_notes(self) -> str:
        """Get the notes text (limited to 500 characters)."""
        text = self.notes_edit.toPlainText()
        return text[:500]  # Enforce 500 character limit
