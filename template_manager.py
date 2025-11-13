"""Compatibility shim for legacy imports.

This module exposes the attributes from `src.templates.template_manager`
and ensures module-level names like `logger` are available for tests
that patch `template_manager.logger`.
"""

from importlib import import_module

_mod = import_module('src.templates.template_manager')

# Re-export module attributes
for _name in dir(_mod):
	if not _name.startswith('_'):
		try:
			globals()[_name] = getattr(_mod, _name)
		except Exception:
			pass

__all__ = [name for name in globals().keys() if not name.startswith('_')]
