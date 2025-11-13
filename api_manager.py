"""Compatibility shim for legacy imports.

Some tests and legacy code import top-level module names like
`api_manager`, `template_manager`, or `plugin_system`. The project
uses a `src` package; expose the same names at the repository root
so legacy imports continue to work during tests.
"""

from src.system.api_manager import *  # noqa: F401,F403

__all__ = [name for name in dir() if not name.startswith("_")]
