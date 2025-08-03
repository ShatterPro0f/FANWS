"""
FANWS Testing Integration & Configuration
=========================================

This script integrates with the current FANWS application state and provides
specialized testing for the recent FileCache fixes and overall system health.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_current_fanws_state():
    """Test the current state of FANWS with recent fixes."""

    print("🔍 Testing Current FANWS Application State")
    print("=" * 50)

    test_results = []

    # Test 1: Import validation
    print("\n1️⃣ Testing Module Imports...")
    import_results = test_module_imports()
    test_results.extend(import_results)

    # Test 2: FileCache fix validation
    print("\n2️⃣ Testing FileCache Fix...")
    cache_results = test_filecache_fix()
    test_results.extend(cache_results)

    # Test 3: Project file operations
    print("\n3️⃣ Testing Project File Operations...")
    project_results = test_project_operations()
    test_results.extend(project_results)

    # Test 4: Configuration system
    print("\n4️⃣ Testing Configuration System...")
    config_results = test_configuration_system()
    test_results.extend(config_results)

    # Test 5: API Manager
    print("\n5️⃣ Testing API Manager...")
    api_results = test_api_manager()
    test_results.extend(api_results)

    # Test 6: Application startup
    print("\n6️⃣ Testing Application Startup...")
    startup_results = test_application_startup()
    test_results.extend(startup_results)

    # Generate report
    generate_state_report(test_results)

    return test_results

def test_module_imports():
    """Test that all required modules can be imported."""
    results = []

    modules_to_test = [
        ("fanws", "Main application module"),
        ("src.memory_manager", "Memory management with FileCache fix"),
        ("src.file_operations", "File operations"),
        ("src.api_manager", "API management"),
        ("src.text_processing", "Text processing"),
        ("src.error_handling_system", "Error handling"),
        ("src.configuration_manager", "Configuration management"),
    ]

    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            results.append({
                "test": f"Import {module_name}",
                "status": "PASSED",
                "description": description,
                "details": "Module imported successfully"
            })
            print(f"   ✅ {module_name}: OK")
        except ImportError as e:
            results.append({
                "test": f"Import {module_name}",
                "status": "FAILED",
                "description": description,
                "details": f"Import error: {str(e)}",
                "error": str(e)
            })
            print(f"   ❌ {module_name}: FAILED - {str(e)}")
        except Exception as e:
            results.append({
                "test": f"Import {module_name}",
                "status": "ERROR",
                "description": description,
                "details": f"Unexpected error: {str(e)}",
                "error": str(e)
            })
            print(f"   🚨 {module_name}: ERROR - {str(e)}")

    return results

def test_filecache_fix():
    """Test the recent FileCache ttl_seconds fix."""
    results = []

    try:
        from src.memory_manager import FileCache, ProjectFileCache

        # Test 1: FileCache with ttl_seconds
        try:
            cache = FileCache(ttl_seconds=300)
            results.append({
                "test": "FileCache with ttl_seconds",
                "status": "PASSED",
                "description": "FileCache accepts ttl_seconds parameter",
                "details": "Successfully created FileCache with ttl_seconds=300"
            })
            print("   ✅ FileCache with ttl_seconds: OK")
        except Exception as e:
            results.append({
                "test": "FileCache with ttl_seconds",
                "status": "FAILED",
                "description": "FileCache should accept ttl_seconds parameter",
                "details": f"Error: {str(e)}",
                "error": str(e)
            })
            print(f"   ❌ FileCache with ttl_seconds: FAILED - {str(e)}")

        # Test 2: ProjectFileCache functionality
        try:
            project_cache = ProjectFileCache("test_project")
            project_cache.update("test_file.txt", "test content")
            content = project_cache.get("test_file.txt")

            if content == "test content":
                results.append({
                    "test": "ProjectFileCache operations",
                    "status": "PASSED",
                    "description": "ProjectFileCache basic operations",
                    "details": "Successfully stored and retrieved content"
                })
                print("   ✅ ProjectFileCache operations: OK")
            else:
                results.append({
                    "test": "ProjectFileCache operations",
                    "status": "FAILED",
                    "description": "ProjectFileCache basic operations",
                    "details": f"Expected 'test content', got '{content}'",
                    "error": "Content mismatch"
                })
                print(f"   ❌ ProjectFileCache operations: FAILED - Content mismatch")
        except Exception as e:
            results.append({
                "test": "ProjectFileCache operations",
                "status": "FAILED",
                "description": "ProjectFileCache basic operations",
                "details": f"Error: {str(e)}",
                "error": str(e)
            })
            print(f"   ❌ ProjectFileCache operations: FAILED - {str(e)}")

        # Test 3: API Manager and Text Analyzer with ttl_seconds
        try:
            from src.api_manager import APIManager
            from src.text_processing import TextAnalyzer

            api_manager = APIManager()
            text_analyzer = TextAnalyzer()

            results.append({
                "test": "API Manager and Text Analyzer initialization",
                "status": "PASSED",
                "description": "Components that use MemoryCache with ttl_seconds",
                "details": "Successfully initialized without ttl_seconds errors"
            })
            print("   ✅ API Manager and Text Analyzer: OK")
        except Exception as e:
            results.append({
                "test": "API Manager and Text Analyzer initialization",
                "status": "FAILED",
                "description": "Components that use MemoryCache with ttl_seconds",
                "details": f"Error: {str(e)}",
                "error": str(e)
            })
            print(f"   ❌ API Manager and Text Analyzer: FAILED - {str(e)}")

    except ImportError as e:
        results.append({
            "test": "FileCache module import",
            "status": "FAILED",
            "description": "Import memory_manager module",
            "details": f"Import error: {str(e)}",
            "error": str(e)
        })
        print(f"   ❌ Memory manager import: FAILED - {str(e)}")

    return results

def test_project_operations():
    """Test project file operations."""
    results = []

    try:
        from src.file_operations import get_project_list, validate_project_name

        # Test project list
        try:
            projects = get_project_list()
            results.append({
                "test": "Get project list",
                "status": "PASSED",
                "description": "Retrieve list of existing projects",
                "details": f"Found {len(projects)} projects: {projects[:3]}..." if len(projects) > 3 else f"Found projects: {projects}"
            })
            print(f"   ✅ Project list: OK ({len(projects)} projects)")
        except Exception as e:
            results.append({
                "test": "Get project list",
                "status": "FAILED",
                "description": "Retrieve list of existing projects",
                "details": f"Error: {str(e)}",
                "error": str(e)
            })
            print(f"   ❌ Project list: FAILED - {str(e)}")

        # Test project name validation
        try:
            valid_name = validate_project_name("test_project")
            invalid_name = validate_project_name("test/project")

            if valid_name and not invalid_name:
                results.append({
                    "test": "Project name validation",
                    "status": "PASSED",
                    "description": "Validate project names",
                    "details": "Correctly validated valid and invalid names"
                })
                print("   ✅ Project name validation: OK")
            else:
                results.append({
                    "test": "Project name validation",
                    "status": "FAILED",
                    "description": "Validate project names",
                    "details": f"Validation logic error: valid='{valid_name}', invalid='{invalid_name}'",
                    "error": "Validation logic error"
                })
                print("   ❌ Project name validation: FAILED - Logic error")
        except Exception as e:
            results.append({
                "test": "Project name validation",
                "status": "FAILED",
                "description": "Validate project names",
                "details": f"Error: {str(e)}",
                "error": str(e)
            })
            print(f"   ❌ Project name validation: FAILED - {str(e)}")

    except ImportError as e:
        results.append({
            "test": "File operations import",
            "status": "FAILED",
            "description": "Import file_operations module",
            "details": f"Import error: {str(e)}",
            "error": str(e)
        })
        print(f"   ❌ File operations import: FAILED - {str(e)}")

    return results

def test_configuration_system():
    """Test configuration management system."""
    results = []

    try:
        # Test configuration files exist
        config_files = [
            "config/app_config.json",
            "config/development.json",
            "config/production.json",
            "config/testing.json"
        ]

        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    results.append({
                        "test": f"Configuration file {config_file}",
                        "status": "PASSED",
                        "description": f"Load {config_file}",
                        "details": f"Successfully loaded with {len(config_data)} settings"
                    })
                    print(f"   ✅ {config_file}: OK")
                except Exception as e:
                    results.append({
                        "test": f"Configuration file {config_file}",
                        "status": "FAILED",
                        "description": f"Load {config_file}",
                        "details": f"Parse error: {str(e)}",
                        "error": str(e)
                    })
                    print(f"   ❌ {config_file}: FAILED - {str(e)}")
            else:
                results.append({
                    "test": f"Configuration file {config_file}",
                    "status": "FAILED",
                    "description": f"Check {config_file} exists",
                    "details": "File not found",
                    "error": "File not found"
                })
                print(f"   ❌ {config_file}: NOT FOUND")

    except Exception as e:
        results.append({
            "test": "Configuration system",
            "status": "ERROR",
            "description": "Test configuration system",
            "details": f"Unexpected error: {str(e)}",
            "error": str(e)
        })
        print(f"   🚨 Configuration system: ERROR - {str(e)}")

    return results

def test_api_manager():
    """Test API manager functionality."""
    results = []

    try:
        from src.api_manager import APIManager

        # Test initialization
        try:
            api_manager = APIManager()
            results.append({
                "test": "API Manager initialization",
                "status": "PASSED",
                "description": "Initialize API manager",
                "details": "Successfully created API manager instance"
            })
            print("   ✅ API Manager initialization: OK")
        except Exception as e:
            results.append({
                "test": "API Manager initialization",
                "status": "FAILED",
                "description": "Initialize API manager",
                "details": f"Error: {str(e)}",
                "error": str(e)
            })
            print(f"   ❌ API Manager initialization: FAILED - {str(e)}")

    except ImportError as e:
        results.append({
            "test": "API Manager import",
            "status": "FAILED",
            "description": "Import API manager module",
            "details": f"Import error: {str(e)}",
            "error": str(e)
        })
        print(f"   ❌ API Manager import: FAILED - {str(e)}")

    return results

def test_application_startup():
    """Test application startup without GUI."""
    results = []

    try:
        # Test main application class import
        from fanws import FANWSWindow

        results.append({
            "test": "Application class import",
            "status": "PASSED",
            "description": "Import main application class",
            "details": "Successfully imported FANWSWindow"
        })
        print("   ✅ Application class import: OK")

        # Note: We don't actually create the window here to avoid GUI dependencies
        # in automated testing, but we verify the class can be imported

    except Exception as e:
        results.append({
            "test": "Application class import",
            "status": "FAILED",
            "description": "Import main application class",
            "details": f"Error: {str(e)}",
            "error": str(e)
        })
        print(f"   ❌ Application class import: FAILED - {str(e)}")

    return results

def generate_state_report(test_results):
    """Generate a report of the current application state."""

    # Calculate statistics
    total_tests = len(test_results)
    passed_tests = len([r for r in test_results if r["status"] == "PASSED"])
    failed_tests = len([r for r in test_results if r["status"] == "FAILED"])
    error_tests = len([r for r in test_results if r["status"] == "ERROR"])

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    # Create report
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_summary": {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "success_rate": success_rate
        },
        "test_results": test_results,
        "recommendations": generate_recommendations(test_results),
        "next_steps": generate_next_steps(test_results)
    }

    # Save report
    with open("fanws_state_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print(f"\n📊 FANWS State Test Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Errors: {error_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")

    if success_rate >= 90:
        print("   🎉 Excellent! Application state is very healthy.")
    elif success_rate >= 75:
        print("   👍 Good! Minor issues detected.")
    elif success_rate >= 50:
        print("   ⚠️ Moderate issues detected. Review failures.")
    else:
        print("   🚨 Significant issues detected. Immediate attention required.")

    print(f"\n📄 Detailed report saved to: fanws_state_report.json")

    return report

def generate_recommendations(test_results):
    """Generate recommendations based on test results."""
    recommendations = []

    failed_tests = [r for r in test_results if r["status"] in ["FAILED", "ERROR"]]

    # Check for specific failure patterns
    cache_failures = [r for r in failed_tests if "cache" in r["test"].lower()]
    if cache_failures:
        recommendations.append("🔄 Cache system issues detected - review FileCache and ProjectFileCache implementations")

    import_failures = [r for r in failed_tests if "import" in r["test"].lower()]
    if import_failures:
        recommendations.append("📦 Module import issues detected - check dependencies and file structure")

    config_failures = [r for r in failed_tests if "config" in r["test"].lower()]
    if config_failures:
        recommendations.append("⚙️ Configuration issues detected - verify config files and settings")

    api_failures = [r for r in failed_tests if "api" in r["test"].lower()]
    if api_failures:
        recommendations.append("🌐 API system issues detected - review API manager and integrations")

    if len(failed_tests) == 0:
        recommendations.append("✅ All systems operational - ready for user testing")

    return recommendations

def generate_next_steps(test_results):
    """Generate next steps based on test results."""
    failed_tests = [r for r in test_results if r["status"] in ["FAILED", "ERROR"]]

    if not failed_tests:
        return [
            "Run full user testing suite with UI interactions",
            "Test project creation and workflow execution",
            "Validate API integrations with real keys",
            "Perform stress testing with large projects"
        ]

    next_steps = []

    # Priority order for fixes
    critical_areas = [
        ("cache", "Fix cache system issues"),
        ("import", "Resolve module import problems"),
        ("config", "Fix configuration system"),
        ("api", "Resolve API manager issues")
    ]

    for area, action in critical_areas:
        area_failures = [r for r in failed_tests if area in r["test"].lower()]
        if area_failures:
            next_steps.append(f"{action} ({len(area_failures)} issues)")

    next_steps.append("Re-run state tests after fixes")
    next_steps.append("Proceed with full user testing suite")

    return next_steps

def create_continuous_testing_config():
    """Create configuration for continuous testing."""

    config = {
        "testing_schedule": {
            "quick_tests": "every_startup",
            "full_tests": "daily",
            "stress_tests": "weekly"
        },
        "test_categories": {
            "critical": ["imports", "cache_operations", "project_loading"],
            "important": ["configuration", "api_manager", "file_operations"],
            "optional": ["performance", "ui_responsiveness", "memory_usage"]
        },
        "failure_actions": {
            "critical_failure": "stop_application",
            "important_failure": "log_and_continue",
            "optional_failure": "log_only"
        },
        "reporting": {
            "save_logs": True,
            "email_alerts": False,
            "console_output": True
        }
    }

    with open("testing_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("📋 Continuous testing configuration saved to: testing_config.json")

def main():
    """Main entry point for state testing."""
    print("🔧 FANWS State Testing & Validation")
    print("=" * 40)

    # Test current state
    test_results = test_current_fanws_state()

    # Create testing configuration
    create_continuous_testing_config()

    print("\n🎯 State testing complete!")
    print("\nNext: Run the full user testing suite with:")
    print("   python user_testing_suite.py")

if __name__ == "__main__":
    main()
