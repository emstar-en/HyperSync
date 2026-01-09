"""
ChatLLM Provider Adapter

Integrates Abacus.AI ChatLLM Teams API with HyperSync provider framework.
Supports text completion, chat completion, and streaming.
"""

import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from hypersync.providers import (
    ProviderAdapter,
    ProviderConfig,
    ProviderStatus,
    ProviderCapability
)


class ChatLLMAdapter(ProviderAdapter):
    """
    Adapter for Abacus.AI ChatLLM Teams API.

    Features:
    - Text and chat completions
    - Streaming support
    - Token accounting
    - Automatic retries with exponential backoff
    - Health monitoring
    """

    DEFAULT_API_BASE = "https://api.abacus.ai/v1"
    DEFAULT_MODEL = "claude-sonnet-4.5"

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_base = config.api_base or self.DEFAULT_API_BASE
        self.api_key = config.api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_count = 0
        self._error_count = 0
        self._total_tokens = 0

        # Set default capabilities
        if not config.capabilities:
            config.capabilities = [
                ProviderCapability.TEXT_COMPLETION,
                ProviderCapability.CHAT_COMPLETION,
                ProviderCapability.STREAMING,
                ProviderCapability.FUNCTION_CALLING
            ]

    async def initialize(self) -> bool:
        """Initialize HTTP session and validate credentials."""
        try:
            # Create session with timeout
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "HyperSync/1.0"
                }
            )

            # Validate credentials with a simple health check
            status = await self.health_check()
            self._initialized = (status == ProviderStatus.HEALTHY)

            return self._initialized

        except Exception as e:
            print(f"ChatLLM adapter initialization failed: {e}")
            return False

    async def health_check(self) -> ProviderStatus:
        """Check ChatLLM API health."""
        if not self.session:
            return ProviderStatus.UNAVAILABLE

        try:
            # Simple ping to models endpoint
            url = f"{self.api_base}/models"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return ProviderStatus.HEALTHY
                elif response.status == 401:
                    return ProviderStatus.UNAUTHORIZED
                elif response.status == 429:
                    return ProviderStatus.RATE_LIMITED
                else:
                    return ProviderStatus.DEGRADED

        except asyncio.TimeoutError:
            return ProviderStatus.DEGRADED
        except Exception as e:
            print(f"Health check failed: {e}")
            return ProviderStatus.UNAVAILABLE

    async def complete(self, prompt: str, **kwargs) -> Dict:
        """
        Execute a text completion request.

        Args:
            prompt: Input text prompt
            **kwargs: Additional parameters (model, temperature, max_tokens, etc.)

        Returns:
            {
                "text": str,
                "tokens_used": int,
                "model": str,
                "metadata": dict
            }
        """
        # Convert to chat format (ChatLLM uses chat API)
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_complete(messages, **kwargs)

    async def chat_complete(self, messages: List[Dict], **kwargs) -> Dict:
        """
        Execute a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters

        Returns:
            Completion result with text, tokens, and metadata
        """
        if not self._initialized:
            raise RuntimeError("Adapter not initialized")

        model = kwargs.get("model", self.DEFAULT_MODEL)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)
        stream = kwargs.get("stream", False)

        url = f"{self.api_base}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        # Add optional parameters
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        if "frequency_penalty" in kwargs:
            payload["frequency_penalty"] = kwargs["frequency_penalty"]
        if "presence_penalty" in kwargs:
            payload["presence_penalty"] = kwargs["presence_penalty"]

        # Execute with retries
        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()

                async with self.session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()

                        # Extract response
                        text = result["choices"][0]["message"]["content"]
                        tokens_used = result.get("usage", {}).get("total_tokens", 0)

                        # Update stats
                        self._request_count += 1
                        self._total_tokens += tokens_used

                        return {
                            "text": text,
                            "tokens_used": tokens_used,
                            "model": model,
                            "metadata": {
                                "provider": "chatllm",
                                "latency_ms": int((time.time() - start_time) * 1000),
                                "finish_reason": result["choices"][0].get("finish_reason"),
                                "request_id": result.get("id"),
                                "prompt_tokens": result.get("usage", {}).get("prompt_tokens", 0),
                                "completion_tokens": result.get("usage", {}).get("completion_tokens", 0)
                            }
                        }

                    elif response.status == 429:
                        # Rate limited - exponential backoff
                        if attempt < self.config.max_retries - 1:
                            wait_time = 2 ** attempt
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise Exception("Rate limit exceeded")

                    elif response.status == 401:
                        raise Exception("Unauthorized - check API key")

                    else:
                        error_text = await response.text()
                        raise Exception(f"API error {response.status}: {error_text}")

            except asyncio.TimeoutError:
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    raise Exception("Request timeout")

            except Exception as e:
                self._error_count += 1
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    raise

        raise Exception("Max retries exceeded")

    async def embed(self, texts: List[str], **kwargs) -> Dict:
        """
        Generate embeddings (not currently supported by ChatLLM).

        Raises:
            NotImplementedError: ChatLLM doesn't support embeddings yet
        """
        raise NotImplementedError("ChatLLM does not support embeddings")

    async def stream_complete(self, messages: List[Dict], **kwargs):
        """
        Stream a chat completion response.

        Yields chunks of text as they arrive.
        """
        if not self._initialized:
            raise RuntimeError("Adapter not initialized")

        model = kwargs.get("model", self.DEFAULT_MODEL)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)

        url = f"{self.api_base}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        async with self.session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Stream error {response.status}: {error_text}")

            async for line in response.content:
                if line:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith("data: "):
                        data = line_text[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk["choices"][0]["delta"]
                            if "content" in delta:
                                yield delta["content"]
                        except json.JSONDecodeError:
                            continue

    async def shutdown(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics."""
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "total_tokens": self._total_tokens,
            "error_rate": self._error_count / max(self._request_count, 1)
        }
