#!/usr/bin/env python3
"""Simple test for folder selection dialog"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

def test_folder_dialog():
    """Test the folder selection dialog functionality"""
    app = QApplication(sys.argv)

    print("Testing folder selection dialog...")

    # Test folder dialog
    folder_path = QFileDialog.getExistingDirectory(
        None,
        "Test: Select Any Folder",
        os.path.expanduser("~"),
        QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
    )

    if folder_path:
        print(f"✅ Folder selected: {folder_path}")
        print(f"✅ Folder name: {os.path.basename(folder_path)}")

        # Show message box with results
        msg = QMessageBox()
        msg.setWindowTitle("Test Results")
        msg.setText(f"Selected folder: {folder_path}\nFolder name: {os.path.basename(folder_path)}")
        msg.exec_()

        app.quit()
        return True
    else:
        print("❌ No folder selected (user cancelled)")
        app.quit()
        return False

if __name__ == "__main__":
    success = test_folder_dialog()
    print(f"Test {'passed' if success else 'cancelled'}")
