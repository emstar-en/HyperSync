"""
Unit Tests for Schwarzschild Black Hole Geometry

This module contains comprehensive tests for Schwarzschild spacetime geometry
implementation, including metric tensors, geodesics, and physical effects.
"""

import pytest
import numpy as np
from src.hypersync_core.geometry.black_holes import (
    SchwarzschildGeometry,
    schwarzschild_radius,
    schwarzschild_metric,
    schwarzschild_christoffel,
    schwarzschild_distance,
)


class TestSchwarzschildGeometry:
    """Tests for Schwarzschild geometry."""
    
    def test_schwarzschild_radius(self):
        """Test Schwarzschild radius calculation."""
        # Solar mass black hole
        M_sun = 1.989e30  # kg
        geom = SchwarzschildGeometry(mass=M_sun)
        
        # Schwarzschild radius should be about 2953 meters
        expected_rs = 2.0 * 6.67430e-11 * M_sun / (299792458.0 ** 2)
        assert np.allclose(geom.r_s, expected_rs, rtol=1e-6)
    
    def test_metric_tensor_shape(self):
        """Test metric tensor has correct shape."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        g = geom.compute_metric_tensor(r=10.0, theta=np.pi/2)
        
        assert g.shape == (4, 4), "Metric should be 4x4"
    
    def test_metric_tensor_diagonal(self):
        """Test metric tensor is diagonal."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        g = geom.compute_metric_tensor(r=10.0, theta=np.pi/2)
        
        # Check off-diagonal elements are zero
        for i in range(4):
            for j in range(4):
                if i != j:
                    assert np.allclose(g[i, j], 0.0), f"Off-diagonal element g[{i},{j}] should be 0"
    
    def test_metric_at_infinity(self):
        """Test metric approaches Minkowski at large r."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        r_large = 1000.0
        g = geom.compute_metric_tensor(r=r_large, theta=np.pi/2)
        
        # At large r, metric should approach Minkowski: diag(-1, 1, r^2, r^2)
        assert np.allclose(g[0, 0], -1.0, atol=1e-3), "g_tt should approach -1"
        assert np.allclose(g[1, 1], 1.0, atol=1e-3), "g_rr should approach 1"
    
    def test_inverse_metric(self):
        """Test inverse metric computation."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        r = 10.0
        theta = np.pi / 2
        
        g = geom.compute_metric_tensor(r, theta)
        g_inv = geom.compute_inverse_metric(r, theta)
        
        # Check g * g_inv = I (for diagonal metric)
        for i in range(4):
            product = g[i, i] * g_inv[i, i]
            assert np.allclose(product, 1.0, atol=1e-10), f"g[{i},{i}] * g_inv[{i},{i}] should be 1"
    
    def test_christoffel_symbols_shape(self):
        """Test Christoffel symbols have correct shape."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        Gamma = geom.compute_christoffel_symbols(r=10.0, theta=np.pi/2)
        
        assert Gamma.shape == (4, 4, 4), "Christoffel symbols should be 4x4x4"
    
    def test_christoffel_symmetry(self):
        """Test Christoffel symbols are symmetric in lower indices."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        Gamma = geom.compute_christoffel_symbols(r=10.0, theta=np.pi/2)
        
        # Check symmetry: Γ^μ_νσ = Γ^μ_σν
        for mu in range(4):
            for nu in range(4):
                for sigma in range(4):
                    assert np.allclose(Gamma[mu, nu, sigma], Gamma[mu, sigma, nu]), \
                        f"Christoffel should be symmetric: Γ^{mu}_{nu}{sigma} != Γ^{mu}_{sigma}{nu}"
    
    def test_ricci_tensor_vacuum(self):
        """Test Ricci tensor vanishes (vacuum solution)."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        R = geom.compute_ricci_tensor(r=10.0, theta=np.pi/2)
        
        assert np.allclose(R, 0.0), "Ricci tensor should vanish for vacuum solution"
    
    def test_kretschmann_scalar_singularity(self):
        """Test Kretschmann scalar diverges at singularity."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        
        # At large r, K should be small
        K_large = geom.compute_kretschmann_scalar(r=100.0)
        
        # At small r, K should be large
        K_small = geom.compute_kretschmann_scalar(r=2.1)
        
        assert K_small > K_large, "Kretschmann scalar should increase as r decreases"
    
    def test_event_horizon_properties(self):
        """Test event horizon properties calculation."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        props = geom.compute_event_horizon_properties()
        
        assert 'radius' in props
        assert 'area' in props
        assert 'surface_gravity' in props
        assert 'temperature' in props
        
        assert props['radius'] == geom.r_s
        assert props['area'] > 0
    
    def test_horizon_crossing_detection(self):
        """Test horizon crossing detection."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        
        assert geom.check_horizon_crossing(r=10.0) == 'outside'
        assert geom.check_horizon_crossing(r=geom.r_s) == 'on'
        assert geom.check_horizon_crossing(r=1.0) == 'inside'
    
    def test_time_dilation(self):
        """Test time dilation factor."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        
        # At infinity, time dilation factor should be 1
        factor_large = geom.compute_time_dilation(r=1000.0)
        assert np.allclose(factor_large, 1.0, atol=1e-3)
        
        # At horizon, time dilation factor should be 0
        factor_horizon = geom.compute_time_dilation(r=geom.r_s)
        assert np.allclose(factor_horizon, 0.0, atol=1e-10)
    
    def test_escape_velocity(self):
        """Test escape velocity calculation."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        
        # At large r, escape velocity should be small
        v_large = geom.compute_escape_velocity(r=1000.0)
        assert v_large < 0.1  # In geometric units (c=1)
        
        # At horizon, escape velocity should equal c
        v_horizon = geom.compute_escape_velocity(r=geom.r_s)
        assert np.allclose(v_horizon, 1.0, atol=1e-10)
    
    def test_gravitational_redshift(self):
        """Test gravitational redshift calculation."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        
        # Light escaping from closer to horizon should be more redshifted
        z1 = geom.compute_gravitational_redshift(r1=3.0, r2=100.0)
        z2 = geom.compute_gravitational_redshift(r1=10.0, r2=100.0)
        
        assert z1 > z2, "Redshift from closer point should be larger"
    
    def test_proper_time(self):
        """Test proper time calculation."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        dt = 1.0
        
        # At large r, proper time approaches coordinate time
        dtau_large = geom.compute_proper_time(r=1000.0, dt=dt)
        assert np.allclose(dtau_large, dt, atol=1e-3)
        
        # At horizon, proper time is zero
        dtau_horizon = geom.compute_proper_time(r=geom.r_s, dt=dt)
        assert np.allclose(dtau_horizon, 0.0, atol=1e-10)
    
    def test_tidal_force(self):
        """Test tidal force calculation."""
        geom = SchwarzschildGeometry(mass=1.0, use_geometric_units=True)
        length = 1.0
        
        # Tidal force should increase as r decreases
        F1 = geom.compute_tidal_force(r=10.0, length=length)
        F2 = geom.compute_tidal_force(r=5.0, length=length)
        
        assert F2 > F1, "Tidal force should increase closer to singularity"


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_schwarzschild_radius_function(self):
        """Test schwarzschild_radius convenience function."""
        mass = 1.0
        r_s = schwarzschild_radius(mass, use_geometric_units=True)
        
        expected = 2.0 * mass
        assert np.allclose(r_s, expected)
    
    def test_schwarzschild_metric_function(self):
        """Test schwarzschild_metric convenience function."""
        mass = 1.0
        g = schwarzschild_metric(mass, r=10.0, theta=np.pi/2)
        
        assert g.shape == (4, 4)
    
    def test_schwarzschild_christoffel_function(self):
        """Test schwarzschild_christoffel convenience function."""
        mass = 1.0
        Gamma = schwarzschild_christoffel(mass, r=10.0, theta=np.pi/2)
        
        assert Gamma.shape == (4, 4, 4)
    
    def test_schwarzschild_distance_function(self):
        """Test schwarzschild_distance convenience function."""
        mass = 1.0
        dist = schwarzschild_distance(mass, r1=10.0, r2=20.0)
        
        assert dist > 0


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
