#!/usr/bin/env python3
"""
ProjectFileCache Issue Diagnostic Tool
"""

import os
import sys
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def test_file_operations():
    print("=== Testing File Operations ===")

    from src.file_operations import save_to_file, read_file, project_file_path

    # Test basic file operations
    test_project = "debug_test_project"
    test_file = "test.txt"
    test_content = "test content"

    print(f"1. Testing project_file_path for {test_project}/{test_file}")
    file_path = project_file_path(test_project, test_file)
    print(f"   File path: {file_path}")

    print("2. Testing save_to_file")
    save_result = save_to_file(file_path, test_content)
    print(f"   Save result: {save_result}")

    print("3. Testing read_file")
    read_content = read_file(file_path)
    print(f"   Read content: {repr(read_content)}")

    print("4. File exists check")
    exists = os.path.exists(file_path)
    print(f"   File exists: {exists}")

    return save_result, read_content

def test_project_file_cache():
    print("\n=== Testing ProjectFileCache ===")

    from src.memory_manager import ProjectFileCache

    cache = ProjectFileCache("debug_test_project")

    print("1. Initial cache state")
    print(f"   Cache dict: {cache.cache}")

    print("2. Testing update method")
    update_result = cache.update("test.txt", "test content")
    print(f"   Update result: {update_result}")
    print(f"   Cache after update: {cache.cache}")

    print("3. Testing get method")
    get_result = cache.get("test.txt")
    print(f"   Get result: {repr(get_result)}")
    print(f"   Cache after get: {cache.cache}")

    print("4. Testing direct cache access")
    direct_access = cache.cache.get("test.txt")
    print(f"   Direct cache access: {repr(direct_access)}")

    return update_result, get_result

if __name__ == "__main__":
    try:
        print("Starting ProjectFileCache diagnostic...")

        # Test basic file operations first
        save_result, read_content = test_file_operations()

        # Test ProjectFileCache
        update_result, get_result = test_project_file_cache()

        print(f"\n=== Summary ===")
        print(f"File operations save: {save_result}")
        print(f"File operations read: {repr(read_content)}")
        print(f"ProjectFileCache update: {update_result}")
        print(f"ProjectFileCache get: {repr(get_result)}")
        print(f"Content match: {get_result == 'test content'}")

        if get_result != "test content":
            print(f"\n❌ ISSUE IDENTIFIED: ProjectFileCache.get() returned {repr(get_result)} instead of 'test content'")
        else:
            print(f"\n✅ ProjectFileCache working correctly")

    except Exception as e:
        print(f"Error during diagnostic: {e}")
        import traceback
        traceback.print_exc()
