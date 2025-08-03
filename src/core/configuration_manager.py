"""
FANWS Unified Configuration Management System
Complete configuration management with advanced features, UI integration, and migration support.
"""

import os
import json
import yaml
import configparser
import logging
from typing import Dict, Any, Optional, List, Union, Type, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
import threading
import copy
from enum import Enum
import time
import shutil

# Configuration system constants
CONFIG_VERSION = "2.0.0"
DEFAULT_CONFIG_DIR = "config"
DEFAULT_CONFIG_FILE = "app_config.json"
ENV_CONFIG_PREFIX = "FANWS_"

class ConfigEnvironment(Enum):
    """Configuration environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class ConfigFormat(Enum):
    """Supported configuration file formats."""
    JSON = "json"
    YAML = "yaml"
    INI = "ini"
    ENV = "env"

@dataclass
class ConfigValidationRule:
    """Configuration validation rule."""
    field_path: str
    validator_type: str
    validator_args: Dict[str, Any] = field(default_factory=dict)
    required: bool = True
    default_value: Any = None
    description: str = ""

@dataclass
class ConfigChangeEvent:
    """Configuration change event."""
    timestamp: datetime
    key: str
    old_value: Any
    new_value: Any
    source: str = "manual"

class ConfigValidator:
    """Configuration value validator."""

    @staticmethod
    def validate_string(value: Any, min_length: int = 0, max_length: int = None, pattern: str = None) -> bool:
        """Validate string value."""
        if not isinstance(value, str):
            return False
        if len(value) < min_length:
            return False
        if max_length and len(value) > max_length:
            return False
        if pattern:
            import re
            return bool(re.match(pattern, value))
        return True

    @staticmethod
    def validate_number(value: Any, min_val: float = None, max_val: float = None) -> bool:
        """Validate numeric value."""
        if not isinstance(value, (int, float)):
            return False
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
        return True

    @staticmethod
    def validate_boolean(value: Any) -> bool:
        """Validate boolean value."""
        return isinstance(value, bool)

    @staticmethod
    def validate_list(value: Any, item_type: Type = None, min_items: int = 0, max_items: int = None) -> bool:
        """Validate list value."""
        if not isinstance(value, list):
            return False
        if len(value) < min_items:
            return False
        if max_items and len(value) > max_items:
            return False
        if item_type:
            return all(isinstance(item, item_type) for item in value)
        return True

class ConfigManager:
    """
    Unified Configuration Manager for FANWS
    Handles all configuration management including advanced features, UI integration, and migration.
    """

    def __init__(self, project_name: str = None, environment: str = "development", config_dir: str = None):
        """Initialize configuration manager."""
        self.project_name = project_name or "default"
        self.environment = ConfigEnvironment(environment) if isinstance(environment, str) else environment
        self.config_dir = Path(config_dir) if config_dir else Path(DEFAULT_CONFIG_DIR)

        # Core configuration storage
        self._config_data = {}
        self._default_config = {}
        self._validation_rules = {}
        self._change_history = []
        self._snapshots = {}
        self._templates = {}

        # Advanced features
        self._hot_reload_enabled = False
        self._file_watchers = []
        self._change_callbacks = []
        self._inheritance_chain = []

        # Migration and compatibility
        self._migration_hooks = {}
        self._migrated_components = set()
        self._compatibility_layer = None

        # Thread safety
        self._lock = threading.RLock()

        # Initialize configuration
        self._initialize()

    def _initialize(self):
        """Initialize configuration system."""
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Load default configuration
            self._load_default_config()

            # Load environment-specific configuration
            self._load_environment_config()

            # Initialize default validation rules
            self.initialize_default_validation_rules()

            # Set up file watchers for hot reload
            if self._hot_reload_enabled:
                self._setup_file_watchers()

            # Initialize migration system
            self._initialize_migration_system()

            logging.info(f"Configuration manager initialized for project '{self.project_name}' in '{self.environment.value}' environment")

        except Exception as e:
            logging.error(f"Failed to initialize configuration manager: {e}")
            raise

    def _load_default_config(self):
        """Load default configuration values."""
        self._default_config = {
            # AI Configuration
            "ai": {
                "openai": {
                    "api_key": "",
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "timeout": 30
                },
                "anthropic": {
                    "api_key": "",
                    "model": "claude-3-sonnet-20240229",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                "default_provider": "openai",
                "failover_enabled": True,
                "load_balancing": False
            },

            # UI Configuration
            "ui": {
                "theme": "light",
                "font_size": 12,
                "font_family": "Arial",
                "auto_save": True,
                "auto_save_interval": 60,
                "show_line_numbers": True,
                "word_wrap": True,
                "gui": True
            },

            # Database Configuration
            "database": {
                "path": "fanws.db",
                "pool_size": 5,
                "query_timeout": 30,
                "auto_vacuum": True,
                "wal_mode": True,
                "backup_enabled": True
            },

            # Project Configuration
            "project": {
                "idea": "",
                "tone": "neutral",
                "sub_tone": "neutral",
                "theme": "",
                "soft_target": 50000,
                "reading_level": "College",
                "thesaurus_weight": 0.5,
                "characters_seed": "",
                "world_seed": "",
                "themes_seed": "",
                "structure_seed": "25 chapters, 5 sections each",
                "custom_prompt": ""
            },

            # Workflow Configuration
            "workflow": {
                "default": "standard",
                "auto_save_drafts": True,
                "backup_frequency": 300,
                "max_parallel_tasks": 3,
                "async_enabled": True
            },

            # Plugin Configuration
            "plugins": {
                "directories": ["plugins/"],
                "auto_load": True,
                "timeout": 10,
                "hot_reload": False,
                "enabled": []
            },

            # Analytics Configuration
            "analytics": {
                "enabled": True,
                "session_tracking": True,
                "performance_monitoring": True,
                "export_format": "json"
            },

            # Collaboration Configuration
            "collaboration": {
                "enabled": False,
                "server_url": "",
                "auto_sync": True,
                "conflict_resolution": "manual"
            }
        }

        # Copy defaults to current config
        self._config_data = copy.deepcopy(self._default_config)

    def _load_environment_config(self):
        """Load environment-specific configuration."""
        env_file = self.config_dir / f"{self.environment.value}.json"
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    env_config = json.load(f)
                self._merge_config(self._config_data, env_config)
                logging.info(f"Loaded environment configuration: {env_file}")
            except Exception as e:
                logging.error(f"Failed to load environment config {env_file}: {e}")

    def _merge_config(self, base_config: Dict, override_config: Dict):
        """Merge configuration dictionaries."""
        for key, value in override_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value

    # Core configuration methods
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dotted key path."""
        with self._lock:
            try:
                keys = key.split('.')
                value = self._config_data

                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default

                return value
            except Exception:
                return default

    def set(self, key: str, value: Any) -> bool:
        """Set configuration value by dotted key path."""
        with self._lock:
            try:
                keys = key.split('.')
                config_ref = self._config_data

                # Navigate to parent of target key
                for k in keys[:-1]:
                    if k not in config_ref:
                        config_ref[k] = {}
                    config_ref = config_ref[k]

                # Store old value for history
                old_value = config_ref.get(keys[-1])

                # Validate new value
                if not self._validate_value(key, value):
                    logging.warning(f"Validation failed for key '{key}' with value '{value}'")
                    return False

                # Set new value
                config_ref[keys[-1]] = value

                # Record change
                change_event = ConfigChangeEvent(
                    timestamp=datetime.now(),
                    key=key,
                    old_value=old_value,
                    new_value=value
                )
                self._change_history.append(change_event)

                # Notify callbacks
                self._notify_change_callbacks(change_event)

                return True

            except Exception as e:
                logging.error(f"Failed to set config key '{key}': {e}")
                return False

    def save_config(self) -> bool:
        """Save current configuration to file."""
        with self._lock:
            try:
                config_file = self.config_dir / f"{self.project_name}_config.json"

                # Create backup if file exists
                if config_file.exists():
                    backup_file = config_file.with_suffix('.json.bak')
                    shutil.copy2(config_file, backup_file)

                # Save configuration
                with open(config_file, 'w') as f:
                    json.dump(self._config_data, f, indent=2, default=str)

                logging.info(f"Configuration saved to {config_file}")
                return True

            except Exception as e:
                logging.error(f"Failed to save configuration: {e}")
                return False

    def load_config(self) -> bool:
        """Load configuration from file."""
        with self._lock:
            try:
                config_file = self.config_dir / f"{self.project_name}_config.json"

                if not config_file.exists():
                    logging.info(f"No configuration file found: {config_file}")
                    return True  # Use defaults

                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)

                # Merge with defaults
                self._merge_config(self._config_data, loaded_config)

                logging.info(f"Configuration loaded from {config_file}")
                return True

            except Exception as e:
                logging.error(f"Failed to load configuration: {e}")
                return False

    # Advanced features
    def enable_hot_reload(self) -> bool:
        """Enable configuration hot reload."""
        try:
            self._hot_reload_enabled = True
            self._setup_file_watchers()
            logging.info("Configuration hot reload enabled")
            return True
        except Exception as e:
            logging.error(f"Failed to enable hot reload: {e}")
            return False

    def disable_hot_reload(self) -> bool:
        """Disable configuration hot reload."""
        try:
            self._hot_reload_enabled = False
            self._cleanup_file_watchers()
            logging.info("Configuration hot reload disabled")
            return True
        except Exception as e:
            logging.error(f"Failed to disable hot reload: {e}")
            return False

    def setup_configuration_inheritance(self, base_configs: List[str] = None) -> bool:
        """Set up configuration inheritance chain."""
        try:
            if base_configs:
                self._inheritance_chain = base_configs
                for base_config in base_configs:
                    base_file = self.config_dir / f"{base_config}.json"
                    if base_file.exists():
                        with open(base_file, 'r') as f:
                            base_data = json.load(f)
                        self._merge_config(self._config_data, base_data)
                logging.info(f"Configuration inheritance set up with {len(base_configs)} base configs")
                return True
            return False
        except Exception as e:
            logging.error(f"Failed to setup inheritance: {e}")
            return False

    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate current configuration against rules."""
        validation_errors = {}

        try:
            for key, rule in self._validation_rules.items():
                value = self.get(key)
                if rule.required and value is None:
                    if "required" not in validation_errors:
                        validation_errors["required"] = []
                    validation_errors["required"].append(f"Required key '{key}' is missing")
                elif value is not None and not self._validate_value(key, value):
                    if "validation" not in validation_errors:
                        validation_errors["validation"] = []
                    validation_errors["validation"].append(f"Key '{key}' failed validation")

            # Additional validation checks
            if not self.get("ai.openai.api_key") and not self.get("ai.anthropic.api_key"):
                if "configuration" not in validation_errors:
                    validation_errors["configuration"] = []
                validation_errors["configuration"].append("At least one AI API key must be configured")

            return validation_errors
        except Exception as e:
            logging.error(f"Configuration validation failed: {e}")
            return {"error": [str(e)]}

    def restore_from_snapshot(self, snapshot_id: str) -> bool:
        """Restore configuration from snapshot."""
        with self._lock:
            try:
                snapshot_file = self.config_dir / f"{snapshot_id}.json"
                if not snapshot_file.exists():
                    logging.error(f"Snapshot not found: {snapshot_id}")
                    return False

                with open(snapshot_file, 'r') as f:
                    snapshot_data = json.load(f)

                if "config" not in snapshot_data:
                    logging.error(f"Invalid snapshot format: {snapshot_id}")
                    return False

                # Create backup of current config
                backup_id = self.create_config_snapshot("Pre-restore backup")

                # Restore configuration
                self._config_data = copy.deepcopy(snapshot_data["config"])

                # Record change
                change_event = ConfigChangeEvent(
                    timestamp=datetime.now(),
                    key="__restore__",
                    old_value=f"backup_{backup_id}",
                    new_value=snapshot_id,
                    source="restore"
                )
                self._change_history.append(change_event)

                logging.info(f"Configuration restored from snapshot: {snapshot_id}")
                return True

            except Exception as e:
                logging.error(f"Failed to restore from snapshot: {e}")
                return False

    def export_configuration(self, format_type: ConfigFormat = ConfigFormat.JSON, include_history: bool = False) -> str:
        """Export configuration in specified format."""
        try:
            export_data = {
                "version": CONFIG_VERSION,
                "timestamp": datetime.now().isoformat(),
                "environment": self.environment.value,
                "project": self.project_name,
                "config": copy.deepcopy(self._config_data)
            }

            if include_history:
                export_data["history"] = [
                    {
                        "timestamp": event.timestamp.isoformat(),
                        "key": event.key,
                        "old_value": event.old_value,
                        "new_value": event.new_value,
                        "source": event.source
                    }
                    for event in self._change_history
                ]

            if format_type == ConfigFormat.JSON:
                return json.dumps(export_data, indent=2, default=str)
            elif format_type == ConfigFormat.YAML:
                import yaml
                return yaml.dump(export_data, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")

        except Exception as e:
            logging.error(f"Failed to export configuration: {e}")
            return None

    def import_configuration(self, config_data: str, format_type: ConfigFormat = ConfigFormat.JSON, merge: bool = True) -> bool:
        """Import configuration from data string."""
        try:
            if format_type == ConfigFormat.JSON:
                import_data = json.loads(config_data)
            elif format_type == ConfigFormat.YAML:
                import yaml
                import_data = yaml.safe_load(config_data)
            else:
                raise ValueError(f"Unsupported import format: {format_type}")

            if "config" not in import_data:
                logging.error("Invalid import data: missing 'config' section")
                return False

            # Create backup before import
            backup_id = self.create_config_snapshot("Pre-import backup")

            if merge:
                self._merge_config(self._config_data, import_data["config"])
            else:
                self._config_data = copy.deepcopy(import_data["config"])

            # Record change
            change_event = ConfigChangeEvent(
                timestamp=datetime.now(),
                key="__import__",
                old_value=f"backup_{backup_id}",
                new_value="imported_config",
                source="import"
            )
            self._change_history.append(change_event)

            logging.info("Configuration imported successfully")
            return True

        except Exception as e:
            logging.error(f"Failed to import configuration: {e}")
            return False

    def add_validation_rule(self, field_path: str, validator_type: str, **kwargs) -> bool:
        """Add validation rule for configuration field."""
        try:
            rule = ConfigValidationRule(
                field_path=field_path,
                validator_type=validator_type,
                validator_args=kwargs.get("validator_args", {}),
                required=kwargs.get("required", True),
                default_value=kwargs.get("default_value"),
                description=kwargs.get("description", "")
            )
            self._validation_rules[field_path] = rule
            logging.info(f"Added validation rule for '{field_path}'")
            return True
        except Exception as e:
            logging.error(f"Failed to add validation rule: {e}")
            return False

    def get_environment_configs(self) -> List[str]:
        """Get list of available environment configurations."""
        try:
            env_files = list(self.config_dir.glob("*.json"))
            environments = []
            for env_file in env_files:
                if env_file.stem in [e.value for e in ConfigEnvironment]:
                    environments.append(env_file.stem)
            return environments
        except Exception as e:
            logging.error(f"Failed to get environment configs: {e}")
            return []

    def switch_environment(self, environment: str) -> bool:
        """Switch to different environment configuration."""
        try:
            if environment not in [e.value for e in ConfigEnvironment]:
                logging.error(f"Invalid environment: {environment}")
                return False

            # Save current configuration
            current_backup = self.create_config_snapshot(f"Pre-switch to {environment}")

            # Reset to defaults
            self._config_data = copy.deepcopy(self._default_config)

            # Update environment
            self.environment = ConfigEnvironment(environment)

            # Load new environment config
            self._load_environment_config()

            # Record change
            change_event = ConfigChangeEvent(
                timestamp=datetime.now(),
                key="__environment__",
                old_value=current_backup,
                new_value=environment,
                source="environment_switch"
            )
            self._change_history.append(change_event)

            logging.info(f"Switched to environment: {environment}")
            return True

        except Exception as e:
            logging.error(f"Failed to switch environment: {e}")
            return False

    def create_config_snapshot(self, description: str = None) -> str:
        """Create configuration snapshot."""
        with self._lock:
            try:
                snapshot_id = f"snapshot_{int(time.time())}"
                snapshot_data = {
                    "id": snapshot_id,
                    "timestamp": datetime.now().isoformat(),
                    "description": description or f"Snapshot created at {datetime.now()}",
                    "config": copy.deepcopy(self._config_data),
                    "environment": self.environment.value,
                    "project": self.project_name
                }

                self._snapshots[snapshot_id] = snapshot_data

                # Save snapshot to file
                snapshot_file = self.config_dir / f"{snapshot_id}.json"
                with open(snapshot_file, 'w') as f:
                    json.dump(snapshot_data, f, indent=2, default=str)

                logging.info(f"Configuration snapshot created: {snapshot_id}")
                return snapshot_id

            except Exception as e:
                logging.error(f"Failed to create snapshot: {e}")
                return None

    def get_config_history(self, limit: int = 50) -> List[Dict]:
        """Get configuration change history."""
        with self._lock:
            return [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "key": event.key,
                    "old_value": event.old_value,
                    "new_value": event.new_value,
                    "source": event.source
                }
                for event in self._change_history[-limit:]
            ]

    def cleanup_old_snapshots(self, keep_count: int = 10) -> int:
        """Clean up old configuration snapshots."""
        try:
            snapshot_files = list(self.config_dir.glob("snapshot_*.json"))
            snapshot_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            cleaned = 0
            for snapshot_file in snapshot_files[keep_count:]:
                snapshot_file.unlink()
                cleaned += 1

            logging.info(f"Cleaned up {cleaned} old snapshots")
            return cleaned

        except Exception as e:
            logging.error(f"Failed to cleanup snapshots: {e}")
            return 0

    def get_configuration_templates(self) -> List[Dict]:
        """Get available configuration templates."""
        templates = [
            {
                "name": "Development",
                "description": "Development environment settings",
                "config": {"ai": {"openai": {"temperature": 0.8}}, "ui": {"theme": "dark"}}
            },
            {
                "name": "Production",
                "description": "Production environment settings",
                "config": {"ai": {"openai": {"temperature": 0.7}}, "ui": {"theme": "light"}}
            },
            {
                "name": "Testing",
                "description": "Testing environment settings",
                "config": {"ai": {"openai": {"temperature": 0.5}}, "database": {"path": ":memory:"}}
            }
        ]
        return templates

    # Migration system
    def _initialize_migration_system(self):
        """Initialize the migration system."""
        # Register standard migration hooks
        self._migration_hooks = {
            "api_manager": self._migrate_api_manager,
            "ui_components": self._migrate_ui_components,
            "database_manager": self._migrate_database_manager,
            "workflow_manager": self._migrate_workflow_manager,
            "plugin_system": self._migrate_plugin_system
        }

    def migrate_component(self, component_name: str, component_instance: Any) -> bool:
        """Migrate a component to use advanced configuration."""
        if component_name in self._migrated_components:
            return True

        if component_name not in self._migration_hooks:
            # Only warn for components that are expected to have migration hooks
            if component_name in ["api_manager", "ui_components", "database_manager", "workflow_manager", "plugin_system"]:
                logging.warning(f"No migration hook for component: {component_name}")
            else:
                logging.debug(f"No migration hook for component (not required): {component_name}")
            return False

        try:
            migration_func = self._migration_hooks[component_name]
            success = migration_func(component_instance)

            if success:
                self._migrated_components.add(component_name)
                logging.info(f"✓ Migrated component: {component_name}")

            return success

        except Exception as e:
            logging.error(f"Failed to migrate component {component_name}: {e}")
            return False

    def _migrate_api_manager(self, instance: Any) -> bool:
        """Migrate API manager to use advanced configuration."""
        try:
            api_settings = {
                "openai_api_key": self.get("ai.openai.api_key"),
                "anthropic_api_key": self.get("ai.anthropic.api_key"),
                "default_model": self.get("ai.openai.model", "gpt-4"),
                "temperature": self.get("ai.openai.temperature", 0.7),
                "max_tokens": self.get("ai.openai.max_tokens", 2000),
                "timeout": self.get("ai.openai.timeout", 30),
            }

            for key, value in api_settings.items():
                if value is not None and hasattr(instance, key):
                    setattr(instance, key, value)

            return True
        except Exception as e:
            logging.error(f"API manager migration failed: {e}")
            return False

    def _migrate_ui_components(self, instance: Any) -> bool:
        """Migrate UI components to use advanced configuration."""
        try:
            ui_settings = {
                "theme": self.get("ui.theme", "light"),
                "font_size": self.get("ui.font_size", 12),
                "auto_save": self.get("ui.auto_save", True),
                "auto_save_interval": self.get("ui.auto_save_interval", 60),
                "show_line_numbers": self.get("ui.show_line_numbers", True),
                "word_wrap": self.get("ui.word_wrap", True),
            }

            for key, value in ui_settings.items():
                if value is not None and hasattr(instance, key):
                    setattr(instance, key, value)

            return True
        except Exception as e:
            logging.error(f"UI components migration failed: {e}")
            return False

    def _migrate_database_manager(self, instance: Any) -> bool:
        """Migrate database manager to use advanced configuration."""
        try:
            db_settings = {
                "database_path": self.get("database.path", "fanws.db"),
                "connection_pool_size": self.get("database.pool_size", 5),
                "query_timeout": self.get("database.query_timeout", 30),
                "auto_vacuum": self.get("database.auto_vacuum", True),
                "wal_mode": self.get("database.wal_mode", True),
            }

            for key, value in db_settings.items():
                if value is not None and hasattr(instance, key):
                    setattr(instance, key, value)

            return True
        except Exception as e:
            logging.error(f"Database manager migration failed: {e}")
            return False

    def _migrate_workflow_manager(self, instance: Any) -> bool:
        """Migrate workflow manager to use advanced configuration."""
        try:
            workflow_settings = {
                "default_workflow": self.get("workflow.default", "standard"),
                "auto_save_drafts": self.get("workflow.auto_save_drafts", True),
                "backup_frequency": self.get("workflow.backup_frequency", 300),
                "max_parallel_tasks": self.get("workflow.max_parallel_tasks", 3),
            }

            for key, value in workflow_settings.items():
                if value is not None and hasattr(instance, key):
                    setattr(instance, key, value)

            return True
        except Exception as e:
            logging.error(f"Workflow manager migration failed: {e}")
            return False

    def _migrate_plugin_system(self, instance: Any) -> bool:
        """Migrate plugin system to use advanced configuration."""
        try:
            plugin_settings = {
                "plugin_directories": self.get("plugins.directories", ["plugins/"]),
                "auto_load_plugins": self.get("plugins.auto_load", True),
                "plugin_timeout": self.get("plugins.timeout", 10),
                "enable_hot_reload": self.get("plugins.hot_reload", False),
            }

            for key, value in plugin_settings.items():
                if value is not None and hasattr(instance, key):
                    setattr(instance, key, value)

            return True
        except Exception as e:
            logging.error(f"Plugin system migration failed: {e}")
            return False

    # Compatibility layer
    def create_compatibility_layer(self):
        """Create compatibility layer for legacy configuration access."""
        if self._compatibility_layer is None:
            self._compatibility_layer = ConfigCompatibilityLayer(self)
        return self._compatibility_layer

    # Utility methods
    def _validate_value(self, key: str, value: Any) -> bool:
        """Validate configuration value."""
        if key not in self._validation_rules:
            return True  # No validation rule = valid

        rule = self._validation_rules[key]
        validator_method = getattr(ConfigValidator, f"validate_{rule.validator_type}", None)

        if validator_method:
            return validator_method(value, **rule.validator_args)

        return True

    def _notify_change_callbacks(self, change_event: ConfigChangeEvent):
        """Notify registered change callbacks."""
        for callback in self._change_callbacks:
            try:
                callback(change_event)
            except Exception as e:
                logging.error(f"Error in change callback: {e}")

    def _setup_file_watchers(self):
        """Set up file watchers for hot reload."""
        try:
            import threading
            import time
            from pathlib import Path

            def watch_config_files():
                """Watch configuration files for changes."""
                watched_files = {}
                config_files = [
                    self.config_dir / f"{self.project_name}_config.json",
                    self.config_dir / f"{self.environment.value}.json"
                ]

                # Initialize file modification times
                for config_file in config_files:
                    if config_file.exists():
                        watched_files[config_file] = config_file.stat().st_mtime

                while self._hot_reload_enabled:
                    try:
                        for config_file in config_files:
                            if config_file.exists():
                                current_mtime = config_file.stat().st_mtime
                                if config_file in watched_files:
                                    if current_mtime > watched_files[config_file]:
                                        logging.info(f"Configuration file changed: {config_file}")
                                        self._reload_configuration()
                                        watched_files[config_file] = current_mtime
                                else:
                                    watched_files[config_file] = current_mtime

                        time.sleep(1)  # Check every second
                    except Exception as e:
                        logging.error(f"Error in file watcher: {e}")
                        time.sleep(5)  # Wait longer if error

            # Start watcher thread
            watcher_thread = threading.Thread(target=watch_config_files, daemon=True)
            watcher_thread.start()
            self._file_watchers.append(watcher_thread)

            logging.info("File watchers set up for hot reload")
        except Exception as e:
            logging.error(f"Failed to set up file watchers: {e}")

    def _cleanup_file_watchers(self):
        """Clean up file watchers."""
        try:
            self._hot_reload_enabled = False
            self._file_watchers.clear()
            logging.info("File watchers cleaned up")
        except Exception as e:
            logging.error(f"Failed to cleanup file watchers: {e}")

    def _reload_configuration(self):
        """Reload configuration from files."""
        with self._lock:
            try:
                # Create backup before reload
                backup_id = self.create_config_snapshot("Pre-reload backup")

                # Reset to defaults
                old_config = copy.deepcopy(self._config_data)
                self._config_data = copy.deepcopy(self._default_config)

                # Reload environment config
                self._load_environment_config()

                # Load project config
                self.load_config()

                # Record change
                change_event = ConfigChangeEvent(
                    timestamp=datetime.now(),
                    key="__reload__",
                    old_value=f"backup_{backup_id}",
                    new_value="reloaded",
                    source="hot_reload"
                )
                self._change_history.append(change_event)

                # Notify callbacks
                self._notify_change_callbacks(change_event)

                logging.info("Configuration reloaded from files")

            except Exception as e:
                logging.error(f"Failed to reload configuration: {e}")

    def add_change_callback(self, callback: Callable[[ConfigChangeEvent], None]):
        """Add callback for configuration changes."""
        self._change_callbacks.append(callback)

    def remove_change_callback(self, callback: Callable[[ConfigChangeEvent], None]):
        """Remove configuration change callback."""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)

    def get_validation_rules(self) -> Dict[str, ConfigValidationRule]:
        """Get all validation rules."""
        return self._validation_rules.copy()

    def apply_configuration_template(self, template_name: str) -> bool:
        """Apply a configuration template."""
        try:
            templates = self.get_configuration_templates()
            template = next((t for t in templates if t["name"] == template_name), None)

            if not template:
                logging.error(f"Template not found: {template_name}")
                return False

            # Create backup before applying template
            backup_id = self.create_config_snapshot(f"Pre-template: {template_name}")

            # Apply template configuration
            template_config = template.get("config", {})
            self._merge_config(self._config_data, template_config)

            # Record change
            change_event = ConfigChangeEvent(
                timestamp=datetime.now(),
                key="__template__",
                old_value=f"backup_{backup_id}",
                new_value=template_name,
                source="template"
            )
            self._change_history.append(change_event)

            logging.info(f"Applied configuration template: {template_name}")
            return True

        except Exception as e:
            logging.error(f"Failed to apply template: {e}")
            return False

    def get_configuration_diff(self, snapshot_id: str) -> Dict[str, Any]:
        """Get difference between current config and snapshot."""
        try:
            snapshot_file = self.config_dir / f"{snapshot_id}.json"
            if not snapshot_file.exists():
                return {"error": f"Snapshot not found: {snapshot_id}"}

            with open(snapshot_file, 'r') as f:
                snapshot_data = json.load(f)

            if "config" not in snapshot_data:
                return {"error": "Invalid snapshot format"}

            def compare_configs(current, snapshot, path=""):
                """Recursively compare configurations."""
                differences = {}

                # Check for changes and additions in current
                for key, value in current.items():
                    current_path = f"{path}.{key}" if path else key
                    if key in snapshot:
                        if isinstance(value, dict) and isinstance(snapshot[key], dict):
                            nested_diff = compare_configs(value, snapshot[key], current_path)
                            if nested_diff:
                                differences[current_path] = nested_diff
                        elif value != snapshot[key]:
                            differences[current_path] = {
                                "type": "changed",
                                "current": value,
                                "snapshot": snapshot[key]
                            }
                    else:
                        differences[current_path] = {
                            "type": "added",
                            "current": value
                        }

                # Check for removals
                for key in snapshot:
                    if key not in current:
                        current_path = f"{path}.{key}" if path else key
                        differences[current_path] = {
                            "type": "removed",
                            "snapshot": snapshot[key]
                        }

                return differences

            return compare_configs(self._config_data, snapshot_data["config"])

        except Exception as e:
            logging.error(f"Failed to get configuration diff: {e}")
            return {"error": str(e)}

    def get_feature_status(self) -> Dict[str, bool]:
        """Get status of configuration features."""
        return {
            "hot_reload": self._hot_reload_enabled,
            "inheritance": bool(self._inheritance_chain),
            "history": bool(self._change_history),
            "templates": bool(self.get_configuration_templates()),
            "migration": bool(self._migration_hooks),
            "validation": bool(self._validation_rules),
            "snapshots": bool(self._snapshots),
            "environment_support": len(self.get_environment_configs()) > 0,
            "file_watchers": len(self._file_watchers) > 0,
            "change_callbacks": len(self._change_callbacks) > 0
        }

    def initialize_default_validation_rules(self):
        """Initialize default validation rules for common configuration fields."""
        try:
            # AI configuration validation
            self.add_validation_rule(
                "ai.openai.temperature",
                "number",
                validator_args={"min_val": 0.0, "max_val": 2.0},
                required=False,
                description="OpenAI temperature must be between 0.0 and 2.0"
            )

            self.add_validation_rule(
                "ai.openai.max_tokens",
                "number",
                validator_args={"min_val": 1, "max_val": 8192},
                required=False,
                description="OpenAI max tokens must be between 1 and 8192"
            )

            # UI configuration validation
            self.add_validation_rule(
                "ui.font_size",
                "number",
                validator_args={"min_val": 8, "max_val": 72},
                required=False,
                description="Font size must be between 8 and 72"
            )

            self.add_validation_rule(
                "ui.auto_save_interval",
                "number",
                validator_args={"min_val": 10, "max_val": 3600},
                required=False,
                description="Auto-save interval must be between 10 seconds and 1 hour"
            )

            # Project configuration validation
            self.add_validation_rule(
                "project.soft_target",
                "number",
                validator_args={"min_val": 1000, "max_val": 1000000},
                required=False,
                description="Soft target must be between 1,000 and 1,000,000 words"
            )

            logging.info("Default validation rules initialized")

        except Exception as e:
            logging.error(f"Failed to initialize validation rules: {e}")

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration status."""
        try:
            validation_errors = self.validate_configuration()

            return {
                "project": self.project_name,
                "environment": self.environment.value,
                "version": CONFIG_VERSION,
                "last_modified": max([event.timestamp for event in self._change_history]) if self._change_history else None,
                "total_settings": self._count_config_items(self._config_data),
                "validation_status": "valid" if not validation_errors else "invalid",
                "validation_errors": validation_errors,
                "feature_status": self.get_feature_status(),
                "snapshots_count": len(self._snapshots),
                "history_count": len(self._change_history),
                "inheritance_chain": self._inheritance_chain,
                "available_environments": self.get_environment_configs()
            }
        except Exception as e:
            logging.error(f"Failed to get configuration summary: {e}")
            return {"error": str(e)}

    def _count_config_items(self, config_dict: Dict, count: int = 0) -> int:
        """Recursively count configuration items."""
        for key, value in config_dict.items():
            if isinstance(value, dict):
                count = self._count_config_items(value, count)
            else:
                count += 1
        return count

    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values."""
        with self._lock:
            try:
                # Create backup before reset
                backup_id = self.create_config_snapshot("Pre-reset backup")

                # Reset to defaults
                self._config_data = copy.deepcopy(self._default_config)

                # Record change
                change_event = ConfigChangeEvent(
                    timestamp=datetime.now(),
                    key="__reset__",
                    old_value=f"backup_{backup_id}",
                    new_value="defaults",
                    source="reset"
                )
                self._change_history.append(change_event)

                logging.info("Configuration reset to defaults")
                return True

            except Exception as e:
                logging.error(f"Failed to reset configuration: {e}")
                return False

class ConfigCompatibilityLayer:
    """Compatibility layer for legacy configuration access patterns."""

    def __init__(self, config_manager: ConfigManager):
        self._config = config_manager

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with legacy key format support."""
        # Try direct key first
        value = self._config.get(key, None)
        if value is not None:
            return value

        # Try with dotted notation conversion
        dotted_key = key.replace('_', '.')
        value = self._config.get(dotted_key, None)
        if value is not None:
            return value

        # Try legacy key mappings
        legacy_mappings = {
            "api_key": "ai.openai.api_key",
            "model": "ai.openai.model",
            "temperature": "ai.openai.temperature",
            "theme": "ui.theme",
            "auto_save": "ui.auto_save",
            "Idea": "project.idea",
            "Tone": "project.tone",
            "Theme": "project.theme",
            "SoftTarget": "project.soft_target",
            "ReadingLevel": "project.reading_level",
            "CharactersSeed": "project.characters_seed",
            "WorldSeed": "project.world_seed",
            "ThemesSeed": "project.themes_seed",
            "StructureSeed": "project.structure_seed",
            "CustomPrompt": "project.custom_prompt"
        }

        if key in legacy_mappings:
            return self._config.get(legacy_mappings[key], default)

        return default

    def set(self, key: str, value: Any) -> bool:
        """Set configuration value with legacy key format support."""
        # Try legacy key mappings first
        legacy_mappings = {
            "api_key": "ai.openai.api_key",
            "model": "ai.openai.model",
            "temperature": "ai.openai.temperature",
            "theme": "ui.theme",
            "auto_save": "ui.auto_save",
            "Idea": "project.idea",
            "Tone": "project.tone",
            "Theme": "project.theme",
            "SoftTarget": "project.soft_target",
            "ReadingLevel": "project.reading_level",
            "CharactersSeed": "project.characters_seed",
            "WorldSeed": "project.world_seed",
            "ThemesSeed": "project.themes_seed",
            "StructureSeed": "project.structure_seed",
            "CustomPrompt": "project.custom_prompt"
        }

        if key in legacy_mappings:
            return self._config.set(legacy_mappings[key], value)

        # Try with dotted notation conversion
        dotted_key = key.replace('_', '.')
        return self._config.set(dotted_key, value)

    def save_config(self, **kwargs) -> bool:
        """Save configuration with legacy method signature."""
        try:
            # Set all provided values
            for key, value in kwargs.items():
                self.set(key, value)

            # Save configuration
            return self._config.save_config()
        except Exception as e:
            logging.error(f"Failed to save config with legacy method: {e}")
            return False

# Global configuration manager instance
_global_config_manager = None

def get_config_manager(project_name: str = None, environment: str = "development") -> ConfigManager:
    """Get global configuration manager instance."""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager(project_name, environment)
    return _global_config_manager

def initialize_global_config(project_name: str = None, environment: str = "development") -> ConfigManager:
    """Initialize global configuration manager."""
    global _global_config_manager
    _global_config_manager = ConfigManager(project_name, environment)
    return _global_config_manager

def get_global_config() -> ConfigManager:
    """Get the global configuration manager."""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager

# Convenience functions for backward compatibility
def create_configuration_compatibility_layer():
    """Create compatibility layer for legacy configuration access."""
    config_manager = get_global_config()
    return config_manager.create_compatibility_layer()

def initialize_configuration_migration(application_instance: Any) -> Dict[str, bool]:
    """Initialize and execute configuration migration for the entire application."""
    config_manager = get_global_config()

    results = {}
    for component_name in config_manager._migration_hooks.keys():
        try:
            component_instance = getattr(application_instance, component_name, None)
            if component_instance is None:
                alt_name = component_name.replace('_', '').lower()
                component_instance = getattr(application_instance, alt_name, None)

            if component_instance is not None:
                results[component_name] = config_manager.migrate_component(component_name, component_instance)
            else:
                logging.warning(f"Component instance not found: {component_name}")
                results[component_name] = False

        except Exception as e:
            logging.error(f"Error accessing component {component_name}: {e}")
            results[component_name] = False

    return results
