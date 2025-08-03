#!/usr/bin/env python3
"""Test script to verify save_to_file fix by creating a project"""

import sys
import traceback
from PyQt5.QtWidgets import QApplication

try:
    print("Testing project creation with save_to_file fix...")

    # Create QApplication first (required for PyQt widgets)
    app = QApplication(sys.argv)

    import fanws
    print("✅ FANWS imported successfully")

    window = fanws.FANWS()
    print("✅ FANWS initialized successfully")

    # Test creating a dummy project configuration
    from src.utils import project_file_path
    from src.file_operations import save_to_file

    test_project = "test_save_fix"
    test_content = "This is a test to verify save_to_file works correctly."

    # Test the corrected save_to_file usage
    continuity_rules_path = project_file_path(test_project, "continuity_rules.txt")
    result = save_to_file(continuity_rules_path, test_content)

    if result:
        print("✅ save_to_file fix works correctly!")
    else:
        print("❌ save_to_file fix failed")

    # Clean exit
    app.quit()

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
