#!/usr/bin/env python3
"""
Navigation Button Test Script
Tests that all navigation buttons are functioning correctly.
"""

import sys
import os
import traceback
import time
from datetime import datetime

def test_navigation_buttons():
    """Test navigation button functionality."""
    print("🧭 Testing Navigation Button Functionality")
    print("=" * 60)

    results = []

    try:
        # Test 1: Import GUI Framework
        from PyQt5.QtWidgets import QApplication
        from fanws import FANWSWindow

        # Create application if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create window instance (but don't show it)
        window = FANWSWindow()

        results.append(("✅ GUI Framework Import", "PASS", "Successfully imported and created window"))

        # Test 2: Check Navigation Button Existence
        nav_buttons = [
            'show_dashboard_button',
            'show_novel_settings_button',
            'show_advanced_settings_button',
            'show_performance_button',
            'show_settings_button'
        ]

        for button_name in nav_buttons:
            if hasattr(window, button_name):
                button = getattr(window, button_name)
                if button and hasattr(button, 'clicked'):
                    results.append((f"✅ {button_name}", "PASS", "Button exists and has clicked signal"))
                else:
                    results.append((f"❌ {button_name}", "FAIL", "Button exists but no clicked signal"))
            else:
                results.append((f"❌ {button_name}", "FAIL", "Button does not exist"))

        # Test 3: Check UI Component Methods
        ui_methods = [
            'smart_switch_to_dashboard',
            'smart_switch_to_novel_settings',
            'switch_to_settings',
            'smart_switch_to_performance',
            'smart_switch_to_settings'
        ]

        for method_name in ui_methods:
            if hasattr(window.ui, method_name):
                method = getattr(window.ui, method_name)
                if callable(method):
                    results.append((f"✅ UI.{method_name}", "PASS", "Method exists and callable"))
                else:
                    results.append((f"❌ UI.{method_name}", "FAIL", "Method exists but not callable"))
            else:
                results.append((f"❌ UI.{method_name}", "FAIL", "Method does not exist"))

        # Test 4: Test Method Execution (without showing GUI)
        test_methods = [
            ('smart_switch_to_dashboard', 'Dashboard'),
            ('smart_switch_to_novel_settings', 'Novel Settings'),
            ('smart_switch_to_performance', 'Performance'),
            ('smart_switch_to_settings', 'Settings')
        ]

        for method_name, display_name in test_methods:
            try:
                if hasattr(window.ui, method_name):
                    method = getattr(window.ui, method_name)
                    method()  # Call the method
                    results.append((f"✅ Execute {display_name}", "PASS", f"Method {method_name} executed without error"))
                else:
                    results.append((f"❌ Execute {display_name}", "FAIL", f"Method {method_name} not found"))
            except Exception as e:
                results.append((f"❌ Execute {display_name}", "FAIL", f"Error: {str(e)}"))

        # Test 5: Check Tab Widget Existence
        try:
            from PyQt5.QtWidgets import QTabWidget
            central_widget = window.centralWidget()
            if central_widget:
                tab_widgets = central_widget.findChildren(QTabWidget)
                if tab_widgets:
                    tab_widget = tab_widgets[0]
                    tab_count = tab_widget.count()
                    tab_names = [tab_widget.tabText(i) for i in range(tab_count)]
                    results.append(("✅ Tab Widget", "PASS", f"Found {tab_count} tabs: {', '.join(tab_names)}"))
                else:
                    results.append(("❌ Tab Widget", "FAIL", "No QTabWidget found in central widget"))
            else:
                results.append(("❌ Central Widget", "FAIL", "No central widget found"))
        except Exception as e:
            results.append(("❌ Tab Widget Check", "FAIL", f"Error: {str(e)}"))

        # Clean up
        window.close()

    except Exception as e:
        results.append(("❌ Navigation Test Setup", "FAIL", f"Setup error: {str(e)}"))
        traceback.print_exc()

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
        print("\n🎉 All navigation tests passed!")
        print("🧭 Navigation buttons should be functional.")
        return True
    else:
        print(f"\n⚠️  {failed} navigation issues found - see details above")
        return False

if __name__ == "__main__":
    print("🧭 Navigation Button Test Suite")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        success = test_navigation_buttons()

        if success:
            print("\n✅ Navigation system ready!")
            sys.exit(0)
        else:
            print("\n❌ Navigation issues detected")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        traceback.print_exc()
        sys.exit(1)
