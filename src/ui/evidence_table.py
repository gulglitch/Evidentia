"""
Evidence Table Module
Display evidence files in a table format with metadata
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal
from typing import List, Dict, Any
from datetime import datetime


class EvidenceTable(QWidget):
    """Table widget to display evidence files."""
    
    # Signals
    evidence_selected = Signal(int)  # evidence_id
    evidence_status_changed = Signal(int, str)  # evidence_id, new_status
    
    def __init__(self):
        super().__init__()
        self.evidence_data = []
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the table UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header with search and filters
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("Evidence Files")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #cdd6f4;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files...")
        self.search_input.setMaximumWidth(200)
        self.search_input.textChanged.connect(self._filter_table)
        header_layout.addWidget(self.search_input)
        
        # File type filter
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "PDF", "DOCX", "JPG", "PNG", "TXT", "Other"])
        self.type_filter.currentTextChanged.connect(self._filter_table)
        header_layout.addWidget(self.type_filter)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "File Name", "Type", "Size", "Modified Date", "Status", "Risk"
        ])
        
        # Configure headers
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(2, 60)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 70)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.cellClicked.connect(self._on_cell_clicked)
        
        layout.addWidget(self.table)
    
    def _apply_styles(self):
        """Apply table styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
            }
            QTableWidget {
                background-color: #181825;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 5px;
                gridline-color: #313244;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #313244;
            }
            QTableWidget::item:alternate {
                background-color: #1e1e2e;
            }
            QHeaderView::section {
                background-color: #181825;
                color: #89b4fa;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #313244;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
        """)
    
    def load_evidence(self, evidence_list: List[Dict[str, Any]]):
        """Load evidence data into the table."""
        self.evidence_data = evidence_list
        self._populate_table(evidence_list)
    
    def _populate_table(self, evidence_list: List[Dict[str, Any]]):
        """Populate the table with evidence data."""
        self.table.setRowCount(0)
        
        for evidence in evidence_list:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(evidence.get('id', ''))))
            
            # File name
            self.table.setItem(row, 1, QTableWidgetItem(evidence.get('file_name', '')))
            
            # Type (extension)
            ext = evidence.get('file_extension', '').upper().replace('.', '')
            self.table.setItem(row, 2, QTableWidgetItem(ext))
            
            # Size
            size = evidence.get('file_size', 0)
            size_str = self._format_size(size)
            self.table.setItem(row, 3, QTableWidgetItem(size_str))
            
            # Modified date
            modified = evidence.get('modified_time', '')
            if isinstance(modified, datetime):
                modified = modified.strftime('%Y-%m-%d %H:%M')
            self.table.setItem(row, 4, QTableWidgetItem(str(modified)))
            
            # Status
            status = evidence.get('status', 'Pending')
            status_item = QTableWidgetItem(status)
            status_item.setForeground(self._get_status_color(status))
            self.table.setItem(row, 5, status_item)
            
            # Risk
            risk = evidence.get('risk_level', 'Low')
            risk_item = QTableWidgetItem(risk)
            risk_item.setForeground(self._get_risk_color(risk))
            self.table.setItem(row, 6, risk_item)
    
    def _format_size(self, size: int) -> str:
        """Format file size in human readable format."""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def _get_status_color(self, status: str):
        """Get color for status text."""
        from PySide6.QtGui import QColor
        colors = {
            'Pending': QColor('#f9e2af'),
            'Analyzed': QColor('#a6e3a1'),
            'Flagged': QColor('#f38ba8'),
            'Archived': QColor('#6c7086'),
        }
        return colors.get(status, QColor('#cdd6f4'))
    
    def _get_risk_color(self, risk: str):
        """Get color for risk level."""
        from PySide6.QtGui import QColor
        colors = {
            'Low': QColor('#a6e3a1'),
            'Medium': QColor('#f9e2af'),
            'High': QColor('#f38ba8'),
        }
        return colors.get(risk, QColor('#cdd6f4'))
    
    def _filter_table(self):
        """Filter table based on search and type filter."""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        
        filtered = []
        for evidence in self.evidence_data:
            # Search filter
            if search_text and search_text not in evidence.get('file_name', '').lower():
                continue
            
            # Type filter
            if type_filter != "All Types":
                ext = evidence.get('file_extension', '').upper().replace('.', '')
                if type_filter == "Other":
                    if ext in ['PDF', 'DOCX', 'JPG', 'PNG', 'TXT']:
                        continue
                elif ext != type_filter:
                    continue
            
            filtered.append(evidence)
        
        self._populate_table(filtered)
    
    def _on_cell_clicked(self, row: int, column: int):
        """Handle cell click events."""
        id_item = self.table.item(row, 0)
        if id_item:
            evidence_id = int(id_item.text())
            self.evidence_selected.emit(evidence_id)
