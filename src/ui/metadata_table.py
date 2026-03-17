"""
Metadata Table Screen
Displays a comprehensive table of all evidence files with their metadata
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from datetime import datetime
from typing import List, Dict, Any

from ..core.database import Database


class MetadataTable(QWidget):
    """Metadata table screen showing all evidence files."""
    
    back_requested = Signal()
    
    def __init__(self, case_id: int = None):
        super().__init__()
        self.case_id = case_id
        self.database = Database()
        self.all_evidence = []
        self._setup_ui()
        self._apply_styles()
        if case_id:
            self.load_evidence()
    
    def set_case_id(self, case_id: int):
        """Set the current case ID and reload evidence."""
        self.case_id = case_id
        self.load_evidence()
    
    def _setup_ui(self):
        """Setup the metadata table UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("‹ Back")
        back_btn.setFont(QFont("Arial", 12))
        back_btn.setFixedSize(100, 35)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8899aa;
                border: 2px solid #1a4a5a;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #122a3a;
                border-color: #40e0d0;
                color: #e0e6ed;
            }
        """)
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)
        
        header_layout.addStretch()
        
        # Title
        self.title_label = QLabel("Evidence Metadata Table")
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.title_label.setStyleSheet("color: #00d4aa;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # File count
        self.count_label = QLabel("0 files")
        self.count_label.setFont(QFont("Arial", 12))
        self.count_label.setStyleSheet("color: #8899aa;")
        header_layout.addWidget(self.count_label)
        
        main_layout.addLayout(header_layout)
        
        # Filter and search bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)
        
        # Search box
        search_label = QLabel("Search:")
        search_label.setFont(QFont("Arial", 12))
        search_label.setStyleSheet("color: #e0e6ed;")
        filter_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by filename...")
        self.search_input.setFixedWidth(300)
        self.search_input.setMinimumHeight(35)
        self.search_input.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addSpacing(20)
        
        # File type filter
        type_label = QLabel("Type:")
        type_label.setFont(QFont("Arial", 12))
        type_label.setStyleSheet("color: #e0e6ed;")
        filter_layout.addWidget(type_label)
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "Document", "Image", "Video", "Archive", "Other"])
        self.type_filter.setFixedWidth(150)
        self.type_filter.setMinimumHeight(35)
        self.type_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addStretch()
        
        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.setFont(QFont("Arial", 11))
        clear_btn.setFixedSize(120, 35)
        clear_btn.clicked.connect(self._clear_filters)
        filter_layout.addWidget(clear_btn)
        
        main_layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "File Name", "Type", "Size", "Created Date", "Modified Date", "Hash"
        ])
        
        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # File Name
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Type
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Size
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Created
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Modified
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Hash
        
        self.table.setColumnWidth(0, 60)   # ID
        self.table.setColumnWidth(2, 100)  # Type
        self.table.setColumnWidth(3, 100)  # Size
        self.table.setColumnWidth(4, 180)  # Created
        self.table.setColumnWidth(5, 180)  # Modified
        
        main_layout.addWidget(self.table)
        
        # Summary bar
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(30)
        
        self.total_size_label = QLabel("Total Size: 0 B")
        self.total_size_label.setFont(QFont("Arial", 12))
        self.total_size_label.setStyleSheet("color: #8899aa;")
        summary_layout.addWidget(self.total_size_label)
        
        self.type_breakdown_label = QLabel("Documents: 0 | Images: 0 | Videos: 0 | Other: 0")
        self.type_breakdown_label.setFont(QFont("Arial", 12))
        self.type_breakdown_label.setStyleSheet("color: #8899aa;")
        summary_layout.addWidget(self.type_breakdown_label)
        
        summary_layout.addStretch()
        
        main_layout.addLayout(summary_layout)
    
    def _apply_styles(self):
        """Apply table styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QLineEdit, QComboBox {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e6ed;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #40e0d0;
                background-color: #122a3a;
            }
            QLineEdit::placeholder {
                color: #6c7086;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #8899aa;
                margin-right: 5px;
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
            QTableWidget {
                background-color: #0d2137;
                border: 1px solid #1a4a5a;
                border-radius: 8px;
                gridline-color: #1a4a5a;
            }
            QTableWidget::item {
                padding: 8px;
                color: #e0e6ed;
            }
            QTableWidget::item:selected {
                background-color: #2a7a8a;
                color: #ffffff;
            }
            QTableWidget::item:alternate {
                background-color: #0f1f2f;
            }
            QHeaderView::section {
                background-color: #122a3a;
                color: #00d4aa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #1a4a5a;
                font-weight: bold;
                font-size: 13px;
            }
            QHeaderView::section:hover {
                background-color: #1a3a4a;
            }
            QScrollBar:vertical {
                background-color: #0d2137;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #2a7a8a;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #40e0d0;
            }
            QScrollBar:horizontal {
                background-color: #0d2137;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #2a7a8a;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #40e0d0;
            }
        """)
    
    def load_evidence(self):
        """Load evidence from database for the current case."""
        if not self.case_id:
            return
        
        # Get case info
        case = self.database.get_case(self.case_id)
        if case:
            self.title_label.setText(f"Evidence Metadata - {case['name']}")
        
        # Get all evidence
        self.all_evidence = self.database.get_evidence_for_case(self.case_id)
        self._populate_table(self.all_evidence)
        self._update_summary()
    
    def _populate_table(self, evidence_list: List[Dict[str, Any]]):
        """Populate the table with evidence data."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        
        for evidence in evidence_list:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(evidence.get('id', '')))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, id_item)
            
            # File Name
            name_item = QTableWidgetItem(evidence.get('file_name', 'Unknown'))
            self.table.setItem(row, 1, name_item)
            
            # Type
            file_type = self._determine_type(evidence.get('file_extension', ''))
            type_item = QTableWidgetItem(file_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, type_item)
            
            # Size
            size = evidence.get('file_size', 0)
            size_item = QTableWidgetItem(self._format_size(size))
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            size_item.setData(Qt.UserRole, size)  # Store raw size for sorting
            self.table.setItem(row, 3, size_item)
            
            # Created Date
            created = evidence.get('created_time', '')
            created_item = QTableWidgetItem(self._format_date(created))
            self.table.setItem(row, 4, created_item)
            
            # Modified Date
            modified = evidence.get('modified_time', '')
            modified_item = QTableWidgetItem(self._format_date(modified))
            self.table.setItem(row, 5, modified_item)
            
            # Hash
            metadata = evidence.get('metadata', '')
            hash_item = QTableWidgetItem(metadata if metadata else 'N/A')
            hash_item.setFont(QFont("Courier New", 9))
            self.table.setItem(row, 6, hash_item)
        
        self.table.setSortingEnabled(True)
        self.count_label.setText(f"{len(evidence_list)} files")
    
    def _apply_filters(self):
        """Apply search and type filters."""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        
        filtered_evidence = []
        for evidence in self.all_evidence:
            # Check search filter
            file_name = evidence.get('file_name', '').lower()
            if search_text and search_text not in file_name:
                continue
            
            # Check type filter
            if type_filter != "All Types":
                file_type = self._determine_type(evidence.get('file_extension', ''))
                if file_type != type_filter:
                    continue
            
            filtered_evidence.append(evidence)
        
        self._populate_table(filtered_evidence)
        self._update_summary(filtered_evidence)
    
    def _clear_filters(self):
        """Clear all filters."""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self._populate_table(self.all_evidence)
        self._update_summary()
    
    def _update_summary(self, evidence_list: List[Dict[str, Any]] = None):
        """Update summary statistics."""
        if evidence_list is None:
            evidence_list = self.all_evidence
        
        # Calculate total size
        total_size = sum(e.get('file_size', 0) for e in evidence_list)
        self.total_size_label.setText(f"Total Size: {self._format_size(total_size)}")
        
        # Count by type
        type_counts = {'Document': 0, 'Image': 0, 'Video': 0, 'Archive': 0, 'Other': 0}
        for evidence in evidence_list:
            file_type = self._determine_type(evidence.get('file_extension', ''))
            if file_type in type_counts:
                type_counts[file_type] += 1
        
        self.type_breakdown_label.setText(
            f"Documents: {type_counts['Document']} | "
            f"Images: {type_counts['Image']} | "
            f"Videos: {type_counts['Video']} | "
            f"Archives: {type_counts['Archive']} | "
            f"Other: {type_counts['Other']}"
        )
    
    def _determine_type(self, extension: str) -> str:
        """Determine file type from extension."""
        ext = extension.lower()
        
        doc_exts = ['.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt']
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.svg']
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        archive_exts = ['.zip', '.rar', '.7z', '.tar', '.gz']
        
        if ext in doc_exts:
            return 'Document'
        elif ext in image_exts:
            return 'Image'
        elif ext in video_exts:
            return 'Video'
        elif ext in archive_exts:
            return 'Archive'
        else:
            return 'Other'
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _format_date(self, date_str: str) -> str:
        """Format date string or return 'Unknown' if missing."""
        if not date_str or date_str == '':
            return 'Unknown'
        
        try:
            # Try parsing ISO format
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(date_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            # If parsing fails, return as-is or Unknown
            return date_str if date_str else 'Unknown'
