"""
Timeline View Screen
Interactive timeline visualization showing evidence chronologically
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem,
    QGraphicsTextItem, QDateEdit, QComboBox, QFrame,
    QSizePolicy, QStyle, QStyleOptionComboBox
)
from PySide6.QtCore import Qt, Signal, QRectF, QDate, QPointF, QRect, QTimer
from PySide6.QtGui import QFont, QColor, QPen, QBrush, QPainter, QIcon, QPixmap
from datetime import datetime
from typing import List, Dict, Any, Optional

from backend.app.database import Database
from backend.app.timeline_generator import TimelineGenerator
from frontend.src.milestone_dialog import MilestoneDialog
from frontend.src.evidence_details_dialog import EvidenceDetailsDialog


class StatusComboBox(QComboBox):
    """Combo box with a consistently visible custom chevron icon."""

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

        center_x = arrow_rect.center().x()
        center_y = arrow_rect.center().y()
        half_width = max(4, arrow_rect.width() // 6)
        half_height = max(3, arrow_rect.height() // 7)

        left = QPointF(center_x - half_width, center_y - half_height)
        middle = QPointF(center_x, center_y + half_height)
        right = QPointF(center_x + half_width, center_y - half_height)
        painter.drawLine(left, middle)
        painter.drawLine(middle, right)
        painter.end()


class HorizontalPanGraphicsView(QGraphicsView):
    """Graphics view that only allows horizontal panning."""

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self._is_panning = False
        self._last_pos = None
        self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_panning = True
            self._last_pos = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning and self._last_pos is not None:
            dx = event.position().x() - self._last_pos.x()
            self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() - dx))
            self.verticalScrollBar().setValue(0)
            self._last_pos = event.position()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._is_panning:
            self._is_panning = False
            self._last_pos = None
            self.setCursor(Qt.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)


class TimelineMarker(QGraphicsEllipseItem):
    """Custom graphics item for evidence markers on timeline."""
    
    def __init__(self, evidence: Dict[str, Any], x: float, y: float, radius: float = 16, parent_view=None):
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.evidence = evidence
        self.parent_view = parent_view
        self.default_radius = radius
        self.setPos(x, y)
        
        # Set color based on file type with brighter colors
        color = self._get_type_color(evidence.get('file_extension', ''))
        self.setBrush(QBrush(color))
        
        # Thicker, more visible border
        self.setPen(QPen(QColor("#e0e6ed"), 3))
        
        # Make clickable
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.PointingHandCursor)
        
        # Add shadow effect for depth
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(64, 224, 208, 100))  # Cyan glow
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def _get_type_color(self, extension: str) -> QColor:
        """Get brighter, more vibrant color based on file type."""
        ext = extension.lower()
        
        # Brighter, more vibrant colors for better visibility
        if ext in ['.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt']:
            return QColor("#3b82f6")  # Bright blue for documents
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg']:
            return QColor("#10b981")  # Emerald green for images
        elif ext in ['.log']:
            return QColor("#f59e0b")  # Amber for logs
        elif ext in ['.csv', '.xlsx', '.xls']:
            return QColor("#06b6d4")  # Cyan for spreadsheets
        elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
            return QColor("#8b5cf6")  # Purple for videos
        elif ext in ['.zip', '.rar', '.7z', '.tar']:
            return QColor("#ef4444")  # Red for archives
        else:
            return QColor("#6b7280")  # Gray for other
    
    def hoverEnterEvent(self, event):
        """Handle hover enter - make marker larger with smooth animation."""
        self.setScale(1.8)  # Larger scale on hover
        self.setZValue(100)  # Bring to front
        
        # Enhance glow effect on hover
        if self.graphicsEffect():
            shadow = self.graphicsEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(64, 224, 208, 180))  # Brighter glow
        
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle hover leave - restore size and glow."""
        self.setScale(1.0)
        self.setZValue(0)
        
        # Restore normal glow
        if self.graphicsEffect():
            shadow = self.graphicsEffect()
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(64, 224, 208, 100))
        
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
        self._is_date_filter_active = False
        self._setup_ui()
        self._apply_styles()
        if case_id:
            self.load_timeline()
    
    def set_case_id(self, case_id: int):
        """Set the current case ID and reload timeline."""
        self.case_id = case_id
        self.load_timeline()
    
    def _add_case_progression_bar(self, parent_layout):
        """Add case progression stages bar with clean, connected design."""
        progression_frame = QFrame()
        progression_frame.setFrameShape(QFrame.StyledPanel)
        progression_frame.setStyleSheet("""
            QFrame {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 12px;
            }
        """)
        
        progression_layout = QVBoxLayout(progression_frame)
        progression_layout.setSpacing(15)
        progression_layout.setContentsMargins(30, 25, 30, 30)  # top, right, bottom, left - more top margin
        
        # Title - larger and positioned top-left
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent; border: none;")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        prog_title = QLabel("Case Progression")
        prog_title.setFont(QFont("Arial", 16, QFont.Bold))
        prog_title.setStyleSheet("color: #00d4aa; border: none; background: transparent; padding: 0px;")
        prog_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        prog_title.setFixedHeight(30)  # Fixed height to ensure visibility
        title_layout.addWidget(prog_title)
        
        # Add status update dropdown
        title_layout.addStretch()
        
        status_label = QLabel("Update Status:")
        status_label.setFont(QFont("Arial", 11))
        status_label.setStyleSheet("color: #8899aa; border: none; background: transparent;")
        title_layout.addWidget(status_label)
        
        self.status_combo = StatusComboBox()
        self.status_combo.addItems([
            "Case Created",
            "Evidence Collected", 
            "Analysis In Progress",
            "Review",
            "Closed"
        ])
        self.status_combo.setFixedWidth(180)
        self.status_combo.setMinimumHeight(32)
        self.status_combo.setStyleSheet("""
            QComboBox {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 6px;
                padding: 6px 12px;
                padding-right: 30px;
                color: #e0e6ed;
                font-size: 11px;
            }
            QComboBox:hover {
                border-color: #40e0d0;
                background-color: #122a3a;
            }
            QComboBox:focus {
                border-color: #40e0d0;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                border-left: none;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background-color: #0d2137;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #0a1929;
                border: 2px solid #40e0d0;
                border-radius: 6px;
                selection-background-color: #2a7a8a;
                selection-color: #ffffff;
                color: #e0e6ed;
                padding: 5px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                background-color: #0a1929;
                padding: 6px 12px;
                border-radius: 4px;
                min-height: 20px;
                max-height: 30px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #1a3a4a;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #2a7a8a;
                color: #ffffff;
            }
        """)
        self.status_combo.currentTextChanged.connect(self._on_status_changed)
        title_layout.addWidget(self.status_combo)
        
        progression_layout.addWidget(title_container)
        
        # Create a single widget for the entire progression line
        progression_widget = QWidget()
        progression_widget.setStyleSheet("background: transparent; border: none;")
        progression_widget.setMinimumHeight(110)
        
        # We'll use a custom paint event for this widget
        class ProgressionLineWidget(QWidget):
            def __init__(self, stages_data, parent=None):
                super().__init__(parent)
                self.stages_data = stages_data
                self.setMinimumHeight(110)
                self.setStyleSheet("background: transparent; border: none;")
            
            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                
                if not self.stages_data:
                    return
                
                # Calculate positions
                width = self.width()
                height = self.height()
                num_stages = len(self.stages_data)
                
                # Spacing between stages
                stage_spacing = (width - 100) / (num_stages - 1) if num_stages > 1 else 0
                start_x = 50
                circle_y = 35
                
                # Draw connecting lines first (behind circles)
                for i in range(num_stages - 1):
                    x1 = start_x + (i * stage_spacing)
                    x2 = start_x + ((i + 1) * stage_spacing)
                    
                    stage_name, stage_id, is_complete, is_current, is_future = self.stages_data[i]
                    next_stage = self.stages_data[i + 1]
                    
                    # Line color based on completion
                    if is_complete:
                        line_color = QColor("#10b981")  # Green for completed
                        line_width = 6
                    elif is_current:
                        line_color = QColor("#40e0d0")  # Cyan for current
                        line_width = 6
                    else:
                        line_color = QColor("#2a4a5a")  # Muted for future
                        line_width = 4
                    
                    pen = QPen(line_color, line_width)
                    pen.setCapStyle(Qt.RoundCap)
                    painter.setPen(pen)
                    painter.drawLine(int(x1 + 20), int(circle_y), int(x2 - 20), int(circle_y))
                
                # Draw circles and labels
                for i, (stage_name, stage_id, is_complete, is_current, is_future) in enumerate(self.stages_data):
                    x = start_x + (i * stage_spacing)
                    
                    # Circle styling
                    # Special case: If "Closed" is current, treat it as complete (show checkmark)
                    if is_complete or (is_current and stage_id == "closed"):
                        circle_color = QColor("#10b981")
                        border_color = QColor("#10b981")
                        icon = "✓"
                        icon_color = QColor("#ffffff")
                    elif is_current:
                        circle_color = QColor("#40e0d0")
                        border_color = QColor("#40e0d0")
                        icon = "●"
                        icon_color = QColor("#0a1929")
                    else:
                        circle_color = QColor("transparent")
                        border_color = QColor("#2a4a5a")
                        icon = ""
                        icon_color = QColor("#6b7280")
                    
                    # Draw circle with glow for active/complete
                    if is_complete or is_current:
                        # Outer glow
                        glow_pen = QPen(QColor(circle_color.red(), circle_color.green(), circle_color.blue(), 50))
                        glow_pen.setWidth(8)
                        painter.setPen(glow_pen)
                        painter.setBrush(Qt.NoBrush)
                        painter.drawEllipse(int(x - 24), int(circle_y - 24), 48, 48)
                    
                    # Main circle
                    painter.setPen(QPen(border_color, 4))
                    painter.setBrush(QBrush(circle_color))
                    painter.drawEllipse(int(x - 20), int(circle_y - 20), 40, 40)
                    
                    # Draw icon/checkmark
                    if icon:
                        painter.setPen(icon_color)
                        if is_complete:
                            painter.setFont(QFont("Arial", 20, QFont.Bold))
                        else:
                            painter.setFont(QFont("Arial", 24, QFont.Bold))
                        
                        # Center the icon
                        fm = painter.fontMetrics()
                        icon_width = fm.horizontalAdvance(icon)
                        icon_height = fm.height()
                        icon_x = int(x - icon_width / 2)
                        icon_y = int(circle_y + icon_height / 4)
                        painter.drawText(icon_x, icon_y, icon)
                    
                    # Draw stage label below with more spacing
                    painter.setFont(QFont("Arial", 10, QFont.Bold))
                    if is_complete:
                        painter.setPen(QColor("#10b981"))
                    elif is_current:
                        painter.setPen(QColor("#00d4aa"))
                    else:
                        painter.setPen(QColor("#6b7280"))
                    
                    # Word wrap for long labels with increased spacing from circles
                    words = stage_name.split()
                    if len(words) > 2:
                        line1 = " ".join(words[:2])
                        line2 = " ".join(words[2:])
                        
                        fm = painter.fontMetrics()
                        text_width1 = fm.horizontalAdvance(line1)
                        text_width2 = fm.horizontalAdvance(line2)
                        
                        # Increased spacing: y+45 and y+60 (was y+38 and y+52)
                        painter.drawText(int(x - text_width1 / 2), int(circle_y + 45), line1)
                        painter.drawText(int(x - text_width2 / 2), int(circle_y + 60), line2)
                    else:
                        fm = painter.fontMetrics()
                        text_width = fm.horizontalAdvance(stage_name)
                        # Increased spacing: y+50 (was y+42)
                        painter.drawText(int(x - text_width / 2), int(circle_y + 50), stage_name)
                
                painter.end()
        
        # Define stages
        stages = [
            ("Case Created", "created"),
            ("Evidence Collected", "evidence"),
            ("Analysis In Progress", "analysis"),
            ("Review", "review"),
            ("Closed", "closed")
        ]
        
        # Get current case status dynamically from database
        current_status = "created"  # Default to first stage
        if self.case_id:
            case = self.database.get_case(self.case_id)
            if case:
                db_status = case.get('status', 'Active').lower()
                
                # Map database status to progression stages
                # This makes it fully dynamic based on case status
                if db_status == 'closed':
                    current_status = "closed"
                elif db_status == 'review':
                    current_status = "review"
                elif db_status == 'active':
                    # Check if evidence has been collected
                    evidence_count = len(self.database.get_evidence_for_case(self.case_id))
                    if evidence_count > 0:
                        current_status = "analysis"  # Has evidence, in analysis
                    else:
                        current_status = "evidence"  # No evidence yet
                elif db_status == 'new' or db_status == 'created':
                    current_status = "created"
                else:
                    # Default: if case exists and has evidence, assume analysis
                    evidence_count = len(self.database.get_evidence_for_case(self.case_id))
                    if evidence_count > 0:
                        current_status = "analysis"
                    else:
                        current_status = "evidence"
        
        # Update the dropdown to match current status
        status_map = {
            "created": "Case Created",
            "evidence": "Evidence Collected",
            "analysis": "Analysis In Progress",
            "review": "Review",
            "closed": "Closed"
        }
        if hasattr(self, 'status_combo'):
            self.status_combo.blockSignals(True)  # Prevent triggering change event
            self.status_combo.setCurrentText(status_map.get(current_status, "Evidence Collected"))
            self.status_combo.blockSignals(False)
        
        # Determine which stages are complete
        stage_order = ["created", "evidence", "analysis", "review", "closed"]
        current_index = stage_order.index(current_status) if current_status in stage_order else 1
        
        # Prepare stage data
        stages_data = []
        for i, (stage_name, stage_id) in enumerate(stages):
            is_complete = i < current_index
            is_current = i == current_index
            is_future = i > current_index
            stages_data.append((stage_name, stage_id, is_complete, is_current, is_future))
        
        # Create the custom widget
        progression_line = ProgressionLineWidget(stages_data)
        progression_layout.addWidget(progression_line)
        
        # Add to parent layout
        parent_layout.addWidget(progression_frame)
    
    def _setup_ui(self):
        """Setup the timeline UI."""
        # Main layout (no outer scroll area)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 20)
        main_layout.setSpacing(20)

        content_layout = main_layout
        
        # Header
        header_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("‹ Back to Case")
        back_btn.setFont(QFont("Arial", 12))
        back_btn.setFixedSize(155, 35)
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
        
        content_layout.addLayout(header_layout)
        
        # Case progression timeline
        self._add_case_progression_bar(content_layout)
        
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
        milestone_btn = QPushButton("Manage Milestones")
        milestone_btn.setFixedSize(180, 35)
        milestone_btn.clicked.connect(self._open_milestone_dialog)
        filter_layout.addWidget(milestone_btn)
        
        filter_layout.addStretch()
        
        content_layout.addLayout(filter_layout)
        
        # Legend section - BEFORE timeline
        legend_frame = QFrame()
        legend_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        legend_main_layout = QHBoxLayout(legend_frame)
        legend_main_layout.setContentsMargins(16, 8, 16, 4)
        legend_main_layout.setSpacing(30)
        
        # Legend title
        legend_label = QLabel("Legend:")
        legend_label.setFont(QFont("Arial", 12, QFont.Bold))
        legend_label.setStyleSheet("color: #00d4aa;")
        legend_main_layout.addWidget(legend_label)
        
        # Color legend with updated colors
        colors = [
            ("#3b82f6", "Documents"),
            ("#10b981", "Images"),
            ("#f59e0b", "Logs"),
            ("#06b6d4", "Spreadsheets"),
            ("#8b5cf6", "Videos"),
            ("#ef4444", "Archives"),
            ("#6b7280", "Other")
        ]
        
        for color, label in colors:
            item_container = QWidget()
            item_container.setStyleSheet("background: transparent;")
            item_layout = QHBoxLayout(item_container)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(6)
            
            color_box = QLabel("●")
            color_box.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
            item_layout.addWidget(color_box)
            
            text_label = QLabel(label)
            text_label.setFont(QFont("Arial", 10))
            text_label.setStyleSheet("color: #e0e6ed;")
            item_layout.addWidget(text_label)
            
            legend_main_layout.addWidget(item_container)
        
        # Milestone indicator
        milestone_container = QWidget()
        milestone_container.setStyleSheet("background: transparent;")
        milestone_layout = QHBoxLayout(milestone_container)
        milestone_layout.setContentsMargins(0, 0, 0, 0)
        milestone_layout.setSpacing(6)
        
        milestone_box = QLabel("◆")
        milestone_box.setStyleSheet("color: #f59e0b; font-size: 14px; font-weight: bold;")
        milestone_layout.addWidget(milestone_box)
        
        milestone_label = QLabel("Milestones")
        milestone_label.setFont(QFont("Arial", 10))
        milestone_label.setStyleSheet("color: #e0e6ed;")
        milestone_layout.addWidget(milestone_label)
        
        legend_main_layout.addWidget(milestone_container)
        legend_main_layout.addStretch()
        
        # Timeline canvas
        self.scene = QGraphicsScene()
        self.view = HorizontalPanGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # No vertical scroll
        self.view.setFixedHeight(400)  # Fixed height instead of expanding
        self.view.setDragMode(QGraphicsView.NoDrag)
        self.view.setFrameShape(QFrame.NoFrame)
        self.view.setLineWidth(0)
        self.view.setContentsMargins(0, 0, 0, 0)
        self.view.viewport().setContentsMargins(0, 0, 0, 0)
        self.view.verticalScrollBar().valueChanged.connect(lambda _: self.view.verticalScrollBar().setValue(0))
        
        # Create a container for timeline with overlay buttons
        timeline_container = QWidget()
        timeline_container.setObjectName("timelineContainer")
        timeline_container.setStyleSheet("""
            #timelineContainer {
                background-color: #0d2137;
                border: 2px solid #1f5f74;
                border-radius: 8px;
            }
        """)
        timeline_layout = QVBoxLayout(timeline_container)
        # Keep inner widgets inset so the outer border remains visible on all sides.
        timeline_layout.setContentsMargins(2, 2, 2, 12)
        timeline_layout.setSpacing(10)
        
        # Add view to container
        timeline_layout.addWidget(self.view)

        self.marker_hint_label = QLabel(
            "Note: Double-click on markers to view evidence details.",
            timeline_container
        )
        self.marker_hint_label.setFont(QFont("Arial", 10))
        self.marker_hint_label.setStyleSheet(
            "color: #8aa2b8; font-style: italic; background: transparent;"
        )
        self.marker_hint_label.setAlignment(Qt.AlignLeft)
        self.marker_hint_label.adjustSize()
        self.marker_hint_label.move(14, 10)
        self.marker_hint_label.raise_()
        
        # Create zoom buttons overlay
        zoom_buttons_container = QWidget(timeline_container)
        zoom_buttons_container.setStyleSheet("background: transparent;")
        zoom_buttons_layout = QHBoxLayout(zoom_buttons_container)
        zoom_buttons_layout.setContentsMargins(0, 10, 10, 0)
        zoom_buttons_layout.setSpacing(8)
        zoom_buttons_layout.addStretch()
        
        # Zoom out button
        self.zoom_out_btn = QPushButton()
        self.zoom_out_btn.setFixedSize(40, 40)
        self.zoom_out_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.zoom_out_btn.setIcon(self._create_zoom_icon(is_plus=False))
        self.zoom_out_btn.setIconSize(QRect(0, 0, 22, 22).size())
        self.zoom_out_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(13, 33, 55, 0.95);
                color: #40e0d0;
                border: 2px solid #40e0d0;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(64, 224, 208, 0.2);
                border-color: #2dd4bf;
            }
            QPushButton:pressed {
                background-color: rgba(64, 224, 208, 0.3);
            }
        """)
        self.zoom_out_btn.setCursor(Qt.PointingHandCursor)
        self.zoom_out_btn.setToolTip("Zoom Out")
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        zoom_buttons_layout.addWidget(self.zoom_out_btn)
        
        # Zoom in button
        self.zoom_in_btn = QPushButton()
        self.zoom_in_btn.setFixedSize(40, 40)
        self.zoom_in_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.zoom_in_btn.setIcon(self._create_zoom_icon(is_plus=True))
        self.zoom_in_btn.setIconSize(QRect(0, 0, 22, 22).size())
        self.zoom_in_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(13, 33, 55, 0.95);
                color: #40e0d0;
                border: 2px solid #40e0d0;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(64, 224, 208, 0.2);
                border-color: #2dd4bf;
            }
            QPushButton:pressed {
                background-color: rgba(64, 224, 208, 0.3);
            }
        """)
        self.zoom_in_btn.setCursor(Qt.PointingHandCursor)
        self.zoom_in_btn.setToolTip("Zoom In")
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        zoom_buttons_layout.addWidget(self.zoom_in_btn)
        
        # Position zoom buttons at top-right
        zoom_buttons_container.setGeometry(0, 0, timeline_container.width(), 60)
        zoom_buttons_container.raise_()  # Ensure buttons are on top
        
        # Store reference to container for resize handling
        self.timeline_container = timeline_container
        self.zoom_buttons_container = zoom_buttons_container
        
        # Install event filter to handle resize
        timeline_container.installEventFilter(self)

        # Place legend inside the timeline box.
        timeline_layout.addSpacing(6)
        timeline_layout.addWidget(legend_frame)
        
        content_layout.addWidget(timeline_container)  # No stretch factor
        
        # Keep content naturally aligned to top while fitting available space.
        content_layout.addStretch(1)

    def _create_zoom_icon(self, is_plus: bool) -> QIcon:
        """Create a magnifier icon with plus/minus symbol for zoom controls."""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        icon_color = QColor("#40e0d0")
        pen = QPen(icon_color, 2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)

        # Magnifier lens
        painter.drawEllipse(3, 3, 12, 12)

        # Magnifier handle
        painter.drawLine(14, 14, 20, 20)

        # Minus symbol in lens
        painter.drawLine(6, 9, 12, 9)

        # Add vertical stroke for plus symbol when needed
        if is_plus:
            painter.drawLine(9, 6, 9, 12)

        painter.end()
        return QIcon(pixmap)
    
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
                border: none;
            }
            QGraphicsView QScrollBar:horizontal {
                height: 0px;
            }
        """)
    
    def load_timeline(self):
        """Load timeline data and render."""
        if not self.case_id:
            return

        self._is_date_filter_active = False
        
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
        """Render the timeline visualization with activity-based curve."""
        import math
        from datetime import timedelta
        from PySide6.QtGui import QPainterPath, QLinearGradient

        self.scene.clear()
        self.markers = []

        if not self.timeline_data or not self.timeline_data['evidence']:
            empty_message = "No data within this range" if self._is_date_filter_active else "No evidence to display"
            msg = self.scene.addText(empty_message)
            msg.setDefaultTextColor(QColor("#8899aa"))
            msg.setFont(QFont("Arial", 14))
            msg_rect = msg.boundingRect()
            msg.setPos(20, max(40, (400 - msg_rect.height()) / 2))
            self.scene.setSceneRect(0, 0, 1400, 400)
            QTimer.singleShot(0, self._reset_timeline_view)
            return

        evidence_list = self.timeline_data['evidence']
        date_field    = self.timeline_data['date_field']

        # Layout constants
        margin       = 80
        scene_width  = max(1400, len(evidence_list) * 90)
        scene_height = 500  # Increased to accommodate X-axis labels
        baseline_y   = 300
        curve_top    = 90
        curve_range  = baseline_y - curve_top

        # Date range
        date_range = self.timeline_data['date_range']
        if not date_range[0] or not date_range[1]:
            return

        start_date = self._parse_date(date_range[0])
        end_date   = self._parse_date(date_range[1])
        if not start_date or not end_date:
            return

        total_seconds = (end_date - start_date).total_seconds()
        zero_span = (total_seconds == 0)
        if zero_span:
            total_seconds = max(len(evidence_list), 1)

        def x_for_date(dt, index=0):
            if zero_span:
                ratio = index / max(len(evidence_list) - 1, 1)
            else:
                ratio = (dt - start_date).total_seconds() / total_seconds
            ratio = max(0.0, min(1.0, ratio))
            return margin + ratio * (scene_width - 2 * margin)

        # Activity buckets
        NUM_BUCKETS = 40
        buckets = [0] * NUM_BUCKETS

        for idx, ev in enumerate(evidence_list):
            ds = ev.get(date_field)
            if not ds:
                continue
            ed = self._parse_date(ds)
            if not ed:
                continue
            if zero_span:
                ratio = idx / max(len(evidence_list) - 1, 1)
            else:
                ratio = (ed - start_date).total_seconds() / total_seconds
            ratio = max(0.0, min(1.0, ratio))
            b = min(int(ratio * NUM_BUCKETS), NUM_BUCKETS - 1)
            buckets[b] += 1

        # Gaussian smoothing
        sigma    = 2.5
        kernel_r = int(3 * sigma)
        kernel   = [math.exp(-0.5 * (k / sigma) ** 2)
                    for k in range(-kernel_r, kernel_r + 1)]
        k_sum    = sum(kernel)
        kernel   = [v / k_sum for v in kernel]

        smooth = []
        for i in range(NUM_BUCKETS):
            val = 0.0
            for ki, kv in enumerate(kernel):
                idx2 = i + ki - kernel_r
                if 0 <= idx2 < NUM_BUCKETS:
                    val += buckets[idx2] * kv
            smooth.append(val)

        max_smooth = max(smooth) if max(smooth) > 0 else 1
        MIN_RATIO  = 0.05
        normalised = [max(s / max_smooth, MIN_RATIO) for s in smooth]

        # Build knot positions
        knots = []
        for i in range(NUM_BUCKETS):
            ratio = (i + 0.5) / NUM_BUCKETS
            x = margin + ratio * (scene_width - 2 * margin)
            y = baseline_y - normalised[i] * curve_range
            knots.append(QPointF(x, y))

        # Catmull-Rom to cubic Bezier
        def catmull_ctrl(p0, p1, p2, p3, alpha=0.5):
            def d(a, b):
                return max(math.hypot(b.x() - a.x(), b.y() - a.y()), 1e-4) ** alpha
            t01, t12, t23 = d(p0, p1), d(p1, p2), d(p2, p3)
            m1x = (p2.x()-p0.x())/(t01+t12)*t12
            m1y = (p2.y()-p0.y())/(t01+t12)*t12
            m2x = (p3.x()-p1.x())/(t12+t23)*t12
            m2y = (p3.y()-p1.y())/(t12+t23)*t12
            return (QPointF(p1.x() + m1x/3, p1.y() + m1y/3),
                    QPointF(p2.x() - m2x/3, p2.y() - m2y/3))

        pts = [knots[0]] + knots + [knots[-1]]
        curve_path = QPainterPath()
        curve_path.moveTo(pts[1])
        for i in range(1, len(pts) - 2):
            cp1, cp2 = catmull_ctrl(pts[i-1], pts[i], pts[i+1], pts[i+2])
            curve_path.cubicTo(cp1, cp2, pts[i+1])

        # LUT for y-at-x queries
        NUM_LUT = 4000
        lut_x, lut_y = [], []
        for i in range(NUM_LUT + 1):
            pt = curve_path.pointAtPercent(i / NUM_LUT)
            lut_x.append(pt.x())
            lut_y.append(pt.y())

        def y_at_x(tx):
            lo, hi = 0, len(lut_x) - 1
            while lo < hi:
                mid = (lo + hi) // 2
                if lut_x[mid] < tx:
                    lo = mid + 1
                else:
                    hi = mid
            return lut_y[lo]

        # Filled gradient area under curve
        fill_path = QPainterPath(curve_path)
        fill_path.lineTo(knots[-1].x(), baseline_y)
        fill_path.lineTo(knots[0].x(),  baseline_y)
        fill_path.closeSubpath()

        fill_grad = QLinearGradient(0, curve_top, 0, baseline_y)
        fill_grad.setColorAt(0.0, QColor(64, 224, 208, 110))
        fill_grad.setColorAt(1.0, QColor(10,  25,  41,   0))
        fill_item = self.scene.addPath(fill_path)
        fill_item.setBrush(QBrush(fill_grad))
        fill_item.setPen(QPen(Qt.NoPen))
        fill_item.setZValue(0)

        # Glow layer
        glow_item = self.scene.addPath(curve_path)
        gp = QPen(QColor(64, 224, 208, 55), 16)
        gp.setCapStyle(Qt.RoundCap)
        gp.setJoinStyle(Qt.RoundJoin)
        glow_item.setPen(gp)
        glow_item.setZValue(1)

        # Main curve stroke
        curve_item = self.scene.addPath(curve_path)
        cp2 = QPen(QColor("#40e0d0"), 2.5)
        cp2.setCapStyle(Qt.RoundCap)
        cp2.setJoinStyle(Qt.RoundJoin)
        curve_item.setPen(cp2)
        curve_item.setZValue(2)

        # Knot dots
        for knot in knots:
            dot = self.scene.addEllipse(knot.x()-3, knot.y()-3, 6, 6)
            dot.setBrush(QBrush(QColor("#40e0d0")))
            dot.setPen(QPen(QColor("#0a1929"), 1))
            dot.setZValue(3)

        # Evidence markers placed ON the curve
        for idx, evidence in enumerate(evidence_list):
            date_str = evidence.get(date_field)
            if not date_str:
                continue
            evidence_date = self._parse_date(date_str)
            if not evidence_date:
                continue

            ex = x_for_date(evidence_date, idx)
            ey = y_at_x(ex)

            marker = TimelineMarker(evidence, ex, ey, radius=10, parent_view=self)
            marker.setZValue(10)
            self.scene.addItem(marker)
            self.markers.append(marker)

            date_formatted = self._format_date_detailed(date_str)
            marker.setToolTip(
                f"File: {evidence.get('file_name', 'Unknown')}\n"
                f"Date: {date_formatted}\n"
                f"Size: {self._format_size(evidence.get('file_size', 0))}\n"
                f"Type: {evidence.get('file_extension', 'Unknown')}\n"
                f"Status: {evidence.get('status', 'Pending')}"
            )

        # Date labels below baseline
        self._add_smart_date_labels(
            start_date, end_date, margin, scene_width, baseline_y)

        # Milestones
        self._add_milestones(
            start_date, end_date, total_seconds,
            margin, scene_width, baseline_y)

        # Scene rect
        self.scene.setSceneRect(0, 0, scene_width, scene_height)
        
        # Keep native scale so horizontal scrolling remains available.
        QTimer.singleShot(0, self._reset_timeline_view)

    def _add_smart_date_labels(self, start_date, end_date, margin, timeline_width, baseline_y):
        """Draw a clean X axis (months) and Y axis (label only)."""
        from datetime import date, timedelta
        import calendar

        total_days = (end_date - start_date).days
        plot_w     = timeline_width - 2 * margin

        # ── helpers ──────────────────────────────────────────────────
        def x_for_dt(dt):
            if total_days == 0:
                return margin + plot_w / 2
            ratio = (dt - start_date).total_seconds() / ((end_date - start_date).total_seconds())
            return margin + max(0.0, min(1.0, ratio)) * plot_w

        # ── Axis positioning ──────────────────────────────────────────
        curve_top = 90
        x_axis_y = baseline_y + 25          # X-axis position
        y_axis_x = margin - 15              # Y-axis position
        axis_pen = QPen(QColor("#40e0d0"), 2)  # Brighter, thicker axis

        # ── Y axis line (vertical) ────────────────────────────────────
        y_axis = self.scene.addLine(y_axis_x, curve_top, y_axis_x, x_axis_y)
        y_axis.setPen(axis_pen)
        y_axis.setZValue(5)

        # Arrow head at top of Y axis
        arrow_size = 6
        for dx, dy in [(-arrow_size, arrow_size), (arrow_size, arrow_size)]:
            a = self.scene.addLine(y_axis_x, curve_top, y_axis_x + dx, curve_top + dy)
            a.setPen(QPen(QColor("#40e0d0"), 2))
            a.setZValue(5)

        # ── X axis baseline (horizontal) ──────────────────────────────
        x_axis = self.scene.addLine(y_axis_x, x_axis_y, timeline_width - margin, x_axis_y)
        x_axis.setPen(axis_pen)
        x_axis.setZValue(5)

        # ── Month labels on X axis ────────────────────────────────────
        # Collect all month-starts that fall within the data range
        from datetime import datetime as dt_cls
        first_month = start_date.replace(day=1)
        month_starts = []
        cur = first_month
        while cur <= end_date:
            month_starts.append(cur)
            # advance by one month
            if cur.month == 12:
                cur = cur.replace(year=cur.year + 1, month=1)
            else:
                cur = cur.replace(month=cur.month + 1)

        # Choose label format based on span
        if total_days > 365 * 2:
            fmt = "%b '%y"      # "Jan '26"
        elif total_days > 365:
            fmt = "%b %Y"       # "Jan 2026"
        elif total_days > 60:
            fmt = "%b"          # "Jan"
        else:
            fmt = "%b %d"       # "Jan 10"

        for ms in month_starts:
            xm = x_for_dt(ms)
            # Don't draw ticks right at the edges
            if xm < margin + 5 or xm > timeline_width - margin - 5:
                continue

            # Tick mark on X axis
            tick = self.scene.addLine(xm, x_axis_y - 5, xm, x_axis_y + 5)
            tick.setPen(QPen(QColor("#40e0d0"), 2))
            tick.setZValue(5)

            # Month label below axis
            label_str = ms.strftime(fmt)
            txt = self.scene.addText(label_str)
            txt.setDefaultTextColor(QColor("#e0e6ed"))  # Brighter text
            txt.setFont(QFont("Arial", 11, QFont.Bold))  # Larger, bolder
            tw = txt.boundingRect().width()
            txt.setPos(xm - tw / 2, x_axis_y + 10)
            txt.setZValue(5)

        # Y axis label — rotated "Activity" text
        from PySide6.QtGui import QTransform
        y_label = self.scene.addText("Activity")
        y_label.setDefaultTextColor(QColor("#e0e6ed"))  # Brighter text
        y_label.setFont(QFont("Arial", 11, QFont.Bold))  # Larger, bolder
        # Rotate -90 degrees so it reads bottom-to-top alongside the Y axis
        transform = QTransform()
        lh = y_label.boundingRect().height()
        lw = y_label.boundingRect().width()
        mid_y = (curve_top + x_axis_y) / 2
        transform.translate(y_axis_x - lh - 8, mid_y + lw / 2)
        transform.rotate(-90)
        y_label.setTransform(transform)
        y_label.setZValue(5)

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
            
            # Draw thicker, more prominent vertical line
            line = QGraphicsLineItem(x_pos, timeline_y - 80, x_pos, timeline_y + 80)
            line.setPen(QPen(QColor("#f59e0b"), 4, Qt.DashLine))  # Thicker line
            line.setZValue(-1)  # Behind markers
            self.scene.addItem(line)
            
            # Add larger milestone marker with glow
            milestone_marker = QGraphicsEllipseItem(x_pos - 14, timeline_y - 14, 28, 28)  # Larger
            milestone_marker.setBrush(QBrush(QColor("#f59e0b")))
            milestone_marker.setPen(QPen(QColor("#ffffff"), 3))  # Thicker border
            milestone_marker.setZValue(50)
            
            # Add glow effect to milestone
            from PySide6.QtWidgets import QGraphicsDropShadowEffect
            milestone_shadow = QGraphicsDropShadowEffect()
            milestone_shadow.setBlurRadius(15)
            milestone_shadow.setColor(QColor(245, 158, 11, 150))  # Orange glow
            milestone_shadow.setOffset(0, 0)
            milestone_marker.setGraphicsEffect(milestone_shadow)
            
            milestone_marker.setToolTip(
                f"Milestone: {milestone.get('milestone_name', 'Unknown')}\n"
                f"Date: {milestone_date.strftime('%Y-%m-%d')}\n"
                f"{milestone.get('description', '')}"
            )
            self.scene.addItem(milestone_marker)
            
            # Add label above with background
            label = self.scene.addText(milestone.get('milestone_name', 'Milestone'))
            label.setDefaultTextColor(QColor("#f59e0b"))
            label.setFont(QFont("Arial", 11, QFont.Bold))  # Larger, bolder
            label_width = label.boundingRect().width()
            label.setPos(x_pos - label_width / 2, timeline_y - 105)
            label.setZValue(50)
            
            # Add background to label
            label_rect = label.boundingRect()
            label_bg = self.scene.addRect(
                label.x() - 4,
                label.y() - 2,
                label_rect.width() + 8,
                label_rect.height() + 4
            )
            label_bg.setBrush(QBrush(QColor("#0d2137")))
            label_bg.setPen(QPen(QColor("#f59e0b"), 2))
            label_bg.setZValue(49)
            label.setZValue(50)
    
    def _apply_date_filter(self):
        """Apply date range filter."""
        if not self.case_id:
            return

        self._is_date_filter_active = True
        
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
        self._is_date_filter_active = False
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
        self.view.scale(1.2, 1.2)
    
    def _zoom_out(self):
        """Zoom out the timeline view."""
        self.view.scale(0.8, 0.8)
    
    def eventFilter(self, obj, event):
        """Handle events for timeline container to keep zoom buttons positioned."""
        if obj == self.timeline_container and event.type() == event.Type.Resize:
            if hasattr(self, 'marker_hint_label'):
                self.marker_hint_label.move(14, 10)
            # Reposition zoom buttons on resize
            if hasattr(self, 'zoom_buttons_container'):
                self.zoom_buttons_container.setGeometry(
                    0, 0, 
                    self.timeline_container.width(), 
                    60
                )
        return super().eventFilter(obj, event)
    
    def _reset_timeline_view(self):
        """Reset timeline view transform and start position."""
        if self.scene.items():
            self.view.resetTransform()
            self.view.horizontalScrollBar().setValue(0)
    
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
    
    def _on_status_changed(self, status_text: str):
        """Handle case status change from dropdown."""
        if not self.case_id:
            return
        
        # Map display text to database status
        status_map = {
            "Case Created": "New",
            "Evidence Collected": "Active",
            "Analysis In Progress": "Active",
            "Review": "Review",
            "Closed": "Closed"
        }
        
        db_status = status_map.get(status_text, "Active")
        
        # Update database
        try:
            self.database.update_case_status(self.case_id, db_status)
            
            # Log the activity
            self.database.log_activity(
                self.case_id,
                "Status Updated",
                f"Case status changed to: {status_text}"
            )
            
            # QUICK UPDATE: Just refresh the progression bar widget, not entire timeline
            self._refresh_progression_bar_only()
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Update Failed",
                f"Failed to update case status: {str(e)}"
            )
    
    def _refresh_progression_bar_only(self):
        """Quickly refresh just the progression bar without reloading timeline."""
        if not self.case_id:
            return
        
        # With the new scroll area structure, it's simpler to just reload the timeline
        # This ensures everything stays in sync
        self.load_timeline()
