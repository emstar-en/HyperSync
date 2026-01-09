"""Component Adapters

Provides adapter interfaces for components that need to communicate
but don't have direct dependencies.
"""

from typing import Protocol, Optional, Dict, Any
import numpy as np


class TelemetryAdapter(Protocol):
    """Telemetry interface for components"""

    def record_placement(self, service_id: str, tier: int, radius: float, duration_ms: float = 0):
        """Record placement metrics"""
        ...

    def record_curvature(self, node_id: str, curvature: float):
        """Record curvature metric"""
        ...

    def record_replication(self, service_id: str, rf: int, tier: int):
        """Record replication metrics"""
        ...

    def record_mesh(self, total_services: int, total_routes: int):
        """Record mesh metrics"""
        ...


class GovernanceAdapter(Protocol):
    """Governance interface for components"""

    def submit_change_request(self, change_type, requester: str, description: str, impact_assessment: Dict):
        """Submit change request"""
        ...

    def check_approval(self, request_id: str):
        """Check approval status"""
        ...

    def is_deployment_frozen(self, tier: int, service_id: Optional[str] = None) -> bool:
        """Check if deployment is frozen"""
        ...


class MeshAdapter(Protocol):
    """Mesh interface for components"""

    def register_service(self, service_name: str, position: np.ndarray, tier: int, capabilities: list) -> str:
        """Register service in mesh"""
        ...

    def discover_services(self, capability: Optional[str] = None, max_distance: Optional[float] = None):
        """Discover services"""
        ...

    def compute_route(self, source_id: str, dest_id: str):
        """Compute route between services"""
        ...


class PolicyAdapter(Protocol):
    """Policy interface for components"""

    def check_policy(self, action: str, context: Dict) -> bool:
        """Check if action is allowed by policy"""
        ...

    def enforce_policy(self, action: str, context: Dict):
        """Enforce policy for action"""
        ...


class ReplicationAdapter(Protocol):
    """Replication interface for components"""

    def plan_replicas(self, service_id: str, position: np.ndarray, tier: int, radius: float):
        """Plan replica placement"""
        ...

    def get_replica_set(self, service_id: str):
        """Get replica set for service"""
        ...


class SchedulerAdapter(Protocol):
    """Scheduler interface for components"""

    def update_curvature(self, node_id: str, load: float):
        """Update curvature based on load"""
        ...

    def check_autoscale(self, node_id: str) -> Optional[str]:
        """Check if autoscaling is needed"""
        ...


# Adapter injection helpers

def inject_telemetry(component, telemetry):
    """Inject telemetry adapter into component"""
    if hasattr(component, 'telemetry'):
        component.telemetry = telemetry
    elif hasattr(component, 'set_telemetry'):
        component.set_telemetry(telemetry)


def inject_governance(component, governance):
    """Inject governance adapter into component"""
    if hasattr(component, 'governance'):
        component.governance = governance
    elif hasattr(component, 'set_governance'):
        component.set_governance(governance)


def inject_mesh(component, mesh):
    """Inject mesh adapter into component"""
    if hasattr(component, 'mesh'):
        component.mesh = mesh
    elif hasattr(component, 'set_mesh'):
        component.set_mesh(mesh)


def inject_policy(component, policy):
    """Inject policy adapter into component"""
    if hasattr(component, 'policy'):
        component.policy = policy
    elif hasattr(component, 'set_policy'):
        component.set_policy(policy)
