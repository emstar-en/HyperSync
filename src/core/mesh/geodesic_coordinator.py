"""Geodesic Service Mesh Runtime

Implements service mesh using hyperbolic geodesics for routing and discovery.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class ServiceEndpoint:
    """Service endpoint in the mesh"""
    service_id: str
    service_name: str
    position: np.ndarray
    tier: int
    capabilities: List[str]
    health_status: str = "healthy"  # healthy, degraded, unhealthy
    last_seen: datetime = None

    def __post_init__(self):
        if self.last_seen is None:
            self.last_seen = datetime.utcnow()

@dataclass
class GeodesicRoute:
    """Route between services"""
    route_id: str
    source: str
    destination: str
    waypoints: List[np.ndarray]
    length: float
    estimated_latency: float
    computed_at: datetime

    def __post_init__(self):
        if not hasattr(self, 'computed_at') or self.computed_at is None:
            self.computed_at = datetime.utcnow()

@dataclass
class TrafficPolicy:
    """Traffic shaping policy"""
    service_id: str
    rate_limit: Optional[float] = None  # requests/sec
    circuit_breaker_threshold: float = 0.5  # error rate
    circuit_breaker_timeout: int = 30  # seconds
    canary_weight: float = 0.0  # 0-1 for canary deployments
    curvature_adjustment: float = 0.0  # manual curvature override

class GeodesicMeshCoordinator:
    """
    Coordinates service mesh using hyperbolic geodesics.

    Services are automatically discovered based on their manifold positions.
    Routes are computed as geodesics, with load balancing via perturbed paths.
    """

    def __init__(self, mesh_radius: float = 3.0):
        """
        Initialize mesh coordinator.

        Args:
            mesh_radius: Services within this hyperbolic distance are "neighbors"
        """
        self.mesh_radius = mesh_radius

        # Service registry
        self.services: Dict[str, ServiceEndpoint] = {}

        # Route cache
        self.route_cache: Dict[Tuple[str, str], GeodesicRoute] = {}

        # Traffic policies
        self.traffic_policies: Dict[str, TrafficPolicy] = {}

        # Circuit breaker states
        self.circuit_breakers: Dict[str, Dict] = {}

    def register_service(self, service_name: str, position: np.ndarray,
                        tier: int, capabilities: List[str]) -> str:
        """
        Register a service in the mesh.

        Args:
            service_name: Service name
            position: Position in manifold
            tier: Deployment tier
            capabilities: Service capabilities

        Returns:
            Service ID
        """
        service_id = str(uuid.uuid4())

        endpoint = ServiceEndpoint(
            service_id=service_id,
            service_name=service_name,
            position=position,
            tier=tier,
            capabilities=capabilities
        )

        self.services[service_id] = endpoint

        # Initialize circuit breaker
        self.circuit_breakers[service_id] = {
            'state': 'closed',  # closed, open, half_open
            'failure_count': 0,
            'last_failure': None
        }

        return service_id

    def deregister_service(self, service_id: str):
        """Remove service from mesh"""
        if service_id in self.services:
            del self.services[service_id]

        # Clear route cache entries
        self.route_cache = {
            k: v for k, v in self.route_cache.items()
            if k[0] != service_id and k[1] != service_id
        }

    def discover_services(self, capability: Optional[str] = None,
                         max_distance: Optional[float] = None,
                         from_position: Optional[np.ndarray] = None) -> List[ServiceEndpoint]:
        """
        Discover services in the mesh.

        Args:
            capability: Filter by capability
            max_distance: Maximum hyperbolic distance
            from_position: Reference position for distance calculation

        Returns:
            List of matching services
        """
        results = []

        for service in self.services.values():
            # Filter by capability
            if capability and capability not in service.capabilities:
                continue

            # Filter by distance
            if max_distance and from_position is not None:
                distance = self._hyperbolic_distance(from_position, service.position)
                if distance > max_distance:
                    continue

            # Filter by health
            if service.health_status == "unhealthy":
                continue

            results.append(service)

        # Sort by distance if reference position provided
        if from_position is not None:
            results.sort(key=lambda s: self._hyperbolic_distance(from_position, s.position))

        return results

    def compute_route(self, source_id: str, dest_id: str,
                     use_cache: bool = True) -> Optional[GeodesicRoute]:
        """
        Compute geodesic route between services.

        Args:
            source_id: Source service ID
            dest_id: Destination service ID
            use_cache: Use cached route if available

        Returns:
            Geodesic route or None if services not found
        """
        # Check cache
        cache_key = (source_id, dest_id)
        if use_cache and cache_key in self.route_cache:
            cached = self.route_cache[cache_key]
            # Cache valid for 60 seconds
            if (datetime.utcnow() - cached.computed_at).seconds < 60:
                return cached

        # Get services
        if source_id not in self.services or dest_id not in self.services:
            return None

        source = self.services[source_id]
        dest = self.services[dest_id]

        # Compute geodesic
        waypoints = self._compute_geodesic_waypoints(
            source.position, dest.position, num_points=10
        )

        # Compute length
        length = self._hyperbolic_distance(source.position, dest.position)

        # Estimate latency (simplified: 1ms per hyperbolic unit + tier penalty)
        tier_penalty = abs(source.tier - dest.tier) * 5  # 5ms per tier difference
        estimated_latency = length + tier_penalty

        route = GeodesicRoute(
            route_id=str(uuid.uuid4()),
            source=source_id,
            destination=dest_id,
            waypoints=waypoints,
            length=length,
            estimated_latency=estimated_latency,
            computed_at=datetime.utcnow()
        )

        # Cache route
        self.route_cache[cache_key] = route

        return route

    def load_balance_route(self, source_id: str, dest_id: str,
                          num_paths: int = 3, epsilon: float = 0.5) -> List[GeodesicRoute]:
        """
        Generate multiple near-geodesic paths for load balancing.

        Args:
            source_id: Source service ID
            dest_id: Destination service ID
            num_paths: Number of alternative paths
            epsilon: Maximum path length increase (hyperbolic units)

        Returns:
            List of routes sorted by estimated cost
        """
        # Get primary geodesic
        primary = self.compute_route(source_id, dest_id)
        if not primary:
            return []

        routes = [primary]

        # Generate perturbed paths
        source = self.services[source_id]
        dest = self.services[dest_id]

        for i in range(1, num_paths):
            # Perturb intermediate points
            perturbed_waypoints = []
            for wp in primary.waypoints:
                # Add random perturbation
                perturbation = np.random.randn(*wp.shape) * epsilon / len(primary.waypoints)
                perturbed = wp + perturbation
                # Project back to hyperboloid
                perturbed = self._project_to_hyperboloid(perturbed)
                perturbed_waypoints.append(perturbed)

            # Compute perturbed length
            perturbed_length = sum(
                self._hyperbolic_distance(perturbed_waypoints[j], perturbed_waypoints[j+1])
                for j in range(len(perturbed_waypoints) - 1)
            )

            # Only include if within epsilon of primary
            if perturbed_length <= primary.length + epsilon:
                route = GeodesicRoute(
                    route_id=str(uuid.uuid4()),
                    source=source_id,
                    destination=dest_id,
                    waypoints=perturbed_waypoints,
                    length=perturbed_length,
                    estimated_latency=perturbed_length + abs(source.tier - dest.tier) * 5,
                    computed_at=datetime.utcnow()
                )
                routes.append(route)

        # Sort by estimated latency
        routes.sort(key=lambda r: r.estimated_latency)

        return routes

    def set_traffic_policy(self, service_id: str, policy: TrafficPolicy):
        """Set traffic policy for a service"""
        self.traffic_policies[service_id] = policy

    def check_rate_limit(self, service_id: str, current_rate: float) -> bool:
        """
        Check if request is within rate limit.

        Returns:
            True if allowed, False if rate limited
        """
        if service_id not in self.traffic_policies:
            return True

        policy = self.traffic_policies[service_id]
        if policy.rate_limit is None:
            return True

        return current_rate <= policy.rate_limit

    def check_circuit_breaker(self, service_id: str) -> bool:
        """
        Check circuit breaker state.

        Returns:
            True if circuit is closed (requests allowed)
        """
        if service_id not in self.circuit_breakers:
            return True

        breaker = self.circuit_breakers[service_id]

        if breaker['state'] == 'open':
            # Check if timeout expired
            if breaker['last_failure']:
                policy = self.traffic_policies.get(service_id)
                timeout = policy.circuit_breaker_timeout if policy else 30

                elapsed = (datetime.utcnow() - breaker['last_failure']).seconds
                if elapsed > timeout:
                    # Move to half-open
                    breaker['state'] = 'half_open'
                    breaker['failure_count'] = 0
                    return True

            return False

        return True

    def record_request_result(self, service_id: str, success: bool):
        """Record request result for circuit breaker"""
        if service_id not in self.circuit_breakers:
            return

        breaker = self.circuit_breakers[service_id]
        policy = self.traffic_policies.get(service_id)

        if not success:
            breaker['failure_count'] += 1
            breaker['last_failure'] = datetime.utcnow()

            # Check threshold
            if policy and breaker['failure_count'] >= policy.circuit_breaker_threshold * 10:
                breaker['state'] = 'open'
        else:
            # Success in half-open state closes circuit
            if breaker['state'] == 'half_open':
                breaker['state'] = 'closed'
                breaker['failure_count'] = 0

    def get_mesh_topology(self) -> Dict:
        """Get current mesh topology"""
        # Build neighbor graph
        neighbors = {}

        for sid, service in self.services.items():
            neighbors[sid] = []

            for other_sid, other in self.services.items():
                if sid == other_sid:
                    continue

                distance = self._hyperbolic_distance(service.position, other.position)
                if distance <= self.mesh_radius:
                    neighbors[sid].append({
                        'service_id': other_sid,
                        'service_name': other.service_name,
                        'distance': distance
                    })

        return {
            'services': {
                sid: {
                    'name': s.service_name,
                    'tier': s.tier,
                    'capabilities': s.capabilities,
                    'health': s.health_status
                }
                for sid, s in self.services.items()
            },
            'neighbors': neighbors,
            'total_services': len(self.services),
            'total_routes_cached': len(self.route_cache)
        }

    # Helper methods

    def _hyperbolic_distance(self, x: np.ndarray, y: np.ndarray) -> float:
        """Compute hyperbolic distance (hyperboloid model)"""
        lorentz_product = -x[0] * y[0] + np.dot(x[1:], y[1:])
        return np.arccosh(max(-lorentz_product, 1.0 + 1e-10))

    def _project_to_hyperboloid(self, p: np.ndarray) -> np.ndarray:
        """Project point to hyperboloid"""
        spatial = p[1:]
        x0 = np.sqrt(1 + np.dot(spatial, spatial))
        return np.concatenate([[x0], spatial])

    def _compute_geodesic_waypoints(self, x: np.ndarray, y: np.ndarray,
                                   num_points: int = 10) -> List[np.ndarray]:
        """Compute waypoints along geodesic"""
        d = self._hyperbolic_distance(x, y)

        if d < 1e-10:
            return [x.copy()]

        waypoints = []
        sinh_d = np.sinh(d)

        for i in range(num_points + 1):
            t = i / num_points
            coeff_x = np.sinh((1 - t) * d) / sinh_d
            coeff_y = np.sinh(t * d) / sinh_d
            waypoint = coeff_x * x + coeff_y * y
            waypoints.append(waypoint)

        return waypoints
