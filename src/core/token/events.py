"""
Token Event Emitter

Emits token usage events for telemetry and accounting.
"""

import uuid
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class TokenEvent:
    """Token usage event."""
    event_id: str
    timestamp: str
    stage: str
    tokens_in: int
    tokens_out: int
    tokens_saved: int
    compression_ratio: float
    model: Optional[str] = None
    provider: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class TokenEventEmitter:
    """
    Emits token events to telemetry system.

    Events are sent to:
    - Telemetry streams (for real-time monitoring)
    - Receipt accumulator (for per-request summaries)
    - Audit log (for compliance)
    """

    def __init__(self, telemetry_client=None, receipt_accumulator=None):
        self.telemetry_client = telemetry_client
        self.receipt_accumulator = receipt_accumulator
        self._event_buffer = []

    def emit(
        self,
        stage: str,
        tokens_in: int,
        tokens_out: int,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> TokenEvent:
        """
        Emit a token usage event.

        Args:
            stage: Pipeline stage name
            tokens_in: Input token count
            tokens_out: Output token count
            request_id: Request identifier
            session_id: Session identifier
            user_id: User identifier
            model: Model name
            provider: Provider identifier
            metadata: Additional metadata

        Returns:
            Created TokenEvent
        """
        # Calculate derived fields
        tokens_saved = max(0, tokens_in - tokens_out)
        compression_ratio = tokens_out / tokens_in if tokens_in > 0 else 1.0

        # Create event
        event = TokenEvent(
            event_id=f"tok_{uuid.uuid4().hex[:16]}",
            timestamp=datetime.utcnow().isoformat() + "Z",
            stage=stage,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            tokens_saved=tokens_saved,
            compression_ratio=compression_ratio,
            model=model,
            provider=provider,
            request_id=request_id,
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {}
        )

        # Send to telemetry
        if self.telemetry_client:
            self.telemetry_client.emit(
                "prompt.token_usage",
                event.to_dict()
            )

        # Accumulate for receipt
        if self.receipt_accumulator and request_id:
            self.receipt_accumulator.add_event(request_id, event)

        # Buffer for batch processing
        self._event_buffer.append(event)

        return event

    def flush(self):
        """Flush buffered events."""
        if self.telemetry_client:
            for event in self._event_buffer:
                self.telemetry_client.emit(
                    "prompt.token_usage",
                    event.to_dict()
                )

        self._event_buffer.clear()
