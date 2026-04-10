"""
Evidence Details Dialog
Shows detailed information about a selected evidence file
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtCore import QUrl
from typing import Dict, Any
from datetime import datetime
import os
import subprocess
import platform


class EvidenceDetailsDialog(QDialog):
    """Dialog showing evidence file details."""
    
    view_in_table_requested = Signal(int)  # Emits evidence ID
    
    def __init__(self, evidence: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.evidence = evidence
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Evidence Details")
        self.setMinimumSize(600, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel(self.evidence.get('file_name', 'Unknown File'))
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #00d4aa;")
        title.setWordWrap(True)
        main_layout.addWidget(title)
        
        # Details grid
        details_frame = QFrame()
        details_frame.setFrameShape(QFrame.StyledPanel)
        details_layout = QGridLayout(details_frame)
        details_layout.setSpacing(15)
        details_layout.setContentsMargins(20, 20, 20, 20)
        
        row = 0
        
        # File ID
        self._add_detail_row(details_layout, row, "Evidence ID:", 
                            str(self.evidence.get('id', 'N/A')))
        row += 1
        
        # File path
        self._add_detail_row(details_layout, row, "File Path:", 
                            self.evidence.get('file_path', 'N/A'))
        row += 1
        
        # File type
        self._add_detail_row(details_layout, row, "File Type:", 
                            self.evidence.get('file_extension', 'N/A').upper())
        row += 1
        
        # File size
        size = self.evidence.get('file_size', 0)
        self._add_detail_row(details_layout, row, "File Size:", 
                            self._format_size(size))
        row += 1
        
        # Created time
        created = self.evidence.get('created_time', 'N/A')
        self._add_detail_row(details_layout, row, "Created:", 
                            self._format_date(created))
        row += 1
        
        # Modified time
        modified = self.evidence.get('modified_time', 'N/A')
        self._add_detail_row(details_layout, row, "Modified:", 
                            self._format_date(modified))
        row += 1
        
        # Status
        status = self.evidence.get('status', 'Pending')
        status_color = self._get_status_color(status)
        status_label = QLabel(status)
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold; font-size: 13px;")
        self._add_detail_row(details_layout, row, "Status:", status_label)
        row += 1
        
        # Risk level
        risk = self.evidence.get('risk_level', 'Low')
        risk_color = self._get_risk_color(risk)
        risk_label = QLabel(risk)
        risk_label.setStyleSheet(f"color: {risk_color}; font-weight: bold; font-size: 13px;")
        self._add_detail_row(details_layout, row, "Risk Level:", risk_label)
        row += 1
        
        # Added at
        added = self.evidence.get('added_at', 'N/A')
        self._add_detail_row(details_layout, row, "Added to Case:", 
                            self._format_date(added))
        row += 1
        
        main_layout.addWidget(details_frame)
        
        # Notes section
        notes_label = QLabel("Notes:")
        notes_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(notes_label)
        
        self.notes_display = QTextEdit()
        self.notes_display.setReadOnly(True)
        self.notes_display.setMaximumHeight(120)
        notes_text = self.evidence.get('notes', 'No notes available.')
        self.notes_display.setPlainText(notes_text if notes_text else 'No notes available.')
        main_layout.addWidget(self.notes_display)
        
        # Metadata section
        metadata_label = QLabel("Metadata:")
        metadata_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(metadata_label)
        
        self.metadata_display = QTextEdit()
        self.metadata_display.setReadOnly(True)
        self.metadata_display.setMaximumHeight(100)
        self.metadata_display.setFont(QFont("Courier New", 9))
        metadata_text = self.evidence.get('metadata', 'No metadata available.')
        self.metadata_display.setPlainText(metadata_text if metadata_text else 'No metadata available.')
        main_layout.addWidget(self.metadata_display)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        # Open file location button
        open_location_btn = QPushButton("📁 Open File Location")
        open_location_btn.setFixedHeight(40)
        open_location_btn.clicked.connect(self._open_file_location)
        action_layout.addWidget(open_location_btn)
        
        # View in table button
        view_table_btn = QPushButton("📊 View in Table")
        view_table_btn.setFixedHeight(40)
        view_table_btn.clicked.connect(self._view_in_table)
        action_layout.addWidget(view_table_btn)
        
        main_layout.addLayout(action_layout)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(120, 40)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
    
    def _add_detail_row(self, layout: QGridLayout, row: int, label_text: str, value):
        """Add a detail row to the grid."""
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 11, QFont.Bold))
        label.setStyleSheet("color: #8899aa;")
        layout.addWidget(label, row, 0, Qt.AlignTop)
        
        if isinstance(value, str):
            value_label = QLabel(value)
            value_label.setFont(QFont("Arial", 11))
            value_label.setWordWrap(True)
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(value_label, row, 1)
        else:
            layout.addWidget(value, row, 1)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _format_date(self, date_str: str) -> str:
        """Format date string."""
        if not date_str or date_str == 'N/A':
            return 'N/A'
        
        try:
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(date_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return date_str
    
    def _get_status_color(self, status: str) -> str:
        """Get color for status."""
        colors = {
            'Pending': '#f59e0b',
            'Analyzed': '#10b981',
            'Flagged': '#ef4444',
        }
        return colors.get(status, '#6b7280')
    
    def _get_risk_color(self, risk: str) -> str:
        """Get color for risk level."""
        colors = {
            'Low': '#10b981',
            'Medium': '#f59e0b',
            'High': '#ef4444',
        }
        return colors.get(risk, '#6b7280')
    
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
            QFrame {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
            }
            QTextEdit {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 6px;
                padding: 10px;
                color: #e0e6ed;
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
    
    def _open_file_location(self):
        """Open the file location in system file explorer."""
        file_path = self.evidence.get('file_path', '')
        
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(
                self,
                "File Not Found",
                "The file location could not be found. The file may have been moved or deleted."
            )
            return
        
        try:
            # Get the directory containing the file
            directory = os.path.dirname(os.path.abspath(file_path))
            
            # Open file explorer based on platform
            system = platform.system()
            if system == 'Windows':
                # Open explorer and select the file
                subprocess.run(['explorer', '/select,', os.path.normpath(file_path)])
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', '-R', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', directory])
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open file location: {str(e)}"
            )
    
    def _view_in_table(self):
        """Emit signal to view this evidence in the metadata table."""
        evidence_id = self.evidence.get('id')
        if evidence_id:
            self.view_in_table_requested.emit(evidence_id)
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Error",
                "Cannot locate this evidence in the table."
            )