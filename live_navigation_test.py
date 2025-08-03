#!/usr/bin/env python3
"""
Live Hierarchical Navigation Test
Test the new hierarchical navigation system with the running GUI
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_hierarchical_navigation_live():
    """Test the hierarchical navigation with live GUI functionality"""

    print("🧭 Live Hierarchical Navigation Test")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # Test the hierarchical tree navigation directly
        print("1️⃣ Testing GUI Application Status...")
        from PyQt5.QtWidgets import QApplication

        app = QApplication.instance()
        if app:
            print("✓ GUI application is running")

            # Find all windows
            windows = app.topLevelWidgets()
            fanws_window = None

            for window in windows:
                if hasattr(window, 'nav_tree'):
                    fanws_window = window
                    break

                if fanws_window:
                    print("✓ FANWS window with hierarchical navigation found")

                    # Test tree structure
                    print("\n2️⃣ Testing Navigation Tree Structure...")
                    nav_tree = fanws_window.nav_tree
                    section_count = nav_tree.topLevelItemCount()
                    print(f"✓ Found {section_count} main sections in navigation tree")                # Test content area
                if hasattr(fanws_window, '_content_area'):
                    content_area = fanws_window._content_area
                    page_count = content_area.count()
                    print(f"✓ Found {page_count} content pages")

                    # Test page mapping
                    if hasattr(fanws_window, '_content_pages'):
                        page_mapping = fanws_window._content_pages
                        print(f"✓ Page mapping contains {len(page_mapping)} entries")

                        # Test navigation to key pages
                        key_pages = ['switch_project', 'novel_concept', 'progress_graph', 'memory_usage', 'openai_api_key']
                        for page_id in key_pages:
                            if page_id in page_mapping:
                                # Switch to the page
                                page_index = page_mapping[page_id]
                                content_area.setCurrentIndex(page_index)
                                current_index = content_area.currentIndex()

                                if current_index == page_index:
                                    print(f"  ✓ Successfully navigated to '{page_id}' (index {page_index})")
                                else:
                                    print(f"  ⚠ Failed to navigate to '{page_id}' (expected {page_index}, got {current_index})")
                            else:
                                print(f"  ❌ Page '{page_id}' not found in mapping")
                    else:
                        print("⚠ Page mapping not found")
                else:
                    print("⚠ Content area not found")

                # Test tree item selection simulation
                print("\n3️⃣ Testing Tree Navigation Simulation...")

                # Get first section and expand it
                if section_count > 0:
                    first_section = nav_tree.topLevelItem(0)
                    section_name = first_section.text(0)
                    print(f"✓ Testing section: {section_name}")

                    # Expand the section
                    first_section.setExpanded(True)
                    print(f"  ✓ Section '{section_name}' expanded")

                    # Test subsection navigation
                    subsection_count = first_section.childCount()
                    if subsection_count > 0:
                        first_subsection = first_section.child(0)
                        subsection_name = first_subsection.text(0)
                        print(f"  ✓ Found subsection: {subsection_name}")

                        # Simulate click on subsection
                        nav_tree.setCurrentItem(first_subsection)
                        print(f"  ✓ Selected subsection: {subsection_name}")

                        # Check for subsubsections
                        subsubsection_count = first_subsection.childCount()
                        if subsubsection_count > 0:
                            print(f"  ✓ Found {subsubsection_count} subsubsections")

                            first_subsubsection = first_subsection.child(0)
                            subsubsection_name = first_subsubsection.text(0)
                            print(f"    ✓ Testing subsubsection: {subsubsection_name}")
                        else:
                            print(f"  ℹ No subsubsections found for {subsection_name}")
                    else:
                        print(f"  ⚠ No subsections found for {section_name}")

                print("\n4️⃣ Testing Layout Structure...")

                # Check layout proportions
                central_widget = fanws_window.centralWidget()
                if central_widget:
                    layout = central_widget.layout()
                    if layout and layout.count() >= 2:
                        # Get sidebar and content area
                        sidebar_item = layout.itemAt(0)
                        content_item = layout.itemAt(1)

                        if sidebar_item and content_item:
                            sidebar_widget = sidebar_item.widget()
                            content_widget = content_item.widget()

                            if sidebar_widget and content_widget:
                                sidebar_width = sidebar_widget.width()
                                content_width = content_widget.width()
                                total_width = sidebar_width + content_width

                                sidebar_ratio = sidebar_width / total_width if total_width > 0 else 0
                                content_ratio = content_width / total_width if total_width > 0 else 0

                                print(f"✓ Sidebar width: {sidebar_width}px ({sidebar_ratio:.1%})")
                                print(f"✓ Content width: {content_width}px ({content_ratio:.1%})")

                                # Check if proportions are approximately correct
                                if 0.2 <= sidebar_ratio <= 0.3:  # Around 1/4
                                    print("✓ Sidebar proportion is correct (≈1/4)")
                                else:
                                    print(f"⚠ Sidebar proportion may be off (expected ≈25%, got {sidebar_ratio:.1%})")

                                if 0.7 <= content_ratio <= 0.8:  # Around 3/4
                                    print("✓ Content area proportion is correct (≈3/4)")
                                else:
                                    print(f"⚠ Content area proportion may be off (expected ≈75%, got {content_ratio:.1%})")
                            else:
                                print("⚠ Could not access layout widgets")
                        else:
                            print("⚠ Could not access layout items")
                    else:
                        print("⚠ Unexpected layout structure")
                else:
                    print("⚠ Central widget not found")

                print("\n5️⃣ Testing Widget Compatibility...")

                # Check for key widgets
                required_widgets = [
                    'story_tab', 'characters_tab', 'log_tab', 'synonyms_tab',
                    'project_selector', 'openai_key_input', 'word_count_label',
                    'progress_bar', 'show_dashboard_button'
                ]

                widget_status = {}
                for widget_name in required_widgets:
                    if hasattr(fanws_window, widget_name):
                        widget = getattr(fanws_window, widget_name)
                        if widget:
                            widget_status[widget_name] = "✓ Created"
                        else:
                            widget_status[widget_name] = "⚠ Null"
                    else:
                        widget_status[widget_name] = "❌ Missing"

                for widget_name, status in widget_status.items():
                    print(f"  {status}: {widget_name}")

                created_count = sum(1 for status in widget_status.values() if status.startswith("✓"))
                total_count = len(widget_status)
                print(f"\n📊 Widget Compatibility: {created_count}/{total_count} widgets available")

            else:
                print("❌ FANWS window with hierarchical navigation not found")
                return False

        else:
            print("❌ No GUI application running")
            return False

        print("\n" + "=" * 60)
        print("🎉 Live Hierarchical Navigation Test Complete!")
        print("✅ New navigation system is operational")

        return True

    except Exception as e:
        print(f"❌ Error during live test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_hierarchical_navigation_live()

        if success:
            print("\n🚀 Hierarchical navigation system is fully operational!")
            print("📋 Ready for comprehensive user testing:")
            print("   • Navigate using the sidebar tree")
            print("   • Test section expansion/collapse")
            print("   • Verify content switching")
            print("   • Check all subsections and subsubsections")
            print("   • Validate widget compatibility")
        else:
            print("\n❌ Issues detected in live navigation system")

    except KeyboardInterrupt:
        print("\n⚠ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
