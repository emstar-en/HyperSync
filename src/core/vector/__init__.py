"""HyperSync Vector Store Federation Module"""

from .orthogonal_allocator import (
    OrthogonalAllocator, OrthogonalFrame,
    ProjectionMatrix, VectorStoreCache
)

__all__ = [
    "OrthogonalAllocator", "OrthogonalFrame",
    "ProjectionMatrix", "VectorStoreCache"
]
