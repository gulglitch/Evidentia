"""
Case Home Screen
Simple case workspace hub for navigating Sprint 2 modules.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from datetime import datetime

from backend.app.database import Database


class CaseHome(QWidget):
    """Hub screen for a selected case."""

    back_to_cases_requested = Signal()
    upload_requested = Signal()
    evidence_requested = Signal()
    timeline_requested = Signal()
    analytics_requested = Signal()

    def __init__(self, case_id: int = None):
        super().__init__()
        self.database = Database()
        self.case_id = case_id
        self.investigator_name = None
        self._setup_ui()
        self._apply_styles()
        if self.case_id:
            self._refresh_case_summary()

    def set_case_id(self, case_id: int):
        """Set active case and refresh summary."""
        self.case_id = case_id
        self._refresh_case_summary()

    def set_investigator_name(self, investigator_name: str):
        """Set investigator display name from signed-in user."""
        self.investigator_name = investigator_name
        self._refresh_case_summary()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(16)

        header_layout = QHBoxLayout()

        back_btn = QPushButton("‹ Cases")
        back_btn.setFont(QFont("Arial", 12))
        back_btn.setFixedSize(110, 35)
        back_btn.clicked.connect(self.back_to_cases_requested.emit)
        header_layout.addWidget(back_btn)

        header_layout.addStretch()

        self.title_label = QLabel("Case Workspace")
        self.title_label.setFont(QFont("Arial", 26, QFont.Bold))
        self.title_label.setStyleSheet("color: #00d4aa;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        upload_btn = QPushButton("+ Upload More Evidence")
        upload_btn.setFixedSize(220, 40)
        upload_btn.clicked.connect(self.upload_requested.emit)
        header_layout.addWidget(upload_btn)

        main_layout.addLayout(header_layout)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        summary_frame = QFrame()
        summary_frame.setObjectName("infoCard")
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(20, 16, 20, 16)
        summary_layout.setSpacing(8)
        summary_title = QLabel("Case Summary")
        summary_title.setFont(QFont("Arial", 12, QFont.Bold))
        summary_title.setStyleSheet("color: #40e0d0;")
        self.investigator_label = QLabel("Investigator: N/A")
        self.team_members_label = QLabel("Team Members: N/A")
        summary_layout.addWidget(summary_title)
        summary_layout.addWidget(self.investigator_label)
        summary_layout.addWidget(self.team_members_label)
        summary_layout.addStretch()
        cards_layout.addWidget(summary_frame)

        dates_frame = QFrame()
        dates_frame.setObjectName("infoCard")
        dates_layout = QVBoxLayout(dates_frame)
        dates_layout.setContentsMargins(20, 16, 20, 16)
        dates_layout.setSpacing(8)
        dates_title = QLabel("Case Dates")
        dates_title.setFont(QFont("Arial", 12, QFont.Bold))
        dates_title.setStyleSheet("color: #40e0d0;")
        self.opened_label = QLabel("Opened: N/A")
        self.closed_label = QLabel("Closed: N/A")
        dates_layout.addWidget(dates_title)
        dates_layout.addWidget(self.opened_label)
        dates_layout.addWidget(self.closed_label)
        dates_layout.addStretch()
        cards_layout.addWidget(dates_frame)

        evidence_frame = QFrame()
        evidence_frame.setObjectName("infoCard")
        evidence_layout = QVBoxLayout(evidence_frame)
        evidence_layout.setContentsMargins(20, 16, 20, 16)
        evidence_layout.setSpacing(8)
        evidence_title = QLabel("Evidence Summary")
        evidence_title.setFont(QFont("Arial", 12, QFont.Bold))
        evidence_title.setStyleSheet("color: #40e0d0;")
        self.total_files_label = QLabel("Total Files: 0")
        self.analyzed_label = QLabel("Analyzed: 0")
        self.pending_label = QLabel("Pending: 0")
        evidence_layout.addWidget(evidence_title)
        evidence_layout.addWidget(self.total_files_label)
        evidence_layout.addWidget(self.analyzed_label)
        evidence_layout.addWidget(self.pending_label)
        evidence_layout.addStretch()
        cards_layout.addWidget(evidence_frame)

        main_layout.addLayout(cards_layout)

        overview_frame = QFrame()
        overview_frame.setObjectName("overviewFrame")
        overview_layout = QVBoxLayout(overview_frame)
        overview_layout.setContentsMargins(20, 16, 20, 16)
        overview_layout.setSpacing(10)

        overview_title = QLabel("Case Overview")
        overview_title.setAlignment(Qt.AlignCenter)
        overview_title.setFont(QFont("Arial", 14, QFont.Bold))
        overview_title.setStyleSheet("color: #40e0d0;")
        overview_layout.addWidget(overview_title)

        self.overview_text = QLabel("No case overview available.")
        self.overview_text.setWordWrap(True)
        self.overview_text.setFont(QFont("Arial", 11))
        self.overview_text.setStyleSheet("color: #e0e6ed;")
        overview_layout.addWidget(self.overview_text)

        main_layout.addWidget(overview_frame)

        # Distribute vertical space more evenly in fullscreen layouts.
        main_layout.addStretch(1)

        module_title = QLabel("Choose Module")
        module_title.setFont(QFont("Arial", 16, QFont.Bold))
        module_title.setStyleSheet("color: #00d4aa;")
        main_layout.addWidget(module_title)

        module_layout = QVBoxLayout()
        module_layout.setSpacing(16)

        evidence_btn = QPushButton("Evidence Management")
        evidence_btn.setObjectName("moduleBtn")
        evidence_btn.setFixedWidth(360)
        evidence_btn.clicked.connect(self.evidence_requested.emit)
        module_layout.addWidget(evidence_btn, 0, Qt.AlignHCenter)

        timeline_btn = QPushButton("Timeline View")
        timeline_btn.setObjectName("moduleBtn")
        timeline_btn.setFixedWidth(360)
        timeline_btn.clicked.connect(self.timeline_requested.emit)
        module_layout.addWidget(timeline_btn, 0, Qt.AlignHCenter)

        analytics_btn = QPushButton("Analytics View")
        analytics_btn.setObjectName("moduleBtn")
        analytics_btn.setFixedWidth(360)
        analytics_btn.clicked.connect(self.analytics_requested.emit)
        module_layout.addWidget(analytics_btn, 0, Qt.AlignHCenter)

        module_layout.setAlignment(Qt.AlignTop)

        main_layout.addLayout(module_layout)

        main_layout.addStretch(1)

    def _refresh_case_summary(self):
        """Refresh summary details for current case."""
        if not self.case_id:
            return

        case = self.database.get_case(self.case_id)
        if case:
            self.title_label.setText(f"Case Workspace - {case.get('name', 'Unknown')}")

            investigator = self.investigator_name or case.get('investigator') or 'Assigned Investigator'
            team_members = case.get('team_members', 'N/A')
            self.investigator_label.setText(f"Investigator: {investigator}")
            self.team_members_label.setText(f"Team Members: {team_members}")

            opened = self._format_case_date(case.get('created_at'))
            closed = "In Progress"
            if str(case.get('status', '')).lower() == 'closed':
                closed = self._format_case_date(case.get('updated_at'))
            self.opened_label.setText(f"Opened: {opened}")
            self.closed_label.setText(f"Closed: {closed}")

            description = case.get('description', '')
            if description:
                self.overview_text.setText(description)
            else:
                self.overview_text.setText(
                    f"This investigation is categorized as {case.get('case_type', 'N/A')} and is currently "
                    f"marked as {case.get('status', 'Open')}."
                )

        evidence = self.database.get_evidence_for_case(self.case_id)
        total = len(evidence)
        pending = sum(1 for item in evidence if item.get('status', 'Pending') == 'Pending')
        analyzed = sum(1 for item in evidence if item.get('status', 'Pending') == 'Analyzed')
        self.total_files_label.setText(f"Total Files: {total}")
        self.analyzed_label.setText(f"Analyzed: {analyzed}")
        self.pending_label.setText(f"Pending: {pending}")

    def _format_case_date(self, date_str):
        """Format case date fields for summary cards."""
        if not date_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            return dt.strftime('%d %b %Y')
        except Exception:
            return str(date_str)

    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QLabel {
                background: transparent;
            }
            QFrame#infoCard {
                background-color: #0d2137;
                border: 1px solid #1a4a5a;
                border-radius: 0px;
            }
            QFrame#overviewFrame {
                background-color: #143947;
                border: 1px solid #1a4a5a;
                border-radius: 0px;
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
            QPushButton#moduleBtn {
                min-height: 50px;
                font-size: 14px;
                text-align: center;
            }
        """)
