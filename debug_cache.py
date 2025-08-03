#!/usr/bin/env python3

from src.memory_manager import ProjectFileCache

def test_project_cache():
    print("=== ProjectFileCache Debug Test ===")

    # Create cache instance
    cache = ProjectFileCache('test_project')

    # Test update
    print("1. Testing update...")
    update_result = cache.update('test.txt', 'test content')
    print(f"   Update result: {update_result}")
    print(f"   Cache contents: {cache.cache}")

    # Test get
    print("2. Testing get...")
    retrieved_content = cache.get('test.txt')
    print(f"   Retrieved content: {repr(retrieved_content)}")
    print(f"   Content type: {type(retrieved_content)}")

    # Test comparison
    expected = 'test content'
    print(f"3. Comparison test:")
    print(f"   Expected: {repr(expected)}")
    print(f"   Retrieved: {repr(retrieved_content)}")
    print(f"   Equal: {retrieved_content == expected}")

    return retrieved_content == expected

if __name__ == "__main__":
    success = test_project_cache()
    print(f"\nTest result: {'PASS' if success else 'FAIL'}")
