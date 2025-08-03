"""
Role-Based Permissions System
Enhanced permissions enforcement for collaborative features
Created: July 31, 2025
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Permission(Enum):
    """Granular permissions for different actions."""
    # Document permissions
    READ_DOCUMENT = "read_document"
    EDIT_DOCUMENT = "edit_document"
    DELETE_DOCUMENT = "delete_document"
    CREATE_DOCUMENT = "create_document"
    SHARE_DOCUMENT = "share_document"

    # Project permissions
    VIEW_PROJECT = "view_project"
    EDIT_PROJECT_SETTINGS = "edit_project_settings"
    MANAGE_PROJECT_MEMBERS = "manage_project_members"
    DELETE_PROJECT = "delete_project"

    # Collaboration permissions
    ADD_COMMENTS = "add_comments"
    RESOLVE_COMMENTS = "resolve_comments"
    REVIEW_CHANGES = "review_changes"
    APPROVE_CHANGES = "approve_changes"

    # Version control permissions
    CREATE_VERSION = "create_version"
    RESTORE_VERSION = "restore_version"
    MANAGE_BRANCHES = "manage_branches"
    MERGE_CHANGES = "merge_changes"

    # Administrative permissions
    INVITE_USERS = "invite_users"
    REMOVE_USERS = "remove_users"
    CHANGE_USER_ROLES = "change_user_roles"
    MANAGE_PERMISSIONS = "manage_permissions"

    # Export/Import permissions
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"

    # Analytics permissions
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_ANALYTICS = "export_analytics"

class UserRole(Enum):
    """Enhanced user roles with clear hierarchy."""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    COMMENTER = "commenter"
    VIEWER = "viewer"
    GUEST = "guest"

@dataclass
class PermissionRule:
    """Represents a permission rule with conditions."""
    permission: Permission
    allowed: bool
    conditions: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class RoleDefinition:
    """Defines a role with its permissions and metadata."""
    role: UserRole
    name: str
    description: str
    permissions: Set[Permission]
    inherits_from: Optional[UserRole] = None
    is_system_role: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class PermissionContext:
    """Context for permission evaluation."""
    user_id: str
    resource_type: str  # 'document', 'project', 'comment', etc.
    resource_id: str
    action: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

class PermissionEvaluator(ABC):
    """Abstract base class for permission evaluators."""

    @abstractmethod
    def evaluate(self, context: PermissionContext, user_permissions: Set[Permission]) -> bool:
        """Evaluate if the permission should be granted."""
        pass

class DocumentOwnershipEvaluator(PermissionEvaluator):
    """Evaluates permissions based on document ownership."""

    def __init__(self, get_document_owner_func: Callable[[str], Optional[str]]):
        self.get_document_owner = get_document_owner_func

    def evaluate(self, context: PermissionContext, user_permissions: Set[Permission]) -> bool:
        """Grant additional permissions to document owners."""
        if context.resource_type == 'document':
            owner_id = self.get_document_owner(context.resource_id)
            if owner_id == context.user_id:
                # Document owners get additional permissions
                return True
        return False

class TimeBasedPermissionEvaluator(PermissionEvaluator):
    """Evaluates permissions based on time constraints."""

    def evaluate(self, context: PermissionContext, user_permissions: Set[Permission]) -> bool:
        """Evaluate time-based permission constraints."""
        time_constraints = context.metadata.get('time_constraints', {})
        if not time_constraints:
            return True  # No time constraints

        current_time = datetime.now()

        # Check valid time range
        start_time = time_constraints.get('start_time')
        end_time = time_constraints.get('end_time')

        if start_time and current_time < datetime.fromisoformat(start_time):
            return False

        if end_time and current_time > datetime.fromisoformat(end_time):
            return False

        return True

class ResourceLockEvaluator(PermissionEvaluator):
    """Evaluates permissions based on resource locks."""

    def __init__(self, get_resource_lock_func: Callable[[str], Optional[str]]):
        self.get_resource_lock = get_resource_lock_func

    def evaluate(self, context: PermissionContext, user_permissions: Set[Permission]) -> bool:
        """Check if resource is locked by another user."""
        if context.action in ['edit', 'delete']:
            lock_owner = self.get_resource_lock(context.resource_id)
            if lock_owner and lock_owner != context.user_id:
                return False
        return True

class RoleBasedPermissionManager:
    """Manages role-based permissions with enhanced features."""

    def __init__(self):
        self.role_definitions: Dict[UserRole, RoleDefinition] = {}
        self.custom_permissions: Dict[str, Set[Permission]] = {}
        self.permission_evaluators: List[PermissionEvaluator] = []
        self.permission_cache: Dict[str, Dict[Permission, bool]] = {}
        self.cache_ttl = timedelta(minutes=5)
        self.audit_log: List[Dict[str, Any]] = []

        self._initialize_default_roles()

    def _initialize_default_roles(self):
        """Initialize default role definitions."""
        # Define permissions for each role
        owner_permissions = {
            Permission.READ_DOCUMENT, Permission.EDIT_DOCUMENT, Permission.DELETE_DOCUMENT,
            Permission.CREATE_DOCUMENT, Permission.SHARE_DOCUMENT,
            Permission.VIEW_PROJECT, Permission.EDIT_PROJECT_SETTINGS, Permission.MANAGE_PROJECT_MEMBERS,
            Permission.DELETE_PROJECT,
            Permission.ADD_COMMENTS, Permission.RESOLVE_COMMENTS, Permission.REVIEW_CHANGES,
            Permission.APPROVE_CHANGES,
            Permission.CREATE_VERSION, Permission.RESTORE_VERSION, Permission.MANAGE_BRANCHES,
            Permission.MERGE_CHANGES,
            Permission.INVITE_USERS, Permission.REMOVE_USERS, Permission.CHANGE_USER_ROLES,
            Permission.MANAGE_PERMISSIONS,
            Permission.EXPORT_DATA, Permission.IMPORT_DATA,
            Permission.VIEW_ANALYTICS, Permission.EXPORT_ANALYTICS
        }

        admin_permissions = owner_permissions - {Permission.DELETE_PROJECT}

        editor_permissions = {
            Permission.READ_DOCUMENT, Permission.EDIT_DOCUMENT, Permission.CREATE_DOCUMENT,
            Permission.SHARE_DOCUMENT,
            Permission.VIEW_PROJECT,
            Permission.ADD_COMMENTS, Permission.RESOLVE_COMMENTS, Permission.REVIEW_CHANGES,
            Permission.CREATE_VERSION, Permission.MANAGE_BRANCHES,
            Permission.EXPORT_DATA, Permission.VIEW_ANALYTICS
        }

        reviewer_permissions = {
            Permission.READ_DOCUMENT,
            Permission.VIEW_PROJECT,
            Permission.ADD_COMMENTS, Permission.RESOLVE_COMMENTS, Permission.REVIEW_CHANGES,
            Permission.APPROVE_CHANGES,
            Permission.EXPORT_DATA, Permission.VIEW_ANALYTICS
        }

        commenter_permissions = {
            Permission.READ_DOCUMENT,
            Permission.VIEW_PROJECT,
            Permission.ADD_COMMENTS,
            Permission.VIEW_ANALYTICS
        }

        viewer_permissions = {
            Permission.READ_DOCUMENT,
            Permission.VIEW_PROJECT,
            Permission.VIEW_ANALYTICS
        }

        guest_permissions = {
            Permission.READ_DOCUMENT,
            Permission.VIEW_PROJECT
        }

        # Create role definitions
        roles = [
            (UserRole.OWNER, "Owner", "Full control over project", owner_permissions),
            (UserRole.ADMIN, "Administrator", "Administrative privileges", admin_permissions),
            (UserRole.EDITOR, "Editor", "Can edit and create content", editor_permissions),
            (UserRole.REVIEWER, "Reviewer", "Can review and approve changes", reviewer_permissions),
            (UserRole.COMMENTER, "Commenter", "Can add comments", commenter_permissions),
            (UserRole.VIEWER, "Viewer", "Read-only access", viewer_permissions),
            (UserRole.GUEST, "Guest", "Limited read access", guest_permissions)
        ]

        for role, name, desc, perms in roles:
            self.role_definitions[role] = RoleDefinition(
                role=role,
                name=name,
                description=desc,
                permissions=perms
            )

    def add_permission_evaluator(self, evaluator: PermissionEvaluator):
        """Add a custom permission evaluator."""
        self.permission_evaluators.append(evaluator)

    def check_permission(self, user_id: str, user_role: UserRole,
                        permission: Permission, context: PermissionContext) -> bool:
        """Check if a user has a specific permission."""
        # Check cache first
        cache_key = f"{user_id}:{permission.value}:{context.resource_id}"
        if cache_key in self.permission_cache:
            cached_result, cached_time = self.permission_cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_result

        # Get user permissions
        user_permissions = self.get_user_permissions(user_id, user_role)

        # Basic permission check
        has_permission = permission in user_permissions

        # Run custom evaluators
        for evaluator in self.permission_evaluators:
            try:
                evaluator_result = evaluator.evaluate(context, user_permissions)
                if evaluator_result is False:
                    has_permission = False
                    break
                elif evaluator_result is True and not has_permission:
                    has_permission = True
            except Exception as e:
                logger.error(f"Error in permission evaluator: {e}")

        # Cache result
        self.permission_cache[cache_key] = (has_permission, datetime.now())

        # Log the permission check
        self._log_permission_check(user_id, permission, context, has_permission)

        return has_permission

    def get_user_permissions(self, user_id: str, user_role: UserRole) -> Set[Permission]:
        """Get all permissions for a user."""
        permissions = set()

        # Add role-based permissions
        if user_role in self.role_definitions:
            permissions.update(self.role_definitions[user_role].permissions)

        # Add custom permissions
        if user_id in self.custom_permissions:
            permissions.update(self.custom_permissions[user_id])

        return permissions

    def grant_custom_permission(self, user_id: str, permission: Permission):
        """Grant a custom permission to a user."""
        if user_id not in self.custom_permissions:
            self.custom_permissions[user_id] = set()
        self.custom_permissions[user_id].add(permission)
        self._clear_user_cache(user_id)

    def revoke_custom_permission(self, user_id: str, permission: Permission):
        """Revoke a custom permission from a user."""
        if user_id in self.custom_permissions:
            self.custom_permissions[user_id].discard(permission)
            if not self.custom_permissions[user_id]:
                del self.custom_permissions[user_id]
        self._clear_user_cache(user_id)

    def create_custom_role(self, role_name: str, description: str,
                          permissions: Set[Permission]) -> str:
        """Create a custom role definition."""
        custom_role = UserRole(role_name.lower())
        self.role_definitions[custom_role] = RoleDefinition(
            role=custom_role,
            name=role_name,
            description=description,
            permissions=permissions,
            is_system_role=False
        )
        return custom_role.value

    def update_role_permissions(self, role: UserRole, permissions: Set[Permission]):
        """Update permissions for a role."""
        if role in self.role_definitions and not self.role_definitions[role].is_system_role:
            self.role_definitions[role].permissions = permissions
            self._clear_all_cache()

    def get_role_hierarchy(self) -> Dict[UserRole, int]:
        """Get role hierarchy levels (higher number = more privileges)."""
        hierarchy = {
            UserRole.GUEST: 1,
            UserRole.VIEWER: 2,
            UserRole.COMMENTER: 3,
            UserRole.REVIEWER: 4,
            UserRole.EDITOR: 5,
            UserRole.ADMIN: 6,
            UserRole.OWNER: 7
        }
        return hierarchy

    def can_modify_user_role(self, modifier_role: UserRole, target_role: UserRole,
                           new_role: UserRole) -> bool:
        """Check if a user can modify another user's role."""
        hierarchy = self.get_role_hierarchy()

        modifier_level = hierarchy.get(modifier_role, 0)
        target_level = hierarchy.get(target_role, 0)
        new_level = hierarchy.get(new_role, 0)

        # Can only modify users with lower hierarchy level
        # Cannot promote users to same or higher level than self
        return modifier_level > target_level and modifier_level > new_level

    def get_available_permissions(self) -> List[Dict[str, Any]]:
        """Get all available permissions with descriptions."""
        permission_descriptions = {
            Permission.READ_DOCUMENT: "View document content",
            Permission.EDIT_DOCUMENT: "Edit document content",
            Permission.DELETE_DOCUMENT: "Delete documents",
            Permission.CREATE_DOCUMENT: "Create new documents",
            Permission.SHARE_DOCUMENT: "Share documents with others",
            Permission.VIEW_PROJECT: "View project details",
            Permission.EDIT_PROJECT_SETTINGS: "Modify project settings",
            Permission.MANAGE_PROJECT_MEMBERS: "Add/remove project members",
            Permission.DELETE_PROJECT: "Delete entire project",
            Permission.ADD_COMMENTS: "Add comments and feedback",
            Permission.RESOLVE_COMMENTS: "Mark comments as resolved",
            Permission.REVIEW_CHANGES: "Review and provide feedback on changes",
            Permission.APPROVE_CHANGES: "Approve or reject changes",
            Permission.CREATE_VERSION: "Create document versions",
            Permission.RESTORE_VERSION: "Restore previous versions",
            Permission.MANAGE_BRANCHES: "Create and manage branches",
            Permission.MERGE_CHANGES: "Merge changes between branches",
            Permission.INVITE_USERS: "Invite new users to project",
            Permission.REMOVE_USERS: "Remove users from project",
            Permission.CHANGE_USER_ROLES: "Modify user roles",
            Permission.MANAGE_PERMISSIONS: "Manage custom permissions",
            Permission.EXPORT_DATA: "Export project data",
            Permission.IMPORT_DATA: "Import external data",
            Permission.VIEW_ANALYTICS: "View project analytics",
            Permission.EXPORT_ANALYTICS: "Export analytics data"
        }

        return [
            {
                'permission': perm.value,
                'name': perm.value.replace('_', ' ').title(),
                'description': permission_descriptions.get(perm, ''),
                'category': self._get_permission_category(perm)
            }
            for perm in Permission
        ]

    def get_role_permissions_matrix(self) -> Dict[str, Dict[str, bool]]:
        """Get a matrix of roles and their permissions."""
        matrix = {}

        for role, definition in self.role_definitions.items():
            matrix[role.value] = {
                perm.value: perm in definition.permissions
                for perm in Permission
            }

        return matrix

    def export_permissions_config(self) -> Dict[str, Any]:
        """Export permissions configuration."""
        return {
            'roles': {
                role.value: {
                    'name': definition.name,
                    'description': definition.description,
                    'permissions': [p.value for p in definition.permissions],
                    'is_system_role': definition.is_system_role
                }
                for role, definition in self.role_definitions.items()
            },
            'custom_permissions': {
                user_id: [p.value for p in perms]
                for user_id, perms in self.custom_permissions.items()
            }
        }

    def import_permissions_config(self, config: Dict[str, Any]):
        """Import permissions configuration."""
        # Import custom roles
        for role_value, role_data in config.get('roles', {}).items():
            if not role_data.get('is_system_role', True):
                try:
                    custom_role = UserRole(role_value)
                    permissions = {Permission(p) for p in role_data.get('permissions', [])}
                    self.role_definitions[custom_role] = RoleDefinition(
                        role=custom_role,
                        name=role_data.get('name', ''),
                        description=role_data.get('description', ''),
                        permissions=permissions,
                        is_system_role=False
                    )
                except Exception as e:
                    logger.error(f"Failed to import custom role {role_value}: {e}")

        # Import custom permissions
        for user_id, perms in config.get('custom_permissions', {}).items():
            try:
                self.custom_permissions[user_id] = {Permission(p) for p in perms}
            except Exception as e:
                logger.error(f"Failed to import custom permissions for {user_id}: {e}")

        self._clear_all_cache()

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent permission audit log entries."""
        return self.audit_log[-limit:]

    def _get_permission_category(self, permission: Permission) -> str:
        """Get the category for a permission."""
        if permission.value.endswith('_document'):
            return 'Document'
        elif permission.value.startswith('view_') or permission.value.startswith('edit_'):
            return 'Project'
        elif 'comment' in permission.value or 'review' in permission.value:
            return 'Collaboration'
        elif 'version' in permission.value or 'branch' in permission.value:
            return 'Version Control'
        elif 'user' in permission.value or 'permission' in permission.value:
            return 'Administration'
        elif 'export' in permission.value or 'import' in permission.value:
            return 'Data Management'
        elif 'analytics' in permission.value:
            return 'Analytics'
        else:
            return 'Other'

    def _log_permission_check(self, user_id: str, permission: Permission,
                            context: PermissionContext, granted: bool):
        """Log a permission check for audit purposes."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'permission': permission.value,
            'resource_type': context.resource_type,
            'resource_id': context.resource_id,
            'action': context.action,
            'granted': granted
        }

        self.audit_log.append(log_entry)

        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

    def _clear_user_cache(self, user_id: str):
        """Clear cache entries for a specific user."""
        keys_to_remove = [key for key in self.permission_cache.keys()
                         if key.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del self.permission_cache[key]

    def _clear_all_cache(self):
        """Clear all permission cache entries."""
        self.permission_cache.clear()

class PermissionDecorator:
    """Decorator for enforcing permissions on methods."""

    def __init__(self, permission_manager: RoleBasedPermissionManager):
        self.permission_manager = permission_manager

    def require_permission(self, permission: Permission, resource_type: str = '',
                          get_resource_id: Optional[Callable] = None):
        """Decorator that requires a specific permission."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Extract user context (this would need to be adapted based on your app structure)
                user_id = kwargs.get('user_id') or getattr(args[0], 'current_user_id', None)
                user_role = kwargs.get('user_role') or getattr(args[0], 'current_user_role', UserRole.GUEST)

                if not user_id:
                    raise PermissionError("User context not available")

                # Get resource ID
                resource_id = ''
                if get_resource_id:
                    resource_id = get_resource_id(*args, **kwargs)
                elif 'resource_id' in kwargs:
                    resource_id = kwargs['resource_id']

                # Create permission context
                context = PermissionContext(
                    user_id=user_id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    action=func.__name__,
                    metadata=kwargs.get('permission_metadata', {})
                )

                # Check permission
                if not self.permission_manager.check_permission(user_id, user_role, permission, context):
                    raise PermissionError(f"Permission denied: {permission.value}")

                return func(*args, **kwargs)
            return wrapper
        return decorator

# Helper functions for common permission patterns
def create_permission_context(user_id: str, resource_type: str, resource_id: str,
                            action: str, **metadata) -> PermissionContext:
    """Helper to create permission context."""
    return PermissionContext(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        metadata=metadata
    )

def check_document_permission(permission_manager: RoleBasedPermissionManager,
                            user_id: str, user_role: UserRole, document_id: str,
                            permission: Permission) -> bool:
    """Helper to check document permissions."""
    context = create_permission_context(
        user_id=user_id,
        resource_type='document',
        resource_id=document_id,
        action=permission.value
    )

    return permission_manager.check_permission(user_id, user_role, permission, context)

def check_project_permission(permission_manager: RoleBasedPermissionManager,
                           user_id: str, user_role: UserRole, project_id: str,
                           permission: Permission) -> bool:
    """Helper to check project permissions."""
    context = create_permission_context(
        user_id=user_id,
        resource_type='project',
        resource_id=project_id,
        action=permission.value
    )

    return permission_manager.check_permission(user_id, user_role, permission, context)
