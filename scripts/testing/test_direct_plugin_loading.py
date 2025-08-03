#!/usr/bin/env python3
"""
Test direct plugin loading
"""

import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

print("=== Direct Plugin Loading Test ===")

try:
    # Test importing plugin system components
    from plugin_system import ContentGeneratorPlugin, PluginInfo, PluginType
    print("✓ Plugin system imports successful")

    # Change directory to plugins folder
    original_dir = os.getcwd()
    plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')

    # Add plugins dir to path
    sys.path.insert(0, plugins_dir)

    # Try to import the sample plugin
    from sample_content_generator import SampleContentGeneratorPlugin
    print("✓ Sample plugin import successful")

    # Try to instantiate the plugin
    plugin = SampleContentGeneratorPlugin()
    print("✓ Plugin instantiation successful")

    # Try to get plugin info
    info = plugin.get_info()
    print(f"✓ Plugin info: {info.name} v{info.version}")

    # Test plugin methods
    types = plugin.get_supported_types()
    print(f"✓ Supported types: {types}")

    # Test content generation
    content = plugin.generate_content("Test prompt", {"content_type": "readme", "title": "Test Project"})
    print(f"✓ Content generated ({len(content)} characters)")

    print("\n🎉 Plugin loading test successful!")

except Exception as e:
    print(f"❌ Plugin loading test failed: {e}")
    import traceback
    traceback.print_exc()
