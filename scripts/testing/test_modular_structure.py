#!/usr/bin/env python3
"""
Test simplified FANWS structure
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication

# Setup logging
logging.basicConfig(level=logging.INFO)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test importing the modular components"""
    print("Testing imports...")

    try:
        print("1. Testing UI main window import...")
        from src.ui.main_window import FANWSMainWindow
        print("   ✓ FANWSMainWindow imported successfully")

        print("2. Testing AI content generator import...")
        from src.ai.content_generator import ContentGenerator, ProjectManager
        print("   ✓ AI content generator imported successfully")

        print("3. Testing basic UI creation...")
        app = QApplication.instance() or QApplication(sys.argv)
        window = FANWSMainWindow()
        print("   ✓ FANWSMainWindow created successfully")

        print("4. Testing window display...")
        window.show()
        print("   ✓ Window displayed successfully")

        # Don't run the event loop, just test creation
        print("\n✓ All modular components working correctly!")
        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🎉 Modular refactoring successful!")
    else:
        print("\n💥 Modular refactoring needs fixes")
    sys.exit(0 if success else 1)
