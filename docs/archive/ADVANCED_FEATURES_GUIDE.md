# Advanced Features Integration Guide

## Overview

This guide covers the implementation of advanced features for FANWS including:

1. **Version Conflict Handling** with timestamp-based detection
2. **SQLAlchemy Connection Pooling** for database reliability
3. **QSystemTrayIcon** for real-time collaboration notifications
4. **Bug Reporting System** with comprehensive log collection

## Features Implemented

### 1. Workflow Manager with Version Conflict Handling

**File**: `src/workflow_manager.py`

**Key Features**:
- Timestamp-based version conflict detection
- Multiple conflict resolution strategies (auto-merge, keep local/remote, manual)
- Real-time collaboration tracking
- Background conflict monitoring
- PyQt signals for UI integration

**Usage**:
```python
from src.workflow_manager import WorkflowManager, ConflictResolution

# Initialize workflow manager
manager = WorkflowManager(project_name="my_project", user_id="user123")

# Create workflow version with conflict detection
version_number, conflict_info = manager.create_workflow_version(
    workflow_id="main_workflow",
    workflow_data={"steps": [], "config": {}}
)

# Handle conflicts
if conflict_info:
    resolved = manager.resolve_conflict(
        workflow_id="main_workflow",
        resolution=ConflictResolution.KEEP_LOCAL
    )
```

### 2. SQLAlchemy Database Manager

**File**: `src/database/__init__.py`

**Key Features**:
- Connection pooling for SQLite
- Retry logic with exponential backoff
- Version conflict tracking
- Active user management
- Comprehensive error handling

**Models**:
- `WorkflowVersion`: Version tracking with conflict detection
- `ApiCache`: Cached API responses with TTL
- `ProjectMetadata`: Project-level collaboration data

### 3. Collaboration Notification System

**File**: `src/ui/collaboration_notifications.py`

**Key Features**:
- QSystemTrayIcon with dynamic status indicators
- Rich notification types (user joined/left, conflicts, exports)
- Notification history window
- Configurable notification settings
- Visual priority indicators (blinking for urgent)

**Components**:
- `CollaborationTrayIcon`: Main system tray integration
- `NotificationWindow`: Notification history viewer
- `NotificationWidget`: Individual notification display
- `NotificationSettingsDialog`: User preferences

### 4. Bug Reporting System

**File**: `src/bug_report_system.py`

**Key Features**:
- Comprehensive system information collection
- Automatic log file gathering
- ZIP package creation with attachments
- Exception auto-reporting
- Export functionality for support

**Information Collected**:
- System platform and hardware details
- Python environment and installed packages
- Application logs and error traces
- Git repository information
- User-provided description and context

### 5. Integration Manager

**File**: `src/collaboration_features.py`

**Key Features**:
- Unified interface for all collaboration features
- Automatic feature detection and fallback
- Signal coordination between components
- Convenience functions for common operations
- Resource cleanup management

## Installation and Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `SQLAlchemy>=2.0.0` for database connection pooling

### 2. Initialize Features

```python
from src.collaboration_features import initialize_collaboration_features

# Initialize all collaboration features
success = initialize_collaboration_features(
    project_name="my_project",
    user_id="current_user"
)

if success:
    print("Collaboration features enabled")
else:
    print("Some features unavailable, fallback mode active")
```

### 3. Integration with Existing UI

```python
from src.collaboration_features import get_collaboration_manager

# Get manager instance
manager = get_collaboration_manager()

# Connect to UI signals
manager.user_action_required.connect(self.handle_user_action)
manager.feature_status_changed.connect(self.update_feature_status)

# Send notifications
manager.send_notification(
    'export_complete',
    'Export Finished',
    'Document exported successfully'
)

# Handle bug reports
try:
    # Your application code
    pass
except Exception as e:
    report_id = manager.report_exception_automatically(e, "During export operation")
```

## Feature Configuration

### Database Configuration

The database manager supports both SQLAlchemy pooling and file-based fallback:

```python
# config/app_config.json
{
    "database": {
        "use_sqlalchemy": true,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 3600
    },
    "collaboration": {
        "conflict_detection_enabled": true,
        "auto_resolve_conflicts": false,
        "conflict_check_interval": 30
    }
}
```

### Notification Settings

Users can configure notification behavior:

```python
# Programmatic configuration
tray_icon.notifications_enabled = True
tray_icon.sound_enabled = False
tray_icon.popup_duration = 5000  # milliseconds
```

### Bug Report Settings

```python
# Bug report manager configuration
bug_manager = get_bug_report_manager()
bug_manager.max_reports = 100
bug_manager.max_log_size_mb = 10
bug_manager.include_system_info = True
```

## API Reference

### WorkflowManager

```python
class WorkflowManager(QObject):
    def create_workflow_version(workflow_id: str, workflow_data: dict) -> tuple
    def update_workflow_version(workflow_id: str, version: int, data: dict) -> bool
    def resolve_conflict(workflow_id: str, resolution: ConflictResolution) -> bool
    def get_workflow_versions(workflow_id: str) -> List[VersionInfo]
    def get_active_users() -> List[str]
```

### CollaborationManager

```python
class CollaborationManager(QObject):
    def create_workflow_version(workflow_id: str, data: dict) -> tuple
    def send_notification(type: str, title: str, message: str, **kwargs) -> bool
    def submit_bug_report(title: str, description: str, **kwargs) -> str
    def get_feature_status() -> Dict[str, bool]
    def cleanup()
```

### BugReportManager

```python
class BugReportManager:
    def create_bug_report(report_data: dict, include_logs: bool = True) -> str
    def get_bug_reports() -> List[dict]
    def export_bug_report(report_id: str, export_path: str) -> bool
```

## Error Handling and Fallbacks

The system is designed with graceful degradation:

1. **Database Unavailable**: Falls back to file-based storage
2. **System Tray Unavailable**: Disables notifications, logs warnings
3. **SQLAlchemy Import Error**: Uses sqlite3 directly
4. **Permission Issues**: Creates temporary directories

## Testing

Run the integration tests:

```bash
# Test workflow management
python -m pytest tests/test_workflow_manager.py -v

# Test notification system
python -m pytest tests/test_collaboration_notifications.py -v

# Test bug reporting
python -m pytest tests/test_bug_report_system.py -v

# Run all collaboration feature tests
python -m pytest tests/test_collaboration_features.py -v
```

## Performance Considerations

### Database Pooling

- Connection pool size: 10 (configurable)
- Max overflow: 20 additional connections
- Connection timeout: 30 seconds
- Pool recycle: 1 hour to prevent stale connections

### Memory Management

- Notification history limited to 100 entries
- Log files capped at 10MB per file
- Bug reports auto-cleanup after 100 reports
- Version cache with LRU eviction

### Background Processing

- Conflict detection runs every 30 seconds
- Non-blocking UI operations
- Asynchronous database operations where possible

## Security Considerations

### Data Privacy

- Bug reports include only necessary system information
- User can opt-out of log collection
- No sensitive data in automatic reports
- Local storage only (no external transmission)

### File Permissions

- Bug reports stored with restricted permissions
- Database files use application-specific directories
- Log files rotated and cleaned up automatically

## Troubleshooting

### Common Issues

1. **"SQLAlchemy not available"**
   - Solution: `pip install SQLAlchemy>=2.0.0`
   - Fallback: File-based versioning still works

2. **"System tray not available"**
   - Solution: Ensure desktop environment supports system tray
   - Fallback: Features work without notifications

3. **"Database connection failed"**
   - Check file permissions in project directory
   - Verify SQLite is available
   - Check disk space

4. **"Bug report creation failed"**
   - Check write permissions in application directory
   - Verify disk space for log collection
   - Check if log files are locked by other processes

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.getLogger('src.collaboration_features').setLevel(logging.DEBUG)
logging.getLogger('src.workflow_manager').setLevel(logging.DEBUG)
logging.getLogger('src.bug_report_system').setLevel(logging.DEBUG)
```

## Future Enhancements

Planned improvements:

1. **Real-time Synchronization**: WebSocket-based collaboration
2. **Advanced Merge Algorithms**: Three-way merge for workflow conflicts
3. **Plugin Integration**: Collaboration hooks for plugins
4. **Cloud Backup**: Optional cloud storage for bug reports
5. **Analytics Dashboard**: Usage and collaboration metrics

## Migration Guide

For existing FANWS installations:

1. **Backup Current Data**:
   ```bash
   python backup_fanws.py
   ```

2. **Update Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Migration**:
   - SQLAlchemy models are auto-created
   - Existing data remains compatible
   - Version history preserved

4. **Configuration Update**:
   - New collaboration settings in `config/app_config.json`
   - UI preferences automatically saved

5. **Feature Activation**:
   ```python
   # Add to main application startup
   from src.collaboration_features import initialize_collaboration_features
   initialize_collaboration_features()
   ```

This completes the implementation of advanced collaboration, versioning, and reporting features for FANWS.
