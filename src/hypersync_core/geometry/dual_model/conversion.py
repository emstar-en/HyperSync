"""
Model Conversion and Utilities for Dual Hyperbolic Model System

This module provides utilities for converting between Lorentz and Poincaré models,
automatic model selection, and unified interfaces for hyperbolic operations.

The dual model system allows users to leverage the advantages of each model:
- Lorentz: Better numerical stability, especially for distant points
- Poincaré: Better for visualization and intuitive understanding

References:
- Anderson "Hyperbolic Geometry" (2005)
- Cannon et al. "Hyperbolic Geometry" (1997)
"""

import numpy as np
from typing import Optional, Union, Tuple, List, Dict, Any, Callable
import time
import warnings

from .lorentz import LorentzModel
from .poincare import PoincareModel


class DualModelSystem:
    """
    Unified interface for dual hyperbolic model system.
    
    This class provides automatic model selection and conversion between
    Lorentz and Poincaré models based on the operation and data characteristics.
    
    Attributes:
        dim (int): Dimension of hyperbolic space
        lorentz (LorentzModel): Lorentz model instance
        poincare (PoincareModel): Poincaré model instance
        default_model (str): Default model to use ('lorentz' or 'poincare')
    """
    
    def __init__(self, dim: int = 2, default_model: str = 'lorentz', eps: float = 1e-12):
        """
        Initialize dual model system.
        
        Args:
            dim: Dimension of hyperbolic space
            default_model: Default model ('lorentz' or 'poincare')
            eps: Numerical precision epsilon
            
        Raises:
            ValueError: If invalid default_model specified
        """
        if default_model not in ['lorentz', 'poincare']:
            raise ValueError(f"default_model must be 'lorentz' or 'poincare', got {default_model}")
        
        self.dim = dim
        self.default_model = default_model
        self.eps = eps
        
        # Initialize both models
        self.lorentz = LorentzModel(dim=dim, eps=eps)
        self.poincare = PoincareModel(dim=dim, eps=eps)
    
    def convert_between_models(self, x: np.ndarray, from_model: str, to_model: str) -> np.ndarray:
        """
        Convert point(s) between models.
        
        Supports conversions:
        - 'lorentz' -> 'poincare': Stereographic projection
        - 'poincare' -> 'lorentz': Inverse stereographic projection
        
        Args:
            x: Point(s) to convert
            from_model: Source model ('lorentz' or 'poincare')
            to_model: Target model ('lorentz' or 'poincare')
            
        Returns:
            Converted point(s)
            
        Raises:
            ValueError: If invalid model names provided
            
        Example:
            >>> system = DualModelSystem(dim=2)
            >>> x_lorentz = np.array([1.0, 0.0, 0.0])
            >>> x_poincare = system.convert_between_models(x_lorentz, 'lorentz', 'poincare')
            >>> x_back = system.convert_between_models(x_poincare, 'poincare', 'lorentz')
            >>> np.allclose(x_lorentz, x_back)
            True
        """
        if from_model == to_model:
            return x.copy()
        
        if from_model == 'lorentz' and to_model == 'poincare':
            return self.lorentz.lorentz_to_poincare(x)
        elif from_model == 'poincare' and to_model == 'lorentz':
            return self.poincare.poincare_to_lorentz(x)
        else:
            raise ValueError(f"Invalid model conversion: {from_model} -> {to_model}")
    
    def auto_select_model(self, operation: str, data: Union[np.ndarray, Tuple[np.ndarray, ...]]) -> str:
        """
        Automatically select best model for operation based on data characteristics.
        
        Selection criteria:
        - For distant points (large distances): Lorentz (better numerical stability)
        - For points near boundary: Poincaré (better for boundary analysis)
        - For visualization: Poincaré (more intuitive)
        - For high-precision calculations: Lorentz (more stable)
        - For operations near origin: Either model works well
        
        Args:
            operation: Operation name (e.g., 'distance', 'exp_map', 'parallel_transport')
            data: Input data (point or tuple of points)
            
        Returns:
            Selected model name ('lorentz' or 'poincare')
            
        Example:
            >>> system = DualModelSystem(dim=2)
            >>> x = np.array([0.95, 0.0])  # Near boundary
            >>> y = np.array([0.96, 0.0])
            >>> model = system.auto_select_model('distance', (x, y))
            >>> print(model)
            'lorentz'
        """
        # Normalize data to tuple
        if isinstance(data, np.ndarray):
            data = (data,)
        
        # Analyze data characteristics
        if data[0].shape[-1] == self.dim + 1:
            # Lorentz format (already in Lorentz model)
            return 'lorentz'
        
        # Check if points are near boundary (Poincaré model)
        max_norm = 0.0
        for x in data:
            if x.shape[-1] == self.dim:  # Poincaré format
                norm = np.max(np.linalg.norm(x, axis=-1))
                max_norm = max(max_norm, norm)
        
        # Decision rules
        if max_norm > 0.9:
            # Near boundary -> prefer Lorentz for stability
            return 'lorentz'
        
        # Check for large distances (estimate)
        if len(data) >= 2 and operation in ['distance', 'log_map', 'geodesic']:
            # Estimate distance in Poincaré model
            x, y = data[0], data[1]
            if x.shape[-1] == self.dim and y.shape[-1] == self.dim:
                diff_norm = np.linalg.norm(x - y)
                if diff_norm > 0.5 and max_norm > 0.7:
                    # Large distance with points far from origin -> Lorentz
                    return 'lorentz'
        
        # Default to configured default model
        return self.default_model
    
    def dual_model_distance(self, x: np.ndarray, y: np.ndarray, 
                           model: Optional[str] = None) -> Union[float, np.ndarray]:
        """
        Compute distance using automatically selected or specified model.
        
        Args:
            x: First point
            y: Second point
            model: Model to use (auto-selected if None)
            
        Returns:
            Hyperbolic distance
        """
        if model is None:
            model = self.auto_select_model('distance', (x, y))
        
        if model == 'lorentz':
            # Ensure points are in Lorentz format
            if x.shape[-1] == self.dim:
                x = self.poincare.poincare_to_lorentz(x)
                y = self.poincare.poincare_to_lorentz(y)
            return self.lorentz.lorentz_distance(x, y)
        else:
            # Ensure points are in Poincaré format
            if x.shape[-1] == self.dim + 1:
                x = self.lorentz.lorentz_to_poincare(x)
                y = self.lorentz.lorentz_to_poincare(y)
            return self.poincare.poincare_distance(x, y)
    
    def dual_model_geodesic(self, x: np.ndarray, y: np.ndarray, t: Union[float, np.ndarray],
                           model: Optional[str] = None) -> np.ndarray:
        """
        Compute geodesic interpolation using automatically selected or specified model.
        
        Args:
            x: Start point
            y: End point
            t: Parameter(s) in [0,1]
            model: Model to use (auto-selected if None)
            
        Returns:
            Point(s) on geodesic
        """
        if model is None:
            model = self.auto_select_model('geodesic', (x, y))
        
        if model == 'lorentz':
            if x.shape[-1] == self.dim:
                x = self.poincare.poincare_to_lorentz(x)
                y = self.poincare.poincare_to_lorentz(y)
            return self.lorentz.lorentz_geodesic(x, y, t)
        else:
            if x.shape[-1] == self.dim + 1:
                x = self.lorentz.lorentz_to_poincare(x)
                y = self.lorentz.lorentz_to_poincare(y)
            return self.poincare.poincare_geodesic(x, y, t)
    
    def dual_model_mean(self, points: np.ndarray, weights: Optional[np.ndarray] = None,
                       model: Optional[str] = None) -> np.ndarray:
        """
        Compute Fréchet mean using automatically selected or specified model.
        
        Args:
            points: Array of points
            weights: Optional weights
            model: Model to use (auto-selected if None)
            
        Returns:
            Fréchet mean
        """
        if model is None:
            model = self.auto_select_model('mean', (points,))
        
        if model == 'lorentz':
            if points.shape[-1] == self.dim:
                points = np.array([self.poincare.poincare_to_lorentz(p) for p in points])
            return self.lorentz.lorentz_mean(points, weights)
        else:
            if points.shape[-1] == self.dim + 1:
                points = np.array([self.lorentz.lorentz_to_poincare(p) for p in points])
            return self.poincare.poincare_mean(points, weights)
    
    def dual_model_interpolation(self, x: np.ndarray, y: np.ndarray, t: Union[float, np.ndarray],
                                model: Optional[str] = None) -> np.ndarray:
        """
        Smart interpolation using best model.
        
        Alias for dual_model_geodesic for consistency with naming conventions.
        """
        return self.dual_model_geodesic(x, y, t, model)
    
    def dual_model_parallel_transport(self, x: np.ndarray, y: np.ndarray, v: np.ndarray,
                                     model: Optional[str] = None) -> np.ndarray:
        """
        Parallel transport using automatically selected or specified model.
        
        Args:
            x: Source point
            y: Target point
            v: Tangent vector at x
            model: Model to use (auto-selected if None)
            
        Returns:
            Parallel transported vector at y
        """
        if model is None:
            model = self.auto_select_model('parallel_transport', (x, y))
        
        if model == 'lorentz':
            if x.shape[-1] == self.dim:
                x = self.poincare.poincare_to_lorentz(x)
                y = self.poincare.poincare_to_lorentz(y)
                # Note: tangent vector also needs transformation
                warnings.warn("Tangent vector transformation not fully implemented")
            return self.lorentz.lorentz_parallel_transport(x, y, v)
        else:
            if x.shape[-1] == self.dim + 1:
                x = self.lorentz.lorentz_to_poincare(x)
                y = self.lorentz.lorentz_to_poincare(y)
                # Note: tangent vector also needs transformation
                warnings.warn("Tangent vector transformation not fully implemented")
            return self.poincare.poincare_parallel_transport(x, y, v)
    
    def benchmark_models(self, operation: str, data: Tuple[np.ndarray, ...], 
                        n_trials: int = 100) -> Dict[str, Dict[str, float]]:
        """
        Benchmark operation performance across models.
        
        Compares execution time and numerical accuracy between Lorentz and
        Poincaré models for a given operation.
        
        Args:
            operation: Operation name ('distance', 'exp_map', etc.)
            data: Input data tuple
            n_trials: Number of trials for timing
            
        Returns:
            Dictionary with benchmark results for each model
            
        Example:
            >>> system = DualModelSystem(dim=2)
            >>> x = np.array([0.5, 0.0])
            >>> y = np.array([0.6, 0.0])
            >>> results = system.benchmark_models('distance', (x, y))
            >>> print(results['lorentz']['time'])
        """
        results = {}
        
        # Benchmark Lorentz model
        if operation == 'distance':
            x, y = data
            # Convert to Lorentz if needed
            if x.shape[-1] == self.dim:
                x_l = self.poincare.poincare_to_lorentz(x)
                y_l = self.poincare.poincare_to_lorentz(y)
            else:
                x_l, y_l = x, y
            
            # Time Lorentz
            start = time.perf_counter()
            for _ in range(n_trials):
                result_l = self.lorentz.lorentz_distance(x_l, y_l)
            time_l = (time.perf_counter() - start) / n_trials
            
            # Convert to Poincaré if needed
            if x.shape[-1] == self.dim + 1:
                x_p = self.lorentz.lorentz_to_poincare(x)
                y_p = self.lorentz.lorentz_to_poincare(y)
            else:
                x_p, y_p = x, y
            
            # Time Poincaré
            start = time.perf_counter()
            for _ in range(n_trials):
                result_p = self.poincare.poincare_distance(x_p, y_p)
            time_p = (time.perf_counter() - start) / n_trials
            
            results['lorentz'] = {'time': time_l, 'result': float(result_l)}
            results['poincare'] = {'time': time_p, 'result': float(result_p)}
            results['difference'] = abs(float(result_l) - float(result_p))
        
        return results
    
    def validate_model_consistency(self, x: np.ndarray, operation: str = 'distance',
                                  y: Optional[np.ndarray] = None, tol: float = 1e-6) -> Dict[str, Any]:
        """
        Validate that operations produce consistent results across models.
        
        Compares results from both models to ensure geometric consistency.
        
        Args:
            x: First point (in either model format)
            operation: Operation to validate
            y: Second point (for binary operations)
            tol: Tolerance for consistency check
            
        Returns:
            Validation results dictionary
            
        Example:
            >>> system = DualModelSystem(dim=2)
            >>> x = np.array([0.5, 0.0])
            >>> y = np.array([0.6, 0.0])
            >>> results = system.validate_model_consistency(x, 'distance', y)
            >>> print(results['consistent'])
        """
        validation = {'operation': operation, 'consistent': False, 'difference': None}
        
        if operation == 'distance' and y is not None:
            # Compute distance in both models
            dist_l = self.dual_model_distance(x, y, model='lorentz')
            dist_p = self.dual_model_distance(x, y, model='poincare')
            
            diff = abs(float(dist_l) - float(dist_p))
            validation['difference'] = diff
            validation['lorentz_result'] = float(dist_l)
            validation['poincare_result'] = float(dist_p)
            validation['consistent'] = diff < tol
        
        return validation
    
    def get_optimal_model(self, curvature: float = -1.0, dimension: Optional[int] = None) -> str:
        """
        Get optimal model recommendation based on curvature and dimension.
        
        Args:
            curvature: Sectional curvature (default -1.0 for standard hyperbolic)
            dimension: Space dimension (uses self.dim if None)
            
        Returns:
            Recommended model name ('lorentz' or 'poincare')
            
        Note:
            For standard hyperbolic space (curvature = -1), both models are equivalent.
            This function provides general guidance:
            - High dimensions (>10): Lorentz (better numerical properties)
            - Low dimensions (≤10): Either model works well
            - Visualization: Poincaré (more intuitive)
        """
        if dimension is None:
            dimension = self.dim
        
        if abs(curvature + 1.0) > 0.01:
            warnings.warn(f"Non-standard curvature {curvature}. Results may vary.")
        
        # High-dimensional spaces: prefer Lorentz
        if dimension > 10:
            return 'lorentz'
        
        # Default to configured default
        return self.default_model


# Convenience functions

def convert_lorentz_to_poincare(x: np.ndarray, dim: Optional[int] = None) -> np.ndarray:
    """
    Convert from Lorentz to Poincaré model.
    
    Args:
        x: Point in Lorentz model
        dim: Dimension (inferred from x if not provided)
        
    Returns:
        Point in Poincaré model
    """
    if dim is None:
        dim = x.shape[-1] - 1
    lorentz = LorentzModel(dim=dim)
    return lorentz.lorentz_to_poincare(x)


def convert_poincare_to_lorentz(x: np.ndarray, dim: Optional[int] = None) -> np.ndarray:
    """
    Convert from Poincaré to Lorentz model.
    
    Args:
        x: Point in Poincaré model
        dim: Dimension (inferred from x if not provided)
        
    Returns:
        Point in Lorentz model
    """
    if dim is None:
        dim = x.shape[-1]
    poincare = PoincareModel(dim=dim)
    return poincare.poincare_to_lorentz(x)


def auto_distance(x: np.ndarray, y: np.ndarray, dim: Optional[int] = None) -> Union[float, np.ndarray]:
    """
    Compute distance with automatic model selection.
    
    Args:
        x: First point
        y: Second point
        dim: Dimension (inferred from x if not provided)
        
    Returns:
        Hyperbolic distance
    """
    if dim is None:
        if x.shape[-1] == y.shape[-1]:
            # Assume Poincaré if same size
            dim = x.shape[-1]
        else:
            raise ValueError("Cannot infer dimension from inputs")
    
    system = DualModelSystem(dim=dim)
    return system.dual_model_distance(x, y)


def auto_geodesic(x: np.ndarray, y: np.ndarray, t: Union[float, np.ndarray],
                 dim: Optional[int] = None) -> np.ndarray:
    """
    Compute geodesic with automatic model selection.
    
    Args:
        x: Start point
        y: End point
        t: Parameter(s)
        dim: Dimension (inferred from x if not provided)
        
    Returns:
        Point(s) on geodesic
    """
    if dim is None:
        dim = x.shape[-1] if x.shape[-1] == y.shape[-1] else x.shape[-1] - 1
    
    system = DualModelSystem(dim=dim)
    return system.dual_model_geodesic(x, y, t)
