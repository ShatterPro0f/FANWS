#!/usr/bin/env python3
"""
Plugin Workflow Integration
Integrates plugins with the main writing workflow.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

class PluginHook:
    """Represents a plugin hook point in the workflow."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.callbacks: List[Callable] = []

    def add_callback(self, callback: Callable):
        """Add a callback function to this hook."""
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        """Remove a callback function from this hook."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all callbacks for this hook."""
        result = context.copy()

        for callback in self.callbacks:
            try:
                callback_result = callback(result)
                if isinstance(callback_result, dict):
                    result.update(callback_result)
            except Exception as e:
                logging.error(f"Plugin hook '{self.name}' callback failed: {str(e)}")

        return result

class PluginWorkflowIntegration:
    """Manages plugin integration with the writing workflow."""

    def __init__(self):
        self.hooks: Dict[str, PluginHook] = {}
        self.active_plugins: List[str] = []
        self.plugin_data: Dict[str, Dict[str, Any]] = {}

        # Initialize standard workflow hooks
        self._initialize_standard_hooks()

    def _initialize_standard_hooks(self):
        """Initialize standard workflow hooks."""
        standard_hooks = [
            ("pre_chapter_generation", "Called before generating a chapter"),
            ("post_chapter_generation", "Called after generating a chapter"),
            ("pre_content_polish", "Called before polishing content"),
            ("post_content_polish", "Called after polishing content"),
            ("quality_check", "Called during quality assessment"),
            ("user_feedback", "Called when user feedback is received"),
            ("workflow_start", "Called when workflow starts"),
            ("workflow_complete", "Called when workflow completes"),
            ("project_create", "Called when a new project is created"),
            ("project_load", "Called when a project is loaded")
        ]

        for hook_name, description in standard_hooks:
            self.hooks[hook_name] = PluginHook(hook_name, description)

    def register_plugin(self, plugin_name: str, plugin_data: Dict[str, Any]):
        """Register a plugin with the workflow system."""
        self.active_plugins.append(plugin_name)
        self.plugin_data[plugin_name] = plugin_data
        logging.info(f"Plugin registered: {plugin_name}")

    def unregister_plugin(self, plugin_name: str):
        """Unregister a plugin from the workflow system."""
        if plugin_name in self.active_plugins:
            self.active_plugins.remove(plugin_name)

        if plugin_name in self.plugin_data:
            del self.plugin_data[plugin_name]

        # Remove all callbacks from this plugin
        for hook in self.hooks.values():
            callbacks_to_remove = []
            for callback in hook.callbacks:
                if hasattr(callback, '_plugin_name') and callback._plugin_name == plugin_name:
                    callbacks_to_remove.append(callback)

            for callback in callbacks_to_remove:
                hook.remove_callback(callback)

        logging.info(f"Plugin unregistered: {plugin_name}")

    def add_hook_callback(self, hook_name: str, callback: Callable, plugin_name: str = ""):
        """Add a callback to a workflow hook."""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = PluginHook(hook_name)

        # Tag callback with plugin name for cleanup
        if plugin_name:
            callback._plugin_name = plugin_name

        self.hooks[hook_name].add_callback(callback)

    def execute_hook(self, hook_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow hook."""
        if hook_name in self.hooks:
            try:
                result = self.hooks[hook_name].execute(context)
                logging.debug(f"Executed workflow hook: {hook_name}")
                return result
            except Exception as e:
                logging.error(f"Failed to execute workflow hook '{hook_name}': {str(e)}")

        return context

    def get_plugin_status(self) -> Dict[str, Any]:
        """Get status of all registered plugins."""
        return {
            "active_plugins": self.active_plugins.copy(),
            "total_hooks": len(self.hooks),
            "total_callbacks": sum(len(hook.callbacks) for hook in self.hooks.values()),
            "plugin_data": {name: data.get("info", {}) for name, data in self.plugin_data.items()}
        }

    def create_plugin_context(self, base_context: Dict[str, Any],
                            plugin_specific: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a context object for plugin execution."""
        context = {
            "timestamp": datetime.now().isoformat(),
            "workflow_active": True,
            **base_context
        }

        if plugin_specific:
            context.update(plugin_specific)

        return context

# Utility functions for common plugin operations
def create_content_filter_plugin(name: str, filter_func: Callable[[str], str]) -> Dict[str, Any]:
    """Create a content filter plugin."""
    return {
        "name": name,
        "type": "content_filter",
        "filter_function": filter_func,
        "info": {
            "description": f"Content filter plugin: {name}",
            "version": "1.0",
            "hooks": ["post_chapter_generation", "post_content_polish"]
        }
    }

def create_quality_checker_plugin(name: str, check_func: Callable[[str], Dict[str, Any]]) -> Dict[str, Any]:
    """Create a quality checker plugin."""
    return {
        "name": name,
        "type": "quality_checker",
        "check_function": check_func,
        "info": {
            "description": f"Quality checker plugin: {name}",
            "version": "1.0",
            "hooks": ["quality_check"]
        }
    }

__all__ = [
    'PluginHook', 'PluginWorkflowIntegration',
    'create_content_filter_plugin', 'create_quality_checker_plugin'
]
