"""
Case Management Screen
Multi-step workflow: New Case → Choose Type → Upload Evidence
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFrame, QStackedWidget, QFileDialog,
    QProgressBar, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent
import os
from pathlib import Path

from ..core.database import Database
from ..core.file_scanner import FileScanner


class CaseTypeCard(QFrame):
    """Clickable card for case type selection."""
    
    clicked = Signal(str)
    
    def __init__(self, icon: str, title: str, description: str):
        super().__init__()
        self.title = title
        self._selected = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(280, 180)
        self._setup_ui(icon, title, description)
        self._update_style()
    
    def _setup_ui(self, icon: str, title: str, description: str):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("Segoe UI Emoji", 36))
        icon_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 15, QFont.Bold))
        title_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Arial", 11))
        desc_label.setStyleSheet("color: #8899aa; background: transparent; border: none;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
    
    def _update_style(self):
        if self._selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #163545;
                    border: 3px solid #40e0d0;
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #122a3a;
                    border: 2px solid #1a4a5a;
                    border-radius: 12px;
                }
                QFrame:hover {
                    border-color: #2a7a8a;
                    background-color: #153040;
                }
            """)
    
    def set_selected(self, selected: bool):
        self._selected = selected
        self._update_style()
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.title)


class UploadWorker(QThread):
    """Background worker for scanning and analyzing uploaded folder."""
    
    progress_updated = Signal(int, str)  # progress, message
    file_found = Signal(str, str)  # filename, file_type
    completed = Signal(int)  # total_files
    
    def __init__(self, folder_path: str, case_id: int):
        super().__init__()
        self.folder_path = folder_path
        self.case_id = case_id
        self.scanner = FileScanner()
        self.database = Database()
    
    def run(self):
        """Scan folder and add evidence files."""
        try:
            # Scan the folder
            self.progress_updated.emit(10, "Scanning folder structure...")
            files = self.scanner.scan_directory(self.folder_path)
            
            total_files = len(files)
            if total_files == 0:
                self.progress_updated.emit(100, "No files found")
                self.completed.emit(0)
                return
            
            self.progress_updated.emit(20, f"Found {total_files} files. Analyzing...")
            
            # Process each file
            for i, file_path in enumerate(files):
                # Extract metadata
                metadata = self.scanner.extract_metadata(file_path)
                
                # Determine file type
                file_type = self._get_file_type(file_path)
                
                # Add to database
                self.database.add_evidence(
                    case_id=self.case_id,
                    file_path=file_path,
                    file_name=os.path.basename(file_path),
                    file_type=file_type,
                    file_size=metadata.get('size', 0),
                    created_date=metadata.get('created', ''),
                    modified_date=metadata.get('modified', ''),
                    hash_value=metadata.get('hash', '')
                )
                
                # Emit progress
                progress = 20 + int((i + 1) / total_files * 70)
                self.progress_updated.emit(
                    progress,
                    f"Processing {i + 1}/{total_files}: {os.path.basename(file_path)}"
                )
                self.file_found.emit(os.path.basename(file_path), file_type)
                
                # Small delay for visual effect
                self.msleep(50)
            
            self.progress_updated.emit(100, f"Analysis complete! {total_files} files processed")
            self.completed.emit(total_files)
            
        except Exception as e:
            self.progress_updated.emit(0, f"Error: {str(e)}")
            self.completed.emit(0)
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type from extension."""
        ext = Path(file_path).suffix.lower()
        
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        doc_exts = ['.pdf', '.doc', '.docx', '.txt', '.rtf']
        
        if ext in image_exts:
            return 'Image'
        elif ext in video_exts:
            return 'Video'
        elif ext in doc_exts:
            return 'Document'
        else:
            return 'Other'


class FolderUploadWidget(QFrame):
    """Big folder upload section with drag-and-drop."""
    
    folder_selected = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFixedSize(700, 400)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Icon
        icon = QLabel("📁")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI Emoji", 80))
        icon.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(icon)
        
        # Title
        title = QLabel("Upload Evidence Folder")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Drag and drop a folder here\nor click to browse")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setFont(QFont("Arial", 16))
        instructions.setStyleSheet("color: #8899aa; background: transparent; border: none;")
        layout.addWidget(instructions)
        
        # Browse button
        browse_btn = QPushButton("Browse Folder")
        browse_btn.setFont(QFont("Arial", 14, QFont.Bold))
        browse_btn.setFixedSize(200, 50)
        browse_btn.clicked.connect(self._browse_folder)
        layout.addWidget(browse_btn)
    
    def _apply_styles(self):
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
                font-weight: bold;
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
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        urls = event.mimeData().urls()
        if urls:
            folder_path = urls[0].toLocalFile()
            if os.path.isdir(folder_path):
                self.folder_selected.emit(folder_path)


class CaseManagement(QWidget):
    """Multi-step case management workflow."""
    
    case_created = Signal(int)  # case_id
    back_requested = Signal()  # Signal to go back to cases dashboard
    
    def __init__(self):
        super().__init__()
        self.database = Database()
        self.current_case_id = None
        self.selected_case_type = None
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the case management UI with stacked steps."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Stacked widget for different steps
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Step 1: Create New Case
        self.step1_widget = self._create_step1()
        self.stack.addWidget(self.step1_widget)
        
        # Step 2: Choose Case Type
        self.step2_widget = self._create_step2()
        self.stack.addWidget(self.step2_widget)
        
        # Note: Step 3 removed - now using separate evidence_upload.py screen
        
        # Start at step 1
        self.stack.setCurrentIndex(0)
    
    def _create_step1(self) -> QWidget:
        """Create Step 1: New Case Form."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(0)
        
        # Add top stretch to center vertically
        layout.addStretch()
        
        # Back button at the top left
        back_button_layout = QHBoxLayout()
        back_btn = QPushButton("‹ Back to Cases")
        back_btn.setFont(QFont("Arial", 12))
        back_btn.setFixedSize(150, 35)
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
        back_button_layout.addWidget(back_btn)
        back_button_layout.addStretch()
        layout.addLayout(back_button_layout)
        
        layout.addSpacing(20)
        
        # Header
        header = QLabel("Create New Case")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 32, QFont.Bold))
        header.setStyleSheet("color: #00d4aa; background: transparent; border: none;")
        layout.addWidget(header)
        
        # Subtitle
        subtitle = QLabel("Enter the details for your new investigation case")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 13))
        subtitle.setStyleSheet("color: #8899aa; background: transparent; border: none; margin-top: 5px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Form container - matching login design
        form_container = QFrame()
        form_container.setObjectName("formContainer")
        form_container.setFixedWidth(500)
        form_container.setStyleSheet("""
            QFrame#formContainer {
                background-color: #122a3a;
                border: 1px solid #1a4a5a;
                border-radius: 12px;
            }
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(50, 40, 50, 40)
        
        # Case Name
        name_label = QLabel("Case Name *")
        name_label.setFont(QFont("Arial", 13, QFont.Bold))
        name_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        form_layout.addWidget(name_label)
        
        self.case_name_input = QLineEdit()
        self.case_name_input.setPlaceholderText("e.g., Data Breach Investigation 2026")
        self.case_name_input.setMinimumHeight(42)
        self.case_name_input.setFont(QFont("Arial", 13))
        form_layout.addWidget(self.case_name_input)
        
        form_layout.addSpacing(5)
        
        # Case Description
        desc_label = QLabel("Description")
        desc_label.setFont(QFont("Arial", 13, QFont.Bold))
        desc_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
        form_layout.addWidget(desc_label)
        
        self.case_desc_input = QTextEdit()
        self.case_desc_input.setPlaceholderText("Brief description of the case...")
        self.case_desc_input.setFixedHeight(100)
        self.case_desc_input.setFont(QFont("Arial", 13))
        form_layout.addWidget(self.case_desc_input)
        
        # Error label
        self.step1_error = QLabel("")
        self.step1_error.setAlignment(Qt.AlignCenter)
        self.step1_error.setFont(QFont("Arial", 12))
        self.step1_error.setStyleSheet("color: #ff6b6b; background: transparent; border: none;")
        self.step1_error.setVisible(False)
        form_layout.addWidget(self.step1_error)
        
        form_layout.addSpacing(5)
        
        # Next button
        next_btn = QPushButton("Choose Case Type")
        next_btn.setFont(QFont("Arial", 15, QFont.Bold))
        next_btn.setMinimumHeight(45)
        next_btn.clicked.connect(self._handle_step1_next)
        form_layout.addWidget(next_btn)
        
        layout.addWidget(form_container, alignment=Qt.AlignCenter)
        
        # Add bottom stretch to center vertically
        layout.addStretch()
        
        return widget
    
    def _create_step2(self) -> QWidget:
        """Create Step 2: Choose Case Type."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(0)
        
        # Add top stretch to center vertically
        layout.addStretch()
        
        # Header
        header = QLabel("Choose Case Type")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 32, QFont.Bold))
        header.setStyleSheet("color: #00d4aa; background: transparent; border: none;")
        layout.addWidget(header)
        
        # Subtitle
        subtitle = QLabel("Select the type that best describes this investigation")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 13))
        subtitle.setStyleSheet("color: #8899aa; background: transparent; border: none; margin-top: 5px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(40)
        
        # Case type cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        cards_layout.setAlignment(Qt.AlignCenter)
        
        self.type_cards = []
        case_types = [
            ("🔒", "Cybercrime", "Hacking, malware, unauthorized access"),
            ("💰", "Financial Fraud", "Embezzlement, money laundering"),
            ("📊", "Data Theft", "Intellectual property, data exfiltration"),
            ("🛡️", "Internal Breach", "Insider threats, policy violations"),
        ]
        
        for icon, title, desc in case_types:
            card = CaseTypeCard(icon, title, desc)
            card.clicked.connect(self._on_type_selected)
            self.type_cards.append(card)
            cards_layout.addWidget(card)
        
        layout.addLayout(cards_layout)
        
        layout.addSpacing(25)
        
        # Error label
        self.step2_error = QLabel("")
        self.step2_error.setAlignment(Qt.AlignCenter)
        self.step2_error.setFont(QFont("Arial", 12))
        self.step2_error.setStyleSheet("color: #ff6b6b; background: transparent; border: none;")
        self.step2_error.setVisible(False)
        layout.addWidget(self.step2_error)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(20)
        
        back_btn = QPushButton("‹ Back")
        back_btn.setFont(QFont("Arial", 13))
        back_btn.setFixedSize(150, 45)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8899aa;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #122a3a;
                border-color: #40e0d0;
                color: #e0e6ed;
            }
        """)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        button_layout.addWidget(back_btn)
        
        next_btn = QPushButton("Upload Evidence")
        next_btn.setFont(QFont("Arial", 15, QFont.Bold))
        next_btn.setFixedSize(220, 45)
        next_btn.clicked.connect(self._handle_step2_next)
        button_layout.addWidget(next_btn)
        
        layout.addLayout(button_layout)
        
        # Add bottom stretch to center vertically
        layout.addStretch()
        
        return widget
    
    def _create_step3(self) -> QWidget:
        """Create Step 3: Upload Evidence."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(25)
        
        # Header
        header = QLabel("Upload Evidence")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 32, QFont.Bold))
        header.setStyleSheet("color: #00d4aa;")
        layout.addWidget(header)
        
        subtitle = QLabel("Select a folder containing evidence files to analyze")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet("color: #8899aa;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Upload widget
        self.upload_widget = FolderUploadWidget()
        self.upload_widget.folder_selected.connect(self._handle_folder_selected)
        layout.addWidget(self.upload_widget, alignment=Qt.AlignCenter)
        
        # Progress section (hidden initially)
        self.progress_container = QFrame()
        self.progress_container.setFixedWidth(700)
        self.progress_container.setVisible(False)
        self.progress_container.setStyleSheet("""
            QFrame {
                background-color: #122a3a;
                border: 1px solid #1a4a5a;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setSpacing(15)
        
        self.progress_label = QLabel("Processing...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.progress_label.setStyleSheet("color: #e0e6ed;")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_status = QLabel("")
        self.progress_status.setAlignment(Qt.AlignCenter)
        self.progress_status.setFont(QFont("Arial", 12))
        self.progress_status.setStyleSheet("color: #8899aa;")
        progress_layout.addWidget(self.progress_status)
        
        layout.addWidget(self.progress_container, alignment=Qt.AlignCenter)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(20)
        
        back_btn = QPushButton("‹ Back")
        back_btn.setFont(QFont("Arial", 13))
        back_btn.setFixedSize(150, 45)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8899aa;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #122a3a;
                border-color: #40e0d0;
                color: #e0e6ed;
            }
        """)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        button_layout.addWidget(back_btn)
        
        self.skip_btn = QPushButton("Skip for Now ›")
        self.skip_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.skip_btn.setFixedSize(200, 45)
        self.skip_btn.clicked.connect(self._handle_skip_upload)
        button_layout.addWidget(self.skip_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    def _apply_styles(self):
        """Apply case management styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QLineEdit {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                color: #e0e6ed;
            }
            QLineEdit:focus {
                border-color: #40e0d0;
                background-color: #122a3a;
            }
            QLineEdit::placeholder {
                color: #6c7086;
            }
            QTextEdit {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                color: #e0e6ed;
            }
            QTextEdit:focus {
                border-color: #40e0d0;
                background-color: #122a3a;
            }
            QPushButton {
                background-color: #40e0d0;
                color: #0a1929;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
            QPushButton:pressed {
                background-color: #00d4aa;
            }
            QProgressBar {
                border: 2px solid #1a4a5a;
                border-radius: 8px;
                text-align: center;
                background-color: #0d2137;
                color: #ffffff;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #40e0d0;
                border-radius: 6px;
            }
        """)
    
    def _handle_step1_next(self):
        """Handle next button on step 1."""
        case_name = self.case_name_input.text().strip()
        
        if not case_name:
            self.step1_error.setText("Please enter a case name")
            self.step1_error.setVisible(True)
            return
        
        # Create case in database
        case_desc = self.case_desc_input.toPlainText().strip()
        self.current_case_id = self.database.create_case(
            name=case_name,
            description=case_desc,
            case_type="Pending"  # Will be updated in step 2
        )
        
        self.step1_error.setVisible(False)
        self.stack.setCurrentIndex(1)
    
    def _on_type_selected(self, type_name: str):
        """Handle case type selection."""
        self.selected_case_type = type_name
        for card in self.type_cards:
            card.set_selected(card.title == type_name)
        self.step2_error.setVisible(False)
    
    def _handle_step2_next(self):
        """Handle next button on step 2 - emit case created to navigate to evidence upload."""
        if not self.selected_case_type:
            self.step2_error.setText("Please select a case type")
            self.step2_error.setVisible(True)
            return
        
        # Update case type in database
        self.database.update_case_type(self.current_case_id, self.selected_case_type)
        
        self.step2_error.setVisible(False)
        
        # Emit case_created signal to navigate to evidence upload screen
        self.case_created.emit(self.current_case_id)
    
    def _handle_folder_selected(self, folder_path: str):
        """Handle folder selection and start upload."""
        # Hide upload widget, show progress
        self.upload_widget.setVisible(False)
        self.progress_container.setVisible(True)
        self.skip_btn.setEnabled(False)
        
        # Start background worker
        self.worker = UploadWorker(folder_path, self.current_case_id)
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.completed.connect(self._upload_completed)
        self.worker.start()
    
    def _update_progress(self, progress: int, message: str):
        """Update progress bar and status."""
        self.progress_bar.setValue(progress)
        self.progress_status.setText(message)
    
    def _upload_completed(self, total_files: int):
        """Handle upload completion."""
        self.skip_btn.setEnabled(True)
        
        if total_files > 0:
            # Wait 2 seconds then emit signal
            QTimer.singleShot(2000, lambda: self.case_created.emit(self.current_case_id))
        else:
            self.progress_status.setText("No files found. Please try another folder.")
    
    def _handle_skip_upload(self):
        """Handle skip upload button."""
        # Emit case created signal even without evidence
        self.case_created.emit(self.current_case_id)