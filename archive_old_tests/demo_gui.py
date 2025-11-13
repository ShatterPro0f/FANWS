#!/usr/bin/env python3
"""
Visual test script to demonstrate the new hierarchical navigation
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

try:
    print("🚀 Starting FANWS GUI Demo...")

    # Create QApplication
    if QApplication.instance() is None:
        app = QApplication(sys.argv)
        print("✅ QApplication created")

    # Import and create MainWindow
    from src.ui.main_gui import MainWindow
    print("✅ MainWindow imported")

    window = MainWindow()
    print("✅ MainWindow created with hierarchical navigation")

    # Show the window
    window.show()
    print("✅ MainWindow displayed")

    print("\n📋 New Hierarchical Structure:")
    print("├── 📁 Project")
    print("│   ├── Switch Project")
    print("│   ├── Create Project")
    print("│   ├── Load Project")
    print("│   ├── Delete Project")
    print("│   └── Novel Settings")
    print("│       ├── Novel Concept")
    print("│       ├── Primary Tone")
    print("│       ├── Sub-Tone")
    print("│       ├── Theme")
    print("│       ├── Target Word Count")
    print("│       ├── Reading Level")
    print("│       ├── Chapter/section organization")
    print("│       ├── Total Chapters")
    print("│       └── Chapter Sections: Sections per chapter")
    print("├── 📊 Dashboard")
    print("│   ├── Progress Graph")
    print("│   ├── Synonyms")
    print("│   ├── Log")
    print("│   ├── Chapter Progress")
    print("│   └── Current Draft")
    print("├── 📈 Performance")
    print("│   ├── Memory Usage")
    print("│   ├── CPU Usage")
    print("│   ├── API Call Statistics")
    print("│   ├── File Operations")
    print("│   ├── Cache Hit Rate")
    print("│   ├── Response Times")
    print("│   ├── Optimization Recommendations")
    print("│   └── System Resources")
    print("├── ⚙️ Settings")
    print("│   ├── OpenAI API Key (Savable)")
    print("│   └── WordsAPI Key (Savable)")
    print("└── 📤 Export")
    print("    ├── Export Status")
    print("    ├── Export Formats")
    print("    ├── Export History")
    print("    ├── File Sizes")
    print("    └── Export Quality")

    print(f"\n🎯 Layout: Sidebar (1/4) + Home Page (3/4)")
    print(f"📐 Window Size: {window.size().width()}x{window.size().height()}")
    print(f"🏠 Home Page: All subsection content opens here")
    print(f"📂 Sidebar: Hierarchical navigation structure")

    print("\n✅ GUI Demo Ready! Check the window for the new interface.")
    print("💡 Click on section headers to expand and explore the hierarchy!")

    # Auto-close after 3 seconds for automated testing
    QTimer.singleShot(3000, window.close)

    # Run the application briefly
    QTimer.singleShot(3100, app.quit)
    app.exec_()

    print("✅ GUI Demo completed successfully!")

except Exception as e:
    print(f"❌ Error during GUI demo: {e}")
    import traceback
    traceback.print_exc()
