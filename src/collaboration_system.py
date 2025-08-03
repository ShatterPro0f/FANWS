"""
FANWS Collaboration System
=========================

Comprehensive collaboration system for FANWS with real-time editing,
user management, and notification system.
"""

import sys
import os
import json
import logging
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import statistics

# Constants
OWNER = "owner"
EDITOR = "editor"
REVIEWER = "reviewer"
COMMENTER = "commenter"
VIEWER = "viewer"

# Permission types
READ = "read"
WRITE = "write"
COMMENT = "comment"
SHARE = "share"
ADMIN = "admin"

# Event types
USER_JOINED = "user_joined"
USER_LEFT = "user_left"
DOCUMENT_EDITED = "document_edited"
COMMENT_ADDED = "comment_added"
PERMISSION_CHANGED = "permission_changed"

# Notification types
DOCUMENT_SHARED = "document_shared"
COMMENT_REPLIED = "comment_replied"
PERMISSION_GRANTED = "permission_granted"
EDIT_CONFLICT = "edit_conflict"
REVIEW_REQUEST = "review_request"

class UserRole(Enum):
    """User roles for collaboration system"""
    OWNER = "owner"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    COMMENTER = "commenter"
    VIEWER = "viewer"

@dataclass
class User:
    """Represents a user in the collaboration system."""
    user_id: str
    username: str
    email: str
    role: str = VIEWER
    last_active: datetime = field(default_factory=datetime.now)
    is_online: bool = False
    permissions: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'last_active': self.last_active.isoformat(),
            'is_online': self.is_online,
            'permissions': list(self.permissions)
        }

@dataclass
class Comment:
    """Represents a comment in the collaboration system."""
    comment_id: str
    author_id: str
    content: str
    timestamp: datetime
    parent_id: Optional[str] = None
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'comment_id': self.comment_id,
            'author_id': self.author_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'parent_id': self.parent_id,
            'resolved': self.resolved
        }

@dataclass
class CollaborationEvent:
    """Represents an event in the collaboration system."""
    event_id: str
    event_type: str
    user_id: str
    project_id: str
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data
        }

class CollaborationSystem:
    """Main collaboration system for FANWS."""

    def __init__(self, project_id: str = None):
        self.project_id = project_id
        self.users: Dict[str, User] = {}
        self.comments: Dict[str, Comment] = {}
        self.events: List[CollaborationEvent] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

        # Initialize collaboration data directory
        self.data_dir = Path("collaboration_data")
        self.data_dir.mkdir(exist_ok=True)

        if self.project_id:
            self.load_collaboration_data()

    def add_user(self, user_id: str, username: str, email: str, role: str = VIEWER) -> bool:
        """Add a user to the collaboration system."""
        try:
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                role=role,
                permissions=self._get_role_permissions(role)
            )
            self.users[user_id] = user
            self.save_collaboration_data()
            self.logger.info(f"User {username} added to collaboration system")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add user: {e}")
            return False

    def remove_user(self, user_id: str) -> bool:
        """Remove a user from the collaboration system."""
        try:
            if user_id in self.users:
                username = self.users[user_id].username
                del self.users[user_id]
                self.save_collaboration_data()
                self.logger.info(f"User {username} removed from collaboration system")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove user: {e}")
            return False

    def update_user_role(self, user_id: str, new_role: str) -> bool:
        """Update a user's role."""
        try:
            if user_id in self.users:
                self.users[user_id].role = new_role
                self.users[user_id].permissions = self._get_role_permissions(new_role)
                self.save_collaboration_data()
                self.logger.info(f"User {user_id} role updated to {new_role}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to update user role: {e}")
            return False

    def add_comment(self, author_id: str, content: str, parent_id: str = None) -> str:
        """Add a comment."""
        try:
            comment_id = str(uuid.uuid4())
            comment = Comment(
                comment_id=comment_id,
                author_id=author_id,
                content=content,
                timestamp=datetime.now(),
                parent_id=parent_id
            )
            self.comments[comment_id] = comment
            self.save_collaboration_data()
            self.logger.info(f"Comment added by user {author_id}")
            return comment_id
        except Exception as e:
            self.logger.error(f"Failed to add comment: {e}")
            return ""

    def resolve_comment(self, comment_id: str) -> bool:
        """Mark a comment as resolved."""
        try:
            if comment_id in self.comments:
                self.comments[comment_id].resolved = True
                self.save_collaboration_data()
                self.logger.info(f"Comment {comment_id} resolved")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to resolve comment: {e}")
            return False

    def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get permissions for a user."""
        if user_id in self.users:
            return self.users[user_id].permissions
        return set()

    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has a specific permission."""
        user_permissions = self.get_user_permissions(user_id)
        return permission in user_permissions

    def get_collaboration_stats(self) -> Dict[str, Any]:
        """Get collaboration statistics."""
        try:
            active_users = len([u for u in self.users.values() if u.is_online])
            total_comments = len(self.comments)
            resolved_comments = len([c for c in self.comments.values() if c.resolved])

            return {
                'total_users': len(self.users),
                'active_users': active_users,
                'total_comments': total_comments,
                'resolved_comments': resolved_comments,
                'unresolved_comments': total_comments - resolved_comments,
                'total_events': len(self.events)
            }
        except Exception as e:
            self.logger.error(f"Failed to get collaboration stats: {e}")
            return {}

    def _get_role_permissions(self, role: str) -> Set[str]:
        """Get permissions for a role."""
        role_permissions = {
            OWNER: {READ, WRITE, COMMENT, SHARE, ADMIN},
            EDITOR: {READ, WRITE, COMMENT},
            REVIEWER: {READ, COMMENT},
            COMMENTER: {READ, COMMENT},
            VIEWER: {READ}
        }
        return role_permissions.get(role, {READ})

    def save_collaboration_data(self):
        """Save collaboration data to file."""
        try:
            if not self.project_id:
                return

            data = {
                'users': {uid: user.to_dict() for uid, user in self.users.items()},
                'comments': {cid: comment.to_dict() for cid, comment in self.comments.items()},
                'events': [event.to_dict() for event in self.events],
                'last_saved': datetime.now().isoformat()
            }

            file_path = self.data_dir / f"{self.project_id}_collaboration.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save collaboration data: {e}")

    def load_collaboration_data(self):
        """Load collaboration data from file."""
        try:
            if not self.project_id:
                return

            file_path = self.data_dir / f"{self.project_id}_collaboration.json"
            if not file_path.exists():
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load users
            for user_data in data.get('users', {}).values():
                user = User(
                    user_id=user_data['user_id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    role=user_data['role'],
                    last_active=datetime.fromisoformat(user_data['last_active']),
                    is_online=user_data.get('is_online', False),
                    permissions=set(user_data.get('permissions', []))
                )
                self.users[user.user_id] = user

            # Load comments
            for comment_data in data.get('comments', {}).values():
                comment = Comment(
                    comment_id=comment_data['comment_id'],
                    author_id=comment_data['author_id'],
                    content=comment_data['content'],
                    timestamp=datetime.fromisoformat(comment_data['timestamp']),
                    parent_id=comment_data.get('parent_id'),
                    resolved=comment_data.get('resolved', False)
                )
                self.comments[comment.comment_id] = comment

            # Load events
            for event_data in data.get('events', []):
                event = CollaborationEvent(
                    event_id=event_data['event_id'],
                    event_type=event_data['event_type'],
                    user_id=event_data['user_id'],
                    project_id=event_data['project_id'],
                    timestamp=datetime.fromisoformat(event_data['timestamp']),
                    data=event_data.get('data', {})
                )
                self.events.append(event)

            self.logger.info("Collaboration data loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load collaboration data: {e}")

class CollaborativeManager:
    """High-level manager for collaboration features."""

    def __init__(self):
        self.collaboration_systems: Dict[str, CollaborationSystem] = {}
        self.logger = logging.getLogger(__name__)

    def get_collaboration_system(self, project_id: str) -> CollaborationSystem:
        """Get or create collaboration system for a project."""
        if project_id not in self.collaboration_systems:
            self.collaboration_systems[project_id] = CollaborationSystem(project_id)
        return self.collaboration_systems[project_id]

    def create_project_collaboration(self, project_id: str, owner_id: str, owner_email: str) -> bool:
        """Create collaboration for a new project."""
        try:
            collab_system = self.get_collaboration_system(project_id)
            return collab_system.add_user(owner_id, "Project Owner", owner_email, OWNER)
        except Exception as e:
            self.logger.error(f"Failed to create project collaboration: {e}")
            return False

    def invite_user_to_project(self, project_id: str, user_id: str, username: str,
                             email: str, role: str = VIEWER) -> bool:
        """Invite a user to collaborate on a project."""
        try:
            collab_system = self.get_collaboration_system(project_id)
            return collab_system.add_user(user_id, username, email, role)
        except Exception as e:
            self.logger.error(f"Failed to invite user to project: {e}")
            return False

    def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get collaboration statistics for a project."""
        try:
            if project_id in self.collaboration_systems:
                return self.collaboration_systems[project_id].get_collaboration_stats()
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get project stats: {e}")
            return {}

# Global collaboration manager instance
_global_collaboration_manager = None

def get_collaboration_manager() -> CollaborativeManager:
    """Get the global collaboration manager instance."""
    global _global_collaboration_manager
    if _global_collaboration_manager is None:
        _global_collaboration_manager = CollaborativeManager()
    return _global_collaboration_manager

# For backward compatibility
def create_collaboration_system(project_id: str = None) -> CollaborationSystem:
    """Create a collaboration system instance."""
    return CollaborationSystem(project_id)
