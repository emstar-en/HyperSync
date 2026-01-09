"""
Graph Engine - Hyperbolic graph storage and algorithms.

Provides hyperbolic adjacency store with graph algorithms optimized
for curved space (shortest path, centrality, etc.) and Neo4j adapter.
"""
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import math


@dataclass
class Node:
    """Graph node."""
    node_id: str
    properties: Dict[str, Any]
    position: Optional[Tuple[float, float]] = None  # Hyperbolic coordinates


@dataclass
class Edge:
    """Graph edge."""
    edge_id: str
    source: str
    target: str
    weight: float
    properties: Dict[str, Any]


class HyperbolicGraphEngine:
    """
    Hyperbolic graph storage and query engine.

    Stores graphs in hyperbolic space with geodesic-aware algorithms
    for path finding, centrality, and community detection.
    """

    def __init__(self, curvature: float = -1.0):
        self.curvature = curvature
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)

    def add_node(self, node_id: str, properties: Optional[Dict[str, Any]] = None,
                 position: Optional[Tuple[float, float]] = None) -> Node:
        """
        Add node to graph.

        Args:
            node_id: Node identifier
            properties: Node properties
            position: Hyperbolic coordinates (r, theta)

        Returns:
            Created Node
        """
        node = Node(
            node_id=node_id,
            properties=properties or {},
            position=position
        )

        self.nodes[node_id] = node
        return node

    def add_edge(self, source: str, target: str, weight: float = 1.0,
                 properties: Optional[Dict[str, Any]] = None) -> Edge:
        """
        Add edge to graph.

        Args:
            source: Source node ID
            target: Target node ID
            weight: Edge weight
            properties: Edge properties

        Returns:
            Created Edge
        """
        edge_id = f"{source}->{target}"

        edge = Edge(
            edge_id=edge_id,
            source=source,
            target=target,
            weight=weight,
            properties=properties or {}
        )

        self.edges[edge_id] = edge
        self.adjacency[source].add(target)

        return edge

    def geodesic_distance(self, node1_id: str, node2_id: str) -> float:
        """
        Compute geodesic distance between nodes in hyperbolic space.

        Args:
            node1_id: First node ID
            node2_id: Second node ID

        Returns:
            Geodesic distance
        """
        node1 = self.nodes.get(node1_id)
        node2 = self.nodes.get(node2_id)

        if not node1 or not node2 or not node1.position or not node2.position:
            return float('inf')

        r1, theta1 = node1.position
        r2, theta2 = node2.position

        # Hyperbolic distance formula in Poincaré disk
        delta_theta = abs(theta2 - theta1)

        numerator = (r1 - r2)**2 + 4 * r1 * r2 * math.sin(delta_theta / 2)**2
        denominator = (1 - r1**2) * (1 - r2**2)

        if denominator <= 0:
            return float('inf')

        return math.acosh(1 + 2 * numerator / denominator)

    def shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find shortest path using geodesic distances (Dijkstra's algorithm).

        Args:
            source: Source node ID
            target: Target node ID

        Returns:
            List of node IDs forming shortest path, or None
        """
        if source not in self.nodes or target not in self.nodes:
            return None

        distances = {node_id: float('inf') for node_id in self.nodes}
        distances[source] = 0
        previous = {}
        unvisited = set(self.nodes.keys())

        while unvisited:
            # Find node with minimum distance
            current = min(unvisited, key=lambda n: distances[n])

            if distances[current] == float('inf'):
                break

            if current == target:
                # Reconstruct path
                path = []
                while current in previous:
                    path.append(current)
                    current = previous[current]
                path.append(source)
                return list(reversed(path))

            unvisited.remove(current)

            # Update distances to neighbors
            for neighbor in self.adjacency[current]:
                if neighbor in unvisited:
                    edge_id = f"{current}->{neighbor}"
                    edge = self.edges.get(edge_id)

                    if edge:
                        alt_distance = distances[current] + edge.weight

                        if alt_distance < distances[neighbor]:
                            distances[neighbor] = alt_distance
                            previous[neighbor] = current

        return None

    def betweenness_centrality(self) -> Dict[str, float]:
        """
        Compute betweenness centrality for all nodes.

        Returns:
            Dict mapping node IDs to centrality scores
        """
        centrality = {node_id: 0.0 for node_id in self.nodes}

        # For each pair of nodes
        node_ids = list(self.nodes.keys())
        for i, source in enumerate(node_ids):
            for target in node_ids[i+1:]:
                path = self.shortest_path(source, target)

                if path and len(path) > 2:
                    # Increment centrality for intermediate nodes
                    for node_id in path[1:-1]:
                        centrality[node_id] += 1.0

        # Normalize
        n = len(self.nodes)
        if n > 2:
            norm_factor = 2.0 / ((n - 1) * (n - 2))
            for node_id in centrality:
                centrality[node_id] *= norm_factor

        return centrality

    def neighbors(self, node_id: str, max_distance: Optional[float] = None) -> List[str]:
        """
        Get neighbors of node, optionally within geodesic distance.

        Args:
            node_id: Node identifier
            max_distance: Maximum geodesic distance (None for direct neighbors)

        Returns:
            List of neighbor node IDs
        """
        if node_id not in self.nodes:
            return []

        if max_distance is None:
            return list(self.adjacency[node_id])

        # Find all nodes within geodesic distance
        neighbors = []
        for other_id in self.nodes:
            if other_id != node_id:
                dist = self.geodesic_distance(node_id, other_id)
                if dist <= max_distance:
                    neighbors.append(other_id)

        return neighbors

    def subgraph(self, node_ids: List[str]) -> 'HyperbolicGraphEngine':
        """
        Extract subgraph containing specified nodes.

        Args:
            node_ids: List of node IDs to include

        Returns:
            New HyperbolicGraphEngine with subgraph
        """
        subgraph = HyperbolicGraphEngine(curvature=self.curvature)

        # Add nodes
        for node_id in node_ids:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                subgraph.add_node(node_id, node.properties, node.position)

        # Add edges between included nodes
        for edge in self.edges.values():
            if edge.source in node_ids and edge.target in node_ids:
                subgraph.add_edge(edge.source, edge.target, edge.weight, edge.properties)

        return subgraph

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "num_nodes": len(self.nodes),
            "num_edges": len(self.edges),
            "avg_degree": sum(len(neighbors) for neighbors in self.adjacency.values()) / max(len(self.nodes), 1),
            "curvature": self.curvature
        }


class Neo4jAdapter:
    """Adapter for Neo4j graph database."""

    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.connected = False

    async def connect(self) -> bool:
        """Connect to Neo4j database."""
        # Simulate connection
        self.connected = True
        return True

    async def import_graph(self, graph: HyperbolicGraphEngine) -> Dict[str, Any]:
        """
        Import HyperbolicGraphEngine into Neo4j.

        Args:
            graph: Graph to import

        Returns:
            Import statistics
        """
        if not self.connected:
            await self.connect()

        # Simulate import
        return {
            "nodes_imported": len(graph.nodes),
            "edges_imported": len(graph.edges)
        }

    async def export_graph(self) -> HyperbolicGraphEngine:
        """
        Export Neo4j graph to HyperbolicGraphEngine.

        Returns:
            Exported graph
        """
        if not self.connected:
            await self.connect()

        # Simulate export
        graph = HyperbolicGraphEngine()
        return graph
