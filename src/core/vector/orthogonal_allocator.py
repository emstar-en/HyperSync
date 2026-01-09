"""
HyperSync Orthogonal Vector Store Allocator

Aligns vector stores in orthogonal subspaces to accelerate cross-node retrieval
while protecting routing geometry.
"""

import uuid
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from scipy.linalg import qr, svd


@dataclass
class ProjectionMatrix:
    """Projection matrix for orthogonal subspace."""
    shape: Tuple[int, int]
    data: np.ndarray
    orthogonality_score: float = 1.0

    def __post_init__(self):
        """Validate matrix dimensions."""
        if self.data.shape != self.shape:
            raise ValueError(f"Matrix shape {self.data.shape} doesn't match declared {self.shape}")

    def to_dict(self) -> Dict:
        """Export to dictionary."""
        return {
            "shape": list(self.shape),
            "data": self.data.tolist(),
            "orthogonality_score": float(self.orthogonality_score)
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ProjectionMatrix":
        """Load from dictionary."""
        return cls(
            shape=tuple(data["shape"]),
            data=np.array(data["data"]),
            orthogonality_score=data.get("orthogonality_score", 1.0)
        )


@dataclass
class OrthogonalFrame:
    """
    Orthogonal vector frame for a node.

    Defines the subspace allocation and projection for vector embeddings.
    """
    frame_id: str
    node_id: str
    base_dimensions: List[int]
    vector_dimensions: int
    projection_matrix: ProjectionMatrix

    routing_geometry_preserved: bool = True
    distortion_factor: float = 0.0

    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    cache_max_entries: int = 10000

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"

    def to_dict(self) -> Dict:
        """Export frame to dictionary."""
        return {
            "frame_id": self.frame_id,
            "node_id": self.node_id,
            "base_dimensions": self.base_dimensions,
            "vector_dimensions": self.vector_dimensions,
            "projection_matrix": self.projection_matrix.to_dict(),
            "routing_geometry": {
                "preserved": self.routing_geometry_preserved,
                "distortion_factor": self.distortion_factor
            },
            "cache_config": {
                "enabled": self.cache_enabled,
                "ttl_seconds": self.cache_ttl_seconds,
                "max_entries": self.cache_max_entries
            },
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "version": self.version
            }
        }


class OrthogonalAllocator:
    """
    Allocates orthogonal subspaces for federated vector stores.

    Computes projection matrices that maintain orthogonality while
    preserving routing geometry.
    """

    def __init__(self, base_dims: List[int], vector_dims: int):
        """
        Initialize allocator.

        Args:
            base_dims: Shared dimensional indices
            vector_dims: Dimensionality of vector embeddings
        """
        self.base_dims = base_dims
        self.vector_dims = vector_dims
        self.base_dim_count = len(base_dims)

        # Track allocated frames
        self.frames: Dict[str, OrthogonalFrame] = {}

        # Orthogonal basis pool
        self._basis_pool: Optional[np.ndarray] = None
        self._next_basis_index = 0

    def _initialize_basis_pool(self):
        """Initialize pool of orthogonal basis vectors."""
        # Generate random matrix and orthogonalize using QR decomposition
        random_matrix = np.random.randn(self.vector_dims, self.vector_dims)
        q, r = qr(random_matrix)
        self._basis_pool = q
        self._next_basis_index = 0

    def allocate(self, node_id: str, preserve_geometry: bool = True) -> OrthogonalFrame:
        """
        Allocate orthogonal frame for a node.

        Args:
            node_id: Node identifier
            preserve_geometry: Whether to preserve routing geometry

        Returns:
            OrthogonalFrame instance
        """
        if self._basis_pool is None:
            self._initialize_basis_pool()

        # Get next orthogonal basis vectors
        if self._next_basis_index + self.base_dim_count > self.vector_dims:
            # Regenerate pool if exhausted
            self._initialize_basis_pool()

        # Extract basis vectors for this allocation
        basis_vectors = self._basis_pool[
            self._next_basis_index:self._next_basis_index + self.base_dim_count
        ]
        self._next_basis_index += self.base_dim_count

        # Compute projection matrix
        projection = self._compute_projection(basis_vectors, preserve_geometry)

        # Create frame
        frame = OrthogonalFrame(
            frame_id=str(uuid.uuid4()),
            node_id=node_id,
            base_dimensions=self.base_dims,
            vector_dimensions=self.vector_dims,
            projection_matrix=projection,
            routing_geometry_preserved=preserve_geometry
        )

        # Compute distortion if geometry preservation requested
        if preserve_geometry:
            frame.distortion_factor = self._compute_distortion(projection.data)

        self.frames[frame.frame_id] = frame
        return frame

    def _compute_projection(self, basis_vectors: np.ndarray,
                           preserve_geometry: bool) -> ProjectionMatrix:
        """
        Compute projection matrix from basis vectors.

        Args:
            basis_vectors: Orthogonal basis vectors
            preserve_geometry: Whether to preserve routing geometry

        Returns:
            ProjectionMatrix instance
        """
        if preserve_geometry:
            # Use SVD to compute geometry-preserving projection
            u, s, vt = svd(basis_vectors, full_matrices=False)
            projection_data = u @ np.diag(s) @ vt
        else:
            # Direct projection
            projection_data = basis_vectors

        # Compute orthogonality score
        orthogonality = self._compute_orthogonality(projection_data)

        return ProjectionMatrix(
            shape=projection_data.shape,
            data=projection_data,
            orthogonality_score=orthogonality
        )

    def _compute_orthogonality(self, matrix: np.ndarray) -> float:
        """
        Compute orthogonality score for matrix.

        Returns value in [0, 1] where 1.0 is perfectly orthogonal.
        """
        # Compute Gram matrix
        gram = matrix @ matrix.T

        # Perfect orthogonality means Gram matrix is identity
        identity = np.eye(gram.shape[0])

        # Compute Frobenius norm of difference
        diff_norm = np.linalg.norm(gram - identity, 'fro')

        # Normalize to [0, 1] range
        max_diff = np.sqrt(2 * gram.shape[0])
        score = 1.0 - (diff_norm / max_diff)

        return max(0.0, min(1.0, score))

    def _compute_distortion(self, projection: np.ndarray) -> float:
        """
        Compute geometric distortion factor.

        Returns value >= 0 where 0 means no distortion.
        """
        # Compute singular values
        _, s, _ = svd(projection, full_matrices=False)

        # Distortion is variance of singular values
        # (perfect preservation has all singular values equal)
        mean_s = np.mean(s)
        if mean_s == 0:
            return 0.0

        variance = np.var(s)
        distortion = variance / (mean_s ** 2)

        return float(distortion)

    def get_frame(self, frame_id: str) -> Optional[OrthogonalFrame]:
        """Get frame by ID."""
        return self.frames.get(frame_id)

    def get_node_frame(self, node_id: str) -> Optional[OrthogonalFrame]:
        """Get frame for a specific node."""
        for frame in self.frames.values():
            if frame.node_id == node_id:
                return frame
        return None

    def compute_similarity(self, query_vector: np.ndarray,
                          remote_embeddings: np.ndarray,
                          remote_frame: OrthogonalFrame) -> np.ndarray:
        """
        Compute similarity between query and remote embeddings.

        Args:
            query_vector: Query embedding vector
            remote_embeddings: Remote node embeddings (N x D)
            remote_frame: Remote node's orthogonal frame

        Returns:
            Similarity scores (N,)
        """
        # Project query into remote frame's subspace
        projected_query = remote_frame.projection_matrix.data @ query_vector

        # Compute dot product similarity
        similarities = remote_embeddings @ projected_query

        return similarities

    def verify_orthogonality(self, frame_a: OrthogonalFrame,
                            frame_b: OrthogonalFrame) -> float:
        """
        Verify orthogonality between two frames.

        Returns orthogonality score in [0, 1].
        """
        proj_a = frame_a.projection_matrix.data
        proj_b = frame_b.projection_matrix.data

        # Compute cross-correlation
        cross_corr = proj_a @ proj_b.T

        # Perfect orthogonality means cross-correlation is zero
        cross_norm = np.linalg.norm(cross_corr, 'fro')

        # Normalize
        max_norm = np.sqrt(proj_a.shape[0] * proj_b.shape[0])
        score = 1.0 - (cross_norm / max_norm)

        return max(0.0, min(1.0, score))

    def list_frames(self) -> List[OrthogonalFrame]:
        """List all allocated frames."""
        return list(self.frames.values())

    def get_statistics(self) -> Dict:
        """Get allocator statistics."""
        if not self.frames:
            return {
                "total_frames": 0,
                "average_orthogonality": 0.0,
                "average_distortion": 0.0
            }

        orthogonality_scores = [
            f.projection_matrix.orthogonality_score
            for f in self.frames.values()
        ]

        distortion_factors = [
            f.distortion_factor
            for f in self.frames.values()
        ]

        return {
            "total_frames": len(self.frames),
            "average_orthogonality": np.mean(orthogonality_scores),
            "average_distortion": np.mean(distortion_factors),
            "min_orthogonality": np.min(orthogonality_scores),
            "max_distortion": np.max(distortion_factors),
            "basis_pool_utilization": self._next_basis_index / self.vector_dims
        }


class VectorStoreCache:
    """
    Cache for vector store projections and similarities.
    """

    def __init__(self, max_entries: int = 10000, ttl_seconds: int = 3600):
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[np.ndarray, datetime]] = {}

    def get(self, key: str) -> Optional[np.ndarray]:
        """Get cached value."""
        if key not in self.cache:
            return None

        value, timestamp = self.cache[key]

        # Check TTL
        age = (datetime.now() - timestamp).total_seconds()
        if age > self.ttl_seconds:
            del self.cache[key]
            return None

        return value

    def put(self, key: str, value: np.ndarray):
        """Put value in cache."""
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_entries:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]

        self.cache[key] = (value, datetime.now())

    def clear(self):
        """Clear cache."""
        self.cache.clear()

    def get_statistics(self) -> Dict:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "capacity": self.max_entries,
            "utilization": len(self.cache) / self.max_entries
        }
