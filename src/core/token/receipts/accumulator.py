"""
Receipt Accumulator

Accumulates token events into comprehensive receipts.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from hypersync.token.events import TokenEvent


@dataclass
class TokenReceipt:
    """Comprehensive token usage receipt."""
    receipt_id: str
    timestamp: str
    request_id: str
    session_id: Optional[str]
    user_id: Optional[str]
    total_tokens: Dict
    stages: List[Dict]
    provider: Optional[Dict]
    savings: Optional[Dict]
    metadata: Dict

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class ReceiptAccumulator:
    """
    Accumulates token events into receipts.

    Maintains per-request state and generates comprehensive
    receipts when requests complete.
    """

    def __init__(self):
        self._active_requests: Dict[str, List[TokenEvent]] = {}
        self._completed_receipts: List[TokenReceipt] = []

    def add_event(self, request_id: str, event: TokenEvent):
        """Add a token event to a request."""
        if request_id not in self._active_requests:
            self._active_requests[request_id] = []

        self._active_requests[request_id].append(event)

    def finalize_receipt(self, request_id: str) -> Optional[TokenReceipt]:
        """
        Finalize a receipt for a completed request.

        Args:
            request_id: Request identifier

        Returns:
            TokenReceipt if events exist, None otherwise
        """
        if request_id not in self._active_requests:
            return None

        events = self._active_requests.pop(request_id)

        if not events:
            return None

        # Aggregate totals
        total_input = sum(e.tokens_in for e in events)
        total_output = sum(e.tokens_out for e in events)
        total_saved = sum(e.tokens_saved for e in events)

        # Find provider event for charged tokens
        provider_event = next(
            (e for e in events if e.stage == "provider_response"),
            None
        )
        provider_charged = provider_event.tokens_out if provider_event else total_output

        # Build stage summaries
        stages = []
        for event in events:
            stages.append({
                "stage": event.stage,
                "tokens_in": event.tokens_in,
                "tokens_out": event.tokens_out,
                "tokens_saved": event.tokens_saved,
                "compression_ratio": event.compression_ratio,
                "latency_ms": event.metadata.get("latency_ms", 0)
            })

        # Provider details
        provider_info = None
        if provider_event:
            provider_info = {
                "provider_id": provider_event.provider,
                "model": provider_event.model,
                "prompt_tokens": provider_event.metadata.get("prompt_tokens", 0),
                "completion_tokens": provider_event.metadata.get("completion_tokens", 0),
                "cost_usd": provider_event.metadata.get("cost_usd", 0.0)
            }

        # Calculate savings
        # Baseline = what we would have sent without compression
        baseline_tokens = events[0].tokens_in if events else 0
        actual_tokens = provider_charged
        tokens_saved = baseline_tokens - actual_tokens
        savings_percent = (tokens_saved / baseline_tokens * 100) if baseline_tokens > 0 else 0

        savings_info = {
            "baseline_tokens": baseline_tokens,
            "actual_tokens": actual_tokens,
            "tokens_saved": tokens_saved,
            "savings_percent": round(savings_percent, 2),
            "cost_saved_usd": 0.0  # TODO: Calculate based on pricing
        }

        # Create receipt
        receipt = TokenReceipt(
            receipt_id=f"rcpt_{uuid.uuid4().hex[:16]}",
            timestamp=datetime.utcnow().isoformat() + "Z",
            request_id=request_id,
            session_id=events[0].session_id,
            user_id=events[0].user_id,
            total_tokens={
                "input": total_input,
                "output": total_output,
                "saved": total_saved,
                "provider_charged": provider_charged
            },
            stages=stages,
            provider=provider_info,
            savings=savings_info,
            metadata={}
        )

        self._completed_receipts.append(receipt)

        return receipt

    def get_receipt(self, receipt_id: str) -> Optional[TokenReceipt]:
        """Get a completed receipt by ID."""
        for receipt in self._completed_receipts:
            if receipt.receipt_id == receipt_id:
                return receipt
        return None

    def list_receipts(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 100
    ) -> List[TokenReceipt]:
        """
        List receipts with optional filtering.

        Args:
            user_id: Filter by user
            session_id: Filter by session
            limit: Maximum number of receipts

        Returns:
            List of matching receipts
        """
        receipts = self._completed_receipts

        if user_id:
            receipts = [r for r in receipts if r.user_id == user_id]

        if session_id:
            receipts = [r for r in receipts if r.session_id == session_id]

        # Return most recent first
        receipts = sorted(
            receipts,
            key=lambda r: r.timestamp,
            reverse=True
        )

        return receipts[:limit]

    def clear_old_receipts(self, max_age_hours: int = 24):
        """Clear receipts older than specified age."""
        cutoff = datetime.utcnow().timestamp() - (max_age_hours * 3600)

        self._completed_receipts = [
            r for r in self._completed_receipts
            if datetime.fromisoformat(r.timestamp.rstrip('Z')).timestamp() > cutoff
        ]


# Global accumulator instance
_global_accumulator = None


def get_accumulator() -> ReceiptAccumulator:
    """Get the global receipt accumulator."""
    global _global_accumulator
    if _global_accumulator is None:
        _global_accumulator = ReceiptAccumulator()
    return _global_accumulator
