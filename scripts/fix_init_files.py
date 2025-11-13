"""
Fix all __init__.py files in the src directory
"""

from pathlib import Path

def fix_init_files():
    """Fix imports in all __init__.py files"""
    src_path = Path('src')

    # Fix core/__init__.py
    core_init = src_path / 'core' / '__init__.py'
    core_content = '''"""
Core system modules for FANWS
Contains essential functionality used throughout the application
"""

from .constants import *
from .utils import *
from .configuration_manager import ConfigManager
from .error_handling_system import ErrorHandler
from .performance_monitor import PerformanceMonitor

__all__ = [
    'ConfigManager',
    'ErrorHandler',
    'PerformanceMonitor'
]'''

    with open(core_init, 'w') as f:
        f.write(core_content)
    print(f"Fixed {core_init}")

    # Fix other __init__.py files to use proper relative imports
    module_dirs = ['ai', 'analytics', 'collaboration', 'database', 'export_formats',
                   'plugins', 'project', 'system', 'templates', 'text', 'ui', 'workflow']

    for module_dir in module_dirs:
        init_file = src_path / module_dir / '__init__.py'
        if init_file.exists():
            with open(init_file, 'r') as f:
                content = f.read()

            # Fix imports to use relative imports
            content = content.replace('from ..', 'from .')
            content = content.replace('from .system.', 'from .')
            content = content.replace('from .core.', 'from .')
            content = content.replace('from .project.', 'from .')
            content = content.replace('from .plugins.', 'from .')
            content = content.replace('from .templates.', 'from .')
            content = content.replace('from .analytics.', 'from .')

            with open(init_file, 'w') as f:
                f.write(content)
            print(f"Fixed {init_file}")

if __name__ == "__main__":
    fix_init_files()
    print("All __init__.py files fixed!")
