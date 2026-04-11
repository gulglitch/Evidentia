"""
Cases Dashboard Screen
View, filter, and manage all investigation cases
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QFrame, QStyle, QStyleOptionComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPainter, QPen
from datetime import datetime
from typing import List, Dict, Any

from backend.app.database import Database


class ChevronComboBox(QComboBox):
    """ComboBox with a consistently visible custom chevron icon."""

    def paintEvent(self, event):
        super().paintEvent(event)

        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        arrow_rect = self.style().subControlRect(
            QStyle.CC_ComboBox, option, QStyle.SC_ComboBoxArrow, self
        )

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        chevron_color = QColor("#40e0d0") if self.underMouse() else QColor("#8899aa")
        pen = QPen(chevron_color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        cx = arrow_rect.center().x()
        cy = arrow_rect.center().y()
        half_w = max(4, arrow_rect.width() // 6)
        half_h = max(3, arrow_rect.height() // 7)

        painter.drawLine(cx - half_w, cy - half_h, cx, cy + half_h)
        painter.drawLine(cx, cy + half_h, cx + half_w, cy - half_h)
        painter.end()


class CasesDashboard(QWidget):
    """Cases dashboard showing all cases with filtering and sorting."""
    
    case_selected = Signal(int)  # case_id
    new_case_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.database = Database()
        self.all_cases = []
        self._setup_ui()
        self._apply_styles()
        self.load_cases()
    
    def _setup_ui(self):
        """Setup the cases dashboard UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("My Cases")
        title_label.setFont(QFont("Arial", 28, QFont.Bold))
        title_label.setStyleSheet("color: #00d4aa;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # New Case button
        new_case_btn = QPushButton("+ New Case")
        new_case_btn.setFont(QFont("Arial", 13, QFont.Bold))
        new_case_btn.setFixedSize(150, 40)
        new_case_btn.clicked.connect(self.new_case_requested.emit)
        header_layout.addWidget(new_case_btn)
        
        main_layout.addLayout(header_layout)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)
        
        # Search box
        search_label = QLabel("Search:")
        search_label.setFont(QFont("Arial", 12))
        search_label.setStyleSheet("color: #e0e6ed;")
        filter_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by case name...")
        self.search_input.setFixedWidth(300)
        self.search_input.setMinimumHeight(35)
        self.search_input.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addSpacing(20)
        
        # Case type filter
        type_label = QLabel("Type:")
        type_label.setFont(QFont("Arial", 12))
        type_label.setStyleSheet("color: #e0e6ed;")
        filter_layout.addWidget(type_label)
        
        self.type_filter = ChevronComboBox()
        self.type_filter.addItems([
            "All Types",
            "Cybercrime",
            "Financial Fraud",
            "Data Theft",
            "Internal Breach",
            "Other"
        ])
        self.type_filter.setFixedWidth(180)
        self.type_filter.setMinimumHeight(35)
        self.type_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addSpacing(20)
        
        # Status filter
        status_label = QLabel("Status:")
        status_label.setFont(QFont("Arial", 12))
        status_label.setStyleSheet("color: #e0e6ed;")
        filter_layout.addWidget(status_label)
        
        self.status_filter = ChevronComboBox()
        self.status_filter.addItems(["All Status", "Open", "In Progress", "Closed"])
        self.status_filter.setFixedWidth(150)
        self.status_filter.setMinimumHeight(35)
        self.status_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        
        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.setFont(QFont("Arial", 11))
        clear_btn.setFixedSize(120, 35)
        clear_btn.clicked.connect(self._clear_filters)
        filter_layout.addWidget(clear_btn)
        
        main_layout.addLayout(filter_layout)
        
        # Cases table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Case Name", "Type", "Status", "Created Date", "Evidence Count"
        ])
        
        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.doubleClicked.connect(self._handle_case_double_click)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Case Name
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Type
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Status
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Created
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Evidence Count
        
        self.table.setColumnWidth(0, 60)   # ID
        self.table.setColumnWidth(2, 150)  # Type
        self.table.setColumnWidth(3, 120)  # Status
        self.table.setColumnWidth(4, 180)  # Created
        self.table.setColumnWidth(5, 130)  # Evidence Count

        # Ensure left row-number header does not clip single/double-digit numbers.
        vheader = self.table.verticalHeader()
        vheader.setVisible(True)
        vheader.setDefaultAlignment(Qt.AlignCenter)
        vheader.setFixedWidth(40)
        
        main_layout.addWidget(self.table)

        # Primary case action row
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)

        self.open_case_btn = QPushButton("Open Selected Case")
        self.open_case_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.open_case_btn.setFixedSize(210, 40)
        self.open_case_btn.setStyleSheet("""
            QPushButton {
                background-color: #40e0d0;
                color: #0a1929;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                text-align: center;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
        """)
        self.open_case_btn.clicked.connect(self._open_selected_case)
        action_layout.addWidget(self.open_case_btn)

        open_hint = QLabel("Tip: You can also double-click a row to open it")
        open_hint.setFont(QFont("Arial", 10))
        open_hint.setStyleSheet("color: #8899aa;")
        action_layout.addWidget(open_hint)

        action_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        # Summary bar
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(30)
        
        self.total_cases_label = QLabel("Total Cases: 0")
        self.total_cases_label.setFont(QFont("Arial", 12))
        self.total_cases_label.setStyleSheet("color: #8899aa;")
        summary_layout.addWidget(self.total_cases_label)
        
        self.type_breakdown_label = QLabel("Cybercrime: 0 | Financial Fraud: 0 | Data Theft: 0 | Internal Breach: 0")
        self.type_breakdown_label.setFont(QFont("Arial", 12))
        self.type_breakdown_label.setStyleSheet("color: #8899aa;")
        summary_layout.addWidget(self.type_breakdown_label)
        
        summary_layout.addStretch()
        
        main_layout.addLayout(summary_layout)
    
    def _apply_styles(self):
        """Apply dashboard styles."""
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
                width: 0px;
                height: 0px;
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
                padding: 10px;
                color: #e0e6ed;
            }
            QTableWidget::item:selected {
                background-color: #2a7a8a;
                color: #ffffff;
            }
            QTableWidget::item:focus {
                outline: none;
                border: none;
            }
            QTableWidget::item:alternate {
                background-color: #0f1f2f;
            }
            QHeaderView::section:horizontal {
                background-color: #122a3a;
                color: #00d4aa;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #1a4a5a;
                font-weight: bold;
                font-size: 13px;
            }
            QHeaderView::section:horizontal:hover {
                background-color: #1a3a4a;
            }
            QHeaderView::section:vertical {
                background-color: #122a3a;
                color: #00d4aa;
                padding: 2px;
                border: none;
                border-right: 1px solid #1a4a5a;
                font-weight: bold;
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
    
    def load_cases(self):
        """Load all cases from database."""
        self.all_cases = self.database.get_all_cases()
        self._populate_table(self.all_cases)
        self._update_summary()
    
    def _populate_table(self, cases_list: List[Dict[str, Any]]):
        """Populate the table with case data."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        
        for case in cases_list:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(case.get('id', '')))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, id_item)
            
            # Case Name
            name_item = QTableWidgetItem(case.get('name', 'Unnamed Case'))
            name_item.setFont(QFont("Arial", 11, QFont.Bold))
            self.table.setItem(row, 1, name_item)
            
            # Type
            case_type = case.get('case_type', 'Other')
            type_item = QTableWidgetItem(case_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            
            # Color code by type
            type_colors = {
                'Cybercrime': '#ff6b6b',
                'Financial Fraud': '#ffd93d',
                'Data Theft': '#6bcf7f',
                'Internal Breach': '#4d96ff'
            }
            if case_type in type_colors:
                type_item.setForeground(QColor(type_colors[case_type]))
            
            self.table.setItem(row, 2, type_item)
            
            # Status
            status = case.get('status', 'Open')
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # Color code by status
            if status == 'Open':
                status_item.setForeground(QColor('#40e0d0'))
            elif status == 'In Progress':
                status_item.setForeground(QColor('#ffd93d'))
            elif status == 'Closed':
                status_item.setForeground(QColor('#8899aa'))
            
            self.table.setItem(row, 3, status_item)
            
            # Created Date
            created = case.get('created_at', '')
            created_item = QTableWidgetItem(self._format_date(created))
            self.table.setItem(row, 4, created_item)
            
            # Evidence Count
            case_id = case.get('id')
            evidence_count = len(self.database.get_evidence_for_case(case_id)) if case_id else 0
            count_item = QTableWidgetItem(str(evidence_count))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, count_item)
        
        self.table.setSortingEnabled(True)
        self.total_cases_label.setText(f"Total Cases: {len(cases_list)}")
    
    def _apply_filters(self):
        """Apply search and filters."""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        filtered_cases = []
        for case in self.all_cases:
            # Check search filter
            case_name = case.get('name', '').lower()
            if search_text and search_text not in case_name:
                continue
            
            # Check type filter
            if type_filter != "All Types":
                case_type = case.get('case_type', 'Other')
                if case_type != type_filter:
                    continue
            
            # Check status filter
            if status_filter != "All Status":
                case_status = case.get('status', 'Open')
                if case_status != status_filter:
                    continue
            
            filtered_cases.append(case)
        
        self._populate_table(filtered_cases)
        self._update_summary(filtered_cases)
    
    def _clear_filters(self):
        """Clear all filters."""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self._populate_table(self.all_cases)
        self._update_summary()
    
    def _update_summary(self, cases_list: List[Dict[str, Any]] = None):
        """Update summary statistics."""
        if cases_list is None:
            cases_list = self.all_cases
        
        # Count by type
        type_counts = {
            'Cybercrime': 0,
            'Financial Fraud': 0,
            'Data Theft': 0,
            'Internal Breach': 0
        }
        
        for case in cases_list:
            case_type = case.get('case_type', 'Other')
            if case_type in type_counts:
                type_counts[case_type] += 1
        
        self.type_breakdown_label.setText(
            f"Cybercrime: {type_counts['Cybercrime']} | "
            f"Financial Fraud: {type_counts['Financial Fraud']} | "
            f"Data Theft: {type_counts['Data Theft']} | "
            f"Internal Breach: {type_counts['Internal Breach']}"
        )
    
    def _handle_case_double_click(self):
        """Handle double-click on a case row."""
        self._open_selected_case()

    def _open_selected_case(self):
        """Open the currently selected case from the table."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        case_id_item = self.table.item(selected_row, 0)
        if case_id_item:
            case_id = int(case_id_item.text())
            self.case_selected.emit(case_id)
    
    def _format_date(self, date_str: str) -> str:
        """Format date string."""
        if not date_str:
            return 'Unknown'
        
        try:
            if isinstance(date_str, str):
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = date_str
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return str(date_str) if date_str else 'Unknown'
