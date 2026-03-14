"""
Dashboard Module
Investigation Statistics Dashboard - Main hub screen
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QFrame, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ..core.database import Database


class StatCard(QFrame):
    """Individual statistic card widget."""
    
    def __init__(self, title: str, value: str, button_text: str = None):
        super().__init__()
        self._setup_ui(title, value, button_text)
        self._apply_styles()
    
    def _setup_ui(self, title: str, value: str, button_text: str):
        """Setup the stat card UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setFont(QFont("Arial", 48, QFont.Bold))
        layout.addWidget(value_label)
        
        # Button (optional)
        if button_text:
            button = QPushButton(button_text)
            button.setMinimumHeight(40)
            button.setMaximumWidth(200)
            layout.addWidget(button, alignment=Qt.AlignCenter)
    
    def _apply_styles(self):
        """Apply card styles."""
        self.setStyleSheet("""
            QFrame {
                background-color: #122a3a;
                border: 1px solid #1a4a5a;
                border-radius: 8px;
                padding: 30px;
                min-width: 250px;
                min-height: 200px;
            }
            QLabel {
                color: #00d4aa;
            }
            QPushButton {
                background-color: #40e0d0;
                color: #0a1929;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
        """)


class StatusDistributionWidget(QFrame):
    """Case status distribution with progress bars."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the status distribution UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Case Status Distribution")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Status bars
        self._add_status_bar(layout, "Open Cases", 38, 100)
        self._add_status_bar(layout, "In Review", 21, 100)
        self._add_status_bar(layout, "Closed Cases", 186, 245)
    
    def _add_status_bar(self, layout, label: str, value: int, max_value: int):
        """Add a status progress bar."""
        row_layout = QHBoxLayout()
        
        # Label
        label_widget = QLabel(label)
        label_widget.setMinimumWidth(100)
        row_layout.addWidget(label_widget)
        
        # Progress bar
        progress = QProgressBar()
        progress.setRange(0, max_value)
        progress.setValue(value)
        progress.setFormat(f"{value}")
        row_layout.addWidget(progress)
        
        layout.addLayout(row_layout)
    
    def _apply_styles(self):
        """Apply status distribution styles."""
        self.setStyleSheet("""
            QFrame {
                background-color: #122a3a;
                border: 1px solid #1a4a5a;
                border-radius: 8px;
                padding: 20px;
            }
            QLabel {
                color: #00d4aa;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #0d2137;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #40e0d0;
                border-radius: 4px;
            }
        """)


class CaseTypesWidget(QFrame):
    """Case types with circle badges."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the case types UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Case Types")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Type badges in a grid
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(20)
        
        types = [
            ("Cybercrime", "42"),
            ("Financial Fraud", "68"),
            ("Data Theft", "31"),
            ("Internal Breach", "12")
        ]
        
        for type_name, count in types:
            badge_layout = QVBoxLayout()
            badge_layout.setAlignment(Qt.AlignCenter)
            
            # Circle badge
            badge = QLabel(count)
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(50, 50)
            badge.setStyleSheet("""
                QLabel {
                    background-color: #2a6a7a;
                    color: #ffffff;
                    border-radius: 25px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            badge_layout.addWidget(badge)
            
            # Label
            label = QLabel(type_name.replace(" ", "\n"))
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 10))
            badge_layout.addWidget(label)
            
            badges_layout.addLayout(badge_layout)
        
        layout.addLayout(badges_layout)
    
    def _apply_styles(self):
        """Apply case types styles."""
        self.setStyleSheet("""
            QFrame {
                background-color: #122a3a;
                border: 1px solid #1a4a5a;
                border-radius: 8px;
                padding: 20px;
            }
            QLabel {
                color: #00d4aa;
            }
        """)


class Dashboard(QWidget):
    """Investigation Statistics Dashboard."""
    
    new_case_requested = Signal()
    open_case_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.database = Database()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header = QLabel("Investigation Statistics Dashboard")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 28, QFont.Bold))
        layout.addWidget(header)
        
        # Top row - Stats cards
        top_row = QHBoxLayout()
        top_row.setSpacing(30)
        
        # Total Cases card
        total_cases_card = StatCard("Total Cases", "245", "New Case")
        total_cases_card.findChild(QPushButton).clicked.connect(self.new_case_requested.emit)
        top_row.addWidget(total_cases_card)
        
        # Team Members card
        team_card = StatCard("Team Members", "15", "Add Investigator")
        top_row.addWidget(team_card)
        
        # Case Status Distribution
        status_widget = StatusDistributionWidget()
        top_row.addWidget(status_widget)
        
        layout.addLayout(top_row)
        
        # Bottom row
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(30)
        
        # Case Types
        case_types_widget = CaseTypesWidget()
        bottom_row.addWidget(case_types_widget)
        
        # Report Generation Summary
        report_card = QFrame()
        report_layout = QVBoxLayout(report_card)
        report_layout.setSpacing(15)
        report_layout.setContentsMargins(30, 30, 30, 30)
        
        report_title = QLabel("Report Generation Summary")
        report_title.setFont(QFont("Arial", 16, QFont.Bold))
        report_layout.addWidget(report_title)
        
        # Stats with better spacing
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(10)
        
        total_files_label = QLabel("Total Evidence Files: 126")
        total_files_label.setFont(QFont("Arial", 14))
        stats_layout.addWidget(total_files_label)
        
        analyzed_label = QLabel("Files Analyzed: 94")
        analyzed_label.setFont(QFont("Arial", 14))
        stats_layout.addWidget(analyzed_label)
        
        pending_label = QLabel("Pending Review: 32")
        pending_label.setFont(QFont("Arial", 14))
        stats_layout.addWidget(pending_label)
        
        report_layout.addLayout(stats_layout)
        
        generate_button = QPushButton("Generate Final Report")
        generate_button.setMinimumHeight(40)
        report_layout.addWidget(generate_button)
        
        report_card.setStyleSheet("""
            QFrame {
                background-color: #122a3a;
                border: 1px solid #1a4a5a;
                border-radius: 8px;
                padding: 30px;
                min-width: 300px;
            }
            QLabel {
                color: #00d4aa;
            }
            QPushButton {
                background-color: #40e0d0;
                color: #0a1929;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        bottom_row.addWidget(report_card)
        
        layout.addLayout(bottom_row)
        
        # Footer
        footer = QLabel("© 2026 Evidentia Forensics | Secure Digital Investigation Platform")
        footer.setAlignment(Qt.AlignCenter)
        footer.setFont(QFont("Arial", 12))
        footer.setStyleSheet("color: #40e0d0; background-color: #0d2137; padding: 15px; margin-top: 20px;")
        layout.addWidget(footer)
    
    def _apply_styles(self):
        """Apply dashboard styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
            }
        """)