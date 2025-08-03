#!/usr/bin/env python3
"""
Base Step Class for Novel Writing Workflow
Provides common functionality for all workflow steps.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod

class BaseWorkflowStep(ABC):
    """
    Abstract base class for all workflow steps.
    Provides common functionality and interface.
    """

    def __init__(self, workflow_instance):
        """Initialize the base step with reference to main workflow."""
        self.workflow = workflow_instance
        self.step_name = self.__class__.__name__
        self.step_number = self.get_step_number()
        self.start_time = None
        self.end_time = None
        self.errors = []
        self.warnings = []

    def get_step_number(self):
        """Extract step number from class name."""
        import re
        match = re.search(r'Step(\d+)', self.__class__.__name__)
        return int(match.group(1)) if match else 0

    def log_action(self, message: str, level: str = "INFO"):
        """Log an action for this step."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Step {self.step_number} - {self.step_name}: {message}"

        if level == "ERROR":
            logging.error(log_entry)
            self.errors.append(message)
        elif level == "WARNING":
            logging.warning(log_entry)
            self.warnings.append(message)
        else:
            logging.info(log_entry)

        # Also log to workflow instance if available
        if hasattr(self.workflow, 'log_action'):
            self.workflow.log_action(f"Step {self.step_number}: {message}")

    def start_step(self):
        """Mark the start of step execution."""
        self.start_time = datetime.now()
        self.errors.clear()
        self.warnings.clear()
        self.log_action(f"Starting {self.step_name}")

        # Emit signal if workflow has it
        if hasattr(self.workflow, 'status_updated'):
            self.workflow.status_updated.emit(f"Starting Step {self.step_number}: {self.step_name}")

    def end_step(self, success: bool = True):
        """Mark the end of step execution."""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds() if self.start_time else 0

        status = "completed successfully" if success else "failed"
        self.log_action(f"Step {self.step_name} {status} in {duration:.2f} seconds")

        # Emit signal if workflow has it
        if hasattr(self.workflow, 'step_completed'):
            self.workflow.step_completed.emit(self.step_number, {
                'success': success,
                'duration': duration,
                'errors': self.errors,
                'warnings': self.warnings
            })

        return success

    def save_step_data(self, data: Dict[str, Any]):
        """Save step-specific data to project directory."""
        try:
            step_data_file = os.path.join(
                self.workflow.project_path,
                f"step_{self.step_number:02d}_data.json"
            )

            with open(step_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.log_action(f"Step data saved to {step_data_file}")
            return True

        except Exception as e:
            self.log_action(f"Error saving step data: {e}", "ERROR")
            return False

    def load_step_data(self) -> Dict[str, Any]:
        """Load step-specific data from project directory."""
        try:
            step_data_file = os.path.join(
                self.workflow.project_path,
                f"step_{self.step_number:02d}_data.json"
            )

            if os.path.exists(step_data_file):
                with open(step_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.log_action(f"Step data loaded from {step_data_file}")
                return data
            else:
                self.log_action(f"No step data file found at {step_data_file}")
                return {}

        except Exception as e:
            self.log_action(f"Error loading step data: {e}", "ERROR")
            return {}

    def validate_prerequisites(self) -> bool:
        """Validate that prerequisites for this step are met."""
        # Check if project path exists
        if not self.workflow.project_path or not os.path.exists(self.workflow.project_path):
            self.log_action("Project path not found", "ERROR")
            return False

        # Check if previous steps completed (if not step 1)
        if self.step_number > 1:
            previous_step_file = os.path.join(
                self.workflow.project_path,
                f"step_{self.step_number-1:02d}_data.json"
            )
            if not os.path.exists(previous_step_file):
                self.log_action(f"Previous step data not found: {previous_step_file}", "ERROR")
                return False

        return True

    def handle_error(self, error: Exception, context: str = ""):
        """Handle errors that occur during step execution."""
        error_msg = f"Error in {context}: {str(error)}"
        self.log_action(error_msg, "ERROR")

        # Use workflow's error handler if available
        if hasattr(self.workflow, 'error_handler'):
            self.workflow.error_handler.handle_error(error, context)

        # Emit error signal if available
        if hasattr(self.workflow, 'error_occurred'):
            self.workflow.error_occurred.emit(error_msg)

    def update_progress(self, percentage: int):
        """Update progress for this step."""
        if hasattr(self.workflow, 'progress_updated'):
            self.workflow.progress_updated.emit(percentage)

    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the main logic of this step.
        Must be implemented by each step class.
        Returns True if successful, False otherwise.
        """
        pass

    def run(self) -> bool:
        """
        Run the complete step workflow.
        This is the main entry point for step execution.
        """
        self.start_step()

        try:
            # Validate prerequisites
            if not self.validate_prerequisites():
                self.log_action("Prerequisites not met", "ERROR")
                return self.end_step(False)

            # Execute the step
            success = self.execute()

            return self.end_step(success)

        except Exception as e:
            self.handle_error(e, "step execution")
            return self.end_step(False)

    def get_step_summary(self) -> Dict[str, Any]:
        """Get a summary of this step's execution."""
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()

        return {
            'step_number': self.step_number,
            'step_name': self.step_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': duration,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings
        }
