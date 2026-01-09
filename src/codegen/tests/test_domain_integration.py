"""
Comprehensive Integration Tests for Domain System

Tests the complete integration of:
- Registry
- API
- CLI
- Configuration
- Schema validation
- All 9 domain types
"""

import sys
import json
sys.path.insert(0, '../hypersync/routing')

from registry import (
    DomainRegistry, DomainType, CurvatureClass,
    get_registry, list_domains
)
from domain_factory import get_factory
from domain_api import create_api
from config_manager import DomainConfigManager
from schema_validator import validate_descriptor


def test_full_stack_integration():
    """Test complete stack from registry to API"""
    print("\n" + "=" * 70)
    print("TEST: Full Stack Integration")
    print("=" * 70)

    # Initialize all components
    registry = get_registry()
    factory = get_factory()
    api = create_api(registry, factory)
    config = DomainConfigManager()

    # Test registry
    domains = registry.list_all()
    assert len(domains) == 9, f"Expected 9 domains, got {len(domains)}"
    print(f"✅ Registry: {len(domains)} domains registered")

    # Test API
    result = api.list_domains()
    assert result['status'] == 'success'
    assert result['count'] == 9
    print(f"✅ API: list_domains returned {result['count']} domains")

    # Test configuration
    assert config.is_domain_enabled('schwarzschild')
    print(f"✅ Config: schwarzschild enabled")

    # Test factory
    instance = factory.create('hyperboloid', {'dimension': 4, 'curvature': -1.0})
    assert instance is not None
    print(f"✅ Factory: created hyperboloid instance")

    print("\n✅ Full stack integration PASSED\n")


def test_all_domain_types():
    """Test all 9 domain types are properly registered"""
    print("=" * 70)
    print("TEST: All Domain Types")
    print("=" * 70)

    registry = get_registry()

    expected_types = [
        ('hyperboloid', DomainType.HYPERBOLOID, CurvatureClass.NEGATIVE),
        ('sphere', DomainType.SPHERE, CurvatureClass.POSITIVE),
        ('flat_minkowski', DomainType.FLAT_MINKOWSKI, CurvatureClass.ZERO),
        ('ads_space', DomainType.ADS_SPACE, CurvatureClass.NEGATIVE),
        ('schwarzschild', DomainType.SCHWARZSCHILD, CurvatureClass.MIXED),
        ('kerr', DomainType.KERR, CurvatureClass.MIXED),
        ('frw_cosmology', DomainType.FRW_COSMOLOGY, CurvatureClass.TIME_VARYING),
        ('inflationary', DomainType.INFLATIONARY, CurvatureClass.TIME_VARYING),
        ('cyclic', DomainType.CYCLIC, CurvatureClass.TIME_VARYING)
    ]

    for domain_id_suffix, dtype, cclass in expected_types:
        domains = registry.get_by_type(dtype)
        assert len(domains) > 0, f"No domains found for {dtype}"

        domain = domains[0]
        assert domain.curvature_class == cclass
        print(f"✅ {dtype.value}: curvature={cclass.value}, dim={domain.dimension}")

    print("\n✅ All domain types PASSED\n")


def test_capability_queries():
    """Test capability-based queries work correctly"""
    print("=" * 70)
    print("TEST: Capability Queries")
    print("=" * 70)

    registry = get_registry()
    api = create_api(registry, get_factory())

    # Test horizons (should find black holes)
    result = api.query_by_capability('supports_horizons')
    assert result['status'] == 'success'
    assert result['count'] >= 2, "Should find Schwarzschild and Kerr"
    print(f"✅ Horizons: found {result['count']} domains")

    # Test ergosphere (should find Kerr)
    result = api.query_by_capability('supports_ergosphere')
    assert result['status'] == 'success'
    assert result['count'] >= 1, "Should find Kerr"
    print(f"✅ Ergosphere: found {result['count']} domain(s)")

    # Test time evolution (should find cosmologies)
    result = api.query_by_capability('supports_time_evolution')
    assert result['status'] == 'success'
    assert result['count'] >= 3, "Should find FRW, Inflationary, Cyclic"
    print(f"✅ Time evolution: found {result['count']} domains")

    # Test causality (should find Lorentzian domains)
    result = api.query_by_capability('supports_causality')
    assert result['status'] == 'success'
    assert result['count'] >= 5, "Should find multiple Lorentzian domains"
    print(f"✅ Causality: found {result['count']} domains")

    print("\n✅ Capability queries PASSED\n")


def test_feature_trait_queries():
    """Test feature trait queries"""
    print("=" * 70)
    print("TEST: Feature Trait Queries")
    print("=" * 70)

    registry = get_registry()

    # Black holes
    black_holes = registry.get_by_feature_trait('black_hole')
    assert len(black_holes) >= 2, "Should find Schwarzschild and Kerr"
    print(f"✅ Black holes: {len(black_holes)} domains")

    # Cosmologies
    cosmologies = registry.get_by_feature_trait('cosmology')
    assert len(cosmologies) >= 3, "Should find FRW, Inflationary, Cyclic"
    print(f"✅ Cosmologies: {len(cosmologies)} domains")

    # Lorentzian
    lorentzian = registry.get_by_feature_trait('lorentzian')
    assert len(lorentzian) >= 3, "Should find multiple Lorentzian domains"
    print(f"✅ Lorentzian: {len(lorentzian)} domains")

    # Constant curvature
    const_curv = registry.get_by_feature_trait('constant_curvature')
    assert len(const_curv) >= 3, "Should find hyperboloid, sphere, AdS"
    print(f"✅ Constant curvature: {len(const_curv)} domains")

    print("\n✅ Feature trait queries PASSED\n")


def test_domain_transitions():
    """Test domain transition planning"""
    print("=" * 70)
    print("TEST: Domain Transitions")
    print("=" * 70)

    registry = get_registry()
    api = create_api(registry, get_factory())

    # Test FRW to AdS transition
    result = api.plan_transition({
        'source_domain': 'frw_default',
        'target_domain': 'ads_default',
        'transition_type': 'smooth'
    })
    assert result['status'] == 'success'
    print(f"✅ FRW → AdS: compatible={result['compatible']}, adapter={result['requires_adapter']}")

    # Test Schwarzschild to Minkowski
    result = api.plan_transition({
        'source_domain': 'schwarzschild_default',
        'target_domain': 'minkowski_default',
        'transition_type': 'smooth'
    })
    assert result['status'] == 'success'
    print(f"✅ Schwarzschild → Minkowski: compatible={result['compatible']}")

    # Test compatible domains for FRW
    result = api.get_compatible_domains('frw_default')
    assert result['status'] == 'success'
    assert result['count'] > 0
    print(f"✅ FRW compatible domains: {result['count']}")

    print("\n✅ Domain transitions PASSED\n")


def test_schema_validation():
    """Test schema validation"""
    print("=" * 70)
    print("TEST: Schema Validation")
    print("=" * 70)

    # Valid descriptor
    valid_descriptor = {
        'domain_id': 'test_schwarzschild',
        'domain_type': 'schwarzschild',
        'curvature_class': 'mixed',
        'dimension': 4,
        'parameters': {'mass': 1.0}
    }

    is_valid, errors = validate_descriptor(valid_descriptor)
    assert is_valid, f"Valid descriptor failed: {errors}"
    print(f"✅ Valid descriptor passed")

    # Invalid: missing required field
    invalid_descriptor = {
        'domain_id': 'test',
        'domain_type': 'schwarzschild'
        # Missing curvature_class and dimension
    }

    is_valid, errors = validate_descriptor(invalid_descriptor)
    assert not is_valid, "Invalid descriptor should fail"
    assert len(errors) > 0
    print(f"✅ Invalid descriptor caught: {len(errors)} errors")

    # Invalid: bad dimension
    bad_dimension = {
        'domain_id': 'test',
        'domain_type': 'schwarzschild',
        'curvature_class': 'mixed',
        'dimension': 100  # Too high
    }

    is_valid, errors = validate_descriptor(bad_dimension)
    assert not is_valid
    print(f"✅ Bad dimension caught")

    # Invalid: negative mass for black hole
    bad_params = {
        'domain_id': 'test',
        'domain_type': 'schwarzschild',
        'curvature_class': 'mixed',
        'dimension': 4,
        'parameters': {'mass': -1.0}  # Negative mass
    }

    is_valid, errors = validate_descriptor(bad_params)
    assert not is_valid
    print(f"✅ Negative mass caught")

    print("\n✅ Schema validation PASSED\n")


def test_configuration_management():
    """Test configuration management"""
    print("=" * 70)
    print("TEST: Configuration Management")
    print("=" * 70)

    config = DomainConfigManager()

    # Test default config
    assert config.is_domain_enabled('schwarzschild')
    print(f"✅ Default config loaded")

    # Test get/set
    config.set('policies.enforce_causality', False)
    assert config.get('policies.enforce_causality') == False
    print(f"✅ Config get/set works")

    # Test routing config
    routing = config.get_routing_config()
    assert 'enable_cross_curvature' in routing
    print(f"✅ Routing config accessible")

    # Test policy config
    policies = config.get_policy_config()
    assert 'enforce_horizon_acl' in policies
    print(f"✅ Policy config accessible")

    print("\n✅ Configuration management PASSED\n")


def test_api_endpoints():
    """Test all API endpoints"""
    print("=" * 70)
    print("TEST: API Endpoints")
    print("=" * 70)

    registry = get_registry()
    factory = get_factory()
    api = create_api(registry, factory)

    # List domains
    result = api.list_domains()
    assert result['status'] == 'success'
    print(f"✅ list_domains: {result['count']} domains")

    # Get domain
    result = api.get_domain('schwarzschild_default')
    assert result['status'] == 'success'
    print(f"✅ get_domain: schwarzschild_default")

    # List types
    result = api.list_domain_types()
    assert result['status'] == 'success'
    print(f"✅ list_domain_types: {result['count']} types")

    # List curvatures
    result = api.list_curvature_classes()
    assert result['status'] == 'success'
    print(f"✅ list_curvature_classes: {result['count']} classes")

    # Get capabilities
    result = api.get_domain_capabilities('kerr_default')
    assert result['status'] == 'success'
    assert result['capabilities']['supports_ergosphere']
    print(f"✅ get_domain_capabilities: kerr_default")

    # Create instance
    result = api.create_domain_instance({
        'domain_type': 'hyperboloid',
        'parameters': {'dimension': 4, 'curvature': -1.0},
        'instance_id': 'test_hyp'
    })
    assert result['status'] == 'success'
    print(f"✅ create_domain_instance: hyperboloid")

    # Validate domain
    result = api.validate_domain('schwarzschild_default')
    assert result['status'] == 'success'
    assert result['valid']
    print(f"✅ validate_domain: schwarzschild_default")

    print("\n✅ API endpoints PASSED\n")


def test_user_operator_controls():
    """Test that users and operators have full control"""
    print("=" * 70)
    print("TEST: User & Operator Controls")
    print("=" * 70)

    registry = get_registry()
    api = create_api(registry, get_factory())
    config = DomainConfigManager()

    # Users can list domains
    result = api.list_domains()
    assert result['status'] == 'success'
    print(f"✅ Users can list domains")

    # Users can filter by capability
    result = api.query_by_capability('supports_horizons')
    assert result['status'] == 'success'
    print(f"✅ Users can query by capability")

    # Users can create instances
    result = api.create_domain_instance({
        'domain_type': 'sphere',
        'parameters': {'radius': 1.0},
        'instance_id': 'user_sphere'
    })
    assert result['status'] == 'success'
    print(f"✅ Users can create instances")

    # Users can plan transitions
    result = api.plan_transition({
        'source_domain': 'frw_default',
        'target_domain': 'ads_default'
    })
    assert result['status'] == 'success'
    print(f"✅ Users can plan transitions")

    # Operators can configure
    config.set('policies.enforce_causality', True)
    assert config.get('policies.enforce_causality') == True
    print(f"✅ Operators can configure policies")

    # Operators can enable/disable domains
    enabled = config.get('registry.enabled_domains')
    assert 'schwarzschild' in enabled
    print(f"✅ Operators can control enabled domains")

    # Operators can set routing parameters
    config.set('routing.max_transition_hops', 10)
    assert config.get('routing.max_transition_hops') == 10
    print(f"✅ Operators can configure routing")

    print("\n✅ User & operator controls PASSED\n")


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 70)
    print("HYPERSYNC DOMAIN INTEGRATION TEST SUITE")
    print("=" * 70)
    print()

    tests = [
        test_full_stack_integration,
        test_all_domain_types,
        test_capability_queries,
        test_feature_trait_queries,
        test_domain_transitions,
        test_schema_validation,
        test_configuration_management,
        test_api_endpoints,
        test_user_operator_controls
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {test.__name__}")
            print(f"   Error: {e}\n")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {test.__name__}")
            print(f"   Error: {e}\n")
            failed += 1

    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()

    if failed == 0:
        print("✅ ALL TESTS PASSED - DOMAIN INTEGRATION COMPLETE")
    else:
        print(f"❌ {failed} TEST(S) FAILED")

    print("=" * 70)

    return failed == 0


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
