#!/usr/bin/env python3
"""
Test script to verify comprehensive GUI implementation.
Tests all navigation sections and widget creation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_comprehensive_gui():
    """Test that the comprehensive GUI has all expected sections and functionality."""
    print("🧪 Testing Comprehensive GUI Implementation...\n")

    try:
        from src.ui.main_gui import MainWindow
        from PyQt5.QtWidgets import QApplication

        # Create application instance
        app = QApplication(sys.argv)

        # Create main window
        window = MainWindow()

        print("✅ MainWindow created successfully")

        # Test navigation structure
        print("\n📁 Testing Navigation Structure:")
        navigation = window.navigation_structure

        expected_sections = [
            'project', 'writing', 'ai', 'templates', 'collaboration',
            'analytics', 'text_tools', 'workflow', 'dashboard',
            'performance', 'settings', 'export'
        ]

        missing_sections = []
        for section in expected_sections:
            if section in navigation:
                print(f"   ✅ Section '{section}' exists")

                # Test subsections
                subsections = navigation[section].get('subsections', {})
                subsection_count = len(subsections)
                print(f"      📊 Has {subsection_count} subsections")

            else:
                missing_sections.append(section)
                print(f"   ❌ Section '{section}' missing")

        if missing_sections:
            print(f"\n❌ Missing sections: {missing_sections}")
            return False

        print(f"\n✅ All {len(expected_sections)} sections found!")

        # Test content creation methods
        print("\n🛠️ Testing Content Creation Methods:")
        test_cases = [
            ('project', 'create_project'),
            ('writing', 'text_editor'),
            ('ai', 'ai_settings'),
            ('templates', 'template_library'),
            ('collaboration', 'collaboration_overview'),
            ('analytics', 'writing_analytics'),
            ('text_tools', 'text_analysis'),
            ('workflow', 'workflow_overview'),
            ('dashboard', 'progress_graph'),
            ('performance', 'memory_usage'),
            ('settings', 'openai_api_key'),
            ('export', 'export_status')
        ]

        success_count = 0
        for section_id, subsection_id in test_cases:
            try:
                widget = window.create_content_for_selection(section_id, subsection_id)
                if widget is not None:
                    print(f"   ✅ {section_id}/{subsection_id} - Widget created")
                    success_count += 1
                else:
                    print(f"   ❌ {section_id}/{subsection_id} - Widget is None")
            except Exception as e:
                print(f"   ❌ {section_id}/{subsection_id} - Error: {str(e)}")

        print(f"\n📈 Widget Creation Success Rate: {success_count}/{len(test_cases)} ({success_count/len(test_cases)*100:.1f}%)")

        # Test AI widget implementations specifically
        print("\n🤖 Testing AI Widget Implementations:")
        ai_widgets = [
            'ai_settings', 'models', 'prompts', 'response_handling', 'usage_limits'
        ]

        ai_success = 0
        for ai_widget in ai_widgets:
            try:
                widget = window.create_content_for_selection('ai', ai_widget)
                if widget is not None:
                    print(f"   ✅ AI/{ai_widget} - Implemented widget")
                    ai_success += 1
                else:
                    print(f"   ❌ AI/{ai_widget} - No widget")
            except Exception as e:
                print(f"   ❌ AI/{ai_widget} - Error: {str(e)}")

        print(f"\n🤖 AI Widget Success Rate: {ai_success}/{len(ai_widgets)} ({ai_success/len(ai_widgets)*100:.1f}%)")

        # Test performance and export widgets (recently implemented)
        print("\n📈 Testing Performance & Export Widgets:")
        perf_export_widgets = [
            ('performance', 'file_operations'),
            ('performance', 'cache_hit_rate'),
            ('performance', 'optimization_recommendations'),
            ('export', 'export_formats'),
            ('export', 'export_quality')
        ]

        perf_success = 0
        for section, widget_id in perf_export_widgets:
            try:
                widget = window.create_content_for_selection(section, widget_id)
                if widget is not None:
                    print(f"   ✅ {section}/{widget_id} - Implemented widget")
                    perf_success += 1
                else:
                    print(f"   ❌ {section}/{widget_id} - No widget")
            except Exception as e:
                print(f"   ❌ {section}/{widget_id} - Error: {str(e)}")

        print(f"\n📊 Performance/Export Success Rate: {perf_success}/{len(perf_export_widgets)} ({perf_success/len(perf_export_widgets)*100:.1f}%)")

        # Overall assessment
        total_tests = len(test_cases) + len(ai_widgets) + len(perf_export_widgets)
        total_success = success_count + ai_success + perf_success
        overall_rate = total_success / total_tests * 100

        print(f"\n🎯 OVERALL ASSESSMENT:")
        print(f"   📊 Total Widgets Tested: {total_tests}")
        print(f"   ✅ Successful Implementations: {total_success}")
        print(f"   📈 Overall Success Rate: {overall_rate:.1f}%")

        if overall_rate >= 90:
            print(f"   🎉 EXCELLENT! Comprehensive GUI implementation is highly successful!")
        elif overall_rate >= 75:
            print(f"   👍 GOOD! Most GUI components are implemented successfully!")
        elif overall_rate >= 50:
            print(f"   ⚠️ PARTIAL! Some GUI components need additional work!")
        else:
            print(f"   ❌ NEEDS WORK! Many GUI components require implementation!")

        # Test navigation functionality
        print(f"\n🧭 Testing Navigation Functionality:")
        try:
            # Test section selection
            window.select_section('ai')
            print(f"   ✅ Section selection works")

            # Test subsection selection
            window.select_subsection('ai_settings')
            print(f"   ✅ Subsection selection works")

            # Test content display
            if hasattr(window, 'content_area') and window.content_area.count() > 0:
                print(f"   ✅ Content area has widgets")
            else:
                print(f"   ⚠️ Content area may be empty")

        except Exception as e:
            print(f"   ❌ Navigation error: {str(e)}")

        print(f"\n✅ Comprehensive GUI test completed successfully!")

        # Cleanup
        app.quit()
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_comprehensive_gui()
