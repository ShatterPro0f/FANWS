#!/usr/bin/env python3
"""
Test script to verify all GUI button functions are properly implemented
"""

import sys
import os
import inspect
from PyQt5.QtWidgets import QApplication

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_gui_functions():
    """Test that all GUI functions are properly implemented."""
    print("🧪 Testing GUI Function Implementation")
    print("=" * 50)

    try:
        # Import the main GUI
        from src.ui.main_gui import MainWindow

        # Create app (required for Qt)
        app = QApplication([])

        # Create main window instance
        window = MainWindow()

        # List of expected functions that should be connected to buttons
        expected_functions = [
            'create_new_project',
            'switch_to_selected_project',
            'load_selected_project',
            'save_novel_settings',
            'start_workflow',
            'pause_workflow',
            'stop_workflow',
            'save_openai_key',
            'test_openai_connection',
            'save_wordsapi_key',
            'test_wordsapi_connection',
            'toggle_password_visibility',
            'refresh_memory_stats',
            'refresh_cache_stats',
            'optimize_cache',
            'clear_cache',
            'export_cache_data',
            'toggle_section',
            'toggle_subsection',
            'open_subsection',
            'open_subsubsection',
            'export_project',
            'perform_project_export',
            'update_project_ui',
            'validate_project_name',
            'refresh_project_list',
            'finalize_project_creation',
            'collect_project_content',
            'export_to_pdf',
            'export_to_docx',
            'export_to_txt',
            'export_to_html'
        ]

        print(f"📊 Checking {len(expected_functions)} expected functions...")
        print()

        missing_functions = []
        implemented_functions = []

        for func_name in expected_functions:
            if hasattr(window, func_name):
                func = getattr(window, func_name)
                if callable(func):
                    implemented_functions.append(func_name)
                    print(f"✅ {func_name}")
                else:
                    missing_functions.append(f"{func_name} (not callable)")
                    print(f"❌ {func_name} (exists but not callable)")
            else:
                missing_functions.append(func_name)
                print(f"❌ {func_name} (missing)")

        print()
        print("📈 Summary:")
        print(f"✅ Implemented: {len(implemented_functions)}")
        print(f"❌ Missing: {len(missing_functions)}")
        print(f"📊 Success Rate: {len(implemented_functions)}/{len(expected_functions)} ({100*len(implemented_functions)/len(expected_functions):.1f}%)")

        if missing_functions:
            print()
            print("❌ Missing Functions:")
            for func in missing_functions:
                print(f"   • {func}")

        print()
        print("🔧 Additional GUI Capabilities:")

        # Check for signal connections
        signal_connections = []
        if hasattr(window, 'workflow_controller'):
            signal_connections.append("Workflow controller signals")
        if hasattr(window, 'async_manager'):
            signal_connections.append("Async task management")
        if hasattr(window, 'design_system'):
            signal_connections.append("Modern design system")
        if hasattr(window, 'content_widgets'):
            signal_connections.append("Dynamic content widgets")

        for capability in signal_connections:
            print(f"✅ {capability}")

        # Test critical GUI components
        print()
        print("🏗️ GUI Component Status:")

        components = [
            ('sidebar', 'Navigation sidebar'),
            ('content_area', 'Main content area'),
            ('content_widgets', 'Content widget system'),
            ('project_name_label', 'Project name display'),
            ('project_stats', 'Project statistics')
        ]

        for attr, description in components:
            if hasattr(window, attr):
                print(f"✅ {description}")
            else:
                print(f"⚠️ {description} (not found)")

        # Test navigation system
        print()
        print("🧭 Navigation System Test:")
        if hasattr(window, 'sections'):
            section_count = len(window.sections)
            print(f"✅ {section_count} main sections available")

            subsection_count = 0
            subsubsection_count = 0

            for section_id, section_data in window.sections.items():
                if 'subsections' in section_data:
                    subsection_count += len(section_data['subsections'])
                    for subsection_data in section_data['subsections'].values():
                        if 'subsubsections' in subsection_data:
                            subsubsection_count += len(subsection_data['subsubsections'])

            print(f"✅ {subsection_count} subsections available")
            print(f"✅ {subsubsection_count} subsubsections available")
        else:
            print("⚠️ Section navigation system not found")

        print()
        if len(missing_functions) == 0:
            print("🎉 All GUI functions successfully implemented!")
            return True
        else:
            print(f"⚠️ {len(missing_functions)} functions still need implementation")
            return False

    except Exception as e:
        print(f"❌ Error testing GUI functions: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_functions()
    sys.exit(0 if success else 1)
