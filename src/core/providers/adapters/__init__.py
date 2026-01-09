"""
Provider Adapters

Concrete implementations for various cloud providers.
"""

from typing import Dict, Type
from hypersync.providers import ProviderAdapter

__all__ = ["get_adapter_class", "list_adapters"]

# Adapter registry
_ADAPTERS: Dict[str, Type[ProviderAdapter]] = {}


def register_adapter(name: str, adapter_class: Type[ProviderAdapter]):
    """Register an adapter class."""
    _ADAPTERS[name] = adapter_class


def get_adapter_class(name: str) -> Type[ProviderAdapter]:
    """Get an adapter class by name."""
    if name not in _ADAPTERS:
        raise ValueError(f"Unknown adapter: {name}")
    return _ADAPTERS[name]


def list_adapters() -> Dict[str, Type[ProviderAdapter]]:
    """List all registered adapters."""
    return _ADAPTERS.copy()


# Auto-register adapters
try:
    from .chatllm_adapter import ChatLLMAdapter
    register_adapter("chatllm", ChatLLMAdapter)
except ImportError:
    pass

try:
    from .openai_adapter import OpenAIAdapter
    register_adapter("openai", OpenAIAdapter)
except ImportError:
    pass

try:
    from .anthropic_adapter import AnthropicAdapter
    register_adapter("anthropic", AnthropicAdapter)
except ImportError:
    pass
