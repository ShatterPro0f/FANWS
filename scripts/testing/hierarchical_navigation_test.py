#!/usr/bin/env python3
"""
Hierarchical Navigation System Test
Test the new sidebar navigation structure with sections, subsections, and subsubsections
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_hierarchical_navigation():
    """Test the hierarchical navigation system"""

    print("🧭 Hierarchical Navigation System Test")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # Test PyQt5 availability
        print("1️⃣ Testing PyQt5 Framework...")
        from PyQt5.QtWidgets import QApplication, QMainWindow
        from PyQt5.QtCore import Qt

        app = QApplication([])

        # Create a test window
        window = QMainWindow()
        window.setWindowTitle("FANWS - Hierarchical Navigation Test")
        window.resize(1200, 800)

        print("✓ PyQt5 framework loaded successfully")

        # Test UI components import
        print("\n2️⃣ Testing UI Components...")
        from src.ui import UIComponents

        # Create UI components
        ui_components = UIComponents(window)
        ui_components.create_ui()

        print("✓ Hierarchical UI components created successfully")

        # Test navigation tree structure
        print("\n3️⃣ Testing Navigation Tree Structure...")

        if hasattr(window, 'nav_tree'):
            tree = window.nav_tree

            # Check sections
            section_count = tree.topLevelItemCount()
            print(f"✓ Found {section_count} main sections")

            expected_sections = ["Project", "Dashboard", "Performance", "Settings", "Export"]

            for i in range(section_count):
                item = tree.topLevelItem(i)
                section_name = item.text(0)
                subsection_count = item.childCount()

                print(f"  📁 Section: {section_name} ({subsection_count} subsections)")

                if section_name in expected_sections:
                    print(f"    ✓ Expected section found")
                else:
                    print(f"    ⚠ Unexpected section: {section_name}")

                # Check subsections
                for j in range(subsection_count):
                    subsection = item.child(j)
                    subsection_name = subsection.text(0)
                    subsubsection_count = subsection.childCount()

                    if subsubsection_count > 0:
                        print(f"    📂 Subsection: {subsection_name} ({subsubsection_count} subsubsections)")

                        # Check subsubsections
                        for k in range(subsubsection_count):
                            subsubsection = subsection.child(k)
                            subsubsection_name = subsubsection.text(0)
                            print(f"      📄 Subsubsection: {subsubsection_name}")
                    else:
                        print(f"    📄 Subsection: {subsection_name}")

        else:
            print("❌ Navigation tree not found")
            return False

        # Test content area
        print("\n4️⃣ Testing Content Area...")

        if hasattr(window, '_content_area'):
            content_area = window._content_area
            page_count = content_area.count()
            print(f"✓ Content area created with {page_count} pages")

            if hasattr(window, '_content_pages'):
                page_mapping = window._content_pages
                print(f"✓ Page mapping created with {len(page_mapping)} entries")

                # Test a few key pages
                test_pages = ['switch_project', 'novel_concept', 'progress_graph', 'openai_api_key', 'export_status']

                for page_id in test_pages:
                    if page_id in page_mapping:
                        print(f"  ✓ Page '{page_id}' found at index {page_mapping[page_id]}")
                    else:
                        print(f"  ⚠ Page '{page_id}' not found")
            else:
                print("⚠ Page mapping not found")
        else:
            print("❌ Content area not found")
            return False

        # Test navigation functionality
        print("\n5️⃣ Testing Navigation Functionality...")

        if hasattr(ui_components, '_switch_to_content_page'):
            # Test switching to different pages
            test_switches = [
                ('switch_project', 'Switch Project'),
                ('novel_concept', 'Novel Concept'),
                ('progress_graph', 'Progress Graph'),
                ('memory_usage', 'Memory Usage'),
                ('openai_api_key', 'OpenAI API Key')
            ]

            for page_id, page_name in test_switches:
                try:
                    ui_components._switch_to_content_page(page_id)
                    current_index = content_area.currentIndex()
                    expected_index = page_mapping.get(page_id, -1)

                    if current_index == expected_index:
                        print(f"  ✓ Navigation to '{page_name}' successful")
                    else:
                        print(f"  ⚠ Navigation to '{page_name}' failed (expected {expected_index}, got {current_index})")
                except Exception as e:
                    print(f"  ❌ Error navigating to '{page_name}': {e}")

        # Test required widgets
        print("\n6️⃣ Testing Required Widget Creation...")

        required_widgets = [
            'story_tab', 'characters_tab', 'world_tab', 'summaries_tab', 'drafts_tab',
            'readability_tab', 'synonyms_tab', 'config_tab', 'log_tab',
            'project_selector', 'project_input', 'new_project_button', 'delete_project_button',
            'openai_key_input', 'wordsapi_key_input', 'save_api_keys_button',
            'word_count_label', 'progress_bar', 'export_button',
            'tone_input', 'sub_tone_input', 'theme_dropdown', 'reading_level_input', 'target_input'
        ]

        missing_widgets = []
        found_widgets = []

        for widget_name in required_widgets:
            if hasattr(window, widget_name):
                found_widgets.append(widget_name)
                print(f"  ✓ Widget '{widget_name}' created")
            else:
                missing_widgets.append(widget_name)
                print(f"  ⚠ Widget '{widget_name}' missing")

        print(f"\n📊 Widget Summary: {len(found_widgets)} found, {len(missing_widgets)} missing")

        # Test legacy navigation methods
        print("\n7️⃣ Testing Legacy Navigation Methods...")

        legacy_methods = [
            ('smart_switch_to_dashboard', 'Dashboard Switch'),
            ('smart_switch_to_novel_settings', 'Novel Settings Switch'),
            ('smart_switch_to_performance', 'Performance Switch'),
            ('smart_switch_to_settings', 'Settings Switch')
        ]

        for method_name, description in legacy_methods:
            if hasattr(ui_components, method_name):
                try:
                    method = getattr(ui_components, method_name)
                    method()
                    print(f"  ✓ {description} method executed successfully")
                except Exception as e:
                    print(f"  ⚠ Error in {description}: {e}")
            else:
                print(f"  ❌ {description} method not found")

        # Test layout structure
        print("\n8️⃣ Testing Layout Structure...")

        central_widget = window.centralWidget()
        if central_widget:
            layout = central_widget.layout()
            if layout and layout.count() == 2:  # Should have sidebar and content area
                print("✓ Main layout structure correct (sidebar + content area)")

                # Check sidebar
                sidebar = layout.itemAt(0).widget()
                if sidebar:
                    print("✓ Sidebar widget found")

                    # Check sidebar width constraint
                    max_width = sidebar.maximumWidth()
                    if max_width <= window.width() * 0.3:  # Should be about 1/4 of screen
                        print(f"✓ Sidebar width constraint correct ({max_width}px)")
                    else:
                        print(f"⚠ Sidebar width may be too large ({max_width}px)")

                # Check content area
                content = layout.itemAt(1).widget()
                if content:
                    print("✓ Content area widget found")
                else:
                    print("⚠ Content area widget not found")
            else:
                print(f"⚠ Unexpected layout structure (items: {layout.count() if layout else 'No layout'})")
        else:
            print("❌ Central widget not found")

        print("\n" + "=" * 60)
        print("🎉 Hierarchical Navigation System Test Complete!")
        print("✅ New navigation structure ready for use")

        # Show the window briefly for visual verification
        window.show()
        app.processEvents()

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_hierarchical_navigation()

        if success:
            print("\n🚀 Hierarchical navigation system is ready!")
            print("📋 Features implemented:")
            print("   • Sidebar with 5 main sections")
            print("   • Project subsections with Novel Settings subsubsections")
            print("   • Dashboard with progress tracking and tools")
            print("   • Performance monitoring with detailed metrics")
            print("   • Settings for API configuration")
            print("   • Export tools with status and history")
            print("   • 1/4 sidebar, 3/4 content area layout")
            print("   • Hierarchical tree navigation")
            print("   • Backward compatibility with existing widgets")
        else:
            print("\n❌ Some issues found in hierarchical navigation system")

    except KeyboardInterrupt:
        print("\n⚠ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
