"""
Anthropic Provider Adapter
"""

from typing import Dict, List, Optional, Any, AsyncIterator
import httpx
import json
from .base_adapter import BaseProviderAdapter


class AnthropicAdapter(BaseProviderAdapter):
    """Adapter for Anthropic API"""

    def __init__(self, provider_config: Dict, credential: str):
        super().__init__(provider_config, credential)
        self.base_url = self.endpoint.get("base_url", "https://api.anthropic.com/v1")
        self.api_version = self.endpoint.get("api_version", "2023-06-01")
        self.headers = {
            "x-api-key": credential,
            "anthropic-version": self.api_version,
            "Content-Type": "application/json"
        }

    async def chat_completion(
        self,
        model: str,
        messages: List[Dict],
        max_tokens: int = 1024,
        temperature: float = 1.0,
        **kwargs
    ) -> Dict:
        """Generate chat completion"""
        async with httpx.AsyncClient() as client:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            payload.update(kwargs)

            try:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload,
                    timeout=self.retry_config.get("timeout_seconds", 60)
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return self._handle_error(e)

    async def completion(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict:
        """Generate text completion (via messages API)"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(model, messages, max_tokens, **kwargs)

    async def embedding(
        self,
        model: str,
        input_text: str | List[str],
        **kwargs
    ) -> Dict:
        """Anthropic doesn't provide embeddings"""
        return {
            "error": {
                "type": "NotSupported",
                "message": "Anthropic does not provide embedding models"
            }
        }

    async def list_models(self) -> List[Dict]:
        """List available models (hardcoded for Anthropic)"""
        return [
            {"id": "claude-3-opus-20240229", "type": "chat"},
            {"id": "claude-3-sonnet-20240229", "type": "chat"},
            {"id": "claude-3-haiku-20240307", "type": "chat"},
            {"id": "claude-2.1", "type": "chat"},
            {"id": "claude-2.0", "type": "chat"}
        ]

    async def health_check(self) -> Dict:
        """Check provider health"""
        try:
            # Simple test message
            result = await self.chat_completion(
                "claude-3-haiku-20240307",
                [{"role": "user", "content": "Hi"}],
                max_tokens=10
            )

            if "error" in result:
                return {
                    "status": "unhealthy",
                    "error": result["error"],
                    "provider": "anthropic"
                }

            return {
                "status": "healthy",
                "provider": "anthropic"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": "anthropic"
            }
