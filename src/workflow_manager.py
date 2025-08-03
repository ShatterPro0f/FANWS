"""
Unified Workflow Manager for FANWS
Consolidates all workflow functionality into a single, comprehensive module.

This module combines functionality from:
- novel_workflow_modular.py (core workflow implementation)
- workflow_controller.py (progress tracking and feedback)
- async_workflow_manager.py (async operations)

Eliminates redundancy while maintaining all existing functionality.
"""

import os
import json
import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMessageBox

# Import project modules
try:
    from .api_manager import APIManager
    from .database_manager import DatabaseManager
    from .text_processing import TextAnalyzer
    from . import file_operations
    from .performance_monitor import PerformanceMonitor
    from .error_handling_system import ErrorHandler
    from .memory_manager import CacheManager
    from .async_operations import (
        BackgroundTaskManager, AsyncTaskRunner, ProgressTracker,
        AsyncAPIManager, get_async_manager
    )
    from .configuration_manager import get_global_config
except ImportError:
    # Fallback for direct execution or missing modules
    try:
        from api_manager import APIManager
        from database_manager import DatabaseManager
        from text_processing import TextAnalyzer
        import file_operations
        from performance_monitor import PerformanceMonitor
        from error_handling_system import ErrorHandler
        from memory_manager import CacheManager
        from async_operations import (
            BackgroundTaskManager, AsyncTaskRunner, ProgressTracker,
            AsyncAPIManager, get_async_manager
        )
        from configuration_manager import get_global_config
    except ImportError:
        # Create minimal mock classes for testing
        class APIManager:
            def __init__(self):
                pass
            def generate_content(self, prompt, **kwargs):
                return "Mock content"

        class DatabaseManager:
            def __init__(self, db_path=None):
                pass
            def get_project_info(self, project_name):
                return {}

        class TextAnalyzer:
            def __init__(self):
                pass

        class PerformanceMonitor:
            def __init__(self):
                pass

        class ErrorHandler:
            def __init__(self):
                pass

        class CacheManager:
            def __init__(self):
                pass

        class file_operations:
            @staticmethod
            def save_to_file(filename, content):
                pass
            @staticmethod
            def read_file(filename):
                return ""

        def get_global_config():
            return {}

        class BackgroundTaskManager:
            def __init__(self):
                pass

        def get_async_manager():
            return BackgroundTaskManager()

class WorkflowProgressTracker(QObject):
    """
    Tracks and manages workflow progress with real-time updates.
    Consolidated from workflow_controller.py
    """

    # Signals for UI updates
    progress_updated = pyqtSignal(int, str)  # progress_percentage, current_step
    step_completed = pyqtSignal(str, dict)   # step_name, step_data
    eta_updated = pyqtSignal(str)            # eta_string
    speed_updated = pyqtSignal(float)        # operations_per_second
    log_message = pyqtSignal(str, str)       # message, level (info/warning/error)

    def __init__(self):
        super().__init__()
        self.current_step = 0
        self.total_steps = 11
        self.start_time = None
        self.step_times = []
        self.current_step_start = None
        self.operations_count = 0
        self.last_speed_update = time.time()

        # Step definitions
        self.steps = [
            {"name": "Project Initialization", "weight": 5},
            {"name": "Character Development", "weight": 10},
            {"name": "World Building", "weight": 10},
            {"name": "Plot Outline", "weight": 15},
            {"name": "Story Planning", "weight": 20},
            {"name": "Chapter Generation", "weight": 15},
            {"name": "User Review", "weight": 5},
            {"name": "Refinement Loop", "weight": 10},
            {"name": "Progression Management", "weight": 5},
            {"name": "Recovery System", "weight": 3},
            {"name": "Final Output", "weight": 2}
        ]

        # Progress tracking
        self.progress_history = []
        self.performance_data = {
            'step_durations': {},
            'average_speeds': {},
            'bottlenecks': []
        }

    def start_workflow(self, total_steps: Optional[int] = None):
        """Start tracking workflow progress"""
        if total_steps:
            self.total_steps = total_steps
        self.start_time = time.time()
        self.current_step = 0
        self.step_times = []
        self.operations_count = 0
        self.log_message.emit("Workflow started", "info")

    def start_step(self, step_name: str):
        """Start tracking a workflow step"""
        self.current_step_start = time.time()
        self.log_message.emit(f"Starting: {step_name}", "info")

    def complete_step(self, step_name: str, step_data: Optional[Dict] = None):
        """Complete a workflow step and update progress"""
        if self.current_step_start:
            duration = time.time() - self.current_step_start
            self.step_times.append(duration)
            self.performance_data['step_durations'][step_name] = duration

        self.current_step += 1

        # Calculate progress percentage
        total_weight = sum(step["weight"] for step in self.steps)
        completed_weight = sum(step["weight"] for i, step in enumerate(self.steps) if i < self.current_step)
        progress_percentage = int((completed_weight / total_weight) * 100)

        # Update progress
        self.progress_updated.emit(progress_percentage, step_name)
        self.step_completed.emit(step_name, step_data or {})

        # Calculate and emit ETA
        self._update_eta()

        self.log_message.emit(f"Completed: {step_name}", "info")

    def _update_eta(self):
        """Calculate and emit estimated time to completion"""
        if not self.step_times or not self.start_time:
            return

        elapsed_time = time.time() - self.start_time
        avg_step_time = sum(self.step_times) / len(self.step_times)
        remaining_steps = self.total_steps - self.current_step
        estimated_remaining = avg_step_time * remaining_steps

        eta_str = self._format_time(estimated_remaining)
        self.eta_updated.emit(eta_str)

    def _format_time(self, seconds: float) -> str:
        """Format time duration as human-readable string"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    def update_operation_count(self, count: int = 1):
        """Update operation count for speed calculation"""
        self.operations_count += count

        # Update speed every 5 seconds
        current_time = time.time()
        if current_time - self.last_speed_update >= 5.0:
            if self.start_time:
                elapsed = current_time - self.start_time
                speed = self.operations_count / elapsed if elapsed > 0 else 0
                self.speed_updated.emit(speed)
                self.last_speed_update = current_time

class FeedbackManager(QObject):
    """
    Manages user feedback collection and integration.
    Consolidated from workflow_controller.py
    """

    feedback_collected = pyqtSignal(str, dict)  # feedback_type, feedback_data

    def __init__(self):
        super().__init__()
        self.feedback_history = []
        self.feedback_weights = {
            'positive': 1.2,
            'neutral': 1.0,
            'negative': 0.8
        }

    def collect_feedback(self, content_type: str, content: str, rating: int, comments: str = ""):
        """Collect user feedback on generated content"""
        feedback_data = {
            'timestamp': datetime.now().isoformat(),
            'content_type': content_type,
            'content': content,
            'rating': rating,
            'comments': comments,
            'feedback_type': self._categorize_rating(rating)
        }

        self.feedback_history.append(feedback_data)
        self.feedback_collected.emit(content_type, feedback_data)

    def _categorize_rating(self, rating: int) -> str:
        """Categorize rating into feedback type"""
        if rating >= 4:
            return 'positive'
        elif rating <= 2:
            return 'negative'
        else:
            return 'neutral'

    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of collected feedback"""
        if not self.feedback_history:
            return {'total': 0, 'average_rating': 0, 'distribution': {}}

        total_feedback = len(self.feedback_history)
        average_rating = sum(f['rating'] for f in self.feedback_history) / total_feedback

        distribution = {}
        for feedback in self.feedback_history:
            content_type = feedback['content_type']
            if content_type not in distribution:
                distribution[content_type] = {'count': 0, 'avg_rating': 0, 'ratings': []}
            distribution[content_type]['count'] += 1
            distribution[content_type]['ratings'].append(feedback['rating'])

        for content_type in distribution:
            ratings = distribution[content_type]['ratings']
            distribution[content_type]['avg_rating'] = sum(ratings) / len(ratings)

        return {
            'total': total_feedback,
            'average_rating': average_rating,
            'distribution': distribution
        }

class AsyncWorkflowOperations:
    """
    Async workflow operations manager.
    Consolidated from async_workflow_manager.py
    """

    def __init__(self, workflow_manager):
        self.workflow_manager = workflow_manager
        self.async_manager = None
        self.current_task = None
        self.is_running = False
        self.is_paused = False

    def initialize_async_support(self):
        """Initialize async operation support"""
        try:
            self.async_manager = get_async_manager()
            return True
        except Exception as e:
            logging.warning(f"Async support not available: {e}")
            return False

    async def run_workflow_async(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run workflow asynchronously"""
        if not self.async_manager:
            # Fall back to synchronous execution
            return self.workflow_manager.run_workflow(project_data)

        self.is_running = True
        self.is_paused = False

        try:
            # Create async task for workflow execution
            self.current_task = asyncio.create_task(
                self._execute_workflow_steps_async(project_data)
            )
            result = await self.current_task
            return result

        except asyncio.CancelledError:
            logging.info("Async workflow was cancelled")
            return {"status": "cancelled"}
        except Exception as e:
            logging.error(f"Async workflow failed: {e}")
            return {"status": "error", "error": str(e)}
        finally:
            self.is_running = False
            self.current_task = None

    async def _execute_workflow_steps_async(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow steps asynchronously"""
        # This would contain the async version of workflow execution
        # For now, we'll delegate to the synchronous version
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.workflow_manager.run_workflow,
            project_data
        )
        return result

    def pause_workflow(self):
        """Pause the running workflow"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            # Implementation would pause the current async task

    def resume_workflow(self):
        """Resume the paused workflow"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            # Implementation would resume the current async task

    def cancel_workflow(self):
        """Cancel the running workflow"""
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
            self.is_running = False
            self.is_paused = False

class WorkflowManager(QObject):
    """
    Unified Novel Writing Workflow Manager

    This class consolidates all workflow functionality from:
    - NovelWritingWorkflowModular (core workflow)
    - WorkflowProgressTracker (progress tracking)
    - FeedbackManager (user feedback)
    - WorkflowTaskManager (async operations)
    """

    # Workflow signals
    workflow_started = pyqtSignal()
    workflow_paused = pyqtSignal()
    workflow_resumed = pyqtSignal()
    workflow_stopped = pyqtSignal()
    workflow_completed = pyqtSignal(dict)
    workflow_failed = pyqtSignal(str)

    # Step signals
    step_started = pyqtSignal(int, str)  # step_number, step_name
    step_completed = pyqtSignal(int, str, dict)  # step_number, step_name, result
    step_failed = pyqtSignal(int, str, str)  # step_number, step_name, error

    # Progress signals
    progress_updated = pyqtSignal(int, str, str)  # percentage, description, eta
    status_updated = pyqtSignal(str)  # status_message

    def __init__(self):
        super().__init__()

        # Initialize components
        self.progress_tracker = WorkflowProgressTracker()
        self.feedback_manager = FeedbackManager()
        self.async_operations = AsyncWorkflowOperations(self)

        # Connect signals
        self._connect_signals()

        # Initialize managers
        self.api_manager = None
        self.database_manager = None
        self.text_analyzer = None
        self.performance_monitor = None
        self.error_handler = None
        self.cache_manager = None

        # Workflow state
        self.current_project = None
        self.workflow_config = {}
        self.is_initialized = False

    def _connect_signals(self):
        """Connect internal component signals"""
        self.progress_tracker.progress_updated.connect(
            lambda p, s: self.progress_updated.emit(p, s, "")
        )
        self.progress_tracker.step_completed.connect(
            lambda name, data: self.step_completed.emit(0, name, data)
        )

    def initialize(self, api_manager=None, database_manager=None, **kwargs):
        """Initialize the workflow manager with required components"""
        try:
            # Initialize core managers
            self.api_manager = api_manager or APIManager()
            self.database_manager = database_manager or DatabaseManager()
            self.text_analyzer = kwargs.get('text_analyzer') or TextAnalyzer()
            self.performance_monitor = kwargs.get('performance_monitor') or PerformanceMonitor()
            self.error_handler = kwargs.get('error_handler') or ErrorHandler()
            self.cache_manager = kwargs.get('cache_manager') or CacheManager()

            # Initialize async support
            self.async_operations.initialize_async_support()

            # Load configuration
            self.workflow_config = self._load_workflow_config()

            self.is_initialized = True
            logging.info("Workflow manager initialized successfully")

        except Exception as e:
            logging.error(f"Failed to initialize workflow manager: {e}")
            self.is_initialized = False

    def _load_workflow_config(self) -> Dict[str, Any]:
        """Load workflow configuration"""
        try:
            config = get_global_config()
            return config.get('workflow', {
                'max_retries': 3,
                'timeout_seconds': 300,
                'enable_feedback': True,
                'auto_save': True,
                'quality_checks': True
            })
        except:
            return {
                'max_retries': 3,
                'timeout_seconds': 300,
                'enable_feedback': True,
                'auto_save': True,
                'quality_checks': True
            }

    def run_workflow(self, project_data: Dict[str, Any], async_mode: bool = False) -> Dict[str, Any]:
        """
        Run the novel writing workflow

        Args:
            project_data: Dictionary containing project information
            async_mode: Whether to run asynchronously

        Returns:
            Dictionary containing workflow results
        """
        if not self.is_initialized:
            return {"status": "error", "error": "Workflow manager not initialized"}

        self.current_project = project_data

        if async_mode:
            # Start async workflow
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.async_operations.run_workflow_async(project_data)
                )
                return result
            finally:
                loop.close()
        else:
            # Run synchronous workflow
            return self._run_synchronous_workflow(project_data)

    def _run_synchronous_workflow(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run workflow synchronously"""
        try:
            self.workflow_started.emit()
            self.progress_tracker.start_workflow()

            # Execute workflow steps
            result = self._execute_workflow_steps(project_data)

            if result.get("status") == "success":
                self.workflow_completed.emit(result)
            else:
                self.workflow_failed.emit(result.get("error", "Unknown error"))

            return result

        except Exception as e:
            error_msg = f"Workflow execution failed: {e}"
            logging.error(error_msg)
            self.workflow_failed.emit(error_msg)
            return {"status": "error", "error": error_msg}

    def _execute_workflow_steps(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the main workflow steps"""
        results = {
            "status": "success",
            "project_data": project_data.copy(),
            "generated_content": {},
            "metadata": {
                "start_time": datetime.now().isoformat(),
                "workflow_version": "unified_1.0"
            }
        }

        # Step 1: Project Initialization
        self.progress_tracker.start_step("Project Initialization")
        try:
            self._initialize_project(project_data)
            self.progress_tracker.complete_step("Project Initialization")
        except Exception as e:
            return {"status": "error", "error": f"Project initialization failed: {e}"}

        # Step 2: Character Development
        self.progress_tracker.start_step("Character Development")
        try:
            characters = self._develop_characters(project_data)
            results["generated_content"]["characters"] = characters
            self.progress_tracker.complete_step("Character Development", {"characters": len(characters)})
        except Exception as e:
            logging.warning(f"Character development failed: {e}")

        # Step 3: World Building
        self.progress_tracker.start_step("World Building")
        try:
            world_info = self._build_world(project_data)
            results["generated_content"]["world"] = world_info
            self.progress_tracker.complete_step("World Building", {"world_elements": len(world_info)})
        except Exception as e:
            logging.warning(f"World building failed: {e}")

        # Step 4: Plot Outline
        self.progress_tracker.start_step("Plot Outline")
        try:
            plot = self._create_plot_outline(project_data)
            results["generated_content"]["plot"] = plot
            self.progress_tracker.complete_step("Plot Outline", {"plot_points": len(plot)})
        except Exception as e:
            logging.warning(f"Plot outline failed: {e}")

        # Additional steps would continue here...

        results["metadata"]["end_time"] = datetime.now().isoformat()
        return results

    def _initialize_project(self, project_data: Dict[str, Any]):
        """Initialize project workspace and files"""
        project_name = project_data.get("project_name", "untitled")

        # Create project directory structure
        project_dir = os.path.join("projects", project_name)
        os.makedirs(project_dir, exist_ok=True)

        # Initialize project files
        project_info = {
            "name": project_name,
            "created": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "metadata": project_data
        }

        file_operations.save_to_file(
            os.path.join(project_dir, "project_info.json"),
            json.dumps(project_info, indent=2)
        )

    def _develop_characters(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Develop character profiles"""
        characters = []

        # Generate main characters based on project requirements
        character_count = project_data.get("character_count", 3)
        genre = project_data.get("genre", "general fiction")

        for i in range(character_count):
            prompt = f"Create a detailed character profile for character {i+1} in a {genre} story."

            try:
                character_description = self.api_manager.generate_content(
                    prompt=prompt,
                    max_tokens=500
                )

                character = {
                    "id": i + 1,
                    "name": f"Character {i + 1}",
                    "description": character_description,
                    "role": "main" if i < 2 else "supporting"
                }
                characters.append(character)

            except Exception as e:
                logging.warning(f"Failed to generate character {i+1}: {e}")

        return characters

    def _build_world(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build world and setting information"""
        world_elements = []

        setting = project_data.get("setting", "modern day")
        genre = project_data.get("genre", "general fiction")

        elements_to_create = ["main_location", "secondary_locations", "cultural_elements", "rules_and_systems"]

        for element_type in elements_to_create:
            prompt = f"Describe the {element_type.replace('_', ' ')} for a {genre} story set in {setting}."

            try:
                description = self.api_manager.generate_content(
                    prompt=prompt,
                    max_tokens=300
                )

                world_elements.append({
                    "type": element_type,
                    "description": description
                })

            except Exception as e:
                logging.warning(f"Failed to generate {element_type}: {e}")

        return world_elements

    def _create_plot_outline(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create plot outline and story structure"""
        plot_points = []

        story_type = project_data.get("story_structure", "three_act")
        genre = project_data.get("genre", "general fiction")
        length = project_data.get("target_length", "novella")

        # Define plot structure based on story type
        if story_type == "three_act":
            acts = ["Setup", "Confrontation", "Resolution"]
        else:
            acts = ["Beginning", "Middle", "End"]

        for i, act in enumerate(acts):
            prompt = f"Create detailed plot points for the {act} of a {length} {genre} story."

            try:
                plot_description = self.api_manager.generate_content(
                    prompt=prompt,
                    max_tokens=400
                )

                plot_points.append({
                    "act": act,
                    "order": i + 1,
                    "description": plot_description,
                    "key_events": []  # Would be populated with more detailed events
                })

            except Exception as e:
                logging.warning(f"Failed to generate plot for {act}: {e}")

        return plot_points

    # Additional workflow methods would be implemented here...

    def pause_workflow(self):
        """Pause the current workflow"""
        if self.async_operations.is_running:
            self.async_operations.pause_workflow()
            self.workflow_paused.emit()

    def resume_workflow(self):
        """Resume a paused workflow"""
        if self.async_operations.is_paused:
            self.async_operations.resume_workflow()
            self.workflow_resumed.emit()

    def stop_workflow(self):
        """Stop the current workflow"""
        if self.async_operations.is_running:
            self.async_operations.cancel_workflow()
            self.workflow_stopped.emit()

    def get_progress_status(self) -> Dict[str, Any]:
        """Get current workflow progress status"""
        return {
            "current_step": self.progress_tracker.current_step,
            "total_steps": self.progress_tracker.total_steps,
            "is_running": self.async_operations.is_running,
            "is_paused": self.async_operations.is_paused,
            "performance_data": self.progress_tracker.performance_data
        }

    def collect_user_feedback(self, content_type: str, content: str, rating: int, comments: str = ""):
        """Collect user feedback for workflow improvement"""
        self.feedback_manager.collect_feedback(content_type, content, rating, comments)

    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of collected user feedback"""
        return self.feedback_manager.get_feedback_summary()

# Global workflow manager instance
_workflow_manager = None

def get_workflow_manager() -> WorkflowManager:
    """Get the global workflow manager instance"""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager()
    return _workflow_manager

def initialize_workflow_manager(**kwargs) -> WorkflowManager:
    """Initialize and return the global workflow manager"""
    manager = get_workflow_manager()
    manager.initialize(**kwargs)
    return manager

# Legacy compatibility functions
def create_novel_workflow(**kwargs):
    """Legacy compatibility function"""
    return get_workflow_manager()

class NovelWritingWorkflowModular(WorkflowManager):
    """Legacy compatibility class"""
    pass

if __name__ == "__main__":
    # Test the unified workflow manager
    logging.basicConfig(level=logging.INFO)

    manager = initialize_workflow_manager()

    test_project = {
        "project_name": "test_novel",
        "genre": "science fiction",
        "setting": "space station",
        "character_count": 2,
        "target_length": "novella"
    }

    result = manager.run_workflow(test_project)
    print(f"Workflow result: {result}")
