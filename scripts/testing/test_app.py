#!/usr/bin/env python3
"""
Test script for FANWS application
"""
import sys
from PyQt5.QtWidgets import QApplication
import fanws

def main():
    print("Creating QApplication...")
    app = QApplication(sys.argv)

    print("Creating FANWS window...")
    window = fanws.FANWS()

    print("Showing window...")
    window.show()

    print("Application ready!")
    # Don't start event loop for test, just check if window can be created
    return 0

if __name__ == "__main__":
    sys.exit(main())
