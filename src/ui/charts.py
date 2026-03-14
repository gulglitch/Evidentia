"""
Charts Module
Data visualization charts for risk levels and statistics
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from typing import Dict


class RiskLevelChart(QWidget):
    """Bar chart showing risk level distribution."""
    
    def __init__(self):
        super().__init__()
        self.data = {'Low': 0, 'Medium': 0, 'High': 0}
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the chart UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Risk Distribution")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #cdd6f4;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Chart area
        self.chart_widget = RiskBarChart()
        layout.addWidget(self.chart_widget)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.setAlignment(Qt.AlignCenter)
        
        for risk, color in [("Low", "#a6e3a1"), ("Medium", "#f9e2af"), ("High", "#f38ba8")]:
            indicator = QFrame()
            indicator.setFixedSize(12, 12)
            indicator.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
            legend_layout.addWidget(indicator)
            
            label = QLabel(risk)
            label.setStyleSheet("color: #a6adc8; font-size: 11px; margin-right: 10px;")
            legend_layout.addWidget(label)
        
        layout.addLayout(legend_layout)
    
    def _apply_styles(self):
        """Apply chart styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 5px;
            }
        """)
    
    def update_data(self, data: Dict[str, int]):
        """Update chart with new data."""
        self.data = {
            'Low': data.get('Low', 0),
            'Medium': data.get('Medium', 0),
            'High': data.get('High', 0)
        }
        self.chart_widget.set_data(self.data)


class RiskBarChart(QWidget):
    """Custom painted bar chart."""
    
    def __init__(self):
        super().__init__()
        self.data = {'Low': 0, 'Medium': 0, 'High': 0}
        self.colors = {
            'Low': QColor('#a6e3a1'),
            'Medium': QColor('#f9e2af'),
            'High': QColor('#f38ba8'),
        }
        self.setMinimumHeight(150)
    
    def set_data(self, data: Dict[str, int]):
        """Set chart data and trigger repaint."""
        self.data = data
        self.update()
    
    def paintEvent(self, event):
        """Paint the bar chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        total = sum(self.data.values())
        if total == 0:
            # Draw "No data" message
            painter.setPen(QPen(QColor('#6c7086')))
            painter.setFont(QFont('Arial', 10))
            painter.drawText(self.rect(), Qt.AlignCenter, "No data available")
            return
        
        # Chart dimensions
        margin = 30
        chart_width = self.width() - 2 * margin
        chart_height = self.height() - 2 * margin
        bar_width = chart_width // 5
        gap = bar_width // 2
        
        max_value = max(self.data.values()) if self.data.values() else 1
        
        x = margin + gap
        for risk in ['Low', 'Medium', 'High']:
            value = self.data[risk]
            bar_height = int((value / max_value) * (chart_height - 20)) if max_value > 0 else 0
            
            # Draw bar
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(self.colors[risk]))
            
            y = self.height() - margin - bar_height
            painter.drawRoundedRect(x, y, bar_width, bar_height, 3, 3)
            
            # Draw value label
            painter.setPen(QPen(QColor('#cdd6f4')))
            painter.setFont(QFont('Arial', 9, QFont.Bold))
            painter.drawText(x, y - 5, bar_width, 20, Qt.AlignCenter, str(value))
            
            # Draw category label
            painter.setPen(QPen(QColor('#a6adc8')))
            painter.setFont(QFont('Arial', 8))
            painter.drawText(x, self.height() - margin + 5, bar_width, 20, Qt.AlignCenter, risk)
            
            x += bar_width + gap


class QuickStatsWidget(QWidget):
    """Quick statistics summary widget."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the stats UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)
        
        # Total files
        self.total_widget = self._create_stat_widget("Total Files", "0")
        layout.addWidget(self.total_widget)
        
        # Analyzed
        self.analyzed_widget = self._create_stat_widget("Analyzed", "0")
        layout.addWidget(self.analyzed_widget)
        
        # Pending
        self.pending_widget = self._create_stat_widget("Pending", "0")
        layout.addWidget(self.pending_widget)
        
        # Flagged
        self.flagged_widget = self._create_stat_widget("Flagged", "0")
        layout.addWidget(self.flagged_widget)
    
    def _create_stat_widget(self, label: str, value: str) -> QWidget:
        """Create a stat display widget."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #89b4fa;")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        name_label = QLabel(label)
        name_label.setStyleSheet("font-size: 11px; color: #a6adc8;")
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        return widget
    
    def _apply_styles(self):
        """Apply widget styles."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
            }
        """)
    
    def update_stats(self, stats: Dict[str, int]):
        """Update stats display."""
        self.total_widget.findChild(QLabel, "value").setText(str(stats.get('total', 0)))
        self.analyzed_widget.findChild(QLabel, "value").setText(str(stats.get('analyzed', 0)))
        self.pending_widget.findChild(QLabel, "value").setText(str(stats.get('pending', 0)))
        self.flagged_widget.findChild(QLabel, "value").setText(str(stats.get('flagged', 0)))
