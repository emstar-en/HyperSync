"""
Telemetry Pipeline Wiring - Connects all collectors to aggregator and exporters.
"""
import logging

logger = logging.getLogger(__name__)

class TelemetryPipelineIntegration:
    """Wires complete telemetry pipeline."""

    def __init__(self):
        self._collectors = []
        self._aggregator = None
        self._exporters = []

    def register_collector(self, collector):
        """Register telemetry collector."""
        self._collectors.append(collector)
        logger.info(f"Registered collector: {collector.__class__.__name__}")

    def set_aggregator(self, aggregator):
        """Set telemetry aggregator."""
        self._aggregator = aggregator

    def register_exporter(self, exporter):
        """Register telemetry exporter."""
        self._exporters.append(exporter)
        logger.info(f"Registered exporter: {exporter.__class__.__name__}")

    def collect_and_export(self):
        """Collect from all sources and export."""
        all_metrics = {}

        # Collect from all collectors
        for collector in self._collectors:
            try:
                metrics = collector.collect()
                all_metrics.update(metrics)
            except Exception as e:
                logger.error(f"Collector failed: {e}")

        # Aggregate
        if self._aggregator:
            all_metrics = self._aggregator.aggregate(all_metrics)

        # Export to all exporters
        for exporter in self._exporters:
            try:
                exporter.export(all_metrics)
            except Exception as e:
                logger.error(f"Exporter failed: {e}")

        return all_metrics

# Global telemetry pipeline
_telemetry_pipeline = None

def get_telemetry_pipeline():
    """Get global telemetry pipeline."""
    global _telemetry_pipeline
    if _telemetry_pipeline is None:
        _telemetry_pipeline = TelemetryPipelineIntegration()
    return _telemetry_pipeline
