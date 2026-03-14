"""
Evidence Management Module
Main workspace for case evidence with drag-drop upload and metadata table
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QRadioButton, QButtonGroup, QScrollArea, QProgressBar,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent
from typing import List, Dict, Any
from datetime import datetime
import os

from ..core.database import Database
from ..core.file_scanner import FileScanner
from ..core.metadata_extractor import MetadataExtractor


class FileProcessingThread(QThread):
    """Thread for processing files in background."""
    
    progress_updated = Signal(int, str)  # progress, current_file
    file_processed = Signal(dict)  # file_data
    finished_processing = Signal(int)  # total_files
    
    def __init__(self, folder_path: str, case_id: int):
        super().__init__()
        self.folder_path = folder_path
        self.case_id = case_id
        self.scanner = FileScanner()
        self.extractor = MetadataExtractor()
        self.database = Database()
    
    def run(self):
        """Process files in the background."""
        try:
            files = self.scanner.scan_directory(self.folder_path)
            total_files = len(files)
            
            for i, file_info in enumerate(files):
                # Update progress
                progress = int((i / total_files) * 100)
                self.progress_updated.emit(progress, file_info.name)
                
                # Extract metadata
                if self.extractor.is_supported(file_info.path):
                    metadata = self.extractor.extract(file_info.path)
                else:
                    metadata = {
                        'file_name': file_info.name,
                        'file_path': file_info.path,
                        'file_extension': file_info.extension,
                        'file_size': file_info.size,
                        'created_time': file_info.created,
                        'modified_time': file_info.modified,
                    }
                
                # Add to database
                evidence_id = self.database.add_evidence(self.case_id, metadata)
                metadata['id'] = evidence_id
                
                # Emit processed file
                self.file_processed.emit(metadata)
            
            # Log activity
            self.database.log_activity(
                self.case_id,
                "Evidence Imported",
                f"Imported {total_files} files from {self.folder_path}"
            )
            
            self.finished_processing.emit(total_files)
            
        except Exception as e:
            self.progress_updated.emit(0, f"Error: {str(e)}")


class SidebarFilter(QFrame):
    """Sidebar filter panel."""
    
    filter_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the sidebar filter UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # File Type section
        file_type_label = QLabel("File Type")
        file_type_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(file_type_label)
        
        self.file_type_checkboxes = {}
        file_types = ["PDF", "Image", "ZIP", "Email"]
        for file_type in file_types:
            checkbox = QCheckBox(file_type)
            checkbox.setFont(QFont("Arial", 14))
            checkbox.stateChanged.connect(self.filter_changed.emit)
            self.file_type_checkboxes[file_type] = checkbox
            layout.addWidget(checkbox)
        
        layout.addSpacing(20)
        
        # Upload Date section
        upload_date_label = QLabel("Upload Date")
        upload_date_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(upload_date_label)
        
        self.date_group = QButtonGroup()
        date_options = ["Last 24 hours", "Last week", "Last month"]
        self.date_radios = {}
        for option in date_options:
            radio = QRadioButton(option)
            radio.setFont(QFont("Arial", 14))
            radio.toggled.connect(self.filter_changed.emit)
            self.date_group.addButton(radio)
            self.date_radios[option] = radio
            layout.addWidget(radio)
        
        layout.addSpacing(20)
        
        # Status section
        status_label = QLabel("Status")
        status_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(status_label)
        
        self.status_checkboxes = {}
        statuses = ["Analyzed", "Pending", "Flagged"]
        for status in statuses:
            checkbox = QCheckBox(status)
            checkbox.setFont(QFont("Arial", 14))
            checkbox.stateChanged.connect(self.filter_changed.emit)
            self.status_checkboxes[status] = checkbox
            layout.addWidget(checkbox)
        
        layout.addStretch()
    
    def _apply_styles(self):
        """Apply sidebar styles."""
        self.setStyleSheet("""
            QFrame {
                background-color: #122a3a;
                border-right: 1px solid #1a4a5a;
            }
            QLabel {
                color: #00d4aa;
                font-weight: bold;
            }
            QCheckBox, QRadioButton {
                color: #e0e6ed;
                spacing: 10px;
                padding: 5px;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #2a6a7a;
                border-radius: 4px;
                background-color: #0d2137;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background-color: #40e0d0;
                border-color: #40e0d0;
            }
            QRadioButton::indicator {
                border-radius: 9px;
            }
        """)
    
    def get_active_filters(self) -> Dict[str, Any]:
        """Get currently active filters."""
        filters = {
            'file_types': [],
            'date_range': None,
            'statuses': []
        }
        
        # File types
        for file_type, checkbox in self.file_type_checkboxes.items():
            if checkbox.isChecked():
                filters['file_types'].append(file_type)
        
        # Date range
        for option, radio in self.date_radios.items():
            if radio.isChecked():
                filters['date_range'] = option
                break
        
        # Statuses
        for status, checkbox in self.status_checkboxes.items():
            if checkbox.isChecked():
                filters['statuses'].append(status)
        
        return filters


class UploadZone(QFrame):
    """Drag and drop upload zone."""
    
    files_dropped = Signal(str)  # folder_path
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the upload zone UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Upload icon (using text for now)
        icon_label = QLabel("+")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("Arial", 64, QFont.Bold))
        layout.addWidget(icon_label)
        
        # Upload text
        text_label = QLabel("Upload File Here")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(text_label)
        
        # Instruction text
        instruction_label = QLabel("Drag and drop a folder or click to browse")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setFont(QFont("Arial", 14))
        layout.addWidget(instruction_label)
    
    def _apply_styles(self):
        """Apply upload zone styles."""
        self.setStyleSheet("""
            QFrame {
                background-color: #0d2137;
                border: 2px dashed #1a4a5a;
                border-radius: 8px;
                min-height: 150px;
            }
            QFrame:hover {
                border-color: #40e0d0;
                background-color: #122a3a;
            }
            QLabel {
                color: #8899aa;
            }
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(self.styleSheet() + """
                QFrame {
                    border-color: #40e0d0 !important;
                    background-color: #122a3a !important;
                }
            """)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave events."""
        self._apply_styles()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events."""
        self._apply_styles()
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.files_dropped.emit(path)
                break
    
    def mousePressEvent(self, event):
        """Handle mouse press for manual folder selection."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Evidence Folder",
            "",
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.files_dropped.emit(folder)


class EvidenceManagement(QWidget):
    """Evidence Management main screen."""
    
    def __init__(self, case_id: int = None):
        super().__init__()
        self.case_id = case_id
        self.database = Database()
        self.evidence_data = []
        self._setup_ui()
        self._apply_styles()
        self._load_evidence()
    
    def _setup_ui(self):
        """Setup the evidence management UI."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = SidebarFilter()
        self.sidebar.setFixedWidth(280)
        self.sidebar.filter_changed.connect(self._apply_filters)
        main_layout.addWidget(self.sidebar)
        
        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        
        title = QLabel("Evidence Management")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        header_layout.addWidget(title)
        
        subtitle = QLabel("Explore detailed metadata information for files...")
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setStyleSheet("color: #8899aa;")
        header_layout.addWidget(subtitle)
        
        content_layout.addLayout(header_layout)
        
        # Metadata table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "File Name", "Type", "Date", "Status"
        ])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 180)
        self.table.setColumnWidth(4, 120)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(400)
        
        content_layout.addWidget(self.table)
        
        # Upload zone
        self.upload_zone = UploadZone()
        self.upload_zone.setMinimumHeight(200)
        self.upload_zone.files_dropped.connect(self._handle_folder_drop)
        content_layout.addWidget(self.upload_zone)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        content_layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel()
        self.progress_label.setVisible(False)
        content_layout.addWidget(self.progress_label)
        
        main_layout.addWidget(content_widget)
    
    def _apply_styles(self):
        """Apply evidence management styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QLabel {
                color: #00d4aa;
            }
            QTableWidget {
                background-color: #0d2137;
                border: 1px solid #1a4a5a;
                border-radius: 5px;
                gridline-color: #1a4a5a;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #1a4a5a;
            }
            QTableWidget::item:selected {
                background-color: #163545;
            }
            QTableWidget::item:alternate {
                background-color: #122a3a;
            }
            QHeaderView::section {
                background-color: #122a3a;
                color: #00d4aa;
                padding: 15px;
                border: none;
                border-bottom: 2px solid #1a4a5a;
                font-weight: bold;
                font-size: 14px;
            }
            QProgressBar {
                border: 2px solid #1a4a5a;
                border-radius: 5px;
                text-align: center;
                background-color: #0d2137;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #40e0d0;
                border-radius: 3px;
            }
        """)
    
    def _load_evidence(self):
        """Load evidence data from database."""
        if self.case_id:
            self.evidence_data = self.database.get_evidence_for_case(self.case_id)
            self._populate_table(self.evidence_data)
    
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
            
            # Date
            modified = evidence.get('modified_time', '')
            if isinstance(modified, datetime):
                modified = modified.strftime('%Y-%m-%d %H:%M')
            elif isinstance(modified, str) and modified:
                try:
                    # Try to parse string datetime
                    dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                    modified = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            self.table.setItem(row, 3, QTableWidgetItem(str(modified)))
            
            # Status
            status = evidence.get('status', 'Pending')
            self.table.setItem(row, 4, QTableWidgetItem(status))
    
    def _apply_filters(self):
        """Apply sidebar filters to the table."""
        filters = self.sidebar.get_active_filters()
        
        # If no filters are active, show all data
        if not any([filters['file_types'], filters['date_range'], filters['statuses']]):
            self._populate_table(self.evidence_data)
            return
        
        # Filter the data
        filtered_data = []
        for evidence in self.evidence_data:
            # File type filter
            if filters['file_types']:
                ext = evidence.get('file_extension', '').upper().replace('.', '')
                if ext not in filters['file_types']:
                    continue
            
            # Status filter
            if filters['statuses']:
                status = evidence.get('status', 'Pending')
                if status not in filters['statuses']:
                    continue
            
            # Date filter (simplified - just check if we have a date)
            if filters['date_range']:
                # For now, just include all files if date filter is active
                pass
            
            filtered_data.append(evidence)
        
        self._populate_table(filtered_data)
    
    def _handle_folder_drop(self, folder_path: str):
        """Handle folder drop for bulk upload."""
        if not self.case_id:
            QMessageBox.warning(
                self,
                "No Case Selected",
                "Please create or select a case before importing evidence."
            )
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting import...")
        
        # Start processing thread
        self.processing_thread = FileProcessingThread(folder_path, self.case_id)
        self.processing_thread.progress_updated.connect(self._update_progress)
        self.processing_thread.file_processed.connect(self._add_evidence_to_table)
        self.processing_thread.finished_processing.connect(self._import_finished)
        self.processing_thread.start()
    
    def _update_progress(self, progress: int, current_file: str):
        """Update progress bar and label."""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Processing: {current_file}")
    
    def _add_evidence_to_table(self, evidence_data: Dict[str, Any]):
        """Add a single evidence item to the table."""
        self.evidence_data.append(evidence_data)
        # Refresh table to show new item
        self._populate_table(self.evidence_data)
    
    def _import_finished(self, total_files: int):
        """Handle import completion."""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        QMessageBox.information(
            self,
            "Import Complete",
            f"Successfully imported {total_files} evidence files."
        )
    
    def set_case_id(self, case_id: int):
        """Set the current case ID and reload evidence."""
        self.case_id = case_id
        self._load_evidence()