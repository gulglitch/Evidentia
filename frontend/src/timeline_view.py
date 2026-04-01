"""
Timeline View Screen
Interactive timeline visualization showing evidence chronologically
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem,
    QGraphicsTextItem, QDateEdit, QComboBox, QFrame, QScrollArea,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QRectF, QDate, QPointF
from PySide6.QtGui import QFont, QColor, QPen, QBrush, QPainter
from datetime import datetime
from typing import List, Dict, Any, Optional

from backend.app.database import Database
from backend.app.timeline_generator import TimelineGenerator


class TimelineMarker(QGraphicsEllipseItem):
    """Custom graphics item for evidence markers on timeline."""
    
    def __init__(self, evidence: Dict[str, Any], x: float, y: float, radius: float = 8):
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.evidence = evidence
        self.setPos(x, y)
        
        # Set color based on file type
        color = self._get_type_color(evidence.get('file_extension', ''))
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor("#e0e6ed"), 2))
        
        # Make clickable
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.PointingHandCursor)
    
    def _get_type_color(self, extension: str) -> QColor:
        """Get color based on file type."""
        ext = extension.lower()
        
        if ext in ['.txt', '.doc', '.docx', '.pdf']:
            return QColor("#3b82f6")  # Blue for documents
        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
            return QColor("#10b981")  # Green for images
        elif ext in ['.log']:
            return QColor("#f59e0b")  # Orange for logs
        elif ext in ['.csv', '.xlsx']:
            return QColor("#8b5cf6")  # Purple for spreadsheets
        else:
            return QColor("#6b7280")  # Gray for other
    
    def hoverEnterEvent(self, event):
        """Handle hover enter - make marker larger."""
        self.setScale(1.3)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle hover leave - restore size."""
        self.setScale(1.0)
        super().hoverLeaveEvent(event)


class TimelineView(QWidget):
    """Timeline view screen showing evidence chronologically."""
    
    back_requested = Signal()
    evidence_selected = Signal(int)  # Emits evidence ID
    
    def __init__(self, case_id: int = None):
        super().__init__()
        self.case_id = case_id
        self.database = Database()
        self.timeline_gen = TimelineGenerator(self.database)
        self.timeline_data = None
        self.markers = []
        self._setup_ui()
        self._apply_styles()
        if case_id:
            self.load_timeline()
    
    def set_case_id(self, case_id: int):
        """Set the current case ID and reload timeline."""
        self.case_id = case_id
        self.load_timeline()
    
    def _setup_ui(self):
        """Setup the timeline UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("‹ Back")
        back_btn.setFont(QFont("Arial", 12))
        back_btn.setFixedSize(100, 35)
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)
        
        header_layout.addStretch()
        
        # Title
        self.title_label = QLabel("Evidence Timeline")
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.title_label.setStyleSheet("color: #00d4aa;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # File count
        self.count_label = QLabel("0 files")
        self.count_label.setFont(QFont("Arial", 12))
        self.count_label.setStyleSheet("color: #8899aa;")
        header_layout.addWidget(self.count_label)
        
        main_layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)
        
        # Date field selector
        date_field_label = QLabel("Date Field:")
        date_field_label.setFont(QFont("Arial", 12))
        filter_layout.addWidget(date_field_label)
        
        self.date_field_combo = QComboBox()
        self.date_field_combo.addItems(["Modified Date", "Created Date"])
        self.date_field_combo.setFixedWidth(150)
        self.date_field_combo.setMinimumHeight(35)
        self.date_field_combo.currentTextChanged.connect(self._on_date_field_changed)
        filter_layout.addWidget(self.date_field_combo)
        
        filter_layout.addSpacing(20)
        
        # Date range filter
        from_label = QLabel("From:")
        from_label.setFont(QFont("Arial", 12))
        filter_layout.addWidget(from_label)
        
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setFixedWidth(150)
        self.from_date.setMinimumHeight(35)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.from_date)
        
        to_label = QLabel("To:")
        to_label.setFont(QFont("Arial", 12))
        filter_layout.addWidget(to_label)
        
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setFixedWidth(150)
        self.to_date.setMinimumHeight(35)
        self.to_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.to_date)
        
        # Apply filter button
        apply_btn = QPushButton("Apply Filter")
        apply_btn.setFixedSize(120, 35)
        apply_btn.clicked.connect(self._apply_date_filter)
        filter_layout.addWidget(apply_btn)
        
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.setFixedSize(80, 35)
        reset_btn.clicked.connect(self._reset_filters)
        filter_layout.addWidget(reset_btn)
        
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # Timeline canvas
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setMinimumHeight(400)
        
        main_layout.addWidget(self.view)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(20)
        
        legend_label = QLabel("Legend:")
        legend_label.setFont(QFont("Arial", 11, QFont.Bold))
        legend_layout.addWidget(legend_label)
        
        # Color legend
        colors = [
            ("#3b82f6", "Documents"),
            ("#10b981", "Images"),
            ("#f59e0b", "Logs"),
            ("#8b5cf6", "Spreadsheets"),
            ("#6b7280", "Other")
        ]
        
        for color, label in colors:
            color_box = QLabel("●")
            color_box.setStyleSheet(f"color: {color}; font-size: 16px;")
            legend_layout.addWidget(color_box)
            
            text_label = QLabel(label)
            text_label.setFont(QFont("Arial", 10))
            legend_layout.addWidget(text_label)
        
        legend_layout.addStretch()
        main_layout.addLayout(legend_layout)
    
    def _apply_styles(self):
        """Apply timeline styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #0a1929;
                color: #e0e6ed;
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
            QComboBox, QDateEdit {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e6ed;
            }
            QComboBox:focus, QDateEdit:focus {
                border-color: #40e0d0;
            }
            QGraphicsView {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
            }
        """)
    
    def load_timeline(self):
        """Load timeline data and render."""
        if not self.case_id:
            return
        
        # Get case info
        case = self.database.get_case(self.case_id)
        if case:
            self.title_label.setText(f"Timeline - {case['name']}")
        
        # Get timeline data
        date_field = 'modified_time' if self.date_field_combo.currentText() == "Modified Date" else 'created_time'
        self.timeline_data = self.timeline_gen.get_timeline_data(self.case_id, date_field=date_field)
        
        # Update count
        count = self.timeline_data['total_count']
        self.count_label.setText(f"{count} file{'s' if count != 1 else ''}")
        
        # Render timeline
        self._render_timeline()
    
    def _render_timeline(self):
        """Render the timeline visualization."""
        self.scene.clear()
        self.markers = []
        
        if not self.timeline_data or not self.timeline_data['evidence']:
            # Show empty message
            text = self.scene.addText("No evidence to display")
            text.setDefaultTextColor(QColor("#8899aa"))
            text.setFont(QFont("Arial", 14))
            return
        
        evidence_list = self.timeline_data['evidence']
        date_field = self.timeline_data['date_field']
        
        # Calculate timeline dimensions
        margin = 50
        timeline_y = 200
        timeline_width = max(1200, len(evidence_list) * 80)
        
        # Draw timeline axis
        axis_line = QGraphicsLineItem(margin, timeline_y, timeline_width - margin, timeline_y)
        axis_line.setPen(QPen(QColor("#40e0d0"), 3))
        self.scene.addItem(axis_line)
        
        # Get date range
        date_range = self.timeline_data['date_range']
        if not date_range[0] or not date_range[1]:
            return
        
        start_date = self._parse_date(date_range[0])
        end_date = self._parse_date(date_range[1])
        
        if not start_date or not end_date:
            return
        
        # Calculate time span
        time_span = (end_date - start_date).total_seconds()
        if time_span == 0:
            time_span = 1  # Avoid division by zero
        
        # Plot evidence markers
        for evidence in evidence_list:
            date_str = evidence.get(date_field)
            if not date_str:
                continue
            
            evidence_date = self._parse_date(date_str)
            if not evidence_date:
                continue
            
            # Calculate x position
            time_offset = (evidence_date - start_date).total_seconds()
            x_ratio = time_offset / time_span
            x_pos = margin + (x_ratio * (timeline_width - 2 * margin))
            
            # Create marker
            marker = TimelineMarker(evidence, x_pos, timeline_y)
            self.scene.addItem(marker)
            self.markers.append(marker)
            
            # Format date for tooltip
            date_formatted = self._format_date_detailed(date_str)
            
            # Add enhanced tooltip
            marker.setToolTip(
                f"File: {evidence.get('file_name', 'Unknown')}\n"
                f"Date: {date_formatted}\n"
                f"Size: {self._format_size(evidence.get('file_size', 0))}\n"
                f"Type: {evidence.get('file_extension', 'Unknown')}\n"
                f"Status: {evidence.get('status', 'Pending')}"
            )
            
            # Add small date label below marker (only for sparse timelines)
            if len(evidence_list) <= 20:  # Only show labels if not too crowded
                date_label = self.scene.addText(evidence_date.strftime('%m/%d'))
                date_label.setDefaultTextColor(QColor("#6b7280"))
                date_label.setFont(QFont("Arial", 8))
                label_width = date_label.boundingRect().width()
                date_label.setPos(x_pos - label_width / 2, timeline_y + 35)
                date_label.setOpacity(0.7)
        
        # Add date labels
        self._add_date_labels(start_date, end_date, margin, timeline_width, timeline_y)
        
        # Add milestones
        self._add_milestones(start_date, end_date, time_span, margin, timeline_width, timeline_y)
        
        # Set scene rect
        self.scene.setSceneRect(0, 0, timeline_width, 400)
    
    def _add_date_labels(self, start_date, end_date, margin, timeline_width, timeline_y):
        """Add date labels to timeline with intermediate dates."""
        from datetime import timedelta
        
        # Calculate time span
        time_span = (end_date - start_date).days
        
        # Determine number of labels based on span
        if time_span <= 7:
            num_labels = time_span + 1  # Show every day
        elif time_span <= 30:
            num_labels = 8  # Show ~weekly
        elif time_span <= 90:
            num_labels = 6  # Show ~bi-weekly
        elif time_span <= 365:
            num_labels = 8  # Show ~monthly
        else:
            num_labels = 10  # Show ~quarterly
        
        # Ensure at least 2 labels (start and end)
        num_labels = max(2, min(num_labels, 12))
        
        # Add date labels at intervals
        for i in range(num_labels):
            # Calculate position
            ratio = i / (num_labels - 1) if num_labels > 1 else 0
            x_pos = margin + (ratio * (timeline_width - 2 * margin))
            
            # Calculate date
            if time_span > 0:
                days_offset = int(time_span * ratio)
                current_date = start_date + timedelta(days=days_offset)
            else:
                current_date = start_date
            
            # Format date based on span
            if time_span <= 30:
                date_str = current_date.strftime('%b %d')  # "Jan 15"
            elif time_span <= 365:
                date_str = current_date.strftime('%b %d')  # "Jan 15"
            else:
                date_str = current_date.strftime('%Y-%m')  # "2026-01"
            
            # Add text label
            text = self.scene.addText(date_str)
            text.setDefaultTextColor(QColor("#8899aa"))
            text.setFont(QFont("Arial", 10))
            
            # Center text under position
            text_width = text.boundingRect().width()
            text.setPos(x_pos - text_width / 2, timeline_y + 15)
            
            # Add tick mark
            tick = QGraphicsLineItem(x_pos, timeline_y - 5, x_pos, timeline_y + 5)
            tick.setPen(QPen(QColor("#40e0d0"), 2))
            self.scene.addItem(tick)
        
        # Add year labels at top if span > 1 year
        if time_span > 365:
            start_year = start_date.year
            end_year = end_date.year
            
            for year in range(start_year, end_year + 1):
                # Find position for this year
                year_start = datetime(year, 1, 1)
                if year_start < start_date:
                    year_start = start_date
                
                days_from_start = (year_start - start_date).days
                ratio = days_from_start / time_span if time_span > 0 else 0
                x_pos = margin + (ratio * (timeline_width - 2 * margin))
                
                # Add year label
                year_text = self.scene.addText(str(year))
                year_text.setDefaultTextColor(QColor("#00d4aa"))
                year_text.setFont(QFont("Arial", 12, QFont.Bold))
                year_text.setPos(x_pos - 20, timeline_y - 60)
    
    def _add_milestones(self, start_date, end_date, time_span, margin, timeline_width, timeline_y):
        """Add milestone markers to timeline."""
        milestones = self.timeline_data.get('milestones', [])
        
        for milestone in milestones:
            milestone_date_str = milestone.get('milestone_date')
            if not milestone_date_str:
                continue
            
            milestone_date = self._parse_date(milestone_date_str)
            if not milestone_date:
                continue
            
            # Calculate x position
            time_offset = (milestone_date - start_date).total_seconds()
            x_ratio = time_offset / time_span
            x_pos = margin + (x_ratio * (timeline_width - 2 * margin))
            
            # Draw vertical line
            line = QGraphicsLineItem(x_pos, timeline_y - 50, x_pos, timeline_y + 50)
            line.setPen(QPen(QColor("#f59e0b"), 2, Qt.DashLine))
            self.scene.addItem(line)
            
            # Add label
            label = self.scene.addText(milestone.get('milestone_name', 'Milestone'))
            label.setDefaultTextColor(QColor("#f59e0b"))
            label.setFont(QFont("Arial", 10, QFont.Bold))
            label.setPos(x_pos - 30, timeline_y - 80)
    
    def _apply_date_filter(self):
        """Apply date range filter."""
        if not self.case_id:
            return
        
        from_date_str = self.from_date.date().toString(Qt.ISODate)
        to_date_str = self.to_date.date().toString(Qt.ISODate)
        date_field = 'modified_time' if self.date_field_combo.currentText() == "Modified Date" else 'created_time'
        
        self.timeline_data = self.timeline_gen.get_timeline_data(
            self.case_id, 
            date_from=from_date_str, 
            date_to=to_date_str,
            date_field=date_field
        )
        
        count = self.timeline_data['total_count']
        self.count_label.setText(f"{count} file{'s' if count != 1 else ''} (filtered)")
        
        self._render_timeline()
    
    def _reset_filters(self):
        """Reset all filters."""
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.to_date.setDate(QDate.currentDate())
        self.load_timeline()
    
    def _on_date_field_changed(self):
        """Handle date field change."""
        self.load_timeline()
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None
        
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def _format_date(self, date_str: str) -> str:
        """Format date string."""
        dt = self._parse_date(date_str)
        return dt.strftime('%Y-%m-%d %H:%M') if dt else 'Unknown'
    
    def _format_date_detailed(self, date_str: str) -> str:
        """Format date string with more detail."""
        dt = self._parse_date(date_str)
        if dt:
            return dt.strftime('%B %d, %Y at %H:%M:%S')  # "January 15, 2026 at 14:30:00"
        return 'Unknown'
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
