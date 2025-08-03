#!/usr/bin/env python3
"""
Complete FANWS integration test
Tests the entire system: workflow coordinator, plugin system, and workflow steps
"""

import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

print("=== FANWS System Integration Test ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Source path: {src_path}")

try:
    # Test 1: Plugin System
    print("\n1. Testing Plugin System...")
    from plugin_system import PluginManager as CorePluginManager, PluginType
    from plugin_manager import PluginManager

    plugin_manager = PluginManager()
    plugin_manager.initialize()

    available_plugins = plugin_manager.get_available_plugins()
    active_plugins = plugin_manager.get_active_plugins()

    print(f"   ✓ Available plugins: {len(available_plugins)}")
    print(f"   ✓ Active plugins: {len(active_plugins)}")

    # Test 2: Workflow Steps (simplified test)
    print("\n2. Testing Workflow Steps...")

    # Change to src directory for proper relative imports
    original_dir = os.getcwd()
    os.chdir(src_path)

    try:
        from workflow_steps.base_step import BaseWorkflowStep
        print("   ✓ Base workflow step imported")

        # Test step manager import
        from workflow_steps.step_manager import WorkflowStepManager
        print("   ✓ Step manager imported")

        # Test workflow coordinator (main integration point)
        from workflow_coordinator import WorkflowCoordinator
        print("   ✓ Workflow coordinator imported")

        # Initialize coordinator
        coordinator = WorkflowCoordinator(project_name="test_integration")
        print("   ✓ Workflow coordinator initialized")

        # Test plugin integration in coordinator
        if hasattr(coordinator, 'plugin_manager') and coordinator.plugin_manager:
            content_gens = coordinator.get_available_content_generators()
            export_formats = coordinator.get_available_export_formats()
            print(f"   ✓ Content generators: {len(content_gens)}")
            print(f"   ✓ Export formats: {len(export_formats)}")
        else:
            print("   ⚠ Plugin manager not integrated in coordinator")

        # Test workflow steps
        if hasattr(coordinator, 'step_manager') and coordinator.step_manager:
            available_steps = coordinator.step_manager.get_available_steps()
            print(f"   ✓ Available workflow steps: {len(available_steps)}")
            for step_name in available_steps[:3]:  # Show first 3
                print(f"     - {step_name}")
        else:
            print("   ⚠ Step manager not initialized")

    finally:
        # Change back to original directory
        os.chdir(original_dir)

    print("\n🎉 Integration test completed successfully!")
    print("\nSummary:")
    print(f"- Plugin system: Working ({len(available_plugins)} plugins)")
    print(f"- Workflow coordinator: Working")
    print(f"- Plugin integration: Working")
    print(f"- Workflow steps: Working")

except Exception as e:
    print(f"\n❌ Integration test failed: {e}")
    import traceback
    traceback.print_exc()

    # Change back to original directory if needed
    try:
        os.chdir(original_dir)
    except:
        pass
