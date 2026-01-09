"""
Monitoring & Observability Complete Wiring - Connects all monitoring.
"""
from hypersync.telemetry.pipeline_integration import get_telemetry_pipeline

class MonitoringIntegration:
    """Complete monitoring wiring."""

    def __init__(self):
        self.telemetry = get_telemetry_pipeline()
        self._dashboards = []
        self._alerting = None

    def register_dashboard(self, dashboard):
        """Register monitoring dashboard."""
        self._dashboards.append(dashboard)

    def set_alerting(self, alerting):
        """Set alerting system."""
        self._alerting = alerting

    def collect_and_monitor(self):
        """Collect metrics and update monitoring."""
        # Collect telemetry
        metrics = self.telemetry.collect_and_export()

        # Update dashboards
        for dashboard in self._dashboards:
            dashboard.update(metrics)

        # Check alerts
        if self._alerting:
            self._alerting.check_and_alert(metrics)

        return metrics
