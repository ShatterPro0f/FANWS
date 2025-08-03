#!/usr/bin/env python3
"""
Debug script to test project creation
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.file_operations import initialize_project_files

# Test project creation
test_project_name = "debug_test_project"
test_project_path = f"projects/{test_project_name}"

# Remove if exists
if os.path.exists(test_project_path):
    import shutil
    shutil.rmtree(test_project_path)

print(f"Creating project: {test_project_name}")
result = initialize_project_files(test_project_name)
print(f"Creation result: {result}")

if os.path.exists(test_project_path):
    print(f"\nProject directory created: {test_project_path}")
    print("\nFiles in project root:")
    for item in os.listdir(test_project_path):
        item_path = os.path.join(test_project_path, item)
        if os.path.isfile(item_path):
            print(f"  FILE: {item}")
        elif os.path.isdir(item_path):
            print(f"  DIR:  {item}")

    # Check for specific files
    check_files = ['plot_points.txt', 'continuity_rules.txt']
    for filename in check_files:
        filepath = os.path.join(test_project_path, filename)
        if os.path.exists(filepath):
            print(f"✅ {filename} exists")
        else:
            print(f"❌ {filename} missing")

    # Clean up
    import shutil
    shutil.rmtree(test_project_path)
    print(f"\n🧹 Cleaned up {test_project_path}")
else:
    print("❌ Project directory not created")
