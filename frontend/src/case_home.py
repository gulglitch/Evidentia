"""
Case Home Screen
Simple case workspace hub for navigating Sprint 2 modules.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve, Property, QPoint
from PySide6.QtGui import QFont, QColor
from datetime import datetime

from backend.app.database import Database


class AnimatedModuleButton(QPushButton):
    """Custom animated button with glow effect for module selection."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("moduleBtn")
        self.setMinimumSize(280, 120)
        self.setCursor(Qt.PointingHandCursor)
        
        # Add glow effect
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(20)
        self.glow.setColor(QColor(64, 224, 208, 100))
        self.glow.setOffset(0, 0)
        self.setGraphicsEffect(self.glow)
        
        # Animation for hover
        self._glow_intensity = 100
        self.glow_animation = QPropertyAnimation(self, b"glowIntensity")
        self.glow_animation.setDuration(300)
        self.glow_animation.setEasingCurve(QEasingCurve.InOutQuad)
    
    def get_glow_intensity(self):
        return self._glow_intensity
    
    def set_glow_intensity(self, value):
        self._glow_intensity = value
        self.glow.setColor(QColor(64, 224, 208, value))
    
    glowIntensity = Property(int, get_glow_intensity, set_glow_intensity)
    
    def enterEvent(self, event):
        """Animate glow on hover."""
        self.glow_animation.stop()
        self.glow_animation.setStartValue(self._glow_intensity)
        self.glow_animation.setEndValue(200)
        self.glow_animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Fade glow on leave."""
        self.glow_animation.stop()
        self.glow_animation.setStartValue(self._glow_intensity)
        self.glow_animation.setEndValue(100)
        self.glow_animation.start()
        super().leaveEvent(event)


class CaseHome(QWidget):
    """Hub screen for a selected case."""

    back_to_cases_requested = Signal()
    upload_requested = Signal()
    evidence_requested = Signal()
    timeline_requested = Signal()
    analytics_requested = Signal()
    report_requested = Signal()

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
        
        # Add shadow effect to summary card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        summary_frame.setGraphicsEffect(shadow)
        
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
        
        # Add shadow effect to dates card
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(15)
        shadow2.setColor(QColor(0, 0, 0, 80))
        shadow2.setOffset(0, 4)
        dates_frame.setGraphicsEffect(shadow2)
        
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
        
        # Add shadow effect to evidence card
        shadow3 = QGraphicsDropShadowEffect()
        shadow3.setBlurRadius(15)
        shadow3.setColor(QColor(0, 0, 0, 80))
        shadow3.setOffset(0, 4)
        evidence_frame.setGraphicsEffect(shadow3)
        
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
        
        # Add shadow effect to overview frame
        shadow4 = QGraphicsDropShadowEffect()
        shadow4.setBlurRadius(15)
        shadow4.setColor(QColor(0, 0, 0, 100))
        shadow4.setOffset(0, 4)
        overview_frame.setGraphicsEffect(shadow4)
        
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

        # 2x2 Grid layout for module buttons
        module_grid = QGridLayout()
        module_grid.setSpacing(20)
        module_grid.setContentsMargins(40, 10, 40, 10)

        # Create animated buttons without icons
        evidence_btn = AnimatedModuleButton("Evidence Management")
        evidence_btn.clicked.connect(self.evidence_requested.emit)
        module_grid.addWidget(evidence_btn, 0, 0)

        timeline_btn = AnimatedModuleButton("Timeline View")
        timeline_btn.clicked.connect(self.timeline_requested.emit)
        module_grid.addWidget(timeline_btn, 0, 1)

        analytics_btn = AnimatedModuleButton("Analytics View")
        analytics_btn.clicked.connect(self.analytics_requested.emit)
        module_grid.addWidget(analytics_btn, 1, 0)

        report_btn = AnimatedModuleButton("Generate Final Report")
        report_btn.clicked.connect(self.report_requested.emit)
        module_grid.addWidget(report_btn, 1, 1)

        main_layout.addLayout(module_grid)

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
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d2137, stop:1 #0a1929);
                border: 2px solid #1a4a5a;
                border-radius: 10px;
                padding: 4px;
            }
            QFrame#infoCard:hover {
                border: 2px solid #40e0d0;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a4a5a, stop:1 #0d2137);
            }
            QFrame#overviewFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #143947, stop:0.5 #0d2137, stop:1 #143947);
                border: 2px solid #2a5a6a;
                border-radius: 10px;
                padding: 4px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #40e0d0, stop:1 #2dd4bf);
                color: #0a1929;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2dd4bf, stop:1 #00d4aa);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4aa, stop:1 #00b899);
            }
            QPushButton#moduleBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0d2137, stop:0.5 #1a4a5a, stop:1 #0d2137);
                color: #40e0d0;
                border: 2px solid #40e0d0;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
                padding: 20px;
            }
            QPushButton#moduleBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a4a5a, stop:0.5 #2a5a6a, stop:1 #1a4a5a);
                color: #00d4aa;
                border: 2px solid #00d4aa;
            }
            QPushButton#moduleBtn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a1929, stop:0.5 #143947, stop:1 #0a1929);
                border: 2px solid #2dd4bf;
            }
        """)
