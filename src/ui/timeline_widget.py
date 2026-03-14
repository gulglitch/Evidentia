"""
Timeline Widget Module
Interactive timeline view for visualizing evidence chronology
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from typing import List, Dict, Any
from datetime import datetime


class TimelineItem(QWidget):
    """Individual item on the timeline."""
    
    clicked = Signal(int)  # evidence_id
    
    def __init__(self, evidence_id: int, title: str, date: str, risk: str = "Low"):
        super().__init__()
        self.evidence_id = evidence_id
        self.title = title
        self.date = date
        self.risk = risk
        
        self.setFixedSize(120, 80)
        self.setCursor(Qt.PointingHandCursor)
    
    def paintEvent(self, event):
        """Paint the timeline item."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background color based on risk
        colors = {
            'Low': QColor('#a6e3a1'),
            'Medium': QColor('#f9e2af'),
            'High': QColor('#f38ba8'),
        }
        bg_color = colors.get(self.risk, QColor('#89b4fa'))
        
        # Draw rounded rectangle
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height() - 20, 5, 5)
        
        # Draw text
        painter.setPen(QPen(QColor('#1e1e2e')))
        
        # Title (truncated)
        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setBold(True)
        painter.setFont(title_font)
        
        title = self.title[:15] + '...' if len(self.title) > 15 else self.title
        painter.drawText(5, 20, title)
        
        # Date
        date_font = QFont()
        date_font.setPointSize(8)
        painter.setFont(date_font)
        painter.drawText(5, 40, self.date)
        
        # Draw connector line
        painter.setPen(QPen(QColor('#89b4fa'), 2))
        painter.drawLine(self.width() // 2, self.height() - 20, self.width() // 2, self.height())
    
    def mousePressEvent(self, event):
        """Handle mouse click."""
        self.clicked.emit(self.evidence_id)


class TimelineWidget(QWidget):
    """Timeline visualization widget."""
    
    item_selected = Signal(int)  # evidence_id
    
    def __init__(self):
        super().__init__()
        self.items = []
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the timeline UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Investigation Timeline")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #cdd6f4;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(15)
        
        for risk, color in [("Low", "#a6e3a1"), ("Medium", "#f9e2af"), ("High", "#f38ba8")]:
            indicator = QFrame()
            indicator.setFixedSize(12, 12)
            indicator.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
            legend_layout.addWidget(indicator)
            
            label = QLabel(risk)
            label.setStyleSheet("color: #a6adc8; font-size: 11px;")
            legend_layout.addWidget(label)
        
        header_layout.addLayout(legend_layout)
        layout.addLayout(header_layout)
        
        # Scroll area for timeline
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #313244;
                border-radius: 5px;
                background-color: #181825;
            }
        """)
        
        # Timeline container
        self.timeline_container = QWidget()
        self.timeline_layout = QHBoxLayout(self.timeline_container)
        self.timeline_layout.setContentsMargins(20, 30, 20, 10)
        self.timeline_layout.setSpacing(20)
        self.timeline_layout.addStretch()
        
        scroll.setWidget(self.timeline_container)
        layout.addWidget(scroll)
        
        # Timeline baseline
        self.baseline = QFrame()
        self.baseline.setFixedHeight(3)
        self.baseline.setStyleSheet("background-color: #89b4fa;")
    
    def _apply_styles(self):
        """Apply widget styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
            }
        """)
    
    def load_evidence(self, evidence_list: List[Dict[str, Any]]):
        """Load evidence onto the timeline."""
        # Clear existing items
        self._clear_timeline()
        
        # Sort by modified date
        sorted_evidence = sorted(
            evidence_list,
            key=lambda x: x.get('modified_time', datetime.min)
        )
        
        for evidence in sorted_evidence:
            modified = evidence.get('modified_time', '')
            if isinstance(modified, datetime):
                date_str = modified.strftime('%Y-%m-%d')
            else:
                date_str = str(modified)[:10]
            
            item = TimelineItem(
                evidence_id=evidence.get('id', 0),
                title=evidence.get('file_name', 'Unknown'),
                date=date_str,
                risk=evidence.get('risk_level', 'Low')
            )
            item.clicked.connect(self.item_selected.emit)
            
            self.timeline_layout.insertWidget(self.timeline_layout.count() - 1, item)
            self.items.append(item)
    
    def _clear_timeline(self):
        """Clear all items from the timeline."""
        for item in self.items:
            self.timeline_layout.removeWidget(item)
            item.deleteLater()
        self.items.clear()
    
    def add_milestone(self, title: str, date: str, milestone_type: str = "default"):
        """Add a milestone marker to the timeline."""
        # Milestones can be used for case events like
        # "Evidence Collected", "Analysis Started", "Report Generated"
        pass  # TODO: Implement milestones
    
    def paintEvent(self, event):
        """Paint the timeline baseline."""
        super().paintEvent(event)
        # The baseline is drawn by the scroll area's stylesheet
