"""
Adapter Factory

Centralized factory for creating and configuring provider adapters.
"""

from typing import Dict, Optional, Type
from hypersync.providers import ProviderAdapter, ProviderConfig
from hypersync.providers.adapters import get_adapter_class


class AdapterFactory:
    """
    Factory for creating provider adapter instances.

    Handles adapter instantiation, configuration validation,
    and default parameter injection.
    """

    # Default configurations for known providers
    DEFAULTS = {
        "chatllm": {
            "api_base": "https://api.abacus.ai/v1",
            "timeout": 30,
            "max_retries": 3
        },
        "openai": {
            "api_base": "https://api.openai.com/v1",
            "timeout": 30,
            "max_retries": 3
        },
        "anthropic": {
            "api_base": "https://api.anthropic.com/v1",
            "timeout": 30,
            "max_retries": 3
        }
    }

    @classmethod
    def create(cls, adapter_name: str, config: ProviderConfig) -> ProviderAdapter:
        """
        Create an adapter instance.

        Args:
            adapter_name: Name of the adapter (e.g., 'chatllm')
            config: Provider configuration

        Returns:
            Initialized adapter instance

        Raises:
            ValueError: If adapter not found or config invalid
        """
        # Get adapter class
        adapter_class = get_adapter_class(adapter_name)

        # Apply defaults
        if adapter_name in cls.DEFAULTS:
            defaults = cls.DEFAULTS[adapter_name]
            for key, value in defaults.items():
                if not hasattr(config, key) or getattr(config, key) is None:
                    setattr(config, key, value)

        # Validate required fields
        cls._validate_config(adapter_name, config)

        # Create instance
        return adapter_class(config)

    @classmethod
    def _validate_config(cls, adapter_name: str, config: ProviderConfig):
        """Validate adapter configuration."""
        # All adapters require an API key
        if not config.api_key:
            raise ValueError(f"{adapter_name} adapter requires api_key")

        # Provider-specific validation
        if adapter_name == "chatllm":
            if not config.api_base:
                config.api_base = cls.DEFAULTS["chatllm"]["api_base"]

    @classmethod
    def create_from_dict(cls, adapter_name: str, config_dict: Dict) -> ProviderAdapter:
        """
        Create adapter from dictionary configuration.

        Args:
            adapter_name: Name of the adapter
            config_dict: Configuration dictionary

        Returns:
            Initialized adapter instance
        """
        config = ProviderConfig(
            provider_id=config_dict.get("provider_id", adapter_name),
            adapter_class=adapter_name,
            api_key=config_dict.get("api_key"),
            api_base=config_dict.get("api_base"),
            timeout=config_dict.get("timeout", 30),
            max_retries=config_dict.get("max_retries", 3),
            capabilities=config_dict.get("capabilities"),
            metadata=config_dict.get("metadata", {})
        )

        return cls.create(adapter_name, config)
