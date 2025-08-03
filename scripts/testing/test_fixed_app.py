#!/usr/bin/env python3
"""Test script to verify FANWS fixes"""

import sys
import traceback
from PyQt5.QtWidgets import QApplication

try:
    print("Testing FANWS import and initialization...")

    # Create QApplication first (required for PyQt widgets)
    app = QApplication(sys.argv)

    import fanws
    print("✅ FANWS imported successfully")

    window = fanws.FANWS()
    print("✅ FANWS initialized successfully")
    print("✅ Both statusBar and UI attribute errors are fixed!")

    # Clean exit
    app.quit()

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
