"""Geometric Operations Module

Provides 28 Core tier geometric operations:
- 14 Hyperbolic geometry operations (ℍⁿ, κ < 0)
- 14 Spherical geometry operations (Sⁿ, κ > 0)

All operations are O(n) or O(n log n) with high precision (1e-12).
"""

from .hyperbolic import (
    hyperbolic_distance,
    hyperbolic_exp_map,
    hyperbolic_log_map,
    hyperbolic_parallel_transport,
    hyperbolic_geodesic,
    poincare_to_lorentz,
    lorentz_to_poincare,
    tangent_projection_hyperbolic,
    hyperbolic_midpoint,
    hyperbolic_retraction,
    stereographic_to_poincare,
    poincare_to_stereographic,
    hyperbolic_reflection,
    hyperbolic_interpolation,
)

from .spherical import (
    spherical_distance,
    spherical_exp_map,
    spherical_log_map,
    spherical_parallel_transport,
    spherical_geodesic,
    spherical_projection,
    tangent_projection_spherical,
    spherical_geodesic_midpoint,
    spherical_interpolation,
    spherical_retraction,
    stereographic_projection,
    inverse_stereographic,
    spherical_reflection,
    spherical_to_hyperbolic,
)

__all__ = [
    # Hyperbolic operations
    "hyperbolic_distance",
    "hyperbolic_exp_map",
    "hyperbolic_log_map",
    "hyperbolic_parallel_transport",
    "hyperbolic_geodesic",
    "poincare_to_lorentz",
    "lorentz_to_poincare",
    "tangent_projection_hyperbolic",
    "hyperbolic_midpoint",
    "hyperbolic_retraction",
    "stereographic_to_poincare",
    "poincare_to_stereographic",
    "hyperbolic_reflection",
    "hyperbolic_interpolation",
    # Spherical operations
    "spherical_distance",
    "spherical_exp_map",
    "spherical_log_map",
    "spherical_parallel_transport",
    "spherical_geodesic",
    "spherical_projection",
    "tangent_projection_spherical",
    "spherical_geodesic_midpoint",
    "spherical_interpolation",
    "spherical_retraction",
    "stereographic_projection",
    "inverse_stereographic",
    "spherical_reflection",
    "spherical_to_hyperbolic",
]
