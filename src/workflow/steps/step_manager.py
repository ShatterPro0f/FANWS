#!/usr/bin/env python3
"""
Step Manager for Novel Writing Workflow
Manages the execution and coordination of all workflow steps.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Type, Any

# Import all step classes
try:
    from ...plugins.plugin_workflow_integration import Step01Initialization
    from ...plugins.plugin_workflow_integration import Step02SynopsisGeneration
    from ...plugins.plugin_workflow_integration import Step03SynopsisRefinement
    from ...plugins.plugin_workflow_integration import Step04StructuralPlanning
    from ...plugins.plugin_workflow_integration import Step05TimelineSynchronization
    from ...plugins.plugin_workflow_integration import Step06IterativeWriting
    from ...plugins.plugin_workflow_integration import Step07UserReview
    from ...plugins.plugin_workflow_integration import Step08RefinementLoop
    from ...plugins.plugin_workflow_integration import Step09ProgressionManagement
    from ...plugins.plugin_workflow_integration import Step10Recovery
    from ...plugins.plugin_workflow_integration import Step11CompletionExport
except ImportError:
    # Fallback for direct execution
    from step_01_initialization import Step01Initialization
    from step_02_synopsis_generation import Step02SynopsisGeneration
    from step_03_synopsis_refinement import Step03SynopsisRefinement
    from step_04_structural_planning import Step04StructuralPlanning
    from step_05_timeline_synchronization import Step05TimelineSynchronization
    from step_06_iterative_writing import Step06IterativeWriting
    from step_07_user_review import Step07UserReview
    from step_08_refinement_loop import Step08RefinementLoop
    from step_09_progression_management import Step09ProgressionManagement
    from step_10_recovery import Step10Recovery
    from step_11_completion_export import Step11CompletionExport

class WorkflowStepManager:
    """
    Manages the execution and coordination of all workflow steps.
    Provides a centralized interface for step management.
    """

    def __init__(self, workflow_instance):
        """Initialize the step manager with workflow instance."""
        self.workflow = workflow_instance
        self.steps = {}
        self.step_order = []
        self.current_step_number = 0
        self.execution_history = []

        # Register all steps
        self._register_steps()

    def _register_steps(self):
        """Register all workflow steps."""
        step_classes = [
            Step01Initialization,
            Step02SynopsisGeneration,
            Step03SynopsisRefinement,
            Step04StructuralPlanning,
            Step05TimelineSynchronization,
            Step06IterativeWriting,
            Step07UserReview,
            Step08RefinementLoop,
            Step09ProgressionManagement,
            Step10Recovery,
            Step11CompletionExport
        ]

        for step_class in step_classes:
            try:
                step_instance = step_class(self.workflow)
                step_number = step_instance.step_number
                self.steps[step_number] = step_instance
                self.step_order.append(step_number)

                logging.info(f"Registered {step_class.__name__} as step {step_number}")

            except Exception as e:
                logging.error(f"Failed to register {step_class.__name__}: {e}")

        # Sort step order
        self.step_order.sort()

    def get_step(self, step_number: int):
        """Get a specific step by number."""
        return self.steps.get(step_number)

    def get_all_steps(self) -> List:
        """Get all registered steps in order."""
        return [self.steps[num] for num in self.step_order if num in self.steps]

    def execute_step(self, step_number: int) -> bool:
        """Execute a specific step."""
        step = self.get_step(step_number)
        if not step:
            logging.error(f"Step {step_number} not found")
            return False

        self.current_step_number = step_number

        # Record execution start
        execution_record = {
            'step_number': step_number,
            'start_time': datetime.now().isoformat(),
            'success': False,
            'end_time': None,
            'errors': [],
            'warnings': []
        }

        try:
            # Execute the step
            success = step.run()

            # Record execution end
            execution_record['success'] = success
            execution_record['end_time'] = datetime.now().isoformat()
            execution_record['errors'] = step.errors
            execution_record['warnings'] = step.warnings

            # Add to history
            self.execution_history.append(execution_record)

            # Save execution history
            self._save_execution_history()

            return success

        except Exception as e:
            execution_record['end_time'] = datetime.now().isoformat()
            execution_record['errors'].append(str(e))
            self.execution_history.append(execution_record)
            self._save_execution_history()

            logging.error(f"Error executing step {step_number}: {e}")
            return False

    def execute_all_steps(self) -> bool:
        """Execute all steps in order."""
        logging.info("Starting execution of all workflow steps")

        all_successful = True

        for step_number in self.step_order:
            logging.info(f"Executing step {step_number}")

            success = self.execute_step(step_number)

            if not success:
                logging.error(f"Step {step_number} failed, stopping workflow")
                all_successful = False
                break

            logging.info(f"Step {step_number} completed successfully")

        if all_successful:
            logging.info("All workflow steps completed successfully")
        else:
            logging.error("Workflow stopped due to step failure")

        return all_successful

    def execute_steps_from(self, start_step: int) -> bool:
        """Execute steps starting from a specific step number."""
        logging.info(f"Starting execution from step {start_step}")

        # Get steps to execute
        steps_to_execute = [num for num in self.step_order if num >= start_step]

        if not steps_to_execute:
            logging.error(f"No steps found from step {start_step}")
            return False

        all_successful = True

        for step_number in steps_to_execute:
            logging.info(f"Executing step {step_number}")

            success = self.execute_step(step_number)

            if not success:
                logging.error(f"Step {step_number} failed, stopping workflow")
                all_successful = False
                break

            logging.info(f"Step {step_number} completed successfully")

        return all_successful

    def execute_steps_range(self, start_step: int, end_step: int) -> bool:
        """Execute steps within a specific range."""
        logging.info(f"Executing steps {start_step} to {end_step}")

        # Get steps to execute
        steps_to_execute = [num for num in self.step_order if start_step <= num <= end_step]

        if not steps_to_execute:
            logging.error(f"No steps found in range {start_step} to {end_step}")
            return False

        all_successful = True

        for step_number in steps_to_execute:
            logging.info(f"Executing step {step_number}")

            success = self.execute_step(step_number)

            if not success:
                logging.error(f"Step {step_number} failed, stopping workflow")
                all_successful = False
                break

            logging.info(f"Step {step_number} completed successfully")

        return all_successful

    def get_step_status(self, step_number: int) -> Optional[Dict[str, Any]]:
        """Get the status of a specific step."""
        step = self.get_step(step_number)
        if not step:
            return None

        return step.get_step_summary()

    def get_workflow_progress(self) -> Dict[str, Any]:
        """Get overall workflow progress."""
        total_steps = len(self.step_order)
        completed_steps = 0

        for step_number in self.step_order:
            step = self.get_step(step_number)
            if step and step.end_time:
                completed_steps += 1

        progress_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0

        return {
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'progress_percentage': progress_percentage,
            'current_step': self.current_step_number,
            'execution_history': self.execution_history
        }

    def pause_workflow(self):
        """Pause the workflow execution."""
        if hasattr(self.workflow, 'workflow_paused'):
            self.workflow.workflow_paused = True
            logging.info("Workflow paused")

    def resume_workflow(self):
        """Resume the workflow execution."""
        if hasattr(self.workflow, 'workflow_paused'):
            self.workflow.workflow_paused = False
            logging.info("Workflow resumed")

    def reset_workflow(self):
        """Reset the workflow to initial state."""
        self.current_step_number = 0
        self.execution_history.clear()

        # Reset all steps
        for step in self.steps.values():
            step.start_time = None
            step.end_time = None
            step.errors.clear()
            step.warnings.clear()

        logging.info("Workflow reset to initial state")

    def _save_execution_history(self):
        """Save execution history to file."""
        try:
            if not self.workflow.project_path:
                return

            history_file = os.path.join(self.workflow.project_path, "execution_history.json")

            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.execution_history, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logging.error(f"Error saving execution history: {e}")

    def load_execution_history(self):
        """Load execution history from file."""
        try:
            if not self.workflow.project_path:
                return

            history_file = os.path.join(self.workflow.project_path, "execution_history.json")

            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.execution_history = json.load(f)

                logging.info(f"Loaded {len(self.execution_history)} execution records")

        except Exception as e:
            logging.error(f"Error loading execution history: {e}")

    def get_step_names(self) -> Dict[int, str]:
        """Get mapping of step numbers to names."""
        return {num: step.step_name for num, step in self.steps.items()}

    def validate_all_steps(self) -> Dict[int, bool]:
        """Validate prerequisites for all steps."""
        validation_results = {}

        for step_number in self.step_order:
            step = self.get_step(step_number)
            if step:
                validation_results[step_number] = step.validate_prerequisites()

        return validation_results
