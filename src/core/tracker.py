"""Token Tracker - Track token usage across all operations."""
import logging
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Token usage record."""
    operation: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    timestamp: float
    context: Dict[str, Any]


class TokenTracker:
    """Track token usage across all operations."""

    def __init__(self):
        self._usage_records: list = []
        self._current_operation: Optional[Dict[str, Any]] = None

    @contextmanager
    def track_operation(self, operation: str, context: Optional[Dict[str, Any]] = None):
        """Context manager for tracking operations."""
        self.start_operation(operation, context or {})
        ctx = OperationContext(self)
        try:
            yield ctx
        finally:
            self.end_operation()

    def start_operation(self, operation: str, context: Dict[str, Any]):
        """Start tracking an operation."""
        self._current_operation = {
            "operation": operation,
            "context": context,
            "start_time": time.time()
        }

    def record_tokens(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: Optional[int] = None
    ):
        """Record token usage."""
        if not self._current_operation:
            logger.warning("No active operation to record tokens")
            return

        if total_tokens is None:
            total_tokens = prompt_tokens + completion_tokens

        usage = TokenUsage(
            operation=self._current_operation["operation"],
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            timestamp=time.time(),
            context=self._current_operation["context"]
        )

        self._usage_records.append(usage)
        logger.debug(f"Recorded {total_tokens} tokens for {usage.operation}")

    def end_operation(self):
        """End current operation."""
        self._current_operation = None

    def get_total_tokens(self) -> int:
        """Get total tokens used."""
        return sum(r.total_tokens for r in self._usage_records)

    def get_usage_by_operation(self) -> Dict[str, int]:
        """Get token usage grouped by operation."""
        usage = {}
        for record in self._usage_records:
            usage[record.operation] = usage.get(record.operation, 0) + record.total_tokens
        return usage

    def get_status(self) -> Dict[str, Any]:
        """Get tracker status."""
        return {
            "total_operations": len(self._usage_records),
            "total_tokens": self.get_total_tokens(),
            "by_operation": self.get_usage_by_operation()
        }


class OperationContext:
    """Context for tracking operation."""
    def __init__(self, tracker: TokenTracker):
        self.tracker = tracker

    def record_tokens(self, **kwargs):
        """Record tokens in context."""
        self.tracker.record_tokens(**kwargs)


_token_tracker: Optional[TokenTracker] = None


def get_token_tracker() -> TokenTracker:
    """Get global token tracker."""
    global _token_tracker
    if _token_tracker is None:
        _token_tracker = TokenTracker()
    return _token_tracker
