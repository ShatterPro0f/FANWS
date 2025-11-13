"""
Simplified FANWS Import Fixer
Focuses on correcting import statements and generating a clean report
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ImportFixer:
    def __init__(self):
        self.module_mapping = {
            # Core modules
            'constants': 'src.core.constants',
            'utils': 'src.core.utils',
            'configuration_manager': 'src.core.configuration_manager',
            'error_handling_system': 'src.core.error_handling_system',
            'performance_monitor': 'src.core.performance_monitor',

            # Text processing
            'text_processing': 'src.text.text_processing',
            'writing_components': 'src.text.writing_components',
            'prompt_engineering_tools': 'src.text.prompt_engineering_tools',

            # Project management
            'project_manager': 'src.project.project_manager',
            'project_utils': 'src.project.project_utils',
            'per_project_config_manager': 'src.project.per_project_config_manager',

            # Plugin system
            'plugin_manager': 'src.plugins.plugin_manager',
            'plugin_system': 'src.plugins.plugin_system',
            'plugin_management_ui': 'src.plugins.plugin_management_ui',
            'plugin_workflow_integration': 'src.plugins.plugin_workflow_integration',

            # System infrastructure
            'api_manager': 'src.system.api_manager',
            'async_operations': 'src.system.async_operations',
            'memory_manager': 'src.system.memory_manager',
            'permissions_system': 'src.system.permissions_system',
            'atomic_backup': 'src.system.atomic_backup',
            'module_compatibility': 'src.system.module_compatibility',
            'file_operations': 'src.system.file_operations',
            'input_validation': 'src.system.input_validation',
            'quality_manager': 'src.system.quality_manager',

            # Database
            'database_manager': 'src.database.database_manager',

            # Templates
            'template_manager': 'src.templates.template_manager',

            # Analytics
            'analytics_system': 'src.analytics.analytics_system',

            # AI
            'ai_provider_abstraction': 'src.ai.ai_provider_abstraction',
            'content_generator': 'src.ai.content_generator',

            # UI
            'main_gui': 'src.ui.main_gui',
            'main_window': 'src.ui.main_window',

            # Workflow
            'coordinator': 'src.workflow.coordinator',
            'manager': 'src.workflow.manager',
            'workflow_coordinator': 'src.workflow.coordinator',
            'workflow_manager': 'src.workflow.manager',

            # Collaboration
            'collaboration_system': 'src.collaboration.system',
            'bug_reporting': 'src.collaboration.bug_reporting',
        }

        self.fixed_files = []
        self.unresolved_imports = []
        self.errors = []

    def fix_imports_in_file(self, file_path: Path) -> bool:
        """Fix imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            current_module = self._get_module_path(file_path)

            # Fix common import patterns
            content = self._fix_relative_imports(content, current_module, file_path)
            content = self._fix_absolute_imports(content, current_module, file_path)

            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True

            return False

        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {e}")
            logger.error(f"Error processing {file_path}: {e}")
            return False

    def _get_module_path(self, file_path: Path) -> str:
        """Get the module path for a file"""
        try:
            relative_path = file_path.relative_to(Path('src'))
            module_parts = list(relative_path.parts[:-1])
            if relative_path.stem != '__init__':
                module_parts.append(relative_path.stem)
            return '.'.join(['src'] + module_parts) if module_parts else 'src'
        except:
            return 'src'

    def _fix_relative_imports(self, content: str, current_module: str, file_path: Path) -> str:
        """Fix relative imports"""
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            original_line = line

            # Pattern: from .module import something
            pattern1 = re.match(r'^(\s*)from\s+\.([a-zA-Z_][a-zA-Z0-9_]*)\s+import\s+(.+)$', line)
            if pattern1:
                indent, module, imports = pattern1.groups()
                if module in self.module_mapping:
                    new_module = self.module_mapping[module]
                    new_import = self._calculate_relative_import(current_module, new_module)
                    line = f"{indent}from {new_import} import {imports}"
                else:
                    # Try to guess the new location
                    new_import = self._guess_relative_import(module, current_module)
                    if new_import:
                        line = f"{indent}from {new_import} import {imports}"
                    else:
                        self.unresolved_imports.append(f"RELATIVE: {original_line} in {file_path}")

            # Pattern: from ..module import something
            pattern2 = re.match(r'^(\s*)from\s+\.\.([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import\s+(.+)$', line)
            if pattern2:
                indent, module, imports = pattern2.groups()
                module_name = module.split('.')[-1]
                if module_name in self.module_mapping:
                    new_module = self.module_mapping[module_name]
                    new_import = self._calculate_relative_import(current_module, new_module)
                    line = f"{indent}from {new_import} import {imports}"

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _fix_absolute_imports(self, content: str, current_module: str, file_path: Path) -> str:
        """Fix absolute imports"""
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            original_line = line

            # Pattern: import module
            pattern1 = re.match(r'^(\s*)import\s+([a-zA-Z_][a-zA-Z0-9_]*)(\s+as\s+\w+)?$', line)
            if pattern1:
                indent, module, alias = pattern1.groups()
                if module in self.module_mapping:
                    new_module = self.module_mapping[module]
                    new_import = self._calculate_relative_import(current_module, new_module)
                    module_name = new_module.split('.')[-1]
                    alias_part = alias if alias else ""
                    line = f"{indent}from {new_import} import {module_name}{alias_part}"

            # Pattern: from module import something
            pattern2 = re.match(r'^(\s*)from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import\s+(.+)$', line)
            if pattern2:
                indent, module, imports = pattern2.groups()
                if module in self.module_mapping:
                    new_module = self.module_mapping[module]
                    new_import = self._calculate_relative_import(current_module, new_module)
                    line = f"{indent}from {new_import} import {imports}"

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _calculate_relative_import(self, from_module: str, to_module: str) -> str:
        """Calculate relative import path between two modules"""
        from_parts = from_module.split('.')
        to_parts = to_module.split('.')

        # Find common prefix
        common_length = 0
        for i in range(min(len(from_parts), len(to_parts))):
            if from_parts[i] == to_parts[i]:
                common_length += 1
            else:
                break

        # Calculate relative path
        up_levels = len(from_parts) - common_length - 1
        down_parts = to_parts[common_length:]

        if up_levels == 0 and len(down_parts) == 1:
            return f".{down_parts[0]}"
        elif up_levels == 0:
            return "." + ".".join(down_parts)
        else:
            prefix = "." * (up_levels + 1)
            if down_parts:
                return prefix + ".".join(down_parts)
            else:
                return prefix[:-1]

    def _guess_relative_import(self, module: str, current_module: str) -> str:
        """Guess the correct relative import for unknown modules"""
        # Common guesses based on module name patterns
        guesses = {
            'cache_manager': '..core.cache_manager',
            'workflow_steps': '..workflow.steps',
            'base_step': '.base_step',
        }

        return guesses.get(module)

    def fix_all_imports(self):
        """Fix imports in all Python files"""
        src_path = Path('src')
        if not src_path.exists():
            logger.error("src directory not found")
            return

        for py_file in src_path.rglob('*.py'):
            logger.info(f"Processing {py_file}")
            if self.fix_imports_in_file(py_file):
                self.fixed_files.append(str(py_file))
                logger.info(f"✓ Fixed imports in {py_file}")

    def generate_report(self) -> str:
        """Generate a simple report"""
        from datetime import datetime

        report = []
        report.append("# FANWS Import Fix Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        report.append("## Summary")
        report.append(f"- Files processed: {len(self.fixed_files) + len(self.errors)}")
        report.append(f"- Files with fixed imports: {len(self.fixed_files)}")
        report.append(f"- Unresolved imports: {len(self.unresolved_imports)}")
        report.append(f"- Errors: {len(self.errors)}")
        report.append("")

        if self.fixed_files:
            report.append("## Fixed Files")
            for file_path in self.fixed_files:
                report.append(f"- {file_path}")
            report.append("")

        if self.unresolved_imports:
            report.append("## Unresolved Imports (Need Manual Review)")
            for unresolved in self.unresolved_imports:
                report.append(f"- {unresolved}")
            report.append("")

        if self.errors:
            report.append("## Errors")
            for error in self.errors:
                report.append(f"- {error}")
            report.append("")

        return "\\n".join(report)

def main():
    """Main execution"""
    logger.info("Starting FANWS Import Fix")

    fixer = ImportFixer()
    fixer.fix_all_imports()

    # Generate report
    report = fixer.generate_report()

    # Save report
    with open('IMPORT_FIX_REPORT.md', 'w') as f:
        f.write(report)

    # Print summary
    print("\\n" + "="*50)
    print("FANWS IMPORT FIX COMPLETE")
    print("="*50)
    print(f"Files fixed: {len(fixer.fixed_files)}")
    print(f"Unresolved: {len(fixer.unresolved_imports)}")
    print(f"Errors: {len(fixer.errors)}")
    print("\\nReport saved to: IMPORT_FIX_REPORT.md")

if __name__ == "__main__":
    main()
