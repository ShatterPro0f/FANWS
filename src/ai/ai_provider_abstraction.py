#!/usr/bin/env python3
"""
AI Provider Abstraction Layer
Provides unified interface for multiple AI providers.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    XAI = "xai"
    LOCAL = "local"

class ProviderConfig:
    """Configuration for an AI provider."""

    def __init__(self, provider: AIProvider, api_key: str = "",
                 endpoint: str = "", model: str = "", **kwargs):
        self.provider = provider
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model
        self.extra_config = kwargs
        self.enabled = bool(api_key)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider.value,
            "api_key": self.api_key,
            "endpoint": self.endpoint,
            "model": self.model,
            "enabled": self.enabled,
            **self.extra_config
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProviderConfig':
        """Create from dictionary."""
        provider = AIProvider(data.get("provider", "openai"))
        return cls(
            provider=provider,
            api_key=data.get("api_key", ""),
            endpoint=data.get("endpoint", ""),
            model=data.get("model", ""),
            **{k: v for k, v in data.items()
               if k not in ["provider", "api_key", "endpoint", "model", "enabled"]}
        )

class MultiProviderConfig:
    """Configuration for multiple AI providers."""

    def __init__(self):
        self.providers: Dict[str, ProviderConfig] = {}
        self.default_provider = AIProvider.OPENAI
        self.fallback_chain: List[AIProvider] = [AIProvider.OPENAI]

    def add_provider(self, name: str, config: ProviderConfig):
        """Add a provider configuration."""
        self.providers[name] = config

    def get_provider(self, name: str) -> Optional[ProviderConfig]:
        """Get provider configuration."""
        return self.providers.get(name)

    def set_default(self, provider: AIProvider):
        """Set default provider."""
        self.default_provider = provider

    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled providers."""
        return [name for name, config in self.providers.items() if config.enabled]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "providers": {name: config.to_dict() for name, config in self.providers.items()},
            "default_provider": self.default_provider.value,
            "fallback_chain": [p.value for p in self.fallback_chain]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MultiProviderConfig':
        """Create from dictionary."""
        config = cls()

        for name, provider_data in data.get("providers", {}).items():
            config.add_provider(name, ProviderConfig.from_dict(provider_data))

        config.default_provider = AIProvider(data.get("default_provider", "openai"))
        config.fallback_chain = [AIProvider(p) for p in data.get("fallback_chain", ["openai"])]

        return config

class AIProviderManager:
    """Manages multiple AI providers."""

    def __init__(self, config: MultiProviderConfig):
        self.config = config
        self.current_provider = config.default_provider

    def switch_provider(self, provider: AIProvider):
        """Switch to a different provider."""
        self.current_provider = provider
        logging.info(f"Switched to AI provider: {provider.value}")

    def get_current_config(self) -> Optional[ProviderConfig]:
        """Get current provider configuration."""
        for config in self.config.providers.values():
            if config.provider == self.current_provider:
                return config
        return None

    def is_provider_available(self, provider: AIProvider) -> bool:
        """Check if provider is available and configured."""
        for config in self.config.providers.values():
            if config.provider == provider and config.enabled:
                return True
        return False

def initialize_multi_provider_ai() -> MultiProviderConfig:
    """Initialize multi-provider AI configuration."""
    config = MultiProviderConfig()

    # Add default OpenAI configuration
    openai_config = ProviderConfig(
        provider=AIProvider.OPENAI,
        model="gpt-4",
        endpoint="https://api.openai.com/v1/chat/completions"
    )
    config.add_provider("openai", openai_config)

    # Add other providers as needed
    xai_config = ProviderConfig(
        provider=AIProvider.XAI,
        model="grok-3",
        endpoint="https://api.x.ai/v1/chat/completions"
    )
    config.add_provider("xai", xai_config)

    logging.info("Multi-provider AI system initialized")
    return config

def get_memory_integration(provider_config: ProviderConfig) -> Dict[str, Any]:
    """Get memory integration settings for provider."""
    return {
        "provider": provider_config.provider.value,
        "supports_context": True,
        "max_context_length": 32000 if provider_config.provider == AIProvider.OPENAI else 8000,
        "memory_management": "automatic"
    }

__all__ = [
    'AIProvider', 'ProviderConfig', 'MultiProviderConfig', 'AIProviderManager',
    'initialize_multi_provider_ai', 'get_memory_integration'
]
