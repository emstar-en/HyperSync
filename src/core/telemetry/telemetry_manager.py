"""
Enhanced Telemetry Manager

Exports metrics, receipts, and events to multiple backends.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class TelemetryBackend(str, Enum):
    """Supported telemetry backends."""
    PROMETHEUS = "prometheus"
    GRAFANA = "grafana"
    DATADOG = "datadog"
    CLOUDWATCH = "cloudwatch"
    STDOUT = "stdout"


@dataclass
class TelemetryEvent:
    """Telemetry event."""
    event_type: str
    source: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "metrics": self.metrics
        }


class TelemetryManager:
    """
    Enhanced telemetry manager.

    Features:
    - Multi-backend export
    - Receipt generation
    - Metrics aggregation
    - Event streaming
    """

    def __init__(self, backends: Optional[List[TelemetryBackend]] = None):
        self.backends = backends or [TelemetryBackend.STDOUT]
        self.events: List[TelemetryEvent] = []
        self.metrics: Dict[str, List[float]] = {}

    def emit_event(self, event: TelemetryEvent):
        """Emit telemetry event."""
        self.events.append(event)

        # Export to backends
        for backend in self.backends:
            self._export_to_backend(backend, event)

    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record metric."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

        # Create event
        event = TelemetryEvent(
            event_type="metric",
            source="telemetry_manager",
            metadata={"metric_name": name, "labels": labels or {}},
            metrics={name: value}
        )
        self.emit_event(event)

    def get_metrics(self, name: Optional[str] = None) -> Dict[str, List[float]]:
        """Get recorded metrics."""
        if name:
            return {name: self.metrics.get(name, [])}
        return self.metrics

    def get_events(self, event_type: Optional[str] = None) -> List[TelemetryEvent]:
        """Get events."""
        if event_type:
            return [e for e in self.events if e.event_type == event_type]
        return self.events

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        for name, values in self.metrics.items():
            if values:
                # Use latest value
                lines.append(f"hypersync_{name} {values[-1]}")
        return "\n".join(lines)

    def export_json(self) -> str:
        """Export events as JSON."""
        return json.dumps([e.to_dict() for e in self.events], indent=2)

    def _export_to_backend(self, backend: TelemetryBackend, event: TelemetryEvent):
        """Export event to specific backend."""
        if backend == TelemetryBackend.STDOUT:
            print(f"[TELEMETRY] {event.event_type}: {event.metadata}")
        elif backend == TelemetryBackend.PROMETHEUS:
            # Would push to Prometheus pushgateway
            pass
        elif backend == TelemetryBackend.GRAFANA:
            # Would send to Grafana Loki
            pass
        elif backend == TelemetryBackend.DATADOG:
            # Would send to Datadog API
            pass
        elif backend == TelemetryBackend.CLOUDWATCH:
            # Would send to CloudWatch
            pass


# Global instance
_telemetry_manager: Optional[TelemetryManager] = None


def get_telemetry_manager() -> TelemetryManager:
    """Get global telemetry manager."""
    global _telemetry_manager
    if _telemetry_manager is None:
        _telemetry_manager = TelemetryManager()
    return _telemetry_manager


def emit_event(event_type: str, source: str, metadata: Optional[Dict[str, Any]] = None,
               metrics: Optional[Dict[str, float]] = None):
    """Convenience function to emit event."""
    manager = get_telemetry_manager()
    event = TelemetryEvent(
        event_type=event_type,
        source=source,
        metadata=metadata or {},
        metrics=metrics or {}
    )
    manager.emit_event(event)


def record_metric(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Convenience function to record metric."""
    manager = get_telemetry_manager()
    manager.record_metric(name, value, labels)
