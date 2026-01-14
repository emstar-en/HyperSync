"""
Unit Tests for Dual Model System (Lorentz and Poincaré Models)

This module contains comprehensive tests for the dual model system implementation,
including Lorentz hyperboloid model, Poincaré ball model, and model conversion utilities.
"""

import pytest
import numpy as np
from src.hypersync_core.geometry.dual_model import (
    LorentzModel,
    PoincareModel,
    DualModelSystem,
    convert_lorentz_to_poincare,
    convert_poincare_to_lorentz,
    auto_distance,
)


class TestLorentzModel:
    """Tests for Lorentz hyperboloid model."""
    
    def test_lorentz_inner_product(self):
        """Test Lorentz inner product computation."""
        model = LorentzModel(dim=2)
        x = np.array([1.0, 0.0, 0.0])  # Origin
        y = np.array([1.0, 0.0, 0.0])
        
        inner_prod = model.lorentz_inner_product(x, y)
        assert np.allclose(inner_prod, -1.0), "Origin should have inner product -1"
    
    def test_lorentz_distance_origin(self):
        """Test distance at origin."""
        model = LorentzModel(dim=2)
        x = np.array([1.0, 0.0, 0.0])
        y = np.array([1.0, 0.0, 0.0])
        
        dist = model.lorentz_distance(x, y)
        assert np.allclose(dist, 0.0, atol=1e-6), "Distance to self should be 0"
    
    def test_lorentz_distance_symmetry(self):
        """Test distance symmetry."""
        model = LorentzModel(dim=2)
        x = np.array([1.0, 0.0, 0.0])
        y = np.array([np.cosh(1.0), np.sinh(1.0), 0.0])
        
        dist_xy = model.lorentz_distance(x, y)
        dist_yx = model.lorentz_distance(y, x)
        
        assert np.allclose(dist_xy, dist_yx), "Distance should be symmetric"
    
    def test_lorentz_exp_log_inverse(self):
        """Test that exp and log are inverse operations."""
        model = LorentzModel(dim=2)
        x = np.array([1.0, 0.0, 0.0])
        y = np.array([np.cosh(1.0), np.sinh(1.0), 0.0])
        
        # Compute log map
        v = model.lorentz_log_map(x, y)
        
        # Apply exp map
        y_reconstructed = model.lorentz_exp_map(x, v)
        
        assert np.allclose(y, y_reconstructed, atol=1e-10), \
            "exp(log(y)) should equal y"
    
    def test_lorentz_exp_map_distance(self):
        """Test that exp map preserves distance."""
        model = LorentzModel(dim=2)
        x = np.array([1.0, 0.0, 0.0])
        v = np.array([0.0, 1.0, 0.0])  # Tangent vector with norm 1
        
        y = model.lorentz_exp_map(x, v)
        dist = model.lorentz_distance(x, y)
        
        v_norm = np.sqrt(model.lorentz_inner_product(v, v))
        assert np.allclose(dist, v_norm, atol=1e-10), \
            "Distance should equal tangent vector norm"
    
    def test_lorentz_parallel_transport_preserves_norm(self):
        """Test that parallel transport preserves norms."""
        model = LorentzModel(dim=2)
        x = np.array([1.0, 0.0, 0.0])
        y = np.array([np.cosh(1.0), np.sinh(1.0), 0.0])
        v = np.array([0.0, 0.0, 1.0])
        
        w = model.lorentz_parallel_transport(x, y, v)
        
        v_norm = model.lorentz_norm(v)
        w_norm = model.lorentz_norm(w)
        
        assert np.allclose(v_norm, w_norm, atol=1e-10), \
            "Parallel transport should preserve norms"
    
    def test_lorentz_geodesic_endpoints(self):
        """Test geodesic interpolation at endpoints."""
        model = LorentzModel(dim=2)
        x = np.array([1.0, 0.0, 0.0])
        y = np.array([np.cosh(1.0), np.sinh(1.0), 0.0])
        
        # At t=0, should return x
        gamma_0 = model.lorentz_geodesic(x, y, 0.0)
        assert np.allclose(gamma_0, x, atol=1e-10), "Geodesic at t=0 should be x"
        
        # At t=1, should return y
        gamma_1 = model.lorentz_geodesic(x, y, 1.0)
        assert np.allclose(gamma_1, y, atol=1e-10), "Geodesic at t=1 should be y"
    
    def test_lorentz_mean_single_point(self):
        """Test Fréchet mean of single point."""
        model = LorentzModel(dim=2)
        x = np.array([1.0, 0.0, 0.0])
        points = np.array([x])
        
        mean = model.lorentz_mean(points)
        assert np.allclose(mean, x, atol=1e-6), "Mean of single point should be the point"
    
    def test_lorentz_to_poincare_origin(self):
        """Test conversion from Lorentz to Poincaré at origin."""
        model = LorentzModel(dim=2)
        x_lorentz = np.array([1.0, 0.0, 0.0])
        
        x_poincare = model.lorentz_to_poincare(x_lorentz)
        expected = np.array([0.0, 0.0])
        
        assert np.allclose(x_poincare, expected, atol=1e-10), \
            "Origin should map to origin"


class TestPoincareModel:
    """Tests for Poincaré ball model."""
    
    def test_poincare_distance_origin(self):
        """Test distance at origin."""
        model = PoincareModel(dim=2)
        x = np.array([0.0, 0.0])
        y = np.array([0.0, 0.0])
        
        dist = model.poincare_distance(x, y)
        assert np.allclose(dist, 0.0, atol=1e-10), "Distance to self should be 0"
    
    def test_poincare_distance_symmetry(self):
        """Test distance symmetry."""
        model = PoincareModel(dim=2)
        x = np.array([0.0, 0.0])
        y = np.array([0.5, 0.0])
        
        dist_xy = model.poincare_distance(x, y)
        dist_yx = model.poincare_distance(y, x)
        
        assert np.allclose(dist_xy, dist_yx), "Distance should be symmetric"
    
    def test_poincare_exp_log_inverse(self):
        """Test that exp and log are inverse operations."""
        model = PoincareModel(dim=2)
        x = np.array([0.0, 0.0])
        y = np.array([0.5, 0.0])
        
        # Compute log map
        v = model.poincare_log_map(x, y)
        
        # Apply exp map
        y_reconstructed = model.poincare_exp_map(x, v)
        
        assert np.allclose(y, y_reconstructed, atol=1e-9), \
            "exp(log(y)) should equal y"
    
    def test_poincare_geodesic_endpoints(self):
        """Test geodesic interpolation at endpoints."""
        model = PoincareModel(dim=2)
        x = np.array([0.0, 0.0])
        y = np.array([0.5, 0.0])
        
        # At t=0, should return x
        gamma_0 = model.poincare_geodesic(x, y, 0.0)
        assert np.allclose(gamma_0, x, atol=1e-10), "Geodesic at t=0 should be x"
        
        # At t=1, should return y
        gamma_1 = model.poincare_geodesic(x, y, 1.0)
        assert np.allclose(gamma_1, y, atol=1e-9), "Geodesic at t=1 should be y"
    
    def test_poincare_projection(self):
        """Test projection to Poincaré ball."""
        model = PoincareModel(dim=2)
        x = np.array([2.0, 0.0])  # Outside ball
        
        projected = model.poincare_projection(x)
        norm = np.linalg.norm(projected)
        
        assert norm < 1.0, "Projected point should be inside ball"
    
    def test_poincare_to_lorentz_origin(self):
        """Test conversion from Poincaré to Lorentz at origin."""
        model = PoincareModel(dim=2)
        x_poincare = np.array([0.0, 0.0])
        
        x_lorentz = model.poincare_to_lorentz(x_poincare)
        expected = np.array([1.0, 0.0, 0.0])
        
        assert np.allclose(x_lorentz, expected, atol=1e-10), \
            "Origin should map to origin"


class TestDualModelSystem:
    """Tests for dual model system."""
    
    def test_model_conversion_roundtrip(self):
        """Test conversion roundtrip Lorentz -> Poincaré -> Lorentz."""
        system = DualModelSystem(dim=2)
        x_lorentz = np.array([1.0, 0.0, 0.0])
        
        # Convert to Poincaré
        x_poincare = system.convert_between_models(x_lorentz, 'lorentz', 'poincare')
        
        # Convert back to Lorentz
        x_lorentz_back = system.convert_between_models(x_poincare, 'poincare', 'lorentz')
        
        assert np.allclose(x_lorentz, x_lorentz_back, atol=1e-10), \
            "Roundtrip conversion should preserve point"
    
    def test_dual_model_distance_consistency(self):
        """Test that distance is consistent across models."""
        system = DualModelSystem(dim=2)
        x_poincare = np.array([0.0, 0.0])
        y_poincare = np.array([0.5, 0.0])
        
        # Compute distance in Poincaré model
        dist_poincare = system.dual_model_distance(x_poincare, y_poincare, model='poincare')
        
        # Convert to Lorentz and compute distance
        x_lorentz = system.poincare.poincare_to_lorentz(x_poincare)
        y_lorentz = system.poincare.poincare_to_lorentz(y_poincare)
        dist_lorentz = system.dual_model_distance(x_lorentz, y_lorentz, model='lorentz')
        
        assert np.allclose(dist_poincare, dist_lorentz, atol=1e-6), \
            "Distance should be consistent across models"
    
    def test_auto_select_model(self):
        """Test automatic model selection."""
        system = DualModelSystem(dim=2)
        x = np.array([0.95, 0.0])  # Near boundary
        y = np.array([0.96, 0.0])
        
        model = system.auto_select_model('distance', (x, y))
        assert model in ['lorentz', 'poincare'], "Should select valid model"
    
    def test_validate_model_consistency(self):
        """Test model consistency validation."""
        system = DualModelSystem(dim=2)
        x = np.array([0.0, 0.0])
        y = np.array([0.5, 0.0])
        
        results = system.validate_model_consistency(x, 'distance', y, tol=1e-6)
        assert results['consistent'], "Models should be consistent"
    
    def test_benchmark_models(self):
        """Test model benchmarking."""
        system = DualModelSystem(dim=2)
        x = np.array([0.0, 0.0])
        y = np.array([0.5, 0.0])
        
        results = system.benchmark_models('distance', (x, y), n_trials=10)
        
        assert 'lorentz' in results, "Should have Lorentz results"
        assert 'poincare' in results, "Should have Poincaré results"
        assert 'difference' in results, "Should compute difference"


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_convert_lorentz_to_poincare(self):
        """Test Lorentz to Poincaré conversion function."""
        x_lorentz = np.array([1.0, 0.0, 0.0])
        x_poincare = convert_lorentz_to_poincare(x_lorentz)
        
        expected = np.array([0.0, 0.0])
        assert np.allclose(x_poincare, expected, atol=1e-10)
    
    def test_convert_poincare_to_lorentz(self):
        """Test Poincaré to Lorentz conversion function."""
        x_poincare = np.array([0.0, 0.0])
        x_lorentz = convert_poincare_to_lorentz(x_poincare)
        
        expected = np.array([1.0, 0.0, 0.0])
        assert np.allclose(x_lorentz, expected, atol=1e-10)
    
    def test_auto_distance(self):
        """Test automatic distance computation."""
        x = np.array([0.0, 0.0])
        y = np.array([0.5, 0.0])
        
        dist = auto_distance(x, y)
        assert dist > 0, "Distance should be positive"


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
