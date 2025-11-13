"""Compatibility shim for legacy imports.

Expose `plugin_system` at the repo root for older imports.
"""

from src.plugins.plugin_system import *  # noqa: F401,F403

__all__ = [name for name in dir() if not name.startswith("_")]
