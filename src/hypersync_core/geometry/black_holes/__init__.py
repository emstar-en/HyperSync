"""
Black Hole Geometries Module

This package provides implementations of black hole spacetime geometries,
including Schwarzschild (non-rotating) and Kerr (rotating) black holes.

Main Components:
- schwarzschild: Non-rotating black hole geometry
- kerr: Rotating black hole geometry
"""

from .schwarzschild import (
    SchwarzschildGeometry,
    schwarzschild_radius,
    schwarzschild_metric,
    schwarzschild_christoffel,
    schwarzschild_distance,
)

__all__ = [
    'SchwarzschildGeometry',
    'schwarzschild_radius',
    'schwarzschild_metric',
    'schwarzschild_christoffel',
    'schwarzschild_distance',
]
