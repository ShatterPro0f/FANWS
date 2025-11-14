"""
Settings Manager for AAWT
Handles persistent configuration with dot-notation access and JSON storage.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from threading import Lock

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manages application settings with persistent JSON storage."""
    
    def __init__(self, settings_path: str = "config/user_settings.json"):
        """
        Initialize settings manager.
        
        Args:
            settings_path: Path to settings JSON file
        """
        self.settings_path = Path(settings_path)
        self._settings = {}
        self._lock = Lock()
        self._defaults = self._get_default_settings()
        
        # Ensure settings directory exists
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load settings
        self.load()
        
        logger.info(f"Settings manager initialized: {settings_path}")
    
    def _get_default_settings(self) -> Dict:
        """Get default settings structure."""
        return {
            'ui': {
                'theme': 'light',
                'primary_color': '#2196F3',
                'secondary_color': '#FFC107',
                'text_color': '#000000',
                'background_color': '#FFFFFF',
                'font_family': 'Arial',
                'font_size': 11,
                'window': {
                    'width': 1280,
                    'height': 800,
                    'maximized': False
                },
                'sidebar_width': 200,
                'show_status_bar': True,
                'show_toolbar': True,
                'animations_enabled': True
            },
            'writing': {
                'default_tone': 'Professional',
                'default_pov': 'Third Limited',
                'default_genre': 'Fiction',
                'default_target_audience': 'General',
                'enable_spell_check': True,
                'enable_grammar_check': True,
                'highlight_repeated_words': True,
                'show_readability_score': True,
                'auto_save_interval': 60,
                'highlight_long_sentences': True,
                'daily_word_goal': 1000,
                'session_word_goal': 500
            },
            'api': {
                'openai_key': '',
                'anthropic_key': '',
                'google_key': '',
                'huggingface_key': '',
                'ollama_url': 'http://localhost:11434',
                'words_api_key': '',
                'apyhub_key': '',
                'default_model': 'gpt-3.5-turbo',
                'default_provider': 'openai',
                'request_timeout': 30,
                'max_retries': 3,
                'enable_api_caching': True,
                'cache_expiration_days': 7,
                'rate_limit_requests': 60,
                'rate_limit_window': 3600,
                'enable_rate_limiting': True
            },
            'export': {
                'default_format': 'docx',
                'default_export_dir': 'exports',
                'include_metadata': True,
                'include_statistics': True,
                'compress_output': False,
                'formats_enabled': {
                    'txt': True,
                    'md': True,
                    'docx': True,
                    'pdf': True,
                    'epub': True,
                    'json': True
                }
            },
            'performance': {
                'cache_size_mb': 100,
                'analytics_update_interval': 2,
                'database_optimization_frequency': 7,
                'connection_pool_size': 5,
                'query_timeout_ms': 5000
            },
            'advanced': {
                'debug_mode': False,
                'logging_level': 'INFO',
                'enable_query_cache': True,
                'enable_connection_pooling': True,
                'database_path': 'config/aawt.db'
            }
        }
    
    def load(self) -> bool:
        """Load settings from file."""
        try:
            if self.settings_path.exists():
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    
                # Merge with defaults (in case new settings were added)
                self._settings = self._merge_dicts(self._defaults.copy(), loaded)
                logger.info("Settings loaded successfully")
            else:
                # Use defaults
                self._settings = self._defaults.copy()
                self.save()  # Save defaults to file
                logger.info("Created default settings file")
            
            return True
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            self._settings = self._defaults.copy()
            return False
    
    def save(self) -> bool:
        """Save settings to file."""
        try:
            with self._lock:
                # Create backup
                if self.settings_path.exists():
                    backup_path = self.settings_path.with_suffix('.json.bak')
                    self.settings_path.rename(backup_path)
                
                # Write settings
                with open(self.settings_path, 'w', encoding='utf-8') as f:
                    json.dump(self._settings, f, indent=2, ensure_ascii=False)
                
                # Remove backup if successful
                backup_path = self.settings_path.with_suffix('.json.bak')
                if backup_path.exists():
                    backup_path.unlink()
                
                logger.debug("Settings saved successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            # Restore backup if it exists
            backup_path = self.settings_path.with_suffix('.json.bak')
            if backup_path.exists():
                backup_path.rename(self.settings_path)
            return False
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get setting value using dot notation.
        
        Args:
            path: Dot-separated path (e.g., 'ui.theme')
            default: Default value if not found
        
        Returns:
            Setting value or default
        """
        try:
            parts = path.split('.')
            value = self._settings
            
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            
            return value
        except Exception as e:
            logger.error(f"Failed to get setting '{path}': {e}")
            return default
    
    def set(self, path: str, value: Any, auto_save: bool = True) -> bool:
        """
        Set setting value using dot notation.
        
        Args:
            path: Dot-separated path (e.g., 'ui.theme')
            value: Value to set
            auto_save: Whether to automatically save to file
        
        Returns:
            True if successful
        """
        try:
            with self._lock:
                parts = path.split('.')
                current = self._settings
                
                # Navigate to parent
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Set value
                current[parts[-1]] = value
                
                if auto_save:
                    return self.save()
                
                return True
        except Exception as e:
            logger.error(f"Failed to set setting '{path}': {e}")
            return False
    
    def get_section(self, section: str) -> Dict:
        """
        Get entire section of settings.
        
        Args:
            section: Section name (e.g., 'ui', 'api')
        
        Returns:
            Dictionary of section settings
        """
        return self.get(section, {})
    
    def set_section(self, section: str, values: Dict, auto_save: bool = True) -> bool:
        """
        Set entire section of settings.
        
        Args:
            section: Section name
            values: Dictionary of settings
            auto_save: Whether to automatically save to file
        
        Returns:
            True if successful
        """
        return self.set(section, values, auto_save)
    
    def reset_to_defaults(self, section: Optional[str] = None) -> bool:
        """
        Reset settings to defaults.
        
        Args:
            section: Optional section to reset (None = reset all)
        
        Returns:
            True if successful
        """
        try:
            with self._lock:
                if section:
                    if section in self._defaults:
                        self._settings[section] = self._defaults[section].copy()
                else:
                    self._settings = self._defaults.copy()
                
                return self.save()
        except Exception as e:
            logger.error(f"Failed to reset settings: {e}")
            return False
    
    def _merge_dicts(self, base: Dict, override: Dict) -> Dict:
        """Recursively merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def export_settings(self, export_path: str) -> bool:
        """Export settings to a file."""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Settings exported to {export_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, import_path: str) -> bool:
        """Import settings from a file."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            self._settings = self._merge_dicts(self._defaults.copy(), imported)
            self.save()
            logger.info(f"Settings imported from {import_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return False
    
    def get_all(self) -> Dict:
        """Get all settings."""
        return self._settings.copy()
