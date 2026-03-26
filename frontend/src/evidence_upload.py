"""
Evidence Upload Screen
Bulk folder upload with live file analysis display
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QProgressBar, QScrollArea, QGridLayout,
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent
import os
from pathlib import Path
from datetime import datetime

from backend.app.database import Database
from backend.app.file_scanner import FileScanner


class FileAnalysisWorker(QThread):
    """Background worker for analyzing uploaded folder with live updates."""
    
    progress_updated = Signal(int, int, str)  # current, total, message
    file_analyzed = Signal(dict)  # file_info dict
    completed = Signal(int)  # total_files
    error_occurred = Signal(str)  # error_message
    
    def __init__(self, folder_path: str, case_id: int):
        super().__init__()
        self.folder_path = folder_path
        self.case_id = case_id
        self.scanner = FileScanner()
        self.database = Database()
        self._is_running = True
    
    def run(self):
        """Scan and analyze folder contents."""
        try:
            # Scan directory - scan ALL files
            self.progress_updated.emit(0, 0, "Scanning folder structure...")
            files = self.scanner.scan_directory(self.folder_path, recursive=True, all_files=True)
            
            total_files = len(files)
            if total_files == 0:
                self.progress_updated.emit(0, 0, "No files found in folder")
                self.completed.emit(0)
                return
            
            self.progress_updated.emit(0, total_files, f"Found {total_files} files. Starting analysis...")
            
            # Process each file
            for i, file_path in enumerate(files):
                if not self._is_running:
                    break
                
                try:
                    # Extract metadata
                    metadata = self.scanner.extract_metadata(file_path)
                    
                    # Determine file type
                    file_type = self._get_file_type(file_path)
                    file_name = os.path.basename(file_path)
                    file_size = metadata.get('size', 0)
                    
                    # Prepare file data dict for database
                    file_data = {
                        'file_name': file_name,
                        'file_path': file_path,
                        'file_extension': Path(file_path).suffix,
                        'file_size': file_size,
                        'created_time': metadata.get('created', ''),
                        'modified_time': metadata.get('modified', ''),
                        'metadata': metadata.get('hash', '')
                    }
                    
                    # Add to database
                    evidence_id = self.database.add_evidence(
                        case_id=self.case_id,
                        file_data=file_data
                    )
                    
                    # Emit file info for live display
                    file_info = {
                        'id': evidence_id,
                        'name': file_name,
                        'type': file_type,
                        'size': file_size,
                        'hash': metadata.get('hash', ''),
                        'created': metadata.get('created', ''),
                        'modified': metadata.get('modified', ''),
                        'path': file_path
                    }
                    self.file_analyzed.emit(file_info)
                    
                    # Update progress
                    self.progress_updated.emit(
                        i + 1,
                        total_files,
                        f"Analyzing: {file_name}"
                    )
                    
                    # Small delay for visual effect
                    self.msleep(100)
                    
                except Exception as e:
                    # Continue with next file if one fails
                    self.progress_updated.emit(
                        i + 1,
                        total_files,
                        f"Error processing {os.path.basename(file_path)}: {str(e)}"
                    )
                    continue
            
            self.progress_updated.emit(total_files, total_files, "Analysis complete!")
            self.completed.emit(total_files)
            
        except Exception as e:
            self.error_occurred.emit(f"Error scanning folder: {str(e)}")
    
    def stop(self):
        """Stop the worker thread."""
        self._is_running = False
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type from extension."""
        ext = Path(file_path).suffix.lower()
        
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.svg']
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        doc_exts = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']
        archive_exts = ['.zip', '.rar', '.7z', '.tar', '.gz']
        
        if ext in image_exts:
            return 'Image'
        elif ext in video_exts:
            return 'Video'
        elif ext in doc_exts:
            return 'Document'
        elif ext in archive_exts:
            return 'Archive'
        else:
            return 'Other'


class FileListItem(QFrame):
    """Individual file item in the live analysis list."""
    
    def __init__(self, file_info: dict):
        super().__init__()
        self.file_info = file_info
        self.setFixedHeight(80)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the file item UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # File type icon
        icon_label = QLabel(self._get_icon())
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setFixedWidth(40)
        icon_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(icon_label)
        
        # File info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # File name
        name_label = QLabel(self.file_info['name'])
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        name_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        name_label.setWordWrap(False)
        info_layout.addWidget(name_label)
        
        # File details
        size_str = self._format_size(self.file_info['size'])
        details = f"{self.file_info['type']} • {size_str}"
        if self.file_info.get('hash'):
            details += f" • Hash: {self.file_info['hash'][:12]}..."
        
        details_label = QLabel(details)
        details_label.setFont(QFont("Arial", 10))
        details_label.setStyleSheet("color: #8899aa; background: transparent; border: none;")
        info_layout.addWidget(details_label)
        
        layout.addLayout(info_layout, stretch=1)
        
        # Status checkmark
        status_label = QLabel("✓")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setFont(QFont("Arial", 20, QFont.Bold))
        status_label.setStyleSheet("color: #00d4aa; background: transparent; border: none;")
        status_label.setFixedWidth(30)
        layout.addWidget(status_label)
    
    def _apply_styles(self):
        """Apply item styles."""
        self.setStyleSheet("""
            QFrame {
                background-color: #122a3a;
                border: 1px solid #1a4a5a;
                border-radius: 8px;
            }
        """)
    
    def _get_icon(self) -> str:
        """Get emoji icon for file type."""
        type_icons = {
            'Image': '🖼️',
            'Video': '🎥',
            'Document': '📄',
            'Archive': '📦',
            'Other': '📁'
        }
        return type_icons.get(self.file_info['type'], '📁')
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


class FolderDropZone(QFrame):
    """Large drag-and-drop zone for folder upload."""
    
    folder_selected = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumSize(400, 250)
        self.setMaximumSize(800, 400)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the drop zone UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)  # Add padding inside the box
        
        # Folder icon
        icon = QLabel("📁")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI Emoji", 60))  # Slightly smaller icon
        icon.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(icon)
        
        layout.addSpacing(10)  # Space after icon
        
        # Title
        title = QLabel("Bulk Evidence Upload")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 22, QFont.Bold))  # Slightly smaller title
        title.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(title)
        
        layout.addSpacing(5)  # Space after title
        
        # Instructions
        instructions = QLabel("Drag and drop a folder here\nor click to browse")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setFont(QFont("Arial", 13))
        instructions.setStyleSheet("color: #8899aa; background: transparent; border: none;")
        layout.addWidget(instructions)
        
        layout.addSpacing(10)  # Space before button
        
        # Browse button - wrapped in horizontal layout for centering
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        browse_btn = QPushButton("Browse Folder")
        browse_btn.setFont(QFont("Arial", 14, QFont.Bold))
        browse_btn.setFixedSize(180, 45)
        browse_btn.clicked.connect(self._browse_folder)
        
        button_layout.addWidget(browse_btn)
        layout.addLayout(button_layout)
    
    def _apply_styles(self):
        """Apply drop zone styles."""
        self.setStyleSheet("""
            QFrame {
                background-color: #122a3a;
                border: 3px dashed #2a7a8a;
                border-radius: 16px;
            }
            QFrame:hover {
                border-color: #40e0d0;
                background-color: #153040;
            }
            QPushButton {
                background-color: #40e0d0;
                color: #0a1929;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
        """)
    
    def _browse_folder(self):
        """Open folder browser dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Evidence Folder",
            "",
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.folder_selected.emit(folder)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter."""
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
        """Handle drag leave."""
        self._apply_styles()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        self._apply_styles()
        urls = event.mimeData().urls()
        if urls:
            folder_path = urls[0].toLocalFile()
            if os.path.isdir(folder_path):
                self.folder_selected.emit(folder_path)


class EvidenceUpload(QWidget):
    """Evidence upload screen with live file analysis."""
    
    upload_completed = Signal(int)  # total_files
    back_requested = Signal()
    
    def __init__(self, case_id: int = None):
        super().__init__()
        self.case_id = case_id
        self.database = Database()
        self.worker = None
        self._setup_ui()
        self._apply_styles()
    
    def set_case_id(self, case_id: int):
        """Set the current case ID."""
        self.case_id = case_id
        self._update_header()
    
    def _setup_ui(self):
        """Setup the evidence upload UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
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
        
        # Case info
        self.case_label = QLabel("Upload Evidence")
        self.case_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.case_label.setStyleSheet("color: #00d4aa;")
        header_layout.addWidget(self.case_label)
        
        header_layout.addStretch()
        
        # Spacer for symmetry
        header_layout.addWidget(QLabel(""), stretch=0)
        header_layout.addSpacing(100)
        
        main_layout.addLayout(header_layout)
        
        # Content area with two columns
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left column: Upload zone
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter)  # Changed from AlignTop to AlignCenter
        
        # Add top stretch for vertical centering
        left_layout.addStretch()
        
        self.drop_zone = FolderDropZone()
        self.drop_zone.folder_selected.connect(self._handle_folder_selected)
        left_layout.addWidget(self.drop_zone, alignment=Qt.AlignCenter)
        
        # Progress section (hidden initially)
        self.progress_container = QFrame()
        self.progress_container.setMinimumWidth(400)
        self.progress_container.setMaximumWidth(800)
        self.progress_container.setVisible(False)
        self.progress_container.setStyleSheet("""
            QFrame {
                background-color: #122a3a;
                border: 1px solid #1a4a5a;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setSpacing(15)
        
        self.progress_title = QLabel("Analyzing Files...")
        self.progress_title.setAlignment(Qt.AlignCenter)
        self.progress_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.progress_title.setStyleSheet("color: #e0e6ed;")
        progress_layout.addWidget(self.progress_title)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(35)
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_status = QLabel("Preparing...")
        self.progress_status.setAlignment(Qt.AlignCenter)
        self.progress_status.setFont(QFont("Arial", 13))
        self.progress_status.setStyleSheet("color: #8899aa;")
        progress_layout.addWidget(self.progress_status)
        
        # Action buttons (hidden initially)
        self.action_buttons_layout = QHBoxLayout()
        self.action_buttons_layout.setAlignment(Qt.AlignCenter)
        self.action_buttons_layout.setSpacing(15)
        
        self.upload_more_btn = QPushButton("Upload More Evidence")
        self.upload_more_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.upload_more_btn.setFixedSize(220, 45)
        self.upload_more_btn.setVisible(False)
        self.upload_more_btn.clicked.connect(self._reset_for_new_upload)
        self.action_buttons_layout.addWidget(self.upload_more_btn)
        
        self.view_table_btn = QPushButton("View Metadata Table")
        self.view_table_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.view_table_btn.setFixedSize(220, 45)
        self.view_table_btn.setVisible(False)
        self.view_table_btn.clicked.connect(lambda: self.upload_completed.emit(0))
        self.action_buttons_layout.addWidget(self.view_table_btn)
        
        progress_layout.addLayout(self.action_buttons_layout)
        
        left_layout.addWidget(self.progress_container, alignment=Qt.AlignCenter)
        
        # Add bottom stretch for vertical centering
        left_layout.addStretch()
        
        content_layout.addLayout(left_layout, stretch=1)
        
        # Right column: Live file list
        right_layout = QVBoxLayout()
        
        list_header = QLabel("Files Being Analyzed")
        list_header.setFont(QFont("Arial", 16, QFont.Bold))
        list_header.setStyleSheet("color: #e0e6ed;")
        right_layout.addWidget(list_header)
        
        # Scroll area for file list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(350)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
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
        """)
        
        # Container for file items
        self.file_list_widget = QWidget()
        self.file_list_layout = QVBoxLayout(self.file_list_widget)
        self.file_list_layout.setAlignment(Qt.AlignTop)
        self.file_list_layout.setSpacing(10)
        self.file_list_layout.setContentsMargins(0, 0, 10, 0)
        
        # Empty state
        self.empty_label = QLabel("No files yet\nSelect a folder to begin")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setFont(QFont("Arial", 14))
        self.empty_label.setStyleSheet("color: #6c7086; padding: 60px;")
        self.file_list_layout.addWidget(self.empty_label)
        
        scroll.setWidget(self.file_list_widget)
        right_layout.addWidget(scroll)
        
        content_layout.addLayout(right_layout, stretch=1)
        
        main_layout.addLayout(content_layout)
    
    def _apply_styles(self):
        """Apply screen styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QProgressBar {
                border: 2px solid #1a4a5a;
                border-radius: 8px;
                text-align: center;
                background-color: #0d2137;
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
            }
            QProgressBar::chunk {
                background-color: #40e0d0;
                border-radius: 6px;
            }
        """)
    
    def _update_header(self):
        """Update header with case info."""
        if self.case_id:
            case = self.database.get_case(self.case_id)
            if case:
                self.case_label.setText(f"Upload Evidence - {case['name']}")
    
    def _handle_folder_selected(self, folder_path: str):
        """Handle folder selection and start analysis."""
        # Hide drop zone, show progress
        self.drop_zone.setVisible(False)
        self.progress_container.setVisible(True)
        
        # Clear previous file list
        self.empty_label.setVisible(False)
        while self.file_list_layout.count() > 0:
            item = self.file_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Start worker
        self.worker = FileAnalysisWorker(folder_path, self.case_id)
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.file_analyzed.connect(self._add_file_to_list)
        self.worker.completed.connect(self._analysis_completed)
        self.worker.error_occurred.connect(self._handle_error)
        self.worker.start()
    
    def _update_progress(self, current: int, total: int, message: str):
        """Update progress bar and status."""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.progress_bar.setFormat(f"{current}/{total} files")
        self.progress_status.setText(message)
    
    def _add_file_to_list(self, file_info: dict):
        """Add analyzed file to the live list."""
        file_item = FileListItem(file_info)
        self.file_list_layout.addWidget(file_item)
        
        # Auto-scroll to bottom
        scroll_area = self.file_list_widget.parent()
        if isinstance(scroll_area, QScrollArea):
            scroll_area.verticalScrollBar().setValue(
                scroll_area.verticalScrollBar().maximum()
            )
    
    def _analysis_completed(self, total_files: int):
        """Handle analysis completion."""
        self.progress_title.setText("✓ Analysis Complete!")
        self.progress_title.setStyleSheet("color: #00d4aa;")
        self.progress_status.setText(f"Successfully analyzed {total_files} files")
        
        # Show action buttons
        self.upload_more_btn.setVisible(True)
        self.view_table_btn.setVisible(True)
        
        # Note: Don't emit upload_completed here automatically
        # Let user choose to view table or upload more
    
    def _handle_error(self, error_message: str):
        """Handle analysis error."""
        self.progress_title.setText("⚠ Error")
        self.progress_title.setStyleSheet("color: #ff6b6b;")
        self.progress_status.setText(error_message)
    
    def _reset_for_new_upload(self):
        """Reset the screen for a new upload."""
        # Hide progress container and show drop zone again
        self.progress_container.setVisible(False)
        self.drop_zone.setVisible(True)
        
        # Hide action buttons
        self.upload_more_btn.setVisible(False)
        self.view_table_btn.setVisible(False)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.progress_title.setText("Analyzing Files...")
        self.progress_title.setStyleSheet("color: #e0e6ed;")
        self.progress_status.setText("Preparing...")
        
        # Clear file list (keep existing files, just clear the display for new batch)
        # Actually, let's keep the file list to show cumulative uploads
        # Just add a separator or timestamp
        separator = QLabel(f"\n─── New Upload Batch ───\n")
        separator.setAlignment(Qt.AlignCenter)
        separator.setFont(QFont("Arial", 11, QFont.Bold))
        separator.setStyleSheet("color: #40e0d0; padding: 10px;")
        self.file_list_layout.addWidget(separator)
