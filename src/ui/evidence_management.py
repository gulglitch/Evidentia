"""
Evidence Management Module
Main workspace for case evidence with drag-drop upload, metadata table,
and an empty-state big upload screen.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QRadioButton, QButtonGroup, QScrollArea, QProgressBar,
    QMessageBox, QFileDialog, QPushButton, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent, QColor
from typing import List, Dict, Any
from datetime import datetime, timedelta
import os

from ..core.database import Database
from ..core.file_scanner import FileScanner
from ..core.metadata_extractor import MetadataExtractor

# ──────────────────────────────────────────────────
# File type filter mapping
# Maps sidebar checkbox labels to actual file extensions
# ──────────────────────────────────────────────────
FILE_TYPE_MAPPING = {
    'PDF': ['.pdf'],
    'Document': ['.docx', '.doc', '.txt', '.rtf'],
    'Image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    'Spreadsheet': ['.xlsx', '.xls', '.csv'],
    'ZIP': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Email': ['.eml', '.msg'],
}

class FileProcessingThread(QThread):
    """Thread for processing files in background."""
    
    progress_updated = Signal(int, int, str)  # current_count, total_count, current_file
    file_processed = Signal(dict)  # file_data
    finished_processing = Signal(int)  # total_files
    error_occurred = Signal(str)  # error_message
    
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
            
            if total_files == 0:
                self.error_occurred.emit("No supported files found in the selected folder.")
                return
            
            for i, file_info in enumerate(files):
                # Update progress with count info
                self.progress_updated.emit(i + 1, total_files, file_info.name)
                
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
                metadata['status'] = 'Pending'
                metadata['risk_level'] = 'Low'
                
                # Emit processed file
                self.file_processed.emit(metadata)
            
            # Log activity
            self.database.log_activity(
                self.case_id,
                "Evidence Imported",
                f"Imported {total_files} files from {os.path.basename(self.folder_path)}"
            )
            
            self.finished_processing.emit(total_files)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class SidebarFilter(QFrame):
    """Sidebar filter panel matching the prototype design."""
    
    filter_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # File Type section
        file_type_label = QLabel("File Type")
        file_type_label.setFont(QFont("Arial", 15, QFont.Bold))
        layout.addWidget(file_type_label)
        
        self.file_type_checkboxes = {}
        file_types = ["PDF", "Document", "Image", "Spreadsheet", "ZIP", "Email"]
        for file_type in file_types:
            checkbox = QCheckBox(file_type)
            checkbox.setFont(QFont("Arial", 13))
            checkbox.stateChanged.connect(self.filter_changed.emit)
            self.file_type_checkboxes[file_type] = checkbox
            layout.addWidget(checkbox)
        
        layout.addSpacing(15)
        
        # Upload Date section
        upload_date_label = QLabel("Upload Date")
        upload_date_label.setFont(QFont("Arial", 15, QFont.Bold))
        layout.addWidget(upload_date_label)
        
        self.date_group = QButtonGroup()
        self.date_group.setExclusive(False)
        date_options = ["Last 24 hours", "Last week", "Last month"]
        self.date_radios = {}
        for option in date_options:
            radio = QRadioButton(option)
            radio.setFont(QFont("Arial", 13))
            radio.toggled.connect(self._on_date_toggled)
            self.date_group.addButton(radio)
            self.date_radios[option] = radio
            layout.addWidget(radio)
        
        layout.addSpacing(15)
        
        # Status section
        status_label = QLabel("Status")
        status_label.setFont(QFont("Arial", 15, QFont.Bold))
        layout.addWidget(status_label)
        
        self.status_checkboxes = {}
        statuses = ["Analyzed", "Pending", "Flagged"]
        for status in statuses:
            checkbox = QCheckBox(status)
            checkbox.setFont(QFont("Arial", 13))
            checkbox.stateChanged.connect(self.filter_changed.emit)
            self.status_checkboxes[status] = checkbox
            layout.addWidget(checkbox)
        
        layout.addSpacing(20)
        
        # Clear Filters button
        clear_btn = QPushButton("Clear All Filters")
        clear_btn.setFont(QFont("Arial", 12))
        clear_btn.setMinimumHeight(35)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d2137;
                color: #40e0d0;
                border: 1px solid #1a4a5a;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #163545;
                border-color: #40e0d0;
            }
        """)
        clear_btn.clicked.connect(self._clear_all_filters)
        layout.addWidget(clear_btn)
        
        layout.addStretch()
    
    def _on_date_toggled(self, checked):
        self.filter_changed.emit()
    
    def _clear_all_filters(self):
        for cb in self.file_type_checkboxes.values():
            cb.setChecked(False)
        for radio in self.date_radios.values():
            radio.setAutoExclusive(False)
            radio.setChecked(False)
            radio.setAutoExclusive(True)
        for cb in self.status_checkboxes.values():
            cb.setChecked(False)
        self.filter_changed.emit()
    
    def _apply_styles(self):
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
                padding: 4px;
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
        filters = {
            'file_types': [],
            'date_range': None,
            'statuses': []
        }
        for file_type, checkbox in self.file_type_checkboxes.items():
            if checkbox.isChecked():
                filters['file_types'].append(file_type)
        for option, radio in self.date_radios.items():
            if radio.isChecked():
                filters['date_range'] = option
                break
        for status, checkbox in self.status_checkboxes.items():
            if checkbox.isChecked():
                filters['statuses'].append(status)
        return filters

class UploadZone(QFrame):
    """Drag and drop upload zone."""
    
    files_dropped = Signal(str)  # folder_path
    
    def __init__(self, large=False):
        super().__init__()
        self.setAcceptDrops(True)
        self._is_importing = False
        self.large = large
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10 if not self.large else 20)
        
        margins = 60 if self.large else 30
        layout.setContentsMargins(margins, margins, margins, margins)
        
        icon_label = QLabel("+")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_size = 80 if self.large else 56
        icon_label.setFont(QFont("Arial", icon_size, QFont.Bold))
        icon_label.setStyleSheet("color: #40e0d0; background: transparent; border: none;")
        layout.addWidget(icon_label)
        
        text_label = QLabel("Upload Folder Here")
        text_label.setAlignment(Qt.AlignCenter)
        text_size = 28 if self.large else 18
        text_label.setFont(QFont("Arial", text_size, QFont.Bold))
        text_label.setStyleSheet("color: #00d4aa; background: transparent; border: none;")
        layout.addWidget(text_label)
        
        instruction_label = QLabel("Drag and drop a folder or click to browse")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_size = 18 if self.large else 13
        instruction_label.setFont(QFont("Arial", instruction_size))
        instruction_label.setStyleSheet("color: #8899aa; background: transparent; border: none;")
        layout.addWidget(instruction_label)
    
    def _apply_styles(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #0d2137;
                border: 3px dashed #1a4a5a;
                border-radius: 16px;
            }
            QFrame:hover {
                border-color: #40e0d0;
                background-color: #122a3a;
            }
        """)
    
    def set_importing(self, importing: bool):
        self._is_importing = importing
        self.setAcceptDrops(not importing)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if self._is_importing:
            return
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    background-color: #163545;
                    border: 3px dashed #40e0d0;
                    border-radius: 16px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self._apply_styles()
    
    def dropEvent(self, event: QDropEvent):
        self._apply_styles()
        if self._is_importing:
            return
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.files_dropped.emit(path)
                break
            elif os.path.isfile(path):
                self.files_dropped.emit(os.path.dirname(path))
                break
    
    def mousePressEvent(self, event):
        if self._is_importing:
            return
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Evidence Folder",
            "",
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.files_dropped.emit(folder)


class EvidenceManagement(QWidget):
    """Evidence Management main screen with Big Upload Empty State."""
    
    back_to_dashboard = Signal()
    
    def __init__(self, case_id: int = None):
        super().__init__()
        self.case_id = case_id
        self.database = Database()
        self.evidence_data = []
        self._is_importing = False
        self._setup_ui()
        self._apply_styles()
        self._load_evidence()
    
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ── Global Top Bar ──
        top_bar_container = QWidget()
        top_bar_container.setStyleSheet("background-color: #0a1929;")
        top_bar = QHBoxLayout(top_bar_container)
        top_bar.setContentsMargins(30, 20, 30, 10)
        
        self.back_button = QPushButton("← Dashboard")
        self.back_button.setFont(QFont("Arial", 12))
        self.back_button.setFixedHeight(36)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #0d2137;
                color: #40e0d0;
                border: 1px solid #1a4a5a;
                border-radius: 6px;
                padding: 6px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #163545;
                border-color: #40e0d0;
            }
        """)
        self.back_button.clicked.connect(self.back_to_dashboard.emit)
        top_bar.addWidget(self.back_button)
        top_bar.addStretch()
        
        self.case_label = QLabel("")
        self.case_label.setFont(QFont("Arial", 13))
        self.case_label.setStyleSheet("color: #8899aa;")
        top_bar.addWidget(self.case_label)
        
        main_layout.addWidget(top_bar_container)
        
        # ── Global Progress Section (Overlays or sits at top) ──
        self.progress_frame = QFrame()
        self.progress_frame.setVisible(False)
        self.progress_frame.setStyleSheet("""
            QFrame {
                background-color: #122a3a;
                border-bottom: 2px solid #40e0d0;
                padding: 15px 30px;
            }
        """)
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setSpacing(8)
        
        self.progress_title = QLabel("Importing Evidence...")
        self.progress_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.progress_title.setStyleSheet("color: #00d4aa; border: none;")
        progress_layout.addWidget(self.progress_title)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(24)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Starting scan...")
        self.progress_label.setFont(QFont("Arial", 13))
        self.progress_label.setStyleSheet("color: #e0e6ed; border: none;")
        progress_layout.addWidget(self.progress_label)
        
        main_layout.addWidget(self.progress_frame)
        
        # ── Main Stacked Area ──
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)  # stretch = 1
        
        # State 0: Empty Upload State
        self.empty_state_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_state_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setContentsMargins(60, 20, 60, 40)
        
        empty_title = QLabel("Add Evidence to Case")
        empty_title.setAlignment(Qt.AlignCenter)
        empty_title.setFont(QFont("Arial", 28, QFont.Bold))
        empty_title.setStyleSheet("color: #00d4aa; margin-bottom: 10px;")
        empty_layout.addWidget(empty_title)
        
        empty_subtitle = QLabel("Import a folder containing your forensic images, logs, or documents to begin the timeline analysis.")
        empty_subtitle.setAlignment(Qt.AlignCenter)
        empty_subtitle.setFont(QFont("Arial", 14))
        empty_subtitle.setStyleSheet("color: #8899aa; margin-bottom: 40px;")
        empty_layout.addWidget(empty_subtitle)
        
        self.big_upload_zone = UploadZone(large=True)
        self.big_upload_zone.setMinimumSize(600, 350)
        self.big_upload_zone.files_dropped.connect(self._handle_folder_drop)
        empty_layout.addWidget(self.big_upload_zone, alignment=Qt.AlignCenter)
        empty_layout.addStretch()
        
        # State 1: Populated Evidence Table State
        self.content_widget = QWidget()
        content_main_layout = QHBoxLayout(self.content_widget)
        content_main_layout.setContentsMargins(0, 0, 0, 0)
        content_main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = SidebarFilter()
        self.sidebar.setFixedWidth(260)
        self.sidebar.filter_changed.connect(self._apply_filters)
        content_main_layout.addWidget(self.sidebar)
        
        # Table & small upload area
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(30, 25, 30, 25)
        table_layout.setSpacing(20)
        
        # Header title
        title = QLabel("Metadata Overview")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #00d4aa;")
        table_layout.addWidget(title)
        
        # File count summary + "Upload More" button row
        header_row = QHBoxLayout()
        self.file_count_label = QLabel("Loading...")
        self.file_count_label.setFont(QFont("Arial", 12))
        self.file_count_label.setStyleSheet("color: #8899aa;")
        header_row.addWidget(self.file_count_label)
        
        header_row.addStretch()
        
        self.upload_more_btn = QPushButton("+ Upload More Evidence")
        self.upload_more_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.upload_more_btn.setFixedHeight(36)
        self.upload_more_btn.setStyleSheet("""
            QPushButton {
                background-color: #40e0d0;
                color: #0a1929;
                border: none;
                border-radius: 6px;
                padding: 6px 18px;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
        """)
        self.upload_more_btn.clicked.connect(self._show_upload_dialog)
        header_row.addWidget(self.upload_more_btn)
        
        table_layout.addLayout(header_row)
        
        # Metadata Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "File Name", "Type", "Date", "Status"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 170)
        self.table.setColumnWidth(4, 110)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(38)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        
        table_layout.addWidget(self.table, 1)
        
        content_main_layout.addWidget(table_container)
        
        # Add widget states
        self.stack.addWidget(self.empty_state_widget)
        self.stack.addWidget(self.content_widget)
    
    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QTableWidget {
                background-color: #0d2137;
                border: 1px solid #1a4a5a;
                border-radius: 5px;
                gridline-color: #1a4a5a;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
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
                padding: 10px;
                border: none;
                border-bottom: 2px solid #1a4a5a;
                font-weight: bold;
                font-size: 13px;
            }
            QProgressBar {
                border: 2px solid #1a4a5a;
                border-radius: 5px;
                text-align: center;
                background-color: #0d2137;
                color: #ffffff;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #40e0d0;
                border-radius: 3px;
            }
        """)
    
    def _update_file_count(self):
        total = len(self.evidence_data)
        if total == 0:
            self.file_count_label.setText("No evidence files loaded")
        else:
            pending = sum(1 for e in self.evidence_data if e.get('status') == 'Pending')
            analyzed = sum(1 for e in self.evidence_data if e.get('status') == 'Analyzed')
            flagged = sum(1 for e in self.evidence_data if e.get('status') == 'Flagged')
            self.file_count_label.setText(
                f"Total: {total} files  |  Pending: {pending}  |  Analyzed: {analyzed}  |  Flagged: {flagged}"
            )
    
    def _load_evidence(self):
        if self.case_id:
            self.evidence_data = self.database.get_evidence_for_case(self.case_id)
            self._populate_table(self.evidence_data)
            self._update_file_count()
            
            case = self.database.get_case(self.case_id)
            if case:
                self.case_label.setText(f"Case #{case['id']}: {case['name']}")
                
            if len(self.evidence_data) == 0:
                self.stack.setCurrentIndex(0)  # Empty big upload state
            else:
                self.stack.setCurrentIndex(1)  # Table state
        else:
            self.evidence_data = []
            self.table.setRowCount(0)
            self._update_file_count()
            self.case_label.setText("")
            self.stack.setCurrentIndex(0)
    
    def _populate_table(self, evidence_list: List[Dict[str, Any]]):
        self.table.setRowCount(0)
        for evidence in evidence_list:
            self._insert_table_row(evidence)
    
    def _insert_table_row(self, evidence_data: Dict[str, Any]):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        id_item = QTableWidgetItem(str(evidence_data.get('id', '')))
        id_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, id_item)
        
        self.table.setItem(row, 1, QTableWidgetItem(evidence_data.get('file_name', '')))
        
        ext = evidence_data.get('file_extension', '').upper().replace('.', '')
        ext_item = QTableWidgetItem(ext)
        ext_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 2, ext_item)
        
        modified = evidence_data.get('modified_time', '')
        date_str = self._format_date(modified)
        date_item = QTableWidgetItem(date_str)
        date_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 3, date_item)
        
        status = evidence_data.get('status', 'Pending')
        status_item = QTableWidgetItem(status)
        status_item.setTextAlignment(Qt.AlignCenter)
        
        status_colors = {
            'Pending': QColor('#f0c040'), 
            'Analyzed': QColor('#00d4aa'), 
            'Flagged': QColor('#ff6b6b'),
        }
        if status in status_colors:
            status_item.setForeground(status_colors[status])
        
        self.table.setItem(row, 4, status_item)
    
    @staticmethod
    def _format_date(date_val) -> str:
        if isinstance(date_val, datetime):
            return date_val.strftime('%Y-%m-%d %H:%M')
        elif isinstance(date_val, str) and date_val:
            try:
                dt = datetime.fromisoformat(date_val.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                return str(date_val)[:16] if date_val else ''
        return ''
    
    @staticmethod
    def _parse_date(date_val) -> datetime:
        if isinstance(date_val, datetime):
            return date_val
        elif isinstance(date_val, str) and date_val:
            try:
                return datetime.fromisoformat(date_val.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        return None
    
    def _apply_filters(self):
        filters = self.sidebar.get_active_filters()
        has_filters = any([filters['file_types'], filters['date_range'], filters['statuses']])
        
        if not has_filters:
            self._populate_table(self.evidence_data)
            return
            
        allowed_extensions = set()
        if filters['file_types']:
            for category in filters['file_types']:
                if category in FILE_TYPE_MAPPING:
                    allowed_extensions.update(FILE_TYPE_MAPPING[category])
                    
        date_cutoff = None
        if filters['date_range']:
            now = datetime.now()
            if filters['date_range'] == 'Last 24 hours':
                date_cutoff = now - timedelta(hours=24)
            elif filters['date_range'] == 'Last week':
                date_cutoff = now - timedelta(weeks=1)
            elif filters['date_range'] == 'Last month':
                date_cutoff = now - timedelta(days=30)
                
        filtered_data = []
        for evidence in self.evidence_data:
            if allowed_extensions:
                ext = evidence.get('file_extension', '').lower()
                if ext not in allowed_extensions:
                    continue
            if filters['statuses']:
                status = evidence.get('status', 'Pending')
                if status not in filters['statuses']:
                    continue
            if date_cutoff:
                date_val = evidence.get('added_at') or evidence.get('modified_time')
                parsed = self._parse_date(date_val)
                if parsed and parsed < date_cutoff:
                    continue
            filtered_data.append(evidence)
            
        self._populate_table(filtered_data)

    def _show_upload_dialog(self):
        if self._is_importing:
            return
        folder = QFileDialog.getExistingDirectory(self, "Select Evidence Folder", "", QFileDialog.ShowDirsOnly)
        if folder:
            self._handle_folder_drop(folder)

    def _handle_folder_drop(self, folder_path: str):
        if not self.case_id:
            QMessageBox.warning(self, "No Case Selected", "Please create or select a case first.")
            return
            
        if self._is_importing:
            QMessageBox.warning(self, "Import In Progress", "Please wait for current import to finish.")
            return
            
        folder_name = os.path.basename(folder_path)
        
        self._is_importing = True
        self.big_upload_zone.set_importing(True)
        self.upload_more_btn.setEnabled(False)
        self.sidebar.setEnabled(False)
        
        # Show global progress bar (always at top)
        self.progress_frame.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setRange(0, 100)
        self.progress_label.setText(f"Scanning folder: {folder_name}...")
        self.progress_title.setText(f"Importing & Analyzing: {folder_name}")
        
        self.processing_thread = FileProcessingThread(folder_path, self.case_id)
        self.processing_thread.progress_updated.connect(self._update_progress)
        self.processing_thread.file_processed.connect(self._add_evidence_to_table)
        self.processing_thread.finished_processing.connect(self._import_finished)
        self.processing_thread.error_occurred.connect(self._import_error)
        self.processing_thread.start()
    
    def _update_progress(self, current: int, total: int, current_file: str):
        progress = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Extracting metadata & processing: {current} of {total} ({current_file})")
        
        # Switch to the table view as soon as we start extracting files!
        if self.stack.currentIndex() == 0:
            self.stack.setCurrentIndex(1)
    
    def _add_evidence_to_table(self, evidence_data: Dict[str, Any]):
        self.evidence_data.append(evidence_data)
        self._insert_table_row(evidence_data)
        self.table.scrollToBottom()
        self._update_file_count()
    
    def _import_finished(self, total_files: int):
        self._is_importing = False
        self.big_upload_zone.set_importing(False)
        self.upload_more_btn.setEnabled(True)
        self.sidebar.setEnabled(True)
        
        self.progress_frame.setVisible(False)
        self._update_file_count()
        
        # Always ensure we show the table
        self.stack.setCurrentIndex(1)
        
        QMessageBox.information(
            self,
            "Import & Analysis Complete",
            f"Successfully processed {total_files} evidence files."
        )
    
    def _import_error(self, error_message: str):
        self._is_importing = False
        self.big_upload_zone.set_importing(False)
        self.upload_more_btn.setEnabled(True)
        self.sidebar.setEnabled(True)
        self.progress_frame.setVisible(False)
        
        QMessageBox.warning(self, "Analysis Error", f"Error during import:\n{error_message}")
        
        if len(self.evidence_data) == 0:
            self.stack.setCurrentIndex(0)
    
    def set_case_id(self, case_id: int):
        self.case_id = case_id
        self.evidence_data = []
        self.table.setRowCount(0)
        self._load_evidence()