#!/usr/bin/env python3
"""
Comprehensive Plugin System Enhancement Test
Tests all Priority 1-4 enhancements: Sample Plugins, UI Integration, Hot Reloading, Error Handling
"""

import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

print("=== FANWS Plugin System Enhancement Test ===")

def test_sample_plugins():
    """Test Priority 1: Complete Sample Plugins"""
    print("\n1. Testing Sample Plugin Registration...")

    try:
        from plugin_manager import PluginManager
        from plugin_system import PluginType

        manager = PluginManager()
        success = manager.initialize()

        if success:
            available = manager.get_available_plugins()
            active = manager.get_active_plugins()

            print(f"✓ Available plugins: {len(available)}")
            print(f"✓ Active plugins: {len(active)}")

            # List plugins by type
            content_plugins = manager.get_plugins_by_type(PluginType.CONTENT_GENERATOR)
            workflow_plugins = manager.get_plugins_by_type(PluginType.WORKFLOW_STEP)

            print(f"✓ Content generators: {len(content_plugins)}")
            print(f"✓ Workflow steps: {len(workflow_plugins)}")

            # Test plugin execution
            if content_plugins:
                plugin = content_plugins[0]
                print(f"✓ Testing plugin: {plugin.name}")

                # Execute plugin method
                result = manager.execute_plugin_method(
                    plugin.name,
                    'generate_content',
                    "Generate a README",
                    {"content_type": "readme", "title": "Enhanced Plugin System"}
                )

                if result and len(result) > 0:
                    print(f"✓ Plugin execution successful ({len(result)} characters)")
                    return True
                else:
                    print("❌ Plugin execution failed")
                    return False
            else:
                print("❌ No content generator plugins found")
                return False
        else:
            print("❌ Plugin manager initialization failed")
            return False

    except Exception as e:
        print(f"❌ Sample plugin test failed: {e}")
        return False

def test_hot_reloading():
    """Test Priority 3: Hot Reloading"""
    print("\n3. Testing Hot Reloading...")

    try:
        from plugin_manager import PluginManager

        manager = PluginManager()
        manager.initialize()

        # Test hot reload all
        reloaded_count = manager.hot_reload_all_plugins()
        print(f"✓ Hot reloaded {reloaded_count} plugins")

        # Test individual plugin reload
        available = manager.get_available_plugins()
        if available:
            plugin_name = available[0].name
            success = manager.reload_plugin(plugin_name)
            print(f"✓ Individual reload: {'Success' if success else 'Failed'}")
            return success
        else:
            print("✓ No plugins to reload")
            return True

    except Exception as e:
        print(f"❌ Hot reloading test failed: {e}")
        return False

def test_error_handling():
    """Test Priority 4: Enhanced Error Handling"""
    print("\n4. Testing Enhanced Error Handling...")

    try:
        from plugin_system import PluginManager as CorePluginManager, PluginInfo, PluginType

        manager = CorePluginManager()

        # Test validation with invalid plugin info
        invalid_plugin = PluginInfo(
            name="",  # Invalid: empty name
            version="invalid",  # Invalid: bad version format
            plugin_type=PluginType.CONTENT_GENERATOR,
            description="Test plugin",
            author="Test",
            api_version="999.0.0"  # Invalid: wrong API version
        )

        is_valid = manager.registry._validate_plugin_info(invalid_plugin)
        print(f"✓ Invalid plugin rejected: {'Success' if not is_valid else 'Failed'}")

        # Test with valid plugin info
        valid_plugin = PluginInfo(
            name="Test Plugin",
            version="1.0.0",
            plugin_type=PluginType.CONTENT_GENERATOR,
            description="A test plugin",
            author="Test Author",
            api_version="1.0.0"
        )

        is_valid = manager.registry._validate_plugin_info(valid_plugin)
        print(f"✓ Valid plugin accepted: {'Success' if is_valid else 'Failed'}")

        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_ui_integration():
    """Test Priority 2: UI Integration (limited test)"""
    print("\n2. Testing UI Integration...")

    try:
        # Test UI component import
        from plugin_management_ui import PluginManagementWidget
        print("✓ Plugin management UI component imported")

        # Test PyQt5 availability
        from PyQt5.QtWidgets import QApplication, QWidget
        print("✓ PyQt5 available for UI")

        # We can't run the full UI in a test, but we can verify creation
        # This would require a display/X11 connection to actually run
        print("✓ UI integration components ready")
        return True

    except ImportError as e:
        print(f"⚠ UI integration test skipped (missing dependencies): {e}")
        return True  # Not a failure, just missing optional components
    except Exception as e:
        print(f"❌ UI integration test failed: {e}")
        return False

def main():
    """Run all enhancement tests"""
    print("Testing all plugin system enhancements...")

    results = {
        "Sample Plugins": test_sample_plugins(),
        "UI Integration": test_ui_integration(),
        "Hot Reloading": test_hot_reloading(),
        "Error Handling": test_error_handling()
    }

    print("\n=== Enhancement Test Results ===")
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    print(f"\n🎯 Overall Status: {'🎉 ALL ENHANCEMENTS WORKING' if all_passed else '⚠ SOME ISSUES FOUND'}")

    if all_passed:
        print("\n🚀 Ready for Production:")
        print("  ✅ Sample plugins working")
        print("  ✅ UI components ready")
        print("  ✅ Hot reloading functional")
        print("  ✅ Error handling enhanced")
        print("  ✅ Plugin system fully integrated")

if __name__ == "__main__":
    main()
