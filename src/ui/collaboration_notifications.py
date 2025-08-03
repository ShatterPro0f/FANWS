"""
Collaboration Notification System with QSystemTrayIcon
Provides real-time notifications for collaborative features
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from PyQt5.QtCore import (QObject, pyqtSignal, QTimer, QThread,
                         QPropertyAnimation, QEasingCurve, QRect)
from PyQt5.QtWidgets import (QSystemTrayIcon, QMenu, QAction, QWidget,
                           QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QListWidget, QListWidgetItem, QMessageBox,
                           QDialog, QTextEdit, QLineEdit, QFormLayout,
                           QDialogButtonBox, QGroupBox, QCheckBox)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from enum import Enum

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Types of collaboration notifications"""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    VERSION_CONFLICT = "version_conflict"
    CONCURRENT_EDIT = "concurrent_edit"
    EXPORT_COMPLETE = "export_complete"
    SYSTEM_MESSAGE = "system_message"
    BUG_REPORT = "bug_report"

@dataclass
class CollaborationNotification:
    """Notification data structure"""
    id: str
    type: NotificationType
    title: str
    message: str
    timestamp: datetime
    project_name: str
    user_id: Optional[str] = None
    workflow_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    priority: str = "normal"  # low, normal, high, urgent
    read: bool = False
    action_required: bool = False

class CollaborationTrayIcon(QSystemTrayIcon):
    """
    System tray icon for collaboration notifications
    """

    # Signals for notification actions
    notification_clicked = pyqtSignal(str)  # notification_id
    user_action_requested = pyqtSignal(str, str)  # action_type, data
    bug_report_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize collaboration tray icon"""
        super().__init__(parent)

        self.notifications: List[CollaborationNotification] = []
        self.unread_count = 0
        self.collaboration_active = False

        # Initialize icon and menu
        self._setup_icon()
        self._setup_menu()
        self._setup_animations()

        # Connect signals
        self.activated.connect(self._on_tray_activated)
        self.messageClicked.connect(self._on_message_clicked)

        # Notification history window
        self.notification_window = None

        # Settings
        self.notifications_enabled = True
        self.sound_enabled = True
        self.popup_duration = 5000  # milliseconds

        # Show tray icon
        self.show()

        logger.info("Collaboration tray icon initialized")

    def _setup_icon(self):
        """Setup tray icon with dynamic indicator"""
        # Create base icon (using a simple colored circle for now)
        # In production, you'd use proper icons
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw main icon circle
        painter.setBrush(QColor(70, 130, 180))  # Steel blue
        painter.setPen(QColor(25, 25, 25))
        painter.drawEllipse(4, 4, 24, 24)

        # Draw collaboration indicator
        if self.collaboration_active:
            painter.setBrush(QColor(50, 205, 50))  # Lime green
            painter.drawEllipse(20, 20, 8, 8)

        # Draw notification badge
        if self.unread_count > 0:
            painter.setBrush(QColor(220, 20, 60))  # Crimson
            painter.drawEllipse(22, 2, 10, 10)

            if self.unread_count < 10:
                painter.setPen(QColor(255, 255, 255))
                painter.setFont(QFont("Arial", 6, QFont.Bold))
                painter.drawText(25, 9, str(self.unread_count))

        painter.end()

        icon = QIcon(pixmap)
        self.setIcon(icon)

    def _setup_menu(self):
        """Setup context menu"""
        self.menu = QMenu()

        # Collaboration status
        self.status_action = QAction("Collaboration: Offline", self.menu)
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)

        self.menu.addSeparator()

        # Notifications
        self.notifications_action = QAction("Show Notifications", self.menu)
        self.notifications_action.triggered.connect(self._show_notifications)
        self.menu.addAction(self.notifications_action)

        # Settings
        self.settings_action = QAction("Notification Settings", self.menu)
        self.settings_action.triggered.connect(self._show_settings)
        self.menu.addAction(self.settings_action)

        self.menu.addSeparator()

        # Bug report
        self.bug_report_action = QAction("Report Bug", self.menu)
        self.bug_report_action.triggered.connect(self._show_bug_report)
        self.menu.addAction(self.bug_report_action)

        self.menu.addSeparator()

        # Exit
        self.exit_action = QAction("Exit", self.menu)
        self.exit_action.triggered.connect(self._exit_application)
        self.menu.addAction(self.exit_action)

        self.setContextMenu(self.menu)

    def _setup_animations(self):
        """Setup notification animations"""
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._blink_icon)
        self.blink_state = False

    def add_notification(self, notification: CollaborationNotification):
        """
        Add a new collaboration notification

        Args:
            notification: Notification to add
        """
        try:
            # Add to notification list
            self.notifications.insert(0, notification)

            # Update unread count
            if not notification.read:
                self.unread_count += 1

            # Update tray icon
            self._setup_icon()

            # Show system notification if enabled
            if self.notifications_enabled:
                self._show_system_notification(notification)

            # Start blinking for urgent notifications
            if notification.priority == "urgent":
                self._start_blinking()

            # Limit notification history
            if len(self.notifications) > 100:
                self.notifications = self.notifications[:100]

            logger.info(f"Added notification: {notification.title}")

        except Exception as e:
            logger.error(f"Error adding notification: {e}")

    def _show_system_notification(self, notification: CollaborationNotification):
        """Show system tray notification"""
        try:
            # Map notification types to icons
            icon_map = {
                NotificationType.USER_JOINED: QSystemTrayIcon.Information,
                NotificationType.USER_LEFT: QSystemTrayIcon.Information,
                NotificationType.VERSION_CONFLICT: QSystemTrayIcon.Warning,
                NotificationType.CONCURRENT_EDIT: QSystemTrayIcon.Warning,
                NotificationType.EXPORT_COMPLETE: QSystemTrayIcon.Information,
                NotificationType.SYSTEM_MESSAGE: QSystemTrayIcon.Information,
                NotificationType.BUG_REPORT: QSystemTrayIcon.Critical,
            }

            icon = icon_map.get(notification.type, QSystemTrayIcon.Information)

            # Show notification
            self.showMessage(
                notification.title,
                notification.message,
                icon,
                self.popup_duration
            )

        except Exception as e:
            logger.error(f"Error showing system notification: {e}")

    def _start_blinking(self):
        """Start blinking animation for urgent notifications"""
        if not self.blink_timer.isActive():
            self.blink_timer.start(500)  # Blink every 500ms

    def _stop_blinking(self):
        """Stop blinking animation"""
        self.blink_timer.stop()
        self.blink_state = False
        self._setup_icon()

    def _blink_icon(self):
        """Toggle icon visibility for blinking effect"""
        self.blink_state = not self.blink_state
        if self.blink_state:
            self.hide()
        else:
            self.show()

    def mark_notification_read(self, notification_id: str):
        """Mark a notification as read"""
        try:
            for notification in self.notifications:
                if notification.id == notification_id:
                    if not notification.read:
                        notification.read = True
                        self.unread_count = max(0, self.unread_count - 1)
                        self._setup_icon()
                    break

        except Exception as e:
            logger.error(f"Error marking notification read: {e}")

    def set_collaboration_status(self, active: bool, user_count: int = 0):
        """Update collaboration status"""
        self.collaboration_active = active

        if active:
            status_text = f"Collaboration: Online ({user_count} users)"
        else:
            status_text = "Collaboration: Offline"

        self.status_action.setText(status_text)
        self._setup_icon()

    def _show_notifications(self):
        """Show notifications window"""
        if self.notification_window is None:
            self.notification_window = NotificationWindow()
            self.notification_window.notification_clicked.connect(self.notification_clicked)
            self.notification_window.mark_read_requested.connect(self.mark_notification_read)

        self.notification_window.update_notifications(self.notifications)
        self.notification_window.show()
        self.notification_window.raise_()
        self.notification_window.activateWindow()

    def _show_settings(self):
        """Show notification settings dialog"""
        dialog = NotificationSettingsDialog(self)

        # Set current settings
        dialog.notifications_enabled.setChecked(self.notifications_enabled)
        dialog.sound_enabled.setChecked(self.sound_enabled)
        dialog.popup_duration.setValue(self.popup_duration // 1000)

        if dialog.exec_() == QDialog.Accepted:
            # Apply settings
            self.notifications_enabled = dialog.notifications_enabled.isChecked()
            self.sound_enabled = dialog.sound_enabled.isChecked()
            self.popup_duration = dialog.popup_duration.value() * 1000

    def _show_bug_report(self):
        """Show bug report dialog"""
        self.bug_report_requested.emit()

    def _on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_notifications()
        elif reason == QSystemTrayIcon.Trigger:
            # Single click - mark all as read if there are unread notifications
            if self.unread_count > 0:
                for notification in self.notifications:
                    notification.read = True
                self.unread_count = 0
                self._setup_icon()
                self._stop_blinking()

    def _on_message_clicked(self):
        """Handle system notification click"""
        self._show_notifications()

    def _exit_application(self):
        """Exit application"""
        self.user_action_requested.emit("exit", "")

class NotificationWindow(QDialog):
    """Window for displaying notification history"""

    notification_clicked = pyqtSignal(str)
    mark_read_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Collaboration Notifications")
        self.setMinimumSize(400, 500)
        self.setup_ui()

    def setup_ui(self):
        """Setup notification window UI"""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Collaboration Notifications")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)

        # Clear all button
        clear_button = QPushButton("Mark All Read")
        clear_button.clicked.connect(self._mark_all_read)
        header_layout.addWidget(clear_button)

        layout.addLayout(header_layout)

        # Notification list
        self.notification_list = QListWidget()
        self.notification_list.itemClicked.connect(self._on_notification_clicked)
        layout.addWidget(self.notification_list)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

    def update_notifications(self, notifications: List[CollaborationNotification]):
        """Update notification list"""
        self.notification_list.clear()

        for notification in notifications:
            item = QListWidgetItem()

            # Create notification widget
            notification_widget = NotificationWidget(notification)
            notification_widget.mark_read_requested.connect(self.mark_read_requested)

            item.setSizeHint(notification_widget.sizeHint())
            self.notification_list.addItem(item)
            self.notification_list.setItemWidget(item, notification_widget)

    def _mark_all_read(self):
        """Mark all notifications as read"""
        for i in range(self.notification_list.count()):
            item = self.notification_list.item(i)
            widget = self.notification_list.itemWidget(item)
            if isinstance(widget, NotificationWidget):
                widget.mark_read()

    def _on_notification_clicked(self, item):
        """Handle notification click"""
        widget = self.notification_list.itemWidget(item)
        if isinstance(widget, NotificationWidget):
            self.notification_clicked.emit(widget.notification.id)

class NotificationWidget(QWidget):
    """Widget for displaying individual notifications"""

    mark_read_requested = pyqtSignal(str)

    def __init__(self, notification: CollaborationNotification, parent=None):
        super().__init__(parent)
        self.notification = notification
        self.setup_ui()

    def setup_ui(self):
        """Setup notification widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # Header with title and timestamp
        header_layout = QHBoxLayout()

        title_label = QLabel(self.notification.title)
        title_font = QFont()
        title_font.setBold(not self.notification.read)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        timestamp_label = QLabel(self.notification.timestamp.strftime("%H:%M"))
        timestamp_label.setStyleSheet("color: gray; font-size: 10px;")
        header_layout.addWidget(timestamp_label)

        layout.addLayout(header_layout)

        # Message
        message_label = QLabel(self.notification.message)
        message_label.setWordWrap(True)
        if not self.notification.read:
            message_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(message_label)

        # Visual indicator for unread
        if not self.notification.read:
            self.setStyleSheet("background-color: #f0f8ff; border-left: 3px solid #4682b4;")

    def mark_read(self):
        """Mark this notification as read"""
        if not self.notification.read:
            self.notification.read = True
            self.mark_read_requested.emit(self.notification.id)

            # Update visual style
            self.setStyleSheet("")
            for child in self.findChildren(QLabel):
                font = child.font()
                font.setBold(False)
                child.setFont(font)

class NotificationSettingsDialog(QDialog):
    """Dialog for notification settings"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Notification Settings")
        self.setFixedSize(300, 200)
        self.setup_ui()

    def setup_ui(self):
        """Setup settings dialog UI"""
        layout = QFormLayout(self)

        # Enable notifications
        self.notifications_enabled = QCheckBox("Enable notifications")
        layout.addRow("Notifications:", self.notifications_enabled)

        # Enable sound
        self.sound_enabled = QCheckBox("Enable sound")
        layout.addRow("Sound:", self.sound_enabled)

        # Popup duration
        self.popup_duration = QLineEdit()
        self.popup_duration.setText("5")
        layout.addRow("Popup duration (seconds):", self.popup_duration)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

class BugReportDialog(QDialog):
    """Dialog for bug reporting"""

    bug_report_submitted = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Report Bug")
        self.setMinimumSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        """Setup bug report dialog UI"""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Report a Bug")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)

        # Form
        form_layout = QFormLayout()

        # Bug title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Brief description of the issue")
        form_layout.addRow("Title:", self.title_edit)

        # Category
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("e.g., UI, Export, Collaboration")
        form_layout.addRow("Category:", self.category_edit)

        # Priority
        self.priority_edit = QLineEdit()
        self.priority_edit.setPlaceholderText("Low, Medium, High, Critical")
        form_layout.addRow("Priority:", self.priority_edit)

        layout.addLayout(form_layout)

        # Description
        description_label = QLabel("Description:")
        layout.addWidget(description_label)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(
            "Please describe the bug in detail:\n"
            "- What were you doing when it happened?\n"
            "- What did you expect to happen?\n"
            "- What actually happened?\n"
            "- Can you reproduce it?"
        )
        layout.addWidget(self.description_edit)

        # System info checkbox
        self.include_logs = QCheckBox("Include system logs and debug information")
        self.include_logs.setChecked(True)
        layout.addWidget(self.include_logs)

        # Buttons
        button_layout = QHBoxLayout()

        submit_button = QPushButton("Submit Bug Report")
        submit_button.clicked.connect(self._submit_report)
        button_layout.addWidget(submit_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _submit_report(self):
        """Submit bug report"""
        try:
            # Validate required fields
            if not self.title_edit.text().strip():
                QMessageBox.warning(self, "Validation Error", "Please enter a title.")
                return

            if not self.description_edit.toPlainText().strip():
                QMessageBox.warning(self, "Validation Error", "Please enter a description.")
                return

            # Create bug report data
            bug_report = {
                'title': self.title_edit.text().strip(),
                'category': self.category_edit.text().strip() or "General",
                'priority': self.priority_edit.text().strip() or "Medium",
                'description': self.description_edit.toPlainText().strip(),
                'include_logs': self.include_logs.isChecked(),
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': "current_user"  # This would be populated from app context
            }

            # Emit signal with bug report data
            self.bug_report_submitted.emit(bug_report)

            # Show confirmation
            QMessageBox.information(
                self,
                "Bug Report Submitted",
                "Thank you for your bug report. It has been saved and will be reviewed."
            )

            self.accept()

        except Exception as e:
            logger.error(f"Error submitting bug report: {e}")
            QMessageBox.critical(self, "Error", f"Failed to submit bug report: {e}")

# Utility functions for creating common notifications
def create_user_joined_notification(project_name: str, user_id: str) -> CollaborationNotification:
    """Create notification for user joining"""
    return CollaborationNotification(
        id=f"user_joined_{user_id}_{datetime.utcnow().timestamp()}",
        type=NotificationType.USER_JOINED,
        title="User Joined",
        message=f"{user_id} joined the project",
        timestamp=datetime.utcnow(),
        project_name=project_name,
        user_id=user_id
    )

def create_version_conflict_notification(workflow_id: str, user_count: int) -> CollaborationNotification:
    """Create notification for version conflict"""
    return CollaborationNotification(
        id=f"conflict_{workflow_id}_{datetime.utcnow().timestamp()}",
        type=NotificationType.VERSION_CONFLICT,
        title="Version Conflict",
        message=f"Version conflict detected in workflow {workflow_id}",
        timestamp=datetime.utcnow(),
        project_name="current",
        workflow_id=workflow_id,
        priority="high",
        action_required=True
    )

def create_export_complete_notification(export_type: str, file_path: str) -> CollaborationNotification:
    """Create notification for completed export"""
    return CollaborationNotification(
        id=f"export_{datetime.utcnow().timestamp()}",
        type=NotificationType.EXPORT_COMPLETE,
        title="Export Complete",
        message=f"{export_type} export completed: {os.path.basename(file_path)}",
        timestamp=datetime.utcnow(),
        project_name="current",
        data={'export_type': export_type, 'file_path': file_path}
    )
