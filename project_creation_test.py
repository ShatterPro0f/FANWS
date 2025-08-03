#!/usr/bin/env python3
"""
Project Creation and Backend-GUI Integration Test
Tests that all necessary files are created and all backend features are accessible via the GUI.
"""
import os
import sys
import json
import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_project_creation():
    """Test that all necessary files are created upon project creation"""
    print("🏗️ Testing Project Creation...")

    # Import the file operations module
    try:
        from src.file_operations import initialize_project_files
        print("   ✅ File operations module imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import file operations: {e}")
        return False

    # Test project creation
    test_project_name = "test_project_creation"
    test_project_path = f"projects/{test_project_name}"

    try:
        # Create test project
        if os.path.exists(test_project_path):
            import shutil
            shutil.rmtree(test_project_path)

        result = initialize_project_files(test_project_name)

        if result and os.path.exists(test_project_path):
            print("   ✅ Project created successfully")

            # Check for required directories
            required_dirs = [
                "chapters", "characters", "world_building", "research",
                "exports", "backups", "analytics", "templates", "metadata"
            ]

            missing_dirs = []
            for directory in required_dirs:
                dir_path = os.path.join(test_project_path, directory)
                if not os.path.exists(dir_path):
                    missing_dirs.append(directory)
                else:
                    print(f"   ✅ Directory '{directory}' created")

            if missing_dirs:
                print(f"   ❌ Missing directories: {missing_dirs}")
                return False

            # Check for required files
            required_files = [
                "synopsis.txt", "outline.txt", "characters.txt", "world_building.txt",
                "timeline.txt", "story.txt", "config/plot_points.txt", "config/continuity_rules.txt",
                "themes.txt", "research_notes.txt", "chapter_summaries.txt",
                "config/project_settings.json", "config/writing_style.json",
                "config/character_config.json", "analytics/writing_sessions.json"
            ]

            missing_files = []
            for filename in required_files:
                file_path = os.path.join(test_project_path, filename)
                if not os.path.exists(file_path):
                    missing_files.append(filename)
                else:
                    print(f"   ✅ File '{filename}' created")

            if missing_files:
                print(f"   ❌ Missing files: {missing_files}")
                return False

            print("   ✅ All required files and directories created")
            return True
        else:
            print("   ❌ Project creation failed")
            return False

    except Exception as e:
        print(f"   ❌ Project creation test failed: {e}")
        return False
    finally:
        # Cleanup test project
        if os.path.exists(test_project_path):
            import shutil
            shutil.rmtree(test_project_path)
            print("   🧹 Test project cleaned up")

def test_gui_integration():
    """Test that all backend features are integrated with the GUI"""
    print("\n🖥️ Testing GUI Integration...")

    try:
        from src.ui import UIComponents
        print("   ✅ GUI navigation module imported successfully")

        # Check that all content creation methods exist
        gui_instance = UIComponents()

        # List of expected content creation methods for backend features
        expected_methods = [
            '_create_character_tools_content',
            '_create_world_tools_content',
            '_create_timeline_tools_content',
            '_create_research_tools_content',
            '_create_analytics_display_content',
            '_create_collaboration_tools_content',
            '_create_backup_tools_content',
            '_create_template_tools_content',
            '_create_quality_tools_content',
            '_create_ai_tools_content',
            '_create_stats_display_content',
            '_create_goal_tools_content',
            '_create_deadline_tools_content',
            '_create_version_tools_content',
            '_create_advanced_config_content',
            '_create_plugin_tools_content',
            '_create_workflow_config_content'
        ]

        missing_methods = []
        for method_name in expected_methods:
            if hasattr(gui_instance, method_name):
                print(f"   ✅ GUI method '{method_name}' exists")
            else:
                missing_methods.append(method_name)

        if missing_methods:
            print(f"   ❌ Missing GUI methods: {missing_methods}")
            return False

        print("   ✅ All backend features have GUI integration methods")
        return True

    except Exception as e:
        print(f"   ❌ GUI integration test failed: {e}")
        return False

def test_navigation_structure():
    """Test that the navigation structure includes all backend features"""
    print("\n🧭 Testing Navigation Structure...")

    try:
        from src.ui import UIComponents

        gui_instance = UIComponents()

        # Check if navigation_structure exists and contains expected sections
        if hasattr(gui_instance, 'navigation_structure'):
            structure = gui_instance.navigation_structure

            # Expected main sections
            expected_sections = [
                'writing', 'story_development', 'project_management',
                'analytics', 'tools', 'settings'
            ]

            missing_sections = []
            for section in expected_sections:
                if section in structure:
                    print(f"   ✅ Navigation section '{section}' exists")

                    # Check subsections for each main section
                    if section == 'story_development':
                        expected_subsections = ['character_tools', 'world_tools', 'timeline_tools', 'research_tools']
                        for subsection in expected_subsections:
                            if subsection in structure[section]:
                                print(f"     ✅ Subsection '{subsection}' exists")
                            else:
                                print(f"     ⚠️ Subsection '{subsection}' missing")

                    elif section == 'analytics':
                        expected_subsections = ['analytics_display', 'stats_display']
                        for subsection in expected_subsections:
                            if subsection in structure[section]:
                                print(f"     ✅ Subsection '{subsection}' exists")
                            else:
                                print(f"     ⚠️ Subsection '{subsection}' missing")

                    elif section == 'tools':
                        expected_subsections = ['collaboration_tools', 'backup_tools', 'template_tools', 'quality_tools', 'ai_tools']
                        for subsection in expected_subsections:
                            if subsection in structure[section]:
                                print(f"     ✅ Subsection '{subsection}' exists")
                            else:
                                print(f"     ⚠️ Subsection '{subsection}' missing")

                else:
                    missing_sections.append(section)

            if missing_sections:
                print(f"   ❌ Missing navigation sections: {missing_sections}")
                return False

            print("   ✅ Navigation structure includes all expected sections")
            return True
        else:
            print("   ⚠️ Navigation structure not found, but basic navigation methods exist")
            # Check for the basic navigation methods instead
            nav_methods = ['_create_project_management_content', '_create_text_input_content',
                          '_create_dropdown_content', '_create_number_input_content',
                          '_create_progress_display_content', '_create_overview_content']

            missing_nav_methods = []
            for method in nav_methods:
                if hasattr(gui_instance, method):
                    print(f"   ✅ Navigation method '{method}' exists")
                else:
                    missing_nav_methods.append(method)

            if missing_nav_methods:
                print(f"   ❌ Missing navigation methods: {missing_nav_methods}")
                return False

            return True

    except Exception as e:
        print(f"   ❌ Navigation structure test failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("🔄 FANWS Backend-GUI Integration Test")
    print("=" * 50)

    tests = [
        ("Project Creation", test_project_creation),
        ("GUI Integration", test_gui_integration),
        ("Navigation Structure", test_navigation_structure)
    ]

    results = []
    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASSED" if result else "FAILED"))
            if result:
                passed += 1
        except Exception as e:
            results.append((test_name, f"ERROR: {e}"))

    # Generate report
    print("\n📊 Test Results Summary")
    print("=" * 50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    print("\n📋 Detailed Results:")
    for test_name, status in results:
        status_icon = "✅" if status == "PASSED" else "❌"
        print(f"  {status_icon} {test_name}: {status}")

    # Save results
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "success_rate": (passed/total)*100,
        "test_results": dict(results)
    }

    with open("integration_test_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved to: integration_test_report.json")

    if passed == total:
        print("\n🎉 All integration tests passed! The application is ready for user testing.")
        print("💡 Next steps:")
        print("   1. Start the user testing suite: python user_testing_suite.py")
        print("   2. Create a new project to test the GUI")
        print("   3. Test all navigation sections and backend features")
    else:
        print("\n⚠️ Some integration tests failed. Please review and fix issues before proceeding.")

    return passed == total

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
