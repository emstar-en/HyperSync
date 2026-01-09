"""
Telemetry Integration

Sends token events to telemetry system for real-time monitoring.
"""

from typing import Dict, Optional, Any
from datetime import datetime


class TelemetryClient:
    """
    Client for sending token events to telemetry system.

    Integrates with HyperSync telemetry infrastructure.
    """

    def __init__(self, telemetry_endpoint: Optional[str] = None):
        self.endpoint = telemetry_endpoint
        self._buffer = []
        self._buffer_size = 100

    def emit(self, event_type: str, data: Dict[str, Any]):
        """
        Emit a telemetry event.

        Args:
            event_type: Event type (e.g., "prompt.token_usage")
            data: Event data
        """
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": data
        }

        self._buffer.append(event)

        # Flush if buffer is full
        if len(self._buffer) >= self._buffer_size:
            self.flush()

    def flush(self):
        """Flush buffered events to telemetry system."""
        if not self._buffer:
            return

        # TODO: Send to actual telemetry endpoint
        # For now, just clear buffer
        self._buffer.clear()

    def close(self):
        """Close client and flush remaining events."""
        self.flush()


class TokenMetrics:
    """
    Aggregates token metrics for dashboards.

    Provides real-time and historical metrics:
    - Tokens per minute
    - Compression ratios
    - Cost savings
    - Provider distribution
    """

    def __init__(self):
        self._metrics = {
            "total_tokens": 0,
            "tokens_saved": 0,
            "requests": 0,
            "by_stage": {},
            "by_provider": {},
            "by_user": {}
        }

    def record_event(self, event: Dict):
        """Record a token event for metrics."""
        self._metrics["total_tokens"] += event.get("tokens_out", 0)
        self._metrics["tokens_saved"] += event.get("tokens_saved", 0)

        # By stage
        stage = event.get("stage")
        if stage:
            if stage not in self._metrics["by_stage"]:
                self._metrics["by_stage"][stage] = {
                    "tokens": 0,
                    "saved": 0,
                    "count": 0
                }
            self._metrics["by_stage"][stage]["tokens"] += event.get("tokens_out", 0)
            self._metrics["by_stage"][stage]["saved"] += event.get("tokens_saved", 0)
            self._metrics["by_stage"][stage]["count"] += 1

        # By provider
        provider = event.get("provider")
        if provider:
            if provider not in self._metrics["by_provider"]:
                self._metrics["by_provider"][provider] = {
                    "tokens": 0,
                    "requests": 0
                }
            self._metrics["by_provider"][provider]["tokens"] += event.get("tokens_out", 0)
            self._metrics["by_provider"][provider]["requests"] += 1

        # By user
        user_id = event.get("user_id")
        if user_id:
            if user_id not in self._metrics["by_user"]:
                self._metrics["by_user"][user_id] = {
                    "tokens": 0,
                    "requests": 0
                }
            self._metrics["by_user"][user_id]["tokens"] += event.get("tokens_out", 0)
            self._metrics["by_user"][user_id]["requests"] += 1

    def get_metrics(self) -> Dict:
        """Get current metrics snapshot."""
        return self._metrics.copy()

    def reset(self):
        """Reset metrics."""
        self._metrics = {
            "total_tokens": 0,
            "tokens_saved": 0,
            "requests": 0,
            "by_stage": {},
            "by_provider": {},
            "by_user": {}
        }


# Global instances
_telemetry_client = None
_token_metrics = None


def get_telemetry_client() -> TelemetryClient:
    """Get global telemetry client."""
    global _telemetry_client
    if _telemetry_client is None:
        _telemetry_client = TelemetryClient()
    return _telemetry_client


def get_token_metrics() -> TokenMetrics:
    """Get global token metrics."""
    global _token_metrics
    if _token_metrics is None:
        _token_metrics = TokenMetrics()
    return _token_metrics
