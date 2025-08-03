"""
FANWS Import Analysis and Correction Script
Scans the entire application, analyzes function intentions and dependencies,
and updates all imports to match the new modular file structure.
"""

import os
import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FunctionAnalyzer:
    """Analyzes function intentions and dependencies"""

    def __init__(self):
        self.function_catalog = {}
        self.import_dependencies = defaultdict(set)
        self.unresolved_imports = []
        self.module_mapping = self._build_module_mapping()

    def _build_module_mapping(self) -> Dict[str, str]:
        """Build mapping of old module names to new module paths"""
        return {
            # Core modules
            'constants': 'src.core.constants',
            'utils': 'src.core.utils',
            'configuration_manager': 'src.core.configuration_manager',
            'error_handling_system': 'src.core.error_handling_system',
            'performance_monitor': 'src.core.performance_monitor',
            'cache_manager': 'src.core.cache_manager',

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
            'database_models': 'src.database.database_models',

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
            'collaboration_notifications': 'src.ui.collaboration_notifications',
            'consolidated_ui': 'src.ui.consolidated_ui',
            'export_ui': 'src.ui.export_ui',
            'onboarding_wizard': 'src.ui.onboarding_wizard',

            # Workflow
            'coordinator': 'src.workflow.coordinator',
            'manager': 'src.workflow.manager',
            'workflow_coordinator': 'src.workflow.coordinator',
            'workflow_manager': 'src.workflow.manager',

            # Collaboration
            'collaboration_system': 'src.collaboration.system',
            'collaboration_features': 'src.collaboration.features',
            'bug_reporting': 'src.collaboration.bug_reporting',

            # Export formats
            'validator': 'src.export_formats.validator',
        }

    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a Python file for functions, classes, and dependencies"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            analysis = {
                'file_path': str(file_path),
                'functions': [],
                'classes': [],
                'imports': [],
                'dependencies': set(),
                'exports': set()
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._analyze_function(node, content)
                    analysis['functions'].append(func_info)
                    analysis['exports'].add(func_info['name'])

                elif isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class(node, content)
                    analysis['classes'].append(class_info)
                    analysis['exports'].add(class_info['name'])

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_info = self._analyze_import(node)
                    analysis['imports'].append(import_info)
                    if import_info['module']:
                        analysis['dependencies'].add(import_info['module'])

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return None

    def _analyze_function(self, node: ast.FunctionDef, content: str) -> Dict:
        """Analyze a function definition"""
        # Get function body as string for intention analysis
        lines = content.split('\n')
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10

        func_body = '\n'.join(lines[start_line:end_line])

        # Analyze function intention based on name and body
        intention = self._determine_function_intention(node.name, func_body)

        return {
            'name': node.name,
            'type': 'function',
            'line': node.lineno,
            'intention': intention,
            'dependencies': self._extract_function_dependencies(func_body),
            'docstring': ast.get_docstring(node) or '',
            'args': [arg.arg for arg in node.args.args]
        }

    def _analyze_class(self, node: ast.ClassDef, content: str) -> Dict:
        """Analyze a class definition"""
        lines = content.split('\n')
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 20

        class_body = '\n'.join(lines[start_line:end_line])
        intention = self._determine_class_intention(node.name, class_body)

        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)

        return {
            'name': node.name,
            'type': 'class',
            'line': node.lineno,
            'intention': intention,
            'methods': methods,
            'dependencies': self._extract_function_dependencies(class_body),
            'docstring': ast.get_docstring(node) or '',
            'bases': [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
        }

    def _analyze_import(self, node) -> Dict:
        """Analyze an import statement"""
        if isinstance(node, ast.Import):
            return {
                'type': 'import',
                'module': node.names[0].name if node.names else None,
                'names': [alias.name for alias in node.names],
                'line': node.lineno
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                'type': 'from_import',
                'module': node.module,
                'names': [alias.name for alias in node.names] if node.names else [],
                'line': node.lineno,
                'level': node.level or 0
            }

    def _determine_function_intention(self, name: str, body: str) -> str:
        """Determine the intention/purpose of a function based on name and body"""
        # Categorize based on function name patterns
        if any(pattern in name.lower() for pattern in ['init', 'setup', 'configure']):
            return 'initialization'
        elif any(pattern in name.lower() for pattern in ['save', 'write', 'store', 'export']):
            return 'data_persistence'
        elif any(pattern in name.lower() for pattern in ['load', 'read', 'get', 'fetch', 'retrieve']):
            return 'data_retrieval'
        elif any(pattern in name.lower() for pattern in ['process', 'analyze', 'transform', 'parse']):
            return 'data_processing'
        elif any(pattern in name.lower() for pattern in ['validate', 'check', 'verify']):
            return 'validation'
        elif any(pattern in name.lower() for pattern in ['render', 'display', 'show', 'update_ui']):
            return 'ui_interaction'
        elif any(pattern in name.lower() for pattern in ['connect', 'request', 'call', 'api']):
            return 'external_communication'
        elif any(pattern in name.lower() for pattern in ['error', 'exception', 'handle']):
            return 'error_handling'
        elif any(pattern in name.lower() for pattern in ['test', 'mock', 'debug']):
            return 'testing_debugging'
        else:
            return 'business_logic'

    def _determine_class_intention(self, name: str, body: str) -> str:
        """Determine the intention/purpose of a class"""
        if any(pattern in name.lower() for pattern in ['manager', 'controller', 'coordinator']):
            return 'management'
        elif any(pattern in name.lower() for pattern in ['ui', 'window', 'dialog', 'widget']):
            return 'user_interface'
        elif any(pattern in name.lower() for pattern in ['model', 'data', 'entity']):
            return 'data_model'
        elif any(pattern in name.lower() for pattern in ['service', 'api', 'client']):
            return 'service'
        elif any(pattern in name.lower() for pattern in ['error', 'exception']):
            return 'error_handling'
        elif any(pattern in name.lower() for pattern in ['test', 'mock']):
            return 'testing'
        else:
            return 'business_logic'

    def _extract_function_dependencies(self, body: str) -> Set[str]:
        """Extract dependencies from function body"""
        dependencies = set()

        # Look for class instantiations and function calls
        patterns = [
            r'(\w+)\(',  # Function calls
            r'(\w+)\.',  # Method calls
            r'from\s+(\w+)',  # Import statements
            r'import\s+(\w+)',  # Import statements
        ]

        for pattern in patterns:
            matches = re.findall(pattern, body)
            dependencies.update(matches)

        return dependencies

    def update_imports_in_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Update imports in a file based on the new module structure"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            unresolved = []

            # Parse the file to find imports
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                logger.error(f"Syntax error in {file_path}: {e}")
                return False, [f"Syntax error: {e}"]

            # Determine the current module's location for relative imports
            current_module_path = self._get_module_path(file_path)

            # Process each import
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    updated_import = self._update_from_import(node, current_module_path, file_path)
                    if updated_import['updated']:
                        old_line = self._get_import_line(content, node)
                        content = content.replace(old_line, updated_import['new_line'])
                    elif updated_import['unresolved']:
                        unresolved.append(updated_import['unresolved'])

                elif isinstance(node, ast.Import):
                    updated_import = self._update_import(node, current_module_path, file_path)
                    if updated_import['updated']:
                        old_line = self._get_import_line(content, node)
                        content = content.replace(old_line, updated_import['new_line'])
                    elif updated_import['unresolved']:
                        unresolved.append(updated_import['unresolved'])

            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, unresolved

            return False, unresolved

        except Exception as e:
            logger.error(f"Error updating imports in {file_path}: {e}")
            return False, [f"Error: {e}"]

    def _get_module_path(self, file_path: Path) -> str:
        """Get the module path for a file"""
        # Convert file path to module path
        relative_path = file_path.relative_to(Path('src') if 'src' in str(file_path) else Path('.'))
        module_parts = list(relative_path.parts[:-1])  # Exclude filename
        if relative_path.stem != '__init__':
            module_parts.append(relative_path.stem)

        return '.'.join(['src'] + module_parts) if module_parts else 'src'

    def _update_from_import(self, node: ast.ImportFrom, current_module_path: str, file_path: Path) -> Dict:
        """Update a from...import statement"""
        if not node.module:
            return {'updated': False, 'unresolved': None, 'new_line': ''}

        # Handle relative imports
        if node.level > 0:
            return self._handle_relative_import(node, current_module_path, file_path)

        # Handle absolute imports
        if node.module in self.module_mapping:
            new_module = self.module_mapping[node.module]
            new_import_path = self._calculate_relative_import(current_module_path, new_module)

            names = ', '.join([alias.name for alias in node.names])
            new_line = f"from {new_import_path} import {names}"

            return {'updated': True, 'unresolved': None, 'new_line': new_line}

        # Check if it's a partial match
        for old_module, new_module in self.module_mapping.items():
            if old_module in node.module or node.module in old_module:
                new_import_path = self._calculate_relative_import(current_module_path, new_module)
                names = ', '.join([alias.name for alias in node.names])
                new_line = f"from {new_import_path} import {names}"

                return {'updated': True, 'unresolved': None, 'new_line': new_line}

        # Unresolved import
        unresolved_info = f"FROM IMPORT: {node.module} -> {[alias.name for alias in node.names]} in {file_path}"
        return {'updated': False, 'unresolved': unresolved_info, 'new_line': ''}

    def _update_import(self, node: ast.Import, current_module_path: str, file_path: Path) -> Dict:
        """Update an import statement"""
        if not node.names:
            return {'updated': False, 'unresolved': None, 'new_line': ''}

        first_import = node.names[0].name

        if first_import in self.module_mapping:
            new_module = self.module_mapping[first_import]
            new_import_path = self._calculate_relative_import(current_module_path, new_module)

            alias = f" as {node.names[0].asname}" if node.names[0].asname else ""
            new_line = f"from {new_import_path} import {first_import.split('.')[-1]}{alias}"

            return {'updated': True, 'unresolved': None, 'new_line': new_line}

        # Unresolved import
        unresolved_info = f"IMPORT: {first_import} in {file_path}"
        return {'updated': False, 'unresolved': unresolved_info, 'new_line': ''}

    def _handle_relative_import(self, node: ast.ImportFrom, current_module_path: str, file_path: Path) -> Dict:
        """Handle relative import updates"""
        # For relative imports, we need to calculate the new path based on current location
        current_parts = current_module_path.split('.')

        # Go up the hierarchy based on the level
        target_parts = current_parts[:-node.level] if node.level <= len(current_parts) else ['src']

        if node.module:
            target_parts.extend(node.module.split('.'))

        # Check if this maps to a known module
        target_module = '.'.join(target_parts)

        # Try to find the best match in our module mapping
        best_match = None
        for old_module, new_module in self.module_mapping.items():
            if old_module in target_module or any(part in old_module for part in target_parts):
                best_match = new_module
                break

        if best_match:
            new_import_path = self._calculate_relative_import(current_module_path, best_match)
            names = ', '.join([alias.name for alias in node.names])
            new_line = f"from {new_import_path} import {names}"

            return {'updated': True, 'unresolved': None, 'new_line': new_line}

        # Keep relative import as is for now
        return {'updated': False, 'unresolved': None, 'new_line': ''}

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
                return prefix[:-1]  # Remove one dot if no down parts

    def _get_import_line(self, content: str, node) -> str:
        """Get the actual import line from content"""
        lines = content.split('\n')
        if node.lineno <= len(lines):
            return lines[node.lineno - 1].strip()
        return ""

    def scan_entire_application(self) -> Dict:
        """Scan the entire application and analyze all modules"""
        src_path = Path('src')
        if not src_path.exists():
            logger.error("src directory not found")
            return {}

        analysis_results = {}

        # Scan all Python files in src
        for py_file in src_path.rglob('*.py'):
            if py_file.name == '__init__.py':
                continue  # Skip __init__.py files for now

            relative_path = str(py_file.relative_to(src_path))
            logger.info(f"Analyzing {relative_path}")

            analysis = self.analyze_file(py_file)
            if analysis:
                analysis_results[relative_path] = analysis

        return analysis_results

    def update_all_imports(self) -> Dict:
        """Update imports in all Python files"""
        src_path = Path('src')
        results = {
            'updated_files': [],
            'unresolved_imports': [],
            'errors': []
        }

        # Process all Python files
        for py_file in src_path.rglob('*.py'):
            try:
                updated, unresolved = self.update_imports_in_file(py_file)

                if updated:
                    results['updated_files'].append(str(py_file))
                    logger.info(f"Updated imports in {py_file}")

                if unresolved:
                    results['unresolved_imports'].extend(unresolved)

            except Exception as e:
                error_msg = f"Error processing {py_file}: {e}"
                results['errors'].append(error_msg)
                logger.error(error_msg)

        return results

    def generate_report(self, analysis_results: Dict, update_results: Dict) -> str:
        """Generate a comprehensive report"""
        from datetime import datetime

        report = []
        report.append("# FANWS Import Analysis and Update Report\\n")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")

        # Analysis summary
        report.append("## Analysis Summary\\n")
        total_files = len(analysis_results)
        total_functions = sum(len(result['functions']) for result in analysis_results.values())
        total_classes = sum(len(result['classes']) for result in analysis_results.values())

        report.append(f"- **Files analyzed**: {total_files}")
        report.append(f"- **Functions found**: {total_functions}")
        report.append(f"- **Classes found**: {total_classes}")
        report.append("")

        # Update summary
        report.append("## Import Update Summary\\n")
        report.append(f"- **Files updated**: {len(update_results['updated_files'])}")
        report.append(f"- **Unresolved imports**: {len(update_results['unresolved_imports'])}")
        report.append(f"- **Errors encountered**: {len(update_results['errors'])}")
        report.append("")

        # Updated files
        if update_results['updated_files']:
            report.append("## Updated Files\\n")
            for file_path in update_results['updated_files']:
                report.append(f"- {file_path}")
            report.append("")

        # Unresolved imports
        if update_results['unresolved_imports']:
            report.append("## Unresolved Imports (Needs Manual Review)\\n")
            for unresolved in update_results['unresolved_imports']:
                report.append(f"- {unresolved}")
            report.append("")

        # Errors
        if update_results['errors']:
            report.append("## Errors\\n")
            for error in update_results['errors']:
                report.append(f"- {error}")
            report.append("")

        # Function intention analysis
        report.append("## Function Intention Analysis\\n")
        intention_counts = defaultdict(int)
        for result in analysis_results.values():
            for func in result['functions']:
                intention_counts[func['intention']] += 1

        for intention, count in sorted(intention_counts.items()):
            report.append(f"- **{intention}**: {count} functions")
        report.append("")

        return "\\n".join(report)

def main():
    """Main execution function"""
    logger.info("Starting FANWS Import Analysis and Correction")

    analyzer = FunctionAnalyzer()

    # Step 1: Analyze the entire application
    logger.info("Step 1: Analyzing entire application...")
    analysis_results = analyzer.scan_entire_application()

    # Step 2: Update all imports
    logger.info("Step 2: Updating all imports...")
    update_results = analyzer.update_all_imports()

    # Step 3: Generate report
    logger.info("Step 3: Generating report...")
    report = analyzer.generate_report(analysis_results, update_results)

    # Save results
    with open('import_analysis_results.json', 'w') as f:
        json.dump({
            'analysis': {k: {**v, 'dependencies': list(v['dependencies']), 'exports': list(v['exports'])}
                        for k, v in analysis_results.items()},
            'updates': update_results
        }, f, indent=2)

    with open('IMPORT_ANALYSIS_REPORT.md', 'w') as f:
        f.write(report)

    logger.info("Analysis complete! Check IMPORT_ANALYSIS_REPORT.md for details.")

    # Print summary
    print("\\n" + "="*60)
    print("FANWS IMPORT ANALYSIS COMPLETE")
    print("="*60)
    print(f"Files analyzed: {len(analysis_results)}")
    print(f"Files updated: {len(update_results['updated_files'])}")
    print(f"Unresolved imports: {len(update_results['unresolved_imports'])}")
    print(f"Errors: {len(update_results['errors'])}")
    print("\\nDetailed report saved to: IMPORT_ANALYSIS_REPORT.md")
    print("Raw data saved to: import_analysis_results.json")

if __name__ == "__main__":
    main()
