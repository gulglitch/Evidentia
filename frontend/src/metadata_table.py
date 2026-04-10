"""
Metadata Table Screen
Displays a comprehensive table of all evidence files with their metadata
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QFrame, QCheckBox, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QCursor
from datetime import datetime
from typing import List, Dict, Any

from backend.app.database import Database
from frontend.src.notes_dialog import NotesDialog


class MetadataTable(QWidget):
    """Metadata table screen showing all evidence files."""
    
    back_requested = Signal()
    timeline_requested = Signal()
    
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
    
    def _add_status_controls(self, main_layout):
        """Add status filter checkboxes and bulk actions."""
        controls_frame = QFrame()
        controls_frame.setFrameShape(QFrame.StyledPanel)
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setSpacing(20)
        
        # Status filters
        status_label = QLabel("Status Filters:")
        status_label.setFont(QFont("Arial", 11, QFont.Bold))
        controls_layout.addWidget(status_label)
        
        self.pending_check = QCheckBox("Show Pending")
        self.pending_check.setChecked(True)
        self.pending_check.stateChanged.connect(self._apply_filters)
        controls_layout.addWidget(self.pending_check)
        
        self.analyzed_check = QCheckBox("Show Analyzed")
        self.analyzed_check.setChecked(True)
        self.analyzed_check.stateChanged.connect(self._apply_filters)
        controls_layout.addWidget(self.analyzed_check)
        
        self.flagged_check = QCheckBox("Show Flagged")
        self.flagged_check.setChecked(True)
        self.flagged_check.stateChanged.connect(self._apply_filters)
        controls_layout.addWidget(self.flagged_check)
        
        controls_layout.addSpacing(30)
        
        # Bulk actions
        bulk_label = QLabel("Bulk Actions:")
        bulk_label.setFont(QFont("Arial", 11, QFont.Bold))
        controls_layout.addWidget(bulk_label)
        
        self.bulk_combo = QComboBox()
        self.bulk_combo.addItems([
            "Select Action...",
            "Mark as Pending",
            "Mark as Analyzed",
            "Mark as Flagged"
        ])
        self.bulk_combo.setFixedWidth(180)
        self.bulk_combo.setMinimumHeight(35)
        self.bulk_combo.currentTextChanged.connect(self._on_bulk_action)
        controls_layout.addWidget(self.bulk_combo)
        
        controls_layout.addStretch()
        
        # Status statistics
        self.stats_widget = QLabel("")
        self.stats_widget.setFont(QFont("Arial", 11))
        self.stats_widget.setStyleSheet("color: #8899aa;")
        controls_layout.addWidget(self.stats_widget)
        
        main_layout.addWidget(controls_frame)
    
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
        
        header_layout.addSpacing(20)
        
        # Timeline button
        timeline_btn = QPushButton("View Timeline")
        timeline_btn.setFont(QFont("Arial", 12))
        timeline_btn.setFixedSize(140, 35)
        timeline_btn.clicked.connect(self.timeline_requested.emit)
        header_layout.addWidget(timeline_btn)
        
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
        
        # Status filter panel and bulk actions
        self._add_status_controls(main_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "☑", "ID", "File Name", "Type", "Size", "Created Date", "Modified Date", "Status", "Risk", "Notes"
        ])
        
        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Checkbox
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # ID
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # File Name
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Type
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Size
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Created
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # Modified
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # Status
        header.setSectionResizeMode(8, QHeaderView.Fixed)  # Risk
        header.setSectionResizeMode(9, QHeaderView.Fixed)  # Notes
        
        self.table.setColumnWidth(0, 40)   # Checkbox
        self.table.setColumnWidth(1, 60)   # ID
        self.table.setColumnWidth(3, 100)  # Type
        self.table.setColumnWidth(4, 100)  # Size
        self.table.setColumnWidth(5, 150)  # Created
        self.table.setColumnWidth(6, 150)  # Modified
        self.table.setColumnWidth(7, 100)  # Status
        self.table.setColumnWidth(8, 80)   # Risk
        self.table.setColumnWidth(9, 60)   # Notes
        
        # Connect cell click for status/risk changes
        self.table.cellClicked.connect(self._on_cell_clicked)
        
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
            
            # Checkbox
            checkbox = QCheckBox()
            checkbox.setStyleSheet("QCheckBox { margin-left: 10px; }")
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, checkbox_widget)
            
            # ID
            id_item = QTableWidgetItem(str(evidence.get('id', '')))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setData(Qt.UserRole, evidence)  # Store full evidence data
            self.table.setItem(row, 1, id_item)
            
            # File Name
            name_item = QTableWidgetItem(evidence.get('file_name', 'Unknown'))
            self.table.setItem(row, 2, name_item)
            
            # Type
            file_type = self._determine_type(evidence.get('file_extension', ''))
            type_item = QTableWidgetItem(file_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, type_item)
            
            # Size
            size = evidence.get('file_size', 0)
            size_item = QTableWidgetItem(self._format_size(size))
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            size_item.setData(Qt.UserRole, size)
            self.table.setItem(row, 4, size_item)
            
            # Created Date
            created = evidence.get('created_time', '')
            created_item = QTableWidgetItem(self._format_date(created))
            self.table.setItem(row, 5, created_item)
            
            # Modified Date
            modified = evidence.get('modified_time', '')
            modified_item = QTableWidgetItem(self._format_date(modified))
            self.table.setItem(row, 6, modified_item)
            
            # Status (clickable badge)
            status = evidence.get('status', 'Pending')
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setFont(QFont("Arial", 10, QFont.Bold))
            status_color = self._get_status_color(status)
            status_item.setForeground(QColor(status_color))
            status_item.setToolTip("Click to change status")
            self.table.setItem(row, 7, status_item)
            
            # Risk Level (clickable badge)
            risk = evidence.get('risk_level', 'Low')
            risk_item = QTableWidgetItem(risk)
            risk_item.setTextAlignment(Qt.AlignCenter)
            risk_item.setFont(QFont("Arial", 10, QFont.Bold))
            risk_color = self._get_risk_color(risk)
            risk_item.setForeground(QColor(risk_color))
            risk_item.setToolTip("Click to change risk level")
            self.table.setItem(row, 8, risk_item)
            
            # Notes icon
            notes = evidence.get('notes', '')
            notes_item = QTableWidgetItem("📝" if notes else "➕")
            notes_item.setTextAlignment(Qt.AlignCenter)
            notes_item.setFont(QFont("Arial", 14))
            notes_item.setToolTip("Click to add/edit notes" if not notes else f"Notes: {notes[:50]}...")
            if notes:
                notes_item.setForeground(QColor("#40e0d0"))
            self.table.setItem(row, 9, notes_item)
        
        self.table.setSortingEnabled(True)
        self.count_label.setText(f"{len(evidence_list)} files")
        
        # Update statistics
        self._update_status_statistics()
    
    def _apply_filters(self):
        """Apply search, type, and status filters."""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        
        # Get status filter states
        show_pending = self.pending_check.isChecked()
        show_analyzed = self.analyzed_check.isChecked()
        show_flagged = self.flagged_check.isChecked()
        
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
            
            # Check status filter
            status = evidence.get('status', 'Pending')
            if status == 'Pending' and not show_pending:
                continue
            if status == 'Analyzed' and not show_analyzed:
                continue
            if status == 'Flagged' and not show_flagged:
                continue
            
            filtered_evidence.append(evidence)
        
        self._populate_table(filtered_evidence)
        self._update_summary(filtered_evidence)
    
    def _clear_filters(self):
        """Clear all filters."""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.pending_check.setChecked(True)
        self.analyzed_check.setChecked(True)
        self.flagged_check.setChecked(True)
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
    
    def _on_cell_clicked(self, row: int, column: int):
        """Handle cell clicks for status, risk, and notes."""
        # Status column (7)
        if column == 7:
            self._change_status(row)
        # Risk column (8)
        elif column == 8:
            self._change_risk(row)
        # Notes column (9)
        elif column == 9:
            self._edit_notes(row)
    
    def _change_status(self, row: int):
        """Change status for a single evidence file."""
        id_item = self.table.item(row, 1)
        if not id_item:
            return
        
        evidence = id_item.data(Qt.UserRole)
        evidence_id = evidence.get('id')
        current_status = evidence.get('status', 'Pending')
        
        # Show context menu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 6px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                color: #e0e6ed;
            }
            QMenu::item:selected {
                background-color: #2a7a8a;
            }
        """)
        
        pending_action = menu.addAction("⚠ Pending")
        analyzed_action = menu.addAction("✓ Analyzed")
        flagged_action = menu.addAction("🚩 Flagged")
        
        action = menu.exec(QCursor.pos())
        
        new_status = None
        if action == pending_action:
            new_status = "Pending"
        elif action == analyzed_action:
            new_status = "Analyzed"
        elif action == flagged_action:
            new_status = "Flagged"
        
        if new_status and new_status != current_status:
            try:
                self.database.update_evidence_status(evidence_id, new_status)
                evidence['status'] = new_status
                
                # Update table cell
                status_item = self.table.item(row, 7)
                status_item.setText(new_status)
                status_color = self._get_status_color(new_status)
                status_item.setForeground(QColor(status_color))
                
                # Brief highlight
                status_item.setBackground(QColor("#40e0d0"))
                QTimer.singleShot(300, lambda: status_item.setBackground(QColor("transparent")))
                
                # Update statistics
                self._update_status_statistics()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update status: {str(e)}")
    
    def _change_risk(self, row: int):
        """Change risk level for a single evidence file."""
        id_item = self.table.item(row, 1)
        if not id_item:
            return
        
        evidence = id_item.data(Qt.UserRole)
        evidence_id = evidence.get('id')
        current_risk = evidence.get('risk_level', 'Low')
        
        # Show context menu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 6px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                color: #e0e6ed;
            }
            QMenu::item:selected {
                background-color: #2a7a8a;
            }
        """)
        
        low_action = menu.addAction("🟢 Low")
        medium_action = menu.addAction("🟡 Medium")
        high_action = menu.addAction("🔴 High")
        
        action = menu.exec(QCursor.pos())
        
        new_risk = None
        if action == low_action:
            new_risk = "Low"
        elif action == medium_action:
            new_risk = "Medium"
        elif action == high_action:
            new_risk = "High"
        
        if new_risk and new_risk != current_risk:
            try:
                self.database.update_evidence_risk(evidence_id, new_risk)
                evidence['risk_level'] = new_risk
                
                # Update table cell
                risk_item = self.table.item(row, 8)
                risk_item.setText(new_risk)
                risk_color = self._get_risk_color(new_risk)
                risk_item.setForeground(QColor(risk_color))
                
                # Brief highlight
                risk_item.setBackground(QColor("#40e0d0"))
                QTimer.singleShot(300, lambda: risk_item.setBackground(QColor("transparent")))
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update risk level: {str(e)}")
    
    def _edit_notes(self, row: int):
        """Edit notes for an evidence file."""
        id_item = self.table.item(row, 1)
        if not id_item:
            return
        
        evidence = id_item.data(Qt.UserRole)
        evidence_id = evidence.get('id')
        current_notes = evidence.get('notes', '')
        
        dialog = NotesDialog(evidence_id, current_notes, self)
        if dialog.exec():
            new_notes = dialog.get_notes()
            try:
                self.database.update_evidence_notes(evidence_id, new_notes)
                evidence['notes'] = new_notes
                
                # Update notes icon
                notes_item = self.table.item(row, 9)
                notes_item.setText("📝" if new_notes else "➕")
                notes_item.setToolTip("Click to add/edit notes" if not new_notes else f"Notes: {new_notes[:50]}...")
                if new_notes:
                    notes_item.setForeground(QColor("#40e0d0"))
                else:
                    notes_item.setForeground(QColor("#e0e6ed"))
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update notes: {str(e)}")
    
    def _on_bulk_action(self, action_text: str):
        """Handle bulk action selection."""
        if action_text == "Select Action...":
            return
        
        # Get selected rows
        selected_ids = []
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    id_item = self.table.item(row, 1)
                    if id_item:
                        evidence = id_item.data(Qt.UserRole)
                        selected_ids.append((evidence.get('id'), row))
        
        if not selected_ids:
            QMessageBox.warning(self, "No Selection", "Please select files using the checkboxes.")
            self.bulk_combo.setCurrentIndex(0)
            return
        
        # Determine new status
        new_status = None
        if "Pending" in action_text:
            new_status = "Pending"
        elif "Analyzed" in action_text:
            new_status = "Analyzed"
        elif "Flagged" in action_text:
            new_status = "Flagged"
        
        if not new_status:
            self.bulk_combo.setCurrentIndex(0)
            return
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirm Bulk Update",
            f"Update status to '{new_status}' for {len(selected_ids)} file(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Update database
                ids_only = [eid for eid, _ in selected_ids]
                self.database.bulk_update_status(ids_only, new_status)
                
                # Update table
                for evidence_id, row in selected_ids:
                    id_item = self.table.item(row, 1)
                    evidence = id_item.data(Qt.UserRole)
                    evidence['status'] = new_status
                    
                    status_item = self.table.item(row, 7)
                    status_item.setText(new_status)
                    status_color = self._get_status_color(new_status)
                    status_item.setForeground(QColor(status_color))
                    
                    # Uncheck checkbox
                    checkbox_widget = self.table.cellWidget(row, 0)
                    if checkbox_widget:
                        checkbox = checkbox_widget.findChild(QCheckBox)
                        if checkbox:
                            checkbox.setChecked(False)
                
                # Update statistics
                self._update_status_statistics()
                
                QMessageBox.information(self, "Success", f"Updated {len(selected_ids)} file(s) successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update status: {str(e)}")
        
        self.bulk_combo.setCurrentIndex(0)
    
    def _update_status_statistics(self):
        """Update status statistics display."""
        if not self.case_id:
            return
        
        try:
            stats = self.database.get_status_statistics(self.case_id)
            pending = stats.get('Pending', 0)
            analyzed = stats.get('Analyzed', 0)
            flagged = stats.get('Flagged', 0)
            total = pending + analyzed + flagged
            
            if total > 0:
                analyzed_pct = int((analyzed / total) * 100)
                self.stats_widget.setText(
                    f"📊 Pending: {pending} | Analyzed: {analyzed} | Flagged: {flagged} | "
                    f"Progress: {analyzed_pct}% Complete"
                )
            else:
                self.stats_widget.setText("📊 No evidence files")
        except Exception as e:
            self.stats_widget.setText("📊 Statistics unavailable")
    
    def _get_status_color(self, status: str) -> str:
        """Get color for status badge."""
        colors = {
            'Pending': '#f59e0b',
            'Analyzed': '#10b981',
            'Flagged': '#ef4444',
        }
        return colors.get(status, '#6b7280')
    
    def _get_risk_color(self, risk: str) -> str:
        """Get color for risk level badge."""
        colors = {
            'Low': '#10b981',
            'Medium': '#f59e0b',
            'High': '#ef4444',
        }
        return colors.get(risk, '#6b7280')
