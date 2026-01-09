"""
HyperSync TUI Metrics Exporter

Exports TUI metrics for Prometheus.
"""

import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


class MetricsExporter:
    """
    Metrics exporter.

    Exports TUI metrics in Prometheus format.
    """

    def __init__(self):
        self.metrics: Dict[str, float] = {}
        logger.info("MetricsExporter initialized")

    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record metric."""
        key = self._make_key(name, labels)
        self.metrics[key] = value

    def increment_counter(self, name: str, labels: Dict[str, str] = None):
        """Increment counter."""
        key = self._make_key(name, labels)
        self.metrics[key] = self.metrics.get(key, 0) + 1

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        for key, value in self.metrics.items():
            lines.append(f"{key} {value}")

        return "\n".join(lines)

    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Make metric key."""
        if labels:
            label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
            return f"{name}{{{label_str}}}"
        return name


# Global metrics exporter
_metrics_exporter = None


def get_metrics_exporter() -> MetricsExporter:
    """Get global metrics exporter."""
    global _metrics_exporter
    if _metrics_exporter is None:
        _metrics_exporter = MetricsExporter()
    return _metrics_exporter
