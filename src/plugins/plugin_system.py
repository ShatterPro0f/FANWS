"""
FANWS Plugin System - Priority 4.4 Implementation
Comprehensive plugin architecture for extensibility and customization.
"""

import os
import sys
import json
import logging
import importlib
import inspect
from typing import Dict, List, Optional, Type, Any, Callable, Union
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
import threading
from enum import Enum
import concurrent.futures
import traceback
import hashlib
import subprocess
try:
    import importlib.metadata as metadata
    METADATA_AVAILABLE = True
except ImportError:
    # Fallback to pkg_resources for older Python versions
    try:
        import pkg_resources
        metadata = None
        METADATA_AVAILABLE = False
    except ImportError:
        pkg_resources = None
        metadata = None
        METADATA_AVAILABLE = False

# Plugin system configuration
PLUGIN_API_VERSION = "1.0.0"
PLUGIN_DIRECTORY = "plugins"
PLUGIN_CONFIG_FILE = "plugin_config.json"
PLUGIN_MANIFEST_FILE = "plugin_manifest.json"

class PluginType(Enum):
    """Types of plugins supported by the system."""
    WORKFLOW_STEP = "workflow_step"
    CONTENT_GENERATOR = "content_generator"
    EXPORT_FORMAT = "export_format"
    TEXT_PROCESSOR = "text_processor"
    UI_COMPONENT = "ui_component"
    DATA_SOURCE = "data_source"
    INTEGRATION = "integration"
    ANALYTICS = "analytics"

class PluginStatus(Enum):
    """Plugin status enumeration."""
    INACTIVE = "inactive"
    LOADING = "loading"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class PluginInfo:
    """Plugin information structure."""
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    api_version: str
    dependencies: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    entry_point: str = ""
    file_path: str = ""
    status: PluginStatus = PluginStatus.INACTIVE
    error_message: str = ""
    load_time: Optional[datetime] = None
    last_used: Optional[datetime] = None
    required_methods: List[str] = field(default_factory=list)
    python_version: str = ""
    checksum: str = ""

@dataclass
class PluginValidationResult:
    """Result of plugin validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_methods: List[str] = field(default_factory=list)
    missing_dependencies: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)

class PluginInterface(ABC):
    """Base interface for all plugins."""

    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Get plugin information."""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration."""
        pass

    @abstractmethod
    def cleanup(self) -> bool:
        """Clean up plugin resources."""
        pass

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        return True

    def get_capabilities(self) -> List[str]:
        """Get list of plugin capabilities."""
        return []

    def get_required_methods(self) -> List[str]:
        """Get list of methods that must be implemented by this plugin."""
        return ['get_info', 'initialize', 'cleanup']

    def get_required_dependencies(self) -> List[str]:
        """Get list of required dependencies for this plugin."""
        return []

    def validate_environment(self) -> PluginValidationResult:
        """Validate the plugin environment and dependencies."""
        result = PluginValidationResult(is_valid=True)

        # Check required methods
        required_methods = self.get_required_methods()
        for method_name in required_methods:
            if not hasattr(self, method_name) or not callable(getattr(self, method_name)):
                result.missing_methods.append(method_name)
                result.is_valid = False

        # Check required dependencies
        required_deps = self.get_required_dependencies()
        for dep in required_deps:
            if not self._check_dependency(dep):
                result.missing_dependencies.append(dep)
                result.is_valid = False

        return result

    def _check_dependency(self, dependency: str) -> bool:
        """Check if a dependency is available."""
        try:
            # Try to import the dependency
            if '.' in dependency:
                # Module with submodule
                module_parts = dependency.split('.')
                module = __import__(module_parts[0])
                for part in module_parts[1:]:
                    module = getattr(module, part)
            else:
                __import__(dependency)
            return True
        except ImportError:
            # Try using package distribution checking
            try:
                if METADATA_AVAILABLE and metadata:
                    metadata.distribution(dependency)
                    return True
                elif pkg_resources:
                    pkg_resources.get_distribution(dependency)
                    return True
                else:
                    return False
            except:
                return False

    def run_in_thread(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """Run a function in a separate thread to prevent crashes."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(func, *args, **kwargs)

class WorkflowStepPlugin(PluginInterface):
    """Base class for workflow step plugins."""

    def __init__(self):
        self.workflow = None
        self.step_number = 0
        self.step_name = ""

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the workflow step."""
        pass

    @abstractmethod
    def validate_prerequisites(self) -> bool:
        """Validate step prerequisites."""
        pass

    def get_step_number(self) -> int:
        """Get the step number."""
        return self.step_number

    def set_workflow(self, workflow):
        """Set the workflow instance."""
        self.workflow = workflow

class ContentGeneratorPlugin(PluginInterface):
    """Base class for content generator plugins."""

    @abstractmethod
    def generate_content(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate content based on prompt and context."""
        pass

    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """Get supported content types."""
        pass

    def get_quality_score(self, content: str) -> float:
        """Get quality score for generated content."""
        return 0.0

class ExportFormatPlugin(PluginInterface):
    """Base class for export format plugins."""

    @abstractmethod
    def export(self, content: str, metadata: Dict[str, Any], output_path: str) -> bool:
        """Export content to specified format."""
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        """Get the format name."""
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the file extension for this format."""
        pass

    def validate_content(self, content: str) -> bool:
        """Validate content for export."""
        return True

class TextProcessorPlugin(PluginInterface):
    """Base class for text processor plugins."""

    @abstractmethod
    def process_text(self, text: str, options: Dict[str, Any]) -> str:
        """Process text with specified options."""
        pass

    @abstractmethod
    def get_processing_types(self) -> List[str]:
        """Get supported processing types."""
        pass

class UIComponentPlugin(PluginInterface):
    """Base class for UI component plugins."""

    @abstractmethod
    def create_widget(self, parent=None) -> Any:
        """Create and return the UI widget."""
        pass

    @abstractmethod
    def get_widget_type(self) -> str:
        """Get the widget type."""
        pass

class DataSourcePlugin(PluginInterface):
    """Base class for data source plugins."""

    @abstractmethod
    def connect(self, connection_string: str) -> bool:
        """Connect to data source."""
        pass

    @abstractmethod
    def query(self, query: str) -> List[Dict[str, Any]]:
        """Query data source."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from data source."""
        pass

class IntegrationPlugin(PluginInterface):
    """Base class for integration plugins."""

    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with external service."""
        pass

    @abstractmethod
    def sync_data(self, data: Dict[str, Any]) -> bool:
        """Sync data with external service."""
        pass

    @abstractmethod
    def get_service_name(self) -> str:
        """Get the external service name."""
        pass

class AnalyticsPlugin(PluginInterface):
    """Base class for analytics plugins."""

    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and return insights."""
        pass

    @abstractmethod
    def get_metrics(self) -> List[str]:
        """Get available metrics."""
        pass

class PluginRegistry:
    """Registry for managing plugins."""

    def __init__(self):
        self.plugins: Dict[str, PluginInfo] = {}
        self.loaded_plugins: Dict[str, PluginInterface] = {}
        self.plugin_types: Dict[PluginType, List[str]] = {
            plugin_type: [] for plugin_type in PluginType
        }
        self.listeners: Dict[str, List[Callable]] = {}
        self._lock = threading.RLock()

    def register_plugin(self, plugin_info: PluginInfo) -> bool:
        """Register a plugin."""
        with self._lock:
            try:
                # Validate plugin info
                if not self._validate_plugin_info(plugin_info):
                    return False

                # Check for conflicts
                if plugin_info.name in self.plugins:
                    existing = self.plugins[plugin_info.name]
                    if existing.version != plugin_info.version:
                        logging.warning(f"Plugin {plugin_info.name} version conflict: {existing.version} vs {plugin_info.version}")

                # Register plugin
                self.plugins[plugin_info.name] = plugin_info
                self.plugin_types[plugin_info.plugin_type].append(plugin_info.name)

                # Notify listeners
                self._notify_listeners('plugin_registered', plugin_info.name)

                logging.info(f"Registered plugin: {plugin_info.name} v{plugin_info.version}")
                return True

            except Exception as e:
                logging.error(f"Failed to register plugin {plugin_info.name}: {e}")
                return False

    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin."""
        with self._lock:
            try:
                if plugin_name not in self.plugins:
                    return False

                plugin_info = self.plugins[plugin_name]

                # Unload if loaded
                if plugin_name in self.loaded_plugins:
                    self.unload_plugin(plugin_name)

                # Remove from registry
                del self.plugins[plugin_name]
                if plugin_name in self.plugin_types[plugin_info.plugin_type]:
                    self.plugin_types[plugin_info.plugin_type].remove(plugin_name)

                # Notify listeners
                self._notify_listeners('plugin_unregistered', plugin_name)

                logging.info(f"Unregistered plugin: {plugin_name}")
                return True

            except Exception as e:
                logging.error(f"Failed to unregister plugin {plugin_name}: {e}")
                return False

    def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin."""
        with self._lock:
            try:
                if plugin_name not in self.plugins:
                    logging.error(f"Plugin {plugin_name} not registered")
                    return False

                plugin_info = self.plugins[plugin_name]

                if plugin_name in self.loaded_plugins:
                    logging.info(f"Plugin {plugin_name} already loaded")
                    return True

                # Update status
                plugin_info.status = PluginStatus.LOADING

                # Load plugin module
                plugin_instance = self._load_plugin_instance(plugin_info)
                if not plugin_instance:
                    plugin_info.status = PluginStatus.ERROR
                    plugin_info.error_message = "Failed to load plugin instance"
                    return False

                # Initialize plugin
                config = self._get_plugin_config(plugin_name)
                if not plugin_instance.initialize(config):
                    plugin_info.status = PluginStatus.ERROR
                    plugin_info.error_message = "Plugin initialization failed"
                    return False

                # Store loaded plugin
                self.loaded_plugins[plugin_name] = plugin_instance
                plugin_info.status = PluginStatus.ACTIVE
                plugin_info.load_time = datetime.now()
                plugin_info.error_message = ""

                # Notify listeners
                self._notify_listeners('plugin_loaded', plugin_name)

                logging.info(f"Loaded plugin: {plugin_name}")
                return True

            except Exception as e:
                logging.error(f"Failed to load plugin {plugin_name}: {e}")
                if plugin_name in self.plugins:
                    self.plugins[plugin_name].status = PluginStatus.ERROR
                    self.plugins[plugin_name].error_message = str(e)
                return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        with self._lock:
            try:
                if plugin_name not in self.loaded_plugins:
                    return True

                plugin_instance = self.loaded_plugins[plugin_name]

                # Cleanup plugin
                plugin_instance.cleanup()

                # Remove from loaded plugins
                del self.loaded_plugins[plugin_name]

                # Update status
                if plugin_name in self.plugins:
                    self.plugins[plugin_name].status = PluginStatus.INACTIVE

                # Notify listeners
                self._notify_listeners('plugin_unloaded', plugin_name)

                logging.info(f"Unloaded plugin: {plugin_name}")
                return True

            except Exception as e:
                logging.error(f"Failed to unload plugin {plugin_name}: {e}")
                return False

    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """Get a loaded plugin instance."""
        return self.loaded_plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInterface]:
        """Get all loaded plugins of a specific type."""
        plugins = []
        for plugin_name in self.plugin_types[plugin_type]:
            if plugin_name in self.loaded_plugins:
                plugins.append(self.loaded_plugins[plugin_name])
        return plugins

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin information."""
        return self.plugins.get(plugin_name)

    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[PluginInfo]:
        """List all plugins or plugins of a specific type."""
        if plugin_type is None:
            return list(self.plugins.values())
        else:
            return [self.plugins[name] for name in self.plugin_types[plugin_type] if name in self.plugins]

    def add_listener(self, event: str, callback: Callable):
        """Add event listener."""
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)

    def remove_listener(self, event: str, callback: Callable):
        """Remove event listener."""
        if event in self.listeners and callback in self.listeners[event]:
            self.listeners[event].remove(callback)

    def _notify_listeners(self, event: str, plugin_name: str):
        """Notify event listeners."""
        if event in self.listeners:
            for callback in self.listeners[event]:
                try:
                    callback(plugin_name)
                except Exception as e:
                    logging.error(f"Error in plugin event listener: {e}")

    def _validate_plugin_info(self, plugin_info: PluginInfo) -> bool:
        """Validate plugin information with comprehensive checks"""
        errors = []

        # Basic validation
        if not plugin_info.name or not plugin_info.name.strip():
            errors.append("Plugin name is required")

        if not plugin_info.version or not plugin_info.version.strip():
            errors.append("Plugin version is required")

        # Version format validation
        try:
            version_parts = plugin_info.version.split('.')
            if len(version_parts) < 2 or not all(part.isdigit() for part in version_parts):
                errors.append("Plugin version must be in format 'x.y' or 'x.y.z'")
        except Exception:
            errors.append("Invalid version format")

        # API version compatibility
        if plugin_info.api_version != PLUGIN_API_VERSION:
            errors.append(f"Plugin API version mismatch: {plugin_info.api_version} vs {PLUGIN_API_VERSION}")

        # Plugin type validation
        if plugin_info.plugin_type not in PluginType:
            errors.append(f"Invalid plugin type: {plugin_info.plugin_type}")

        # File path validation
        if plugin_info.file_path and not os.path.exists(plugin_info.file_path):
            errors.append(f"Plugin file not found: {plugin_info.file_path}")

        # Dependencies validation
        if plugin_info.dependencies:
            for dep in plugin_info.dependencies:
                if not isinstance(dep, str) or not dep.strip():
                    errors.append(f"Invalid dependency format: {dep}")

        # Log errors
        if errors:
            for error in errors:
                logging.error(f"Plugin validation error for {plugin_info.name}: {error}")
            return False

        # Warnings for missing optional fields
        if not plugin_info.description:
            logging.warning(f"Plugin {plugin_info.name} has no description")

        if not plugin_info.author:
            logging.warning(f"Plugin {plugin_info.name} has no author")

        return True

    def validate_plugin_instance(self, plugin_instance: PluginInterface, plugin_info: PluginInfo) -> bool:
        """Validate a plugin instance has all required methods"""
        try:
            # Check if it's the correct type
            if not isinstance(plugin_instance, PluginInterface):
                logging.error(f"Plugin {plugin_info.name} does not implement PluginInterface")
                return False

            # Check required methods exist and are callable
            required_methods = ['get_info', 'initialize', 'cleanup']
            for method_name in required_methods:
                if not hasattr(plugin_instance, method_name):
                    logging.error(f"Plugin {plugin_info.name} missing required method: {method_name}")
                    return False

                method = getattr(plugin_instance, method_name)
                if not callable(method):
                    logging.error(f"Plugin {plugin_info.name} method {method_name} is not callable")
                    return False

            # Type-specific validation
            if plugin_info.plugin_type == PluginType.CONTENT_GENERATOR:
                type_methods = ['generate_content', 'get_supported_types']
            elif plugin_info.plugin_type == PluginType.EXPORT_FORMAT:
                type_methods = ['export', 'get_format_name', 'get_file_extension']
            elif plugin_info.plugin_type == PluginType.WORKFLOW_STEP:
                type_methods = ['execute', 'get_step_name']
            else:
                type_methods = []

            for method_name in type_methods:
                if not hasattr(plugin_instance, method_name):
                    logging.error(f"Plugin {plugin_info.name} missing type-specific method: {method_name}")
                    return False

            # Test plugin info method
            try:
                info = plugin_instance.get_info()
                if not isinstance(info, PluginInfo):
                    logging.error(f"Plugin {plugin_info.name} get_info() does not return PluginInfo")
                    return False
            except Exception as e:
                logging.error(f"Plugin {plugin_info.name} get_info() failed: {e}")
                return False

            return True

        except Exception as e:
            logging.error(f"Plugin validation failed for {plugin_info.name}: {e}")
            return False

    def _load_plugin_instance(self, plugin_info: PluginInfo) -> Optional[PluginInterface]:
        """Load plugin instance from file with enhanced error handling"""
        try:
            # Check if instance is already loaded
            if plugin_info.name in self.loaded_plugins:
                return self.loaded_plugins[plugin_info.name]

            # Validate plugin file exists
            if not plugin_info.file_path or not os.path.exists(plugin_info.file_path):
                logging.error(f"Plugin file not found: {plugin_info.file_path}")
                return None

            # Calculate and verify checksum if available
            if plugin_info.checksum:
                current_checksum = self._calculate_file_checksum(plugin_info.file_path)
                if current_checksum != plugin_info.checksum:
                    logging.error(f"Plugin checksum mismatch for {plugin_info.name}")
                    return None

            # Load plugin module
            spec = importlib.util.spec_from_file_location(plugin_info.name, plugin_info.file_path)
            if spec is None or spec.loader is None:
                logging.error(f"Could not load plugin spec for {plugin_info.name}")
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin class
            plugin_class = self._find_plugin_class(module, plugin_info)
            if plugin_class is None:
                logging.error(f"Could not find plugin class in {plugin_info.name}")
                return None

            # Create plugin instance
            plugin_instance = plugin_class()

            # Validate plugin instance
            if not self.validate_plugin_instance(plugin_instance, plugin_info):
                return None

            # Validate dependencies
            if not self._validate_plugin_dependencies(plugin_info):
                logging.error(f"Plugin {plugin_info.name} has missing dependencies")
                return None

            return plugin_instance

        except Exception as e:
            logging.error(f"Failed to load plugin {plugin_info.name}: {e}")
            logging.error(traceback.format_exc())
            return None

    def execute_plugin_safely(self, plugin_name: str, method_name: str, *args, **kwargs) -> Any:
        """Execute plugin method safely in a separate thread"""
        try:
            plugin = self.get_plugin(plugin_name)
            if plugin is None:
                raise ValueError(f"Plugin {plugin_name} not loaded")

            if not hasattr(plugin, method_name):
                raise AttributeError(f"Plugin {plugin_name} has no method {method_name}")

            method = getattr(plugin, method_name)
            if not callable(method):
                raise TypeError(f"Plugin {plugin_name} method {method_name} is not callable")

            # Execute in separate thread with timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(method, *args, **kwargs)
                try:
                    # Wait up to 30 seconds for plugin method to complete
                    result = future.result(timeout=30)

                    # Update last used time
                    if plugin_name in self.plugins:
                        self.plugins[plugin_name].last_used = datetime.now()

                    return result
                except concurrent.futures.TimeoutError:
                    logging.error(f"Plugin {plugin_name} method {method_name} timed out")
                    raise TimeoutError(f"Plugin method timed out")

        except Exception as e:
            logging.error(f"Error executing plugin {plugin_name}.{method_name}: {e}")

            # Mark plugin as having an error
            if plugin_name in self.plugins:
                self.plugins[plugin_name].status = PluginStatus.ERROR
                self.plugins[plugin_name].error_message = str(e)

            raise

    def _validate_plugin_dependencies(self, plugin_info: PluginInfo) -> bool:
        """Validate plugin dependencies are available"""
        try:
            for dependency in plugin_info.dependencies:
                if not self._check_dependency_available(dependency):
                    logging.error(f"Plugin {plugin_info.name} missing dependency: {dependency}")
                    return False
            return True
        except Exception as e:
            logging.error(f"Error validating dependencies for {plugin_info.name}: {e}")
            return False

    def _check_dependency_available(self, dependency: str) -> bool:
        """Check if a specific dependency is available"""
        try:
            # Handle different dependency formats
            if dependency.startswith('pip:'):
                # pip package
                package_name = dependency[4:]
                try:
                    if METADATA_AVAILABLE and metadata:
                        metadata.distribution(package_name)
                        return True
                    elif pkg_resources:
                        pkg_resources.get_distribution(package_name)
                        return True
                    else:
                        return False
                except Exception:
                    return False
            elif dependency.startswith('python:'):
                # Python version requirement
                version_req = dependency[7:]
                current_version = '.'.join(map(str, sys.version_info[:2]))
                return self._compare_versions(current_version, version_req)
            else:
                # Python module
                try:
                    __import__(dependency)
                    return True
                except ImportError:
                    return False
        except Exception:
            return False

    def _compare_versions(self, current: str, required: str) -> bool:
        """Compare version strings"""
        try:
            current_parts = [int(x) for x in current.split('.')]
            required_parts = [int(x) for x in required.split('.')]

            # Pad with zeros to make same length
            max_len = max(len(current_parts), len(required_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            required_parts.extend([0] * (max_len - len(required_parts)))

            return current_parts >= required_parts
        except:
            return False

    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of plugin file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def _find_plugin_class(self, module, plugin_info: PluginInfo) -> Optional[Type[PluginInterface]]:
        """Find the plugin class in the module"""
        try:
            # Look for classes that inherit from PluginInterface
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, PluginInterface) and
                    obj != PluginInterface and
                    obj.__module__ == module.__name__):
                    return obj

            # Look for class with specific entry point
            if plugin_info.entry_point:
                if hasattr(module, plugin_info.entry_point):
                    obj = getattr(module, plugin_info.entry_point)
                    if inspect.isclass(obj) and issubclass(obj, PluginInterface):
                        return obj

            return None
        except Exception as e:
            logging.error(f"Error finding plugin class: {e}")
            return None

            if not plugin_info.file_path or not os.path.exists(plugin_info.file_path):
                logging.error(f"Plugin file not found: {plugin_info.file_path}")
                return None

            # Import plugin module with error handling
            try:
                spec = importlib.util.spec_from_file_location(plugin_info.name, plugin_info.file_path)
                if not spec or not spec.loader:
                    logging.error(f"Could not load plugin spec: {plugin_info.file_path}")
                    return None

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

            except ImportError as e:
                logging.error(f"Import error loading plugin {plugin_info.name}: {e}")
                return None
            except SyntaxError as e:
                logging.error(f"Syntax error in plugin {plugin_info.name}: {e}")
                return None
            except Exception as e:
                logging.error(f"Unexpected error loading plugin module {plugin_info.name}: {e}")
                return None

            # Find plugin class with better detection
            plugin_class = None
            plugin_classes = []

            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, PluginInterface) and
                    obj != PluginInterface):
                    plugin_classes.append((name, obj))

            if not plugin_classes:
                logging.error(f"No plugin class found in {plugin_info.file_path}")
                return None
            elif len(plugin_classes) == 1:
                plugin_class = plugin_classes[0][1]
            else:
                # Multiple classes found, prefer ones ending with 'Plugin'
                preferred = [cls for name, cls in plugin_classes if name.endswith('Plugin')]
                if preferred:
                    plugin_class = preferred[0]
                else:
                    plugin_class = plugin_classes[0][1]
                    logging.warning(f"Multiple plugin classes found in {plugin_info.file_path}, using {plugin_class.__name__}")

            # Create plugin instance with error handling
            try:
                plugin_instance = plugin_class()
            except TypeError as e:
                logging.error(f"Failed to instantiate plugin {plugin_info.name}: {e}")
                return None
            except Exception as e:
                logging.error(f"Unexpected error instantiating plugin {plugin_info.name}: {e}")
                return None

            # Validate plugin instance
            if not self.validate_plugin_instance(plugin_instance, plugin_info):
                logging.error(f"Plugin {plugin_info.name} failed validation")
                return None

            # Test initialization
            try:
                init_success = plugin_instance.initialize({})
                if not init_success:
                    logging.warning(f"Plugin {plugin_info.name} initialization returned False")
            except Exception as e:
                logging.error(f"Plugin {plugin_info.name} initialization failed: {e}")
                return None

            # Store the instance
            self.loaded_plugins[plugin_info.name] = plugin_instance
            logging.info(f"Successfully loaded plugin instance: {plugin_info.name}")
            return plugin_instance

        except Exception as e:
            logging.error(f"Failed to load plugin instance {plugin_info.name}: {e}")
            return None

    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin from disk"""
        with self._lock:
            if plugin_name not in self.plugins:
                logging.error(f"Plugin {plugin_name} not found for reload")
                return False

            try:
                plugin_info = self.plugins[plugin_name]

                # Remove from loaded plugins if present
                if plugin_name in self.loaded_plugins:
                    del self.loaded_plugins[plugin_name]

                # Clear module from sys.modules if present
                import sys
                module_name = os.path.splitext(os.path.basename(plugin_info.file_path))[0]
                if module_name in sys.modules:
                    del sys.modules[module_name]

                # Reload the plugin instance
                new_instance = self._load_plugin_instance(plugin_info)
                if new_instance:
                    logging.info(f"Reloaded plugin: {plugin_name}")
                    self._notify_listeners('plugin_reloaded', plugin_name)
                    return True
                else:
                    logging.error(f"Failed to reload plugin instance: {plugin_name}")
                    return False

            except Exception as e:
                logging.error(f"Failed to reload plugin {plugin_name}: {e}")
                return False

    def hot_reload_all_plugins(self) -> int:
        """Hot reload all plugins from disk"""
        reloaded_count = 0
        for plugin_name in list(self.plugins.keys()):
            if self.reload_plugin(plugin_name):
                reloaded_count += 1

        logging.info(f"Hot reloaded {reloaded_count} plugins")
        return reloaded_count

    def install_plugin_from_file(self, plugin_file_path: str) -> bool:
        """Install a new plugin from a file"""
        try:
            if not os.path.exists(plugin_file_path):
                logging.error(f"Plugin file not found: {plugin_file_path}")
                return False

            # Discover the plugin
            if plugin_file_path.endswith('.py'):
                plugin_info = self._discover_plugin_file(plugin_file_path)
            else:
                # Assume it's a directory with manifest
                plugin_info = self._discover_plugin_in_directory(plugin_file_path)

            if not plugin_info:
                logging.error(f"Failed to discover plugin from: {plugin_file_path}")
                return False

            # Check if plugin already exists
            if plugin_info.name in self.plugins:
                logging.warning(f"Plugin {plugin_info.name} already exists, reloading instead")
                return self.reload_plugin(plugin_info.name)

            # Register the plugin
            if self.register_plugin(plugin_info):
                # Enable the plugin by default
                self.enable_plugin(plugin_info.name)
                logging.info(f"Installed and enabled plugin: {plugin_info.name}")
                return True
            else:
                logging.error(f"Failed to register plugin: {plugin_info.name}")
                return False

        except Exception as e:
            logging.error(f"Failed to install plugin from {plugin_file_path}: {e}")
            return False

    def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall a plugin completely"""
        with self._lock:
            try:
                if plugin_name not in self.plugins:
                    logging.error(f"Plugin {plugin_name} not found for uninstall")
                    return False

                # Disable the plugin first
                self.disable_plugin(plugin_name)

                # Remove from loaded plugins
                if plugin_name in self.loaded_plugins:
                    del self.loaded_plugins[plugin_name]

                # Remove from registry
                plugin_info = self.plugins[plugin_name]
                self.plugin_types[plugin_info.plugin_type].remove(plugin_name)
                del self.plugins[plugin_name]

                # Notify listeners
                self._notify_listeners('plugin_uninstalled', plugin_name)

                logging.info(f"Uninstalled plugin: {plugin_name}")
                return True

            except Exception as e:
                logging.error(f"Failed to uninstall plugin {plugin_name}: {e}")
                return False
        """Get plugin configuration."""
        config_path = os.path.join(PLUGIN_DIRECTORY, plugin_name, PLUGIN_CONFIG_FILE)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load plugin config for {plugin_name}: {e}")
        return {}

class PluginManager:
    """Main plugin manager for the FANWS system."""

    def __init__(self, plugin_directory: str = PLUGIN_DIRECTORY):
        self.plugin_directory = plugin_directory
        self.registry = PluginRegistry()
        self.enabled_plugins = set()
        self.config = {}
        self._lock = threading.RLock()

        # Ensure plugin directory exists
        os.makedirs(plugin_directory, exist_ok=True)

        # Load configuration
        self._load_config()

        # Set up event handlers
        self._setup_event_handlers()

    def initialize(self):
        """Initialize the plugin manager."""
        logging.info("Initializing plugin manager...")

        try:
            # Discover plugins
            self.discover_plugins()

            # Load enabled plugins
            self.load_enabled_plugins()

            logging.info("Plugin manager initialized successfully")
            return True

        except Exception as e:
            logging.error(f"Plugin manager initialization failed: {e}")
            return False

    def discover_plugins(self):
        """Discover plugins in the plugin directory."""
        logging.info(f"Discovering plugins in {self.plugin_directory}")

        if not os.path.exists(self.plugin_directory):
            logging.warning(f"Plugin directory not found: {self.plugin_directory}")
            return 0

        discovered_count = 0
        for item in os.listdir(self.plugin_directory):
            item_path = os.path.join(self.plugin_directory, item)

            if os.path.isdir(item_path):
                # Discover plugins in subdirectories (with manifest files)
                plugin_info = self._discover_plugin_in_directory(item_path)
                if plugin_info:
                    if self.registry.register_plugin(plugin_info):
                        discovered_count += 1
            elif item.endswith('.py') and not item.startswith('__'):
                # Discover individual Python files as plugins
                plugin_info = self._discover_plugin_file(item_path)
                if plugin_info:
                    if self.registry.register_plugin(plugin_info):
                        discovered_count += 1

        logging.info(f"Discovered {discovered_count} plugins")
        return discovered_count

    def load_enabled_plugins(self):
        """Load all enabled plugins."""
        loaded_count = 0
        for plugin_name in self.enabled_plugins:
            if self.registry.load_plugin(plugin_name):
                loaded_count += 1

        logging.info(f"Loaded {loaded_count} enabled plugins")

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        with self._lock:
            if plugin_name not in self.registry.plugins:
                logging.error(f"Plugin {plugin_name} not found")
                return False

            self.enabled_plugins.add(plugin_name)
            self._save_config()

            # Load plugin if not already loaded
            if plugin_name not in self.registry.loaded_plugins:
                return self.registry.load_plugin(plugin_name)

            return True

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        with self._lock:
            if plugin_name in self.enabled_plugins:
                self.enabled_plugins.remove(plugin_name)
                self._save_config()

            # Unload plugin if loaded
            if plugin_name in self.registry.loaded_plugins:
                return self.registry.unload_plugin(plugin_name)

            return True

    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """Get a loaded plugin."""
        return self.registry.get_plugin(plugin_name)

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInterface]:
        """Get all loaded plugins of a specific type."""
        return self.registry.get_plugins_by_type(plugin_type)

    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[PluginInfo]:
        """List all plugins."""
        return self.registry.list_plugins(plugin_type)

    def get_plugin_status(self) -> Dict[str, Any]:
        """Get plugin system status."""
        return {
            'total_plugins': len(self.registry.plugins),
            'loaded_plugins': len(self.registry.loaded_plugins),
            'enabled_plugins': len(self.enabled_plugins),
            'plugin_types': {
                plugin_type.value: len(plugins)
                for plugin_type, plugins in self.registry.plugin_types.items()
            }
        }

    def _discover_plugin_in_directory(self, plugin_dir: str) -> Optional[PluginInfo]:
        """Discover plugin in a specific directory."""
        try:
            manifest_path = os.path.join(plugin_dir, PLUGIN_MANIFEST_FILE)
            if not os.path.exists(manifest_path):
                return None

            with open(manifest_path, 'r') as f:
                manifest = json.load(f)

            # Create plugin info
            plugin_info = PluginInfo(
                name=manifest['name'],
                version=manifest['version'],
                author=manifest.get('author', 'Unknown'),
                description=manifest.get('description', ''),
                plugin_type=PluginType(manifest['type']),
                api_version=manifest.get('api_version', '1.0.0'),
                dependencies=manifest.get('dependencies', []),
                permissions=manifest.get('permissions', []),
                config_schema=manifest.get('config_schema', {}),
                entry_point=manifest.get('entry_point', 'plugin.py'),
                file_path=os.path.join(plugin_dir, manifest.get('entry_point', 'plugin.py'))
            )

            return plugin_info

        except Exception as e:
            logging.error(f"Failed to discover plugin in {plugin_dir}: {e}")
            return None

    def _discover_plugin_file(self, plugin_file: str) -> Optional[PluginInfo]:
        """Discover plugin from a single Python file."""
        try:
            import importlib.util
            import importlib

            # Extract module name from file path
            module_name = os.path.splitext(os.path.basename(plugin_file))[0]

            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            if spec is None or spec.loader is None:
                return None

            module = importlib.util.module_from_spec(spec)

            # Add to sys.modules temporarily for proper import handling
            import sys
            sys.modules[module_name] = module

            spec.loader.exec_module(module)

            # Look for plugin classes
            plugin_instance = None
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    hasattr(attr, 'get_info') and
                    attr_name.endswith('Plugin')):
                    try:
                        # Try to instantiate the plugin
                        plugin_instance = attr()
                        plugin_class = attr
                        break
                    except Exception as e:
                        logging.debug(f"Failed to instantiate {attr_name}: {e}")
                        continue

            if plugin_instance and hasattr(plugin_instance, 'get_info'):
                plugin_info = plugin_instance.get_info()
                plugin_info.file_path = plugin_file
                plugin_info.entry_point = os.path.basename(plugin_file)

                # Store the instance for later use
                if hasattr(self, 'registry'):
                    self.registry.loaded_plugins[plugin_info.name] = plugin_instance

                return plugin_info

        except Exception as e:
            logging.error(f"Failed to discover plugin file {plugin_file}: {e}")

        return None

    def _load_config(self):
        """Load plugin manager configuration."""
        config_path = os.path.join(self.plugin_directory, 'manager_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                    self.enabled_plugins = set(self.config.get('enabled_plugins', []))
            except Exception as e:
                logging.error(f"Failed to load plugin manager config: {e}")

    def _save_config(self):
        """Save plugin manager configuration."""
        config_path = os.path.join(self.plugin_directory, 'manager_config.json')
        try:
            self.config['enabled_plugins'] = list(self.enabled_plugins)
            self.config['last_updated'] = datetime.now().isoformat()

            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save plugin manager config: {e}")

    def _setup_event_handlers(self):
        """Set up event handlers for the plugin system."""
        self.registry.add_listener('plugin_loaded', self._on_plugin_loaded)
        self.registry.add_listener('plugin_unloaded', self._on_plugin_unloaded)
        self.registry.add_listener('plugin_registered', self._on_plugin_registered)
        self.registry.add_listener('plugin_unregistered', self._on_plugin_unregistered)

    def _on_plugin_loaded(self, plugin_name: str):
        """Handle plugin loaded event."""
        logging.info(f"Plugin loaded: {plugin_name}")

    def _on_plugin_unloaded(self, plugin_name: str):
        """Handle plugin unloaded event."""
        logging.info(f"Plugin unloaded: {plugin_name}")

    def _on_plugin_registered(self, plugin_name: str):
        """Handle plugin registered event."""
        logging.info(f"Plugin registered: {plugin_name}")

    def _on_plugin_unregistered(self, plugin_name: str):
        """Handle plugin unregistered event."""
        logging.info(f"Plugin unregistered: {plugin_name}")

# Global plugin manager instance
_plugin_manager = None
_plugin_manager_lock = threading.Lock()

def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    global _plugin_manager

    if _plugin_manager is None:
        with _plugin_manager_lock:
            if _plugin_manager is None:
                _plugin_manager = PluginManager()

    return _plugin_manager

def initialize_plugin_system():
    """Initialize the plugin system."""
    plugin_manager = get_plugin_manager()
    plugin_manager.initialize()

# Plugin helper functions
def create_plugin_template(plugin_name: str, plugin_type: PluginType,
                          output_dir: str = PLUGIN_DIRECTORY) -> bool:
    """Create a plugin template."""
    try:
        plugin_dir = os.path.join(output_dir, plugin_name)
        os.makedirs(plugin_dir, exist_ok=True)

        # Create manifest
        manifest = {
            "name": plugin_name,
            "version": "1.0.0",
            "author": "Unknown",
            "description": f"A {plugin_type.value} plugin",
            "type": plugin_type.value,
            "api_version": PLUGIN_API_VERSION,
            "entry_point": "plugin.py",
            "dependencies": [],
            "permissions": [],
            "config_schema": {}
        }

        manifest_path = os.path.join(plugin_dir, PLUGIN_MANIFEST_FILE)
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        # Create plugin file
        plugin_code = _generate_plugin_template_code(plugin_name, plugin_type)
        plugin_path = os.path.join(plugin_dir, 'plugin.py')
        with open(plugin_path, 'w') as f:
            f.write(plugin_code)

        # Create config file
        config_path = os.path.join(plugin_dir, PLUGIN_CONFIG_FILE)
        with open(config_path, 'w') as f:
            json.dump({}, f, indent=2)

        logging.info(f"Created plugin template: {plugin_name}")
        return True

    except Exception as e:
        logging.error(f"Failed to create plugin template: {e}")
        return False

def _generate_plugin_template_code(plugin_name: str, plugin_type: PluginType) -> str:
    """Generate plugin template code."""
    class_name = ''.join(word.capitalize() for word in plugin_name.split('_'))

    base_class_map = {
        PluginType.WORKFLOW_STEP: "WorkflowStepPlugin",
        PluginType.CONTENT_GENERATOR: "ContentGeneratorPlugin",
        PluginType.EXPORT_FORMAT: "ExportFormatPlugin",
        PluginType.TEXT_PROCESSOR: "TextProcessorPlugin",
        PluginType.UI_COMPONENT: "UIComponentPlugin",
        PluginType.DATA_SOURCE: "DataSourcePlugin",
        PluginType.INTEGRATION: "IntegrationPlugin",
        PluginType.ANALYTICS: "AnalyticsPlugin"
    }

    base_class = base_class_map.get(plugin_type, "PluginInterface")

    template = f'''"""
{plugin_name} Plugin
Generated plugin template for {plugin_type.value}.
"""

from fanws_plugin_system import {base_class}, PluginInfo, PluginType
from typing import Dict, Any, List

class {class_name}({base_class}):
    """
    {plugin_name} plugin implementation.
    """

    def __init__(self):
        super().__init__()
        self.name = "{plugin_name}"
        self.version = "1.0.0"

    def get_info(self) -> PluginInfo:
        """Get plugin information."""
        return PluginInfo(
            name=self.name,
            version=self.version,
            author="Unknown",
            description="A {plugin_type.value} plugin",
            plugin_type=PluginType.{plugin_type.name},
            api_version="1.0.0"
        )

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin."""
        # Plugin initialization logic here
        return True

    def cleanup(self) -> bool:
        """Clean up plugin resources."""
        # Cleanup logic here
        return True

    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities."""
        return ["basic_functionality"]

    # Add plugin-specific methods here

'''

    # Add plugin-type specific methods
    if plugin_type == PluginType.WORKFLOW_STEP:
        template += '''
    def execute(self) -> Dict[str, Any]:
        """Execute the workflow step."""
        # Step execution logic here
        return {"success": True, "message": "Step executed successfully"}

    def validate_prerequisites(self) -> bool:
        """Validate step prerequisites."""
        # Validation logic here
        return True
'''
    elif plugin_type == PluginType.CONTENT_GENERATOR:
        template += '''
    def generate_content(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate content based on prompt and context."""
        # Content generation logic here
        return f"Generated content for: {prompt}"

    def get_supported_types(self) -> List[str]:
        """Get supported content types."""
        return ["text", "outline", "character"]
'''
    elif plugin_type == PluginType.EXPORT_FORMAT:
        template += '''
    def export(self, content: str, metadata: Dict[str, Any], output_path: str) -> bool:
        """Export content to specified format."""
        # Export logic here
        with open(output_path, 'w') as f:
            f.write(content)
        return True

    def get_format_name(self) -> str:
        """Get the format name."""
        return "Custom Format"

    def get_file_extension(self) -> str:
        """Get the file extension."""
        return ".txt"
'''

    return template

class PluginTemplateGenerator:
    """Generates plugin templates for rapid development."""

    def __init__(self):
        self.templates = {}
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize plugin templates."""
        self.templates['workflow_step'] = self._get_workflow_step_template()
        self.templates['content_generator'] = self._get_content_generator_template()
        self.templates['export_format'] = self._get_export_format_template()
        self.templates['text_processor'] = self._get_text_processor_template()

    def generate_workflow_step_template(self, class_name: str,
                                      description: str, step_number: int) -> str:
        """Generate a workflow step plugin template."""
        template = self.templates['workflow_step']
        return template.format(
            class_name=class_name,
            description=description,
            step_number=step_number
        )

    def generate_content_generator_template(self, class_name: str,
                                          description: str,
                                          supported_types: List[str]) -> str:
        """Generate a content generator plugin template."""
        template = self.templates['content_generator']
        types_str = ', '.join(f"'{t}'" for t in supported_types)
        return template.format(
            class_name=class_name,
            description=description,
            supported_types=types_str
        )

    def generate_export_format_template(self, class_name: str,
                                      description: str, format_name: str,
                                      file_extension: str) -> str:
        """Generate an export format plugin template."""
        template = self.templates['export_format']
        return template.format(
            class_name=class_name,
            description=description,
            format_name=format_name,
            file_extension=file_extension
        )

    def _get_workflow_step_template(self) -> str:
        """Get workflow step template."""
        return '''"""
{description}
"""

from typing import Dict, Any, List
from src.plugins.plugin_system import WorkflowStepPlugin, PluginInfo, PluginType

class {class_name}(WorkflowStepPlugin):
    """Custom workflow step plugin."""

    def __init__(self):
        super().__init__()
        self.workflow = None
        self.step_number = {step_number}

    def get_info(self) -> PluginInfo:
        """Get plugin information."""
        return PluginInfo(
            name="{class_name}",
            version="1.0.0",
            description="{description}",
            author="Plugin Author",
            plugin_type=PluginType.WORKFLOW_STEP,
            dependencies=[]
        )

    def get_step_number(self) -> int:
        """Get the step number this plugin handles."""
        return self.step_number

    def get_step_name(self) -> str:
        """Get the name of this step."""
        return "{class_name}"

    def get_step_description(self) -> str:
        """Get description of what this step does."""
        return "{description}"

    def validate_prerequisites(self) -> bool:
        """Validate that prerequisites are met."""
        return self.workflow is not None

    def execute(self) -> Dict[str, Any]:
        """Execute the workflow step."""
        try:
            # TODO: Implement step logic
            return {{
                'success': True,
                'message': 'Step executed successfully'
            }}
        except Exception as e:
            return {{
                'success': False,
                'error': str(e)
            }}

    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this plugin provides."""
        return ['custom_processing']

    def set_workflow(self, workflow):
        """Set the workflow instance."""
        self.workflow = workflow

# Plugin registration
PLUGIN_CLASS = {class_name}
'''

    def _get_content_generator_template(self) -> str:
        """Get content generator template."""
        return '''"""
{description}
"""

from typing import Dict, Any, List
from src.plugins.plugin_system import ContentGeneratorPlugin, PluginInfo, PluginType

class {class_name}(ContentGeneratorPlugin):
    """Custom content generator plugin."""

    def __init__(self):
        super().__init__()
        self.supported_types = [{supported_types}]

    def get_info(self) -> PluginInfo:
        """Get plugin information."""
        return PluginInfo(
            name="{class_name}",
            version="1.0.0",
            description="{description}",
            author="Plugin Author",
            plugin_type=PluginType.CONTENT_GENERATOR,
            dependencies=[]
        )

    def get_supported_types(self) -> List[str]:
        """Get supported content types."""
        return self.supported_types

    def generate_content(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate content based on prompt and context."""
        # TODO: Implement content generation logic
        return f"Generated content based on: {{prompt}}"

    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        return ['content_generation']

# Plugin registration
PLUGIN_CLASS = {class_name}
'''

    def _get_export_format_template(self) -> str:
        """Get export format template."""
        return '''"""
{description}
"""

from typing import Dict, Any, List
from src.plugins.plugin_system import ExportFormatPlugin, PluginInfo, PluginType

class {class_name}(ExportFormatPlugin):
    """Custom export format plugin."""

    def __init__(self):
        super().__init__()
        self.format_name = "{format_name}"
        self.file_extension = "{file_extension}"

    def get_info(self) -> PluginInfo:
        """Get plugin information."""
        return PluginInfo(
            name="{class_name}",
            version="1.0.0",
            description="{description}",
            author="Plugin Author",
            plugin_type=PluginType.EXPORT_FORMAT,
            dependencies=[]
        )

    def get_format_name(self) -> str:
        """Get the format name."""
        return self.format_name

    def get_file_extension(self) -> str:
        """Get the file extension."""
        return self.file_extension

    def export(self, content: str, metadata: Dict[str, Any],
              output_path: str) -> bool:
        """Export content to file."""
        try:
            # TODO: Implement export logic
            with open(output_path, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            return False

    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        return ['file_export']

# Plugin registration
PLUGIN_CLASS = {class_name}
'''

    def _get_text_processor_template(self) -> str:
        """Get text processor template."""
        return '''"""
{description}
"""

from typing import Dict, Any, List
from src.plugins.plugin_system import TextProcessorPlugin, PluginInfo, PluginType

class {class_name}(TextProcessorPlugin):
    """Custom text processor plugin."""

    def __init__(self):
        super().__init__()
        self.processing_types = ['custom']

    def get_info(self) -> PluginInfo:
        """Get plugin information."""
        return PluginInfo(
            name="{class_name}",
            version="1.0.0",
            description="{description}",
            author="Plugin Author",
            plugin_type=PluginType.TEXT_PROCESSOR,
            dependencies=[]
        )

    def get_processing_types(self) -> List[str]:
        """Get supported processing types."""
        return self.processing_types

    def process_text(self, text: str, options: Dict[str, Any]) -> str:
        """Process text with options."""
        # TODO: Implement text processing logic
        return text

    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        return ['text_processing']

# Plugin registration
PLUGIN_CLASS = {class_name}
'''
