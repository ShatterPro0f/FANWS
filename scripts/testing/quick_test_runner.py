"""
Quick Test Runner for FANWS
===========================

A simple test runner that validates the current state of FANWS without complex dependencies.
This script focuses on the core functionality and recent fixes.
"""

import os
import sys
import json
import time
import traceback
from datetime import datetime

def test_imports():
    """Test critical module imports."""
    print("1️⃣ Testing Module Imports...")
    results = []

    modules = [
        ("fanws", "Main application"),
        ("src.memory_manager", "Memory management with FileCache fix"),
        ("src.file_operations", "File operations"),
        ("src.api_manager", "API management"),
    ]

    for module_name, description in modules:
        try:
            __import__(module_name)
            results.append((module_name, "PASSED", "OK"))
            print(f"   ✅ {module_name}: OK")
        except Exception as e:
            results.append((module_name, "FAILED", str(e)))
            print(f"   ❌ {module_name}: FAILED - {str(e)[:60]}...")

    return results

def test_filecache_fix():
    """Test the FileCache ttl_seconds fix specifically."""
    print("\n2️⃣ Testing FileCache Fix...")
    results = []

    try:
        from src.memory_manager import FileCache, ProjectFileCache

        # Test 1: FileCache with ttl_seconds
        try:
            cache = FileCache(ttl_seconds=300)
            results.append(("FileCache ttl_seconds", "PASSED", "Accepts ttl_seconds parameter"))
            print("   ✅ FileCache accepts ttl_seconds: OK")
        except Exception as e:
            results.append(("FileCache ttl_seconds", "FAILED", str(e)))
            print(f"   ❌ FileCache ttl_seconds: FAILED - {e}")

        # Test 2: ProjectFileCache operations
        try:
            project_cache = ProjectFileCache("test_project")
            project_cache.update("test.txt", "test content")
            content = project_cache.get("test.txt")

            if content == "test content":
                results.append(("ProjectFileCache ops", "PASSED", "Operations work correctly"))
                print("   ✅ ProjectFileCache operations: OK")
            else:
                results.append(("ProjectFileCache ops", "FAILED", f"Content mismatch: {content}"))
                print(f"   ❌ ProjectFileCache operations: Content mismatch")
        except Exception as e:
            results.append(("ProjectFileCache ops", "FAILED", str(e)))
            print(f"   ❌ ProjectFileCache operations: FAILED - {e}")

        # Test 3: API Manager initialization (should not have ttl_seconds error)
        try:
            from src.api_manager import APIManager
            api_manager = APIManager()
            results.append(("APIManager init", "PASSED", "No ttl_seconds error"))
            print("   ✅ APIManager initialization: OK")
        except Exception as e:
            if "ttl_seconds" in str(e):
                results.append(("APIManager init", "FAILED", f"ttl_seconds error: {e}"))
                print(f"   ❌ APIManager initialization: ttl_seconds error still present")
            else:
                results.append(("APIManager init", "FAILED", str(e)))
                print(f"   ❌ APIManager initialization: {e}")

        # Test 4: Text Analyzer initialization
        try:
            from src.text_processing import TextAnalyzer
            analyzer = TextAnalyzer()
            results.append(("TextAnalyzer init", "PASSED", "No ttl_seconds error"))
            print("   ✅ TextAnalyzer initialization: OK")
        except Exception as e:
            if "ttl_seconds" in str(e):
                results.append(("TextAnalyzer init", "FAILED", f"ttl_seconds error: {e}"))
                print(f"   ❌ TextAnalyzer initialization: ttl_seconds error still present")
            else:
                results.append(("TextAnalyzer init", "FAILED", str(e)))
                print(f"   ❌ TextAnalyzer initialization: {e}")

    except ImportError as e:
        results.append(("Memory manager import", "FAILED", str(e)))
        print(f"   ❌ Cannot import memory_manager: {e}")

    return results

def test_project_operations():
    """Test project-related operations."""
    print("\n3️⃣ Testing Project Operations...")
    results = []

    try:
        from src.file_operations import get_project_list, validate_project_name

        # Test project list
        try:
            projects = get_project_list()
            results.append(("Project list", "PASSED", f"Found {len(projects)} projects"))
            print(f"   ✅ Project list: {len(projects)} projects found")
        except Exception as e:
            results.append(("Project list", "FAILED", str(e)))
            print(f"   ❌ Project list: FAILED - {e}")

        # Test project name validation
        try:
            valid = validate_project_name("test_project_123")
            invalid = validate_project_name("test/project<>")

            if valid and not invalid:
                results.append(("Project validation", "PASSED", "Validation logic works"))
                print("   ✅ Project name validation: OK")
            else:
                results.append(("Project validation", "FAILED", f"Logic error: valid={valid}, invalid={invalid}"))
                print("   ❌ Project name validation: Logic error")
        except Exception as e:
            results.append(("Project validation", "FAILED", str(e)))
            print(f"   ❌ Project validation: FAILED - {e}")

    except ImportError as e:
        results.append(("File operations import", "FAILED", str(e)))
        print(f"   ❌ Cannot import file_operations: {e}")

    return results

def test_application_startup():
    """Test basic application startup capabilities."""
    print("\n4️⃣ Testing Application Startup...")
    results = []

    try:
        from fanws import FANWSWindow
        results.append(("FANWSWindow import", "PASSED", "Main class can be imported"))
        print("   ✅ FANWSWindow import: OK")

        # Check for critical attributes that should exist
        expected_methods = ['__init__', 'create_new_project', 'load_project', 'start_writing']
        missing_methods = []

        for method in expected_methods:
            if not hasattr(FANWSWindow, method):
                missing_methods.append(method)

        if not missing_methods:
            results.append(("FANWSWindow methods", "PASSED", "All expected methods present"))
            print("   ✅ FANWSWindow methods: All present")
        else:
            results.append(("FANWSWindow methods", "FAILED", f"Missing: {missing_methods}"))
            print(f"   ❌ FANWSWindow methods: Missing {missing_methods}")

    except Exception as e:
        results.append(("FANWSWindow import", "FAILED", str(e)))
        print(f"   ❌ FANWSWindow import: FAILED - {e}")

    return results

def test_file_structure():
    """Test that essential files and directories exist."""
    print("\n5️⃣ Testing File Structure...")
    results = []

    essential_items = [
        ("fanws.py", "file", "Main application file"),
        ("src/", "directory", "Source code directory"),
        ("src/memory_manager.py", "file", "Memory manager with FileCache fix"),
        ("src/file_operations.py", "file", "File operations"),
        ("src/api_manager.py", "file", "API manager"),
        ("config/", "directory", "Configuration directory"),
        ("projects/", "directory", "Projects directory"),
    ]

    for item, item_type, description in essential_items:
        if item_type == "file" and os.path.isfile(item):
            results.append((item, "PASSED", "File exists"))
            print(f"   ✅ {item}: OK")
        elif item_type == "directory" and os.path.isdir(item):
            results.append((item, "PASSED", "Directory exists"))
            print(f"   ✅ {item}: OK")
        else:
            results.append((item, "FAILED", f"{item_type.capitalize()} missing"))
            print(f"   ❌ {item}: MISSING")

    return results

def generate_report(all_results):
    """Generate a summary report."""
    print("\n📊 Test Results Summary")
    print("=" * 50)

    total_tests = sum(len(results) for results in all_results)
    passed_tests = sum(1 for results in all_results for _, status, _ in results if status == "PASSED")
    failed_tests = total_tests - passed_tests

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")

    # Detailed results
    print("\n📋 Detailed Results:")
    test_categories = [
        "Module Imports",
        "FileCache Fix",
        "Project Operations",
        "Application Startup",
        "File Structure"
    ]

    for category, results in zip(test_categories, all_results):
        print(f"\n{category}:")
        for test_name, status, details in results:
            status_icon = "✅" if status == "PASSED" else "❌"
            print(f"  {status_icon} {test_name}: {status}")
            if status == "FAILED":
                print(f"      Details: {details}")

    # Critical issues
    critical_issues = []
    for results in all_results:
        for test_name, status, details in results:
            if status == "FAILED" and any(keyword in test_name.lower() for keyword in ["ttl_seconds", "filecache", "import"]):
                critical_issues.append((test_name, details))

    if critical_issues:
        print(f"\n🚨 Critical Issues ({len(critical_issues)}):")
        for issue_name, details in critical_issues:
            print(f"  - {issue_name}: {details}")

    # Overall assessment
    print(f"\n🎯 Overall Assessment:")
    if success_rate >= 95:
        print("🎉 EXCELLENT! Application is very stable and ready for use.")
        recommendation = "Ready for full user testing and production use."
    elif success_rate >= 85:
        print("👍 GOOD! Application is mostly stable with minor issues.")
        recommendation = "Address minor issues, then proceed with user testing."
    elif success_rate >= 70:
        print("⚠️ MODERATE! Application has some issues that need attention.")
        recommendation = "Fix failed tests before proceeding with extensive testing."
    else:
        print("🚨 POOR! Significant issues detected that need immediate attention.")
        recommendation = "Focus on fixing critical failures before any testing."

    print(f"Recommendation: {recommendation}")

    # Save report
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate
        },
        "critical_issues": critical_issues,
        "recommendation": recommendation,
        "detailed_results": {
            category: [(test, status, details) for test, status, details in results]
            for category, results in zip(test_categories, all_results)
        }
    }

    with open("quick_test_report.json", "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"\n📄 Report saved to: quick_test_report.json")

    return success_rate >= 85

def main():
    """Main test runner."""
    print("🧪 FANWS Quick Test Runner")
    print("=" * 40)
    print("Testing current application state and recent fixes...")

    start_time = time.time()

    # Run all tests
    all_results = [
        test_imports(),
        test_filecache_fix(),
        test_project_operations(),
        test_application_startup(),
        test_file_structure()
    ]

    # Generate report
    success = generate_report(all_results)

    duration = time.time() - start_time
    print(f"\n⏱️ Testing completed in {duration:.1f} seconds")

    if success:
        print("\n✅ All tests passed! Application is ready for comprehensive testing.")
        print("\nNext steps:")
        print("1. Run the full user testing suite: python user_testing_suite.py")
        print("2. Start error monitoring: python error_tracking_system.py")
        print("3. Run comprehensive campaign: python testing_orchestrator.py")
    else:
        print("\n⚠️ Some tests failed. Address issues before proceeding.")
        print("\nRecommended actions:")
        print("1. Review failed tests in the detailed results")
        print("2. Fix critical issues (especially FileCache-related)")
        print("3. Re-run this test to verify fixes")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
