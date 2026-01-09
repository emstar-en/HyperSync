"""
Tests for Domain Registry Integration
"""

import sys
sys.path.insert(0, '../hypersync/routing')

from registry import (
    DomainRegistry, DomainType, CurvatureClass,
    get_registry, list_domains, list_domain_types
)


def test_registry_initialization():
    """Test that registry initializes with all domain types"""
    registry = DomainRegistry()
    domains = registry.list_all()

    assert len(domains) == 9, f"Expected 9 domains, got {len(domains)}"
    print("✅ Registry initialized with 9 domain types")


def test_domain_types():
    """Test all domain types are registered"""
    registry = get_registry()

    expected_types = [
        DomainType.HYPERBOLOID,
        DomainType.SPHERE,
        DomainType.FLAT_MINKOWSKI,
        DomainType.ADS_SPACE,
        DomainType.SCHWARZSCHILD,
        DomainType.KERR,
        DomainType.FRW_COSMOLOGY,
        DomainType.INFLATIONARY,
        DomainType.CYCLIC
    ]

    for dtype in expected_types:
        domains = registry.get_by_type(dtype)
        assert len(domains) > 0, f"No domains found for type {dtype}"
        print(f"✅ Found domain type: {dtype.value}")


def test_curvature_classes():
    """Test domains are classified by curvature"""
    registry = get_registry()

    negative = registry.get_by_curvature(CurvatureClass.NEGATIVE)
    assert len(negative) >= 2, "Should have hyperboloid and AdS"

    positive = registry.get_by_curvature(CurvatureClass.POSITIVE)
    assert len(positive) >= 1, "Should have sphere"

    zero = registry.get_by_curvature(CurvatureClass.ZERO)
    assert len(zero) >= 1, "Should have flat Minkowski"

    time_varying = registry.get_by_curvature(CurvatureClass.TIME_VARYING)
    assert len(time_varying) >= 3, "Should have FRW, Inflationary, Cyclic"

    print("✅ All curvature classes populated")


def test_capabilities():
    """Test capability-based queries"""
    registry = get_registry()

    with_horizons = registry.get_by_capability('supports_horizons')
    assert len(with_horizons) >= 2, "Should have Schwarzschild and Kerr"

    with_ergosphere = registry.get_by_capability('supports_ergosphere')
    assert len(with_ergosphere) >= 1, "Should have Kerr"

    time_evolving = registry.get_by_capability('supports_time_evolution')
    assert len(time_evolving) >= 3, "Should have cosmologies"

    print("✅ Capability queries working")


def test_feature_traits():
    """Test feature trait queries"""
    registry = get_registry()

    black_holes = registry.get_by_feature_trait('black_hole')
    assert len(black_holes) >= 2, "Should have Schwarzschild and Kerr"

    cosmologies = registry.get_by_feature_trait('cosmology')
    assert len(cosmologies) >= 3, "Should have FRW, Inflationary, Cyclic"

    lorentzian = registry.get_by_feature_trait('lorentzian')
    assert len(lorentzian) >= 3, "Should have multiple Lorentzian domains"

    print("✅ Feature trait queries working")


def test_domain_validation():
    """Test domain validation"""
    registry = get_registry()

    assert registry.validate_domain("hyperboloid_default")
    assert registry.validate_domain("schwarzschild_default")
    assert registry.validate_domain("frw_default")
    assert not registry.validate_domain("nonexistent_domain")

    print("✅ Domain validation working")


def test_compatible_domains():
    """Test finding compatible domains for transitions"""
    registry = get_registry()

    # FRW can transition to many domains
    frw_compatible = registry.get_compatible_domains("frw_default")
    assert len(frw_compatible) > 0, "FRW should have compatible domains"

    # Schwarzschild can transition to same-dimension domains
    bh_compatible = registry.get_compatible_domains("schwarzschild_default")
    assert len(bh_compatible) > 0, "Black hole should have compatible domains"

    print("✅ Compatible domain queries working")


if __name__ == "__main__":
    print("=" * 70)
    print("DOMAIN REGISTRY INTEGRATION TESTS")
    print("=" * 70)
    print()

    test_registry_initialization()
    test_domain_types()
    test_curvature_classes()
    test_capabilities()
    test_feature_traits()
    test_domain_validation()
    test_compatible_domains()

    print()
    print("=" * 70)
    print("✅ ALL TESTS PASSED - PASS 1 COMPLETE")
    print("=" * 70)
