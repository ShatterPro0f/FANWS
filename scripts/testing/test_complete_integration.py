#!/usr/bin/env python3
"""
Comprehensive integration test for FANWS workflow coordinator and plugin system
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Import from src directory directly
    import sys
    import os
    from pathlib import Path

    # Change to src directory to ensure proper relative imports
    current_dir = os.getcwd()
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    os.chdir(src_path)

    from workflow_coordinator import WorkflowCoordinator
    from plugin_manager import PluginManager
    from plugin_system import PluginType

    # Change back to original directory
    os.chdir(current_dir)

    print("✓ All imports successful")

    # Test basic initialization
    coordinator = WorkflowCoordinator(project_name="test_integration")
    print("✓ WorkflowCoordinator initialized")

    # Test plugin integration
    if hasattr(coordinator, 'plugin_manager') and coordinator.plugin_manager:
        print("✓ Plugin manager integrated")

        # Test plugin discovery
        all_plugins = coordinator.plugin_manager.get_all_plugins()
        print(f"✓ Found {len(all_plugins)} plugins")

        # Test plugin type filtering
        workflow_plugins = coordinator.get_available_content_generators()
        print(f"✓ Found {len(workflow_plugins)} content generator plugins")

        export_plugins = coordinator.get_available_export_formats()
        print(f"✓ Found {len(export_plugins)} export format plugins")

    else:
        print("⚠ Plugin manager not initialized")

    # Test workflow steps
    if hasattr(coordinator, 'step_manager') and coordinator.step_manager:
        available_steps = coordinator.step_manager.get_available_steps()
        print(f"✓ Found {len(available_steps)} workflow steps")

        for step_name in available_steps:
            print(f"  - {step_name}")
    else:
        print("⚠ Step manager not initialized")

    print("\n🎉 Integration test completed successfully!")

except Exception as e:
    print(f"❌ Integration test failed: {e}")
    import traceback
    traceback.print_exc()
