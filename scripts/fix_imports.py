"""
Script to fix import paths after reorganization
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix import paths in a Python file after reorganization"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Define import mappings
        import_mappings = {
            # Core imports
            r'from \.constants import': 'from ..core.constants import',
            r'from \.utils import': 'from ..core.utils import',
            r'from \.error_handling_system import': 'from ..core.error_handling_system import',
            r'from \.performance_monitor import': 'from ..core.performance_monitor import',
            r'from \.configuration_manager import': 'from ..core.configuration_manager import',

            # System imports
            r'from \.memory_manager import': 'from ..system.memory_manager import',
            r'from \.api_manager import': 'from ..system.api_manager import',
            r'from \.file_operations import': 'from ..system.file_operations import',
            r'from \.async_operations import': 'from ..system.async_operations import',
            r'from \.permissions_system import': 'from ..system.permissions_system import',
            r'from \.input_validation import': 'from ..system.input_validation import',
            r'from \.quality_manager import': 'from ..system.quality_manager import',

            # Database imports
            r'from \.database_manager import': 'from ..database.database_manager import',

            # Project imports
            r'from \.project_manager import': 'from ..project.project_manager import',
            r'from \.project_utils import': 'from ..project.project_utils import',

            # Plugin imports
            r'from \.plugin_manager import': 'from ..plugins.plugin_manager import',
            r'from \.plugin_system import': 'from ..plugins.plugin_system import',

            # Template imports
            r'from \.template_manager import': 'from ..templates.template_manager import',

            # Analytics imports
            r'from \.analytics_system import': 'from ..analytics.analytics_system import',

            # UI imports
            r'from \.main_gui import': 'from ..ui.main_gui import',

            # Workflow imports
            r'from \.workflow_coordinator import': 'from ..workflow.coordinator import',
            r'from \.workflow_manager import': 'from ..workflow.manager import',

            # AI imports
            r'from \.ai_provider_abstraction import': 'from ..ai.ai_provider_abstraction import',
        }

        # Apply mappings
        for old_pattern, new_import in import_mappings.items():
            content = re.sub(old_pattern, new_import, content)

        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    src_dir = Path("src")
    fixed_count = 0

    # Process all Python files in src subdirectories (not root)
    for module_dir in src_dir.iterdir():
        if module_dir.is_dir() and module_dir.name != "__pycache__":
            for py_file in module_dir.rglob("*.py"):
                if fix_imports_in_file(py_file):
                    print(f"Fixed imports in: {py_file}")
                    fixed_count += 1

    print(f"Fixed imports in {fixed_count} files")

if __name__ == "__main__":
    main()
