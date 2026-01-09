"""
Diff Generator Interceptor

Instruments diff generation with token accounting.
"""

from hypersync.token.interceptors.base import TokenInterceptor


class DiffInterceptor(TokenInterceptor):
    """
    Interceptor for diff generation stages.

    Tracks token reduction from diff-based prompting.
    """

    def __init__(self, model: str = "gpt-4", emitter=None):
        super().__init__("diff_generation", model, emitter)

    def count_input(self, *args, **kwargs) -> int:
        """
        Count input tokens.

        Diff generation typically takes old and new versions.
        """
        total = 0

        if "old_text" in kwargs:
            total += self.counter.count(kwargs["old_text"])
        if "new_text" in kwargs:
            total += self.counter.count(kwargs["new_text"])

        # Fallback to positional args
        if len(args) >= 2:
            total += self.counter.count(args[0])
            total += self.counter.count(args[1])

        return total

    def count_output(self, result) -> int:
        """Count output tokens from diff."""
        if isinstance(result, str):
            return self.counter.count(result)
        elif isinstance(result, dict):
            if "diff" in result:
                return self.counter.count(result["diff"])
            elif "patch" in result:
                return self.counter.count(result["patch"])

        return 0


def intercept_diff(model: str = "gpt-4"):
    """
    Decorator for diff generation functions.

    Usage:
        @intercept_diff()
        def generate_diff(old_text: str, new_text: str) -> str:
            # Diff logic
            return diff
    """
    return DiffInterceptor(model)
