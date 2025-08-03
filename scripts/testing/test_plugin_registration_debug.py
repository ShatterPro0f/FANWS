#!/usr/bin/env python3
"""
Test plugin registration debugging
"""

import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

print("=== Plugin Registration Debug Test ===")

try:
    # Import core components
    from plugin_system import PluginManager, PluginType

    # Initialize plugin manager
    manager = PluginManager()
    print("✓ Plugin manager created")

    # Get the plugins directory
    plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    print(f"✓ Plugin directory: {plugins_dir}")

    # Try manual discovery of a single plugin file
    sample_plugin_path = os.path.join(plugins_dir, 'sample_content_generator.py')
    print(f"✓ Sample plugin path: {sample_plugin_path}")

    # Test the discovery method
    plugin_info = manager._discover_plugin_file(sample_plugin_path)
    if plugin_info:
        print(f"✓ Plugin discovered: {plugin_info.name}")
        print(f"  - Type: {plugin_info.plugin_type}")
        print(f"  - Version: {plugin_info.version}")
        print(f"  - File: {plugin_info.file_path}")

        # Try to register it
        success = manager.registry.register_plugin(plugin_info)
        print(f"✓ Registration: {'Success' if success else 'Failed'}")

        if success:
            # Try to load the plugin instance
            instance = manager.registry._load_plugin_instance(plugin_info)
            print(f"✓ Instance loading: {'Success' if instance else 'Failed'}")

    else:
        print("❌ Plugin discovery failed")

except Exception as e:
    print(f"❌ Debug test failed: {e}")
    import traceback
    traceback.print_exc()
