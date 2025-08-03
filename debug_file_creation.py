#!/usr/bin/env python3
"""
Debug file creation loop
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.file_operations import project_file_path, save_to_file

# Test the specific files that are missing
test_project = "debug_test_2"
test_files = {
    'plot_points.txt': '# Plot Points\n\n## Key Events\n- [ ] Inciting Incident\n',
    'continuity_rules.txt': '# Continuity Rules\n\nMaintain consistency in:\n'
}

# Create project dir if needed
project_dir = f"projects/{test_project}"
os.makedirs(project_dir, exist_ok=True)

for filename, content in test_files.items():
    try:
        filepath = project_file_path(test_project, filename)
        print(f"Creating file: {filepath}")

        # Create directory if needed
        dir_path = os.path.dirname(filepath)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"  Created directory: {dir_path}")

        # Save file
        result = save_to_file(filepath, content)
        print(f"  Save result: {result}")

        # Check if created
        if os.path.exists(filepath):
            print(f"  ✅ File exists: {filepath}")
        else:
            print(f"  ❌ File missing: {filepath}")

    except Exception as e:
        print(f"  ❌ Error creating {filename}: {e}")

# Clean up
import shutil
if os.path.exists(project_dir):
    shutil.rmtree(project_dir)
    print(f"\n🧹 Cleaned up {project_dir}")
