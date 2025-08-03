#!/usr/bin/env python3
"""
Detailed plugin manager initialization test
"""

import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

print("=== Plugin Manager Initialization Test ===")

try:
    from plugin_manager import PluginManager
    from plugin_system import PluginType

    # Create plugin manager
    manager = PluginManager()
    print("✓ Plugin manager created")

    # Test initialization
    print("\nInitializing plugin manager...")
    success = manager.initialize()
    print(f"✓ Initialization: {'Success' if success else 'Failed'}")

    if success:
        # Test plugin discovery
        available = manager.get_available_plugins()
        active = manager.get_active_plugins()

        print(f"✓ Available plugins: {len(available)}")
        print(f"✓ Active plugins: {len(active)}")

        # List discovered plugins
        if available:
            print("\nDiscovered plugins:")
            for plugin in available:
                print(f"  - {plugin.name} v{plugin.version} ({plugin.plugin_type})")

        # Test plugin type filtering
        content_plugins = manager.get_plugins_by_type(PluginType.CONTENT_GENERATOR)
        workflow_plugins = manager.get_plugins_by_type(PluginType.WORKFLOW_STEP)
        export_plugins = manager.get_plugins_by_type(PluginType.EXPORT_FORMAT)

        print(f"\nPlugin types:")
        print(f"  - Content generators: {len(content_plugins)}")
        print(f"  - Workflow steps: {len(workflow_plugins)}")
        print(f"  - Export formats: {len(export_plugins)}")

        # Test plugin execution
        if content_plugins:
            plugin_name = content_plugins[0].name
            print(f"\nTesting plugin execution: {plugin_name}")

            # Try to execute plugin method
            result = manager.execute_plugin_method(
                plugin_name,
                'generate_content',
                "Test prompt",
                {"content_type": "readme", "title": "Test Project"}
            )

            if result:
                print(f"✓ Plugin execution successful ({len(result)} characters generated)")
                print(f"  Preview: {result[:100]}...")
            else:
                print("❌ Plugin execution failed")

        print("\n🎉 Plugin manager test completed successfully!")

    else:
        print("❌ Plugin manager initialization failed")

except Exception as e:
    print(f"❌ Plugin manager test failed: {e}")
    import traceback
    traceback.print_exc()
