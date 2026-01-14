"""Basic Geometry Example

Demonstrates hyperbolic and spherical geometry operations.
"""

import numpy as np
from hypersync_core.geometry import (
    hyperbolic_distance,
    hyperbolic_exp_map,
    spherical_distance,
    spherical_interpolation,
)


def hyperbolic_example():
    """Demonstrate hyperbolic geometry operations."""
    print("=== Hyperbolic Geometry ===")
    
    # Two points in Poincaré ball
    x = np.array([0.1, 0.2, 0.3])
    y = np.array([0.4, 0.1, 0.2])
    
    # Compute hyperbolic distance
    distance = hyperbolic_distance(x, y)
    print(f"Hyperbolic distance: {distance:.4f}")
    
    # Exponential map
    v = np.array([0.1, 0.0, 0.0])  # Tangent vector
    z = hyperbolic_exp_map(x, v)
    print(f"Point on geodesic: {z}")
    
    print()


def spherical_example():
    """Demonstrate spherical geometry operations."""
    print("=== Spherical Geometry ===")
    
    # Two points on unit sphere
    x = np.array([1.0, 0.0, 0.0])
    y = np.array([0.0, 1.0, 0.0])
    
    # Great circle distance
    distance = spherical_distance(x, y)
    print(f"Spherical distance: {distance:.4f} (π/2 ≈ {np.pi/2:.4f})")
    
    # Slerp interpolation
    midpoint = spherical_interpolation(x, y, t=0.5)
    print(f"Midpoint: {midpoint}")
    print(f"Midpoint norm: {np.linalg.norm(midpoint):.4f} (should be 1.0)")
    
    print()


if __name__ == "__main__":
    hyperbolic_example()
    spherical_example()
    print("✓ All examples completed successfully!")
