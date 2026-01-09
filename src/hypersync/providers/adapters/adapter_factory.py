"""
Adapter Factory

Creates appropriate adapter based on provider type.
"""

from typing import Dict
from .base_adapter import BaseProviderAdapter
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .azure_adapter import AzureOpenAIAdapter


class AdapterFactory:
    """Factory for creating provider adapters"""

    ADAPTERS = {
        "openai": OpenAIAdapter,
        "anthropic": Anthropic Adapter,
        "azure": AzureOpenAIAdapter,
    }

    @classmethod
    def create_adapter(
        cls,
        provider_config: Dict,
        credential: str
    ) -> BaseProviderAdapter:
        """Create an adapter for the given provider"""
        provider_type = provider_config.get("provider_type")

        adapter_class = cls.ADAPTERS.get(provider_type)
        if not adapter_class:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        return adapter_class(provider_config, credential)

    @classmethod
    def register_adapter(cls, provider_type: str, adapter_class):
        """Register a custom adapter"""
        cls.ADAPTERS[provider_type] = adapter_class
