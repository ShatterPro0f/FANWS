"""
Collaboration features for FANWS
Includes real-time notifications, version conflict handling, and bug reporting
"""

from .features import CollaborationManager, get_collaboration_manager
from .bug_reporting import BugReportManager, get_bug_report_manager

__all__ = [
    'CollaborationManager',
    'get_collaboration_manager',
    'BugReportManager',
    'get_bug_report_manager'
]
