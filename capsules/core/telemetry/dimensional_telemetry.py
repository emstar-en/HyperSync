"""
HyperSync Dimensional Telemetry Collector

Emits dimensional events and metrics for observability.
Integrates with OpenTelemetry and Prometheus.
"""

import uuid
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import json


class EventType(Enum):
    """Dimensional event types."""
    DIM_SYNC_START = "dim.sync.start"
    DIM_SYNC_COMPLETE = "dim.sync.complete"
    DIM_SYNC_FAILED = "dim.sync.failed"
    DIM_ALIGN_START = "dim.align.start"
    DIM_ALIGN_COMPLETE = "dim.align.complete"
    VECTOR_QUERY = "vector.query"
    CONTRACT_CREATED = "contract.created"
    ROUTE_NEGOTIATED = "route.negotiated"
    POLICY_EVALUATED = "policy.evaluated"


class MetricUnit(Enum):
    """Metric units."""
    COUNT = "count"
    MILLISECONDS = "ms"
    MBPS = "mbps"
    PERCENT = "percent"
    RATIO = "ratio"


class AggregationType(Enum):
    """Metric aggregation types."""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    P50 = "p50"
    P95 = "p95"
    P99 = "p99"


@dataclass
class DimensionalEvent:
    """Dimensional telemetry event."""
    event_id: str
    event_type: EventType
    timestamp: datetime
    node_id: str

    agent_id: Optional[str] = None
    user_id: Optional[str] = None

    dimensions: List[int] = field(default_factory=list)
    curvature: Optional[float] = None
    frame_id: Optional[str] = None
    session_id: Optional[str] = None

    duration_ms: Optional[float] = None
    latency_ms: Optional[float] = None
    throughput_mbps: Optional[float] = None
    error_rate: Optional[float] = None
    convergence_error: Optional[float] = None

    tags: List[str] = field(default_factory=list)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None

    def to_dict(self) -> Dict:
        """Export event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": {
                "node_id": self.node_id,
                "agent_id": self.agent_id,
                "user_id": self.user_id
            },
            "dimensional_context": {
                "dimensions": self.dimensions,
                "curvature": self.curvature,
                "frame_id": self.frame_id,
                "session_id": self.session_id
            },
            "metrics": {
                "duration_ms": self.duration_ms,
                "latency_ms": self.latency_ms,
                "throughput_mbps": self.throughput_mbps,
                "error_rate": self.error_rate,
                "convergence_error": self.convergence_error
            },
            "metadata": {
                "tags": self.tags,
                "trace_id": self.trace_id,
                "span_id": self.span_id
            }
        }


@dataclass
class DimensionalMetric:
    """Dimensional metric."""
    metric_name: str
    timestamp: datetime
    value: float
    unit: MetricUnit

    node_id: Optional[str] = None
    agent_id: Optional[str] = None
    operation: Optional[str] = None
    status: Optional[str] = None

    aggregation_type: Optional[AggregationType] = None
    window_seconds: Optional[int] = None

    def to_dict(self) -> Dict:
        """Export metric to dictionary."""
        return {
            "metric_name": self.metric_name,
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "unit": self.unit.value,
            "dimensions": {
                "node_id": self.node_id,
                "agent_id": self.agent_id,
                "operation": self.operation,
                "status": self.status
            },
            "aggregation": {
                "type": self.aggregation_type.value if self.aggregation_type else None,
                "window_seconds": self.window_seconds
            }
        }


class EventBuffer:
    """Buffer for batching events."""

    def __init__(self, max_size: int = 1000, flush_interval_seconds: int = 60):
        self.max_size = max_size
        self.flush_interval_seconds = flush_interval_seconds
        self.events: List[DimensionalEvent] = []
        self.last_flush = time.time()

    def add(self, event: DimensionalEvent):
        """Add event to buffer."""
        self.events.append(event)

        # Auto-flush if buffer full or interval elapsed
        if len(self.events) >= self.max_size or            (time.time() - self.last_flush) >= self.flush_interval_seconds:
            return True  # Signal flush needed

        return False

    def flush(self) -> List[DimensionalEvent]:
        """Flush buffer and return events."""
        events = self.events.copy()
        self.events.clear()
        self.last_flush = time.time()
        return events

    def size(self) -> int:
        """Get current buffer size."""
        return len(self.events)


class MetricAggregator:
    """Aggregates metrics over time windows."""

    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self.values: Dict[str, List[float]] = defaultdict(list)
        self.last_reset = time.time()

    def record(self, metric_name: str, value: float):
        """Record a metric value."""
        self.values[metric_name].append(value)

        # Reset if window elapsed
        if (time.time() - self.last_reset) >= self.window_seconds:
            return True  # Signal aggregation needed

        return False

    def aggregate(self, metric_name: str, agg_type: AggregationType) -> Optional[float]:
        """Aggregate metric values."""
        if metric_name not in self.values or not self.values[metric_name]:
            return None

        values = self.values[metric_name]

        if agg_type == AggregationType.SUM:
            return sum(values)
        elif agg_type == AggregationType.AVG:
            return sum(values) / len(values)
        elif agg_type == AggregationType.MIN:
            return min(values)
        elif agg_type == AggregationType.MAX:
            return max(values)
        elif agg_type == AggregationType.P50:
            return self._percentile(values, 50)
        elif agg_type == AggregationType.P95:
            return self._percentile(values, 95)
        elif agg_type == AggregationType.P99:
            return self._percentile(values, 99)

        return None

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile."""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100.0))
        return sorted_values[min(index, len(sorted_values) - 1)]

    def reset(self):
        """Reset aggregator."""
        self.values.clear()
        self.last_reset = time.time()


class DimensionalTelemetryCollector:
    """
    Collects and emits dimensional telemetry.

    Integrates with OpenTelemetry and Prometheus for observability.
    """

    def __init__(self, node_id: str, buffer_size: int = 1000,
                 flush_interval: int = 60):
        """
        Initialize telemetry collector.

        Args:
            node_id: Node identifier
            buffer_size: Event buffer size
            flush_interval: Flush interval in seconds
        """
        self.node_id = node_id
        self.event_buffer = EventBuffer(buffer_size, flush_interval)
        self.metric_aggregator = MetricAggregator(window_seconds=60)

        # Event handlers
        self.event_handlers: List[callable] = []
        self.metric_handlers: List[callable] = []

        # Statistics
        self.events_emitted = 0
        self.metrics_emitted = 0

    def emit_event(self, event_type: EventType, **kwargs):
        """
        Emit a dimensional event.

        Args:
            event_type: Type of event
            **kwargs: Event attributes
        """
        event = DimensionalEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.now(),
            node_id=self.node_id,
            **kwargs
        )

        # Add to buffer
        should_flush = self.event_buffer.add(event)

        if should_flush:
            self._flush_events()

        self.events_emitted += 1

    def emit_metric(self, metric_name: str, value: float, unit: MetricUnit,
                   **dimensions):
        """
        Emit a dimensional metric.

        Args:
            metric_name: Metric identifier
            value: Metric value
            unit: Metric unit
            **dimensions: Metric dimensions
        """
        metric = DimensionalMetric(
            metric_name=metric_name,
            timestamp=datetime.now(),
            value=value,
            unit=unit,
            node_id=self.node_id,
            **dimensions
        )

        # Record for aggregation
        should_aggregate = self.metric_aggregator.record(metric_name, value)

        # Emit to handlers
        for handler in self.metric_handlers:
            handler(metric)

        if should_aggregate:
            self._emit_aggregated_metrics()

        self.metrics_emitted += 1

    def register_event_handler(self, handler: callable):
        """Register event handler."""
        self.event_handlers.append(handler)

    def register_metric_handler(self, handler: callable):
        """Register metric handler."""
        self.metric_handlers.append(handler)

    def _flush_events(self):
        """Flush event buffer."""
        events = self.event_buffer.flush()

        for event in events:
            for handler in self.event_handlers:
                handler(event)

    def _emit_aggregated_metrics(self):
        """Emit aggregated metrics."""
        for metric_name in self.metric_aggregator.values.keys():
            for agg_type in [AggregationType.AVG, AggregationType.P95, AggregationType.P99]:
                value = self.metric_aggregator.aggregate(metric_name, agg_type)
                if value is not None:
                    agg_metric = DimensionalMetric(
                        metric_name=f"{metric_name}.{agg_type.value}",
                        timestamp=datetime.now(),
                        value=value,
                        unit=MetricUnit.MILLISECONDS,  # Assume ms for now
                        node_id=self.node_id,
                        aggregation_type=agg_type,
                        window_seconds=self.metric_aggregator.window_seconds
                    )

                    for handler in self.metric_handlers:
                        handler(agg_metric)

        self.metric_aggregator.reset()

    def get_statistics(self) -> Dict:
        """Get collector statistics."""
        return {
            "node_id": self.node_id,
            "events_emitted": self.events_emitted,
            "metrics_emitted": self.metrics_emitted,
            "buffer_size": self.event_buffer.size(),
            "event_handlers": len(self.event_handlers),
            "metric_handlers": len(self.metric_handlers)
        }


class ConsoleEventHandler:
    """Simple console event handler for debugging."""

    def __call__(self, event: DimensionalEvent):
        """Handle event."""
        print(f"[EVENT] {event.event_type.value} @ {event.timestamp.isoformat()}")
        if event.session_id:
            print(f"  Session: {event.session_id}")
        if event.duration_ms:
            print(f"  Duration: {event.duration_ms}ms")


class ConsoleMetricHandler:
    """Simple console metric handler for debugging."""

    def __call__(self, metric: DimensionalMetric):
        """Handle metric."""
        print(f"[METRIC] {metric.metric_name} = {metric.value} {metric.unit.value}")


class JSONFileHandler:
    """Writes events/metrics to JSON file."""

    def __init__(self, filepath: str):
        self.filepath = filepath

    def __call__(self, item):
        """Handle event or metric."""
        with open(self.filepath, 'a') as f:
            json.dump(item.to_dict(), f)
            f.write('\n')
