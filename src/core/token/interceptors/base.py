"""
Token Interceptor Framework

Provides decorators and middleware for instrumenting pipeline stages
with token accounting.
"""

import functools
import time
from typing import Callable, Optional, Any
from hypersync.token import TokenCounterFactory, TokenEventEmitter


class TokenInterceptor:
    """
    Base class for token interceptors.

    Interceptors wrap pipeline stages to automatically count tokens
    and emit usage events.
    """

    def __init__(
        self,
        stage_name: str,
        model: str = "gpt-4",
        emitter: Optional[TokenEventEmitter] = None
    ):
        self.stage_name = stage_name
        self.counter = TokenCounterFactory.create(model)
        self.emitter = emitter or TokenEventEmitter()

    def count_input(self, *args, **kwargs) -> int:
        """
        Count input tokens.

        Override this method to extract and count tokens from
        stage-specific input formats.
        """
        raise NotImplementedError

    def count_output(self, result: Any) -> int:
        """
        Count output tokens.

        Override this method to extract and count tokens from
        stage-specific output formats.
        """
        raise NotImplementedError

    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap a function with token accounting."""

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Count input tokens
            tokens_in = self.count_input(*args, **kwargs)

            # Execute stage
            start_time = time.time()
            result = await func(*args, **kwargs)
            latency_ms = int((time.time() - start_time) * 1000)

            # Count output tokens
            tokens_out = self.count_output(result)

            # Emit event
            request_id = kwargs.get("request_id")
            session_id = kwargs.get("session_id")
            user_id = kwargs.get("user_id")

            self.emitter.emit(
                stage=self.stage_name,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                request_id=request_id,
                session_id=session_id,
                user_id=user_id,
                metadata={"latency_ms": latency_ms}
            )

            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Count input tokens
            tokens_in = self.count_input(*args, **kwargs)

            # Execute stage
            start_time = time.time()
            result = func(*args, **kwargs)
            latency_ms = int((time.time() - start_time) * 1000)

            # Count output tokens
            tokens_out = self.count_output(result)

            # Emit event
            request_id = kwargs.get("request_id")
            session_id = kwargs.get("session_id")
            user_id = kwargs.get("user_id")

            self.emitter.emit(
                stage=self.stage_name,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                request_id=request_id,
                session_id=session_id,
                user_id=user_id,
                metadata={"latency_ms": latency_ms}
            )

            return result

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper


class TextInterceptor(TokenInterceptor):
    """
    Interceptor for text-to-text transformations.

    Assumes input is a string and output is a string.
    """

    def count_input(self, text: str, *args, **kwargs) -> int:
        """Count tokens in input text."""
        return self.counter.count(text)

    def count_output(self, result: str) -> int:
        """Count tokens in output text."""
        if isinstance(result, str):
            return self.counter.count(result)
        return 0


class MessagesInterceptor(TokenInterceptor):
    """
    Interceptor for chat message transformations.

    Assumes input/output are lists of message dicts.
    """

    def count_input(self, messages: list, *args, **kwargs) -> int:
        """Count tokens in input messages."""
        return self.counter.count_messages(messages)

    def count_output(self, result) -> int:
        """Count tokens in output messages."""
        if isinstance(result, list):
            return self.counter.count_messages(result)
        elif isinstance(result, dict) and "messages" in result:
            return self.counter.count_messages(result["messages"])
        return 0


class ProviderInterceptor(TokenInterceptor):
    """
    Interceptor for provider API calls.

    Extracts token counts from provider responses.
    """

    def count_input(self, *args, **kwargs) -> int:
        """
        Count input tokens from request.

        For provider calls, we typically have messages or prompt.
        """
        if "messages" in kwargs:
            return self.counter.count_messages(kwargs["messages"])
        elif "prompt" in kwargs:
            return self.counter.count(kwargs["prompt"])
        elif len(args) > 0:
            if isinstance(args[0], str):
                return self.counter.count(args[0])
            elif isinstance(args[0], list):
                return self.counter.count_messages(args[0])
        return 0

    def count_output(self, result: dict) -> int:
        """
        Extract token count from provider response.

        Most providers return token counts in their response.
        """
        if isinstance(result, dict):
            # Check for tokens_used field (our standard)
            if "tokens_used" in result:
                return result["tokens_used"]

            # Check for usage object (OpenAI format)
            if "usage" in result:
                usage = result["usage"]
                if "total_tokens" in usage:
                    return usage["total_tokens"]

            # Fallback: count the text
            if "text" in result:
                return self.counter.count(result["text"])

        return 0


def intercept_text(stage_name: str, model: str = "gpt-4"):
    """
    Decorator for text-to-text stages.

    Usage:
        @intercept_text("summarization")
        def summarize(text: str) -> str:
            ...
    """
    return TextInterceptor(stage_name, model)


def intercept_messages(stage_name: str, model: str = "gpt-4"):
    """
    Decorator for message-to-message stages.

    Usage:
        @intercept_messages("preprocessing")
        async def preprocess(messages: list) -> list:
            ...
    """
    return MessagesInterceptor(stage_name, model)


def intercept_provider(stage_name: str, model: str = "gpt-4"):
    """
    Decorator for provider API calls.

    Usage:
        @intercept_provider("provider_request")
        async def call_provider(messages: list) -> dict:
            ...
    """
    return ProviderInterceptor(stage_name, model)
