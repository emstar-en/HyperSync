"""
Example: Operator Dashboard Usage
"""

import logging
import time
from hypersync.operator.dashboard import (
    OperatorDashboard,
    AlertSeverity
)

logging.basicConfig(level=logging.INFO)


def main():
    print("=" * 80)
    print("Operator Dashboard Example")
    print("=" * 80)

    dashboard = OperatorDashboard()

    # Simulate system monitoring
    print("\n1. Recording System Metrics")
    print("-" * 80)

    dashboard.metrics_collector.record_metric("cpu_usage", 45.2)
    dashboard.metrics_collector.record_metric("memory_usage", 62.8)
    dashboard.metrics_collector.record_metric("disk_usage", 38.5)
    dashboard.metrics_collector.record_metric("network_throughput", 125.3)

    print("Metrics recorded:")
    for name in ["cpu_usage", "memory_usage", "disk_usage", "network_throughput"]:
        value = dashboard.metrics_collector.get_latest_value(name)
        print(f"  {name}: {value}")

    # Create alerts
    print("\n2. Creating Alerts")
    print("-" * 80)

    alert1 = dashboard.alert_manager.create_alert(
        AlertSeverity.INFO,
        "System Started",
        "HyperSync system started successfully",
        "system"
    )
    print(f"Created INFO alert: {alert1.alert_id}")

    alert2 = dashboard.alert_manager.create_alert(
        AlertSeverity.WARNING,
        "High Memory Usage",
        "Memory usage is above 60%",
        "memory-monitor"
    )
    print(f"Created WARNING alert: {alert2.alert_id}")

    alert3 = dashboard.alert_manager.create_alert(
        AlertSeverity.ERROR,
        "Agent Timeout",
        "Agent agent-1 did not respond within timeout",
        "agent-monitor"
    )
    print(f"Created ERROR alert: {alert3.alert_id}")

    # System status
    print("\n3. System Status")
    print("-" * 80)

    status = dashboard.get_system_status()
    print(f"Overall Status: {status['status'].upper()}")
    print(f"Total Alerts: {status['total_alerts']}")
    print(f"Critical Alerts: {status['critical_alerts']}")
    print(f"Error Alerts: {status['error_alerts']}")

    # Acknowledge and resolve
    print("\n4. Alert Management")
    print("-" * 80)

    print(f"Acknowledging alert: {alert2.alert_id}")
    dashboard.alert_manager.acknowledge_alert(alert2.alert_id)

    print(f"Resolving alert: {alert1.alert_id}")
    dashboard.alert_manager.resolve_alert(alert1.alert_id)

    # Chaos testing
    print("\n5. Chaos Testing")
    print("-" * 80)

    print("Injecting latency...")
    dashboard.chaos_validator.inject_latency(duration_ms=50)

    print("Simulating resource exhaustion...")
    dashboard.chaos_validator.inject_resource_exhaustion("cpu")

    print("Testing random failures...")
    for i in range(5):
        if dashboard.chaos_validator.inject_random_failure(probability=0.3):
            print(f"  Failure injected on attempt {i+1}")

    chaos_history = dashboard.chaos_validator.get_chaos_history()
    print(f"Total chaos tests: {len(chaos_history)}")

    # Dashboard data
    print("\n6. Complete Dashboard View")
    print("-" * 80)

    data = dashboard.get_dashboard_data()

    print(f"System Status: {data['system_status']['status']}")
    print(f"\nRecent Alerts ({len(data['recent_alerts'])}):")
    for alert in data['recent_alerts'][-5:]:
        status_str = "✓" if alert['resolved'] else "○"
        print(f"  {status_str} [{alert['severity']}] {alert['title']}")

    print(f"\nMetrics:")
    print(f"  Total: {data['metrics_summary']['total_metrics']}")
    print(f"  Retention: {data['metrics_summary']['retention_hours']} hours")

    print(f"\nChaos Tests: {data['chaos_tests']}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
