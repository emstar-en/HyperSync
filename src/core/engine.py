"""
Geometry Engine - Unified interface for all hyperbolic geometry operations.

Provides access to distance metrics, geodesics, curvature, and projections.
"""
import logging
import numpy as np
from typing import Tuple, List, Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class GeometryModel(Enum):
    """Supported hyperbolic geometry models."""
    POINCARE_DISK = "poincare_disk"
    POINCARE_HALF_PLANE = "poincare_half_plane"
    HYPERBOLOID = "hyperboloid"
    KLEIN = "klein"
    UPPER_HALF_SPACE = "upper_half_space"


class CurvatureType(Enum):
    """Types of curvature calculations."""
    SCALAR = "scalar"
    GAUSSIAN = "gaussian"
    RICCI = "ricci"
    MEAN = "mean"


class GeometryEngine:
    """
    Unified geometry engine for hyperbolic operations.

    Responsibilities:
    - Compute distances in various models
    - Generate geodesic paths
    - Calculate curvatures
    - Project between models
    - Provide geometric primitives
    """

    def __init__(self):
        self._metrics = None
        self._geodesics = None
        self._curvature = None
        self._projections = None

        # Lazy load modules
        self._initialize_modules()

    def _initialize_modules(self):
        """Initialize geometry modules."""
        from hypersync.geometry.metrics import HyperbolicMetrics
        from hypersync.geometry.geodesics import GeodesicComputer
        from hypersync.geometry.curvature import CurvatureComputer
        from hypersync.geometry.projections import ProjectionRegistry

        self._metrics = HyperbolicMetrics()
        self._geodesics = GeodesicComputer()
        self._curvature = CurvatureComputer()
        self._projections = ProjectionRegistry()

        logger.info("Geometry engine initialized")

    # ========================================================================
    # Distance Calculations
    # ========================================================================

    def compute_distance(
        self,
        point_a: Tuple,
        point_b: Tuple,
        model: str = "poincare_disk"
    ) -> float:
        """
        Compute hyperbolic distance between two points.

        Args:
            point_a: First point coordinates
            point_b: Second point coordinates
            model: Geometry model to use

        Returns:
            Hyperbolic distance
        """
        model_enum = GeometryModel(model)

        if model_enum == GeometryModel.POINCARE_DISK:
            return self._metrics.poincare_distance(point_a, point_b)
        elif model_enum == GeometryModel.HYPERBOLOID:
            return self._metrics.hyperboloid_distance(point_a, point_b)
        elif model_enum == GeometryModel.KLEIN:
            return self._metrics.klein_distance(point_a, point_b)
        elif model_enum == GeometryModel.UPPER_HALF_SPACE:
            return self._metrics.upper_half_space_distance(point_a, point_b)
        else:
            raise ValueError(f"Unsupported model: {model}")

    def poincare_distance(self, z1: Tuple[float, float], z2: Tuple[float, float]) -> float:
        """Compute distance in Poincaré disk model."""
        return self._metrics.poincare_distance(z1, z2)

    def hyperboloid_distance(self, p1: Tuple, p2: Tuple) -> float:
        """Compute distance in hyperboloid model."""
        return self._metrics.hyperboloid_distance(p1, p2)

    def klein_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Compute distance in Klein model."""
        return self._metrics.klein_distance(p1, p2)

    # ========================================================================
    # Geodesic Computation
    # ========================================================================

    def compute_geodesic(
        self,
        start: Tuple,
        end: Tuple,
        model: str = "poincare_disk",
        num_points: int = 50
    ) -> List[Tuple]:
        """
        Compute geodesic path between two points.

        Args:
            start: Starting point
            end: Ending point
            model: Geometry model
            num_points: Number of points along path

        Returns:
            List of points along geodesic
        """
        model_enum = GeometryModel(model)

        if model_enum == GeometryModel.POINCARE_DISK:
            return self._geodesics.poincare_geodesic(start, end, num_points)
        elif model_enum == GeometryModel.HYPERBOLOID:
            return self._geodesics.hyperboloid_geodesic(start, end, num_points)
        else:
            raise ValueError(f"Geodesic not implemented for model: {model}")

    def parallel_transport(
        self,
        vector: Tuple,
        along_geodesic: List[Tuple],
        model: str = "poincare_disk"
    ) -> List[Tuple]:
        """
        Parallel transport a vector along a geodesic.

        Args:
            vector: Initial vector
            along_geodesic: Geodesic path
            model: Geometry model

        Returns:
            Transported vectors at each point
        """
        return self._geodesics.parallel_transport(vector, along_geodesic, model)

    # ========================================================================
    # Curvature Calculations
    # ========================================================================

    def compute_curvature(
        self,
        point: Tuple,
        curvature_type: str = "scalar",
        metric_tensor: Optional[np.ndarray] = None
    ) -> float:
        """
        Compute curvature at a point.

        Args:
            point: Point coordinates
            curvature_type: Type of curvature
            metric_tensor: Optional metric tensor

        Returns:
            Curvature value
        """
        curv_type = CurvatureType(curvature_type)

        if curv_type == CurvatureType.SCALAR:
            return self._curvature.scalar_curvature(point, metric_tensor)
        elif curv_type == CurvatureType.GAUSSIAN:
            return self._curvature.gaussian_curvature(point)
        elif curv_type == CurvatureType.RICCI:
            return self._curvature.ricci_curvature(point, metric_tensor)
        else:
            raise ValueError(f"Unsupported curvature type: {curvature_type}")

    def compute_scalar_curvature(
        self,
        point: Tuple,
        metric_tensor: Optional[np.ndarray] = None
    ) -> float:
        """Compute scalar curvature."""
        return self._curvature.scalar_curvature(point, metric_tensor)

    def compute_gaussian_curvature(self, point: Tuple) -> float:
        """Compute Gaussian curvature."""
        return self._curvature.gaussian_curvature(point)

    def ricci_flow_step(
        self,
        metric: np.ndarray,
        dt: float = 0.01
    ) -> np.ndarray:
        """
        Evolve metric under Ricci flow.

        Args:
            metric: Current metric tensor
            dt: Time step

        Returns:
            Evolved metric tensor
        """
        return self._curvature.ricci_flow_step(metric, dt)

    # ========================================================================
    # Projections
    # ========================================================================

    def project(
        self,
        point: Tuple,
        from_model: str,
        to_model: str
    ) -> Tuple:
        """
        Project point from one model to another.

        Args:
            point: Point in source model
            from_model: Source geometry model
            to_model: Target geometry model

        Returns:
            Point in target model
        """
        return self._projections.project(point, from_model, to_model)

    def project_batch(
        self,
        points: List[Tuple],
        from_model: str,
        to_model: str
    ) -> List[Tuple]:
        """
        Project multiple points.

        Args:
            points: Points in source model
            from_model: Source geometry model
            to_model: Target geometry model

        Returns:
            Points in target model
        """
        return [self.project(p, from_model, to_model) for p in points]

    # ========================================================================
    # Geometric Metrics for Telemetry
    # ========================================================================

    def compute_geometric_metrics(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute comprehensive geometric metrics for telemetry.

        Args:
            state: Current system state with positions

        Returns:
            Dictionary of geometric metrics
        """
        metrics = {}

        # Extract positions
        positions = state.get("positions", [])

        if len(positions) >= 2:
            # Compute pairwise distances
            distances = []
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    dist = self.poincare_distance(positions[i], positions[j])
                    distances.append(dist)

            metrics["mean_distance"] = np.mean(distances) if distances else 0.0
            metrics["max_distance"] = np.max(distances) if distances else 0.0
            metrics["min_distance"] = np.min(distances) if distances else 0.0

        # Compute curvatures
        if positions:
            curvatures = [self.compute_gaussian_curvature(p) for p in positions]
            metrics["mean_curvature"] = np.mean(curvatures)

        return metrics

    def find_optimal_placement(
        self,
        constraints: Dict[str, Any],
        curvature_field: Optional[np.ndarray] = None
    ) -> Tuple:
        """
        Find optimal placement position given constraints.

        Args:
            constraints: Placement constraints
            curvature_field: Optional curvature field

        Returns:
            Optimal position
        """
        # Simple implementation - can be enhanced
        # Place at origin if no constraints
        if not constraints:
            return (0.0, 0.0)

        # Use curvature field if available
        if curvature_field is not None:
            # Find minimum curvature region
            min_idx = np.argmin(curvature_field)
            # Convert to coordinates (simplified)
            return (0.0, 0.0)

        return (0.0, 0.0)

    def get_status(self) -> Dict[str, Any]:
        """Get geometry engine status."""
        return {
            "initialized": all([
                self._metrics is not None,
                self._geodesics is not None,
                self._curvature is not None,
                self._projections is not None
            ]),
            "supported_models": [m.value for m in GeometryModel],
            "supported_curvature_types": [c.value for c in CurvatureType]
        }


# Global geometry engine instance
_geometry_engine: Optional[GeometryEngine] = None


def get_geometry_engine() -> GeometryEngine:
    """Get the global geometry engine instance."""
    global _geometry_engine
    if _geometry_engine is None:
        _geometry_engine = GeometryEngine()
    return _geometry_engine
