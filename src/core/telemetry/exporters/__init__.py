"""
HyperSync Telemetry Exporters

Export telemetry events to various backends (console, file, OTLP, etc.).
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class TelemetryExporter:
    """Base class for telemetry exporters."""

    def export(self, event: Dict[str, Any]) -> None:
        """
        Export a telemetry event.

        Args:
            event: Event dictionary
        """
        raise NotImplementedError("Subclasses must implement export()")

    def flush(self) -> None:
        """Flush any buffered events."""
        pass

    def close(self) -> None:
        """Close the exporter and release resources."""
        pass


class ConsoleExporter(TelemetryExporter):
    """Export events to console/stdout."""

    def __init__(self, pretty: bool = True):
        """
        Initialize console exporter.

        Args:
            pretty: Pretty-print JSON output
        """
        self.pretty = pretty

    def export(self, event: Dict[str, Any]) -> None:
        """Export event to console."""
        if self.pretty:
            print(json.dumps(event, indent=2))
        else:
            print(json.dumps(event))


class FileExporter(TelemetryExporter):
    """Export events to a file."""

    def __init__(self, filepath: str, buffer_size: int = 100):
        """
        Initialize file exporter.

        Args:
            filepath: Path to output file
            buffer_size: Number of events to buffer before flushing
        """
        self.filepath = Path(filepath)
        self.buffer_size = buffer_size
        self.buffer = []

        # Create parent directories
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        # Open file in append mode
        self.file = open(self.filepath, 'a')

    def export(self, event: Dict[str, Any]) -> None:
        """Export event to file."""
        self.buffer.append(event)

        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self) -> None:
        """Flush buffered events to file."""
        if not self.buffer:
            return

        for event in self.buffer:
            self.file.write(json.dumps(event) + '\n')

        self.file.flush()
        self.buffer.clear()
        logger.debug(f"Flushed events to {self.filepath}")

    def close(self) -> None:
        """Close file exporter."""
        self.flush()
        self.file.close()


class StructuredLogExporter(TelemetryExporter):
    """Export events to structured logging."""

    def __init__(self, logger_name: str = 'hypersync.telemetry'):
        """
        Initialize structured log exporter.

        Args:
            logger_name: Logger name to use
        """
        self.logger = logging.getLogger(logger_name)

    def export(self, event: Dict[str, Any]) -> None:
        """Export event to structured log."""
        event_type = event.get('event_type', 'unknown')
        agent_id = event.get('agent_id', 'unknown')

        # Determine log level based on event type
        if 'failed' in event_type or 'denied' in event_type or 'violated' in event_type:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

        self.logger.log(
            log_level,
            f"Agent telemetry: {event_type}",
            extra={
                'event': event,
                'agent_id': agent_id,
                'event_type': event_type
            }
        )


class AuditLogExporter(TelemetryExporter):
    """
    Export security-relevant events to audit log.

    Only exports events with security context.
    """

    def __init__(self, audit_log_path: str):
        """
        Initialize audit log exporter.

        Args:
            audit_log_path: Path to audit log file
        """
        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.audit_log_path, 'a')

    def export(self, event: Dict[str, Any]) -> None:
        """Export security events to audit log."""
        security_context = event.get('security_context', {})

        # Only export events with security context
        if not security_context:
            return

        # Create audit entry
        audit_entry = {
            'timestamp': event['timestamp'],
            'event_id': event['event_id'],
            'event_type': event['event_type'],
            'agent_id': event['agent_id'],
            'requester_id': event.get('requester_id'),
            'security_context': security_context,
            'trace_id': event.get('trace_id')
        }

        self.file.write(json.dumps(audit_entry) + '\n')
        self.file.flush()

    def close(self) -> None:
        """Close audit log exporter."""
        self.file.close()


class MetricsExporter(TelemetryExporter):
    """
    Export events as metrics.

    Aggregates events into counters, gauges, and histograms.
    """

    def __init__(self):
        """Initialize metrics exporter."""
        self.counters = {}
        self.histograms = {}

    def export(self, event: Dict[str, Any]) -> None:
        """Export event as metrics."""
        event_type = event.get('event_type', 'unknown')

        # Increment counter for event type
        counter_key = f"agent.events.{event_type}"
        self.counters[counter_key] = self.counters.get(counter_key, 0) + 1

        # Track duration if present
        duration_ms = event.get('attributes', {}).get('duration_ms')
        if duration_ms is not None:
            histogram_key = f"agent.duration.{event_type}"
            if histogram_key not in self.histograms:
                self.histograms[histogram_key] = []
            self.histograms[histogram_key].append(duration_ms)

        # Track clearance escalations
        if event.get('security_context', {}).get('clearance_escalation'):
            escalation_key = "agent.clearance.escalations"
            self.counters[escalation_key] = self.counters.get(escalation_key, 0) + 1

        # Track policy violations
        violations = event.get('security_context', {}).get('policy_violations', [])
        if violations:
            violation_key = "agent.policy.violations"
            self.counters[violation_key] = self.counters.get(violation_key, 0) + len(violations)

    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics."""
        metrics = {
            'counters': self.counters.copy(),
            'histograms': {}
        }

        # Calculate histogram statistics
        for key, values in self.histograms.items():
            if values:
                metrics['histograms'][key] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values)
                }

        return metrics

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.counters.clear()
        self.histograms.clear()


class OTLPExporter(TelemetryExporter):
    """
    Export events to OpenTelemetry Protocol (OTLP) endpoint.

    Stub implementation - integrate with actual OTLP library in production.
    """

    def __init__(self, endpoint: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize OTLP exporter.

        Args:
            endpoint: OTLP endpoint URL
            headers: Optional HTTP headers
        """
        self.endpoint = endpoint
        self.headers = headers or {}
        logger.info(f"OTLP exporter initialized for {endpoint}")

    def export(self, event: Dict[str, Any]) -> None:
        """Export event to OTLP endpoint."""
        # TODO: Implement actual OTLP export
        # This is a stub - integrate with opentelemetry-exporter-otlp
        logger.debug(f"Would export to OTLP: {event['event_type']}")


# Exporter registry
EXPORTER_REGISTRY = {
    'console': ConsoleExporter,
    'file': FileExporter,
    'structured_log': StructuredLogExporter,
    'audit_log': AuditLogExporter,
    'metrics': MetricsExporter,
    'otlp': OTLPExporter
}


def create_exporter(exporter_type: str, **kwargs) -> TelemetryExporter:
    """
    Create an exporter instance.

    Args:
        exporter_type: Type of exporter
        **kwargs: Exporter-specific arguments

    Returns:
        Exporter instance
    """
    exporter_class = EXPORTER_REGISTRY.get(exporter_type)
    if not exporter_class:
        raise ValueError(f"Unknown exporter type: {exporter_type}")

    return exporter_class(**kwargs)
