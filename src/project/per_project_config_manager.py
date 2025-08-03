#!/usr/bin/env python3
"""
Per-Project Configuration Manager
Manages project-specific configuration settings and isolation.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class PerProjectConfigManager:
    """Manages configuration for individual projects."""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_dir = os.path.join("projects", project_name)
        self.config_file = os.path.join(self.project_dir, "project_config.json")
        self.config = {}

    def initialize_project_config(self):
        """Initialize project configuration."""
        try:
            os.makedirs(self.project_dir, exist_ok=True)

            if os.path.exists(self.config_file):
                self.load_config()
            else:
                self.create_default_config()
                self.save_config()

            logging.info(f"Project configuration initialized for {self.project_name}")

        except Exception as e:
            logging.error(f"Failed to initialize project config: {str(e)}")
            raise

    def create_default_config(self):
        """Create default project configuration."""
        self.config = {
            "project_name": self.project_name,
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "version": "1.0",
            "settings": {
                "auto_save": True,
                "backup_interval": 300,
                "quality_checks": True,
                "analytics_enabled": True
            },
            "ai_settings": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "workflow_settings": {
                "auto_approve": False,
                "chapter_length": 2500,
                "quality_threshold": 0.7
            }
        }

    def load_config(self):
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load project config: {str(e)}")
            self.create_default_config()

    def save_config(self):
        """Save configuration to file."""
        try:
            self.config["last_modified"] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save project config: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
        self.save_config()

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings."""
        return self.config.copy()

    def get_project_file_path(self, filename: str) -> str:
        """Get project-specific file path."""
        # Create the appropriate subdirectory structure
        if filename in ["config.txt", "synonyms_cache.txt", "wordsapi_log.txt", "context.txt", "plot_points.txt", "continuity_rules.txt"]:
            config_dir = os.path.join(self.project_dir, "config")
            os.makedirs(config_dir, exist_ok=True)
            return os.path.join(config_dir, filename)
        elif filename.startswith("drafts/"):
            drafts_dir = os.path.join(self.project_dir, "drafts")
            os.makedirs(drafts_dir, exist_ok=True)
            return os.path.join(self.project_dir, filename)
        elif filename.startswith("backups/"):
            backups_dir = os.path.join(self.project_dir, "backups")
            os.makedirs(backups_dir, exist_ok=True)
            return os.path.join(self.project_dir, filename)
        else:
            return os.path.join(self.project_dir, filename)

def migrate_all_projects_to_isolation():
    """Migrate existing projects to use per-project configuration."""
    try:
        projects_dir = "projects"
        if not os.path.exists(projects_dir):
            return

        for project_name in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_name)
            if os.path.isdir(project_path):
                try:
                    config_manager = PerProjectConfigManager(project_name)
                    config_manager.initialize_project_config()
                    logging.info(f"Migrated project: {project_name}")
                except Exception as e:
                    logging.error(f"Failed to migrate project {project_name}: {str(e)}")

    except Exception as e:
        logging.error(f"Failed to migrate projects: {str(e)}")

__all__ = ['PerProjectConfigManager', 'migrate_all_projects_to_isolation']
