"""
OpenAI Provider Adapter
"""

from typing import Dict, List, Optional, Any, AsyncIterator
import httpx
import json
from .base_adapter import BaseProviderAdapter


class OpenAIAdapter(BaseProviderAdapter):
    """Adapter for OpenAI API"""

    def __init__(self, provider_config: Dict, credential: str):
        super().__init__(provider_config, credential)
        self.base_url = self.endpoint.get("base_url", "https://api.openai.com/v1")
        self.headers = {
            "Authorization": f"Bearer {credential}",
            "Content-Type": "application/json"
        }

    async def chat_completion(
        self,
        model: str,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict:
        """Generate chat completion"""
        async with httpx.AsyncClient() as client:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }

            if max_tokens:
                payload["max_tokens"] = max_tokens

            payload.update(kwargs)

            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
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
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict:
        """Generate text completion"""
        async with httpx.AsyncClient() as client:
            payload = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature
            }

            if max_tokens:
                payload["max_tokens"] = max_tokens

            payload.update(kwargs)

            try:
                response = await client.post(
                    f"{self.base_url}/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=self.retry_config.get("timeout_seconds", 60)
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return self._handle_error(e)

    async def embedding(
        self,
        model: str,
        input_text: str | List[str],
        **kwargs
    ) -> Dict:
        """Generate embeddings"""
        async with httpx.AsyncClient() as client:
            payload = {
                "model": model,
                "input": input_text
            }
            payload.update(kwargs)

            try:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=self.headers,
                    json=payload,
                    timeout=self.retry_config.get("timeout_seconds", 60)
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return self._handle_error(e)

    async def list_models(self) -> List[Dict]:
        """List available models"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                return data.get("data", [])
            except Exception as e:
                return []

    async def health_check(self) -> Dict:
        """Check provider health"""
        try:
            models = await self.list_models()
            return {
                "status": "healthy",
                "models_available": len(models),
                "provider": "openai"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": "openai"
            }

    async def stream_chat_completion(
        self,
        model: str,
        messages: List[Dict],
        **kwargs
    ) -> AsyncIterator[Dict]:
        """Stream chat completion"""
        async with httpx.AsyncClient() as client:
            payload = {
                "model": model,
                "messages": messages,
                "stream": True
            }
            payload.update(kwargs)

            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.retry_config.get("timeout_seconds", 60)
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            continue
