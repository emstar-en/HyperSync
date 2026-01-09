"""Boundary Edge & CDN Manager

Implements Poincaré boundary compression for edge computing and CDN operations.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

@dataclass
class EdgeNode:
    """Edge node near boundary"""
    node_id: str
    position: np.ndarray  # Poincaré disk coordinates
    boundary_position: np.ndarray  # Projected to boundary
    angular_position: float  # Angle on boundary
    region: str
    gateway_id: Optional[str] = None
    cache_size: int = 0  # MB
    cache_used: int = 0  # MB

@dataclass
class EdgeGateway:
    """Edge gateway (cluster center on boundary)"""
    gateway_id: str
    boundary_position: np.ndarray
    angular_position: float
    region: str
    member_nodes: List[str]
    total_capacity: int  # MB
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class CacheEntry:
    """CDN cache entry"""
    key: str
    value: bytes
    size: int  # bytes
    radius: float  # Origin distance (for eviction)
    access_count: int = 0
    last_accessed: datetime = None
    created_at: datetime = None

    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = datetime.utcnow()
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class BoundaryEdgeManager:
    """
    Manages edge nodes using Poincaré boundary compression.

    Nodes near boundary (||x|| → 1) are logically close even if
    physically distributed, enabling efficient edge computing.
    """

    def __init__(self, boundary_threshold: float = 0.95):
        """
        Initialize boundary edge manager.

        Args:
            boundary_threshold: Nodes with ||x|| > threshold are "edge"
        """
        self.boundary_threshold = boundary_threshold

        # Edge nodes registry
        self.edge_nodes: Dict[str, EdgeNode] = {}

        # Edge gateways
        self.gateways: Dict[str, EdgeGateway] = {}

        # CDN cache
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_capacity = 10 * 1024 * 1024 * 1024  # 10GB default
        self.cache_used = 0

    def project_to_boundary(self, position: np.ndarray) -> np.ndarray:
        """
        Project position to Poincaré disk boundary.

        Args:
            position: Position in Poincaré disk

        Returns:
            Position on boundary (||x|| = 1)
        """
        norm = np.linalg.norm(position)
        if norm < 1e-10:
            return np.array([1.0, 0.0, 0.0])[:len(position)]

        return position / norm

    def compute_angular_position(self, boundary_pos: np.ndarray) -> float:
        """
        Compute angular position on boundary.

        Args:
            boundary_pos: Position on boundary

        Returns:
            Angle in radians [0, 2π)
        """
        # Use first two spatial dimensions
        x, y = boundary_pos[0], boundary_pos[1] if len(boundary_pos) > 1 else 0
        angle = np.arctan2(y, x)
        if angle < 0:
            angle += 2 * np.pi
        return angle

    def angular_distance(self, angle1: float, angle2: float) -> float:
        """
        Compute angular distance on boundary circle.

        Returns minimum arc length.
        """
        diff = abs(angle1 - angle2)
        return min(diff, 2 * np.pi - diff)

    def register_edge_node(self, node_id: str, position: np.ndarray,
                          region: str, cache_size: int = 1024) -> EdgeNode:
        """
        Register an edge node.

        Args:
            node_id: Node ID
            position: Position in Poincaré disk
            region: Geographic region
            cache_size: Cache size in MB

        Returns:
            Edge node
        """
        # Project to boundary
        boundary_pos = self.project_to_boundary(position)
        angular_pos = self.compute_angular_position(boundary_pos)

        edge_node = EdgeNode(
            node_id=node_id,
            position=position,
            boundary_position=boundary_pos,
            angular_position=angular_pos,
            region=region,
            cache_size=cache_size
        )

        self.edge_nodes[node_id] = edge_node

        # Assign to nearest gateway
        self._assign_to_gateway(edge_node)

        return edge_node

    def create_edge_gateway(self, region: str, angular_position: float,
                           capacity: int = 100 * 1024) -> EdgeGateway:
        """
        Create edge gateway (cluster center).

        Args:
            region: Geographic region
            angular_position: Angular position on boundary
            capacity: Total capacity in MB

        Returns:
            Edge gateway
        """
        gateway_id = str(uuid.uuid4())

        # Compute boundary position from angle
        boundary_pos = np.array([
            np.cos(angular_position),
            np.sin(angular_position),
            0.0
        ])

        gateway = EdgeGateway(
            gateway_id=gateway_id,
            boundary_position=boundary_pos,
            angular_position=angular_position,
            region=region,
            member_nodes=[],
            total_capacity=capacity
        )

        self.gateways[gateway_id] = gateway

        return gateway

    def cluster_edge_nodes(self, num_clusters: int) -> List[EdgeGateway]:
        """
        Cluster edge nodes by angular distance.

        Args:
            num_clusters: Number of clusters (gateways) to create

        Returns:
            List of created gateways
        """
        if not self.edge_nodes:
            return []

        # Get angular positions
        angles = [node.angular_position for node in self.edge_nodes.values()]

        # Simple k-means on circle
        # Initialize cluster centers uniformly
        cluster_angles = [2 * np.pi * i / num_clusters for i in range(num_clusters)]

        # Iterate to convergence
        for _ in range(10):
            # Assign nodes to nearest cluster
            assignments = []
            for angle in angles:
                distances = [self.angular_distance(angle, ca) for ca in cluster_angles]
                assignments.append(np.argmin(distances))

            # Update cluster centers
            for i in range(num_clusters):
                cluster_angles_i = [angles[j] for j in range(len(angles)) if assignments[j] == i]
                if cluster_angles_i:
                    # Mean angle (circular mean)
                    x = np.mean([np.cos(a) for a in cluster_angles_i])
                    y = np.mean([np.sin(a) for a in cluster_angles_i])
                    cluster_angles[i] = np.arctan2(y, x)
                    if cluster_angles[i] < 0:
                        cluster_angles[i] += 2 * np.pi

        # Create gateways at cluster centers
        gateways = []
        for angle in cluster_angles:
            # Determine region (simplified: use angle ranges)
            region = f"region-{int(angle * 180 / np.pi)}"
            gateway = self.create_edge_gateway(region, angle)
            gateways.append(gateway)

        # Reassign all nodes to gateways
        for node in self.edge_nodes.values():
            self._assign_to_gateway(node)

        return gateways

    def _assign_to_gateway(self, node: EdgeNode):
        """Assign node to nearest gateway"""
        if not self.gateways:
            return

        # Find nearest gateway by angular distance
        min_distance = float('inf')
        nearest_gateway = None

        for gateway in self.gateways.values():
            distance = self.angular_distance(node.angular_position, gateway.angular_position)
            if distance < min_distance:
                min_distance = distance
                nearest_gateway = gateway

        if nearest_gateway:
            node.gateway_id = nearest_gateway.gateway_id
            if node.node_id not in nearest_gateway.member_nodes:
                nearest_gateway.member_nodes.append(node.node_id)

    def route_through_gateway(self, source_node_id: str, dest_node_id: str) -> Optional[str]:
        """
        Route edge request through nearest gateway.

        Args:
            source_node_id: Source edge node
            dest_node_id: Destination node

        Returns:
            Gateway ID to route through, or None
        """
        if source_node_id not in self.edge_nodes:
            return None

        source = self.edge_nodes[source_node_id]
        return source.gateway_id

    # CDN Operations

    def cache_put(self, key: str, value: bytes, radius: float) -> bool:
        """
        Put content in CDN cache.

        Args:
            key: Content key
            value: Content value
            radius: Origin distance (for eviction policy)

        Returns:
            True if cached, False if evicted
        """
        size = len(value)

        # Check capacity
        if self.cache_used + size > self.cache_capacity:
            # Evict based on radius (furthest from origin = oldest/coldest)
            self._evict_by_radius(size)

        # Still not enough space?
        if self.cache_used + size > self.cache_capacity:
            return False

        entry = CacheEntry(
            key=key,
            value=value,
            size=size,
            radius=radius
        )

        self.cache[key] = entry
        self.cache_used += size

        return True

    def cache_get(self, key: str) -> Optional[bytes]:
        """Get content from cache"""
        if key not in self.cache:
            return None

        entry = self.cache[key]
        entry.access_count += 1
        entry.last_accessed = datetime.utcnow()

        return entry.value

    def _evict_by_radius(self, space_needed: int):
        """
        Evict cache entries based on radius.

        Entries furthest from origin (highest radius) are evicted first.
        This implements "coldest content at edge" policy.
        """
        # Sort by radius (descending)
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].radius,
            reverse=True
        )

        space_freed = 0
        for key, entry in sorted_entries:
            if space_freed >= space_needed:
                break

            del self.cache[key]
            self.cache_used -= entry.size
            space_freed += entry.size

    def cache_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.cache:
            return {
                'entries': 0,
                'used': 0,
                'capacity': self.cache_capacity,
                'hit_rate': 0.0
            }

        total_accesses = sum(e.access_count for e in self.cache.values())

        return {
            'entries': len(self.cache),
            'used': self.cache_used,
            'capacity': self.cache_capacity,
            'utilization': self.cache_used / self.cache_capacity,
            'total_accesses': total_accesses,
            'avg_radius': np.mean([e.radius for e in self.cache.values()])
        }

    def get_edge_topology(self) -> Dict:
        """Get edge topology"""
        return {
            'edge_nodes': len(self.edge_nodes),
            'gateways': len(self.gateways),
            'gateway_details': {
                gw_id: {
                    'region': gw.region,
                    'angular_position': gw.angular_position,
                    'member_count': len(gw.member_nodes),
                    'capacity': gw.total_capacity
                }
                for gw_id, gw in self.gateways.items()
            },
            'cache_stats': self.cache_stats()
        }
