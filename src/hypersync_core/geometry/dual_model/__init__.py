"""
Dual Model System for Hyperbolic Geometry

This package provides a comprehensive dual-model system for hyperbolic geometry,
supporting both Lorentz (hyperboloid) and Poincaré (ball) models with automatic
model selection and conversion utilities.

Main Components:
- LorentzModel: Hyperboloid model implementation
- PoincareModel: Poincaré ball model implementation
- DualModelSystem: Unified interface with automatic model selection
"""

from .lorentz import (
    LorentzModel,
    lorentz_distance,
    lorentz_exp_map,
    lorentz_log_map,
)

from .poincare import (
    PoincareModel,
    poincare_distance,
    poincare_exp_map,
    poincare_log_map,
)

from .conversion import (
    DualModelSystem,
    convert_lorentz_to_poincare,
    convert_poincare_to_lorentz,
    auto_distance,
    auto_geodesic,
)

__all__ = [
    # Lorentz Model
    'LorentzModel',
    'lorentz_distance',
    'lorentz_exp_map',
    'lorentz_log_map',
    
    # Poincaré Model
    'PoincareModel',
    'poincare_distance',
    'poincare_exp_map',
    'poincare_log_map',
    
    # Dual Model System
    'DualModelSystem',
    'convert_lorentz_to_poincare',
    'convert_poincare_to_lorentz',
    'auto_distance',
    'auto_geodesic',
]
