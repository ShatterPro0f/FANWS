"""
User Testing Monitor System for FANWS
Monitors all user actions, logs errors, and generates fix recommendations
"""

import os
import sys
import json
import time
import logging
import threading
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import psutil
import queue
import sqlite3
from contextlib import contextmanager

class UserTestingMonitor:
    """Comprehensive user testing monitoring system."""

    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"user_test_{int(time.time())}"
        self.start_time = datetime.now()
        self.actions_log = []
        self.errors_log = []
        self.performance_log = []
        self.fixes_needed = []
        self.current_test_phase = "initialization"

        # Create monitoring directories
        self.log_dir = Path("user_testing_logs")
        self.log_dir.mkdir(exist_ok=True)

        # Initialize database for detailed logging
        self.db_path = self.log_dir / f"user_testing_{self.session_id}.db"
        self.init_database()

        # Setup logging
        self.setup_logging()

        # Action tracking
        self.action_queue = queue.Queue()
        self.monitor_thread = None
        self.monitoring_active = False

        # Performance monitoring
        self.process = psutil.Process()
        self.memory_baseline = self.process.memory_info().rss / 1024 / 1024  # MB

        # Error tracking hooks
        self.original_excepthook = sys.excepthook
        sys.excepthook = self.exception_handler

        print(f"🔍 User Testing Monitor initialized - Session: {self.session_id}")

    def init_database(self):
        """Initialize SQLite database for detailed logging."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    phase TEXT,
                    action_type TEXT,
                    component TEXT,
                    details TEXT,
                    success BOOLEAN,
                    duration_ms REAL,
                    memory_mb REAL
                );

                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    phase TEXT,
                    error_type TEXT,
                    component TEXT,
                    message TEXT,
                    traceback TEXT,
                    severity TEXT,
                    context TEXT
                );

                CREATE TABLE IF NOT EXISTS performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    phase TEXT,
                    metric_name TEXT,
                    value REAL,
                    unit TEXT,
                    context TEXT
                );

                CREATE TABLE IF NOT EXISTS fixes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    priority INTEGER,
                    component TEXT,
                    issue TEXT,
                    recommended_fix TEXT,
                    status TEXT DEFAULT 'pending'
                );
            """)

    def setup_logging(self):
        """Setup comprehensive logging system."""
        log_file = self.log_dir / f"user_testing_{self.session_id}.log"

        # Configure logger
        self.logger = logging.getLogger(f"UserTesting_{self.session_id}")
        self.logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler (disabled to avoid Unicode issues on Windows)
        # console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        file_handler.setFormatter(formatter)
        # console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        # self.logger.addHandler(console_handler)  # Disabled to prevent Unicode errors

    def start_monitoring(self):
        """Start the monitoring system."""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.log_action("system", "monitoring_started", "UserTestingMonitor",
                       "User testing monitoring system started")

    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

        # Restore original exception handler
        sys.excepthook = self.original_excepthook

        self.generate_final_report()
        self.log_action("system", "monitoring_stopped", "UserTestingMonitor",
                       "User testing monitoring system stopped")

    def set_test_phase(self, phase: str):
        """Set the current testing phase."""
        self.current_test_phase = phase
        self.log_action("phase", "phase_change", "TestingPhase", f"Changed to phase: {phase}")
        print(f"📋 Testing Phase: {phase}")

    def log_action(self, action_type: str, action: str, component: str,
                   details: str, success: bool = True, duration_ms: float = 0):
        """Log a user action."""
        current_memory = self.process.memory_info().rss / 1024 / 1024

        action_data = {
            'timestamp': datetime.now().isoformat(),
            'phase': self.current_test_phase,
            'action_type': action_type,
            'action': action,
            'component': component,
            'details': details,
            'success': success,
            'duration_ms': duration_ms,
            'memory_mb': current_memory
        }

        self.actions_log.append(action_data)

        # Log to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO actions (phase, action_type, component, details, success, duration_ms, memory_mb)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (self.current_test_phase, f"{action_type}:{action}", component, details,
                  success, duration_ms, current_memory))

        status = "✅" if success else "❌"
        self.logger.info(f"{status} [{action_type}] {component}: {action} - {details}")

    def log_error(self, error_type: str, component: str, message: str,
                  severity: str = "medium", context: str = "", tb: str = ""):
        """Log an error with detailed information."""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'phase': self.current_test_phase,
            'error_type': error_type,
            'component': component,
            'message': message,
            'severity': severity,
            'context': context,
            'traceback': tb
        }

        self.errors_log.append(error_data)

        # Log to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO errors (phase, error_type, component, message, traceback, severity, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (self.current_test_phase, error_type, component, message, tb, severity, context))

        # Generate fix recommendation
        self.recommend_fix(component, message, severity)

        severity_emoji = {"low": "⚠️", "medium": "🚨", "high": "🔥", "critical": "💥"}
        emoji = severity_emoji.get(severity, "⚠️")
        self.logger.error(f"{emoji} [{severity.upper()}] {component}: {error_type} - {message}")

    def log_performance(self, metric_name: str, value: float, unit: str = "", context: str = ""):
        """Log performance metrics."""
        perf_data = {
            'timestamp': datetime.now().isoformat(),
            'phase': self.current_test_phase,
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'context': context
        }

        self.performance_log.append(perf_data)

        # Log to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO performance (phase, metric_name, value, unit, context)
                VALUES (?, ?, ?, ?, ?)
            """, (self.current_test_phase, metric_name, value, unit, context))

        self.logger.info(f"📊 Performance: {metric_name} = {value}{unit} ({context})")

    def recommend_fix(self, component: str, issue: str, severity: str):
        """Generate fix recommendations based on errors."""
        priority_map = {"low": 4, "medium": 3, "high": 2, "critical": 1}
        priority = priority_map.get(severity, 3)

        # Generate intelligent fix recommendations
        fix_recommendation = self._generate_fix_recommendation(component, issue)

        fix_data = {
            'timestamp': datetime.now().isoformat(),
            'priority': priority,
            'component': component,
            'issue': issue,
            'recommended_fix': fix_recommendation,
            'status': 'pending'
        }

        self.fixes_needed.append(fix_data)

        # Log to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO fixes (priority, component, issue, recommended_fix)
                VALUES (?, ?, ?, ?)
            """, (priority, component, issue, fix_recommendation))

    def _generate_fix_recommendation(self, component: str, issue: str) -> str:
        """Generate intelligent fix recommendations."""
        fix_patterns = {
            'FileCache': {
                'missing method': 'Add missing method to FileCache class with proper signature',
                'import error': 'Check import paths and ensure all dependencies are available',
                'memory': 'Implement memory cleanup and optimize cache size management'
            },
            'ProjectFileCache': {
                'file not found': 'Ensure project directory structure exists and files are created',
                'permission denied': 'Check file permissions and directory access rights',
                'encoding': 'Specify proper encoding (utf-8) for file operations'
            },
            'UI': {
                'widget error': 'Verify widget initialization and parent-child relationships',
                'layout': 'Check layout manager configuration and widget sizing',
                'event': 'Ensure event handlers are properly connected and configured'
            },
            'Database': {
                'connection': 'Verify database file exists and is accessible',
                'query': 'Check SQL syntax and table schema compatibility',
                'lock': 'Implement proper database connection management and timeouts'
            }
        }

        for comp_key, patterns in fix_patterns.items():
            if comp_key.lower() in component.lower():
                for pattern_key, fix in patterns.items():
                    if pattern_key.lower() in issue.lower():
                        return fix

        return f"Investigate {component} issue: {issue[:100]}... - Review code and add proper error handling"

    def exception_handler(self, exc_type, exc_value, exc_traceback):
        """Custom exception handler to capture all errors."""
        if issubclass(exc_type, KeyboardInterrupt):
            self.original_excepthook(exc_type, exc_value, exc_traceback)
            return

        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.log_error(
            error_type=exc_type.__name__,
            component="System",
            message=str(exc_value),
            severity="high",
            context=f"Unhandled exception in phase: {self.current_test_phase}",
            tb=tb_str
        )

        # Still call original handler
        self.original_excepthook(exc_type, exc_value, exc_traceback)

    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Monitor memory usage
                current_memory = self.process.memory_info().rss / 1024 / 1024
                memory_growth = current_memory - self.memory_baseline

                if memory_growth > 200:  # More than 200MB growth (increased threshold)
                    self.log_performance("memory_growth", memory_growth, "MB", "Significant memory growth")
                elif memory_growth > 500:  # More than 500MB growth
                    self.log_performance("memory_growth", memory_growth, "MB", "Potential memory leak")

                # Monitor CPU usage
                cpu_percent = self.process.cpu_percent()
                if cpu_percent > 80:
                    self.log_performance("cpu_usage", cpu_percent, "%", "High CPU usage detected")

                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")
                time.sleep(10)

    def generate_final_report(self):
        """Generate comprehensive final testing report."""
        end_time = datetime.now()
        duration = end_time - self.start_time

        report = {
            'session_info': {
                'session_id': self.session_id,
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_minutes': duration.total_seconds() / 60
            },
            'summary': {
                'total_actions': len(self.actions_log),
                'total_errors': len(self.errors_log),
                'total_fixes_needed': len(self.fixes_needed),
                'critical_issues': len([f for f in self.fixes_needed if f['priority'] == 1]),
                'success_rate': self._calculate_success_rate()
            },
            'detailed_results': {
                'actions': self.actions_log,
                'errors': self.errors_log,
                'performance': self.performance_log,
                'fixes': sorted(self.fixes_needed, key=lambda x: x['priority'])
            }
        }

        # Save detailed report
        report_file = self.log_dir / f"user_testing_report_{self.session_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Generate summary report
        self._generate_summary_report(report)

        print(f"📄 Final report saved: {report_file}")
        return report

    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        if not self.actions_log:
            return 0.0

        successful_actions = sum(1 for action in self.actions_log if action['success'])
        return (successful_actions / len(self.actions_log)) * 100

    def _generate_summary_report(self, report: Dict):
        """Generate human-readable summary report."""
        summary_file = self.log_dir / f"user_testing_summary_{self.session_id}.md"

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"""# User Testing Report - {self.session_id}

## Session Summary
- **Duration**: {report['session_info']['duration_minutes']:.1f} minutes
- **Total Actions**: {report['summary']['total_actions']}
- **Success Rate**: {report['summary']['success_rate']:.1f}%
- **Errors Found**: {report['summary']['total_errors']}
- **Fixes Needed**: {report['summary']['total_fixes_needed']}
- **Critical Issues**: {report['summary']['critical_issues']}

## Critical Issues (Priority 1)
""")

            critical_fixes = [f for f in report['detailed_results']['fixes'] if f['priority'] == 1]
            if critical_fixes:
                for fix in critical_fixes:
                    f.write(f"- **{fix['component']}**: {fix['issue']}\n")
                    f.write(f"  - *Fix*: {fix['recommended_fix']}\n\n")
            else:
                f.write("✅ No critical issues found!\n\n")

            f.write("## High Priority Issues (Priority 2)\n")
            high_fixes = [f for f in report['detailed_results']['fixes'] if f['priority'] == 2]
            if high_fixes:
                for fix in high_fixes:
                    f.write(f"- **{fix['component']}**: {fix['issue']}\n")
                    f.write(f"  - *Fix*: {fix['recommended_fix']}\n\n")
            else:
                f.write("✅ No high priority issues found!\n\n")

            f.write("## Error Summary by Component\n")
            error_by_component = {}
            for error in report['detailed_results']['errors']:
                comp = error['component']
                if comp not in error_by_component:
                    error_by_component[comp] = []
                error_by_component[comp].append(error)

            for component, errors in error_by_component.items():
                f.write(f"### {component} ({len(errors)} errors)\n")
                for error in errors:
                    f.write(f"- {error['error_type']}: {error['message']}\n")
                f.write("\n")

        print(f"📋 Summary report saved: {summary_file}")

# Global monitor instance
_user_monitor = None

def start_user_testing_monitor(session_id: str = None) -> UserTestingMonitor:
    """Start user testing monitoring."""
    global _user_monitor
    _user_monitor = UserTestingMonitor(session_id)
    _user_monitor.start_monitoring()
    return _user_monitor

def get_user_monitor() -> Optional[UserTestingMonitor]:
    """Get current user testing monitor."""
    return _user_monitor

def stop_user_testing_monitor():
    """Stop user testing monitoring."""
    global _user_monitor
    if _user_monitor:
        _user_monitor.stop_monitoring()
        _user_monitor = None

# Decorator for automatic action logging
def log_user_action(component: str, action_type: str = "user_action"):
    """Decorator to automatically log user actions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_user_monitor()
            if monitor:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000
                    monitor.log_action(action_type, func.__name__, component,
                                     f"Successfully executed {func.__name__}", True, duration)
                    return result
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    monitor.log_action(action_type, func.__name__, component,
                                     f"Failed to execute {func.__name__}: {e}", False, duration)
                    monitor.log_error("function_error", component, str(e), "medium",
                                    f"Error in {func.__name__}", traceback.format_exc())
                    raise
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test the monitoring system
    monitor = start_user_testing_monitor("test_session")
    monitor.set_test_phase("manual_testing")

    # Simulate some actions
    monitor.log_action("user", "click", "MainWindow", "User clicked main window")
    monitor.log_error("test_error", "TestComponent", "This is a test error", "medium")
    monitor.log_performance("response_time", 150.5, "ms", "Button click response")

    time.sleep(2)
    stop_user_testing_monitor()
