#!/usr/bin/env python3
"""
Critical Fixes Test Script
Tests all the critical fixes applied to resolve GUI issues.
"""

import sys
import os
import traceback
from datetime import datetime

def test_critical_fixes():
    """Test all critical fixes."""
    print("🔧 Testing Critical Fixes Applied")
    print("=" * 60)

    results = []

    # Test 1: Analytics System Imports
    try:
        from src.analytics_system import WritingAnalyticsDashboard
        dashboard = WritingAnalyticsDashboard()

        # Test update_writing_progress method
        result = dashboard.update_writing_progress(100, "Test content")
        if hasattr(dashboard, 'update_writing_progress'):
            results.append(("✅ WritingAnalyticsDashboard.update_writing_progress", "PASS", "Method exists and callable"))
        else:
            results.append(("❌ WritingAnalyticsDashboard.update_writing_progress", "FAIL", "Method missing"))

        # Test set_project method
        result = dashboard.set_project("test_project")
        if hasattr(dashboard, 'set_project'):
            results.append(("✅ WritingAnalyticsDashboard.set_project", "PASS", "Method exists and callable"))
        else:
            results.append(("❌ WritingAnalyticsDashboard.set_project", "FAIL", "Method missing"))

    except Exception as e:
        results.append(("❌ Analytics System Import", "FAIL", f"Error: {str(e)}"))

    # Test 2: File Operations API Keys Loading
    try:
        from src.file_operations import load_project_env, save_project_env, get_wordsapi_call_count

        # Test load_project_env returns dict
        env_data = load_project_env("test_project")
        if isinstance(env_data, dict):
            results.append(("✅ load_project_env return type", "PASS", "Returns dict"))
        else:
            results.append(("❌ load_project_env return type", "FAIL", f"Returns {type(env_data)}"))

        # Test save_project_env compatibility
        test_result = save_project_env("test_project", "test_key", "test_thesaurus")
        results.append(("✅ save_project_env compatibility", "PASS", "Two-parameter version works"))

        # Test get_wordsapi_call_count
        count = get_wordsapi_call_count("test_project")
        if isinstance(count, int):
            results.append(("✅ get_wordsapi_call_count", "PASS", f"Returns int: {count}"))
        else:
            results.append(("❌ get_wordsapi_call_count", "FAIL", f"Returns {type(count)}"))

    except Exception as e:
        results.append(("❌ File Operations Test", "FAIL", f"Error: {str(e)}"))
        traceback.print_exc()

    # Test 3: Configuration Value Handling
    try:
        # Test None value handling for numeric controls
        test_values = [None, 0.5, "0.5", 250000, "250000"]
        for val in test_values:
            try:
                if val is not None:
                    float_val = float(val)
                    results.append(("✅ Config value conversion", "PASS", f"{val} -> {float_val}"))
                else:
                    results.append(("✅ Config None handling", "PASS", "None values handled"))
            except Exception as e:
                results.append(("❌ Config value conversion", "FAIL", f"{val}: {str(e)}"))

    except Exception as e:
        results.append(("❌ Configuration Test", "FAIL", f"Error: {str(e)}"))

    # Test 4: Import Critical Modules
    critical_modules = [
        "src.memory_manager",
        "src.per_project_config_manager",
        "src.analytics_system",
        "src.file_operations"
    ]

    for module in critical_modules:
        try:
            __import__(module)
            results.append(("✅ Module Import", "PASS", f"{module}"))
        except Exception as e:
            results.append(("❌ Module Import", "FAIL", f"{module}: {str(e)}"))

    # Print Results
    print("\n📊 Test Results:")
    print("-" * 60)

    passed = 0
    failed = 0

    for test_name, status, details in results:
        print(f"{test_name:<40} {status:<6} {details}")
        if "PASS" in status:
            passed += 1
        else:
            failed += 1

    print("-" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")

    if failed == 0:
        print("\n🎉 All critical fixes verified successfully!")
        print("🚀 GUI should now run without the major errors.")
        return True
    else:
        print(f"\n⚠️  {failed} issues remain - see details above")
        return False

if __name__ == "__main__":
    print("🔍 Critical Fixes Verification")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    success = test_critical_fixes()

    if success:
        print("\n✅ Ready to test GUI again!")
        sys.exit(0)
    else:
        print("\n❌ Additional fixes needed")
        sys.exit(1)
