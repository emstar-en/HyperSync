"""
HyperSync Provider Registry - Runtime Module

Manages cloud provider adapters for prompt routing, token accounting,
and distributed inference capabilities.
"""

from typing import Dict, Type, Optional, List
from dataclasses import dataclass
from enum import Enum

__version__ = "1.0.0"
__all__ = [
    "Provider",
    "ProviderCapability",
    "ProviderRegistry",
    "ProviderAdapter",
    "ProviderConfig",
    "ProviderStatus"
]


class ProviderCapability(Enum):
    """Capabilities that providers can expose."""
    TEXT_COMPLETION = "text_completion"
    CHAT_COMPLETION = "chat_completion"
    EMBEDDINGS = "embeddings"
    IMAGE_GENERATION = "image_generation"
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    BATCH_PROCESSING = "batch_processing"


class ProviderStatus(Enum):
    """Provider health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNAUTHORIZED = "unauthorized"
    RATE_LIMITED = "rate_limited"


@dataclass
class ProviderConfig:
    """Configuration for a provider instance."""
    provider_id: str
    adapter_class: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    capabilities: List[ProviderCapability] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Provider:
    """Runtime provider instance."""
    config: ProviderConfig
    adapter: 'ProviderAdapter'
    status: ProviderStatus = ProviderStatus.HEALTHY
    last_health_check: Optional[datetime] = None
    error_count: int = 0

    def is_available(self) -> bool:
        """Check if provider is available for requests."""
        return self.status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED]

    def supports_capability(self, capability: ProviderCapability) -> bool:
        """Check if provider supports a capability."""
        return capability in self.config.capabilities


class ProviderAdapter:
    """
    Base class for provider adapters.

    All cloud provider integrations must implement this interface.
    """

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the adapter (auth, connection pooling, etc.)."""
        raise NotImplementedError

    async def health_check(self) -> ProviderStatus:
        """Check provider health and return status."""
        raise NotImplementedError

    async def complete(self, prompt: str, **kwargs) -> Dict:
        """
        Execute a completion request.

        Returns:
            {
                "text": str,
                "tokens_used": int,
                "model": str,
                "metadata": dict
            }
        """
        raise NotImplementedError

    async def chat_complete(self, messages: List[Dict], **kwargs) -> Dict:
        """Execute a chat completion request."""
        raise NotImplementedError

    async def embed(self, texts: List[str], **kwargs) -> Dict:
        """Generate embeddings for texts."""
        raise NotImplementedError

    async def shutdown(self):
        """Clean up resources."""
        pass


class ProviderRegistry:
    """
    Central registry for managing provider instances.

    Handles registration, health checks, and provider selection.
    """

    def __init__(self):
        self._providers: Dict[str, Provider] = {}
        self._adapter_classes: Dict[str, Type[ProviderAdapter]] = {}

    def register_adapter_class(self, name: str, adapter_class: Type[ProviderAdapter]):
        """Register an adapter class for dynamic instantiation."""
        self._adapter_classes[name] = adapter_class

    async def register_provider(self, config: ProviderConfig) -> Provider:
        """
        Register a new provider instance.

        Args:
            config: Provider configuration

        Returns:
            Initialized Provider instance

        Raises:
            ValueError: If adapter class not found or initialization fails
        """
        if config.adapter_class not in self._adapter_classes:
            raise ValueError(f"Unknown adapter class: {config.adapter_class}")

        adapter_class = self._adapter_classes[config.adapter_class]
        adapter = adapter_class(config)

        # Initialize adapter
        success = await adapter.initialize()
        if not success:
            raise ValueError(f"Failed to initialize adapter: {config.provider_id}")

        # Create provider instance
        provider = Provider(
            config=config,
            adapter=adapter,
            status=ProviderStatus.HEALTHY,
            last_health_check=datetime.utcnow()
        )

        self._providers[config.provider_id] = provider
        return provider

    def get_provider(self, provider_id: str) -> Optional[Provider]:
        """Get a provider by ID."""
        return self._providers.get(provider_id)

    def list_providers(self, capability: Optional[ProviderCapability] = None) -> List[Provider]:
        """
        List all providers, optionally filtered by capability.

        Args:
            capability: Filter by capability

        Returns:
            List of matching providers
        """
        providers = list(self._providers.values())

        if capability:
            providers = [p for p in providers if p.supports_capability(capability)]

        return providers

    async def health_check_all(self) -> Dict[str, ProviderStatus]:
        """Run health checks on all providers."""
        results = {}

        for provider_id, provider in self._providers.items():
            try:
                status = await provider.adapter.health_check()
                provider.status = status
                provider.last_health_check = datetime.utcnow()
                results[provider_id] = status
            except Exception as e:
                provider.status = ProviderStatus.UNAVAILABLE
                provider.error_count += 1
                results[provider_id] = ProviderStatus.UNAVAILABLE

        return results

    def unregister_provider(self, provider_id: str):
        """Remove a provider from the registry."""
        if provider_id in self._providers:
            del self._providers[provider_id]


# Global registry instance
_global_registry = None


def get_registry() -> ProviderRegistry:
    """Get the global provider registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ProviderRegistry()
    return _global_registry
