"""
Notes Dialog
Dialog for adding/editing notes for flagged evidence
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from backend.app.database import Database


class NotesDialog(QDialog):
    """Dialog for editing evidence notes."""
    
    notes_saved = Signal(int, str)  # evidence_id, notes
    
    def __init__(self, evidence_id: int, current_notes: str = "", parent=None):
        super().__init__(parent)
        self.evidence_id = evidence_id
        self.database = Database()
        self.setWindowTitle("Evidence Notes")
        self.setMinimumSize(500, 400)
        self._setup_ui()
        self._apply_styles()
        
        # Load existing notes
        if current_notes:
            self.notes_text.setPlainText(current_notes)
            self._update_char_count()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Add Notes for Flagged Evidence")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #00d4aa;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Add notes to document why this evidence is flagged:")
        instructions.setFont(QFont("Arial", 11))
        instructions.setStyleSheet("color: #8899aa;")
        layout.addWidget(instructions)
        
        # Text area
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Enter your notes here...")
        self.notes_text.setFont(QFont("Arial", 12))
        self.notes_text.textChanged.connect(self._update_char_count)
        layout.addWidget(self.notes_text)
        
        # Character counter
        self.char_count_label = QLabel("0 / 500 characters")
        self.char_count_label.setFont(QFont("Arial", 10))
        self.char_count_label.setStyleSheet("color: #8899aa;")
        self.char_count_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.char_count_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.save_btn = QPushButton("Save Notes")
        self.save_btn.setFixedSize(120, 35)
        self.save_btn.clicked.connect(self._save_notes)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def _apply_styles(self):
        """Apply dialog styles."""
        self.setStyleSheet("""
            QDialog {
                background-color: #0a1929;
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
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
        """)
    
    def _update_char_count(self):
        """Update character count label."""
        text = self.notes_text.toPlainText()
        char_count = len(text)
        self.char_count_label.setText(f"{char_count} / 500 characters")
        
        # Change color if over limit
        if char_count > 500:
            self.char_count_label.setStyleSheet("color: #ef4444;")  # Red
            self.save_btn.setEnabled(False)
        else:
            self.char_count_label.setStyleSheet("color: #8899aa;")
            self.save_btn.setEnabled(True)
    
    def _save_notes(self):
        """Save notes to database."""
        notes = self.notes_text.toPlainText().strip()
        
        # Validate length
        if len(notes) > 500:
            return
        
        # Save to database
        self.database.update_evidence_notes(self.evidence_id, notes)
        
        # Emit signal
        self.notes_saved.emit(self.evidence_id, notes)
        
        # Close dialog
        self.accept()
    
    def get_notes(self) -> str:
        """Get the notes text."""
        return self.notes_text.toPlainText().strip()
