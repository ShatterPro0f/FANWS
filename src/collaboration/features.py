"""
Feature Integration Module
Integrates workflow management, collaboration notifications, and bug reporting
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog

# Import new features
try:
    from ..core.configuration_manager import WorkflowManager, ConflictResolution, ConflictInfo
    from ..plugins.plugin_management_ui import (
        CollaborationTrayIcon, BugReportDialog, CollaborationNotification,
        NotificationType, create_user_joined_notification,
        create_version_conflict_notification, create_export_complete_notification
    )
    from .bug_reporting import get_bug_report_manager, submit_bug_report, report_exception
    FEATURES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some new features not available: {e}")
    FEATURES_AVAILABLE = False
    # Create fallback classes
    class WorkflowManager:
        pass
    class ConflictResolution:
        pass
    class ConflictInfo:
        pass

logger = logging.getLogger(__name__)

class CollaborationManager(QObject):
    """
    Main manager for collaboration features
    Integrates workflow management, notifications, and bug reporting
    """

    # Signals for UI integration
    feature_status_changed = pyqtSignal(str, bool)  # feature_name, enabled
    user_action_required = pyqtSignal(str, dict)    # action_type, data

    def __init__(self, project_name: str = "default", user_id: str = "local_user"):
        """
        Initialize collaboration manager

        Args:
            project_name: Name of the current project
            user_id: Identifier for current user
        """
        super().__init__()

        self.project_name = project_name
        self.user_id = user_id
        self.enabled = FEATURES_AVAILABLE

        # Initialize components
        self.workflow_manager = None
        self.tray_icon = None
        self.bug_report_manager = None

        # Feature status
        self.features = {
            'workflow_versioning': False,
            'collaboration_notifications': False,
            'bug_reporting': False,
            'database_pooling': False
        }

        if self.enabled:
            self._initialize_features()
        else:
            logger.warning("Collaboration features not available")

    def _initialize_features(self):
        """Initialize all collaboration features"""
        try:
            # Initialize workflow manager
            self._initialize_workflow_management()

            # Initialize collaboration notifications
            self._initialize_collaboration_notifications()

            # Initialize bug reporting
            self._initialize_bug_reporting()

            logger.info("Collaboration manager initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing collaboration features: {e}")
            self.enabled = False

    def _initialize_workflow_management(self):
        """Initialize workflow management with version control"""
        try:
            self.workflow_manager = WorkflowManager(self.project_name, self.user_id)

            # Connect workflow signals
            self.workflow_manager.version_conflict_detected.connect(self._handle_version_conflict)
            self.workflow_manager.version_conflict_resolved.connect(self._handle_conflict_resolved)
            self.workflow_manager.user_joined.connect(self._handle_user_joined)
            self.workflow_manager.user_left.connect(self._handle_user_left)
            self.workflow_manager.concurrent_edit_detected.connect(self._handle_concurrent_edit)

            self.features['workflow_versioning'] = True
            self.feature_status_changed.emit('workflow_versioning', True)

            logger.info("Workflow management initialized")

        except Exception as e:
            logger.error(f"Error initializing workflow management: {e}")
            self.features['workflow_versioning'] = False

    def _initialize_collaboration_notifications(self):
        """Initialize collaboration notifications with system tray"""
        try:
            # Check if system tray is available
            from PyQt5.QtWidgets import QSystemTrayIcon
            if not QSystemTrayIcon.isSystemTrayAvailable():
                logger.warning("System tray not available, notifications disabled")
                return

            self.tray_icon = CollaborationTrayIcon()

            # Connect tray icon signals
            self.tray_icon.notification_clicked.connect(self._handle_notification_clicked)
            self.tray_icon.user_action_requested.connect(self._handle_user_action)
            self.tray_icon.bug_report_requested.connect(self._show_bug_report_dialog)

            self.features['collaboration_notifications'] = True
            self.feature_status_changed.emit('collaboration_notifications', True)

            logger.info("Collaboration notifications initialized")

        except Exception as e:
            logger.error(f"Error initializing collaboration notifications: {e}")
            self.features['collaboration_notifications'] = False

    def _initialize_bug_reporting(self):
        """Initialize bug reporting system"""
        try:
            self.bug_report_manager = get_bug_report_manager()

            self.features['bug_reporting'] = True
            self.feature_status_changed.emit('bug_reporting', True)

            logger.info("Bug reporting system initialized")

        except Exception as e:
            logger.error(f"Error initializing bug reporting: {e}")
            self.features['bug_reporting'] = False

    # Workflow Management Methods
    def create_workflow_version(self, workflow_id: str, workflow_data: Dict[str, Any]) -> tuple:
        """Create a new workflow version with conflict detection"""
        if not self.workflow_manager:
            raise RuntimeError("Workflow management not available")

        return self.workflow_manager.create_workflow_version(workflow_id, workflow_data)

    def resolve_workflow_conflict(self, workflow_id: str, resolution: str,
                                 selected_version: Optional[int] = None) -> bool:
        """Resolve a workflow version conflict"""
        if not self.workflow_manager:
            return False

        # Convert string to enum
        resolution_enum = {
            'keep_local': ConflictResolution.KEEP_LOCAL,
            'keep_remote': ConflictResolution.KEEP_REMOTE,
            'auto_merge': ConflictResolution.AUTO_MERGE,
            'manual': ConflictResolution.MANUAL_RESOLVE,
            'prompt': ConflictResolution.PROMPT_USER
        }.get(resolution, ConflictResolution.PROMPT_USER)

        return self.workflow_manager.resolve_conflict(workflow_id, resolution_enum, selected_version)

    def get_active_users(self) -> List[str]:
        """Get list of currently active users"""
        if not self.workflow_manager:
            return [self.user_id]

        return self.workflow_manager.get_active_users()

    # Notification Methods
    def send_notification(self, notification_type: str, title: str, message: str,
                         **kwargs) -> bool:
        """Send a collaboration notification"""
        if not self.tray_icon:
            logger.warning("Notifications not available")
            return False

        try:
            # Map string types to enum
            type_map = {
                'user_joined': NotificationType.USER_JOINED,
                'user_left': NotificationType.USER_LEFT,
                'version_conflict': NotificationType.VERSION_CONFLICT,
                'concurrent_edit': NotificationType.CONCURRENT_EDIT,
                'export_complete': NotificationType.EXPORT_COMPLETE,
                'system_message': NotificationType.SYSTEM_MESSAGE,
                'bug_report': NotificationType.BUG_REPORT,
            }

            notification_type_enum = type_map.get(notification_type, NotificationType.SYSTEM_MESSAGE)

            notification = CollaborationNotification(
                id=f"{notification_type}_{datetime.utcnow().timestamp()}",
                type=notification_type_enum,
                title=title,
                message=message,
                timestamp=datetime.utcnow(),
                project_name=self.project_name,
                user_id=kwargs.get('user_id'),
                workflow_id=kwargs.get('workflow_id'),
                data=kwargs.get('data'),
                priority=kwargs.get('priority', 'normal')
            )

            self.tray_icon.add_notification(notification)
            return True

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False

    def update_collaboration_status(self, active: bool, user_count: int = 0):
        """Update collaboration status in tray icon"""
        if self.tray_icon:
            self.tray_icon.set_collaboration_status(active, user_count)

    # Bug Reporting Methods
    def submit_bug_report(self, title: str, description: str, category: str = "General",
                         priority: str = "Medium", include_logs: bool = True) -> str:
        """Submit a bug report"""
        if not self.bug_report_manager:
            raise RuntimeError("Bug reporting not available")

        report_data = {
            'title': title,
            'description': description,
            'category': category,
            'priority': priority,
            'user_id': self.user_id,
            'project_name': self.project_name
        }

        report_id = self.bug_report_manager.create_bug_report(report_data, include_logs)

        # Send notification about bug report
        self.send_notification(
            'bug_report',
            'Bug Report Submitted',
            f'Bug report "{title}" has been submitted with ID: {report_id}',
            data={'report_id': report_id}
        )

        return report_id

    def report_exception_automatically(self, exception: Exception, context: str = "") -> str:
        """Automatically report an exception"""
        if not self.bug_report_manager:
            logger.error(f"Cannot report exception - bug reporting not available: {exception}")
            return ""

        try:
            report_id = report_exception(exception, context)

            # Send notification
            self.send_notification(
                'bug_report',
                'Automatic Bug Report',
                f'An exception was automatically reported: {type(exception).__name__}',
                priority='high',
                data={'report_id': report_id, 'automatic': True}
            )

            return report_id

        except Exception as e:
            logger.error(f"Error reporting exception automatically: {e}")
            return ""

    # Signal Handlers
    def _handle_version_conflict(self, workflow_id: str, conflict_data: dict):
        """Handle version conflict detection"""
        try:
            conflict_info = conflict_data.get('conflict_info')

            # Send notification
            self.send_notification(
                'version_conflict',
                'Version Conflict Detected',
                f'Version conflict detected in workflow: {workflow_id}',
                workflow_id=workflow_id,
                priority='high',
                data=conflict_data
            )

            # Emit signal for UI handling
            self.user_action_required.emit('resolve_conflict', {
                'workflow_id': workflow_id,
                'conflict_info': conflict_info
            })

        except Exception as e:
            logger.error(f"Error handling version conflict: {e}")

    def _handle_conflict_resolved(self, workflow_id: str, resolution: str):
        """Handle version conflict resolution"""
        self.send_notification(
            'system_message',
            'Conflict Resolved',
            f'Version conflict in {workflow_id} resolved using {resolution}',
            workflow_id=workflow_id
        )

    def _handle_user_joined(self, project_name: str, user_id: str):
        """Handle user joining project"""
        self.send_notification(
            'user_joined',
            'User Joined',
            f'{user_id} joined the project',
            user_id=user_id
        )

        # Update collaboration status
        active_users = self.get_active_users()
        self.update_collaboration_status(len(active_users) > 1, len(active_users))

    def _handle_user_left(self, project_name: str, user_id: str):
        """Handle user leaving project"""
        self.send_notification(
            'user_left',
            'User Left',
            f'{user_id} left the project',
            user_id=user_id
        )

        # Update collaboration status
        active_users = self.get_active_users()
        self.update_collaboration_status(len(active_users) > 1, len(active_users))

    def _handle_concurrent_edit(self, workflow_id: str, active_users: List[str]):
        """Handle concurrent edit detection"""
        if len(active_users) > 1:
            other_users = [u for u in active_users if u != self.user_id]
            self.send_notification(
                'concurrent_edit',
                'Concurrent Edit Detected',
                f'Multiple users editing {workflow_id}: {", ".join(other_users)}',
                workflow_id=workflow_id,
                priority='medium',
                data={'active_users': active_users}
            )

    def _handle_notification_clicked(self, notification_id: str):
        """Handle notification click"""
        # Mark notification as read
        if self.tray_icon:
            self.tray_icon.mark_notification_read(notification_id)

    def _handle_user_action(self, action_type: str, data: str):
        """Handle user action from tray icon"""
        if action_type == "exit":
            QApplication.quit()

    def _show_bug_report_dialog(self):
        """Show bug report dialog"""
        try:
            dialog = BugReportDialog()
            dialog.bug_report_submitted.connect(self._handle_bug_report_submission)
            dialog.exec_()

        except Exception as e:
            logger.error(f"Error showing bug report dialog: {e}")

    def _handle_bug_report_submission(self, report_data: dict):
        """Handle bug report submission from dialog"""
        try:
            report_id = self.submit_bug_report(
                title=report_data['title'],
                description=report_data['description'],
                category=report_data.get('category', 'General'),
                priority=report_data.get('priority', 'Medium'),
                include_logs=report_data.get('include_logs', True)
            )

            logger.info(f"Bug report submitted via dialog: {report_id}")

        except Exception as e:
            logger.error(f"Error handling bug report submission: {e}")

    # Cleanup and Status Methods
    def get_feature_status(self) -> Dict[str, bool]:
        """Get status of all features"""
        return self.features.copy()

    def is_enabled(self) -> bool:
        """Check if collaboration manager is enabled"""
        return self.enabled

    def cleanup(self):
        """Clean up resources"""
        try:
            if self.workflow_manager:
                self.workflow_manager.cleanup()

            if self.tray_icon:
                self.tray_icon.hide()

            logger.info("Collaboration manager cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def __del__(self):
        """Destructor"""
        self.cleanup()

# Global collaboration manager instance
_collaboration_manager = None

def get_collaboration_manager(project_name: str = "default",
                            user_id: str = "local_user") -> CollaborationManager:
    """Get the global collaboration manager instance"""
    global _collaboration_manager
    if _collaboration_manager is None:
        _collaboration_manager = CollaborationManager(project_name, user_id)
    return _collaboration_manager

def initialize_collaboration_features(project_name: str = "default",
                                    user_id: str = "local_user") -> bool:
    """
    Initialize collaboration features for the application

    Args:
        project_name: Name of the current project
        user_id: Identifier for current user

    Returns:
        True if initialization successful, False otherwise
    """
    try:
        manager = get_collaboration_manager(project_name, user_id)
        return manager.is_enabled()

    except Exception as e:
        logger.error(f"Error initializing collaboration features: {e}")
        return False

# Convenience functions for common operations
def create_workflow_version(workflow_id: str, workflow_data: Dict[str, Any]) -> tuple:
    """Create a workflow version with conflict detection"""
    manager = get_collaboration_manager()
    return manager.create_workflow_version(workflow_id, workflow_data)

def send_notification(notification_type: str, title: str, message: str, **kwargs) -> bool:
    """Send a collaboration notification"""
    manager = get_collaboration_manager()
    return manager.send_notification(notification_type, title, message, **kwargs)

def report_bug(title: str, description: str, **kwargs) -> str:
    """Submit a bug report"""
    manager = get_collaboration_manager()
    return manager.submit_bug_report(title, description, **kwargs)

def report_exception(exception: Exception, context: str = "") -> str:
    """Report an exception automatically"""
    manager = get_collaboration_manager()
    return manager.report_exception_automatically(exception, context)

def create_collaborative_manager() -> CollaborationManager:
    """Create and return a collaborative manager instance."""
    return CollaborationManager()

class CollaborationSession:
    """Represents a collaboration session."""

    def __init__(self, session_id: str, project_name: str):
        self.session_id = session_id
        self.project_name = project_name
        self.members = []
        self.created_at = datetime.now()

class TeamMember:
    """Represents a team member."""

    def __init__(self, user_id: str, name: str, role: str = "writer"):
        self.user_id = user_id
        self.name = name
        self.role = role
        self.joined_at = datetime.now()

class CollaborativeIntegration:
    """Integration layer for collaborative features."""

    def __init__(self, collaboration_manager):
        self.collaboration_manager = collaboration_manager

# Import the full CollaborativeManager from system module
try:
    from .system import CollaborativeManager
except ImportError:
    # Create an alias if import fails
    CollaborativeManager = CollaborationManager
