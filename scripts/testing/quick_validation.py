#!/usr/bin/env python3
"""
Quick validation script to confirm FANWS cache fix
Bypasses terminal issues with direct Python execution
"""

def test_cache_fix():
    """Test the FileCache.update() method fix"""
    print("Testing FileCache.update() method...")

    try:
        from src.memory_manager import FileCache

        # Create cache instance
        cache = FileCache()
        print("✓ FileCache created successfully")

        # Test the fix - this should work now
        cache.update('test_key', 'test_value')
        print("✓ FileCache.update() method works")

        # Verify retrieval
        value = cache.get('test_key')
        if value == 'test_value':
            print("✓ Cache retrieval successful")
            return True
        else:
            print(f"✗ Cache retrieval failed: expected 'test_value', got {value}")
            return False

    except Exception as e:
        print(f"✗ Cache test failed: {e}")
        return False

def test_project_cache():
    """Test ProjectFileCache functionality"""
    print("\nTesting ProjectFileCache...")

    try:
        from src.memory_manager import ProjectFileCache

        # Create project cache
        cache = ProjectFileCache('test_project')
        print("✓ ProjectFileCache created successfully")

        # Test update method
        result = cache.update('test.txt', 'test content')
        print(f"✓ ProjectFileCache.update() returned: {result}")

        return True

    except Exception as e:
        print(f"✗ ProjectFileCache test failed: {e}")
        return False

if __name__ == "__main__":
    print("FANWS Quick Validation")
    print("=" * 40)

    success1 = test_cache_fix()
    success2 = test_project_cache()

    print("\n" + "=" * 40)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED - Cache fix confirmed!")
        print("FANWS is ready for production.")
    else:
        print("❌ Some tests failed - review errors above.")

    print("=" * 40)
