"""
Asynchronous Operations Framework for FANWS
Priority 4.1: Eliminate UI freezing during long-running operations

This module provides a comprehensive asynchronous operations framework that replaces
the blocking QThread-based approach with proper async/await patterns and QRunnable
tasks for better thread management.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from PyQt5.QtCore import (
    QObject, QRunnable, QThreadPool, QTimer, pyqtSignal, pyqtSlot,
    QMutex, QWaitCondition, QEventLoop
)
from PyQt5.QtWidgets import QProgressBar, QLabel, QWidget, QVBoxLayout, QProgressDialog

from ..core.error_handling_system import ErrorHandler
from ..database.database_manager import DatabaseManager
from ..core.performance_monitor import PerformanceMonitor

class AsyncTaskSignals(QObject):
    """Signals for async task communication."""

    # Task progress signals
    progress_updated = pyqtSignal(int, str)  # progress_percentage, description
    status_updated = pyqtSignal(str)  # status_message

    # Task completion signals
    task_completed = pyqtSignal(object)  # result
    task_failed = pyqtSignal(str)  # error_message

    # Content signals
    content_generated = pyqtSignal(str, str)  # filename, content

    # API signals
    api_limit_reached = pyqtSignal(str)  # message
    api_request_completed = pyqtSignal(dict)  # response_data

    # Log signals
    log_message = pyqtSignal(str, str)  # message, level

class AsyncTaskRunner(QRunnable):
    """
    QRunnable-based task runner for non-blocking operations.

    This replaces the QThread-based approach with proper QRunnable tasks
    that don't block the UI thread.
    """

    def __init__(self, task_func: Callable, *args, **kwargs):
        """
        Initialize async task runner.

        Args:
            task_func: The function to run asynchronously
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        """
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.signals = AsyncTaskSignals()
        self.is_cancelled = False
        self.task_id = f"task_{int(time.time() * 1000)}"

        # Performance monitoring
        self.start_time = None
        self.end_time = None

        # Error handling
        self.error_handler = ErrorHandler()

        logging.info(f"AsyncTaskRunner initialized: {self.task_id}")

    def run(self):
        """Execute the task."""
        try:
            self.start_time = time.time()
            self.signals.status_updated.emit(f"Starting task: {self.task_id}")

            # Check if task is already cancelled
            if self.is_cancelled:
                self.signals.status_updated.emit("Task cancelled before execution")
                return

            # Execute the task
            if asyncio.iscoroutinefunction(self.task_func):
                # Handle async functions
                result = asyncio.run(self._run_async())
            else:
                # Handle regular functions
                result = self.task_func(*self.args, **self.kwargs)

            if not self.is_cancelled:
                self.end_time = time.time()
                execution_time = self.end_time - self.start_time

                self.signals.task_completed.emit(result)
                self.signals.status_updated.emit(f"Task completed in {execution_time:.2f}s")

                logging.info(f"Task {self.task_id} completed successfully in {execution_time:.2f}s")

        except Exception as e:
            self.error_handler.handle_error(e, context=f"AsyncTaskRunner.run - {self.task_id}")
            error_msg = f"Task {self.task_id} failed: {str(e)}"
            self.signals.task_failed.emit(error_msg)
            self.signals.log_message.emit(error_msg, "error")
            logging.error(error_msg)

    async def _run_async(self):
        """Run async task function."""
        return await self.task_func(*self.args, **self.kwargs)

    def cancel(self):
        """Cancel the task."""
        self.is_cancelled = True
        self.signals.status_updated.emit(f"Task {self.task_id} cancelled")
        logging.info(f"Task {self.task_id} cancelled")

class ProgressTracker(QObject):
    """
    Progress tracker for long-running operations.

    Provides real-time progress updates and ETA calculations.
    """

    progress_updated = pyqtSignal(int, str, str)  # percentage, description, eta
    speed_updated = pyqtSignal(float)  # operations_per_second

    def __init__(self, total_operations: int = 100):
        """Initialize progress tracker."""
        super().__init__()
        self.total_operations = total_operations
        self.completed_operations = 0
        self.start_time = None
        self.operation_times = []
        self.last_update = time.time()

        # Timer for periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)  # Update every second

    def start(self):
        """Start progress tracking."""
        self.start_time = time.time()
        self.completed_operations = 0
        self.operation_times = []
        self.progress_updated.emit(0, "Starting...", "Calculating...")
        logging.info("Progress tracking started")

    def update_progress(self, completed: int, description: str = ""):
        """Update progress with completed operations."""
        self.completed_operations = completed
        percentage = min(int((completed / self.total_operations) * 100), 100)

        # Calculate ETA
        eta = self.calculate_eta()

        self.progress_updated.emit(percentage, description, eta)

        # Record operation time
        current_time = time.time()
        if self.start_time:
            self.operation_times.append(current_time - self.last_update)
            # Keep only recent times for accuracy
            if len(self.operation_times) > 100:
                self.operation_times = self.operation_times[-100:]

        self.last_update = current_time

    def calculate_eta(self) -> str:
        """Calculate estimated time to completion."""
        if not self.start_time or self.completed_operations == 0:
            return "Calculating..."

        elapsed_time = time.time() - self.start_time
        remaining_operations = self.total_operations - self.completed_operations

        if remaining_operations <= 0:
            return "Complete"

        # Calculate average time per operation
        avg_time_per_operation = elapsed_time / self.completed_operations
        estimated_remaining_time = avg_time_per_operation * remaining_operations

        # Format time
        if estimated_remaining_time < 60:
            return f"{int(estimated_remaining_time)}s"
        elif estimated_remaining_time < 3600:
            minutes = int(estimated_remaining_time // 60)
            seconds = int(estimated_remaining_time % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(estimated_remaining_time // 3600)
            minutes = int((estimated_remaining_time % 3600) // 60)
            return f"{hours}h {minutes}m"

    def update_metrics(self):
        """Update speed metrics."""
        if self.operation_times:
            avg_operation_time = sum(self.operation_times) / len(self.operation_times)
            operations_per_second = 1.0 / avg_operation_time if avg_operation_time > 0 else 0
            self.speed_updated.emit(operations_per_second)

    def complete(self):
        """Mark progress as complete."""
        self.timer.stop()
        self.progress_updated.emit(100, "Complete", "0s")
        logging.info("Progress tracking completed")

class BackgroundTaskManager(QObject):
    """
    Manager for asynchronous operations.

    Coordinates multiple async tasks and provides centralized management
    of thread pool and task execution.
    """

    # Manager signals
    manager_started = pyqtSignal()
    manager_stopped = pyqtSignal()
    task_queued = pyqtSignal(str)  # task_id
    all_tasks_completed = pyqtSignal()

    def __init__(self, max_workers: int = 4):
        """Initialize async operations manager."""
        super().__init__()

        # Thread pool for task execution
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(max_workers)

        # Task management
        self.active_tasks = {}  # task_id -> AsyncTaskRunner
        self.completed_tasks = {}  # task_id -> result
        self.failed_tasks = {}  # task_id -> error_message

        # Task queue
        self.task_queue = []

        # Performance monitoring
        self.performance_monitor = None

        # Database manager for persistence
        self.db_manager = DatabaseManager()

        # Thread synchronization
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()

        logging.info(f"BackgroundTaskManager initialized with {max_workers} max workers")

    def set_performance_monitor(self, monitor: PerformanceMonitor):
        """Set performance monitor."""
        self.performance_monitor = monitor

    def start_manager(self):
        """Start the async operations manager."""
        self.manager_started.emit()
        logging.info("BackgroundTaskManager started")

    def stop_manager(self):
        """Stop the async operations manager."""
        # Cancel all active tasks
        for task_id, task in self.active_tasks.items():
            task.cancel()

        # Wait for thread pool to finish
        self.thread_pool.waitForDone(5000)  # Wait up to 5 seconds

        self.manager_stopped.emit()
        logging.info("BackgroundTaskManager stopped")

    def cleanup(self):
        """Clean up resources and stop the manager."""
        self.stop_manager()

    def submit_task(self, task_func: Callable, *args, **kwargs) -> str:
        """
        Submit a task for asynchronous execution.

        Args:
            task_func: The function to execute asynchronously
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            str: Task ID for tracking
        """
        # Create task runner
        task_runner = AsyncTaskRunner(task_func, *args, **kwargs)
        task_id = task_runner.task_id

        # Connect signals
        task_runner.signals.task_completed.connect(
            lambda result: self._on_task_completed(task_id, result)
        )
        task_runner.signals.task_failed.connect(
            lambda error: self._on_task_failed(task_id, error)
        )

        # Store task
        self.active_tasks[task_id] = task_runner

        # Submit to thread pool
        self.thread_pool.start(task_runner)

        # Performance monitoring
        if self.performance_monitor:
            self.performance_monitor.log_event(
                "task_submitted",
                f"Task {task_id} submitted for execution"
            )

        self.task_queued.emit(task_id)
        logging.info(f"Task {task_id} submitted for execution")

        return task_id

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.cancel()

            # Move to failed tasks
            self.failed_tasks[task_id] = "Task cancelled by user"
            del self.active_tasks[task_id]

            logging.info(f"Task {task_id} cancelled")
            return True

        return False

    def get_task_status(self, task_id: str) -> str:
        """Get the status of a task."""
        if task_id in self.active_tasks:
            return "running"
        elif task_id in self.completed_tasks:
            return "completed"
        elif task_id in self.failed_tasks:
            return "failed"
        else:
            return "unknown"

    def get_task_result(self, task_id: str) -> Any:
        """Get the result of a completed task."""
        return self.completed_tasks.get(task_id)

    def get_active_task_count(self) -> int:
        """Get the number of active tasks."""
        return len(self.active_tasks)

    def get_thread_pool_info(self) -> Dict[str, Any]:
        """Get thread pool information."""
        return {
            'max_threads': self.thread_pool.maxThreadCount(),
            'active_threads': self.thread_pool.activeThreadCount(),
            'pending_tasks': len(self.active_tasks)
        }

    @pyqtSlot(str, object)
    def _on_task_completed(self, task_id: str, result: Any):
        """Handle task completion."""
        if task_id in self.active_tasks:
            # Move to completed tasks
            self.completed_tasks[task_id] = result
            del self.active_tasks[task_id]

            # Performance monitoring
            if self.performance_monitor:
                self.performance_monitor.log_event(
                    "task_completed",
                    f"Task {task_id} completed successfully"
                )

            # Check if all tasks are completed
            if not self.active_tasks:
                self.all_tasks_completed.emit()

            logging.info(f"Task {task_id} completed successfully")

    @pyqtSlot(str, str)
    def _on_task_failed(self, task_id: str, error_message: str):
        """Handle task failure."""
        if task_id in self.active_tasks:
            # Move to failed tasks
            self.failed_tasks[task_id] = error_message
            del self.active_tasks[task_id]

            # Performance monitoring
            if self.performance_monitor:
                self.performance_monitor.log_event(
                    "task_failed",
                    f"Task {task_id} failed: {error_message}"
                )

            logging.error(f"Task {task_id} failed: {error_message}")

class AsyncAPIManager(QObject):
    """
    Asynchronous API manager for non-blocking API calls.

    Provides async/await patterns for all API interactions to prevent UI freezing.
    """

    # API signals
    api_response_received = pyqtSignal(str, dict)  # request_id, response
    api_error_occurred = pyqtSignal(str, str)  # request_id, error_message
    api_limit_reached = pyqtSignal(str)  # message

    def __init__(self, api_manager):
        """Initialize async API manager."""
        super().__init__()
        self.api_manager = api_manager
        self.active_requests = {}
        self.request_queue = []

        # Async operations manager
        self.async_manager = BackgroundTaskManager()

        logging.info("AsyncAPIManager initialized")

    async def generate_text_async(self, prompt: str, max_tokens: int = 1000,
                                 api_key: str = None, model: str = "gpt-4") -> str:
        """
        Generate text asynchronously.

        Args:
            prompt: The prompt for text generation
            max_tokens: Maximum tokens to generate
            api_key: API key for the request
            model: Model to use for generation

        Returns:
            str: Generated text
        """
        request_id = f"generate_text_{int(time.time() * 1000)}"

        try:
            # Submit async task
            task_id = self.async_manager.submit_task(
                self._generate_text_task,
                prompt, max_tokens, api_key, model, request_id
            )

            # Wait for task completion (non-blocking)
            result = await self._wait_for_task_completion(task_id)

            if isinstance(result, str) and result.startswith("ERROR:"):
                raise Exception(result[6:])  # Remove "ERROR:" prefix

            return result

        except Exception as e:
            error_msg = f"Async text generation failed: {str(e)}"
            self.api_error_occurred.emit(request_id, error_msg)
            raise

    def _generate_text_task(self, prompt: str, max_tokens: int, api_key: str,
                           model: str, request_id: str) -> str:
        """Task function for text generation."""
        try:
            # Use existing API manager for actual generation
            result = self.api_manager.generate_text_openai(prompt, max_tokens, api_key)

            if result == "API_LIMIT_REACHED":
                self.api_limit_reached.emit("OpenAI API limit reached")
                return "API_LIMIT_REACHED"

            self.api_response_received.emit(request_id, {"result": result})
            return result

        except Exception as e:
            error_msg = f"Text generation task failed: {str(e)}"
            self.api_error_occurred.emit(request_id, error_msg)
            return f"ERROR:{error_msg}"

    async def _wait_for_task_completion(self, task_id: str, timeout: int = 30) -> Any:
        """Wait for task completion with timeout."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.async_manager.get_task_status(task_id)

            if status == "completed":
                return self.async_manager.get_task_result(task_id)
            elif status == "failed":
                error = self.async_manager.failed_tasks.get(task_id, "Unknown error")
                raise Exception(error)

            # Small delay to prevent busy waiting
            await asyncio.sleep(0.1)

        # Timeout reached
        self.async_manager.cancel_task(task_id)
        raise TimeoutError(f"Task {task_id} timed out after {timeout} seconds")

class AsyncProgressDialog(QProgressDialog):
    """
    Async-aware progress dialog for long-running operations.

    Provides non-blocking progress indication with cancel support.
    """

    def __init__(self, parent=None, title="Processing...", description="Please wait..."):
        """Initialize async progress dialog."""
        super().__init__(description, "Cancel", 0, 100, parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumDuration(0)

        # Progress tracking
        self.progress_tracker = None
        self.task_id = None

        # Connect cancel button
        self.canceled.connect(self.cancel_operation)

    def set_progress_tracker(self, tracker: ProgressTracker):
        """Set progress tracker."""
        self.progress_tracker = tracker

        # Connect signals
        tracker.progress_updated.connect(self.update_progress)
        tracker.speed_updated.connect(self.update_speed)

    def set_task_id(self, task_id: str):
        """Set task ID for cancellation."""
        self.task_id = task_id

    @pyqtSlot(int, str, str)
    def update_progress(self, percentage: int, description: str, eta: str):
        """Update progress display."""
        self.setValue(percentage)
        self.setLabelText(f"{description}\nETA: {eta}")

    @pyqtSlot(float)
    def update_speed(self, speed: float):
        """Update speed display."""
        if speed > 0:
            self.setLabelText(f"{self.labelText()}\nSpeed: {speed:.2f} ops/sec")

    def cancel_operation(self):
        """Cancel the current operation."""
        if self.task_id:
            # Cancel through async manager
            # This would need to be connected to the appropriate manager
            logging.info(f"Cancelling operation: {self.task_id}")

# Global async operations manager instance
_async_manager = None

def get_async_manager() -> BackgroundTaskManager:
    """Get global async operations manager."""
    global _async_manager
    if _async_manager is None:
        _async_manager = BackgroundTaskManager()
        _async_manager.start_manager()
    return _async_manager

# Convenience functions for common async operations
async def run_async_task(task_func: Callable, *args, **kwargs) -> Any:
    """Run a task asynchronously and return the result."""
    manager = get_async_manager()
    task_id = manager.submit_task(task_func, *args, **kwargs)

    # Wait for completion
    while manager.get_task_status(task_id) == "running":
        await asyncio.sleep(0.1)

    status = manager.get_task_status(task_id)
    if status == "completed":
        return manager.get_task_result(task_id)
    elif status == "failed":
        error = manager.failed_tasks.get(task_id, "Unknown error")
        raise Exception(error)
    else:
        raise Exception(f"Task {task_id} in unexpected state: {status}")

def submit_background_task(task_func: Callable, *args, **kwargs) -> str:
    """Submit a task to run in the background."""
    manager = get_async_manager()
    return manager.submit_task(task_func, *args, **kwargs)

def cancel_background_task(task_id: str) -> bool:
    """Cancel a background task."""
    manager = get_async_manager()
    return manager.cancel_task(task_id)

class AsyncManager:
    """High-level async manager class for compatibility."""

    def __init__(self):
        self.async_manager = get_async_manager()

    def submit_task(self, task_func: Callable, *args, **kwargs) -> str:
        """Submit a task for async execution."""
        return self.async_manager.submit_task(task_func, *args, **kwargs)

    def get_task_status(self, task_id: str) -> str:
        """Get the status of a task."""
        return self.async_manager.get_task_status(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        return self.async_manager.cancel_task(task_id)

class AsyncWorkflowHandler:
    """Handles asynchronous workflow operations."""

    def __init__(self):
        self.async_manager = get_async_manager()
        self.active_workflows = {}

    def start_workflow(self, workflow_func: Callable, *args, **kwargs) -> str:
        """Start an asynchronous workflow."""
        return self.async_manager.submit_task(workflow_func, *args, **kwargs)

    def stop_workflow(self, workflow_id: str) -> bool:
        """Stop a running workflow."""
        return self.async_manager.cancel_task(workflow_id)

    def get_workflow_status(self, workflow_id: str) -> str:
        """Get the status of a workflow."""
        return self.async_manager.get_task_status(workflow_id)
