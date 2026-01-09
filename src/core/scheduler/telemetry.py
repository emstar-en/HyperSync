"""Scheduler telemetry integration"""
from typing import Dict
from datetime import datetime
from hypersync.scheduler.curvature_manager import CurvatureManager, LoadMetrics

class SchedulerTelemetry:
    """Telemetry for scheduler and curvature manager"""

    def __init__(self, curvature_manager: CurvatureManager):
        self.curvature_manager = curvature_manager
        self.events = []

    def emit_curvature_update(self, node_id: str, old_curvature: float, 
                             new_curvature: float):
        """Emit curvature update event"""
        event = {
            'type': 'curvature.updated',
            'timestamp': datetime.utcnow().isoformat(),
            'node_id': node_id,
            'old_curvature': old_curvature,
            'new_curvature': new_curvature,
            'delta': new_curvature - old_curvature
        }
        self.events.append(event)
        # In production, send to telemetry backend

    def emit_autoscale_action(self, node_id: str, tier: int, action: str):
        """Emit autoscale action event"""
        event = {
            'type': 'autoscale.action',
            'timestamp': datetime.utcnow().isoformat(),
            'node_id': node_id,
            'tier': tier,
            'action': action
        }
        self.events.append(event)

    def emit_tier_migration(self, node_id: str, from_tier: int, to_tier: int):
        """Emit tier migration event"""
        event = {
            'type': 'tier.migration',
            'timestamp': datetime.utcnow().isoformat(),
            'node_id': node_id,
            'from_tier': from_tier,
            'to_tier': to_tier
        }
        self.events.append(event)

    def get_metrics(self) -> Dict:
        """Get current scheduler metrics"""
        status = self.curvature_manager.get_status()
        return {
            'nodes_tracked': status['nodes_tracked'],
            'avg_curvature': sum(
                f['effective_curvature'] 
                for f in status['fields'].values()
            ) / max(len(status['fields']), 1),
            'recent_events': self.events[-100:]
        }
