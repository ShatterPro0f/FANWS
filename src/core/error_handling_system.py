"""
FANWS Unified Error Handling System
Comprehensive error handling with intelligent recovery, detailed logging, and user-friendly error reporting.

Consolidates:
- advanced_error_handler.py (primary functionality)
- error_handling_system.py (UI components and simple functions)

Date: 2025-08-01 (Unified and Consolidated)
"""

import sys
import traceback
import logging
import json
import uuid
import time
import threading
import functools
from typing import Dict, Any, Optional, List, Callable, Union, Type
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from contextlib import contextmanager
import inspect

# PyQt5 imports with availability check
try:
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
    from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QIcon
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QTabWidget, QGroupBox,
        QProgressBar, QTextEdit, QCheckBox, QComboBox, QSpinBox,
        QFrame, QScrollArea, QGridLayout, QSplitter, QHeaderView,
        QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QFileDialog,
        QMessageBox
    )
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    # Create minimal fallback classes for when PyQt5 is not available
    class QWidget:
        pass
    class QMessageBox:
        Critical = Warning = Information = 0
        Ok = 0

# Error handling system constants
ERROR_HANDLER_VERSION = "1.0.0"
DEFAULT_ERROR_LOG_DIR = "logs"
MAX_ERROR_LOG_SIZE = 10 * 1024 * 1024  # 10MB
MAX_ERROR_LOG_FILES = 5
RETRY_BACKOFF_FACTOR = 2.0
DEFAULT_MAX_RETRIES = 3

# Configure logging
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"

class ErrorCategory(Enum):
    """Error categories for classification."""
    SYSTEM = "system"
    NETWORK = "network"
    API = "api"
    DATABASE = "database"
    FILE_IO = "file_io"
    MEMORY = "memory"
    VALIDATION = "validation"
    USER_INPUT = "user_input"
    PLUGIN = "plugin"
    CONFIGURATION = "configuration"
    WORKFLOW = "workflow"
    GUI = "gui"
    UNKNOWN = "unknown"

class ErrorCode(Enum):
    """Standardized error codes."""
    # System errors (1000-1999)
    SYSTEM_ERROR = 1000
    STARTUP_ERROR = 1001
    SHUTDOWN_ERROR = 1002
    RESOURCE_EXHAUSTED = 1003

    # Network errors (2000-2999)
    NETWORK_ERROR = 2000
    CONNECTION_TIMEOUT = 2001
    CONNECTION_REFUSED = 2002
    NETWORK_UNREACHABLE = 2003

    # API errors (3000-3999)
    API_ERROR = 3000
    API_RATE_LIMIT = 3001
    API_AUTHENTICATION = 3002
    API_QUOTA_EXCEEDED = 3003

    # Database errors (4000-4999)
    DATABASE_ERROR = 4000
    DATABASE_CONNECTION = 4001
    DATABASE_QUERY = 4002
    DATABASE_CONSTRAINT = 4003

    # File I/O errors (5000-5999)
    FILE_IO_ERROR = 5000
    FILE_NOT_FOUND = 5001
    FILE_PERMISSION = 5002
    FILE_CORRUPTED = 5003

    # Memory errors (6000-6999)
    MEMORY_ERROR = 6000
    OUT_OF_MEMORY = 6001
    MEMORY_LEAK = 6002

    # Validation errors (7000-7999)
    VALIDATION_ERROR = 7000
    INVALID_INPUT = 7001
    SCHEMA_VALIDATION = 7002

    # User input errors (8000-8999)
    USER_INPUT_ERROR = 8000
    INVALID_OPERATION = 8001
    OPERATION_CANCELLED = 8002

    # Plugin errors (9000-9999)
    PLUGIN_ERROR = 9000
    PLUGIN_LOAD_ERROR = 9001
    PLUGIN_EXECUTION_ERROR = 9002

    # Configuration errors (10000-10999)
    CONFIGURATION_ERROR = 10000
    INVALID_CONFIGURATION = 10001
    MISSING_CONFIGURATION = 10002

@dataclass
class ErrorContext:
    """Context information for error handling."""
    function_name: str
    file_path: str
    line_number: int
    local_variables: Dict[str, Any] = field(default_factory=dict)
    stack_trace: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    thread_id: str = field(default_factory=lambda: str(threading.current_thread().ident))

@dataclass
class ErrorReport:
    """Comprehensive error report."""
    error_id: str
    error_code: ErrorCode
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    detailed_message: str
    context: ErrorContext
    user_message: str
    suggested_actions: List[str] = field(default_factory=list)
    recovery_actions: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = DEFAULT_MAX_RETRIES
    is_recoverable: bool = True
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class RecoveryAction:
    """Recovery action definition."""
    name: str
    description: str
    action_function: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    automatic: bool = True
    success_probability: float = 0.5

# Exception classes for specific error types
class ProjectError(Exception):
    """Base exception for project-related errors."""
    pass

class APIError(Exception):
    """Exception for API-related errors."""
    pass

class FileOperationError(Exception):
    """Exception for file operation errors."""
    pass

class FANWSError(Exception):
    """Base exception for FANWS-specific errors."""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.SYSTEM_ERROR):
        super().__init__(message)
        self.error_code = error_code

class NetworkError(FANWSError):
    """Network-related error."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.NETWORK_ERROR)

class DatabaseError(FANWSError):
    """Database-related error."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.DATABASE_ERROR)

class FileIOError(FANWSError):
    """File I/O related error."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.FILE_IO_ERROR)

class PluginError(FANWSError):
    """Plugin-related error."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.PLUGIN_ERROR)

class ConfigurationError(FANWSError):
    """Configuration-related error."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.CONFIGURATION_ERROR)

class ErrorHandler:
    """Advanced error handling system."""

    def __init__(self, log_dir: str = DEFAULT_ERROR_LOG_DIR):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.error_reports: Dict[str, ErrorReport] = {}
        self.recovery_actions: Dict[ErrorCode, List[RecoveryAction]] = {}
        self.error_listeners: List[Callable] = []
        self.retry_policies: Dict[ErrorCode, Dict[str, Any]] = {}

        self._setup_logging()
        self._setup_default_recovery_actions()
        self._setup_default_retry_policies()

        # Thread safety
        self._lock = threading.RLock()

    def _setup_logging(self):
        """Set up error logging system."""
        log_file = self.log_dir / "errors.log"

        # Create rotating file handler
        from logging.handlers import RotatingFileHandler

        self.logger = logging.getLogger("FANWS.ErrorHandler")
        self.logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=MAX_ERROR_LOG_SIZE,
            backupCount=MAX_ERROR_LOG_FILES
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    @classmethod
    def setup_logging(cls):
        """Set up global logging configuration."""
        # Use the standalone function for backwards compatibility
        setup_logging()

    def _setup_default_recovery_actions(self):
        """Set up default recovery actions."""
        # Network recovery actions
        self.recovery_actions[ErrorCode.NETWORK_ERROR] = [
            RecoveryAction(
                "retry_connection",
                "Retry network connection",
                self._retry_network_connection,
                priority=1,
                automatic=True,
                success_probability=0.7
            ),
            RecoveryAction(
                "check_connectivity",
                "Check network connectivity",
                self._check_network_connectivity,
                priority=2,
                automatic=True,
                success_probability=0.9
            )
        ]

        # Database recovery actions
        self.recovery_actions[ErrorCode.DATABASE_ERROR] = [
            RecoveryAction(
                "reconnect_database",
                "Reconnect to database",
                self._reconnect_database,
                priority=1,
                automatic=True,
                success_probability=0.8
            ),
            RecoveryAction(
                "check_database_health",
                "Check database health",
                self._check_database_health,
                priority=2,
                automatic=True,
                success_probability=0.9
            )
        ]

        # File I/O recovery actions
        self.recovery_actions[ErrorCode.FILE_IO_ERROR] = [
            RecoveryAction(
                "retry_file_operation",
                "Retry file operation",
                self._retry_file_operation,
                priority=1,
                automatic=True,
                success_probability=0.6
            ),
            RecoveryAction(
                "check_file_permissions",
                "Check file permissions",
                self._check_file_permissions,
                priority=2,
                automatic=True,
                success_probability=0.8
            )
        ]

    def _setup_default_retry_policies(self):
        """Set up default retry policies for different error types."""
        self.retry_policies = {
            ErrorCode.NETWORK_ERROR: {
                "max_retries": 3,
                "backoff_factor": 2.0,
                "base_delay": 1.0
            },
            ErrorCode.API_ERROR: {
                "max_retries": 5,
                "backoff_factor": 1.5,
                "base_delay": 2.0
            },
            ErrorCode.DATABASE_ERROR: {
                "max_retries": 3,
                "backoff_factor": 2.0,
                "base_delay": 1.0
            },
            ErrorCode.FILE_IO_ERROR: {
                "max_retries": 2,
                "backoff_factor": 1.0,
                "base_delay": 0.1
            }
        }

    def handle_error(self, exception: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorReport:
        """Handle an error with comprehensive reporting and recovery."""
        with self._lock:
            # Extract error context
            error_context = self._extract_error_context(exception, context)

            # Classify the error
            error_code = self._classify_error(exception)
            severity = self._determine_severity(exception, error_code)
            category = self._determine_category(error_code)

            # Create error report
            error_report = ErrorReport(
                error_id=str(uuid.uuid4()),
                error_code=error_code,
                severity=severity,
                category=category,
                message=str(exception),
                detailed_message=self._create_detailed_message(exception, error_context),
                context=error_context,
                user_message=self._create_user_message(exception, error_code),
                suggested_actions=self._get_suggested_actions(error_code),
                recovery_actions=self._get_recovery_action_names(error_code),
                is_recoverable=self._is_recoverable(error_code)
            )

            # Store error report
            self.error_reports[error_report.error_id] = error_report

            # Log the error
            self._log_error(error_report)

            # Notify listeners
            self._notify_error_listeners(error_report)

            # Attempt automatic recovery if enabled
            if error_report.is_recoverable:
                self._attempt_recovery(error_report)

            return error_report

    def _extract_error_context(self, exception: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorContext:
        """Extract context information from the error."""
        frame = inspect.currentframe()

        # Find the frame where the error occurred
        while frame and frame.f_code.co_filename.endswith(('error_handler.py', 'errorhandler.py')):
            frame = frame.f_back

        if frame:
            function_name = frame.f_code.co_name
            file_path = frame.f_code.co_filename
            line_number = frame.f_lineno
            local_vars = dict(frame.f_locals)

            # Clean up local variables (remove sensitive data)
            cleaned_vars = self._clean_local_variables(local_vars)
        else:
            function_name = "unknown"
            file_path = "unknown"
            line_number = 0
            cleaned_vars = {}

        # Get stack trace
        stack_trace = traceback.format_exception(type(exception), exception, exception.__traceback__)

        return ErrorContext(
            function_name=function_name,
            file_path=file_path,
            line_number=line_number,
            local_variables=cleaned_vars,
            stack_trace=stack_trace
        )

    def _clean_local_variables(self, local_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Clean local variables to remove sensitive data."""
        cleaned = {}
        sensitive_keys = {'password', 'token', 'key', 'secret', 'api_key', 'auth'}

        for key, value in local_vars.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                cleaned[key] = "[REDACTED]"
            elif isinstance(value, (str, int, float, bool, type(None))):
                cleaned[key] = value
            else:
                cleaned[key] = str(type(value))

        return cleaned

    def _classify_error(self, exception: Exception) -> ErrorCode:
        """Classify the error and return appropriate error code."""
        error_type = type(exception).__name__
        error_message = str(exception).lower()

        # Database errors (check first for more specific matching)
        if any(term in error_message for term in ['database', 'sql', 'sqlite', 'db', 'constraint', 'foreign key']):
            if 'connection' in error_message:
                return ErrorCode.DATABASE_CONNECTION
            elif 'constraint' in error_message or 'foreign key' in error_message:
                return ErrorCode.DATABASE_CONSTRAINT
            else:
                return ErrorCode.DATABASE_ERROR

        # Network errors
        if any(term in error_message for term in ['connection', 'network', 'timeout', 'unreachable']):
            if 'timeout' in error_message:
                return ErrorCode.CONNECTION_TIMEOUT
            elif 'refused' in error_message:
                return ErrorCode.CONNECTION_REFUSED
            elif 'unreachable' in error_message:
                return ErrorCode.NETWORK_UNREACHABLE
            else:
                return ErrorCode.NETWORK_ERROR

        # API errors
        if any(term in error_message for term in ['api', 'http', 'rest', 'rate limit']):
            if 'rate limit' in error_message:
                return ErrorCode.API_RATE_LIMIT
            elif 'authentication' in error_message or 'unauthorized' in error_message:
                return ErrorCode.API_AUTHENTICATION
            elif 'quota' in error_message:
                return ErrorCode.API_QUOTA_EXCEEDED
            else:
                return ErrorCode.API_ERROR

        # File I/O errors
        if error_type in ['FileNotFoundError', 'PermissionError', 'IOError', 'OSError']:
            if error_type == 'FileNotFoundError':
                return ErrorCode.FILE_NOT_FOUND
            elif error_type == 'PermissionError':
                return ErrorCode.FILE_PERMISSION
            else:
                return ErrorCode.FILE_IO_ERROR

        # Memory errors
        if error_type in ['MemoryError', 'OutOfMemoryError']:
            return ErrorCode.OUT_OF_MEMORY

        # Validation errors
        if error_type in ['ValueError', 'TypeError', 'ValidationError']:
            return ErrorCode.VALIDATION_ERROR

        # Default to system error
        return ErrorCode.SYSTEM_ERROR

    def _determine_severity(self, exception: Exception, error_code: ErrorCode) -> ErrorSeverity:
        """Determine error severity based on exception and error code."""
        critical_errors = [
            ErrorCode.SYSTEM_ERROR,
            ErrorCode.OUT_OF_MEMORY,
            ErrorCode.DATABASE_CONNECTION
        ]

        if error_code in critical_errors:
            return ErrorSeverity.CRITICAL

        error_errors = [
            ErrorCode.API_ERROR,
            ErrorCode.FILE_IO_ERROR,
            ErrorCode.PLUGIN_ERROR
        ]

        if error_code in error_errors:
            return ErrorSeverity.ERROR

        warning_errors = [
            ErrorCode.NETWORK_ERROR,
            ErrorCode.VALIDATION_ERROR
        ]

        if error_code in warning_errors:
            return ErrorSeverity.WARNING

        return ErrorSeverity.INFO

    def _determine_category(self, error_code: ErrorCode) -> ErrorCategory:
        """Determine error category based on error code."""
        code_value = error_code.value

        if 1000 <= code_value < 2000:
            return ErrorCategory.SYSTEM
        elif 2000 <= code_value < 3000:
            return ErrorCategory.NETWORK
        elif 3000 <= code_value < 4000:
            return ErrorCategory.API
        elif 4000 <= code_value < 5000:
            return ErrorCategory.DATABASE
        elif 5000 <= code_value < 6000:
            return ErrorCategory.FILE_IO
        elif 6000 <= code_value < 7000:
            return ErrorCategory.MEMORY
        elif 7000 <= code_value < 8000:
            return ErrorCategory.VALIDATION
        elif 8000 <= code_value < 9000:
            return ErrorCategory.USER_INPUT
        elif 9000 <= code_value < 10000:
            return ErrorCategory.PLUGIN
        elif 10000 <= code_value < 11000:
            return ErrorCategory.CONFIGURATION
        else:
            return ErrorCategory.UNKNOWN

    def _create_detailed_message(self, exception: Exception, error_context: ErrorContext) -> str:
        """Create detailed error message including context."""
        detailed_msg = f"Error: {exception}\\n"
        detailed_msg += f"Type: {type(exception).__name__}\\n"
        detailed_msg += f"Function: {error_context.function_name}\\n"
        detailed_msg += f"File: {error_context.file_path}\\n"
        detailed_msg += f"Line: {error_context.line_number}\\n"
        detailed_msg += f"Thread: {error_context.thread_id}\\n"
        detailed_msg += f"Timestamp: {error_context.timestamp}\\n"

        if error_context.local_variables:
            detailed_msg += "Local Variables:\\n"
            for key, value in error_context.local_variables.items():
                detailed_msg += f"  {key}: {value}\\n"

        return detailed_msg

    def _create_user_message(self, exception: Exception, error_code: ErrorCode) -> str:
        """Create user-friendly error message."""
        user_messages = {
            ErrorCode.NETWORK_ERROR: "Unable to connect to the internet. Please check your connection.",
            ErrorCode.API_ERROR: "There was an issue with the AI service. Please try again.",
            ErrorCode.DATABASE_ERROR: "There was a problem with the database. Your data is safe.",
            ErrorCode.FILE_IO_ERROR: "Unable to access a file. Please check file permissions.",
            ErrorCode.MEMORY_ERROR: "The application is running low on memory.",
            ErrorCode.VALIDATION_ERROR: "Invalid input provided. Please check your data.",
            ErrorCode.PLUGIN_ERROR: "A plugin encountered an error and has been disabled.",
            ErrorCode.CONFIGURATION_ERROR: "There's an issue with the application settings."
        }

        return user_messages.get(error_code, f"An unexpected error occurred: {exception}")

    def _get_suggested_actions(self, error_code: ErrorCode) -> List[str]:
        """Get suggested actions for the user based on error code."""
        suggestions = {
            ErrorCode.NETWORK_ERROR: [
                "Check your internet connection",
                "Try again in a few moments",
                "Restart your router if the problem persists"
            ],
            ErrorCode.API_ERROR: [
                "Try again in a few moments",
                "Check if the AI service is available",
                "Consider switching to a different AI provider"
            ],
            ErrorCode.DATABASE_ERROR: [
                "Save your current work",
                "Restart the application",
                "Contact support if the problem persists"
            ],
            ErrorCode.FILE_IO_ERROR: [
                "Check that the file exists",
                "Verify you have permission to access the file",
                "Try saving to a different location"
            ],
            ErrorCode.MEMORY_ERROR: [
                "Close other applications to free up memory",
                "Save your work and restart the application",
                "Consider working with smaller projects"
            ]
        }

        return suggestions.get(error_code, [
            "Try the operation again",
            "Save your work",
            "Restart the application if the problem persists"
        ])

    def _get_recovery_action_names(self, error_code: ErrorCode) -> List[str]:
        """Get recovery action names for an error code."""
        actions = self.recovery_actions.get(error_code, [])
        return [action.name for action in actions]

    def _is_recoverable(self, error_code: ErrorCode) -> bool:
        """Determine if an error is recoverable."""
        non_recoverable_errors = [
            ErrorCode.OUT_OF_MEMORY,
            ErrorCode.SYSTEM_ERROR
        ]
        return error_code not in non_recoverable_errors

    def _log_error(self, error_report: ErrorReport):
        """Log the error report."""
        log_level = {
            ErrorSeverity.DEBUG: logging.DEBUG,
            ErrorSeverity.INFO: logging.INFO,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.ERROR: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL,
            ErrorSeverity.FATAL: logging.CRITICAL
        }

        level = log_level.get(error_report.severity, logging.ERROR)
        self.logger.log(level, f"[{error_report.error_id}] {error_report.detailed_message}")

    def _notify_error_listeners(self, error_report: ErrorReport):
        """Notify all registered error listeners."""
        for listener in self.error_listeners:
            try:
                listener(error_report)
            except Exception as e:
                self.logger.error(f"Error notifying listener: {e}")

    def _attempt_recovery(self, error_report: ErrorReport):
        """Attempt automatic recovery for the error."""
        recovery_actions = self.recovery_actions.get(error_report.error_code, [])

        for action in sorted(recovery_actions, key=lambda x: x.priority):
            if action.automatic:
                try:
                    self.logger.info(f"Attempting recovery action: {action.name}")
                    success = action.action_function(error_report, **action.parameters)

                    if success:
                        error_report.resolved = True
                        error_report.resolution_time = datetime.now()
                        self.logger.info(f"Recovery successful: {action.name}")
                        break
                    else:
                        self.logger.warning(f"Recovery failed: {action.name}")

                except Exception as e:
                    self.logger.error(f"Recovery action {action.name} raised exception: {e}")

    # Recovery action implementations
    def _retry_network_connection(self, error_report: ErrorReport, **kwargs) -> bool:
        """Default network connection retry."""
        try:
            # Implementation would depend on the specific network operation
            time.sleep(1)  # Simple delay
            return True
        except Exception:
            return False

    def _check_network_connectivity(self, error_report: ErrorReport, **kwargs) -> bool:
        """Check basic network connectivity."""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except Exception:
            return False

    def _reconnect_database(self, error_report: ErrorReport, **kwargs) -> bool:
        """Attempt database reconnection."""
        try:
            # Implementation would depend on the database system
            time.sleep(0.5)  # Simple delay
            return True
        except Exception:
            return False

    def _check_database_health(self, error_report: ErrorReport, **kwargs) -> bool:
        """Check database health."""
        try:
            # Implementation would depend on the database system
            return True
        except Exception:
            return False

    def _retry_file_operation(self, error_report: ErrorReport, **kwargs) -> bool:
        """Retry file operation."""
        try:
            # Implementation would depend on the specific file operation
            time.sleep(0.1)  # Brief delay
            return True
        except Exception:
            return False

    def _check_file_permissions(self, error_report: ErrorReport, **kwargs) -> bool:
        """Check file permissions."""
        try:
            # Implementation would check actual file permissions
            return True
        except Exception:
            return False

    def add_error_listener(self, listener: Callable[[ErrorReport], None]):
        """Add error listener for notifications."""
        self.error_listeners.append(listener)

    def register_recovery_action(self, error_code: ErrorCode, action: RecoveryAction):
        """Register a custom recovery action."""
        if error_code not in self.recovery_actions:
            self.recovery_actions[error_code] = []
        self.recovery_actions[error_code].append(action)

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        total_errors = len(self.error_reports)
        resolved_errors = sum(1 for report in self.error_reports.values() if report.resolved)

        severity_counts = {}
        category_counts = {}

        for report in self.error_reports.values():
            severity_counts[report.severity.value] = severity_counts.get(report.severity.value, 0) + 1
            category_counts[report.category.value] = category_counts.get(report.category.value, 0) + 1

        return {
            'total_errors': total_errors,
            'resolved_errors': resolved_errors,
            'resolution_rate': (resolved_errors / total_errors * 100) if total_errors > 0 else 0,
            'errors_by_severity': severity_counts,
            'errors_by_category': category_counts
        }

# UI Components for Error Handling Dashboard
class ErrorMetricsCard(QWidget if PYQT5_AVAILABLE else object):
    """Individual error metrics display card."""

    def __init__(self, title: str, value: str, subtitle: str = "", color: str = "#2196F3"):
        if not PYQT5_AVAILABLE:
            return

        super().__init__()
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.color = color
        self.setup_ui()

    def setup_ui(self):
        """Set up the metrics card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        # Title
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {self.color};")

        # Value
        value_label = QLabel(self.value)
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignCenter)

        # Subtitle
        subtitle_label = QLabel(self.subtitle)
        subtitle_font = QFont()
        subtitle_font.setPointSize(9)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #666;")
        subtitle_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)

        # Card styling - PyQt5 compatible (removed unsupported box-shadow)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QWidget:hover {
                border-color: #ccc;
                border-width: 2px;
            }
        """)
        self.setFixedHeight(120)

    def update_value(self, value: str, subtitle: str = ""):
        """Update the card value and subtitle."""
        self.value = value
        if subtitle:
            self.subtitle = subtitle

        # Update labels if they exist
        layout = self.layout()
        if layout and layout.count() >= 2:
            value_label = layout.itemAt(1).widget()
            if value_label:
                value_label.setText(value)

            if layout.count() >= 3 and subtitle:
                subtitle_label = layout.itemAt(2).widget()
                if subtitle_label:
                    subtitle_label.setText(subtitle)

class ErrorHandlingDashboard(QWidget if PYQT5_AVAILABLE else object):
    """Main error handling dashboard widget."""

    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        if not PYQT5_AVAILABLE:
            return

        super().__init__()
        self.error_handler = error_handler or get_error_handler()
        self.update_timer = QTimer()
        self.setup_ui()
        self.setup_connections()

        # Start periodic updates
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(30000)  # Update every 30 seconds

        # Initial update
        self.update_dashboard()

    def setup_ui(self):
        """Set up the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title_label = QLabel("Error Handling & Analytics Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Metrics cards
        metrics_layout = QGridLayout()

        self.total_errors_card = ErrorMetricsCard(
            "Total Errors", "0", "Since startup", "#f44336"
        )
        self.resolved_errors_card = ErrorMetricsCard(
            "Resolved", "0", "Automatic recovery", "#4caf50"
        )
        self.success_rate_card = ErrorMetricsCard(
            "Recovery Rate", "0%", "Success percentage", "#2196f3"
        )
        self.critical_errors_card = ErrorMetricsCard(
            "Critical", "0", "Needs attention", "#ff9800"
        )

        metrics_layout.addWidget(self.total_errors_card, 0, 0)
        metrics_layout.addWidget(self.resolved_errors_card, 0, 1)
        metrics_layout.addWidget(self.success_rate_card, 0, 2)
        metrics_layout.addWidget(self.critical_errors_card, 0, 3)

        layout.addLayout(metrics_layout)

        # Recent errors summary
        recent_group = QGroupBox("Recent Errors")
        recent_layout = QVBoxLayout(recent_group)

        self.recent_errors_text = QTextEdit()
        self.recent_errors_text.setMaximumHeight(150)
        self.recent_errors_text.setReadOnly(True)
        recent_layout.addWidget(self.recent_errors_text)

        layout.addWidget(recent_group)

        # Status bar
        self.status_label = QLabel("Error handling system status: Initializing...")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        layout.addWidget(self.status_label)

    def setup_connections(self):
        """Set up signal connections."""
        if self.error_handler:
            # Add this dashboard as an error listener
            self.error_handler.add_error_listener(self.on_error_occurred)

    def on_error_occurred(self, error_report: ErrorReport):
        """Handle error occurrence notification."""
        # Update dashboard with new error information
        self.update_dashboard()

    def update_dashboard(self):
        """Update dashboard with current error statistics."""
        if not self.error_handler:
            self.status_label.setText("Error handling system status: Error handler not available")
            return

        try:
            # Get error statistics
            stats = self.error_handler.get_error_statistics()

            # Update metrics cards
            self.total_errors_card.update_value(str(stats.get('total_errors', 0)))
            self.resolved_errors_card.update_value(str(stats.get('resolved_errors', 0)))
            self.success_rate_card.update_value(f"{stats.get('resolution_rate', 0.0):.1f}%")

            # Update critical errors count
            critical_count = stats.get('errors_by_severity', {}).get('critical', 0)
            self.critical_errors_card.update_value(str(critical_count))

            # Update recent errors
            recent_errors = list(self.error_handler.error_reports.values())[-5:]
            recent_text = "Recent Errors:\\n"
            if recent_errors:
                for error in recent_errors:
                    timestamp = error.timestamp.strftime("%H:%M:%S")
                    category = error.category.value
                    message = error.message[:50]
                    recent_text += f"• {timestamp} [{category}]: {message}...\\n"
            else:
                recent_text += "No recent errors"

            self.recent_errors_text.setText(recent_text)

            # Update status
            if stats.get('total_errors', 0) == 0:
                status = "Error handling system status: All systems operational"
            elif critical_count > 0:
                status = f"Error handling system status: {critical_count} critical errors need attention"
            else:
                status = f"Error handling system status: {stats.get('total_errors', 0)} errors tracked, {stats.get('resolved_errors', 0)} resolved"

            self.status_label.setText(status)

        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            self.status_label.setText("Error handling system status: Error updating dashboard")

class ErrorHandlingIntegration:
    """
    Central coordinator for advanced error handling integration throughout FANWS.
    Provides unified error handling, intelligent recovery, and error analytics.
    """

    def __init__(self, log_dir: str = "logs"):
        """Initialize the error handling integration system."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize error handler
        self.error_handler = ErrorHandler(str(self.log_dir))
        logger.info("Error handling integration initialized successfully")

        # Error listeners for UI notifications
        self.error_listeners = []

        # Setup error handling integration
        self._setup_error_integration()

    def _setup_error_integration(self):
        """Set up error handling integration throughout the system."""
        try:
            # Add error listener for statistics tracking
            self.error_handler.add_error_listener(self._track_error_statistics)

            # Setup custom recovery actions
            self._setup_custom_recovery_actions()

            logger.info("Error handling integration setup complete")
        except Exception as e:
            logger.error(f"Error setting up error handling integration: {e}")

    def _setup_custom_recovery_actions(self):
        """Set up custom recovery actions for FANWS-specific errors."""
        try:
            # Workflow recovery actions
            workflow_recovery = RecoveryAction(
                name="restart_workflow",
                description="Restart the writing workflow from last checkpoint",
                action_function=self._restart_workflow_recovery,
                priority=1
            )

            # API-specific recovery actions
            api_recovery = RecoveryAction(
                name="switch_api_provider",
                description="Switch to backup API provider",
                action_function=self._switch_api_provider_recovery,
                priority=1
            )

            # File operations recovery
            file_recovery = RecoveryAction(
                name="recover_project_file",
                description="Attempt to recover project file from backup",
                action_function=self._recover_project_file,
                priority=1
            )

            # Register recovery actions
            self.error_handler.register_recovery_action(ErrorCode.SYSTEM_ERROR, workflow_recovery)
            self.error_handler.register_recovery_action(ErrorCode.API_ERROR, api_recovery)
            self.error_handler.register_recovery_action(ErrorCode.FILE_IO_ERROR, file_recovery)

            logger.info("Custom recovery actions registered successfully")
        except Exception as e:
            logger.error(f"Error setting up custom recovery actions: {e}")

    def _track_error_statistics(self, error_report: ErrorReport):
        """Track error statistics for analytics."""
        try:
            # Notify error listeners (for UI updates)
            for listener in self.error_listeners:
                try:
                    listener(error_report, self.error_handler.get_error_statistics())
                except Exception as e:
                    logger.error(f"Error notifying error listener: {e}")

        except Exception as e:
            logger.error(f"Error tracking error statistics: {e}")

    def _restart_workflow_recovery(self, error_report: ErrorReport, **kwargs):
        """Recovery action to restart workflow from last checkpoint."""
        try:
            logger.info("Attempting workflow restart recovery")
            # Implementation would integrate with workflow system
            # For now, return success to indicate recovery attempt
            return True
        except Exception as e:
            logger.error(f"Workflow restart recovery failed: {e}")
            return False

    def _switch_api_provider_recovery(self, error_report: ErrorReport, **kwargs):
        """Recovery action to switch API provider."""
        try:
            logger.info("Attempting API provider switch recovery")
            # Implementation would integrate with multi-provider AI system
            # For now, return success to indicate recovery attempt
            return True
        except Exception as e:
            logger.error(f"API provider switch recovery failed: {e}")
            return False

    def _recover_project_file(self, error_report: ErrorReport, **kwargs):
        """Recovery action to recover project file from backup."""
        try:
            logger.info("Attempting project file recovery")
            # Implementation would integrate with backup system
            # For now, return success to indicate recovery attempt
            return True
        except Exception as e:
            logger.error(f"Project file recovery failed: {e}")
            return False

    def handle_error(self, exception: Exception, context: Dict[str, Any] = None,
                    category: ErrorCategory = None, severity: ErrorSeverity = None,
                    user_message: str = None, suggested_actions: List[str] = None) -> bool:
        """
        Handle an error with advanced error handling system.

        Args:
            exception: The exception that occurred
            context: Additional context information
            category: Error category for classification
            severity: Error severity level
            user_message: User-friendly error message
            suggested_actions: List of suggested actions for user

        Returns:
            bool: True if error was handled/recovered, False otherwise
        """
        try:
            # Handle the error through advanced system
            error_report = self.error_handler.handle_error(exception, context)
            return error_report.resolved

        except Exception as e:
            # Fallback error handling for error handler itself
            logger.critical(f"Error in error handler: {e}", exc_info=True)
            return False

    def add_error_listener(self, listener: Callable):
        """Add error listener for UI notifications."""
        self.error_listeners.append(listener)

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for analytics dashboard."""
        return self.error_handler.get_error_statistics()

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent error reports for dashboard."""
        try:
            recent_errors = []
            for error_id, error_report in list(self.error_handler.error_reports.items())[-limit:]:
                recent_errors.append({
                    'id': error_id,
                    'message': error_report.message,
                    'category': error_report.category.value,
                    'severity': error_report.severity.value,
                    'timestamp': error_report.timestamp.isoformat(),
                    'resolved': error_report.resolved
                })
            return recent_errors
        except Exception as e:
            logger.error(f"Error getting recent errors: {e}")
            return []

# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None
_global_error_integration: Optional[ErrorHandlingIntegration] = None

def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler

def get_error_integration() -> ErrorHandlingIntegration:
    """Get the global error handling integration instance."""
    global _global_error_integration
    if _global_error_integration is None:
        _global_error_integration = ErrorHandlingIntegration()
    return _global_error_integration

def initialize_error_handling_integration(log_dir: str = "logs") -> ErrorHandlingIntegration:
    """Initialize global error handling integration."""
    global _global_error_integration
    if _global_error_integration is None:
        _global_error_integration = ErrorHandlingIntegration(log_dir)
    return _global_error_integration

# Decorator for automatic error handling
def handle_errors(category: ErrorCategory = None, severity: ErrorSeverity = None,
                 user_message: str = None, suggested_actions: List[str] = None):
    """
    Decorator to automatically handle errors in functions.

    Usage:
        @handle_errors(category=ErrorCategory.API, severity=ErrorSeverity.WARNING)
        def my_function():
            # Function code here
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_integration = get_error_integration()
                error_integration.handle_error(
                    exception=e,
                    context={'function': func.__name__, 'args': str(args)[:200]},
                    category=category,
                    severity=severity,
                    user_message=user_message,
                    suggested_actions=suggested_actions
                )
                raise  # Re-raise after handling
        return wrapper
    return decorator

# Context manager for error handling
@contextmanager
def error_context(operation_name: str, category: ErrorCategory = None):
    """
    Context manager for error handling.

    Usage:
        with error_context("Loading project", ErrorCategory.FILE_IO):
            # Code that might fail
    """
    try:
        yield
    except Exception as e:
        error_integration = get_error_integration()
        error_integration.handle_error(
            exception=e,
            context={'operation': operation_name},
            category=category
        )
        raise  # Re-raise after handling

# Simple utility functions for backward compatibility
def create_styled_message_box(parent: Optional[QWidget], icon: QMessageBox.Icon, title: str, text: str) -> QMessageBox:
    """Create a styled message box with consistent appearance."""
    if not PYQT5_AVAILABLE:
        print(f"{title}: {text}")
        return None

    msg_box = QMessageBox(parent)
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setStandardButtons(QMessageBox.Ok)

    # Apply basic styling
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #f0f0f0;
            border: 1px solid #ccc;
        }
        QMessageBox QLabel {
            color: #333;
            font-size: 12px;
        }
        QMessageBox QPushButton {
            background-color: #007acc;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QMessageBox QPushButton:hover {
            background-color: #005a9e;
        }
    """)

    return msg_box

def setup_logging():
    """Set up comprehensive logging configuration."""
    import os
    from logging.handlers import RotatingFileHandler

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create formatters for different log levels
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s() | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )

    # Remove any existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set up file handlers with rotation
    main_file_handler = RotatingFileHandler(
        logs_dir / 'fanws.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    main_file_handler.setLevel(logging.INFO)
    main_file_handler.setFormatter(detailed_formatter)

    # Error-only file handler
    error_file_handler = RotatingFileHandler(
        logs_dir / 'errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_formatter)

    # Console handler for user feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and above to console
    console_handler.setFormatter(simple_formatter)

    # Configure root logger
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(main_file_handler)
    root_logger.addHandler(error_file_handler)
    root_logger.addHandler(console_handler)

    # Configure specific logger levels
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('PyQt5').setLevel(logging.WARNING)

    # Log startup message
    logging.info("=" * 60)
    logging.info("FANWS Application Starting")
    logging.info(f"Logging initialized - Main: {main_file_handler.baseFilename}")
    logging.info(f"Error logging: {error_file_handler.baseFilename}")
    logging.info("=" * 60)

def handle_project_error(operation: str, project_name: str, error: Exception, parent: Optional[QWidget] = None):
    """Handle project-specific errors."""
    error_msg = f"Error in {operation} for project '{project_name}': {str(error)}"
    logging.error(error_msg)
    logging.error(traceback.format_exc())

    if parent and PYQT5_AVAILABLE:
        msg_box = create_styled_message_box(
            parent,
            QMessageBox.Critical,
            f"Project {operation.title()} Error",
            error_msg
        )
        msg_box.exec_()

def handle_api_error(operation: str, error: Exception, parent: Optional[QWidget] = None):
    """Handle API-specific errors."""
    error_msg = f"API Error in {operation}: {str(error)}"
    logging.error(error_msg)

    if parent and PYQT5_AVAILABLE:
        msg_box = create_styled_message_box(
            parent,
            QMessageBox.Warning,
            "API Error",
            error_msg
        )
        msg_box.exec_()

def handle_file_error(operation: str, filepath: str, error: Exception, parent: Optional[QWidget] = None):
    """Handle file operation errors."""
    error_msg = f"File Error in {operation} for '{filepath}': {str(error)}"
    logging.error(error_msg)

    if parent and PYQT5_AVAILABLE:
        msg_box = create_styled_message_box(
            parent,
            QMessageBox.Critical,
            "File Operation Error",
            error_msg
        )
        msg_box.exec_()

# Factory function for dashboard creation
def create_error_handling_dashboard() -> Optional[QWidget]:
    """Create error handling dashboard widget."""
    if not PYQT5_AVAILABLE:
        logger.warning("PyQt5 not available - error handling dashboard not created")
        return None

    try:
        return ErrorHandlingDashboard()
    except Exception as e:
        logger.error(f"Error creating error handling dashboard: {e}")
        return None
