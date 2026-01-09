"""
Query Executor

Executes query plans with streamed and materialized modes.
Supports vectorized evaluation for distance computations.
"""
import logging
from typing import List, Dict, Any, Iterator, Optional
from dataclasses import dataclass
from enum import Enum
import math

from hypersync.db.query.planner import PlanNode, PlanNodeType
from hypersync.db.engine.core import HyperbolicStorageEngine

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Execution modes."""
    STREAMED = "streamed"
    MATERIALIZED = "materialized"


@dataclass
class ExecutionContext:
    """Context for query execution."""
    storage_engine: HyperbolicStorageEngine
    mode: ExecutionMode = ExecutionMode.STREAMED
    batch_size: int = 1000
    use_vectorization: bool = True


class KernelRegistry:
    """
    Registry for execution kernels.

    Allows fallback to CPU/GPU implementations.
    """

    def __init__(self):
        self._kernels: Dict[str, callable] = {}

    def register(self, name: str, kernel: callable):
        """Register kernel."""
        self._kernels[name] = kernel
        logger.debug(f"Registered kernel: {name}")

    def get(self, name: str) -> Optional[callable]:
        """Get kernel by name."""
        return self._kernels.get(name)

    def has(self, name: str) -> bool:
        """Check if kernel exists."""
        return name in self._kernels


# Global kernel registry
KERNEL_REGISTRY = KernelRegistry()


# Register default kernels
def _poincare_distance_kernel(p1: tuple, p2: tuple) -> float:
    """Compute Poincaré distance between two points."""
    x1, y1 = p1
    x2, y2 = p2

    # Euclidean distance squared
    dx = x2 - x1
    dy = y2 - y1
    dist_sq = dx * dx + dy * dy

    # Poincaré distance formula
    norm1_sq = x1 * x1 + y1 * y1
    norm2_sq = x2 * x2 + y2 * y2

    numerator = 2 * dist_sq
    denominator = (1 - norm1_sq) * (1 - norm2_sq)

    if denominator <= 0:
        return float('inf')

    return math.acosh(1 + numerator / denominator)


KERNEL_REGISTRY.register('poincare_distance', _poincare_distance_kernel)


class Executor:
    """
    Query executor.

    Executes query plans with support for streaming and materialization.
    """

    def __init__(self, context: ExecutionContext):
        self.context = context
        self.kernel_registry = KERNEL_REGISTRY

    def execute(self, plan: PlanNode) -> Iterator[Dict[str, Any]]:
        """
        Execute query plan.

        Args:
            plan: Query plan

        Yields:
            Result rows
        """
        if self.context.mode == ExecutionMode.STREAMED:
            yield from self._execute_streamed(plan)
        else:
            # Materialize all results
            results = list(self._execute_streamed(plan))
            yield from results

    def _execute_streamed(self, plan: PlanNode) -> Iterator[Dict[str, Any]]:
        """Execute plan in streaming mode."""
        if plan.node_type == PlanNodeType.SCAN:
            yield from self._execute_scan(plan)
        elif plan.node_type == PlanNodeType.GEODESIC_SCAN:
            yield from self._execute_geodesic_scan(plan)
        elif plan.node_type == PlanNodeType.FILTER:
            yield from self._execute_filter(plan)
        elif plan.node_type == PlanNodeType.JOIN:
            yield from self._execute_join(plan)
        elif plan.node_type == PlanNodeType.GEODESIC_JOIN:
            yield from self._execute_geodesic_join(plan)
        elif plan.node_type == PlanNodeType.LIMIT:
            yield from self._execute_limit(plan)
        else:
            raise ValueError(f"Unknown plan node type: {plan.node_type}")

    def _execute_scan(self, plan: PlanNode) -> Iterator[Dict[str, Any]]:
        """Execute table scan."""
        table = plan.metadata['table']

        # Scan table
        results = self.context.storage_engine.scan(table)

        for record in results:
            yield record

    def _execute_geodesic_scan(self, plan: PlanNode) -> Iterator[Dict[str, Any]]:
        """Execute geodesic scan."""
        table = plan.metadata['table']
        start_point = plan.metadata.get('start_point', (0.0, 0.0))
        radius = plan.metadata.get('radius', 1.0)

        # Get distance kernel
        distance_fn = self.kernel_registry.get('poincare_distance')
        if not distance_fn:
            raise ValueError("Poincaré distance kernel not found")

        # Scan and filter by distance
        results = self.context.storage_engine.scan(table)

        for record in results:
            point = record.get('point', (0.0, 0.0))
            distance = distance_fn(start_point, point)

            if distance <= radius:
                record['_distance'] = distance
                yield record

    def _execute_filter(self, plan: PlanNode) -> Iterator[Dict[str, Any]]:
        """Execute filter."""
        # Get input
        input_plan = plan.children[0]

        # For now, just pass through
        # In production, would evaluate condition
        yield from self._execute_streamed(input_plan)

    def _execute_join(self, plan: PlanNode) -> Iterator[Dict[str, Any]]:
        """Execute regular join."""
        left_plan = plan.children[0]
        right_plan = plan.children[1]

        # Nested loop join (simplified)
        left_results = list(self._execute_streamed(left_plan))

        for left_row in left_results:
            for right_row in self._execute_streamed(right_plan):
                # Merge rows
                merged = {**left_row, **right_row}
                yield merged

    def _execute_geodesic_join(self, plan: PlanNode) -> Iterator[Dict[str, Any]]:
        """Execute geodesic join."""
        left_plan = plan.children[0]
        right_plan = plan.children[1]

        distance_threshold = plan.metadata['distance_threshold']
        left_point_col = plan.metadata['left_point']
        right_point_col = plan.metadata['right_point']

        # Get distance kernel
        distance_fn = self.kernel_registry.get('poincare_distance')
        if not distance_fn:
            raise ValueError("Poincaré distance kernel not found")

        # Nested loop with distance check
        left_results = list(self._execute_streamed(left_plan))

        for left_row in left_results:
            left_point = left_row.get(left_point_col, (0.0, 0.0))

            for right_row in self._execute_streamed(right_plan):
                right_point = right_row.get(right_point_col, (0.0, 0.0))

                # Compute distance
                distance = distance_fn(left_point, right_point)

                if distance <= distance_threshold:
                    # Merge rows
                    merged = {**left_row, **right_row}
                    merged['_join_distance'] = distance
                    yield merged

    def _execute_limit(self, plan: PlanNode) -> Iterator[Dict[str, Any]]:
        """Execute limit."""
        input_plan = plan.children[0]
        limit = plan.metadata['limit']

        count = 0
        for row in self._execute_streamed(input_plan):
            if count >= limit:
                break
            yield row
            count += 1


class VectorizedExecutor(Executor):
    """
    Vectorized executor for batch operations.

    Uses numpy for efficient distance computations.
    """

    def __init__(self, context: ExecutionContext):
        super().__init__(context)
        self._has_numpy = False

        try:
            import numpy as np
            self._has_numpy = True
            self._np = np
        except ImportError:
            logger.warning("NumPy not available, falling back to scalar execution")

    def _execute_geodesic_join(self, plan: PlanNode) -> Iterator[Dict[str, Any]]:
        """Execute geodesic join with vectorization."""
        if not self._has_numpy or not self.context.use_vectorization:
            # Fall back to scalar execution
            yield from super()._execute_geodesic_join(plan)
            return

        left_plan = plan.children[0]
        right_plan = plan.children[1]

        distance_threshold = plan.metadata['distance_threshold']
        left_point_col = plan.metadata['left_point']
        right_point_col = plan.metadata['right_point']

        # Materialize both sides
        left_results = list(self._execute_streamed(left_plan))
        right_results = list(self._execute_streamed(right_plan))

        if not left_results or not right_results:
            return

        # Extract points as numpy arrays
        left_points = self._np.array([
            row.get(left_point_col, (0.0, 0.0))
            for row in left_results
        ])

        right_points = self._np.array([
            row.get(right_point_col, (0.0, 0.0))
            for row in right_results
        ])

        # Compute all pairwise distances (vectorized)
        distances = self._compute_pairwise_distances(left_points, right_points)

        # Find pairs within threshold
        matches = self._np.where(distances <= distance_threshold)

        # Yield matching pairs
        for left_idx, right_idx in zip(matches[0], matches[1]):
            merged = {**left_results[left_idx], **right_results[right_idx]}
            merged['_join_distance'] = float(distances[left_idx, right_idx])
            yield merged

    def _compute_pairwise_distances(self, left_points, right_points):
        """Compute pairwise Poincaré distances (vectorized)."""
        # Expand dimensions for broadcasting
        left = left_points[:, self._np.newaxis, :]  # (n, 1, 2)
        right = right_points[self._np.newaxis, :, :]  # (1, m, 2)

        # Euclidean distance squared
        diff = left - right
        dist_sq = self._np.sum(diff * diff, axis=2)

        # Norms squared
        left_norm_sq = self._np.sum(left_points * left_points, axis=1, keepdims=True)
        right_norm_sq = self._np.sum(right_points * right_points, axis=1, keepdims=True).T

        # Poincaré distance formula
        numerator = 2 * dist_sq
        denominator = (1 - left_norm_sq) * (1 - right_norm_sq)

        # Avoid division by zero
        denominator = self._np.maximum(denominator, 1e-10)

        distances = self._np.arccosh(1 + numerator / denominator)

        return distances


# Export public API
__all__ = [
    'Executor',
    'VectorizedExecutor',
    'ExecutionContext',
    'ExecutionMode',
    'KernelRegistry',
    'KERNEL_REGISTRY'
]
