"""
Plugin Manager - Main interface for FANWS Plugin System
Provides the expected interface that the main application uses.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Type
from datetime import datetime

# Import the actual plugin system implementation
try:
    from .plugin_system import (
        PluginManager as PluginSystemManager, PluginInterface, PluginInfo, PluginType, PluginStatus,
        PLUGIN_DIRECTORY, PLUGIN_CONFIG_FILE
    )
except ImportError:
    from .plugin_system import (
        PluginManager as PluginSystemManager, PluginInterface, PluginInfo, PluginType, PluginStatus,
        PLUGIN_DIRECTORY, PLUGIN_CONFIG_FILE
    )

class PluginManager:
    """
    Main plugin manager that provides a simplified interface to the plugin system.
    This is the primary interface used by the FANWS application.
    """

    def __init__(self):
        """Initialize the plugin manager"""
        self.plugin_system = PluginSystemManager()
        self.is_initialized = False

    def initialize(self) -> bool:
        """Initialize the plugin system"""
        try:
            success = self.plugin_system.initialize()
            self.is_initialized = success

            if success:
                # Load plugins from the plugins directory
                self.discover_and_load_plugins()

            return success

        except Exception as e:
            logging.error(f"Failed to initialize plugin manager: {e}")
            return False

    def discover_and_load_plugins(self):
        """Discover and load available plugins"""
        if not self.is_initialized:
            return

        try:
            # Discover plugins in the plugins directory
            self.plugin_system.discover_plugins()

            # Load enabled plugins
            self.plugin_system.load_enabled_plugins()

            logging.info(f"Plugin discovery complete. Found {len(self.get_available_plugins())} plugins.")

        except Exception as e:
            logging.error(f"Plugin discovery failed: {e}")

    def get_available_plugins(self) -> List[PluginInfo]:
        """Get list of all available plugins"""
        if not self.is_initialized:
            return []
        return self.plugin_system.list_plugins()

    def get_active_plugins(self) -> List[PluginInfo]:
        """Get list of active plugins"""
        if not self.is_initialized:
            return []
        # Get plugins that are both enabled and loaded
        active_plugins = []
        for plugin_name in self.plugin_system.enabled_plugins:
            if plugin_name in self.plugin_system.registry.loaded_plugins:
                plugin_info = self.plugin_system.registry.get_plugin_info(plugin_name)
                if plugin_info:
                    active_plugins.append(plugin_info)
        return active_plugins

    def get_plugin_by_name(self, name: str) -> Optional[PluginInfo]:
        """Get plugin by name"""
        if not self.is_initialized:
            return None
        return self.plugin_system.registry.get_plugin_info(name)

    def enable_plugin(self, name: str) -> bool:
        """Enable a plugin"""
        if not self.is_initialized:
            return False
        return self.plugin_system.enable_plugin(name)

    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin"""
        if not self.is_initialized:
            return False
        return self.plugin_system.disable_plugin(name)

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInfo]:
        """Get plugins by type"""
        if not self.is_initialized:
            return []
        return self.plugin_system.get_plugins_by_type(plugin_type)

    def execute_plugin_method(self, plugin_name: str, method_name: str, *args, **kwargs) -> Any:
        """Execute a method on a plugin"""
        if not self.is_initialized:
            return None
        plugin = self.plugin_system.get_plugin(plugin_name)
        if plugin and hasattr(plugin, method_name):
            method = getattr(plugin, method_name)
            if callable(method):
                return method(*args, **kwargs)
        return None

    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get plugin configuration"""
        if not self.is_initialized:
            return {}
        # Plugin config would be stored in the plugin system config
        return self.plugin_system.config.get(f"plugin_config_{plugin_name}", {})

    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Set plugin configuration"""
        if not self.is_initialized:
            return False
        try:
            self.plugin_system.config[f"plugin_config_{plugin_name}"] = config
            self.plugin_system._save_config()
            return True
        except Exception as e:
            logging.error(f"Failed to set plugin config for {plugin_name}: {e}")
            return False

class PluginIntegration:
    """
    Plugin integration helper for specific application areas
    """

    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager

    def get_workflow_plugins(self) -> List[PluginInfo]:
        """Get workflow step plugins"""
        return self.plugin_manager.get_plugins_by_type(PluginType.WORKFLOW_STEP)

    def get_content_generator_plugins(self) -> List[PluginInfo]:
        """Get content generator plugins"""
        return self.plugin_manager.get_plugins_by_type(PluginType.CONTENT_GENERATOR)

    def get_export_format_plugins(self) -> List[PluginInfo]:
        """Get export format plugins"""
        return self.plugin_manager.get_plugins_by_type(PluginType.EXPORT_FORMAT)

    def get_text_processor_plugins(self) -> List[PluginInfo]:
        """Get text processor plugins"""
        return self.plugin_manager.get_plugins_by_type(PluginType.TEXT_PROCESSOR)

    def get_ui_component_plugins(self) -> List[PluginInfo]:
        """Get UI component plugins"""
        return self.get_plugins_by_type(PluginType.UI_COMPONENT)

    def get_analytics_plugins(self) -> List[PluginInfo]:
        """Get analytics plugins"""
        return self.get_plugins_by_type(PluginType.ANALYTICS)

    # Hot reloading and management methods
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin from disk"""
        if not self.is_initialized:
            return False
        return self.plugin_system.registry.reload_plugin(plugin_name)

    def hot_reload_all_plugins(self) -> int:
        """Hot reload all plugins"""
        if not self.is_initialized:
            return 0
        return self.plugin_system.registry.hot_reload_all_plugins()

    def install_plugin_from_file(self, plugin_file_path: str) -> bool:
        """Install a new plugin from file"""
        if not self.is_initialized:
            return False
        return self.plugin_system.registry.install_plugin_from_file(plugin_file_path)

    def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall a plugin completely"""
        if not self.is_initialized:
            return False
        return self.plugin_system.registry.uninstall_plugin(plugin_name)

# Convenience aliases for the expected imports
Plugin = PluginInterface
PluginConfig = Dict[str, Any]

# Global plugin manager instance
_plugin_manager = None

def create_plugin_manager() -> PluginManager:
    """Create and initialize the global plugin manager"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
        _plugin_manager.initialize()
    return _plugin_manager

def get_plugin_manager() -> Optional[PluginManager]:
    """Get the global plugin manager instance"""
    global _plugin_manager
    return _plugin_manager

def initialize_plugin_system() -> bool:
    """Initialize the plugin system"""
    try:
        manager = create_plugin_manager()
        return manager.is_initialized
    except Exception as e:
        logging.error(f"Failed to initialize plugin system: {e}")
        return False
