#!/usr/bin/env python3
"""
Minimal test to identify where the workflow system is hanging
"""

import sys
import traceback
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test individual imports to find the hanging one"""

    print("Testing basic imports...")

    try:
        print("1. Testing PyQt5 imports...")
        from PyQt5.QtCore import QObject, pyqtSignal
        print("   ✓ PyQt5 imports successful")
    except Exception as e:
        print(f"   ✗ PyQt5 import failed: {e}")
        return False

    try:
        print("2. Testing base_step import...")
        from src.workflow_steps.base_step import BaseWorkflowStep
        print("   ✓ BaseWorkflowStep import successful")
    except Exception as e:
        print(f"   ✗ BaseWorkflowStep import failed: {e}")
        return False

    try:
        print("3. Testing individual step imports...")
        from src.workflow_steps.step_01_initialization import Step01Initialization
        print("   ✓ Step01Initialization import successful")
    except Exception as e:
        print(f"   ✗ Step01Initialization import failed: {e}")
        traceback.print_exc()
        return False

    try:
        print("4. Testing step_manager import...")
        from src.workflow_steps.step_manager import WorkflowStepManager
        print("   ✓ WorkflowStepManager import successful")
    except Exception as e:
        print(f"   ✗ WorkflowStepManager import failed: {e}")
        traceback.print_exc()
        return False

    return True

def test_step_manager():
    """Test step manager creation"""

    print("5. Testing step manager creation...")

    try:
        # Create a minimal workflow instance for testing
        class MockWorkflow:
            def __init__(self):
                self.project_path = "test_project"

        mock_workflow = MockWorkflow()

        from src.workflow_steps.step_manager import WorkflowStepManager
        print("   Creating WorkflowStepManager...")

        # This is where it might hang
        step_manager = WorkflowStepManager(mock_workflow)
        print(f"   ✓ WorkflowStepManager created with {len(step_manager.steps)} steps")

        return True

    except Exception as e:
        print(f"   ✗ WorkflowStepManager creation failed: {e}")
        traceback.print_exc()
        return False

def test_workflow_coordinator():
    """Test workflow coordinator creation"""

    print("6. Testing workflow coordinator creation...")

    try:
        from src.workflow_coordinator import WorkflowCoordinator
        print("   Creating WorkflowCoordinator...")

        coordinator = WorkflowCoordinator()
        print(f"   ✓ WorkflowCoordinator created, initialized: {coordinator.is_initialized}")

        return True

    except Exception as e:
        print(f"   ✗ WorkflowCoordinator creation failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting workflow system diagnostic test...")

    # Test imports first
    if not test_imports():
        print("Import test failed, stopping here")
        sys.exit(1)

    # Test step manager creation
    if not test_step_manager():
        print("Step manager test failed, stopping here")
        sys.exit(1)

    # Test workflow coordinator
    if not test_workflow_coordinator():
        print("Workflow coordinator test failed")
        sys.exit(1)

    print("All tests passed successfully!")
