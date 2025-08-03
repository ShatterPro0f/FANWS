#!/usr/bin/env python3
"""
Simple plugin system test
"""

import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

try:
    # Test plugin system import
    from plugin_system import PluginManager, PluginType
    print("✓ Plugin system imported successfully")

    # Test plugin manager wrapper
    from plugin_manager import PluginManager as PluginManagerWrapper
    print("✓ Plugin manager wrapper imported successfully")

    # Test plugin manager initialization
    plugin_manager = PluginManagerWrapper()
    print("✓ Plugin manager initialized")

    # Initialize the plugin system
    plugin_manager.initialize()
    print("✓ Plugin system initialized")

    # Test plugin discovery
    all_plugins = plugin_manager.get_available_plugins()
    active_plugins = plugin_manager.get_active_plugins()
    print(f"✓ Found {len(all_plugins)} available plugins")
    print(f"✓ Found {len(active_plugins)} active plugins")

    # Test plugin types
    workflow_plugins = plugin_manager.get_plugins_by_type(PluginType.WORKFLOW_STEP)
    content_plugins = plugin_manager.get_plugins_by_type(PluginType.CONTENT_GENERATOR)
    export_plugins = plugin_manager.get_plugins_by_type(PluginType.EXPORT_FORMAT)

    print(f"✓ Workflow plugins: {len(workflow_plugins)}")
    print(f"✓ Content generator plugins: {len(content_plugins)}")
    print(f"✓ Export format plugins: {len(export_plugins)}")

    print("\n🎉 Plugin system test completed successfully!")

except Exception as e:
    print(f"❌ Plugin system test failed: {e}")
    import traceback
    traceback.print_exc()
