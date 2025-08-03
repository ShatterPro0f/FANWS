"""
Workflow Manager with Version Conflict Handling
Implements timestamp-based version conflict detection and resolution
"""

import os
import json
import logging
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

try:
    from ..plugins.plugin_workflow_integration import get_database_manager
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

logger = logging.getLogger(__name__)

class ConflictResolution(Enum):
    """Version conflict resolution strategies"""
    PROMPT_USER = "prompt"
    AUTO_MERGE = "auto_merge"
    KEEP_LOCAL = "keep_local"
    KEEP_REMOTE = "keep_remote"
    MANUAL_RESOLVE = "manual"

@dataclass
class VersionInfo:
    """Information about a workflow version"""
    version_number: int
    created_at: datetime
    modified_at: datetime
    created_by: str
    checksum: str
    is_active: bool = True
    conflict_resolved: bool = False
    resolution_strategy: Optional[str] = None
    workflow_data: Optional[Dict[str, Any]] = None

@dataclass
class ConflictInfo:
    """Information about a version conflict"""
    conflicting_versions: List[VersionInfo]
    current_version: VersionInfo
    conflict_type: str  # 'timestamp', 'content', 'user'
    severity: str  # 'low', 'medium', 'high'
    auto_resolvable: bool = False
    suggested_resolution: ConflictResolution = ConflictResolution.PROMPT_USER

class WorkflowManager(QObject):
    """
    Manages workflow versions with conflict detection and resolution
    """

    # Signals for version conflict handling
    version_conflict_detected = pyqtSignal(str, dict)  # workflow_id, conflict_info
    version_conflict_resolved = pyqtSignal(str, str)   # workflow_id, resolution
    version_created = pyqtSignal(str, int)             # workflow_id, version_number
    version_updated = pyqtSignal(str, int)             # workflow_id, version_number

    # Collaboration signals
    user_joined = pyqtSignal(str, str)                 # project_name, user_id
    user_left = pyqtSignal(str, str)                   # project_name, user_id
    concurrent_edit_detected = pyqtSignal(str, list)   # workflow_id, active_users

    def __init__(self, project_name: str = "default", user_id: str = "local_user"):
        """
        Initialize workflow manager

        Args:
            project_name: Name of the current project
            user_id: Identifier for current user
        """
        super().__init__()
        self.project_name = project_name
        self.user_id = user_id
        self._lock = threading.RLock()

        # Initialize database if available
        self.db_manager = None
        if DATABASE_AVAILABLE:
            try:
                self.db_manager = get_database_manager()
                logger.info("Database manager initialized for workflow versioning")
            except Exception as e:
                logger.warning(f"Database not available, using file-based versioning: {e}")

        # Fallback to file-based storage
        self.workflow_dir = os.path.join("projects", project_name, ".workflow_versions")
        os.makedirs(self.workflow_dir, exist_ok=True)

        # In-memory version cache
        self.version_cache: Dict[str, List[VersionInfo]] = {}
        self.active_workflows: Dict[str, VersionInfo] = {}

        # Conflict detection settings
        self.conflict_detection_enabled = True
        self.auto_resolve_conflicts = False
        self.conflict_check_interval = 30  # seconds

        # Setup periodic conflict checking
        self.conflict_timer = QTimer()
        self.conflict_timer.timeout.connect(self._check_for_conflicts)
        self.conflict_timer.start(self.conflict_check_interval * 1000)

        # Track active users
        self._register_user()

        logger.info(f"Workflow manager initialized for project: {project_name}, user: {user_id}")

    def create_workflow_version(self, workflow_id: str, workflow_data: Dict[str, Any],
                               force: bool = False) -> Tuple[int, Optional[ConflictInfo]]:
        """
        Create a new workflow version with conflict detection

        Args:
            workflow_id: Unique identifier for the workflow
            workflow_data: Workflow configuration and state
            force: Skip conflict detection if True

        Returns:
            Tuple of (version_number, conflict_info)
        """
        with self._lock:
            try:
                # Calculate checksum for content-based conflict detection
                checksum = self._calculate_checksum(workflow_data)

                # Check for conflicts unless forced
                conflict_info = None
                if not force and self.conflict_detection_enabled:
                    conflict_info = self._detect_conflicts(workflow_id, checksum, workflow_data)

                    if conflict_info and not conflict_info.auto_resolvable:
                        # Return conflict for user resolution
                        self.version_conflict_detected.emit(workflow_id, {
                            'conflict_info': conflict_info,
                            'workflow_data': workflow_data
                        })
                        return -1, conflict_info

                # Create version
                if self.db_manager:
                    version_number = self.db_manager.create_workflow_version(
                        workflow_id, self.project_name, workflow_data, self.user_id
                    )
                else:
                    version_number = self._create_file_version(workflow_id, workflow_data)

                # Update cache
                version_info = VersionInfo(
                    version_number=version_number,
                    created_at=datetime.utcnow(),
                    modified_at=datetime.utcnow(),
                    created_by=self.user_id,
                    checksum=checksum,
                    workflow_data=workflow_data
                )

                if workflow_id not in self.version_cache:
                    self.version_cache[workflow_id] = []
                self.version_cache[workflow_id].insert(0, version_info)
                self.active_workflows[workflow_id] = version_info

                # Auto-resolve if possible
                if conflict_info and conflict_info.auto_resolvable:
                    self._auto_resolve_conflict(workflow_id, conflict_info)

                self.version_created.emit(workflow_id, version_number)
                logger.info(f"Created workflow version {version_number} for {workflow_id}")

                return version_number, conflict_info

            except Exception as e:
                logger.error(f"Error creating workflow version: {e}")
                raise

    def update_workflow_version(self, workflow_id: str, version_number: int,
                               workflow_data: Dict[str, Any]) -> bool:
        """Update an existing workflow version"""
        with self._lock:
            try:
                if self.db_manager:
                    # Update in database
                    return self._update_db_version(workflow_id, version_number, workflow_data)
                else:
                    # Update file-based version
                    return self._update_file_version(workflow_id, version_number, workflow_data)

            except Exception as e:
                logger.error(f"Error updating workflow version: {e}")
                return False

    def get_workflow_versions(self, workflow_id: str) -> List[VersionInfo]:
        """Get all versions of a workflow"""
        with self._lock:
            # Check cache first
            if workflow_id in self.version_cache:
                return self.version_cache[workflow_id].copy()

            # Load from storage
            if self.db_manager:
                versions_data = self.db_manager.get_workflow_versions(workflow_id, self.project_name)
                versions = [self._dict_to_version_info(v) for v in versions_data]
            else:
                versions = self._load_file_versions(workflow_id)

            # Update cache
            self.version_cache[workflow_id] = versions
            return versions.copy()

    def resolve_conflict(self, workflow_id: str, resolution: ConflictResolution,
                        selected_version: Optional[int] = None) -> bool:
        """
        Resolve a version conflict with specified strategy

        Args:
            workflow_id: Workflow identifier
            resolution: Resolution strategy
            selected_version: Version to keep (for manual resolution)
        """
        with self._lock:
            try:
                if resolution == ConflictResolution.KEEP_LOCAL:
                    # Keep current local version, mark others as resolved
                    current_version = self.active_workflows.get(workflow_id)
                    if current_version:
                        result = self._mark_conflict_resolved(workflow_id,
                                                            current_version.version_number,
                                                            resolution.value)
                elif resolution == ConflictResolution.KEEP_REMOTE:
                    # Load and activate remote version
                    result = self._activate_remote_version(workflow_id)
                elif resolution == ConflictResolution.AUTO_MERGE:
                    # Attempt automatic merge
                    result = self._attempt_auto_merge(workflow_id)
                elif resolution == ConflictResolution.MANUAL_RESOLVE and selected_version:
                    # Use manually selected version
                    result = self._activate_version(workflow_id, selected_version)
                else:
                    logger.error(f"Invalid resolution strategy: {resolution}")
                    return False

                if result:
                    self.version_conflict_resolved.emit(workflow_id, resolution.value)
                    logger.info(f"Conflict resolved for {workflow_id} using {resolution.value}")

                return result

            except Exception as e:
                logger.error(f"Error resolving conflict: {e}")
                return False

    def _detect_conflicts(self, workflow_id: str, current_checksum: str,
                         workflow_data: Dict[str, Any]) -> Optional[ConflictInfo]:
        """Detect version conflicts using timestamps and content comparison"""
        try:
            if self.db_manager:
                conflicts = self.db_manager.detect_version_conflicts(
                    workflow_id, self.project_name, current_checksum
                )
            else:
                conflicts = self._detect_file_conflicts(workflow_id, current_checksum)

            if not conflicts:
                return None

            # Analyze conflict severity and auto-resolution possibilities
            conflicting_versions = []
            for conflict in conflicts:
                version_info = VersionInfo(
                    version_number=conflict['version_number'],
                    created_at=datetime.fromisoformat(conflict['modified_at']),
                    modified_at=datetime.fromisoformat(conflict['modified_at']),
                    created_by=conflict['created_by'],
                    checksum=conflict['checksum']
                )
                conflicting_versions.append(version_info)

            # Determine conflict type and severity
            conflict_type = self._classify_conflict(conflicting_versions, workflow_data)
            severity = self._assess_conflict_severity(conflicting_versions)
            auto_resolvable = self._can_auto_resolve(conflicting_versions, workflow_data)

            current_version = VersionInfo(
                version_number=0,  # Temporary
                created_at=datetime.utcnow(),
                modified_at=datetime.utcnow(),
                created_by=self.user_id,
                checksum=current_checksum,
                workflow_data=workflow_data
            )

            return ConflictInfo(
                conflicting_versions=conflicting_versions,
                current_version=current_version,
                conflict_type=conflict_type,
                severity=severity,
                auto_resolvable=auto_resolvable,
                suggested_resolution=self._suggest_resolution(conflicting_versions, workflow_data)
            )

        except Exception as e:
            logger.error(f"Error detecting conflicts: {e}")
            return None

    def _classify_conflict(self, conflicting_versions: List[VersionInfo],
                          workflow_data: Dict[str, Any]) -> str:
        """Classify the type of conflict"""
        # Check if it's a timestamp-based conflict
        recent_modifications = [v for v in conflicting_versions
                              if (datetime.utcnow() - v.modified_at).total_seconds() < 300]

        if recent_modifications:
            if len(set(v.created_by for v in recent_modifications)) > 1:
                return "concurrent_user"
            else:
                return "timestamp"

        # Check for content-based conflicts
        unique_checksums = set(v.checksum for v in conflicting_versions)
        if len(unique_checksums) > 1:
            return "content"

        return "unknown"

    def _assess_conflict_severity(self, conflicting_versions: List[VersionInfo]) -> str:
        """Assess the severity of conflicts"""
        # High severity: Multiple users editing recently
        recent_users = set(v.created_by for v in conflicting_versions
                          if (datetime.utcnow() - v.modified_at).total_seconds() < 600)

        if len(recent_users) > 2:
            return "high"
        elif len(recent_users) > 1:
            return "medium"
        else:
            return "low"

    def _can_auto_resolve(self, conflicting_versions: List[VersionInfo],
                         workflow_data: Dict[str, Any]) -> bool:
        """Determine if conflict can be automatically resolved"""
        # Auto-resolve if only timestamp differs and content is similar
        if len(conflicting_versions) == 1:
            # Simple timestamp conflict with same user
            if conflicting_versions[0].created_by == self.user_id:
                return True

        return False

    def _suggest_resolution(self, conflicting_versions: List[VersionInfo],
                           workflow_data: Dict[str, Any]) -> ConflictResolution:
        """Suggest the best resolution strategy"""
        if self._can_auto_resolve(conflicting_versions, workflow_data):
            return ConflictResolution.AUTO_MERGE

        # If only one other user, suggest keeping local
        other_users = set(v.created_by for v in conflicting_versions if v.created_by != self.user_id)
        if len(other_users) == 1:
            return ConflictResolution.KEEP_LOCAL

        # Default to prompting user
        return ConflictResolution.PROMPT_USER

    def _auto_resolve_conflict(self, workflow_id: str, conflict_info: ConflictInfo) -> bool:
        """Automatically resolve simple conflicts"""
        try:
            if conflict_info.suggested_resolution == ConflictResolution.AUTO_MERGE:
                # For auto-merge, just mark as resolved and keep current version
                current_version = self.active_workflows.get(workflow_id)
                if current_version:
                    return self._mark_conflict_resolved(workflow_id,
                                                      current_version.version_number,
                                                      "auto_merge")

            return False

        except Exception as e:
            logger.error(f"Error auto-resolving conflict: {e}")
            return False

    def _calculate_checksum(self, workflow_data: Dict[str, Any]) -> str:
        """Calculate SHA256 checksum of workflow data"""
        try:
            data_str = json.dumps(workflow_data, sort_keys=True, default=str)
            return hashlib.sha256(data_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            return ""

    def _register_user(self):
        """Register current user as active"""
        try:
            if self.db_manager:
                self.db_manager.add_active_user(self.project_name, self.user_id)
                self.user_joined.emit(self.project_name, self.user_id)

            logger.info(f"Registered user {self.user_id} for project {self.project_name}")

        except Exception as e:
            logger.error(f"Error registering user: {e}")

    def _check_for_conflicts(self):
        """Periodic check for conflicts in active workflows"""
        try:
            for workflow_id in self.active_workflows.keys():
                # Check for new concurrent edits
                if self.db_manager:
                    active_users = self.db_manager.get_active_users(self.project_name)
                    if len(active_users) > 1:
                        self.concurrent_edit_detected.emit(workflow_id, active_users)

        except Exception as e:
            logger.error(f"Error checking for conflicts: {e}")

    # File-based fallback methods
    def _create_file_version(self, workflow_id: str, workflow_data: Dict[str, Any]) -> int:
        """Create file-based version (fallback)"""
        version_file = os.path.join(self.workflow_dir, f"{workflow_id}_versions.json")

        try:
            # Load existing versions
            versions = []
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    versions = json.load(f)

            # Create new version
            version_number = max([v.get('version_number', 0) for v in versions], default=0) + 1

            new_version = {
                'version_number': version_number,
                'created_at': datetime.utcnow().isoformat(),
                'modified_at': datetime.utcnow().isoformat(),
                'created_by': self.user_id,
                'checksum': self._calculate_checksum(workflow_data),
                'workflow_data': workflow_data,
                'is_active': True,
                'conflict_resolved': False
            }

            versions.insert(0, new_version)

            # Save updated versions
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(versions, f, indent=2, default=str)

            return version_number

        except Exception as e:
            logger.error(f"Error creating file version: {e}")
            raise

    def _load_file_versions(self, workflow_id: str) -> List[VersionInfo]:
        """Load versions from file (fallback)"""
        version_file = os.path.join(self.workflow_dir, f"{workflow_id}_versions.json")

        try:
            if not os.path.exists(version_file):
                return []

            with open(version_file, 'r', encoding='utf-8') as f:
                versions_data = json.load(f)

            return [self._dict_to_version_info(v) for v in versions_data]

        except Exception as e:
            logger.error(f"Error loading file versions: {e}")
            return []

    def _dict_to_version_info(self, version_dict: Dict[str, Any]) -> VersionInfo:
        """Convert dictionary to VersionInfo"""
        return VersionInfo(
            version_number=version_dict['version_number'],
            created_at=datetime.fromisoformat(version_dict['created_at']),
            modified_at=datetime.fromisoformat(version_dict['modified_at']),
            created_by=version_dict['created_by'],
            checksum=version_dict['checksum'],
            is_active=version_dict.get('is_active', True),
            conflict_resolved=version_dict.get('conflict_resolved', False),
            resolution_strategy=version_dict.get('resolution_strategy'),
            workflow_data=version_dict.get('workflow_data')
        )

    def _mark_conflict_resolved(self, workflow_id: str, version_number: int,
                               resolution: str) -> bool:
        """Mark a conflict as resolved"""
        try:
            if self.db_manager:
                return self.db_manager.resolve_version_conflict(
                    workflow_id, self.project_name, version_number, resolution
                )
            else:
                # File-based resolution marking
                return self._mark_file_conflict_resolved(workflow_id, version_number, resolution)

        except Exception as e:
            logger.error(f"Error marking conflict resolved: {e}")
            return False

    def get_active_users(self) -> List[str]:
        """Get list of currently active users"""
        try:
            if self.db_manager:
                return self.db_manager.get_active_users(self.project_name)
            else:
                return [self.user_id]  # Fallback to just current user

        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return [self.user_id]

    def cleanup(self):
        """Clean up resources"""
        try:
            # Remove user from active list
            if self.db_manager:
                self.db_manager.remove_active_user(self.project_name, self.user_id)
                self.user_left.emit(self.project_name, self.user_id)

            # Stop conflict checking
            if self.conflict_timer:
                self.conflict_timer.stop()

            logger.info(f"Workflow manager cleanup completed for {self.user_id}")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def _mark_file_conflict_resolved(self, workflow_id: str, version_number: int,
                                    resolution: str) -> bool:
        """Mark a conflict as resolved in file-based storage"""
        version_file = os.path.join(self.workflow_dir, f"{workflow_id}_versions.json")

        try:
            if not os.path.exists(version_file):
                return False

            with open(version_file, 'r', encoding='utf-8') as f:
                versions = json.load(f)

            # Update the specified version
            for version in versions:
                if version.get('version_number') == version_number:
                    version['conflict_resolved'] = True
                    version['resolution_strategy'] = resolution
                    break

            # Save updated versions
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(versions, f, indent=2, default=str)

            return True

        except Exception as e:
            logger.error(f"Error marking file conflict resolved: {e}")
            return False

    def _detect_file_conflicts(self, workflow_id: str, current_checksum: str) -> List[Dict[str, Any]]:
        """Detect conflicts in file-based storage"""
        try:
            version_file = os.path.join(self.workflow_dir, f"{workflow_id}_versions.json")

            if not os.path.exists(version_file):
                return []

            with open(version_file, 'r', encoding='utf-8') as f:
                versions = json.load(f)

            conflicts = []
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)

            for version in versions:
                try:
                    version_time = datetime.fromisoformat(version['modified_at'])

                    # Check for recent modifications by other users
                    if (version_time > cutoff_time and
                        version.get('created_by') != self.user_id and
                        version.get('checksum') != current_checksum):

                        conflicts.append({
                            'version_number': version['version_number'],
                            'modified_at': version['modified_at'],
                            'created_by': version['created_by'],
                            'checksum': version['checksum']
                        })

                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid version data: {e}")
                    continue

            return conflicts

        except Exception as e:
            logger.error(f"Error detecting file conflicts: {e}")
            return []

    def _update_file_version(self, workflow_id: str, version_number: int,
                           workflow_data: Dict[str, Any]) -> bool:
        """Update file-based version"""
        version_file = os.path.join(self.workflow_dir, f"{workflow_id}_versions.json")

        try:
            if not os.path.exists(version_file):
                return False

            with open(version_file, 'r', encoding='utf-8') as f:
                versions = json.load(f)

            # Update the specified version
            for version in versions:
                if version.get('version_number') == version_number:
                    version['workflow_data'] = workflow_data
                    version['modified_at'] = datetime.utcnow().isoformat()
                    version['checksum'] = self._calculate_checksum(workflow_data)

                    # Save updated versions
                    with open(version_file, 'w', encoding='utf-8') as f:
                        json.dump(versions, f, indent=2, default=str)

                    self.version_updated.emit(workflow_id, version_number)
                    return True

            return False

        except Exception as e:
            logger.error(f"Error updating file version: {e}")
            return False

    def _update_db_version(self, workflow_id: str, version_number: int,
                          workflow_data: Dict[str, Any]) -> bool:
        """Update database version"""
        try:
            return self.db_manager.update_workflow_version(
                workflow_id, self.project_name, version_number, workflow_data
            )
        except Exception as e:
            logger.error(f"Error updating database version: {e}")
            return False

    def _activate_version(self, workflow_id: str, version_number: int) -> bool:
        """Activate a specific version"""
        try:
            versions = self.get_workflow_versions(workflow_id)

            for version in versions:
                if version.version_number == version_number:
                    self.active_workflows[workflow_id] = version
                    return True

            return False

        except Exception as e:
            logger.error(f"Error activating version: {e}")
            return False

    def _activate_remote_version(self, workflow_id: str) -> bool:
        """Activate the most recent remote version"""
        try:
            versions = self.get_workflow_versions(workflow_id)

            # Find most recent version by someone else
            remote_versions = [v for v in versions if v.created_by != self.user_id]

            if remote_versions:
                latest_remote = max(remote_versions, key=lambda v: v.modified_at)
                self.active_workflows[workflow_id] = latest_remote
                return True

            return False

        except Exception as e:
            logger.error(f"Error activating remote version: {e}")
            return False

    def _attempt_auto_merge(self, workflow_id: str) -> bool:
        """Attempt automatic merge of conflicting versions"""
        try:
            # For now, just use the most recent version
            # In a more sophisticated implementation, this would perform
            # actual content merging
            return self._activate_remote_version(workflow_id)

        except Exception as e:
            logger.error(f"Error attempting auto-merge: {e}")
            return False
