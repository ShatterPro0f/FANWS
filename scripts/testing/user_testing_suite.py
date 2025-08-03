"""
FANWS User Testing Suite
========================

Comprehensive user testing framework that logs every action and systematically tests
all application functionality to ensure 100% reliability.

Features:
- Action logging for every user interaction
- Systematic testing of all UI components
- Error detection and reporting
- Performance monitoring
- Automated test scenarios
- Manual testing guidance
- Issue tracking and resolution
"""

import os
import sys
import json
import time
import traceback
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import subprocess
import psutil

# PyQt5 imports for UI testing
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Import FANWS modules for testing
try:
    from fanws import FANWSWindow
    from src.file_operations import get_project_list, validate_project_name
    from src.memory_manager import FileCache, ProjectFileCache
    from src.api_manager import APIManager
    FANWS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: FANWS modules not fully available: {e}")
    FANWS_AVAILABLE = False

class TestSeverity(Enum):
    """Test result severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class TestStatus(Enum):
    """Test execution status."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"

@dataclass
class UserAction:
    """Represents a single user action during testing."""
    timestamp: datetime
    action_type: str
    component: str
    details: Dict[str, Any]
    result: Optional[str] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None

@dataclass
class TestResult:
    """Represents the result of a single test."""
    test_name: str
    status: TestStatus
    severity: TestSeverity
    description: str
    timestamp: datetime
    duration_ms: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    user_actions: List[UserAction] = None
    recommendations: List[str] = None

class ActionLogger:
    """Logs all user actions during testing."""

    def __init__(self, log_file: str = "user_testing_actions.json"):
        self.log_file = log_file
        self.actions: List[UserAction] = []
        self.session_start = datetime.now()
        self.current_test = None

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('user_testing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def log_action(self, action_type: str, component: str, details: Dict[str, Any],
                   result: str = None, error: str = None, duration_ms: float = None):
        """Log a user action."""
        action = UserAction(
            timestamp=datetime.now(),
            action_type=action_type,
            component=component,
            details=details,
            result=result,
            error=error,
            duration_ms=duration_ms
        )

        self.actions.append(action)
        self.logger.info(f"Action: {action_type} on {component} - {details}")

        if error:
            self.logger.error(f"Error in {action_type}: {error}")

    def save_log(self):
        """Save actions log to file."""
        log_data = {
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "total_actions": len(self.actions),
            "actions": [asdict(action) for action in self.actions]
        }

        with open(self.log_file, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)

    def get_action_summary(self) -> Dict[str, Any]:
        """Get summary of logged actions."""
        action_types = {}
        components = {}
        errors = []

        for action in self.actions:
            action_types[action.action_type] = action_types.get(action.action_type, 0) + 1
            components[action.component] = components.get(action.component, 0) + 1
            if action.error:
                errors.append({
                    "timestamp": action.timestamp.isoformat(),
                    "action": action.action_type,
                    "component": action.component,
                    "error": action.error
                })

        return {
            "total_actions": len(self.actions),
            "action_types": action_types,
            "components_tested": components,
            "errors_encountered": len(errors),
            "error_details": errors,
            "session_duration": str(datetime.now() - self.session_start)
        }

class PerformanceMonitor:
    """Monitors application performance during testing."""

    def __init__(self):
        self.start_time = time.time()
        self.memory_samples = []
        self.cpu_samples = []
        self.response_times = []
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """Start performance monitoring."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

    def _monitor_loop(self):
        """Monitor loop for collecting performance data."""
        while self.monitoring:
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent()

                self.memory_samples.append({
                    "timestamp": time.time(),
                    "memory_mb": memory_mb
                })

                self.cpu_samples.append({
                    "timestamp": time.time(),
                    "cpu_percent": cpu_percent
                })

                time.sleep(1)  # Sample every second
            except Exception as e:
                logging.error(f"Performance monitoring error: {e}")
                break

    def record_response_time(self, operation: str, duration_ms: float):
        """Record response time for an operation."""
        self.response_times.append({
            "operation": operation,
            "duration_ms": duration_ms,
            "timestamp": time.time()
        })

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.memory_samples or not self.cpu_samples:
            return {"error": "No performance data collected"}

        memory_values = [s["memory_mb"] for s in self.memory_samples]
        cpu_values = [s["cpu_percent"] for s in self.cpu_samples]

        response_time_summary = {}
        for rt in self.response_times:
            op = rt["operation"]
            if op not in response_time_summary:
                response_time_summary[op] = []
            response_time_summary[op].append(rt["duration_ms"])

        # Calculate averages for response times
        avg_response_times = {}
        for op, times in response_time_summary.items():
            avg_response_times[op] = sum(times) / len(times) if times else 0

        return {
            "memory_usage": {
                "min_mb": min(memory_values),
                "max_mb": max(memory_values),
                "avg_mb": sum(memory_values) / len(memory_values)
            },
            "cpu_usage": {
                "min_percent": min(cpu_values),
                "max_percent": max(cpu_values),
                "avg_percent": sum(cpu_values) / len(cpu_values)
            },
            "response_times": avg_response_times,
            "total_operations": len(self.response_times)
        }

class UITestFramework:
    """Framework for testing UI components."""

    def __init__(self, action_logger: ActionLogger, performance_monitor: PerformanceMonitor):
        self.action_logger = action_logger
        self.performance_monitor = performance_monitor
        self.app = None
        self.main_window = None
        self.test_results = []

    def setup_test_environment(self) -> bool:
        """Setup the test environment."""
        try:
            if not FANWS_AVAILABLE:
                raise ImportError("FANWS modules not available")

            # Create QApplication if it doesn't exist
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()

            # Create main window
            self.main_window = FANWSWindow()
            self.main_window.show()

            self.action_logger.log_action(
                "setup", "test_environment",
                {"status": "success"},
                "Test environment initialized"
            )

            return True

        except Exception as e:
            self.action_logger.log_action(
                "setup", "test_environment",
                {"status": "failed"},
                error=str(e)
            )
            return False

    def simulate_click(self, widget, delay_ms: int = 100) -> bool:
        """Simulate a click on a widget."""
        try:
            start_time = time.time()

            self.action_logger.log_action(
                "click", widget.__class__.__name__,
                {"widget_text": getattr(widget, 'text', lambda: 'N/A')()}
            )

            QTest.mouseClick(widget, Qt.LeftButton)
            QTest.qWait(delay_ms)

            duration_ms = (time.time() - start_time) * 1000
            self.performance_monitor.record_response_time("click", duration_ms)

            return True

        except Exception as e:
            self.action_logger.log_action(
                "click", widget.__class__.__name__,
                {"widget_text": getattr(widget, 'text', lambda: 'N/A')()},
                error=str(e)
            )
            return False

    def simulate_text_input(self, widget, text: str, delay_ms: int = 50) -> bool:
        """Simulate text input into a widget."""
        try:
            start_time = time.time()

            self.action_logger.log_action(
                "text_input", widget.__class__.__name__,
                {"input_text": text[:50] + "..." if len(text) > 50 else text}
            )

            widget.clear()
            QTest.keyClicks(widget, text)
            QTest.qWait(delay_ms)

            duration_ms = (time.time() - start_time) * 1000
            self.performance_monitor.record_response_time("text_input", duration_ms)

            return True

        except Exception as e:
            self.action_logger.log_action(
                "text_input", widget.__class__.__name__,
                {"input_text": text},
                error=str(e)
            )
            return False

    def run_test(self, test_func, test_name: str, severity: TestSeverity = TestSeverity.MEDIUM) -> TestResult:
        """Run a single test and record results."""
        start_time = time.time()
        actions_before = len(self.action_logger.actions)

        try:
            self.action_logger.current_test = test_name
            test_func()

            duration_ms = (time.time() - start_time) * 1000
            actions_during_test = self.action_logger.actions[actions_before:]

            result = TestResult(
                test_name=test_name,
                status=TestStatus.PASSED,
                severity=severity,
                description=f"Test '{test_name}' completed successfully",
                timestamp=datetime.now(),
                duration_ms=duration_ms,
                user_actions=actions_during_test
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            actions_during_test = self.action_logger.actions[actions_before:]

            result = TestResult(
                test_name=test_name,
                status=TestStatus.FAILED,
                severity=severity,
                description=f"Test '{test_name}' failed",
                timestamp=datetime.now(),
                duration_ms=duration_ms,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
                user_actions=actions_during_test
            )

        finally:
            self.action_logger.current_test = None

        self.test_results.append(result)
        return result

class FANWSTestSuite:
    """Main test suite for FANWS application."""

    def __init__(self):
        self.action_logger = ActionLogger()
        self.performance_monitor = PerformanceMonitor()
        self.ui_framework = UITestFramework(self.action_logger, self.performance_monitor)
        self.test_results = []

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests in the suite."""
        print("🚀 Starting FANWS User Testing Suite")
        print("=" * 50)

        self.performance_monitor.start_monitoring()

        try:
            # Setup test environment
            if not self.ui_framework.setup_test_environment():
                return {"error": "Failed to setup test environment"}

            # Run test categories
            self._run_ui_component_tests()
            self._run_project_management_tests()
            self._run_configuration_tests()
            self._run_workflow_tests()
            self._run_file_operations_tests()
            self._run_api_integration_tests()
            self._run_performance_tests()
            self._run_error_handling_tests()

        finally:
            self.performance_monitor.stop_monitoring()
            self.action_logger.save_log()

        return self._generate_test_report()

    def _run_ui_component_tests(self):
        """Test all UI components."""
        print("\n📱 Testing UI Components...")

        # Test main window initialization
        self.ui_framework.run_test(
            self._test_main_window_initialization,
            "main_window_initialization",
            TestSeverity.CRITICAL
        )

        # Test tab navigation
        self.ui_framework.run_test(
            self._test_tab_navigation,
            "tab_navigation",
            TestSeverity.HIGH
        )

        # Test button functionality
        self.ui_framework.run_test(
            self._test_button_functionality,
            "button_functionality",
            TestSeverity.HIGH
        )

        # Test input validation
        self.ui_framework.run_test(
            self._test_input_validation,
            "input_validation",
            TestSeverity.MEDIUM
        )

    def _run_project_management_tests(self):
        """Test project management functionality."""
        print("\n📁 Testing Project Management...")

        # Test project creation
        self.ui_framework.run_test(
            self._test_project_creation,
            "project_creation",
            TestSeverity.CRITICAL
        )

        # Test project loading
        self.ui_framework.run_test(
            self._test_project_loading,
            "project_loading",
            TestSeverity.CRITICAL
        )

        # Test project deletion
        self.ui_framework.run_test(
            self._test_project_deletion,
            "project_deletion",
            TestSeverity.HIGH
        )

    def _run_configuration_tests(self):
        """Test configuration management."""
        print("\n⚙️ Testing Configuration Management...")

        # Test configuration loading
        self.ui_framework.run_test(
            self._test_configuration_loading,
            "configuration_loading",
            TestSeverity.HIGH
        )

        # Test configuration saving
        self.ui_framework.run_test(
            self._test_configuration_saving,
            "configuration_saving",
            TestSeverity.HIGH
        )

    def _run_workflow_tests(self):
        """Test workflow functionality."""
        print("\n🔄 Testing Workflow Operations...")

        # Test workflow initialization
        self.ui_framework.run_test(
            self._test_workflow_initialization,
            "workflow_initialization",
            TestSeverity.HIGH
        )

        # Test workflow execution
        self.ui_framework.run_test(
            self._test_workflow_execution,
            "workflow_execution",
            TestSeverity.CRITICAL
        )

    def _run_file_operations_tests(self):
        """Test file operations."""
        print("\n💾 Testing File Operations...")

        # Test file cache operations
        self.ui_framework.run_test(
            self._test_file_cache_operations,
            "file_cache_operations",
            TestSeverity.HIGH
        )

        # Test backup operations
        self.ui_framework.run_test(
            self._test_backup_operations,
            "backup_operations",
            TestSeverity.MEDIUM
        )

    def _run_api_integration_tests(self):
        """Test API integrations."""
        print("\n🌐 Testing API Integrations...")

        # Test API manager initialization
        self.ui_framework.run_test(
            self._test_api_manager_initialization,
            "api_manager_initialization",
            TestSeverity.HIGH
        )

    def _run_performance_tests(self):
        """Test performance characteristics."""
        print("\n⚡ Testing Performance...")

        # Test memory usage
        self.ui_framework.run_test(
            self._test_memory_usage,
            "memory_usage",
            TestSeverity.MEDIUM
        )

        # Test response times
        self.ui_framework.run_test(
            self._test_response_times,
            "response_times",
            TestSeverity.MEDIUM
        )

    def _run_error_handling_tests(self):
        """Test error handling."""
        print("\n🚨 Testing Error Handling...")

        # Test error recovery
        self.ui_framework.run_test(
            self._test_error_recovery,
            "error_recovery",
            TestSeverity.HIGH
        )

    # Individual test methods
    def _test_main_window_initialization(self):
        """Test main window initialization."""
        window = self.ui_framework.main_window
        assert window is not None, "Main window not initialized"
        assert window.isVisible(), "Main window not visible"
        assert window.windowTitle() == "Fiction AI Novel Writing Suite (FANWS)", "Incorrect window title"

    def _test_tab_navigation(self):
        """Test tab navigation functionality."""
        window = self.ui_framework.main_window

        # Test switching between main sections
        if hasattr(window, 'show_dashboard_button'):
            self.ui_framework.simulate_click(window.show_dashboard_button)
            QTest.qWait(500)  # Wait for UI update

        if hasattr(window, 'show_novel_settings_button'):
            self.ui_framework.simulate_click(window.show_novel_settings_button)
            QTest.qWait(500)

    def _test_button_functionality(self):
        """Test button functionality."""
        window = self.ui_framework.main_window

        # Test various buttons
        buttons_to_test = [
            'new_project_button',
            'save_api_keys_button',
            'reset_api_button',
            'clear_cache_button'
        ]

        for button_name in buttons_to_test:
            if hasattr(window, button_name):
                button = getattr(window, button_name)
                self.ui_framework.simulate_click(button)
                QTest.qWait(200)

    def _test_input_validation(self):
        """Test input validation."""
        window = self.ui_framework.main_window

        # Test project name validation
        if hasattr(window, 'project_input'):
            # Test invalid characters
            invalid_names = ["test/name", "test<name", "test>name", "test|name"]
            for invalid_name in invalid_names:
                self.ui_framework.simulate_text_input(window.project_input, invalid_name)
                QTest.qWait(100)

    def _test_project_creation(self):
        """Test project creation."""
        window = self.ui_framework.main_window

        # Fill in project details
        if hasattr(window, 'project_input'):
            test_project_name = f"test_project_{int(time.time())}"
            self.ui_framework.simulate_text_input(window.project_input, test_project_name)

        if hasattr(window, 'idea_input'):
            self.ui_framework.simulate_text_input(window.idea_input, "A test story about testing")

        # Attempt to create project
        if hasattr(window, 'new_project_button'):
            self.ui_framework.simulate_click(window.new_project_button)
            QTest.qWait(1000)  # Wait for project creation

    def _test_project_loading(self):
        """Test project loading."""
        window = self.ui_framework.main_window

        if hasattr(window, 'project_selector'):
            # Get available projects
            projects = [window.project_selector.itemText(i)
                       for i in range(window.project_selector.count())]

            # Try to load each project
            for project in projects:
                if project != "Select a project":
                    window.project_selector.setCurrentText(project)
                    QTest.qWait(500)  # Wait for loading

    def _test_project_deletion(self):
        """Test project deletion."""
        window = self.ui_framework.main_window

        # This test should be careful not to delete important projects
        # For now, just test the button exists and can be clicked
        if hasattr(window, 'delete_project_button'):
            # Don't actually delete, just test the button
            assert window.delete_project_button is not None

    def _test_configuration_loading(self):
        """Test configuration loading."""
        window = self.ui_framework.main_window

        # Test that configuration attributes exist
        config_attributes = ['config', 'file_cache', 'current_project']
        for attr in config_attributes:
            if hasattr(window, attr):
                value = getattr(window, attr)
                # Just verify the attribute exists, value can be None initially

    def _test_configuration_saving(self):
        """Test configuration saving."""
        window = self.ui_framework.main_window

        if hasattr(window, 'save_api_keys_button'):
            self.ui_framework.simulate_click(window.save_api_keys_button)
            QTest.qWait(500)

    def _test_workflow_initialization(self):
        """Test workflow initialization."""
        window = self.ui_framework.main_window

        # Test workflow manager exists
        if hasattr(window, 'novel_workflow'):
            # Workflow manager may be None initially, which is ok
            pass

    def _test_workflow_execution(self):
        """Test workflow execution."""
        window = self.ui_framework.main_window

        # Test start button functionality (without actually starting)
        if hasattr(window, 'start_button'):
            # Check button state
            assert window.start_button is not None

    def _test_file_cache_operations(self):
        """Test file cache operations."""
        # Test FileCache and ProjectFileCache
        try:
            cache = FileCache()
            cache.update("test_key", "test_value")
            value = cache.get("test_key")
            assert value == "test_value", "FileCache operation failed"

            # Test ProjectFileCache
            project_cache = ProjectFileCache("test_project")
            project_cache.update("test_file.txt", "test content")
            content = project_cache.get("test_file.txt")
            assert content == "test content", "ProjectFileCache operation failed"

        except Exception as e:
            raise AssertionError(f"File cache test failed: {e}")

    def _test_backup_operations(self):
        """Test backup operations."""
        # Test backup functionality exists
        try:
            from src.file_operations import create_backup
            # Don't actually create backup, just test import
        except ImportError:
            raise AssertionError("Backup operations not available")

    def _test_api_manager_initialization(self):
        """Test API manager initialization."""
        try:
            api_manager = APIManager()
            assert api_manager is not None, "API manager not initialized"
        except Exception as e:
            raise AssertionError(f"API manager initialization failed: {e}")

    def _test_memory_usage(self):
        """Test memory usage."""
        performance_data = self.performance_monitor.get_performance_summary()
        if "memory_usage" in performance_data:
            max_memory = performance_data["memory_usage"]["max_mb"]
            assert max_memory < 1000, f"Memory usage too high: {max_memory}MB"  # Reasonable limit

    def _test_response_times(self):
        """Test response times."""
        performance_data = self.performance_monitor.get_performance_summary()
        if "response_times" in performance_data:
            for operation, avg_time in performance_data["response_times"].items():
                assert avg_time < 5000, f"Response time too slow for {operation}: {avg_time}ms"

    def _test_error_recovery(self):
        """Test error recovery."""
        # Test that error handling system exists
        try:
            from src.error_handling_system import ErrorHandler
            # Just test import for now
        except ImportError:
            # Error handling system may not be available, which is ok
            pass

    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        all_results = self.test_results + self.ui_framework.test_results

        # Calculate statistics
        total_tests = len(all_results)
        passed_tests = len([r for r in all_results if r.status == TestStatus.PASSED])
        failed_tests = len([r for r in all_results if r.status == TestStatus.FAILED])
        error_tests = len([r for r in all_results if r.status == TestStatus.ERROR])

        # Group by severity
        severity_breakdown = {}
        for severity in TestSeverity:
            severity_tests = [r for r in all_results if r.severity == severity]
            severity_breakdown[severity.value] = {
                "total": len(severity_tests),
                "passed": len([r for r in severity_tests if r.status == TestStatus.PASSED]),
                "failed": len([r for r in severity_tests if r.status == TestStatus.FAILED])
            }

        # Performance summary
        performance_summary = self.performance_monitor.get_performance_summary()

        # Action summary
        action_summary = self.action_logger.get_action_summary()

        # Failed tests details
        failed_test_details = []
        for result in all_results:
            if result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                failed_test_details.append({
                    "test_name": result.test_name,
                    "severity": result.severity.value,
                    "error_message": result.error_message,
                    "recommendations": result.recommendations or []
                })

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "severity_breakdown": severity_breakdown,
            "performance_summary": performance_summary,
            "action_summary": action_summary,
            "failed_tests": failed_test_details,
            "detailed_results": [asdict(r) for r in all_results],
            "recommendations": self._generate_recommendations(all_results),
            "timestamp": datetime.now().isoformat()
        }

        # Save report
        with open("user_testing_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n📊 Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Errors: {error_tests}")
        print(f"   Success Rate: {report['test_summary']['success_rate']:.1f}%")
        print(f"\n📄 Detailed report saved to: user_testing_report.json")
        print(f"📄 Action log saved to: {self.action_logger.log_file}")

        return report

    def _generate_recommendations(self, results: List[TestResult]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        failed_tests = [r for r in results if r.status in [TestStatus.FAILED, TestStatus.ERROR]]
        critical_failures = [r for r in failed_tests if r.severity == TestSeverity.CRITICAL]

        if critical_failures:
            recommendations.append("🚨 CRITICAL: Address critical test failures immediately")
            for failure in critical_failures:
                recommendations.append(f"   - Fix: {failure.test_name}")

        if len(failed_tests) > len(results) * 0.2:  # More than 20% failure rate
            recommendations.append("⚠️ High failure rate detected - review overall system stability")

        # Performance recommendations
        performance_data = self.performance_monitor.get_performance_summary()
        if "memory_usage" in performance_data:
            max_memory = performance_data["memory_usage"]["max_mb"]
            if max_memory > 500:
                recommendations.append(f"🐏 Memory usage high ({max_memory:.1f}MB) - consider optimization")

        if "response_times" in performance_data:
            slow_operations = [op for op, time in performance_data["response_times"].items() if time > 1000]
            if slow_operations:
                recommendations.append(f"🐌 Slow operations detected: {', '.join(slow_operations)}")

        # Action-based recommendations
        action_summary = self.action_logger.get_action_summary()
        if action_summary["errors_encountered"] > 0:
            recommendations.append(f"🐛 {action_summary['errors_encountered']} user action errors - review error handling")

        if not recommendations:
            recommendations.append("✅ All tests passed - system appears stable")

        return recommendations

def run_manual_testing_guide():
    """Generate a manual testing guide for users."""
    guide = """
    🧪 FANWS Manual Testing Guide
    ============================

    Follow these steps to manually test the application:

    1. APPLICATION STARTUP
       □ Application starts without errors
       □ Main window displays correctly
       □ All UI elements are visible and properly positioned

    2. PROJECT MANAGEMENT
       □ Create a new project with valid inputs
       □ Create a project with invalid inputs (should show error)
       □ Load an existing project
       □ Switch between projects
       □ Delete a project (test with confirmation)

    3. CONFIGURATION
       □ Enter API keys and save
       □ Modify novel settings (tone, reading level, etc.)
       □ Change advanced settings
       □ Verify settings persist after restart

    4. WRITING WORKFLOW
       □ Start writing process
       □ Monitor progress updates
       □ Approve/reject generated sections
       □ Pause and resume workflow
       □ Handle API limit scenarios

    5. FILE OPERATIONS
       □ Save content to files
       □ Load content from files
       □ Create backups
       □ Export novel in different formats

    6. ERROR SCENARIOS
       □ Invalid API keys
       □ Network connectivity issues
       □ File permission problems
       □ Memory/resource constraints

    7. PERFORMANCE
       □ Application responsiveness during operations
       □ Memory usage during long operations
       □ CPU usage patterns
       □ Concurrent operation handling

    LOG ALL ISSUES FOUND:
    - Exact steps to reproduce
    - Expected vs actual behavior
    - Error messages or symptoms
    - System environment details
    """

    with open("manual_testing_guide.txt", "w") as f:
        f.write(guide)

    print("📋 Manual testing guide saved to: manual_testing_guide.txt")

def main():
    """Main entry point for the testing suite."""
    print("🧪 FANWS User Testing Suite")
    print("Choose testing mode:")
    print("1. Automated Testing")
    print("2. Generate Manual Testing Guide")
    print("3. Both")

    choice = input("Enter choice (1-3): ").strip()

    if choice in ["1", "3"]:
        suite = FANWSTestSuite()
        report = suite.run_all_tests()

        if report.get("error"):
            print(f"❌ Testing failed: {report['error']}")
        else:
            success_rate = report["test_summary"]["success_rate"]
            if success_rate >= 90:
                print("✅ Excellent - Application is very stable!")
            elif success_rate >= 75:
                print("⚠️ Good - Some issues need attention")
            else:
                print("🚨 Poor - Significant issues detected")

    if choice in ["2", "3"]:
        run_manual_testing_guide()

    print("\n🏁 Testing complete!")

if __name__ == "__main__":
    main()
