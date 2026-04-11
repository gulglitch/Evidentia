"""
Analytics Dashboard Screen
Displays risk level charts and file type distribution analytics
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from typing import Dict
import math

from backend.app.database import Database


class BarChartWidget(QWidget):
    """Custom widget to draw a bar chart."""
    
    def __init__(self, data: Dict[str, int], colors: Dict[str, str], title: str = ""):
        super().__init__()
        self.data = data
        self.colors = colors
        self.title = title
        self.setMinimumHeight(320)
        self.setMinimumWidth(420)
    
    def paintEvent(self, event):
        """Draw the bar chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor("#0d2137"))
        
        # Title
        if self.title:
            painter.setPen(QColor("#00d4aa"))
            painter.setFont(QFont("Arial", 14, QFont.Bold))
            painter.drawText(20, 30, self.title)
        
        # Calculate dimensions
        margin = 60
        chart_width = self.width() - 2 * margin
        chart_height = self.height() - 2 * margin - 40
        
        if not self.data or sum(self.data.values()) == 0:
            painter.setPen(QColor("#8899aa"))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignCenter, "No data available")
            return
        
        # Draw axes
        painter.setPen(QPen(QColor("#1a4a5a"), 2))
        # Y-axis
        painter.drawLine(margin, margin + 40, margin, margin + 40 + chart_height)
        # X-axis
        painter.drawLine(margin, margin + 40 + chart_height, 
                        margin + chart_width, margin + 40 + chart_height)
        
        # Calculate bar dimensions
        num_bars = len(self.data)
        bar_width = (chart_width - (num_bars + 1) * 20) / num_bars
        max_value = max(self.data.values())
        
        # Draw bars
        x = margin + 20
        for category, count in self.data.items():
            # Calculate bar height
            if max_value > 0:
                bar_height = (count / max_value) * chart_height
            else:
                bar_height = 0
            
            # Draw bar
            color = QColor(self.colors.get(category, "#8899aa"))
            painter.fillRect(
                int(x), 
                int(margin + 40 + chart_height - bar_height),
                int(bar_width),
                int(bar_height),
                color
            )
            
            # Draw count on top of bar
            painter.setPen(QColor("#e0e6ed"))
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            count_text = str(count)
            text_rect = painter.fontMetrics().boundingRect(count_text)
            painter.drawText(
                int(x + bar_width/2 - text_rect.width()/2),
                int(margin + 40 + chart_height - bar_height - 10),
                count_text
            )
            
            # Draw category label
            painter.setPen(QColor("#8899aa"))
            painter.setFont(QFont("Arial", 10))
            label_rect = painter.fontMetrics().boundingRect(category)
            painter.drawText(
                int(x + bar_width/2 - label_rect.width()/2),
                int(margin + 40 + chart_height + 20),
                category
            )
            
            x += bar_width + 20
        
        painter.end()


class PieChartWidget(QWidget):
    """Custom widget to draw a pie chart."""
    
    def __init__(self, data: Dict[str, int], colors: Dict[str, str], title: str = ""):
        super().__init__()
        self.data = data
        self.colors = colors
        self.title = title
        self.setMinimumHeight(360)
        self.setMinimumWidth(420)
    
    def paintEvent(self, event):
        """Draw the pie chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor("#0d2137"))
        
        # Title
        if self.title:
            painter.setPen(QColor("#00d4aa"))
            painter.setFont(QFont("Arial", 14, QFont.Bold))
            painter.drawText(20, 30, self.title)
        
        total = sum(self.data.values())
        if total == 0:
            painter.setPen(QColor("#8899aa"))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignCenter, "No data available")
            return
        
        # Reserve compact bottom area for legend and maximize pie area above it.
        items = list(self.data.items())
        col_count = 2 if len(items) > 3 else 1
        row_count = max(1, math.ceil(len(items) / col_count))
        legend_row_h = 24
        legend_height = row_count * legend_row_h + 16

        chart_area_h = max(220, self.height() - legend_height - 18)
        max_diameter = min(int(self.width() * 0.62), int(chart_area_h * 0.80))
        size = max(180, max_diameter)
        center_x = self.width() // 2
        center_y = (chart_area_h // 2) + 4
        
        # Draw pie slices
        start_angle = 0
        for category, count in self.data.items():
            span_angle = int((count / total) * 360 * 16)  # Qt uses 1/16th degree
            
            color = QColor(self.colors.get(category, "#8899aa"))
            painter.setBrush(color)
            painter.setPen(QPen(QColor("#0a1929"), 2))
            
            painter.drawPie(
                center_x - size//2, center_y - size//2,
                size, size,
                start_angle, span_angle
            )
            
            start_angle += span_angle
        
        # Draw centered legend below the pie chart.
        legend_y = self.height() - legend_height + 8
        painter.setFont(QFont("Arial", 10))
        fm = painter.fontMetrics()
        item_width = 0
        for category, count in items:
            percentage = (count / total) * 100
            text = f"{category}: {count} ({percentage:.1f}%)"
            item_width = max(item_width, 22 + fm.horizontalAdvance(text))

        col_gap = 24
        total_legend_w = (item_width * col_count) + (col_gap * (col_count - 1))
        legend_x0 = max(16, (self.width() - total_legend_w) // 2)

        for idx, (category, count) in enumerate(items):
            row = idx // col_count
            col = idx % col_count
            legend_x = legend_x0 + col * (item_width + col_gap)
            y = legend_y + row * legend_row_h

            # Color box
            color = QColor(self.colors.get(category, "#8899aa"))
            painter.fillRect(legend_x, y, 15, 15, color)
            
            # Label
            painter.setPen(QColor("#e0e6ed"))
            percentage = (count / total) * 100
            text = f"{category}: {count} ({percentage:.1f}%)"
            painter.drawText(legend_x + 22, y + 12, text)
        
        painter.end()


class AnalyticsDashboard(QWidget):
    """Analytics dashboard showing risk and type distribution charts."""
    
    back_requested = Signal()
    filter_by_risk = Signal(str)  # Signal to filter evidence by risk level
    
    def __init__(self, case_id: int = None):
        super().__init__()
        self.setObjectName("analyticsDashboard")
        self.case_id = case_id
        self.database = Database()
        self.evidence_data = []
        self._setup_ui()
        self._apply_styles()
        if case_id:
            self.load_analytics()
    
    def set_case_id(self, case_id: int):
        """Set the current case ID and reload analytics."""
        self.case_id = case_id
        self.load_analytics()
    
    def _setup_ui(self):
        """Setup the analytics dashboard UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 20)
        main_layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("‹ Back to Case")
        back_btn.setFont(QFont("Arial", 12))
        back_btn.setFixedSize(155, 35)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8899aa;
                border: 2px solid #1a4a5a;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #122a3a;
                border-color: #40e0d0;
                color: #e0e6ed;
            }
        """)
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)
        
        header_layout.addStretch()
        
        # Title
        self.title_label = QLabel("Evidence Analytics Dashboard")
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.title_label.setStyleSheet("color: #00d4aa;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Side-by-side analytics sections (no scroll view).
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        risk_section = self._create_risk_section()
        type_section = self._create_type_section()
        content_layout.addWidget(risk_section, 1)
        content_layout.addWidget(type_section, 1)

        main_layout.addLayout(content_layout, 1)
    
    def _create_risk_section(self) -> QFrame:
        """Create the risk level analytics section."""
        section = QFrame()
        section.setObjectName("riskSection")
        section.setFrameShape(QFrame.StyledPanel)
        section.setStyleSheet("""
            QFrame#riskSection {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(section)
        layout.setSpacing(20)
        
        # Section header
        header_layout = QHBoxLayout()
        
        section_title = QLabel("Evidence Risk Distribution")
        section_title.setFont(QFont("Arial", 18, QFont.Bold))
        section_title.setStyleSheet("color: #00d4aa;")
        header_layout.addWidget(section_title)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedSize(100, 30)
        refresh_btn.clicked.connect(self.load_analytics)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Description
        desc = QLabel("Automatic risk assessment based on file type, size, and modification date")
        desc.setStyleSheet("color: #8899aa; font-size: 12px; background: transparent; border: none; padding: 0px;")
        layout.addWidget(desc)
        
        # Bar chart
        self.risk_chart = BarChartWidget(
            {'Low': 0, 'Medium': 0, 'High': 0},
            {'Low': '#10b981', 'Medium': '#f59e0b', 'High': '#ef4444'},
            ""
        )
        layout.addWidget(self.risk_chart, 1)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(14)
        filter_label = QLabel("Filters:")
        filter_label.setStyleSheet("color: #e0e6ed; font-size: 12px; font-weight: 600;")
        filter_layout.addWidget(filter_label)

        self.low_risk_check = QCheckBox("Low")
        self.low_risk_check.setChecked(True)
        self.low_risk_check.setStyleSheet("color: #10b981; font-size: 12px;")
        self.low_risk_check.stateChanged.connect(self._on_risk_checkbox_changed)
        filter_layout.addWidget(self.low_risk_check)

        self.medium_risk_check = QCheckBox("Medium")
        self.medium_risk_check.setChecked(True)
        self.medium_risk_check.setStyleSheet("color: #f59e0b; font-size: 12px;")
        self.medium_risk_check.stateChanged.connect(self._on_risk_checkbox_changed)
        filter_layout.addWidget(self.medium_risk_check)

        self.high_risk_check = QCheckBox("High")
        self.high_risk_check.setChecked(True)
        self.high_risk_check.setStyleSheet("color: #ef4444; font-size: 12px;")
        self.high_risk_check.stateChanged.connect(self._on_risk_checkbox_changed)
        filter_layout.addWidget(self.high_risk_check)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        return section
    
    def _create_type_section(self) -> QFrame:
        """Create the file type distribution section."""
        section = QFrame()
        section.setObjectName("typeSection")
        section.setFrameShape(QFrame.StyledPanel)
        section.setStyleSheet("""
            QFrame#typeSection {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        # Section header
        section_title = QLabel("File Type Distribution")
        section_title.setFont(QFont("Arial", 18, QFont.Bold))
        section_title.setStyleSheet("color: #00d4aa;")
        section_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(section_title)
        
        # Description
        desc = QLabel("Breakdown of evidence files by type category")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        desc.setStyleSheet("color: #8899aa; font-size: 12px; background: transparent; border: none; padding: 0px;")
        layout.addWidget(desc)
        
        # Pie chart
        self.type_chart = PieChartWidget(
            {},
            {
                'Document': '#3b82f6',
                'Image': '#10b981',
                'Video': '#8b5cf6',
                'Archive': '#f59e0b',
                'Log': '#ef4444',
                'Other': '#6b7280'
            },
            ""
        )
        layout.addWidget(self.type_chart, 1)
        
        return section
    
    def _apply_styles(self):
        """Apply dashboard styles."""
        self.setStyleSheet("""
            QWidget#analyticsDashboard {
                background-color: #0a1929;
                color: #e0e6ed;
            }
            QLabel {
                background: transparent;
                border: none;
            }
            QPushButton {
                background-color: #40e0d0;
                color: #0a1929;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
            QCheckBox {
                spacing: 6px;
                background: transparent;
                border: none;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #1a4a5a;
                border-radius: 3px;
                background-color: #0d2137;
            }
            QCheckBox::indicator:checked {
                background-color: #40e0d0;
                border-color: #40e0d0;
            }
        """)
    
    def load_analytics(self):
        """Load analytics data from database."""
        if not self.case_id:
            return
        
        # Get case info
        case = self.database.get_case(self.case_id)
        if case:
            self.title_label.setText(f"Analytics - {case['name']}")
        
        # Get all evidence
        self.evidence_data = self.database.get_evidence_for_case(self.case_id)
        
        self._on_risk_checkbox_changed()
        
        # Calculate type distribution
        type_counts = {}
        for evidence in self.evidence_data:
            file_type = self._determine_type(evidence.get('file_extension', ''))
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
        
        # Update type chart
        self.type_chart.data = type_counts
        self.type_chart.update()
    
    def _determine_type(self, extension: str) -> str:
        """Determine file type category from extension."""
        ext = extension.lower()
        
        doc_exts = ['.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt']
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.svg']
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        archive_exts = ['.zip', '.rar', '.7z', '.tar', '.gz']
        log_exts = ['.log']
        
        if ext in doc_exts:
            return 'Document'
        elif ext in image_exts:
            return 'Image'
        elif ext in video_exts:
            return 'Video'
        elif ext in archive_exts:
            return 'Archive'
        elif ext in log_exts:
            return 'Log'
        else:
            return 'Other'
    
    def _compute_risk_counts(self) -> Dict[str, int]:
        """Compute unfiltered risk-level counts from loaded evidence."""
        risk_counts = {'Low': 0, 'Medium': 0, 'High': 0}
        for evidence in self.evidence_data:
            risk = evidence.get('risk_level', 'Low')
            if risk in risk_counts:
                risk_counts[risk] += 1
        return risk_counts

    def _on_risk_checkbox_changed(self):
        """Update bar chart using selected risk-level checkboxes."""
        risk_counts = self._compute_risk_counts()

        if not self.low_risk_check.isChecked():
            risk_counts['Low'] = 0
        if not self.medium_risk_check.isChecked():
            risk_counts['Medium'] = 0
        if not self.high_risk_check.isChecked():
            risk_counts['High'] = 0

        selected = []
        if self.low_risk_check.isChecked():
            selected.append('Low')
        if self.medium_risk_check.isChecked():
            selected.append('Medium')
        if self.high_risk_check.isChecked():
            selected.append('High')

        self.risk_chart.data = risk_counts
        self.risk_chart.update()

        self.filter_by_risk.emit('+'.join(selected) if selected else 'None')
