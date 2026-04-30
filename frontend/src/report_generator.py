"""
Report Generator Module
Generate automated final reports for investigation cases
Feature #10: Automated Final Report
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QCheckBox, QLineEdit, QTextEdit, QFileDialog,
    QMessageBox, QProgressBar, QGroupBox, QScrollArea
)
from PySide6.QtCore import Signal, Qt, QThread
from PySide6.QtGui import QFont
from pathlib import Path
from datetime import datetime
from typing import Optional

from backend.app.database import Database
from backend.app.pdf_generator import PDFReportGenerator


class ReportGeneratorThread(QThread):
    """Background thread for PDF generation."""
    
    progress_updated = Signal(int, str)
    generation_complete = Signal(str)
    generation_failed = Signal(str)
    
    def __init__(self, case_id: int, output_path: str, options: dict, user_id: int = None):
        super().__init__()
        self.case_id = case_id
        self.output_path = output_path
        self.options = options
        self.user_id = user_id
        self.database = Database()
    
    def run(self):
        """Generate the PDF report in background."""
        try:
            self.progress_updated.emit(10, "Loading case information...")
            
            case = self.database.get_case(self.case_id)
            if not case:
                self.generation_failed.emit("Case not found")
                return
            
            self.progress_updated.emit(30, "Gathering evidence data...")
            evidence_list = self.database.get_evidence_for_case(self.case_id)
            
            self.progress_updated.emit(50, "Calculating statistics...")
            stats = self.database.get_case_stats(self.case_id)
            
            activity_log = None
            if self.options.get('include_activity_log', True):
                self.progress_updated.emit(60, "Loading activity log...")
                activity_log = self.database.get_recent_activity(
                    case_id=self.case_id,
                    limit=50
                )
            
            self.progress_updated.emit(80, "Generating PDF document...")
            
            generator = PDFReportGenerator()
            generator.generate_report(
                output_path=self.output_path,
                case_info=case,
                evidence_list=evidence_list,
                stats=stats,
                activity_log=activity_log
            )
            
            self.progress_updated.emit(100, "Report generated successfully")
            
            # Log activity with user_id
            self.database.log_activity(
                case_id=self.case_id,
                user_id=self.user_id,
                action="Report Generated",
                details=f"Final investigation report generated: {Path(self.output_path).name}"
            )
            
            self.generation_complete.emit(self.output_path)
            
        except Exception as e:
            self.generation_failed.emit(str(e))


class ReportGenerator(QWidget):
    """Report generation interface for creating final investigation reports."""
    
    back_requested = Signal()
    
    def __init__(self, case_id: int = None, user_id: int = None):
        super().__init__()
        self.database = Database()
        self.case_id = case_id
        self.user_id = user_id
        self.generator_thread = None
        self._setup_ui()
        self._apply_styles()
        if self.case_id:
            self._load_case_info()
    
    def set_case_id(self, case_id: int):
        """Set the active case and reload information."""
        self.case_id = case_id
        self._load_case_info()
    
    def set_user_id(self, user_id: int):
        """Set the current user ID for activity logging."""
        self.user_id = user_id
    
    def _setup_ui(self):
        """Setup the report generator UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("‹ Back")
        back_btn.setFont(QFont("Arial", 12))
        back_btn.setFixedSize(100, 35)
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)
        
        header_layout.addStretch()
        
        title_label = QLabel("Generate Final Report")
        title_label.setFont(QFont("Arial", 28, QFont.Bold))
        title_label.setStyleSheet("color: #00d4aa;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(20)
        
        # Case information section
        info_group = QGroupBox("Case Information")
        info_group.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout = QVBoxLayout(info_group)
        info_layout.setSpacing(10)
        
        self.case_name_label = QLabel("Case: Loading...")
        self.case_name_label.setFont(QFont("Arial", 11))
        self.case_name_label.setWordWrap(True)
        info_layout.addWidget(self.case_name_label)
        
        self.case_type_label = QLabel("Type: N/A")
        self.case_type_label.setFont(QFont("Arial", 11))
        info_layout.addWidget(self.case_type_label)
        
        self.case_status_label = QLabel("Status: N/A")
        self.case_status_label.setFont(QFont("Arial", 11))
        info_layout.addWidget(self.case_status_label)
        
        self.evidence_count_label = QLabel("Evidence Files: 0")
        self.evidence_count_label.setFont(QFont("Arial", 11))
        info_layout.addWidget(self.evidence_count_label)
        
        content_layout.addWidget(info_group)
        
        # Report options section
        options_group = QGroupBox("Report Options")
        options_group.setFont(QFont("Arial", 12, QFont.Bold))
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(12)
        
        self.include_summary_check = QCheckBox("Include Executive Summary")
        self.include_summary_check.setChecked(True)
        self.include_summary_check.setFont(QFont("Arial", 11))
        options_layout.addWidget(self.include_summary_check)
        
        self.include_evidence_check = QCheckBox("Include Evidence Inventory")
        self.include_evidence_check.setChecked(True)
        self.include_evidence_check.setFont(QFont("Arial", 11))
        options_layout.addWidget(self.include_evidence_check)
        
        self.include_statistics_check = QCheckBox("Include Risk Analysis Statistics")
        self.include_statistics_check.setChecked(True)
        self.include_statistics_check.setFont(QFont("Arial", 11))
        options_layout.addWidget(self.include_statistics_check)
        
        self.include_activity_check = QCheckBox("Include Activity Log")
        self.include_activity_check.setChecked(True)
        self.include_activity_check.setFont(QFont("Arial", 11))
        options_layout.addWidget(self.include_activity_check)
        
        content_layout.addWidget(options_group)
        
        # Output settings section
        output_group = QGroupBox("Output Settings")
        output_group.setFont(QFont("Arial", 12, QFont.Bold))
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(12)
        
        filename_layout = QHBoxLayout()
        filename_label = QLabel("Report Filename:")
        filename_label.setFont(QFont("Arial", 11))
        filename_layout.addWidget(filename_label)
        
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Enter filename (without extension)")
        self.filename_input.setFont(QFont("Arial", 11))
        self.filename_input.setMinimumHeight(35)
        filename_layout.addWidget(self.filename_input)
        
        output_layout.addLayout(filename_layout)
        
        location_layout = QHBoxLayout()
        location_label = QLabel("Save Location:")
        location_label.setFont(QFont("Arial", 11))
        location_layout.addWidget(location_label)
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Select output directory")
        self.location_input.setFont(QFont("Arial", 11))
        self.location_input.setMinimumHeight(35)
        self.location_input.setReadOnly(True)
        location_layout.addWidget(self.location_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedSize(100, 35)
        browse_btn.clicked.connect(self._browse_output_location)
        location_layout.addWidget(browse_btn)
        
        output_layout.addLayout(location_layout)
        
        content_layout.addWidget(output_group)
        
        # Progress section
        progress_group = QGroupBox("Generation Progress")
        progress_group.setObjectName("progressGroup")
        progress_group.setFont(QFont("Arial", 12, QFont.Bold))
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to generate report")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #8899aa;")
        progress_layout.addWidget(self.status_label)
        
        content_layout.addWidget(progress_group)
        
        content_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        
        action_layout.addStretch()
        
        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.generate_btn.setFixedSize(200, 45)
        self.generate_btn.clicked.connect(self._generate_report)
        action_layout.addWidget(self.generate_btn)
        
        self.open_btn = QPushButton("Open Report")
        self.open_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.open_btn.setFixedSize(150, 45)
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self._open_generated_report)
        action_layout.addWidget(self.open_btn)
        
        action_layout.addStretch()
        
        main_layout.addLayout(action_layout)
        
        # Store last generated path
        self.last_generated_path = None
    
    def _apply_styles(self):
        """Apply report generator styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QGroupBox {
                background-color: transparent;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
                padding: 35px 15px 15px 15px;
                margin-top: 15px;
                font-weight: bold;
                color: #40e0d0;
            }
            QGroupBox#progressGroup {
                border: none;
                padding: 15px 0px 0px 0px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 15px;
                left: 15px;
                top: 8px;
                background-color: #0a1929;
                color: #40e0d0;
            }
            QCheckBox {
                spacing: 8px;
                color: #e0e6ed;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #1a4a5a;
                border-radius: 4px;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #40e0d0;
                border-color: #40e0d0;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzIDRMNiAxMUwzIDgiIHN0cm9rZT0iIzAwMDAwMCIgc3Ryb2tlLXdpZHRoPSIyLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QCheckBox::indicator:hover {
                border-color: #40e0d0;
            }
            QLabel {
                background-color: transparent;
                border: none;
            }
            QLineEdit {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e6ed;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: none;
            }
            QLineEdit::placeholder {
                color: #6c7086;
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
            QPushButton:disabled {
                background-color: #1a4a5a;
                color: #6c7086;
            }
            QProgressBar {
                border: 2px solid #1a4a5a;
                border-radius: 8px;
                text-align: center;
                background-color: transparent;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #40e0d0;
                border-radius: 6px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
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
    
    def _load_case_info(self):
        """Load and display case information."""
        if not self.case_id:
            return
        
        case = self.database.get_case(self.case_id)
        if not case:
            return
        
        self.case_name_label.setText(f"Case: {case.get('name', 'Unknown')}")
        self.case_type_label.setText(f"Type: {case.get('case_type', 'N/A')}")
        self.case_status_label.setText(f"Status: {case.get('status', 'N/A')}")
        
        evidence = self.database.get_evidence_for_case(self.case_id)
        self.evidence_count_label.setText(f"Evidence Files: {len(evidence)}")
        
        # Set default filename
        case_name_safe = case.get('name', 'report').replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_filename = f"{case_name_safe}_Report_{timestamp}"
        self.filename_input.setText(default_filename)
        
        # Set default location to reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        self.location_input.setText(str(reports_dir.absolute()))
    
    def _browse_output_location(self):
        """Open directory browser for output location."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.location_input.text() or str(Path.home())
        )
        
        if directory:
            self.location_input.setText(directory)
    
    def _generate_report(self):
        """Start report generation process."""
        # Validate inputs
        if not self.case_id:
            QMessageBox.warning(self, "No Case", "No case selected for report generation.")
            return
        
        filename = self.filename_input.text().strip()
        if not filename:
            QMessageBox.warning(self, "Invalid Filename", "Please enter a filename for the report.")
            return
        
        location = self.location_input.text().strip()
        if not location:
            QMessageBox.warning(self, "Invalid Location", "Please select an output directory.")
            return
        
        # Ensure filename has .pdf extension
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        output_path = str(Path(location) / filename)
        
        # Check if file exists
        if Path(output_path).exists():
            reply = QMessageBox.question(
                self,
                "File Exists",
                f"The file '{filename}' already exists. Do you want to overwrite it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Gather options
        options = {
            'include_summary': self.include_summary_check.isChecked(),
            'include_evidence': self.include_evidence_check.isChecked(),
            'include_statistics': self.include_statistics_check.isChecked(),
            'include_activity_log': self.include_activity_check.isChecked(),
        }
        
        # Disable generate button during generation
        self.generate_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting report generation...")
        
        # Start generation thread
        self.generator_thread = ReportGeneratorThread(self.case_id, output_path, options, self.user_id)
        self.generator_thread.progress_updated.connect(self._update_progress)
        self.generator_thread.generation_complete.connect(self._handle_generation_complete)
        self.generator_thread.generation_failed.connect(self._handle_generation_failed)
        self.generator_thread.start()
    
    def _update_progress(self, value: int, message: str):
        """Update progress bar and status message."""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def _handle_generation_complete(self, output_path: str):
        """Handle successful report generation."""
        self.generate_btn.setEnabled(True)
        self.open_btn.setEnabled(True)
        self.last_generated_path = output_path
        self.status_label.setText(f"Report generated successfully: {Path(output_path).name}")
        
        QMessageBox.information(
            self,
            "Report Generated",
            f"Report has been successfully generated:\n\n{output_path}\n\nYou can now open the report or generate another one."
        )
    
    def _handle_generation_failed(self, error_message: str):
        """Handle report generation failure."""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Generation failed: {error_message}")
        
        QMessageBox.critical(
            self,
            "Generation Failed",
            f"Failed to generate report:\n\n{error_message}"
        )
    
    def _open_generated_report(self):
        """Open the last generated report in default PDF viewer."""
        if not self.last_generated_path or not Path(self.last_generated_path).exists():
            QMessageBox.warning(
                self,
                "Report Not Found",
                "The generated report file could not be found."
            )
            return
        
        import os
        import platform
        
        try:
            if platform.system() == 'Windows':
                os.startfile(self.last_generated_path)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{self.last_generated_path}"')
            else:  # Linux
                os.system(f'xdg-open "{self.last_generated_path}"')
        except Exception as e:
            QMessageBox.warning(
                self,
                "Cannot Open Report",
                f"Could not open the report automatically:\n\n{str(e)}\n\nPlease open it manually from:\n{self.last_generated_path}"
            )
