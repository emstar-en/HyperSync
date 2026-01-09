"""
Vector Engine - Hyperbolic vector index with HNSW.

Provides hyperbolic vector storage with HNSW-based indexing optimized
for curved space, embedding lifecycle management, and FAISS bridge.
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import math
import random


@dataclass
class VectorRecord:
    """Vector record with metadata."""
    vector_id: str
    embedding: List[float]
    metadata: Dict[str, Any]
    norm: float


class HyperbolicVectorIndex:
    """
    Hyperbolic vector index using HNSW-inspired algorithm.

    Stores vectors in hyperbolic space with efficient nearest neighbor
    search using hierarchical navigable small world graphs.
    """

    def __init__(self, dimension: int, curvature: float = -1.0, m: int = 16):
        self.dimension = dimension
        self.curvature = curvature
        self.m = m  # Max connections per layer
        self.vectors: Dict[str, VectorRecord] = {}
        self.graph: Dict[str, Dict[int, List[str]]] = {}  # vector_id -> layer -> neighbors
        self.entry_point: Optional[str] = None

    def insert(self, vector_id: str, embedding: List[float],
               metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Insert vector into index.

        Args:
            vector_id: Vector identifier
            embedding: Vector embedding
            metadata: Optional metadata
        """
        if len(embedding) != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {len(embedding)}")

        # Compute norm
        norm = math.sqrt(sum(x**2 for x in embedding))

        record = VectorRecord(
            vector_id=vector_id,
            embedding=embedding,
            metadata=metadata or {},
            norm=norm
        )

        self.vectors[vector_id] = record

        # Initialize graph layers
        max_layer = self._get_random_layer()
        self.graph[vector_id] = {layer: [] for layer in range(max_layer + 1)}

        # Set entry point if first vector
        if self.entry_point is None:
            self.entry_point = vector_id
            return

        # Insert into graph layers
        self._insert_into_graph(vector_id, max_layer)

    def search(self, query: List[float], k: int = 10,
               ef: int = 50) -> List[Tuple[str, float]]:
        """
        Search for k nearest neighbors.

        Args:
            query: Query vector
            k: Number of neighbors to return
            ef: Size of dynamic candidate list

        Returns:
            List of (vector_id, distance) tuples
        """
        if len(query) != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {len(query)}")

        if not self.vectors or self.entry_point is None:
            return []

        # Start from entry point
        current = self.entry_point
        current_dist = self._hyperbolic_distance(query, self.vectors[current].embedding)

        # Greedy search through layers
        max_layer = max(self.graph[self.entry_point].keys())

        for layer in range(max_layer, -1, -1):
            changed = True
            while changed:
                changed = False

                # Check neighbors at this layer
                for neighbor_id in self.graph[current].get(layer, []):
                    neighbor_dist = self._hyperbolic_distance(query, self.vectors[neighbor_id].embedding)

                    if neighbor_dist < current_dist:
                        current = neighbor_id
                        current_dist = neighbor_dist
                        changed = True

        # Beam search at layer 0
        candidates = [(current_dist, current)]
        visited = {current}

        while len(candidates) < ef and candidates:
            # Get closest unvisited candidate
            candidates.sort()
            _, current = candidates.pop(0)

            # Explore neighbors
            for neighbor_id in self.graph[current].get(0, []):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    neighbor_dist = self._hyperbolic_distance(query, self.vectors[neighbor_id].embedding)
                    candidates.append((neighbor_dist, neighbor_id))

        # Return top k
        candidates.sort()
        return [(vid, dist) for dist, vid in candidates[:k]]

    def delete(self, vector_id: str) -> bool:
        """
        Delete vector from index.

        Args:
            vector_id: Vector identifier

        Returns:
            True if deleted successfully
        """
        if vector_id not in self.vectors:
            return False

        # Remove from vectors
        del self.vectors[vector_id]

        # Remove from graph
        if vector_id in self.graph:
            # Remove connections to this vector
            for other_id in self.graph:
                if other_id != vector_id:
                    for layer in self.graph[other_id]:
                        if vector_id in self.graph[other_id][layer]:
                            self.graph[other_id][layer].remove(vector_id)

            del self.graph[vector_id]

        # Update entry point if needed
        if self.entry_point == vector_id:
            self.entry_point = next(iter(self.vectors.keys())) if self.vectors else None

        return True

    def _hyperbolic_distance(self, v1: List[float], v2: List[float]) -> float:
        """Compute hyperbolic distance between vectors."""
        # Poincaré distance formula
        diff_norm_sq = sum((a - b)**2 for a, b in zip(v1, v2))
        v1_norm_sq = sum(x**2 for x in v1)
        v2_norm_sq = sum(x**2 for x in v2)

        numerator = 2 * diff_norm_sq
        denominator = (1 - v1_norm_sq) * (1 - v2_norm_sq)

        if denominator <= 0:
            return float('inf')

        return math.acosh(1 + numerator / denominator)

    def _get_random_layer(self) -> int:
        """Get random layer for new vector."""
        # Exponential decay
        ml = 1.0 / math.log(2.0)
        return int(-math.log(random.random()) * ml)

    def _insert_into_graph(self, vector_id: str, max_layer: int) -> None:
        """Insert vector into graph structure."""
        # Find nearest neighbors at each layer
        for layer in range(max_layer + 1):
            # Find m nearest neighbors at this layer
            neighbors = self._find_neighbors_at_layer(vector_id, layer, self.m)

            # Add bidirectional connections
            for neighbor_id in neighbors:
                self.graph[vector_id][layer].append(neighbor_id)

                if layer in self.graph[neighbor_id]:
                    self.graph[neighbor_id][layer].append(vector_id)

                    # Prune if too many connections
                    if len(self.graph[neighbor_id][layer]) > self.m:
                        self._prune_connections(neighbor_id, layer)

    def _find_neighbors_at_layer(self, vector_id: str, layer: int, m: int) -> List[str]:
        """Find m nearest neighbors at specified layer."""
        candidates = []
        query_embedding = self.vectors[vector_id].embedding

        for other_id in self.vectors:
            if other_id != vector_id and layer in self.graph.get(other_id, {}):
                dist = self._hyperbolic_distance(query_embedding, self.vectors[other_id].embedding)
                candidates.append((dist, other_id))

        candidates.sort()
        return [vid for _, vid in candidates[:m]]

    def _prune_connections(self, vector_id: str, layer: int) -> None:
        """Prune connections to maintain m limit."""
        if layer not in self.graph[vector_id]:
            return

        neighbors = self.graph[vector_id][layer]
        query_embedding = self.vectors[vector_id].embedding

        # Sort by distance
        neighbor_dists = [
            (self._hyperbolic_distance(query_embedding, self.vectors[nid].embedding), nid)
            for nid in neighbors
        ]
        neighbor_dists.sort()

        # Keep only m closest
        self.graph[vector_id][layer] = [nid for _, nid in neighbor_dists[:self.m]]

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        total_connections = sum(
            len(neighbors)
            for vector_graph in self.graph.values()
            for neighbors in vector_graph.values()
        )

        return {
            "num_vectors": len(self.vectors),
            "dimension": self.dimension,
            "total_connections": total_connections,
            "avg_connections": total_connections / max(len(self.vectors), 1),
            "curvature": self.curvature
        }


class EmbeddingLifecycleManager:
    """Manages embedding versioning and lifecycle."""

    def __init__(self):
        self.embeddings: Dict[str, Dict[str, List[float]]] = {}  # entity_id -> version -> embedding
        self.current_versions: Dict[str, str] = {}  # entity_id -> current_version

    def store_embedding(self, entity_id: str, embedding: List[float], version: str = "v1") -> None:
        """Store embedding with version."""
        if entity_id not in self.embeddings:
            self.embeddings[entity_id] = {}

        self.embeddings[entity_id][version] = embedding
        self.current_versions[entity_id] = version

    def get_embedding(self, entity_id: str, version: Optional[str] = None) -> Optional[List[float]]:
        """Get embedding, optionally specific version."""
        if entity_id not in self.embeddings:
            return None

        if version is None:
            version = self.current_versions.get(entity_id)

        return self.embeddings[entity_id].get(version)

    def list_versions(self, entity_id: str) -> List[str]:
        """List all versions for entity."""
        return list(self.embeddings.get(entity_id, {}).keys())
