"""
Hyperbolic Compression Interceptor

Instruments hyperbolic compression with token accounting.
"""

from hypersync.token.interceptors.base import TokenInterceptor


class HyperbolicInterceptor(TokenInterceptor):
    """
    Interceptor for hyperbolic compression stages.

    Tracks aggressive token reduction from hyperbolic compression.
    """

    def __init__(self, model: str = "gpt-4", emitter=None):
        super().__init__("hyperbolic_compression", model, emitter)

    def count_input(self, *args, **kwargs) -> int:
        """Count input tokens."""
        # Input can be text or messages
        if len(args) > 0:
            if isinstance(args[0], str):
                return self.counter.count(args[0])
            elif isinstance(args[0], list):
                return self.counter.count_messages(args[0])

        if "text" in kwargs:
            return self.counter.count(kwargs["text"])
        elif "messages" in kwargs:
            return self.counter.count_messages(kwargs["messages"])

        return 0

    def count_output(self, result) -> int:
        """Count output tokens from compressed result."""
        if isinstance(result, str):
            return self.counter.count(result)
        elif isinstance(result, dict):
            if "compressed" in result:
                return self.counter.count(result["compressed"])
            elif "text" in result:
                return self.counter.count(result["text"])
            elif "messages" in result:
                return self.counter.count_messages(result["messages"])
        elif isinstance(result, list):
            return self.counter.count_messages(result)

        return 0


def intercept_hyperbolic(model: str = "gpt-4"):
    """
    Decorator for hyperbolic compression functions.

    Usage:
        @intercept_hyperbolic()
        async def compress_hyperbolic(text: str) -> str:
            # Compression logic
            return compressed
    """
    return HyperbolicInterceptor(model)
