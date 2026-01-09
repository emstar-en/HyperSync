"""Curvature Field Manager

Ingests telemetry (load, latency, token spend) and adjusts local curvature
to influence routing and placement decisions.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
import time

@dataclass
class CurvatureField:
    """Curvature field at a point in the manifold"""
    position: np.ndarray
    base_curvature: float
    traffic_curvature: float
    load_curvature: float
    effective_curvature: float
    last_updated: datetime

    def compute_effective(self) -> float:
        """Compute effective curvature from components"""
        return self.base_curvature + self.traffic_curvature + self.load_curvature

@dataclass
class LoadMetrics:
    """Load metrics for a node"""
    node_id: str
    cpu_usage: float  # 0-1
    memory_usage: float  # 0-1
    network_usage: float  # 0-1
    request_rate: float  # requests/sec
    latency_p99: float  # milliseconds
    timestamp: datetime

@dataclass
class AutoscalePolicy:
    """Autoscaling policy"""
    tier: int
    scale_up_threshold: float = 0.8
    scale_down_threshold: float = 0.3
    cooldown_period: int = 300  # seconds
    min_replicas: int = 1
    max_replicas: int = 10
    target_utilization: float = 0.7

class CurvatureManager:
    """
    Manages curvature field based on system load and traffic.

    High load/traffic increases curvature, causing routes to avoid the region.
    Low load decreases curvature, attracting more traffic.
    """

    def __init__(self, 
                 base_curvature: float = -1.0,
                 traffic_weight: float = 0.5,
                 load_weight: float = 0.5):
        """
        Initialize curvature manager.

        Args:
            base_curvature: Base curvature value (negative for hyperbolic)
            traffic_weight: Weight for traffic-induced curvature
            load_weight: Weight for load-induced curvature
        """
        self.base_curvature = base_curvature
        self.traffic_weight = traffic_weight
        self.load_weight = load_weight

        # Curvature fields indexed by node_id
        self.fields: Dict[str, CurvatureField] = {}

        # Load metrics history
        self.metrics_history: Dict[str, List[LoadMetrics]] = {}
        self.history_window = timedelta(minutes=5)

        # Autoscale policies by tier
        self.autoscale_policies: Dict[int, AutoscalePolicy] = {}

        # Background update thread
        self._running = False
        self._update_thread = None

    def register_node(self, node_id: str, position: np.ndarray):
        """Register a node for curvature tracking"""
        self.fields[node_id] = CurvatureField(
            position=position,
            base_curvature=self.base_curvature,
            traffic_curvature=0.0,
            load_curvature=0.0,
            effective_curvature=self.base_curvature,
            last_updated=datetime.utcnow()
        )
        self.metrics_history[node_id] = []

    def update_metrics(self, metrics: LoadMetrics):
        """Update load metrics for a node"""
        if metrics.node_id not in self.metrics_history:
            self.metrics_history[metrics.node_id] = []

        # Add to history
        self.metrics_history[metrics.node_id].append(metrics)

        # Trim old metrics
        cutoff = datetime.utcnow() - self.history_window
        self.metrics_history[metrics.node_id] = [
            m for m in self.metrics_history[metrics.node_id]
            if m.timestamp > cutoff
        ]

        # Update curvature field
        self._update_curvature_field(metrics.node_id)

    def _update_curvature_field(self, node_id: str):
        """Update curvature field based on recent metrics"""
        if node_id not in self.fields:
            return

        field = self.fields[node_id]
        history = self.metrics_history.get(node_id, [])

        if not history:
            return

        # Compute average load over window
        avg_cpu = np.mean([m.cpu_usage for m in history])
        avg_memory = np.mean([m.memory_usage for m in history])
        avg_network = np.mean([m.network_usage for m in history])
        avg_load = (avg_cpu + avg_memory + avg_network) / 3.0

        # Compute traffic intensity
        avg_request_rate = np.mean([m.request_rate for m in history])
        max_request_rate = 1000.0  # Normalize to this
        traffic_intensity = min(avg_request_rate / max_request_rate, 1.0)

        # Update curvature components
        # High load/traffic increases curvature (makes region less attractive)
        field.load_curvature = self.load_weight * avg_load
        field.traffic_curvature = self.traffic_weight * traffic_intensity
        field.effective_curvature = field.compute_effective()
        field.last_updated = datetime.utcnow()

    def get_effective_curvature(self, node_id: str) -> float:
        """Get effective curvature for a node"""
        if node_id not in self.fields:
            return self.base_curvature
        return self.fields[node_id].effective_curvature

    def get_curvature_gradient(self, position: np.ndarray) -> np.ndarray:
        """
        Compute curvature gradient at a position.

        Used for routing decisions - routes follow negative gradient
        (toward lower curvature = less loaded regions).
        """
        if not self.fields:
            return np.zeros_like(position)

        # Compute weighted gradient based on nearby nodes
        gradient = np.zeros_like(position)
        total_weight = 0.0

        for node_id, field in self.fields.items():
            # Distance to this node
            diff = position - field.position
            distance = np.linalg.norm(diff)

            if distance < 1e-6:
                continue

            # Weight by inverse distance
            weight = 1.0 / (distance + 0.1)

            # Gradient contribution (points toward high curvature)
            gradient += weight * field.effective_curvature * diff / distance
            total_weight += weight

        if total_weight > 0:
            gradient /= total_weight

        return gradient

    def set_autoscale_policy(self, tier: int, policy: AutoscalePolicy):
        """Set autoscaling policy for a tier"""
        self.autoscale_policies[tier] = policy

    def check_autoscale(self, node_id: str, tier: int) -> Optional[str]:
        """
        Check if autoscaling action is needed.

        Returns:
            'scale_up', 'scale_down', or None
        """
        if tier not in self.autoscale_policies:
            return None

        policy = self.autoscale_policies[tier]
        history = self.metrics_history.get(node_id, [])

        if not history:
            return None

        # Check recent metrics
        recent = history[-10:]  # Last 10 samples
        avg_load = np.mean([
            (m.cpu_usage + m.memory_usage + m.network_usage) / 3.0
            for m in recent
        ])

        if avg_load > policy.scale_up_threshold:
            return 'scale_up'
        elif avg_load < policy.scale_down_threshold:
            return 'scale_down'

        return None

    def start_background_updates(self, interval: float = 10.0):
        """Start background thread for curvature updates"""
        if self._running:
            return

        self._running = True

        def update_loop():
            while self._running:
                # Update all curvature fields
                for node_id in list(self.fields.keys()):
                    self._update_curvature_field(node_id)

                time.sleep(interval)

        self._update_thread = threading.Thread(target=update_loop, daemon=True)
        self._update_thread.start()

    def stop_background_updates(self):
        """Stop background updates"""
        self._running = False
        if self._update_thread:
            self._update_thread.join(timeout=5.0)

    def get_status(self) -> Dict:
        """Get current curvature manager status"""
        return {
            'nodes_tracked': len(self.fields),
            'fields': {
                node_id: {
                    'effective_curvature': field.effective_curvature,
                    'load_curvature': field.load_curvature,
                    'traffic_curvature': field.traffic_curvature,
                    'last_updated': field.last_updated.isoformat()
                }
                for node_id, field in self.fields.items()
            },
            'autoscale_policies': {
                tier: {
                    'scale_up_threshold': policy.scale_up_threshold,
                    'scale_down_threshold': policy.scale_down_threshold,
                    'min_replicas': policy.min_replicas,
                    'max_replicas': policy.max_replicas
                }
                for tier, policy in self.autoscale_policies.items()
            }
        }


class SchedulerIntegration:
    """
    Integrates curvature manager with ProcessManager and SandboxManager.

    Enforces tier budgets and triggers autoscale actions.
    """

    def __init__(self, curvature_manager: CurvatureManager):
        self.curvature_manager = curvature_manager

        # Tier budgets (CPU cores)
        self.tier_budgets = {
            0: 1000,
            1: 640,
            2: 320,
            3: 160,
            4: 80
        }

        # Current usage
        self.tier_usage = {tier: 0.0 for tier in self.tier_budgets.keys()}

    def can_schedule(self, tier: int, cpu_required: float) -> bool:
        """Check if scheduling is allowed within tier budget"""
        budget = self.tier_budgets.get(tier, 0)
        current = self.tier_usage.get(tier, 0)
        return (current + cpu_required) <= budget

    def schedule_process(self, node_id: str, tier: int, cpu_required: float) -> bool:
        """
        Schedule a process with tier budget enforcement.

        Returns:
            True if scheduled, False if budget exceeded
        """
        if not self.can_schedule(tier, cpu_required):
            # Try to trigger autoscale
            action = self.curvature_manager.check_autoscale(node_id, tier)
            if action == 'scale_up':
                # Trigger scale up (implementation depends on orchestrator)
                pass
            return False

        # Update usage
        self.tier_usage[tier] += cpu_required
        return True

    def release_process(self, tier: int, cpu_used: float):
        """Release process resources"""
        self.tier_usage[tier] = max(0, self.tier_usage[tier] - cpu_used)

    def get_tier_utilization(self, tier: int) -> float:
        """Get current tier utilization (0-1)"""
        budget = self.tier_budgets.get(tier, 1)
        usage = self.tier_usage.get(tier, 0)
        return usage / budget if budget > 0 else 0.0
