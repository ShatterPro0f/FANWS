"""
Workflow Coordinator - Integrates existing workflow_steps system
Replaces workflow_manager.py with proper integration to workflow_steps
Includes plugin system integration for extensible workflows
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

# Import the existing workflow step system
try:
    from ..plugins.plugin_workflow_integration import WorkflowStepManager
    from ..plugins.plugin_workflow_integration import BaseWorkflowStep
    from ..plugins.plugin_manager import create_plugin_manager, PluginType
except ImportError:
    try:
        from ..core.configuration_manager import WorkflowStepManager
        from workflow_steps.base_step import BaseWorkflowStep
        from ..plugins.plugin_manager import create_plugin_manager, PluginType
    except ImportError:
        # Fallback if plugin system not available
        def create_plugin_manager():
            return None
        class PluginType:
            WORKFLOW_STEP = "workflow_step"
            CONTENT_GENERATOR = "content_generator"

class WorkflowCoordinator(QObject):
    """
    Coordinates the execution of workflow steps using the existing workflow_steps system.
    This replaces the workflow_manager.py with proper integration.
    """

    # Workflow signals for UI integration
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
    progress_updated = pyqtSignal(int, str)  # percentage, description
    status_updated = pyqtSignal(str)  # status_message

    def __init__(self):
        super().__init__()

        # Initialize the step manager
        self.step_manager = None
        self.plugin_manager = None
        self.is_initialized = False
        self.is_running = False
        self.is_paused = False
        self.current_step = 0
        self.total_steps = 11  # Based on the 11 workflow steps

        # Project data
        self.project_name = None
        self.project_path = None
        self.project_data = {}

        # Don't initialize immediately to avoid hanging
        # initialize() will be called when needed

    def initialize(self):
        """Initialize the workflow coordinator"""
        if self.is_initialized:
            return True

        try:
            # Initialize plugin system first
            self.plugin_manager = create_plugin_manager()
            if self.plugin_manager:
                logging.info("Plugin system initialized for workflow")

            # Create step manager with this coordinator as the workflow instance
            self.step_manager = WorkflowStepManager(self)
            self.total_steps = len(self.step_manager.step_order)

            # Check for workflow plugin steps
            self._integrate_workflow_plugins()

            self.is_initialized = True

            logging.info("Workflow coordinator initialized successfully")
            return True

        except Exception as e:
            logging.error(f"Failed to initialize workflow coordinator: {e}")
            self.is_initialized = False
            return False

    def set_project_data(self, project_name: str, project_data: Dict[str, Any]):
        """Set project data for the workflow"""
        self.project_name = project_name
        self.project_data = project_data
        self.project_path = os.path.join("projects", project_name)

        # Ensure project directory exists
        os.makedirs(self.project_path, exist_ok=True)

    def _integrate_workflow_plugins(self):
        """Integrate workflow plugins with the step system"""
        if not self.plugin_manager:
            return

        try:
            # Get workflow step plugins
            workflow_plugins = self.plugin_manager.get_plugins_by_type(PluginType.WORKFLOW_STEP)

            for plugin_info in workflow_plugins:
                plugin_instance = self.plugin_manager.get_plugin_by_name(plugin_info.name)
                if plugin_instance:
                    # Set the workflow reference for the plugin
                    if hasattr(plugin_instance, 'set_workflow'):
                        plugin_instance.set_workflow(self)
                    logging.info(f"Integrated workflow plugin: {plugin_info.name}")

        except Exception as e:
            logging.error(f"Failed to integrate workflow plugins: {e}")

    def get_available_content_generators(self) -> List[Any]:
        """Get available content generator plugins"""
        if not self.plugin_manager:
            return []

        return self.plugin_manager.get_plugins_by_type(PluginType.CONTENT_GENERATOR)

    def get_available_export_formats(self) -> List[Any]:
        """Get available export format plugins"""
        if not self.plugin_manager:
            return []

        return self.plugin_manager.get_plugins_by_type(PluginType.EXPORT_FORMAT)

    def execute_plugin_content_generation(self, plugin_name: str, prompt: str, context: Dict[str, Any]) -> Optional[str]:
        """Execute a content generator plugin"""
        if not self.plugin_manager:
            return None

        return self.plugin_manager.execute_plugin_method(plugin_name, 'generate_content', prompt, context)

    def execute_plugin_export(self, plugin_name: str, content: str, metadata: Dict[str, Any], output_path: str) -> bool:
        """Execute an export format plugin"""
        if not self.plugin_manager:
            return False

        result = self.plugin_manager.execute_plugin_method(plugin_name, 'export', content, metadata, output_path)
        return result if isinstance(result, bool) else False

    def start_workflow(self, project_data: Optional[Dict[str, Any]] = None) -> bool:
        """Start the workflow execution"""
        if not self.is_initialized:
            if not self.initialize():
                logging.error("Cannot start workflow: initialization failed")
                return False

        if self.is_running:
            logging.warning("Workflow is already running")
            return False

        try:
            # Set project data if provided
            if project_data:
                project_name = project_data.get('project_name', 'default')
                self.set_project_data(project_name, project_data)

            # Start workflow execution
            self.is_running = True
            self.current_step = 0

            # Emit started signal
            self.workflow_started.emit()
            self.status_updated.emit("Starting workflow...")

            # Execute all steps
            success = self.step_manager.execute_all_steps()

            if success:
                self.workflow_completed.emit({"status": "success", "project_data": self.project_data})
                self.status_updated.emit("Workflow completed successfully")
            else:
                self.workflow_failed.emit("Workflow execution failed")
                self.status_updated.emit("Workflow failed")

            self.is_running = False
            return success

        except Exception as e:
            self.is_running = False
            error_msg = f"Workflow execution error: {e}"
            logging.error(error_msg)
            self.workflow_failed.emit(error_msg)
            return False

    def execute_step(self, step_number: int) -> bool:
        """Execute a specific workflow step"""
        if not self.is_initialized:
            return False

        try:
            step = self.step_manager.get_step(step_number)
            if not step:
                logging.error(f"Step {step_number} not found")
                return False

            # Emit step started signal
            self.step_started.emit(step_number, step.step_name)
            self.status_updated.emit(f"Executing {step.step_name}...")

            # Update progress
            progress = int((step_number / self.total_steps) * 100)
            self.progress_updated.emit(progress, f"Step {step_number}: {step.step_name}")

            # Execute the step
            success = self.step_manager.execute_step(step_number)

            if success:
                self.step_completed.emit(step_number, step.step_name, {})
                logging.info(f"Step {step_number} ({step.step_name}) completed successfully")
            else:
                error_msg = f"Step {step_number} ({step.step_name}) failed"
                self.step_failed.emit(step_number, step.step_name, error_msg)
                logging.error(error_msg)

            return success

        except Exception as e:
            error_msg = f"Error executing step {step_number}: {e}"
            logging.error(error_msg)
            self.step_failed.emit(step_number, "", error_msg)
            return False

    def pause_workflow(self):
        """Pause the workflow execution"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.workflow_paused.emit()
            self.status_updated.emit("Workflow paused")

    def resume_workflow(self):
        """Resume the paused workflow"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            self.workflow_resumed.emit()
            self.status_updated.emit("Workflow resumed")

    def stop_workflow(self):
        """Stop the workflow execution"""
        if self.is_running:
            self.is_running = False
            self.is_paused = False
            self.workflow_stopped.emit()
            self.status_updated.emit("Workflow stopped")

    def get_workflow_steps(self) -> List[Dict[str, Any]]:
        """Get list of all workflow steps"""
        if not self.is_initialized:
            # Return basic step info without initializing
            return [
                {'number': i+1, 'name': f'Step {i+1}', 'description': '', 'status': 'pending'}
                for i in range(self.total_steps)
            ]

        steps = []
        for step_number in self.step_manager.step_order:
            step = self.step_manager.get_step(step_number)
            if step:
                steps.append({
                    'number': step_number,
                    'name': step.step_name,
                    'description': getattr(step, '__doc__', ''),
                    'status': 'pending'
                })

        return steps

    def get_progress_status(self) -> Dict[str, Any]:
        """Get current workflow progress status"""
        return {
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "project_name": self.project_name,
            "project_path": self.project_path
        }

    # Legacy compatibility methods for workflow_manager.py replacement
    def run_workflow(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy compatibility method"""
        success = self.start_workflow(project_data)
        if success:
            return {"status": "success", "project_data": project_data}
        else:
            return {"status": "error", "error": "Workflow execution failed"}

    def initialize_from_config(self, config: Dict[str, Any]):
        """Legacy compatibility method for config initialization"""
        # The step-based system doesn't need explicit config initialization
        # as each step handles its own configuration
        pass

    # Properties for compatibility with existing code
    @property
    def total_chapters(self):
        """Get total chapters from project data"""
        return self.project_data.get('total_chapters', 10)

    @property
    def sections_per_chapter(self):
        """Get sections per chapter from project data"""
        return self.project_data.get('sections_per_chapter', 5)

    def generate_section_content(self, chapter: int, section: int) -> str:
        """Generate content for a specific section"""
        # This would be handled by the appropriate workflow step
        # For now, return a placeholder
        return f"Content for Chapter {chapter}, Section {section}"

# Global workflow coordinator instance
_workflow_coordinator = None

def get_workflow_coordinator() -> WorkflowCoordinator:
    """Get the global workflow coordinator instance"""
    global _workflow_coordinator
    if _workflow_coordinator is None:
        _workflow_coordinator = WorkflowCoordinator()
    return _workflow_coordinator

def create_novel_workflow() -> WorkflowCoordinator:
    """Legacy compatibility function"""
    return get_workflow_coordinator()

# Legacy compatibility class
class NovelWritingWorkflowModular(WorkflowCoordinator):
    """Legacy compatibility class that extends WorkflowCoordinator"""
    pass

# For compatibility with existing imports
WorkflowManager = WorkflowCoordinator
AsyncWorkflowOperations = WorkflowCoordinator  # Simplified for now

if __name__ == "__main__":
    # Test the workflow coordinator
    logging.basicConfig(level=logging.INFO)

    coordinator = WorkflowCoordinator()

    test_project = {
        "project_name": "test_novel",
        "genre": "science fiction",
        "setting": "space station",
        "character_count": 2,
        "target_length": "novella"
    }

    result = coordinator.run_workflow(test_project)
    print(f"Workflow result: {result}")
