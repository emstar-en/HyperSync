"""
Summarizer Stage Interceptor

Instruments text summarization with token accounting.
"""

from hypersync.token.interceptors.base import TextInterceptor


class SummarizerInterceptor(TextInterceptor):
    """
    Interceptor for summarization stages.

    Tracks token reduction from summarization.
    """

    def __init__(self, model: str = "gpt-4", emitter=None):
        super().__init__("summarization", model, emitter)

    def count_output(self, result) -> int:
        """
        Count output tokens from summarization result.

        Result can be:
        - String (summary text)
        - Dict with 'summary' key
        - Dict with 'text' key
        """
        if isinstance(result, str):
            return self.counter.count(result)
        elif isinstance(result, dict):
            if "summary" in result:
                return self.counter.count(result["summary"])
            elif "text" in result:
                return self.counter.count(result["text"])

        return 0


def intercept_summarizer(model: str = "gpt-4"):
    """
    Decorator for summarization functions.

    Usage:
        @intercept_summarizer()
        def summarize_document(text: str) -> str:
            # Summarization logic
            return summary
    """
    return SummarizerInterceptor(model)
