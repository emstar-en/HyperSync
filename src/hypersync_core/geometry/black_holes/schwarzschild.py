"""
Schwarzschild Black Hole Geometry

This module implements the Schwarzschild solution to Einstein's field equations,
describing the spacetime geometry around a non-rotating, spherically symmetric
mass (black hole).

The Schwarzschild metric in standard coordinates (t, r, θ, φ):
    ds² = -(1 - r_s/r)dt² + (1 - r_s/r)⁻¹dr² + r²(dθ² + sin²θ dφ²)

where r_s = 2GM/c² is the Schwarzschild radius (event horizon).

Key Properties:
- Event horizon at r = r_s = 2GM/c²
- Singularity at r = 0
- Vacuum solution (T_μν = 0)
- Ricci tensor vanishes everywhere except at r = 0
- Constant sectional curvature at large r

References:
- Misner, Thorne & Wheeler "Gravitation" (1973)
- Carroll "Spacetime and Geometry" (2004)
- Wald "General Relativity" (1984)
"""

import numpy as np
from typing import Optional, Union, Tuple, Dict, Any
import warnings

# Physical constants (in SI units)
G = 6.67430e-11  # Gravitational constant (m³ kg⁻¹ s⁻²)
C = 299792458.0  # Speed of light (m/s)


class SchwarzschildGeometry:
    """
    Schwarzschild spacetime geometry implementation.
    
    This class provides methods for computing metric tensors, geodesics,
    curvature tensors, and physical effects in Schwarzschild spacetime.
    
    Attributes:
        mass (float): Black hole mass in kg
        r_s (float): Schwarzschild radius in meters
        use_geometric_units (bool): Use G=c=1 units if True
    """
    
    def __init__(self, mass: float, use_geometric_units: bool = False):
        """
        Initialize Schwarzschild geometry.
        
        Args:
            mass: Black hole mass in kg (or in solar masses if geometric units)
            use_geometric_units: If True, use G=c=1 (set mass = 1 for solar mass)
        """
        self.mass = mass
        self.use_geometric_units = use_geometric_units
        
        if use_geometric_units:
            self.r_s = 2.0 * mass  # G=c=1
        else:
            self.r_s = 2.0 * G * mass / (C ** 2)
    
    def compute_metric_tensor(self, r: float, theta: float, phi: float = 0.0) -> np.ndarray:
        """
        Compute Schwarzschild metric tensor g_μν at spacetime point.
        
        The metric in standard Schwarzschild coordinates:
            g_tt = -(1 - r_s/r)
            g_rr = (1 - r_s/r)⁻¹
            g_θθ = r²
            g_φφ = r²sin²θ
        
        Args:
            r: Radial coordinate (must be > 0)
            theta: Polar angle [0, π]
            phi: Azimuthal angle [0, 2π]
            
        Returns:
            4x4 metric tensor array
            
        Raises:
            ValueError: If r <= 0
            
        Example:
            >>> geom = SchwarzschildGeometry(mass=1.989e30)  # Solar mass
            >>> g = geom.compute_metric_tensor(r=1e7, theta=np.pi/2)
            >>> print(g[0,0])  # g_tt
        """
        if r <= 0:
            raise ValueError(f"Radial coordinate must be positive, got r={r}")
        
        f = 1.0 - self.r_s / r
        
        g = np.zeros((4, 4), dtype=np.float64)
        g[0, 0] = -f  # g_tt
        g[1, 1] = 1.0 / f if f != 0 else np.inf  # g_rr
        g[2, 2] = r ** 2  # g_θθ
        g[3, 3] = r ** 2 * np.sin(theta) ** 2  # g_φφ
        
        return g
    
    def compute_inverse_metric(self, r: float, theta: float, phi: float = 0.0) -> np.ndarray:
        """
        Compute inverse metric tensor g^μν.
        
        Args:
            r: Radial coordinate
            theta: Polar angle
            phi: Azimuthal angle
            
        Returns:
            4x4 inverse metric tensor
        """
        if r <= 0:
            raise ValueError(f"Radial coordinate must be positive, got r={r}")
        
        f = 1.0 - self.r_s / r
        
        g_inv = np.zeros((4, 4), dtype=np.float64)
        g_inv[0, 0] = -1.0 / f if f != 0 else 0.0  # g^tt
        g_inv[1, 1] = f  # g^rr
        g_inv[2, 2] = 1.0 / (r ** 2)  # g^θθ
        g_inv[3, 3] = 1.0 / (r ** 2 * np.sin(theta) ** 2) if np.sin(theta) != 0 else np.inf  # g^φφ
        
        return g_inv
    
    def compute_christoffel_symbols(self, r: float, theta: float, phi: float = 0.0) -> np.ndarray:
        """
        Compute Christoffel symbols Γ^μ_νσ for geodesic equations.
        
        The Christoffel symbols encode the connection and are used in
        geodesic equations: d²x^μ/dλ² + Γ^μ_νσ (dx^ν/dλ)(dx^σ/dλ) = 0
        
        Non-zero components in Schwarzschild:
            Γ^t_tr = r_s/(2r(r-r_s))
            Γ^r_tt = r_s(r-r_s)/(2r³)
            Γ^r_rr = -r_s/(2r(r-r_s))
            Γ^r_θθ = -(r-r_s)
            Γ^r_φφ = -(r-r_s)sin²θ
            Γ^θ_rθ = 1/r
            Γ^θ_φφ = -sinθ cosθ
            Γ^φ_rφ = 1/r
            Γ^φ_θφ = cosθ/sinθ
        
        Args:
            r: Radial coordinate
            theta: Polar angle
            phi: Azimuthal angle
            
        Returns:
            4x4x4 Christoffel symbol array
        """
        if r <= 0:
            raise ValueError(f"Radial coordinate must be positive, got r={r}")
        if r <= self.r_s:
            warnings.warn(f"Computing Christoffel symbols inside event horizon (r={r:.2e}, r_s={self.r_s:.2e})")
        
        Gamma = np.zeros((4, 4, 4), dtype=np.float64)
        
        f = 1.0 - self.r_s / r
        
        # Γ^t components
        if f != 0:
            Gamma[0, 0, 1] = Gamma[0, 1, 0] = self.r_s / (2.0 * r * (r - self.r_s))
        
        # Γ^r components
        Gamma[1, 0, 0] = self.r_s * (r - self.r_s) / (2.0 * r ** 3)
        if f != 0:
            Gamma[1, 1, 1] = -self.r_s / (2.0 * r * (r - self.r_s))
        Gamma[1, 2, 2] = -(r - self.r_s)
        Gamma[1, 3, 3] = -(r - self.r_s) * np.sin(theta) ** 2
        
        # Γ^θ components
        Gamma[2, 1, 2] = Gamma[2, 2, 1] = 1.0 / r
        Gamma[2, 3, 3] = -np.sin(theta) * np.cos(theta)
        
        # Γ^φ components
        Gamma[3, 1, 3] = Gamma[3, 3, 1] = 1.0 / r
        if np.sin(theta) != 0:
            Gamma[3, 2, 3] = Gamma[3, 3, 2] = np.cos(theta) / np.sin(theta)
        
        return Gamma
    
    def compute_riemann_tensor(self, r: float, theta: float, phi: float = 0.0) -> np.ndarray:
        """
        Compute Riemann curvature tensor R^μ_νσλ.
        
        The Riemann tensor characterizes the curvature of spacetime.
        
        Args:
            r: Radial coordinate
            theta: Polar angle
            phi: Azimuthal angle
            
        Returns:
            4x4x4x4 Riemann tensor array
            
        Note:
            This is a simplified computation. Full tensor has many components.
        """
        # Simplified implementation - returns key components
        R = np.zeros((4, 4, 4, 4), dtype=np.float64)
        
        # For Schwarzschild, many components can be expressed in terms of r_s and r
        # This is a placeholder for the most important components
        
        if r > self.r_s:
            factor = self.r_s / (r ** 3)
            # R^t_rtr component (example)
            R[0, 1, 0, 1] = factor
        
        return R
    
    def compute_ricci_tensor(self, r: float, theta: float, phi: float = 0.0) -> np.ndarray:
        """
        Compute Ricci tensor R_μν (identically zero for vacuum).
        
        For Schwarzschild spacetime (vacuum solution), R_μν = 0 everywhere
        except at the singularity r=0.
        
        Args:
            r: Radial coordinate
            theta: Polar angle
            phi: Azimuthal angle
            
        Returns:
            4x4 Ricci tensor (all zeros for r > 0)
        """
        # Vacuum solution: Ricci tensor vanishes
        return np.zeros((4, 4), dtype=np.float64)
    
    def compute_weyl_tensor(self, r: float, theta: float, phi: float = 0.0) -> np.ndarray:
        """
        Compute Weyl conformal curvature tensor C_μνσλ.
        
        For Schwarzschild, the Weyl tensor equals the Riemann tensor
        since the Ricci tensor vanishes.
        
        Args:
            r: Radial coordinate
            theta: Polar angle
            phi: Azimuthal angle
            
        Returns:
            4x4x4x4 Weyl tensor array
        """
        # For vacuum solutions: C = R (since Ricci = 0)
        return self.compute_riemann_tensor(r, theta, phi)
    
    def compute_kretschmann_scalar(self, r: float) -> float:
        """
        Compute Kretschmann scalar K = R_μνσλ R^μνσλ (curvature invariant).
        
        The Kretschmann scalar is a curvature invariant that characterizes
        tidal forces. It diverges at the singularity r=0.
        
        Mathematical formula:
            K = 48 * (r_s)² / r⁶
        
        Args:
            r: Radial coordinate
            
        Returns:
            Kretschmann scalar value
            
        Example:
            >>> geom = SchwarzschildGeometry(mass=1.989e30)
            >>> K = geom.compute_kretschmann_scalar(r=1e7)
        """
        if r <= 0:
            return np.inf
        
        return 48.0 * (self.r_s ** 2) / (r ** 6)
    
    def compute_event_horizon_properties(self) -> Dict[str, float]:
        """
        Compute event horizon properties (radius, area, surface gravity).
        
        Returns:
            Dictionary with:
                - radius: Schwarzschild radius (r_s)
                - area: Horizon surface area
                - surface_gravity: Surface gravity κ
                - temperature: Hawking temperature
        """
        area = 4.0 * np.pi * (self.r_s ** 2)
        
        if self.use_geometric_units:
            kappa = 1.0 / (4.0 * self.mass)  # Surface gravity (G=c=1)
            temp = kappa / (2.0 * np.pi)  # Hawking temperature
        else:
            kappa = C ** 4 / (4.0 * G * self.mass)  # Surface gravity
            temp = kappa * 1.05457e-34 / (2.0 * np.pi * 1.38065e-23)  # Hawking temp (K)
        
        return {
            'radius': self.r_s,
            'area': area,
            'surface_gravity': kappa,
            'temperature': temp
        }
    
    def check_horizon_crossing(self, r: float) -> str:
        """
        Determine if spacetime point is inside/outside/on event horizon.
        
        Args:
            r: Radial coordinate
            
        Returns:
            'inside' if r < r_s, 'on' if r ≈ r_s, 'outside' if r > r_s
        """
        if r < self.r_s * 0.999:
            return 'inside'
        elif r < self.r_s * 1.001:
            return 'on'
        else:
            return 'outside'
    
    def compute_proper_time(self, r: float, dt: float) -> float:
        """
        Compute proper time dτ along timelike worldline.
        
        For a stationary observer at radius r:
            dτ = √(1 - r_s/r) * dt
        
        Args:
            r: Radial coordinate
            dt: Coordinate time interval
            
        Returns:
            Proper time interval
        """
        if r <= self.r_s:
            return 0.0
        
        f = 1.0 - self.r_s / r
        return np.sqrt(f) * dt
    
    def compute_gravitational_redshift(self, r1: float, r2: float) -> float:
        """
        Compute gravitational redshift z between two radii.
        
        Formula:
            1 + z = √((1 - r_s/r₂)/(1 - r_s/r₁))
        
        Args:
            r1: Source radius
            r2: Observer radius
            
        Returns:
            Redshift factor z
        """
        if r1 <= self.r_s or r2 <= self.r_s:
            return np.inf
        
        f1 = 1.0 - self.r_s / r1
        f2 = 1.0 - self.r_s / r2
        
        return np.sqrt(f2 / f1) - 1.0
    
    def compute_time_dilation(self, r: float) -> float:
        """
        Compute gravitational time dilation factor relative to infinity.
        
        Factor = √(1 - r_s/r)
        
        Args:
            r: Radial coordinate
            
        Returns:
            Time dilation factor (1.0 at infinity, 0.0 at horizon)
        """
        if r <= self.r_s:
            return 0.0
        
        return np.sqrt(1.0 - self.r_s / r)
    
    def compute_escape_velocity(self, r: float) -> float:
        """
        Compute escape velocity from given radius.
        
        Formula:
            v_esc = c * √(r_s/r)
        
        Args:
            r: Radial coordinate
            
        Returns:
            Escape velocity (approaching c as r → r_s)
        """
        if r <= self.r_s:
            return C if not self.use_geometric_units else 1.0
        
        if self.use_geometric_units:
            return np.sqrt(self.r_s / r)
        else:
            return C * np.sqrt(self.r_s / r)
    
    def compute_tidal_force(self, r: float, length: float) -> float:
        """
        Compute tidal force (Riemann curvature effect) on extended object.
        
        Approximation for radial stretching force:
            F_tidal ≈ 2 * r_s / r³ * length
        
        Args:
            r: Radial coordinate
            length: Object length
            
        Returns:
            Tidal force magnitude
        """
        if r <= 0:
            return np.inf
        
        return 2.0 * self.r_s / (r ** 3) * length
    
    def compute_distance_schwarzschild(self, r1: float, r2: float, theta: float = np.pi/2) -> float:
        """
        Compute spacetime interval between two events.
        
        For spacelike separation at fixed time and angles:
            ds² = (1 - r_s/r)⁻¹ dr²
        
        Args:
            r1: First radial coordinate
            r2: Second radial coordinate
            theta: Polar angle
            
        Returns:
            Spacetime interval
        """
        if r1 <= 0 or r2 <= 0:
            raise ValueError("Radial coordinates must be positive")
        
        # Simplified calculation for radial separation
        def integrand(r):
            if r <= self.r_s:
                return 0.0
            return 1.0 / np.sqrt(1.0 - self.r_s / r)
        
        # Numerical integration (simplified)
        n_steps = 100
        r_vals = np.linspace(r1, r2, n_steps)
        dr = (r2 - r1) / n_steps
        
        distance = np.sum([integrand(r) * dr for r in r_vals])
        return abs(distance)


# Convenience functions

def schwarzschild_radius(mass: float, use_geometric_units: bool = False) -> float:
    """
    Compute Schwarzschild radius for given mass.
    
    Args:
        mass: Black hole mass (kg or solar masses)
        use_geometric_units: Use G=c=1 if True
        
    Returns:
        Schwarzschild radius
    """
    if use_geometric_units:
        return 2.0 * mass
    else:
        return 2.0 * G * mass / (C ** 2)


def schwarzschild_metric(mass: float, r: float, theta: float, phi: float = 0.0) -> np.ndarray:
    """
    Convenience function to compute Schwarzschild metric.
    
    Args:
        mass: Black hole mass
        r: Radial coordinate
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        4x4 metric tensor
    """
    geom = SchwarzschildGeometry(mass)
    return geom.compute_metric_tensor(r, theta, phi)


def schwarzschild_christoffel(mass: float, r: float, theta: float, phi: float = 0.0) -> np.ndarray:
    """
    Convenience function to compute Christoffel symbols.
    
    Args:
        mass: Black hole mass
        r: Radial coordinate
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        4x4x4 Christoffel symbol array
    """
    geom = SchwarzschildGeometry(mass)
    return geom.compute_christoffel_symbols(r, theta, phi)


def schwarzschild_distance(mass: float, r1: float, r2: float) -> float:
    """
    Convenience function to compute distance between radii.
    
    Args:
        mass: Black hole mass
        r1: First radius
        r2: Second radius
        
    Returns:
        Spacetime interval
    """
    geom = SchwarzschildGeometry(mass)
    return geom.compute_distance_schwarzschild(r1, r2)
