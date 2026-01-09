"""
Operator Dashboard and Monitoring Interface
Provides monitoring, alerting, and chaos testing for HyperSync environments.
"""

import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import random

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class Alert:
    """Represents an alert"""
    alert_id: str
    severity: AlertSeverity
    title: str
    message: str
    source: str
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False

    def to_dict(self) -> dict:
        return {
            "alert_id": self.alert_id,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "resolved": self.resolved
        }


@dataclass
class Metric:
    """Represents a metric"""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels
        }


class AlertManager:
    """Manages alerts and notifications"""

    def __init__(self):
        """Initialize alert manager"""
        self.alerts: List[Alert] = []
        self.alert_callbacks: List[Callable[[Alert], None]] = []

        logger.info("AlertManager initialized")

    def add_callback(self, callback: Callable[[Alert], None]):
        """Add alert callback"""
        self.alert_callbacks.append(callback)

    def create_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        source: str
    ) -> Alert:
        """
        Create an alert.

        Args:
            severity: Alert severity
            title: Alert title
            message: Alert message
            source: Alert source

        Returns:
            Alert object
        """
        alert_id = f"alert-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        alert = Alert(
            alert_id=alert_id,
            severity=severity,
            title=title,
            message=message,
            source=source,
            timestamp=datetime.utcnow()
        )

        self.alerts.append(alert)
        logger.info(f"Alert created: {alert_id} [{severity.value}] {title}")

        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")

        return alert

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert acknowledged: {alert_id}")
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                logger.info(f"Alert resolved: {alert_id}")
                return True
        return False

    def get_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        unresolved_only: bool = False
    ) -> List[Alert]:
        """Get alerts"""
        alerts = self.alerts

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]

        return alerts


class MetricsCollector:
    """Collects and stores metrics"""

    def __init__(self):
        """Initialize metrics collector"""
        self.metrics: List[Metric] = []
        self.retention_hours = 24

        logger.info("MetricsCollector initialized")

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Record a metric.

        Args:
            name: Metric name
            value: Metric value
            metric_type: Type of metric
            labels: Optional labels
        """
        metric = Metric(
            name=name,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {}
        )

        self.metrics.append(metric)

        # Clean old metrics
        self._cleanup_old_metrics()

    def get_metrics(
        self,
        name: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[Metric]:
        """Get metrics"""
        metrics = self.metrics

        if name:
            metrics = [m for m in metrics if m.name == name]

        if since:
            metrics = [m for m in metrics if m.timestamp > since]

        return metrics

    def get_latest_value(self, name: str) -> Optional[float]:
        """Get latest value for a metric"""
        metrics = [m for m in self.metrics if m.name == name]
        if metrics:
            return metrics[-1].value
        return None

    def _cleanup_old_metrics(self):
        """Remove old metrics"""
        cutoff = datetime.utcnow() - timedelta(hours=self.retention_hours)
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff]


class ChaosValidator:
    """Chaos testing and validation"""

    def __init__(self):
        """Initialize chaos validator"""
        self.chaos_tests: List[Dict] = []

        logger.info("ChaosValidator initialized")

    def inject_file_corruption(self, path: str) -> bool:
        """
        Inject file corruption for testing.

        Args:
            path: File to corrupt

        Returns:
            True if injected
        """
        logger.warning(f"CHAOS: Injecting file corruption: {path}")

        try:
            import os
            if os.path.exists(path):
                # Corrupt file by appending garbage
                with open(path, 'ab') as f:
                    f.write(b'\x00\xFF\xDE\xAD\xBE\xEF')

                self.chaos_tests.append({
                    "type": "file_corruption",
                    "target": path,
                    "timestamp": datetime.utcnow().isoformat()
                })

                return True
        except Exception as e:
            logger.error(f"Chaos injection failed: {e}")

        return False

    def inject_latency(self, duration_ms: int) -> bool:
        """
        Inject artificial latency.

        Args:
            duration_ms: Latency in milliseconds

        Returns:
            True if injected
        """
        logger.warning(f"CHAOS: Injecting {duration_ms}ms latency")

        import time
        time.sleep(duration_ms / 1000.0)

        self.chaos_tests.append({
            "type": "latency",
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat()
        })

        return True

    def inject_resource_exhaustion(self, resource: str) -> bool:
        """
        Simulate resource exhaustion.

        Args:
            resource: Resource to exhaust (memory, disk, cpu)

        Returns:
            True if injected
        """
        logger.warning(f"CHAOS: Simulating {resource} exhaustion")

        self.chaos_tests.append({
            "type": "resource_exhaustion",
            "resource": resource,
            "timestamp": datetime.utcnow().isoformat()
        })

        return True

    def inject_random_failure(self, probability: float = 0.1) -> bool:
        """
        Randomly inject failures.

        Args:
            probability: Probability of failure (0.0-1.0)

        Returns:
            True if failure injected
        """
        if random.random() < probability:
            logger.warning("CHAOS: Random failure injected")

            self.chaos_tests.append({
                "type": "random_failure",
                "probability": probability,
                "timestamp": datetime.utcnow().isoformat()
            })

            return True

        return False

    def get_chaos_history(self) -> List[Dict]:
        """Get chaos test history"""
        return self.chaos_tests


class OperatorDashboard:
    """Main operator dashboard"""

    def __init__(self):
        """Initialize operator dashboard"""
        self.alert_manager = AlertManager()
        self.metrics_collector = MetricsCollector()
        self.chaos_validator = ChaosValidator()

        logger.info("OperatorDashboard initialized")

    def get_system_status(self) -> Dict:
        """Get overall system status"""
        alerts = self.alert_manager.get_alerts(unresolved_only=True)
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        error_alerts = [a for a in alerts if a.severity == AlertSeverity.ERROR]

        # Determine overall status
        if critical_alerts:
            status = "critical"
        elif error_alerts:
            status = "degraded"
        elif alerts:
            status = "warning"
        else:
            status = "healthy"

        return {
            "status": status,
            "total_alerts": len(alerts),
            "critical_alerts": len(critical_alerts),
            "error_alerts": len(error_alerts),
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_dashboard_data(self) -> Dict:
        """Get complete dashboard data"""
        return {
            "system_status": self.get_system_status(),
            "recent_alerts": [a.to_dict() for a in self.alert_manager.get_alerts()[-10:]],
            "metrics_summary": {
                "total_metrics": len(self.metrics_collector.metrics),
                "retention_hours": self.metrics_collector.retention_hours
            },
            "chaos_tests": len(self.chaos_validator.chaos_tests)
        }


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    dashboard = OperatorDashboard()

    # Create some alerts
    dashboard.alert_manager.create_alert(
        AlertSeverity.WARNING,
        "High CPU Usage",
        "CPU usage is above 80%",
        "system-monitor"
    )

    dashboard.alert_manager.create_alert(
        AlertSeverity.ERROR,
        "Disk Space Low",
        "Disk space is below 10%",
        "disk-monitor"
    )

    # Record metrics
    dashboard.metrics_collector.record_metric("cpu_usage", 85.5)
    dashboard.metrics_collector.record_metric("memory_usage", 72.3)
    dashboard.metrics_collector.record_metric("disk_usage", 92.1)

    # Get system status
    status = dashboard.get_system_status()
    print(f"System Status: {status['status']}")
    print(f"Total Alerts: {status['total_alerts']}")

    # Get dashboard data
    data = dashboard.get_dashboard_data()
    print(f"\nDashboard Data:")
    print(f"  Status: {data['system_status']['status']}")
    print(f"  Recent Alerts: {len(data['recent_alerts'])}")
    print(f"  Total Metrics: {data['metrics_summary']['total_metrics']}")
