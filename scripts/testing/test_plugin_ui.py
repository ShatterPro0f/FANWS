#!/usr/bin/env python3
"""
Test the plugin management UI
"""

import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

print("=== Plugin Management UI Test ===")

try:
    from PyQt5.QtWidgets import QApplication
    from plugin_management_ui import PluginManagementWidget

    # Create QApplication
    app = QApplication(sys.argv)
    print("✓ QApplication created")

    # Create plugin management widget
    widget = PluginManagementWidget()
    print("✓ Plugin management widget created")

    # Set window properties
    widget.setWindowTitle("FANWS Plugin Manager")
    widget.resize(900, 700)

    # Show the widget
    widget.show()
    print("✓ Plugin management UI displayed")

    print("\n🎉 Plugin management UI test successful!")
    print("Close the window to exit...")

    # Run the application
    sys.exit(app.exec_())

except Exception as e:
    print(f"❌ Plugin management UI test failed: {e}")
    import traceback
    traceback.print_exc()
