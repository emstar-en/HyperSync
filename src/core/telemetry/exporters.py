"""Telemetry Exporters

Exports geometric metrics to Prometheus, OTLP, and other backends.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json

class PrometheusExporter:
    """Export metrics in Prometheus format"""

    def __init__(self):
        self.metrics = []

    def record_placement_metric(self, service_id: str, tier: int, radius: float):
        """Record placement metric"""
        self.metrics.append({
            'name': 'hypersync_placement_tier',
            'type': 'gauge',
            'value': tier,
            'labels': {'service_id': service_id},
            'timestamp': datetime.utcnow()
        })

        self.metrics.append({
            'name': 'hypersync_placement_radius',
            'type': 'gauge',
            'value': radius,
            'labels': {'service_id': service_id},
            'timestamp': datetime.utcnow()
        })

    def record_curvature_metric(self, node_id: str, curvature: float):
        """Record curvature metric"""
        self.metrics.append({
            'name': 'hypersync_curvature',
            'type': 'gauge',
            'value': curvature,
            'labels': {'node_id': node_id},
            'timestamp': datetime.utcnow()
        })

    def record_replication_metric(self, service_id: str, rf: int, tier: int):
        """Record replication factor metric"""
        self.metrics.append({
            'name': 'hypersync_replication_factor',
            'type': 'gauge',
            'value': rf,
            'labels': {'service_id': service_id, 'tier': str(tier)},
            'timestamp': datetime.utcnow()
        })

    def record_mesh_metric(self, total_services: int, total_routes: int):
        """Record mesh metrics"""
        self.metrics.append({
            'name': 'hypersync_mesh_services',
            'type': 'gauge',
            'value': total_services,
            'labels': {},
            'timestamp': datetime.utcnow()
        })

        self.metrics.append({
            'name': 'hypersync_mesh_routes',
            'type': 'gauge',
            'value': total_routes,
            'labels': {},
            'timestamp': datetime.utcnow()
        })

    def export(self) -> str:
        """Export metrics in Prometheus text format"""
        lines = []

        # Group by metric name
        by_name = {}
        for metric in self.metrics:
            name = metric['name']
            if name not in by_name:
                by_name[name] = []
            by_name[name].append(metric)

        # Format each metric
        for name, metrics in by_name.items():
            # Type declaration
            if metrics:
                lines.append(f"# TYPE {name} {metrics[0]['type']}")

            # Values
            for m in metrics:
                labels_str = ','.join(f'{k}="{v}"' for k, v in m['labels'].items())
                if labels_str:
                    lines.append(f"{name}{{{labels_str}}} {m['value']}")
                else:
                    lines.append(f"{name} {m['value']}")

        return '\n'.join(lines)


class OTLPExporter:
    """Export metrics in OpenTelemetry Protocol format"""

    def __init__(self):
        self.spans = []

    def record_placement_span(self, service_id: str, tier: int, radius: float,
                             duration_ms: float):
        """Record placement operation span"""
        span = {
            'name': 'hypersync.placement',
            'kind': 'INTERNAL',
            'start_time': datetime.utcnow().isoformat(),
            'duration_ms': duration_ms,
            'attributes': {
                'service.id': service_id,
                'placement.tier': tier,
                'placement.radius': radius
            }
        }
        self.spans.append(span)

    def record_routing_span(self, source: str, dest: str, route_length: float,
                           latency_ms: float):
        """Record routing operation span"""
        span = {
            'name': 'hypersync.routing',
            'kind': 'INTERNAL',
            'start_time': datetime.utcnow().isoformat(),
            'duration_ms': latency_ms,
            'attributes': {
                'route.source': source,
                'route.destination': dest,
                'route.length': route_length
            }
        }
        self.spans.append(span)

    def export(self) -> str:
        """Export spans in OTLP JSON format"""
        return json.dumps({
            'resourceSpans': [{
                'resource': {
                    'attributes': [
                        {'key': 'service.name', 'value': {'stringValue': 'hypersync-orchestrator'}}
                    ]
                },
                'scopeSpans': [{
                    'scope': {'name': 'hypersync'},
                    'spans': self.spans
                }]
            }]
        }, indent=2)


class ReceiptEnricher:
    """Enriches receipts with geometric metrics"""

    def enrich_deployment_receipt(self, receipt: Dict, position: 'np.ndarray',
                                  tier: int, radius: float) -> Dict:
        """Add geometric metrics to deployment receipt"""
        receipt['geometric_metrics'] = {
            'position': position.tolist() if hasattr(position, 'tolist') else position,
            'tier': tier,
            'radius': radius,
            'timestamp': datetime.utcnow().isoformat()
        }
        return receipt

    def enrich_routing_receipt(self, receipt: Dict, route_length: float,
                              waypoints: List) -> Dict:
        """Add routing metrics to receipt"""
        receipt['routing_metrics'] = {
            'route_length': route_length,
            'waypoint_count': len(waypoints),
            'timestamp': datetime.utcnow().isoformat()
        }
        return receipt

    def enrich_replication_receipt(self, receipt: Dict, rf: int,
                                   replica_positions: List) -> Dict:
        """Add replication metrics to receipt"""
        receipt['replication_metrics'] = {
            'replication_factor': rf,
            'replica_count': len(replica_positions),
            'timestamp': datetime.utcnow().isoformat()
        }
        return receipt


class TelemetryManager:
    """Central telemetry manager"""

    def __init__(self):
        self.prometheus = PrometheusExporter()
        self.otlp = OTLPExporter()
        self.enricher = ReceiptEnricher()

    def record_placement(self, service_id: str, tier: int, radius: float,
                        duration_ms: float = 0):
        """Record placement metrics"""
        self.prometheus.record_placement_metric(service_id, tier, radius)
        if duration_ms > 0:
            self.otlp.record_placement_span(service_id, tier, radius, duration_ms)

    def record_curvature(self, node_id: str, curvature: float):
        """Record curvature metric"""
        self.prometheus.record_curvature_metric(node_id, curvature)

    def record_replication(self, service_id: str, rf: int, tier: int):
        """Record replication metrics"""
        self.prometheus.record_replication_metric(service_id, rf, tier)

    def record_mesh(self, total_services: int, total_routes: int):
        """Record mesh metrics"""
        self.prometheus.record_mesh_metric(total_services, total_routes)

    def export_prometheus(self) -> str:
        """Export Prometheus metrics"""
        return self.prometheus.export()

    def export_otlp(self) -> str:
        """Export OTLP traces"""
        return self.otlp.export()
