"""
Quick Stats Dashboard Screen
Feature 8: Recent Activity Feed
Feature 9: Quick Stats Dashboard

Displays comprehensive statistics and recent activity across all cases
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor
from datetime import datetime
from typing import List, Dict, Any, Optional

from backend.app.database import Database


class StatCard(QFrame):
    """Card widget displaying a single statistic."""
    
    def __init__(self, title: str, value: str, subtitle: str = "", color: str = "#40e0d0"):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
            }}
            QFrame:hover {{
                border-color: {color};
                background-color: #122a3a;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # Title (bold and teal)
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Bold))
        title_label.setStyleSheet("color: #40e0d0; background: transparent; border: none;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Value (large, bold, and colored)
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 36, QFont.Bold))
        value_label.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        value_label.setWordWrap(False)
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(value_label)
        
        # Subtitle (smaller, teal color)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(QFont("Arial", 9))
            subtitle_label.setStyleSheet("color: #40e0d0; background: transparent; border: none;")
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)
        
        layout.addStretch()
        self.setMinimumHeight(100)
        self.setMaximumHeight(130)
        self.setMinimumWidth(140)


class ActivityItem(QFrame):
    """Single activity item in the feed."""
    
    def __init__(self, activity: Dict[str, Any]):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #0d2137;
                border: 2px solid #1a4a5a;
                border-radius: 8px;
                padding: 12px;
            }
            QFrame:hover {
                background-color: #122a3a;
                border-color: #40e0d0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header row: action and timestamp
        header_layout = QHBoxLayout()
        
        # Action with icon
        action_text = activity.get('action', 'Unknown Action')
        icon = self._get_action_icon(action_text)
        action_label = QLabel(f"{icon} {action_text}")
        action_label.setFont(QFont("Arial", 12, QFont.Bold))
        action_label.setStyleSheet(f"color: {self._get_action_color(action_text)}; background: transparent; border: none;")
        header_layout.addWidget(action_label)
        
        header_layout.addStretch()
        
        # Timestamp
        timestamp = activity.get('timestamp', '')
        time_label = QLabel(self._format_timestamp(timestamp))
        time_label.setFont(QFont("Arial", 10))
        time_label.setStyleSheet("color: #6c7086; background: transparent; border: none;")
        header_layout.addWidget(time_label)
        
        layout.addLayout(header_layout)
        
        # Details (more prominent)
        details = activity.get('details', '')
        if details:
            details_label = QLabel(details)
            details_label.setFont(QFont("Arial", 11, QFont.Bold))
            details_label.setStyleSheet("color: #e0e6ed; background: transparent; border: none;")
            details_label.setWordWrap(True)
            layout.addWidget(details_label)
        
        # Footer: case info with case_id
        footer_layout = QHBoxLayout()
        
        case_id = activity.get('case_id', 'N/A')
        case_name = activity.get('case_name', 'Unknown Case')
        case_label = QLabel(f"Case #{case_id}: {case_name}")
        case_label.setFont(QFont("Arial", 10, QFont.Bold))
        case_label.setStyleSheet("color: #40e0d0; background: transparent; border: none;")
        footer_layout.addWidget(case_label)
        
        footer_layout.addStretch()
        
        user_name = activity.get('user_name', 'Unknown User')
        if user_name and user_name != 'Unknown User':
            user_label = QLabel(f"by {user_name}")
            user_label.setFont(QFont("Arial", 10))
            user_label.setStyleSheet("color: #8899aa; background: transparent; border: none;")
            footer_layout.addWidget(user_label)
        
        layout.addLayout(footer_layout)
    
    def _get_action_icon(self, action: str) -> str:
        """Get icon for action type."""
        action_lower = action.lower()
        if 'upload' in action_lower or 'add' in action_lower:
            return '↑'
        elif 'delete' in action_lower or 'remove' in action_lower:
            return '×'
        elif 'update' in action_lower or 'edit' in action_lower:
            return '✎'
        elif 'create' in action_lower:
            return '+'
        elif 'analyze' in action_lower or 'scan' in action_lower:
            return '⚲'
        elif 'export' in action_lower or 'report' in action_lower:
            return '⎙'
        elif 'milestone' in action_lower:
            return '◉'
        elif 'status' in action_lower:
            return '↻'
        else:
            return '•'
    
    def _get_action_color(self, action: str) -> str:
        """Get color for action type."""
        action_lower = action.lower()
        if 'upload' in action_lower or 'add' in action_lower or 'create' in action_lower:
            return '#10b981'  # Green
        elif 'delete' in action_lower or 'remove' in action_lower:
            return '#ef4444'  # Red
        elif 'update' in action_lower or 'edit' in action_lower:
            return '#f59e0b'  # Orange
        elif 'analyze' in action_lower or 'scan' in action_lower:
            return '#3b82f6'  # Blue
        elif 'export' in action_lower or 'report' in action_lower:
            return '#8b5cf6'  # Purple
        else:
            return '#40e0d0'  # Teal
    
    def _format_timestamp(self, timestamp_str: str) -> str:
        """Format timestamp for display."""
        if not timestamp_str:
            return 'Unknown time'
        
        try:
            if isinstance(timestamp_str, str):
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                dt = timestamp_str
            
            now = datetime.now()
            diff = now - dt.replace(tzinfo=None)
            
            # Show relative time for recent activities
            if diff.days == 0:
                if diff.seconds < 60:
                    return 'Just now'
                elif diff.seconds < 3600:
                    minutes = diff.seconds // 60
                    return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
                else:
                    hours = diff.seconds // 3600
                    return f'{hours} hour{"s" if hours != 1 else ""} ago'
            elif diff.days == 1:
                return 'Yesterday'
            elif diff.days < 7:
                return f'{diff.days} days ago'
            else:
                return dt.strftime('%b %d, %Y at %I:%M %p')
        except:
            return str(timestamp_str) if timestamp_str else 'Unknown time'


class QuickStatsDashboard(QWidget):
    """
    Quick Stats Dashboard with Recent Activity Feed.
    
    Feature 8: Recent Activity Feed - Shows recent actions across cases
    Feature 9: Quick Stats Dashboard - Displays comprehensive statistics
    """
    
    back_requested = Signal()
    
    def __init__(self, user_id: Optional[int] = None):
        super().__init__()
        self.setObjectName("quickStatsDashboard")
        self.database = Database()
        self.current_user_id = user_id
        self._setup_ui()
        self._apply_styles()
        
        # Auto-refresh timer (every 30 seconds)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(30000)  # 30 seconds
        
        self.load_data()
    
    def set_current_user(self, user_id: Optional[int]):
        """Set current user context."""
        self.current_user_id = user_id
        self.load_data()
    
    def _setup_ui(self):
        """Setup the dashboard UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("‹ Back to Cases")
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
        title_label = QLabel("Investigation Statistics Dashboard")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #00d4aa;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFont(QFont("Arial", 12, QFont.Bold))
        refresh_btn.setFixedSize(130, 38)
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Stats cards grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        
        self.total_cases_card = StatCard("Total Cases", "0", "All investigation cases", "#40e0d0")
        self.active_cases_card = StatCard("Active Cases", "0", "Currently in progress", "#10b981")
        self.total_evidence_card = StatCard("Total Evidence", "0", "Files collected", "#3b82f6")
        self.analyzed_card = StatCard("Analyzed", "0", "Evidence reviewed", "#8b5cf6")
        self.pending_card = StatCard("Pending", "0", "Awaiting review", "#f59e0b")
        self.high_risk_card = StatCard("High Risk", "0", "Critical items", "#ef4444")
        
        stats_grid.addWidget(self.total_cases_card, 0, 0)
        stats_grid.addWidget(self.active_cases_card, 0, 1)
        stats_grid.addWidget(self.total_evidence_card, 0, 2)
        stats_grid.addWidget(self.analyzed_card, 1, 0)
        stats_grid.addWidget(self.pending_card, 1, 1)
        stats_grid.addWidget(self.high_risk_card, 1, 2)
        
        main_layout.addLayout(stats_grid)
        
        # Recent Activity Feed section
        activity_header = QHBoxLayout()
        
        activity_title = QLabel("Recent Activity Feed")
        activity_title.setFont(QFont("Arial", 20, QFont.Bold))
        activity_title.setStyleSheet("color: #00d4aa;")
        activity_header.addWidget(activity_title)
        
        activity_header.addStretch()
        
        self.activity_count_label = QLabel("Last 20 activities")
        self.activity_count_label.setFont(QFont("Arial", 11))
        self.activity_count_label.setStyleSheet("color: #8899aa;")
        activity_header.addWidget(self.activity_count_label)
        
        main_layout.addLayout(activity_header)
        
        # Activity feed scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
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
        
        # Activity feed container
        self.activity_container = QWidget()
        self.activity_layout = QVBoxLayout(self.activity_container)
        self.activity_layout.setSpacing(10)
        self.activity_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.activity_container)
        main_layout.addWidget(scroll_area, 1)  # Give it stretch factor
        
        # Empty state message
        self.empty_label = QLabel("No recent activity to display")
        self.empty_label.setFont(QFont("Arial", 13))
        self.empty_label.setStyleSheet("color: #6c7086;")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.hide()
        self.activity_layout.addWidget(self.empty_label)
    
    def _apply_styles(self):
        """Apply dashboard styles."""
        self.setStyleSheet("""
            QWidget#quickStatsDashboard {
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
            }
            QPushButton:hover {
                background-color: #2dd4bf;
            }
        """)
    
    def load_data(self):
        """Load statistics and activity data."""
        # Load stats
        stats = self.database.get_dashboard_stats(user_id=self.current_user_id)
        
        # Update stat cards
        self.total_cases_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(str(stats.get('total_cases', 0)))
        self.active_cases_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(str(stats.get('active_cases', 0)))
        self.total_evidence_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(str(stats.get('total_evidence', 0)))
        
        evidence_status = stats.get('evidence_status', {})
        self.analyzed_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(str(evidence_status.get('Analyzed', 0)))
        self.pending_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(str(evidence_status.get('Pending', 0)))
        
        risk_breakdown = stats.get('risk_breakdown', {})
        self.high_risk_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(str(risk_breakdown.get('High', 0)))
        
        # Update stat card values properly
        self._update_stat_card(self.total_cases_card, str(stats.get('total_cases', 0)))
        self._update_stat_card(self.active_cases_card, str(stats.get('active_cases', 0)))
        self._update_stat_card(self.total_evidence_card, str(stats.get('total_evidence', 0)))
        self._update_stat_card(self.analyzed_card, str(evidence_status.get('Analyzed', 0)))
        self._update_stat_card(self.pending_card, str(evidence_status.get('Pending', 0)))
        self._update_stat_card(self.high_risk_card, str(risk_breakdown.get('High', 0)))
        
        # Load recent activity
        activities = self.database.get_recent_activity(
            case_id=None,
            limit=20,
            user_id=self.current_user_id
        )
        
        self._populate_activity_feed(activities)
    
    def _update_stat_card(self, card: StatCard, value: str):
        """Update the value in a stat card."""
        # Find the value label (second label, which is the large number)
        labels = card.findChildren(QLabel)
        if len(labels) >= 2:
            labels[1].setText(value)
    
    def _populate_activity_feed(self, activities: List[Dict[str, Any]]):
        """Populate the activity feed with items."""
        # Clear existing items
        while self.activity_layout.count() > 0:
            item = self.activity_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not activities:
            self.empty_label = QLabel("No recent activity to display")
            self.empty_label.setFont(QFont("Arial", 13))
            self.empty_label.setStyleSheet("color: #6c7086;")
            self.empty_label.setAlignment(Qt.AlignCenter)
            self.activity_layout.addWidget(self.empty_label)
            self.activity_count_label.setText("No activities")
        else:
            self.activity_count_label.setText(f"Last {len(activities)} activities")
            
            for activity in activities:
                activity_item = ActivityItem(activity)
                self.activity_layout.addWidget(activity_item)
            
            # Add stretch at the end
            self.activity_layout.addStretch()
    
    def closeEvent(self, event):
        """Stop timer when widget is closed."""
        self.refresh_timer.stop()
        super().closeEvent(event)
