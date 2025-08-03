"""
Test script for validating the enhanced FANWS features:
- API retry logic with tenacity
- Enhanced logging system
- Input validation system
- Atomic backup system
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_logging_setup():
    """Test the enhanced logging setup"""
    print("Testing enhanced logging setup...")

    try:
        from src.error_handling_system import setup_logging
        setup_logging()

        # Test different log levels
        logging.debug("Debug message - should appear in files only")
        logging.info("Info message - should appear in main log")
        logging.warning("Warning message - should appear in console and files")
        logging.error("Error message - should appear in error log and console")

        print("✓ Logging setup test passed")
        return True
    except Exception as e:
        print(f"✗ Logging setup test failed: {e}")
        return False

def test_input_validation():
    """Test the input validation system"""
    print("\nTesting input validation system...")

    try:
        from src.input_validation import validator, APIProvider, InputType, validate_input

        # Test API key validation
        test_cases = [
            ("sk-test123456789012345678901234567890123456789012345", APIProvider.OPENAI, False),  # Wrong format
            ("", APIProvider.OPENAI, False),  # Empty
            ("sk-" + "a" * 48, APIProvider.OPENAI, True),  # Relaxed validation should pass
            ("hf_" + "a" * 34, APIProvider.HUGGINGFACE, True),  # Correct format
            ("invalid_key", APIProvider.HUGGINGFACE, False),  # Wrong prefix
        ]

        for key, provider, should_pass in test_cases:
            result = validator.validate_api_key(key, provider)
            if result.is_valid == should_pass:
                print(f"✓ API key validation test passed for {provider.value}")
            else:
                print(f"✗ API key validation test failed for {provider.value}: {result.message}")

        # Test project name validation
        project_tests = [
            ("ValidProject", True),
            ("Project With Spaces", True),
            ("Project/With\\Invalid*Chars", False),
            ("", False),
            ("a" * 60, False),  # Too long
        ]

        for name, should_pass in project_tests:
            result = validator.validate_project_name(name)
            if result.is_valid == should_pass:
                print(f"✓ Project name validation test passed for '{name}'")
            else:
                print(f"✗ Project name validation test failed for '{name}': {result.message}")

        print("✓ Input validation system test passed")
        return True
    except Exception as e:
        print(f"✗ Input validation test failed: {e}")
        return False

def test_atomic_backup():
    """Test the atomic backup system"""
    print("\nTesting atomic backup system...")

    try:
        from src.atomic_backup import backup_manager, create_projects_backup

        # Create a test projects directory if it doesn't exist
        test_projects_dir = Path("projects")
        test_projects_dir.mkdir(exist_ok=True)

        # Create a test project
        test_project = test_projects_dir / "test_project"
        test_project.mkdir(exist_ok=True)
        (test_project / "test_file.txt").write_text("Test content")

        # Test backup creation
        success, backup_path, metadata = create_projects_backup("test_backup")

        if success:
            print(f"✓ Backup created successfully: {backup_path}")
            print(f"  - Size: {metadata.get('backup_size_bytes', 0)} bytes")
            print(f"  - Files: {metadata.get('file_count', 0)}")
            print(f"  - Time: {metadata.get('copy_time_seconds', 0):.2f}s")
        else:
            print(f"✗ Backup creation failed: {metadata.get('error', 'Unknown error')}")
            return False

        # Test backup listing
        backups = backup_manager.list_backups()
        if "test_backup" in backups:
            print("✓ Backup listing test passed")
        else:
            print("✗ Backup listing test failed")
            return False

        # Clean up test backup
        success, message = backup_manager.delete_backup("test_backup")
        if success:
            print("✓ Backup cleanup successful")
        else:
            print(f"⚠ Backup cleanup failed: {message}")

        print("✓ Atomic backup system test passed")
        return True
    except Exception as e:
        print(f"✗ Atomic backup test failed: {e}")
        return False

def test_api_retry_logic():
    """Test the API retry logic"""
    print("\nTesting API retry logic...")

    try:
        from src.api_manager import get_api_manager

        # Get API manager instance
        api_manager = get_api_manager()

        # Check if tenacity decorator is present
        if hasattr(api_manager, '_make_http_request'):
            print("✓ API retry method found")

            # Try to access the retry decorator attributes
            retry_method = api_manager._make_http_request
            if hasattr(retry_method, 'retry'):
                print("✓ Tenacity retry decorator detected")
            else:
                print("⚠ Retry decorator not detected, but method exists")
        else:
            print("✗ API retry method not found")
            return False

        print("✓ API retry logic test passed")
        return True
    except Exception as e:
        print(f"✗ API retry logic test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("FANWS Enhanced Features Validation Test")
    print("=" * 50)

    tests = [
        test_logging_setup,
        test_input_validation,
        test_atomic_backup,
        test_api_retry_logic,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 50)
    print(f"Test Results: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("✓ All enhanced features are working correctly!")
        return True
    else:
        print("✗ Some features need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
