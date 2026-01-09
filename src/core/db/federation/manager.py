"""
Federation Manager

Composes shards across nodes, maintains replica topology, and routes
queries using geodesic placement policies.
"""
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class ReplicaRole(Enum):
    """Replica roles."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ARBITER = "arbiter"


class QuorumPolicy(Enum):
    """Quorum policies."""
    MAJORITY = "majority"
    ALL = "all"
    ONE = "one"
    CUSTOM = "custom"


@dataclass
class Node:
    """Federation node."""
    node_id: str
    address: str
    port: int
    role: ReplicaRole = ReplicaRole.SECONDARY
    curvature_zone: float = -1.0
    capacity: int = 100
    current_load: int = 0
    healthy: bool = True
    metadata: Dict = field(default_factory=dict)

    def get_load_factor(self) -> float:
        """Get current load factor (0.0 to 1.0)."""
        if self.capacity == 0:
            return 1.0
        return self.current_load / self.capacity


@dataclass
class Shard:
    """Data shard."""
    shard_id: str
    key_range: tuple  # (start, end)
    replicas: List[str]  # Node IDs
    primary_node: str
    curvature: float = -1.0
    size_bytes: int = 0


class FederationManager:
    """
    Manages federated database topology.

    Composes shards across nodes, maintains replica topology, and
    routes queries using geodesic placement policies.
    """

    def __init__(self, quorum_policy: QuorumPolicy = QuorumPolicy.MAJORITY):
        self.quorum_policy = quorum_policy
        self._nodes: Dict[str, Node] = {}
        self._shards: Dict[str, Shard] = {}
        self._topology_version = 0

    def register_node(self, node: Node):
        """
        Register node in federation.

        Args:
            node: Node to register
        """
        self._nodes[node.node_id] = node
        self._topology_version += 1
        logger.info(f"Registered node: {node.node_id} at {node.address}:{node.port}")

    def unregister_node(self, node_id: str):
        """Unregister node."""
        if node_id in self._nodes:
            del self._nodes[node_id]
            self._topology_version += 1
            logger.info(f"Unregistered node: {node_id}")

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID."""
        return self._nodes.get(node_id)

    def list_nodes(self, role: Optional[ReplicaRole] = None) -> List[Node]:
        """List nodes, optionally filtered by role."""
        nodes = list(self._nodes.values())
        if role:
            nodes = [n for n in nodes if n.role == role]
        return nodes

    def create_shard(
        self,
        shard_id: str,
        key_range: tuple,
        replication_factor: int = 3,
        curvature: float = -1.0
    ) -> Shard:
        """
        Create new shard.

        Args:
            shard_id: Shard identifier
            key_range: Key range (start, end)
            replication_factor: Number of replicas
            curvature: Shard curvature

        Returns:
            Created shard
        """
        # Select nodes for replicas using geodesic placement
        replica_nodes = self._select_replica_nodes(replication_factor, curvature)

        if len(replica_nodes) < replication_factor:
            logger.warning(f"Could not allocate {replication_factor} replicas, got {len(replica_nodes)}")

        # First node is primary
        primary_node = replica_nodes[0] if replica_nodes else None

        shard = Shard(
            shard_id=shard_id,
            key_range=key_range,
            replicas=[n.node_id for n in replica_nodes],
            primary_node=primary_node.node_id if primary_node else "",
            curvature=curvature
        )

        self._shards[shard_id] = shard
        logger.info(f"Created shard: {shard_id}, replicas: {shard.replicas}")

        return shard

    def _select_replica_nodes(self, count: int, curvature: float) -> List[Node]:
        """
        Select nodes for replicas using geodesic placement.

        Prefers nodes in same curvature zone.
        """
        # Get healthy nodes
        candidates = [n for n in self._nodes.values() if n.healthy]

        # Sort by curvature distance and load
        def score(node: Node) -> float:
            curvature_dist = abs(node.curvature_zone - curvature)
            load_penalty = node.get_load_factor() * 10
            return curvature_dist + load_penalty

        candidates.sort(key=score)

        # Select top N
        selected = candidates[:count]

        # Update load
        for node in selected:
            node.current_load += 1

        return selected

    def get_shard_for_key(self, key: str) -> Optional[Shard]:
        """
        Get shard for key using consistent hashing.

        Args:
            key: Key to lookup

        Returns:
            Shard containing key
        """
        # Hash key
        key_hash = int(hashlib.md5(key.encode()).hexdigest(), 16)

        # Find shard
        for shard in self._shards.values():
            start, end = shard.key_range
            if start <= key_hash < end:
                return shard

        return None

    def route_query(self, query: dict) -> dict:
        """
        Route query to appropriate nodes.

        Args:
            query: Query to route

        Returns:
            Routing plan
        """
        # Extract key or table from query
        table = query.get('table', 'default')
        key = query.get('key')

        if key:
            # Route to specific shard
            shard = self.get_shard_for_key(key)
            if shard:
                return {
                    'strategy': 'single_shard',
                    'shard': shard.shard_id,
                    'nodes': shard.replicas,
                    'primary': shard.primary_node
                }

        # Broadcast to all shards
        return {
            'strategy': 'broadcast',
            'shards': list(self._shards.keys()),
            'nodes': list(self._nodes.keys())
        }

    def check_quorum(self, shard_id: str, responding_nodes: Set[str]) -> bool:
        """
        Check if quorum is satisfied.

        Args:
            shard_id: Shard identifier
            responding_nodes: Set of responding node IDs

        Returns:
            True if quorum satisfied
        """
        shard = self._shards.get(shard_id)
        if not shard:
            return False

        total_replicas = len(shard.replicas)
        responding_replicas = len(responding_nodes & set(shard.replicas))

        if self.quorum_policy == QuorumPolicy.MAJORITY:
            return responding_replicas > total_replicas / 2
        elif self.quorum_policy == QuorumPolicy.ALL:
            return responding_replicas == total_replicas
        elif self.quorum_policy == QuorumPolicy.ONE:
            return responding_replicas >= 1
        else:
            return False

    def rebalance_shards(self):
        """Rebalance shards across nodes."""
        logger.info("Starting shard rebalancing...")

        # Calculate average load
        total_load = sum(n.current_load for n in self._nodes.values())
        avg_load = total_load / len(self._nodes) if self._nodes else 0

        # Find overloaded and underloaded nodes
        overloaded = [n for n in self._nodes.values() if n.current_load > avg_load * 1.2]
        underloaded = [n for n in self._nodes.values() if n.current_load < avg_load * 0.8]

        # Move shards from overloaded to underloaded
        for node in overloaded:
            # Find shards on this node
            shards_on_node = [
                s for s in self._shards.values()
                if node.node_id in s.replicas
            ]

            # Move some shards
            for shard in shards_on_node[:1]:  # Move one shard
                if underloaded:
                    target = underloaded[0]

                    # Update shard replicas
                    shard.replicas.remove(node.node_id)
                    shard.replicas.append(target.node_id)

                    # Update loads
                    node.current_load -= 1
                    target.current_load += 1

                    logger.info(f"Moved shard {shard.shard_id} from {node.node_id} to {target.node_id}")

                    # Re-sort underloaded
                    underloaded.sort(key=lambda n: n.current_load)

        self._topology_version += 1
        logger.info("Shard rebalancing completed")

    def get_topology(self) -> dict:
        """Get current topology."""
        return {
            'version': self._topology_version,
            'nodes': {nid: {
                'address': n.address,
                'port': n.port,
                'role': n.role.value,
                'load': n.current_load,
                'capacity': n.capacity,
                'healthy': n.healthy
            } for nid, n in self._nodes.items()},
            'shards': {sid: {
                'key_range': s.key_range,
                'replicas': s.replicas,
                'primary': s.primary_node,
                'curvature': s.curvature
            } for sid, s in self._shards.items()}
        }


# Export public API
__all__ = [
    'FederationManager',
    'Node',
    'Shard',
    'ReplicaRole',
    'QuorumPolicy'
]
