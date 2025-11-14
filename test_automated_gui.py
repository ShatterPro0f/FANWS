#!/usr/bin/env python3
"""
Test script for Automated Novel GUI
Launches the GUI for visual inspection
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from src.ui.automated_novel_gui import AutomatedNovelGUI

if __name__ == "__main__":
    print("Launching Automated Novel Writing GUI...")
    print("This will open the GUI window for inspection.")
    print("Close the window to exit.")
    
    app = QApplication(sys.argv)
    window = AutomatedNovelGUI()
    window.show()
    
    print("\n✓ GUI launched successfully!")
    print("Features available:")
    print("  - Initialize new novel project")
    print("  - Track progress in real-time")
    print("  - View logs, story, characters, world")
    print("  - Approve/adjust generated content")
    print("  - Export novel in multiple formats")
    
    sys.exit(app.exec_())
