"""
Configuration module for FANWS
Manages both global and per-project configurations
"""

from .global_config import (
    GlobalConfigManager,
    get_global_config,
    get_api_key,
    set_api_key,
    get_ollama_url,
    set_ollama_url,
    get_default_ai_provider,
    set_default_ai_provider
)

__all__ = [
    'GlobalConfigManager',
    'get_global_config',
    'get_api_key',
    'set_api_key',
    'get_ollama_url',
    'set_ollama_url',
    'get_default_ai_provider',
    'set_default_ai_provider'
]
