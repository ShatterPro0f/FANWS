#!/usr/bin/env python3
"""
Module verification script for FANWS
Tests all modules can be imported without errors
"""

import sys
from typing import List, Tuple

def test_module_import(module_name: str) -> Tuple[bool, str]:
    """Test if a module can be imported successfully."""
    try:
        __import__(module_name)
        return True, "Success"
    except Exception as e:
        return False, str(e)

def main():
    """Test all main modules."""
    print("FANWS Module Import Verification")
    print("=" * 50)

    # List of modules to test
    modules_to_test = [
        # Core modules
        "src.core.utils",
        "src.core.error_handling_system",
        "src.core.configuration_manager",

        # System modules
        "src.system.file_operations",
        "src.system.memory_manager",
        "src.system.module_compatibility",

        # Database
        "src.database.database_manager",

        # Analytics
        "src.analytics.analytics_system",

        # Collaboration
        "src.collaboration.features",

        # Plugins
        "src.plugins.plugin_manager",

        # Text processing
        "src.text.text_processing",

        # AI
        "src.ai.ai_provider_abstraction",

        # Project management
        "src.project.project_manager",

        # Templates
        "src.templates.template_manager",

        # UI
        "src.ui.consolidated_ui",

        # Workflow
        "src.workflow.coordinator",

        # Export formats
        "src.export_formats.validator"
    ]

    success_count = 0
    total_count = len(modules_to_test)
    failed_modules = []

    for module in modules_to_test:
        success, message = test_module_import(module)
        status = "✓" if success else "✗"
        print(f"{status} {module:<40} {message}")

        if success:
            success_count += 1
        else:
            failed_modules.append((module, message))

    print("\n" + "=" * 50)
    print(f"Results: {success_count}/{total_count} modules imported successfully")

    if failed_modules:
        print(f"\nFailed modules ({len(failed_modules)}):")
        for module, error in failed_modules:
            print(f"  • {module}: {error}")
    else:
        print("\n🎉 All modules imported successfully!")

    return len(failed_modules) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
