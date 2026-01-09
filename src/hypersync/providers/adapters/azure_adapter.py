"""
Azure OpenAI Provider Adapter
"""

from typing import Dict, List, Optional, Any
import httpx
from .base_adapter import BaseProviderAdapter


class AzureOpenAIAdapter(BaseProviderAdapter):
    """Adapter for Azure OpenAI API"""

    def __init__(self, provider_config: Dict, credential: str):
        super().__init__(provider_config, credential)
        self.base_url = self.endpoint.get("base_url")  # e.g., https://your-resource.openai.azure.com
        self.api_version = self.endpoint.get("api_version", "2023-05-15")
        self.deployment_name = self.endpoint.get("deployment_name")
        self.headers = {
            "api-key": credential,
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
        deployment = self.deployment_name or model

        async with httpx.AsyncClient() as client:
            payload = {
                "messages": messages,
                "temperature": temperature
            }

            if max_tokens:
                payload["max_tokens"] = max_tokens

            payload.update(kwargs)

            try:
                response = await client.post(
                    f"{self.base_url}/openai/deployments/{deployment}/chat/completions?api-version={self.api_version}",
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
        deployment = self.deployment_name or model

        async with httpx.AsyncClient() as client:
            payload = {
                "prompt": prompt,
                "temperature": temperature
            }

            if max_tokens:
                payload["max_tokens"] = max_tokens

            payload.update(kwargs)

            try:
                response = await client.post(
                    f"{self.base_url}/openai/deployments/{deployment}/completions?api-version={self.api_version}",
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
        deployment = self.deployment_name or model

        async with httpx.AsyncClient() as client:
            payload = {
                "input": input_text
            }
            payload.update(kwargs)

            try:
                response = await client.post(
                    f"{self.base_url}/openai/deployments/{deployment}/embeddings?api-version={self.api_version}",
                    headers=self.headers,
                    json=payload,
                    timeout=self.retry_config.get("timeout_seconds", 60)
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return self._handle_error(e)

    async def list_models(self) -> List[Dict]:
        """List available deployments"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/openai/deployments?api-version={self.api_version}",
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
                "deployments_available": len(models),
                "provider": "azure_openai"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": "azure_openai"
            }
