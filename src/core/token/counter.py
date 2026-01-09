"""
Token Counter Interface

Provides token counting utilities for various models and providers.
"""

from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import tiktoken


class TokenCounter(ABC):
    """
    Abstract base class for token counters.

    Different models use different tokenization schemes,
    so we need model-specific counters.
    """

    @abstractmethod
    def count(self, text: str) -> int:
        """Count tokens in text."""
        pass

    @abstractmethod
    def count_messages(self, messages: List[Dict]) -> int:
        """Count tokens in chat messages."""
        pass


class TiktokenCounter(TokenCounter):
    """
    Token counter using tiktoken (OpenAI tokenizer).

    Works for GPT-3.5, GPT-4, and compatible models.
    """

    def __init__(self, model: str = "gpt-4"):
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base for unknown models
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def count_messages(self, messages: List[Dict]) -> int:
        """
        Count tokens in chat messages.

        Includes overhead for message formatting.
        """
        tokens = 0

        for message in messages:
            tokens += 4  # Message overhead
            tokens += self.count(message.get("role", ""))
            tokens += self.count(message.get("content", ""))

        tokens += 2  # Conversation overhead

        return tokens


class ClaudeCounter(TokenCounter):
    """
    Token counter for Claude models.

    Uses approximate counting based on character length
    since Anthropic doesn't provide a public tokenizer.
    """

    # Approximate: 1 token ≈ 4 characters for English text
    CHARS_PER_TOKEN = 4

    def count(self, text: str) -> int:
        """Approximate token count."""
        return len(text) // self.CHARS_PER_TOKEN

    def count_messages(self, messages: List[Dict]) -> int:
        """Count tokens in messages."""
        total = 0

        for message in messages:
            # Add role overhead
            total += 2
            # Add content
            total += self.count(message.get("content", ""))

        return total


class TokenCounterFactory:
    """Factory for creating appropriate token counters."""

    _COUNTERS = {
        "gpt-3.5-turbo": TiktokenCounter,
        "gpt-4": TiktokenCounter,
        "gpt-4-turbo": TiktokenCounter,
        "claude-3": ClaudeCounter,
        "claude-sonnet": ClaudeCounter,
        "claude-opus": ClaudeCounter,
    }

    @classmethod
    def create(cls, model: str) -> TokenCounter:
        """
        Create a token counter for the specified model.

        Args:
            model: Model identifier

        Returns:
            Appropriate TokenCounter instance
        """
        # Try exact match
        if model in cls._COUNTERS:
            counter_class = cls._COUNTERS[model]
            return counter_class(model)

        # Try prefix match
        for prefix, counter_class in cls._COUNTERS.items():
            if model.startswith(prefix):
                return counter_class(model)

        # Default to tiktoken
        return TiktokenCounter(model)

    @classmethod
    def register(cls, model: str, counter_class: type):
        """Register a custom counter for a model."""
        cls._COUNTERS[model] = counter_class
