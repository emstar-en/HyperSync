"""
Base Provider Adapter

Abstract base class for all provider adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
import logging

logger = logging.getLogger(__name__)


class BaseProviderAdapter(ABC):
    """Base class for provider adapters"""

    def __init__(self, provider_config: Dict, credential: str):
        self.provider_config = provider_config
        self.credential = credential
        self.provider_type = provider_config.get("provider_type")
        self.endpoint = provider_config.get("endpoint", {})
        self.rate_limits = provider_config.get("rate_limits", {})
        self.retry_config = provider_config.get("retry_config", {})

    @abstractmethod
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict],
        **kwargs
    ) -> Dict:
        """Generate chat completion"""
        pass

    @abstractmethod
    async def completion(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> Dict:
        """Generate text completion"""
        pass

    @abstractmethod
    async def embedding(
        self,
        model: str,
        input_text: str | List[str],
        **kwargs
    ) -> Dict:
        """Generate embeddings"""
        pass

    @abstractmethod
    async def list_models(self) -> List[Dict]:
        """List available models"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict:
        """Check provider health"""
        pass

    async def stream_chat_completion(
        self,
        model: str,
        messages: List[Dict],
        **kwargs
    ) -> AsyncIterator[Dict]:
        """Stream chat completion (optional)"""
        raise NotImplementedError("Streaming not supported by this provider")

    def _apply_rate_limits(self):
        """Apply rate limiting"""
        # Implement rate limiting logic
        pass

    def _handle_error(self, error: Exception) -> Dict:
        """Handle and format errors"""
        return {
            "error": {
                "type": type(error).__name__,
                "message": str(error)
            }
        }
