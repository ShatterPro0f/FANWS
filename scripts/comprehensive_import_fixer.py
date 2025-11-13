#!/usr/bin/env python3
"""
Comprehensive Import Fixer for FANWS
Systematically fixes all incorrect imports across the entire codebase.
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set

class ImportFixer:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.src_dir = self.root_dir / "src"

        # Mapping of old import paths to new import paths
        self.import_mapping = {
            # Core modules
            "src.error_handling_system": "src.core.error_handling_system",
            "src.utils": "src.core.utils",
            "src.configuration_manager": "src.core.configuration_manager",
            "src.constants": "src.core.constants",
            "src.performance_monitor": "src.core.performance_monitor",
            "src.input_validation": "src.system.input_validation",

            # System modules
            "src.file_operations": "src.system.file_operations",
            "src.memory_manager": "src.system.memory_manager",
            "src.module_compatibility": "src.system.module_compatibility",
            "src.api_manager": "src.system.api_manager",
            "src.async_operations": "src.system.async_operations",
            "src.quality_manager": "src.system.quality_manager",

            # Text processing
            "src.text_processing": "src.text.text_processing",

            # AI modules
            "src.ai_provider_abstraction": "src.ai.ai_provider_abstraction",

            # Database
            "src.database_manager": "src.database.database_manager",

            # Analytics
            "src.analytics_system": "src.analytics.analytics_system",

            # Collaboration
            "src.collaborative_manager": "src.collaboration.features",
            "src.collaboration_system": "src.collaboration.system",

            # Templates
            "src.template_manager": "src.templates.template_manager",

            # Plugins
            "src.plugin_manager": "src.plugins.plugin_manager",
            "src.plugin_system": "src.plugins.plugin_system",
            "src.plugin_workflow_integration": "src.plugins.plugin_workflow_integration",

            # Workflow
            "src.workflow_coordinator": "src.workflow.coordinator",
            "src.workflow_steps": "src.workflow.steps",

            # UI
            "src.main_gui": "src.ui.main_gui",
            "src.collaborative_ui": "src.ui.collaboration_notifications",

            # Project
            "src.per_project_config_manager": "src.project.per_project_config_manager",

            # Export
            "src.export_formats": "src.export_formats.validator"
        }

        # Non-existent modules to remove
        self.modules_to_remove = {
            "src.atomic_backup",
            "src.database_integration",
            "src.performance_monitor",
        }

        # Function/class mappings
        self.function_mappings = {
            "MemoryCache": None,  # Replace with {}
            "auto_backup_before_operation": None,  # Comment out
        }

    def scan_python_files(self) -> List[Path]:
        """Scan for all Python files in the project."""
        python_files = []
        for root, dirs, files in os.walk(self.src_dir):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']

            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)

        # Also include fanws.py
        fanws_file = self.root_dir / "fanws.py"
        if fanws_file.exists():
            python_files.append(fanws_file)

        return python_files

    def fix_import_line(self, line: str) -> str:
        """Fix a single import line."""
        original_line = line

        # Handle from imports
        from_match = re.match(r'^(\s*from\s+)([^\s]+)(\s+import\s+.*)$', line)
        if from_match:
            prefix, module_path, suffix = from_match.groups()

            # Check if module should be removed
            if module_path in self.modules_to_remove:
                return f"# {line.strip()}  # Removed: module not available\n"

            # Check for mapping
            if module_path in self.import_mapping:
                new_module = self.import_mapping[module_path]
                return f"{prefix}{new_module}{suffix}\n"

            # Handle relative imports that need fixing
            if module_path.startswith("..") and "workflow_steps" in module_path:
                fixed_module = module_path.replace("..workflow_steps", "..workflow.steps")
                return f"{prefix}{fixed_module}{suffix}\n"

            if module_path.startswith("..") and "plugins.plugin_workflow_integration" in module_path:
                # These should come from local files
                if "BaseWorkflowStep" in suffix:
                    return f"{prefix}.base_step{suffix}\n"

        # Handle direct imports
        import_match = re.match(r'^(\s*import\s+)([^\s]+)(.*)$', line)
        if import_match:
            prefix, module_path, suffix = import_match.groups()

            if module_path in self.import_mapping:
                new_module = self.import_mapping[module_path]
                return f"{prefix}{new_module}{suffix}\n"

        return line

    def fix_file_imports(self, file_path: Path) -> bool:
        """Fix imports in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            modified = False
            new_lines = []

            for line in lines:
                stripped = line.strip()

                # Skip empty lines and comments
                if not stripped or stripped.startswith('#'):
                    new_lines.append(line)
                    continue

                # Check if it's an import line
                if (stripped.startswith('from ') or stripped.startswith('import ')) and 'import' in stripped:
                    new_line = self.fix_import_line(line)
                    if new_line != line:
                        modified = True
                        print(f"  Fixed: {line.strip()} -> {new_line.strip()}")
                    new_lines.append(new_line.rstrip('\n'))
                else:
                    # Fix function calls that don't exist
                    if 'auto_backup_before_operation' in line:
                        comment_line = line.replace('auto_backup_before_operation', '# auto_backup_before_operation')
                        comment_line += "  # TODO: Implement backup system"
                        new_lines.append(comment_line)
                        if 'backup_path =' in line:
                            new_lines.append(line.split('=')[0] + '= None')
                        modified = True
                    elif 'MemoryCache(' in line:
                        fixed_line = line.replace('MemoryCache(', '{  # Simple dict cache instead of MemoryCache(')
                        new_lines.append(fixed_line)
                        modified = True
                    else:
                        new_lines.append(line)

            if modified:
                new_content = '\n'.join(new_lines)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def fix_all_imports(self):
        """Fix imports in all Python files."""
        python_files = self.scan_python_files()
        fixed_files = []

        print(f"Found {len(python_files)} Python files to check")
        print("=" * 60)

        for file_path in python_files:
            rel_path = file_path.relative_to(self.root_dir)
            print(f"Checking {rel_path}...")

            if self.fix_file_imports(file_path):
                fixed_files.append(rel_path)
                print(f"  ✓ Fixed imports in {rel_path}")
            else:
                print(f"  - No changes needed in {rel_path}")

        print("=" * 60)
        print(f"Fixed imports in {len(fixed_files)} files:")
        for file_path in fixed_files:
            print(f"  - {file_path}")

def main():
    root_dir = os.getcwd()
    print(f"Starting comprehensive import fix in {root_dir}")

    fixer = ImportFixer(root_dir)
    fixer.fix_all_imports()

    print("\nImport fixing complete!")
    print("Please test the modules with: python verify_all_modules.py")

if __name__ == "__main__":
    main()
