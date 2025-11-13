#!/usr/bin/env python3
"""
Test script to verify MainWindow functionality
"""

try:
    print("Starting MainWindow test...")

    # Import PyQt5 and create application first
    from PyQt5.QtWidgets import QApplication
    import sys

    if QApplication.instance() is None:
        app = QApplication(sys.argv)
        print("✅ QApplication created")

    from src.ui.main_gui import MainWindow, create_modern_gui
    print("✅ MainWindow import successful")

    window = MainWindow()
    print("✅ MainWindow created successfully")
    print(f"Window title: {window.windowTitle()}")
    print(f"Window size: {window.size().width()}x{window.size().height()}")

    # Test the create_modern_gui function
    modern_window = create_modern_gui()
    print("✅ create_modern_gui() successful")
    print(f"Modern window type: {type(modern_window).__name__}")

    print("✅ All MainWindow tests passed!")

except Exception as e:
    print(f"❌ Error during MainWindow test: {e}")
    import traceback
    traceback.print_exc()
