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
from frontend.src.milestone_dialog import MilestoneDialog
from frontend.src.evidence_details_dialog import EvidenceDetailsDialog


class TimelineMarker(QGraphicsEllipseItem):
    """Custom graphics item for evidence markers on timeline."""
    
    def __init__(self, evidence: Dict[str, Any], x: float, y: float, radius: float = 8, parent_view=None):
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.evidence = evidence
        self.parent_view = parent_view
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
        self.setScale(1.5)
        self.setZValue(100)  # Bring to front
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle hover leave - restore size."""
        self.setScale(1.0)
        self.setZValue(0)
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse click - show evidence details."""
        if event.button() == Qt.LeftButton and self.parent_view:
            self.parent_view._show_evidence_details(self.evidence)
        super().mousePressEvent(event)


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
    
    def _add_case_progression_bar(self):
        """Add case progression stages bar."""
        progression_frame = QFrame()
        progression_frame.setFrameShape(QFrame.StyledPanel)
        progression_frame.setStyleSheet("""
            QFrame {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        progression_layout = QVBoxLayout(progression_frame)
        progression_layout.setSpacing(10)
        
        # Title
        prog_title = QLabel("Case Progression")
        prog_title.setFont(QFont("Arial", 14, QFont.Bold))
        prog_title.setStyleSheet("color: #00d4aa;")
        progression_layout.addWidget(prog_title)
        
        # Stages layout
        stages_layout = QHBoxLayout()
        stages_layout.setSpacing(0)
        
        # Define stages
        stages = [
            ("Case Created", "created"),
            ("Evidence Collected", "evidence"),
            ("Analysis In Progress", "analysis"),
            ("Review", "review"),
            ("Closed", "closed")
        ]
        
        # Get current case status
        current_status = "evidence"  # Default
        if self.case_id:
            case = self.database.get_case(self.case_id)
            if case:
                status = case.get('status', 'Active').lower()
                if status == 'active':
                    current_status = "analysis"
                elif status == 'closed':
                    current_status = "closed"
        
        # Determine which stages are complete
        stage_order = ["created", "evidence", "analysis", "review", "closed"]
        current_index = stage_order.index(current_status) if current_status in stage_order else 1
        
        for i, (stage_name, stage_id) in enumerate(stages):
            # Stage container
            stage_widget = QWidget()
            stage_layout = QVBoxLayout(stage_widget)
            stage_layout.setContentsMargins(5, 5, 5, 5)
            stage_layout.setSpacing(5)
            
            # Determine stage state
            is_complete = i < current_index
            is_current = i == current_index
            is_future = i > current_index
            
            # Stage icon/marker
            if is_complete:
                icon = QLabel("✓")
                icon.setStyleSheet("color: #10b981; font-size: 24px; font-weight: bold;")
            elif is_current:
                icon = QLabel("●")
                icon.setStyleSheet("color: #00d4aa; font-size: 24px;")
            else:
                icon = QLabel("○")
                icon.setStyleSheet("color: #6b7280; font-size: 24px;")
            
            icon.setAlignment(Qt.AlignCenter)
            stage_layout.addWidget(icon)
            
            # Stage label
            label = QLabel(stage_name)
            label.setFont(QFont("Arial", 9))
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignCenter)
            
            if is_complete:
                label.setStyleSheet("color: #10b981;")
            elif is_current:
                label.setStyleSheet("color: #00d4aa; font-weight: bold;")
            else:
                label.setStyleSheet("color: #6b7280;")
            
            stage_layout.addWidget(label)
            
            stages_layout.addWidget(stage_widget)
            
            # Add connector line (except after last stage)
            if i < len(stages) - 1:
                line = QLabel("─────")
                line.setFont(QFont("Arial", 12))
                if i < current_index:
                    line.setStyleSheet("color: #10b981;")
                elif i == current_index:
                    line.setStyleSheet("color: #00d4aa;")
                else:
                    line.setStyleSheet("color: #6b7280;")
                line.setAlignment(Qt.AlignCenter)
                stages_layout.addWidget(line)
        
        progression_layout.addLayout(stages_layout)
        
        # Add to main layout
        self.layout().insertWidget(1, progression_frame)
    
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
        self.title_label = QLabel("Case Timeline & Evidence")
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
        
        # Case progression timeline
        self._add_case_progression_bar()
        
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
        
        filter_layout.addSpacing(20)
        
        # Manage milestones button
        milestone_btn = QPushButton("📍 Manage Milestones")
        milestone_btn.setFixedSize(180, 35)
        milestone_btn.clicked.connect(self._open_milestone_dialog)
        filter_layout.addWidget(milestone_btn)
        
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # Timeline canvas
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setMinimumHeight(400)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)  # Enable panning
        
        main_layout.addWidget(self.view)
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(10)
        
        zoom_label = QLabel("Zoom:")
        zoom_label.setFont(QFont("Arial", 11))
        zoom_layout.addWidget(zoom_label)
        
        zoom_out_btn = QPushButton("−")
        zoom_out_btn.setFixedSize(35, 35)
        zoom_out_btn.clicked.connect(self._zoom_out)
        zoom_layout.addWidget(zoom_out_btn)
        
        zoom_reset_btn = QPushButton("Reset")
        zoom_reset_btn.setFixedSize(60, 35)
        zoom_reset_btn.clicked.connect(self._zoom_reset)
        zoom_layout.addWidget(zoom_reset_btn)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(35, 35)
        zoom_in_btn.clicked.connect(self._zoom_in)
        zoom_layout.addWidget(zoom_in_btn)
        
        zoom_layout.addSpacing(20)
        
        fit_btn = QPushButton("Fit to View")
        fit_btn.setFixedSize(100, 35)
        fit_btn.clicked.connect(self._fit_to_view)
        zoom_layout.addWidget(fit_btn)
        
        zoom_layout.addStretch()
        
        main_layout.addLayout(zoom_layout)
        
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
        
        legend_layout.addSpacing(30)
        
        # Milestone indicator
        milestone_box = QLabel("◆")
        milestone_box.setStyleSheet("color: #f59e0b; font-size: 16px;")
        legend_layout.addWidget(milestone_box)
        
        milestone_label = QLabel("Milestones")
        milestone_label.setFont(QFont("Arial", 10))
        legend_layout.addWidget(milestone_label)
        
        legend_layout.addStretch()
        
        # Timeline stats
        self.stats_label = QLabel("")
        self.stats_label.setFont(QFont("Arial", 10))
        self.stats_label.setStyleSheet("color: #8899aa;")
        legend_layout.addWidget(self.stats_label)
        
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
            
            # Add slight vertical offset to avoid complete overlap
            y_offset = (hash(evidence.get('id', 0)) % 5) * 3 - 6
            
            # Create marker
            marker = TimelineMarker(evidence, x_pos, timeline_y + y_offset, parent_view=self)
            self.scene.addItem(marker)
            self.markers.append(marker)
            
            # Add tooltip
            marker.setToolTip(
                f"{evidence.get('file_name', 'Unknown')}\n"
                f"Date: {self._format_date(date_str)}\n"
                f"Size: {self._format_size(evidence.get('file_size', 0))}\n"
                f"Type: {evidence.get('file_extension', 'Unknown')}"
            )
        
        # Add date labels
        self._add_date_labels(start_date, end_date, margin, timeline_width, timeline_y)
        
        # Add milestones
        self._add_milestones(start_date, end_date, time_span, margin, timeline_width, timeline_y)
        
        # Set scene rect
        self.scene.setSceneRect(0, 0, timeline_width, 400)
        
        # Update stats
        self._update_stats()
    
    def _add_date_labels(self, start_date, end_date, margin, timeline_width, timeline_y):
        """Add date labels to timeline."""
        # Start date
        start_text = self.scene.addText(start_date.strftime('%Y-%m-%d'))
        start_text.setDefaultTextColor(QColor("#8899aa"))
        start_text.setFont(QFont("Arial", 10))
        start_text.setPos(margin - 40, timeline_y + 15)
        
        # End date
        end_text = self.scene.addText(end_date.strftime('%Y-%m-%d'))
        end_text.setDefaultTextColor(QColor("#8899aa"))
        end_text.setFont(QFont("Arial", 10))
        end_text.setPos(timeline_width - margin - 40, timeline_y + 15)
    
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
            
            # Skip if outside date range
            if milestone_date < start_date or milestone_date > end_date:
                continue
            
            # Calculate x position
            time_offset = (milestone_date - start_date).total_seconds()
            x_ratio = time_offset / time_span
            x_pos = margin + (x_ratio * (timeline_width - 2 * margin))
            
            # Draw vertical line
            line = QGraphicsLineItem(x_pos, timeline_y - 60, x_pos, timeline_y + 60)
            line.setPen(QPen(QColor("#f59e0b"), 3, Qt.DashLine))
            line.setZValue(-1)  # Behind markers
            self.scene.addItem(line)
            
            # Add milestone marker (star shape approximation with circle)
            milestone_marker = QGraphicsEllipseItem(x_pos - 10, timeline_y - 10, 20, 20)
            milestone_marker.setBrush(QBrush(QColor("#f59e0b")))
            milestone_marker.setPen(QPen(QColor("#ffffff"), 2))
            milestone_marker.setZValue(50)
            milestone_marker.setToolTip(
                f"Milestone: {milestone.get('milestone_name', 'Unknown')}\n"
                f"Date: {milestone_date.strftime('%Y-%m-%d')}\n"
                f"{milestone.get('description', '')}"
            )
            self.scene.addItem(milestone_marker)
            
            # Add label above
            label = self.scene.addText(milestone.get('milestone_name', 'Milestone'))
            label.setDefaultTextColor(QColor("#f59e0b"))
            label.setFont(QFont("Arial", 10, QFont.Bold))
            label_width = label.boundingRect().width()
            label.setPos(x_pos - label_width / 2, timeline_y - 90)
            label.setZValue(50)
    
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
    
    def _open_milestone_dialog(self):
        """Open milestone management dialog."""
        if not self.case_id:
            return
        
        dialog = MilestoneDialog(self.case_id, self)
        dialog.milestone_added.connect(self.load_timeline)
        dialog.exec()
    
    def _show_evidence_details(self, evidence: Dict[str, Any]):
        """Show evidence details dialog."""
        dialog = EvidenceDetailsDialog(evidence, self)
        dialog.exec()
    
    def _zoom_in(self):
        """Zoom in the timeline view."""
        self.view.scale(1.2, 1.0)
    
    def _zoom_out(self):
        """Zoom out the timeline view."""
        self.view.scale(0.8, 1.0)
    
    def _zoom_reset(self):
        """Reset zoom to default."""
        self.view.resetTransform()
    
    def _fit_to_view(self):
        """Fit timeline to view."""
        if self.scene.items():
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def _update_stats(self):
        """Update timeline statistics display."""
        if not self.timeline_data:
            return
        
        evidence_count = len(self.timeline_data.get('evidence', []))
        milestone_count = len(self.timeline_data.get('milestones', []))
        date_range = self.timeline_data.get('date_range', (None, None))
        
        if date_range[0] and date_range[1]:
            start = self._parse_date(date_range[0])
            end = self._parse_date(date_range[1])
            if start and end:
                days = (end - start).days
                self.stats_label.setText(
                    f"Evidence: {evidence_count} | Milestones: {milestone_count} | "
                    f"Time Span: {days} days"
                )
            else:
                self.stats_label.setText(
                    f"Evidence: {evidence_count} | Milestones: {milestone_count}"
                )
        else:
            self.stats_label.setText(
                f"Evidence: {evidence_count} | Milestones: {milestone_count}"
            )
    
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
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
