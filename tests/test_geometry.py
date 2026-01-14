"""Unit tests for geometry operations."""

import numpy as np
import pytest
from hypersync_core.geometry import (
    hyperbolic_distance,
    hyperbolic_exp_map,
    hyperbolic_log_map,
    spherical_distance,
    spherical_exp_map,
    spherical_log_map,
    spherical_geodesic_midpoint,
)


class TestHyperbolicGeometry:
    """Test hyperbolic geometry operations."""
    
    def test_hyperbolic_distance_zero(self):
        """Test distance from point to itself is zero."""
        x = np.array([0.1, 0.2, 0.3])
        distance = hyperbolic_distance(x, x)
        assert abs(distance) < 1e-10
    
    def test_hyperbolic_distance_symmetric(self):
        """Test distance is symmetric."""
        x = np.array([0.1, 0.2, 0.3])
        y = np.array([0.4, 0.1, 0.2])
        d1 = hyperbolic_distance(x, y)
        d2 = hyperbolic_distance(y, x)
        assert abs(d1 - d2) < 1e-10
    
    def test_hyperbolic_exp_log_inverse(self):
        """Test exp and log are inverses."""
        x = np.array([0.1, 0.2, 0.3])
        v = np.array([0.1, 0.0, 0.0])
        
        # exp then log should give back v
        y = hyperbolic_exp_map(x, v)
        v_recovered = hyperbolic_log_map(x, y)
        
        assert np.allclose(v, v_recovered, atol=1e-9)


class TestSphericalGeometry:
    """Test spherical geometry operations."""
    
    def test_spherical_distance_orthogonal(self):
        """Test distance between orthogonal vectors is π/2."""
        x = np.array([1.0, 0.0, 0.0])
        y = np.array([0.0, 1.0, 0.0])
        distance = spherical_distance(x, y)
        assert abs(distance - np.pi / 2) < 1e-10
    
    def test_spherical_distance_antipodal(self):
        """Test distance to antipodal point is π."""
        x = np.array([1.0, 0.0, 0.0])
        y = np.array([-1.0, 0.0, 0.0])
        distance = spherical_distance(x, y)
        assert abs(distance - np.pi) < 1e-10
    
    def test_spherical_exp_log_inverse(self):
        """Test exp and log are inverses."""
        x = np.array([1.0, 0.0, 0.0])
        v = np.array([0.0, 0.5, 0.0])  # Tangent vector
        
        # exp then log should give back v
        y = spherical_exp_map(x, v)
        v_recovered = spherical_log_map(x, y)
        
        assert np.allclose(v, v_recovered, atol=1e-9)
    
    def test_spherical_midpoint(self):
        """Test midpoint is equidistant from both points."""
        x = np.array([1.0, 0.0, 0.0])
        y = np.array([0.0, 1.0, 0.0])
        
        mid = spherical_geodesic_midpoint(x, y)
        
        d1 = spherical_distance(x, mid)
        d2 = spherical_distance(mid, y)
        
        assert abs(d1 - d2) < 1e-10
        assert abs(np.linalg.norm(mid) - 1.0) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
