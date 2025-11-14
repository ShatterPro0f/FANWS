"""
Global Configuration Manager for FANWS
Handles global settings that should NOT be saved per-project, such as:
- API keys (OpenAI, Anthropic, etc.)
- Ollama server URLs
- User preferences
- Application-wide settings
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Global config location (in user's home directory, NOT in project folders)
GLOBAL_CONFIG_DIR = Path.home() / ".fanws"
GLOBAL_CONFIG_FILE = GLOBAL_CONFIG_DIR / "global_config.json"
API_KEYS_FILE = GLOBAL_CONFIG_DIR / "api_keys.json"


class GlobalConfigManager:
    """Manages global configuration separate from per-project settings"""
    
    def __init__(self):
        self.config_dir = GLOBAL_CONFIG_DIR
        self.config_file = GLOBAL_CONFIG_FILE
        self.api_keys_file = API_KEYS_FILE
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Set restrictive permissions on config directory (700 = rwx------)
        try:
            os.chmod(self.config_dir, 0o700)
        except Exception as e:
            logging.warning(f"Could not set permissions on config directory: {e}")
        
        # Load or initialize configuration
        self.config = self._load_config()
        self.api_keys = self._load_api_keys()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load global configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading global config: {e}")
                return self._default_config()
        else:
            # Create default config
            config = self._default_config()
            self._save_config(config)
            return config
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default global configuration"""
        return {
            'version': '1.0',
            'user_preferences': {
                'default_ai_provider': 'openai',  # 'openai', 'ollama', etc.
                'ollama_url': 'http://localhost:11434',
                'ollama_default_model': 'llama2',
                'theme': 'dark',
                'auto_save_interval': 300,  # seconds
                'backup_enabled': True,
                'check_updates': True
            },
            'application_settings': {
                'last_opened_project': None,
                'recent_projects': [],
                'max_recent_projects': 10,
                'default_project_location': str(Path.home() / "Documents" / "FANWS_Projects"),
                'log_level': 'INFO',
                'crash_reports': True
            },
            'ai_defaults': {
                'temperature': 0.7,
                'max_tokens': 2000,
                'timeout': 300,
                'retry_attempts': 3,
                'cache_enabled': True
            },
            'workflow_defaults': {
                'target_word_count': 200000,
                'chapters': 25,
                'sections_per_chapter': 5,
                'auto_approve': False
            }
        }
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save global configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error saving global config: {e}")
            return False
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from secure location"""
        if self.api_keys_file.exists():
            try:
                # Set restrictive permissions on API keys file (600 = rw-------)
                os.chmod(self.api_keys_file, 0o600)
                
                with open(self.api_keys_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading API keys: {e}")
                return {}
        else:
            return {}
    
    def _save_api_keys(self) -> bool:
        """Save API keys to secure location"""
        try:
            with open(self.api_keys_file, 'w') as f:
                json.dump(self.api_keys, f, indent=2)
            
            # Set restrictive permissions (600 = rw-------)
            os.chmod(self.api_keys_file, 0o600)
            return True
        except Exception as e:
            logging.error(f"Error saving API keys: {e}")
            return False
    
    # Public API methods
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation path.
        Example: get('user_preferences.theme')
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        Set configuration value by dot-notation path.
        Example: set('user_preferences.theme', 'light')
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent dict
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        
        return self._save_config(self.config)
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider"""
        return self.api_keys.get(provider)
    
    def set_api_key(self, provider: str, api_key: str) -> bool:
        """Set API key for a specific provider"""
        self.api_keys[provider] = api_key
        return self._save_api_keys()
    
    def remove_api_key(self, provider: str) -> bool:
        """Remove API key for a specific provider"""
        if provider in self.api_keys:
            del self.api_keys[provider]
            return self._save_api_keys()
        return True
    
    def list_api_providers(self) -> list:
        """List all providers with API keys configured"""
        return list(self.api_keys.keys())
    
    def get_ollama_url(self) -> str:
        """Get Ollama server URL"""
        return self.get('user_preferences.ollama_url', 'http://localhost:11434')
    
    def set_ollama_url(self, url: str) -> bool:
        """Set Ollama server URL"""
        return self.set('user_preferences.ollama_url', url)
    
    def get_default_ai_provider(self) -> str:
        """Get default AI provider"""
        return self.get('user_preferences.default_ai_provider', 'openai')
    
    def set_default_ai_provider(self, provider: str) -> bool:
        """Set default AI provider"""
        return self.set('user_preferences.default_ai_provider', provider)
    
    def add_recent_project(self, project_path: str) -> bool:
        """Add project to recent projects list"""
        recent = self.get('application_settings.recent_projects', [])
        max_recent = self.get('application_settings.max_recent_projects', 10)
        
        # Remove if already exists
        if project_path in recent:
            recent.remove(project_path)
        
        # Add to front
        recent.insert(0, project_path)
        
        # Trim to max
        recent = recent[:max_recent]
        
        return self.set('application_settings.recent_projects', recent)
    
    def get_recent_projects(self) -> list:
        """Get list of recent projects"""
        return self.get('application_settings.recent_projects', [])
    
    def export_config(self, filepath: str, include_api_keys: bool = False) -> bool:
        """Export configuration to file"""
        try:
            export_data = {
                'config': self.config,
            }
            
            if include_api_keys:
                export_data['api_keys'] = self.api_keys
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
        except Exception as e:
            logging.error(f"Error exporting config: {e}")
            return False
    
    def import_config(self, filepath: str) -> bool:
        """Import configuration from file"""
        try:
            with open(filepath, 'r') as f:
                import_data = json.load(f)
            
            if 'config' in import_data:
                self.config = import_data['config']
                self._save_config(self.config)
            
            if 'api_keys' in import_data:
                self.api_keys = import_data['api_keys']
                self._save_api_keys()
            
            return True
        except Exception as e:
            logging.error(f"Error importing config: {e}")
            return False


# Global instance
_global_config = None


def get_global_config() -> GlobalConfigManager:
    """Get the global configuration manager instance"""
    global _global_config
    if _global_config is None:
        _global_config = GlobalConfigManager()
    return _global_config


# Convenience functions

def get_api_key(provider: str) -> Optional[str]:
    """Get API key for provider"""
    return get_global_config().get_api_key(provider)


def set_api_key(provider: str, api_key: str) -> bool:
    """Set API key for provider"""
    return get_global_config().set_api_key(provider, api_key)


def get_ollama_url() -> str:
    """Get Ollama server URL"""
    return get_global_config().get_ollama_url()


def set_ollama_url(url: str) -> bool:
    """Set Ollama server URL"""
    return get_global_config().set_ollama_url(url)


def get_default_ai_provider() -> str:
    """Get default AI provider"""
    return get_global_config().get_default_ai_provider()


def set_default_ai_provider(provider: str) -> bool:
    """Set default AI provider"""
    return get_global_config().set_default_ai_provider(provider)
