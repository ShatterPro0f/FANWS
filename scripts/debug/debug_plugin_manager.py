#!/usr/bin/env python3
"""
Debug plugin manager initialization
"""

import sys
import os
import logging

# Set up logging to see error details
logging.basicConfig(level=logging.DEBUG)

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

print("=== Plugin Manager Debug ===")

try:
    from plugin_manager import PluginManager

    # Create plugin manager
    manager = PluginManager()
    print("✓ Plugin manager created")

    # Test plugin system initialization
    print("\nTesting plugin system initialization...")
    success = manager.plugin_system.initialize()
    print(f"✓ Plugin system init: {'Success' if success else 'Failed'}")

    if success:
        # Test discovery
        print("\nTesting plugin discovery...")
        count = manager.plugin_system.discover_plugins()
        print(f"✓ Discovered: {count} plugins")

        # Check registry
        available = list(manager.plugin_system.registry.plugins.values())
        print(f"✓ Registry has: {len(available)} plugins")

        for plugin in available:
            print(f"  - {plugin.name} ({plugin.plugin_type})")

    print("\n🎉 Debug completed!")

except Exception as e:
    print(f"❌ Debug failed: {e}")
    import traceback
    traceback.print_exc()
