#!/usr/bin/env python3
"""
Smart method restoration script
This script will extract unique methods from the original fanws.py and add them to the clean version
"""

import re
import os

def extract_methods_from_file(filename):
    """Extract all method definitions and their content from a file"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    methods = {}
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i]
        # Look for method definitions
        if re.match(r'^    def \w+\(', line):
            method_name = re.search(r'def (\w+)\(', line).group(1)
            method_lines = [line]
            i += 1

            # Collect the entire method body
            while i < len(lines):
                if lines[i].startswith('    def ') or lines[i].startswith('class ') or (lines[i].strip() == '' and i + 1 < len(lines) and not lines[i + 1].startswith('    ')):
                    break
                method_lines.append(lines[i])
                i += 1

            # Only keep if we don't already have this method, or if this one is longer (more complete)
            method_content = '\n'.join(method_lines)
            if method_name not in methods or len(method_content) > len(methods[method_name]):
                methods[method_name] = method_content
        else:
            i += 1

    return methods

def get_current_methods(filename):
    """Get list of methods that already exist in the current file"""
    existing = set()
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    for match in re.finditer(r'^    def (\w+)\(', content, re.MULTILINE):
        existing.add(match.group(1))

    return existing

def main():
    # Extract methods from original file
    print("Extracting methods from original file...")
    original_methods = extract_methods_from_file('fanws_old_duplicate_methods.py')
    print(f"Found {len(original_methods)} unique methods in original file")

    # Get methods already in current file
    current_methods = get_current_methods('fanws.py')
    print(f"Current file has {len(current_methods)} methods")

    # Find missing methods
    missing_methods = []
    essential_methods = [
        'update_sub_tone_options', 'update_wordsapi_count', 'update_word_count',
        'init_background_task_system', 'init_task_monitoring_ui', 'init_task_analytics_system',
        'init_analytics_ui', 'show_task_monitor_dialog', 'create_task_monitor_dialog',
        'update_task_monitor_display', 'show_analytics_dialog', 'create_analytics_dialog',
        'update_analytics_display', 'reset_analytics', 'export_analytics',
        'init_plugin_system', 'load_plugin_configuration', 'save_plugin_configuration',
        'discover_plugins', 'load_plugins', 'show_plugin_manager', 'create_plugin_manager_dialog',
        'show_onboarding', 'create_project', 'open_project', 'populate_draft_versions',
        'connect_draft_version_selector', 'load_draft_version', 'init_multi_provider_ai_system',
        'update_ai_provider_key', 'generate_ai_content', 'get_ai_provider_status',
        'on_analytics_updated', 'on_session_started', 'on_session_ended', 'on_milestone_reached',
        'update_word_count_enhanced', 'start_analytics_session', 'end_analytics_session',
        'get_analytics_dashboard_data', 'on_goal_achieved', 'on_pattern_detected',
        'get_advanced_analytics_dashboard', 'export_all_analytics', '_initialize_enhanced_collaborative_features',
        '_handle_collaboration_notification', '_ensure_default_user_exists', '_initialize_project_collaboration',
        'get_collaborative_manager', 'launch_collaboration_hub', 'get_collaboration_status',
        '_handle_memory_event', '_handle_config_change', 'get_configuration_value',
        'set_configuration_value', 'show_configuration_dashboard', 'get_configuration_feature_status',
        'get_template_manager', 'launch_template_marketplace', 'create_project_from_template',
        '_handle_template_project_created', 'test_workflow_integration', 'test_all_workflow_steps',
        'test_gui_integration', 'run_system_validation', 'run_external_tests'
    ]

    for method_name in essential_methods:
        if method_name not in current_methods and method_name in original_methods:
            missing_methods.append((method_name, original_methods[method_name]))

    if not missing_methods:
        print("No essential methods are missing!")
        return

    print(f"Found {len(missing_methods)} essential missing methods")

    # Read current file
    with open('fanws.py', 'r', encoding='utf-8') as f:
        current_content = f.read()

    # Find insertion point (before the final class alias)
    insertion_point = current_content.rfind('\n\n# Create alias for main class')
    if insertion_point == -1:
        insertion_point = current_content.rfind('\nFANWS = FANWSWindow')
        if insertion_point == -1:
            print("Could not find insertion point!")
            return

    # Build the new methods section
    new_methods_section = "\n    # ==========================================\n"
    new_methods_section += "    # Additional Restored Methods\n"
    new_methods_section += "    # ==========================================\n\n"

    for method_name, method_content in missing_methods:
        new_methods_section += method_content + "\n\n"

    # Insert the new methods
    new_content = current_content[:insertion_point] + new_methods_section + current_content[insertion_point:]

    # Write the updated file
    with open('fanws_restored.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Created fanws_restored.py with {len(missing_methods)} additional methods restored")
    print("Essential methods added:")
    for method_name, _ in missing_methods:
        print(f"  - {method_name}")

if __name__ == "__main__":
    main()
