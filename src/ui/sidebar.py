"""
Sidebar Module
Navigation sidebar with filters and case information
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QGroupBox,
    QScrollArea, QFrame, QPushButton, QComboBox
)
from PySide6.QtCore import Qt, Signal


class Sidebar(QWidget):
    """Sidebar widget for navigation and filtering."""
    
    # Signals for filter changes
    status_filter_changed = Signal(list)
    risk_filter_changed = Signal(list)
    file_type_filter_changed = Signal(list)
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Case info section
        case_group = QGroupBox("Current Case")
        case_layout = QVBoxLayout(case_group)
        
        self.case_name_label = QLabel("No case loaded")
        self.case_name_label.setWordWrap(True)
        case_layout.addWidget(self.case_name_label)
        
        self.case_type_combo = QComboBox()
        self.case_type_combo.addItems([
            "Select Type...",
            "Financial Fraud",
            "Cybercrime",
            "Data Breach",
            "Intellectual Property",
            "Corporate Investigation",
            "Other"
        ])
        case_layout.addWidget(self.case_type_combo)
        
        layout.addWidget(case_group)
        
        # Evidence Status Filter
        status_group = QGroupBox("Evidence Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_checkboxes = {}
        statuses = ["Pending", "Analyzed", "Flagged", "Archived"]
        for status in statuses:
            cb = QCheckBox(status)
            cb.setChecked(True)
            cb.stateChanged.connect(self._on_status_filter_change)
            self.status_checkboxes[status] = cb
            status_layout.addWidget(cb)
        
        layout.addWidget(status_group)
        
        # Risk Level Filter
        risk_group = QGroupBox("Risk Level")
        risk_layout = QVBoxLayout(risk_group)
        
        self.risk_checkboxes = {}
        risks = ["Low", "Medium", "High"]
        for risk in risks:
            cb = QCheckBox(risk)
            cb.setChecked(True)
            cb.stateChanged.connect(self._on_risk_filter_change)
            self.risk_checkboxes[risk] = cb
            risk_layout.addWidget(cb)
        
        layout.addWidget(risk_group)
        
        # File Type Filter
        filetype_group = QGroupBox("File Types")
        filetype_layout = QVBoxLayout(filetype_group)
        
        self.filetype_checkboxes = {}
        filetypes = ["Documents", "Images", "Spreadsheets", "Others"]
        for ft in filetypes:
            cb = QCheckBox(ft)
            cb.setChecked(True)
            cb.stateChanged.connect(self._on_filetype_filter_change)
            self.filetype_checkboxes[ft] = cb
            filetype_layout.addWidget(cb)
        
        layout.addWidget(filetype_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        select_all_btn = QPushButton("Select All Filters")
        select_all_btn.clicked.connect(self._select_all_filters)
        actions_layout.addWidget(select_all_btn)
        
        clear_all_btn = QPushButton("Clear All Filters")
        clear_all_btn.clicked.connect(self._clear_all_filters)
        actions_layout.addWidget(clear_all_btn)
        
        layout.addWidget(actions_group)
        
        # Spacer
        layout.addStretch()
        
        # Stats summary
        self.stats_label = QLabel("Files: 0 | Analyzed: 0")
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)
    
    def _apply_styles(self):
        """Apply sidebar styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #313244;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QCheckBox {
                spacing: 8px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #6c7086;
                border-radius: 3px;
                background-color: #181825;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #89b4fa;
                border-radius: 3px;
                background-color: #89b4fa;
            }
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
    
    def _on_status_filter_change(self):
        """Handle status filter checkbox changes."""
        selected = [s for s, cb in self.status_checkboxes.items() if cb.isChecked()]
        self.status_filter_changed.emit(selected)
    
    def _on_risk_filter_change(self):
        """Handle risk filter checkbox changes."""
        selected = [r for r, cb in self.risk_checkboxes.items() if cb.isChecked()]
        self.risk_filter_changed.emit(selected)
    
    def _on_filetype_filter_change(self):
        """Handle file type filter checkbox changes."""
        selected = [ft for ft, cb in self.filetype_checkboxes.items() if cb.isChecked()]
        self.file_type_filter_changed.emit(selected)
    
    def _select_all_filters(self):
        """Select all filter checkboxes."""
        for cb in self.status_checkboxes.values():
            cb.setChecked(True)
        for cb in self.risk_checkboxes.values():
            cb.setChecked(True)
        for cb in self.filetype_checkboxes.values():
            cb.setChecked(True)
    
    def _clear_all_filters(self):
        """Clear all filter checkboxes."""
        for cb in self.status_checkboxes.values():
            cb.setChecked(False)
        for cb in self.risk_checkboxes.values():
            cb.setChecked(False)
        for cb in self.filetype_checkboxes.values():
            cb.setChecked(False)
    
    def update_case_info(self, case_name: str, case_type: str = ""):
        """Update the case information display."""
        self.case_name_label.setText(case_name)
        if case_type:
            index = self.case_type_combo.findText(case_type)
            if index >= 0:
                self.case_type_combo.setCurrentIndex(index)
    
    def update_stats(self, total_files: int, analyzed: int):
        """Update the stats display."""
        self.stats_label.setText(f"Files: {total_files} | Analyzed: {analyzed}")
