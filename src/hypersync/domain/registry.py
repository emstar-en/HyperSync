"""
HyperSync Domain Registry
Enhanced with Lorentzian/Pseudo-Riemannian Domain Support

Manages registration and discovery of all geometric domain types including:
- Constant curvature domains (Hyperboloid, Sphere, Flat Minkowski)
- Advanced domains (AdS, Schwarzschild, Kerr black holes)
- Time-varying domains (FRW, Inflationary, Cyclic cosmologies)
"""

from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DomainType(Enum):
    """Enumeration of all supported domain types"""
    # Constant curvature domains
    HYPERBOLOID = "hyperboloid"
    SPHERE = "sphere"
    FLAT_MINKOWSKI = "flat_minkowski"

    # Advanced domains
    ADS_SPACE = "ads_space"
    SCHWARZSCHILD = "schwarzschild"
    KERR = "kerr"

    # Time-varying domains
    FRW_COSMOLOGY = "frw_cosmology"
    INFLATIONARY = "inflationary"
    CYCLIC = "cyclic"

    # Legacy/compatibility
    EUCLIDEAN = "euclidean"
    HYPERBOLIC = "hyperbolic"


class CurvatureClass(Enum):
    """Classification by curvature type"""
    NEGATIVE = "negative"  # Hyperbolic/AdS
    ZERO = "zero"  # Flat/Minkowski
    POSITIVE = "positive"  # Spherical/de Sitter
    MIXED = "mixed"  # Schwarzschild/Kerr
    TIME_VARYING = "time_varying"  # FRW/Inflationary/Cyclic


@dataclass
class DomainCapabilities:
    """Capabilities and features of a domain"""
    supports_causality: bool = False
    supports_horizons: bool = False
    supports_ergosphere: bool = False
    supports_time_evolution: bool = False
    supports_redshift: bool = False
    supports_geodesics: bool = True
    supports_parallel_transport: bool = True
    supports_curvature_tensor: bool = True
    max_dimension: Optional[int] = None
    requires_time_coordinate: bool = False


@dataclass
class DomainDescriptor:
    """Complete descriptor for a geometric domain"""
    domain_id: str
    domain_type: DomainType
    curvature_class: CurvatureClass
    dimension: int
    capabilities: DomainCapabilities
    parameters: Dict[str, Any] = field(default_factory=dict)
    feature_traits: List[str] = field(default_factory=list)
    policy_constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DomainRegistry:
    """
    Central registry for all geometric domain types.
    Provides discovery, validation, and instantiation of domains.
    """

    def __init__(self):
        self._domains: Dict[str, DomainDescriptor] = {}
        self._type_map: Dict[DomainType, List[str]] = {}
        self._curvature_map: Dict[CurvatureClass, List[str]] = {}
        self._initialize_builtin_domains()

    def _initialize_builtin_domains(self):
        """Register all built-in domain types"""

        # Hyperboloid Model (constant negative curvature)
        self.register(DomainDescriptor(
            domain_id="hyperboloid_default",
            domain_type=DomainType.HYPERBOLOID,
            curvature_class=CurvatureClass.NEGATIVE,
            dimension=4,
            capabilities=DomainCapabilities(
                supports_causality=True,
                supports_geodesics=True,
                supports_parallel_transport=True,
                supports_curvature_tensor=True
            ),
            parameters={"curvature": -1.0},
            feature_traits=["constant_curvature", "lorentzian", "time_like"],
            metadata={"description": "Hyperboloid model of hyperbolic space"}
        ))

        # Sphere Model (constant positive curvature)
        self.register(DomainDescriptor(
            domain_id="sphere_default",
            domain_type=DomainType.SPHERE,
            curvature_class=CurvatureClass.POSITIVE,
            dimension=3,
            capabilities=DomainCapabilities(
                supports_geodesics=True,
                supports_parallel_transport=True,
                supports_curvature_tensor=True
            ),
            parameters={"radius": 1.0},
            feature_traits=["constant_curvature", "riemannian", "compact"],
            metadata={"description": "Spherical geometry with constant positive curvature"}
        ))

        # Flat Minkowski (zero curvature spacetime)
        self.register(DomainDescriptor(
            domain_id="minkowski_default",
            domain_type=DomainType.FLAT_MINKOWSKI,
            curvature_class=CurvatureClass.ZERO,
            dimension=4,
            capabilities=DomainCapabilities(
                supports_causality=True,
                supports_geodesics=True,
                supports_parallel_transport=True,
                requires_time_coordinate=True
            ),
            parameters={"signature": "(-,+,+,+)"},
            feature_traits=["flat", "lorentzian", "special_relativity"],
            metadata={"description": "Flat Minkowski spacetime"}
        ))

        # Anti-de Sitter Space (negative cosmological constant)
        self.register(DomainDescriptor(
            domain_id="ads_default",
            domain_type=DomainType.ADS_SPACE,
            curvature_class=CurvatureClass.NEGATIVE,
            dimension=4,
            capabilities=DomainCapabilities(
                supports_causality=True,
                supports_horizons=False,
                supports_geodesics=True,
                supports_curvature_tensor=True,
                requires_time_coordinate=True
            ),
            parameters={"radius": 1.0, "cosmological_constant": -1.0},
            feature_traits=["constant_curvature", "lorentzian", "ads_cft", "conformal_boundary"],
            metadata={"description": "Anti-de Sitter space with conformal boundary"}
        ))

        # Schwarzschild Black Hole (spherically symmetric)
        self.register(DomainDescriptor(
            domain_id="schwarzschild_default",
            domain_type=DomainType.SCHWARZSCHILD,
            curvature_class=CurvatureClass.MIXED,
            dimension=4,
            capabilities=DomainCapabilities(
                supports_causality=True,
                supports_horizons=True,
                supports_geodesics=True,
                supports_curvature_tensor=True,
                supports_redshift=True,
                requires_time_coordinate=True
            ),
            parameters={"mass": 1.0, "schwarzschild_radius": 2.0},
            feature_traits=["black_hole", "event_horizon", "singularity", "spherical_symmetry"],
            policy_constraints=["horizon_acl", "causality_check"],
            metadata={"description": "Schwarzschild black hole spacetime"}
        ))

        # Kerr Black Hole (rotating)
        self.register(DomainDescriptor(
            domain_id="kerr_default",
            domain_type=DomainType.KERR,
            curvature_class=CurvatureClass.MIXED,
            dimension=4,
            capabilities=DomainCapabilities(
                supports_causality=True,
                supports_horizons=True,
                supports_ergosphere=True,
                supports_geodesics=True,
                supports_curvature_tensor=True,
                supports_redshift=True,
                requires_time_coordinate=True
            ),
            parameters={"mass": 1.0, "angular_momentum": 0.5},
            feature_traits=["black_hole", "rotating", "ergosphere", "frame_dragging", "ring_singularity"],
            policy_constraints=["horizon_acl", "causality_check", "ergosphere_policy"],
            metadata={"description": "Kerr rotating black hole spacetime"}
        ))

        # FRW Cosmology (expanding universe)
        self.register(DomainDescriptor(
            domain_id="frw_default",
            domain_type=DomainType.FRW_COSMOLOGY,
            curvature_class=CurvatureClass.TIME_VARYING,
            dimension=4,
            capabilities=DomainCapabilities(
                supports_causality=True,
                supports_time_evolution=True,
                supports_redshift=True,
                supports_geodesics=True,
                requires_time_coordinate=True
            ),
            parameters={"H0": 1.0, "Omega_m": 0.3, "Omega_Lambda": 0.7},
            feature_traits=["cosmology", "expanding", "time_varying", "homogeneous", "isotropic"],
            metadata={"description": "Friedmann-Robertson-Walker cosmology"}
        ))

        # Inflationary Cosmology (exponential expansion)
        self.register(DomainDescriptor(
            domain_id="inflationary_default",
            domain_type=DomainType.INFLATIONARY,
            curvature_class=CurvatureClass.TIME_VARYING,
            dimension=4,
            capabilities=DomainCapabilities(
                supports_causality=True,
                supports_time_evolution=True,
                supports_redshift=True,
                supports_geodesics=True,
                requires_time_coordinate=True
            ),
            parameters={"H_inflation": 10.0, "duration": 60.0},
            feature_traits=["cosmology", "inflation", "exponential_expansion", "early_universe"],
            metadata={"description": "Inflationary cosmology with exponential expansion"}
        ))

        # Cyclic Cosmology (periodic)
        self.register(DomainDescriptor(
            domain_id="cyclic_default",
            domain_type=DomainType.CYCLIC,
            curvature_class=CurvatureClass.TIME_VARYING,
            dimension=4,
            capabilities=DomainCapabilities(
                supports_causality=True,
                supports_time_evolution=True,
                supports_geodesics=True,
                requires_time_coordinate=True
            ),
            parameters={"period": 100.0, "amplitude": 1.0},
            feature_traits=["cosmology", "cyclic", "periodic", "bounce"],
            metadata={"description": "Cyclic cosmology with periodic evolution"}
        ))

        logger.info(f"Initialized {len(self._domains)} built-in domain types")

    def register(self, descriptor: DomainDescriptor) -> None:
        """Register a domain descriptor"""
        self._domains[descriptor.domain_id] = descriptor

        # Update type map
        if descriptor.domain_type not in self._type_map:
            self._type_map[descriptor.domain_type] = []
        self._type_map[descriptor.domain_type].append(descriptor.domain_id)

        # Update curvature map
        if descriptor.curvature_class not in self._curvature_map:
            self._curvature_map[descriptor.curvature_class] = []
        self._curvature_map[descriptor.curvature_class].append(descriptor.domain_id)

        logger.debug(f"Registered domain: {descriptor.domain_id} ({descriptor.domain_type.value})")

    def get(self, domain_id: str) -> Optional[DomainDescriptor]:
        """Get a domain descriptor by ID"""
        return self._domains.get(domain_id)

    def get_by_type(self, domain_type: DomainType) -> List[DomainDescriptor]:
        """Get all domains of a specific type"""
        domain_ids = self._type_map.get(domain_type, [])
        return [self._domains[did] for did in domain_ids]

    def get_by_curvature(self, curvature_class: CurvatureClass) -> List[DomainDescriptor]:
        """Get all domains with a specific curvature class"""
        domain_ids = self._curvature_map.get(curvature_class, [])
        return [self._domains[did] for did in domain_ids]

    def get_by_capability(self, capability: str) -> List[DomainDescriptor]:
        """Get all domains with a specific capability"""
        results = []
        for descriptor in self._domains.values():
            if hasattr(descriptor.capabilities, capability):
                if getattr(descriptor.capabilities, capability):
                    results.append(descriptor)
        return results

    def get_by_feature_trait(self, trait: str) -> List[DomainDescriptor]:
        """Get all domains with a specific feature trait"""
        return [d for d in self._domains.values() if trait in d.feature_traits]

    def list_all(self) -> List[DomainDescriptor]:
        """List all registered domains"""
        return list(self._domains.values())

    def validate_domain(self, domain_id: str) -> bool:
        """Validate that a domain exists and is properly configured"""
        descriptor = self.get(domain_id)
        if not descriptor:
            return False

        # Basic validation
        if descriptor.dimension < 1:
            return False

        if descriptor.capabilities.requires_time_coordinate and descriptor.dimension < 2:
            return False

        return True

    def get_compatible_domains(self, source_domain_id: str) -> List[DomainDescriptor]:
        """Get domains compatible for transitions from source domain"""
        source = self.get(source_domain_id)
        if not source:
            return []

        compatible = []
        for descriptor in self._domains.values():
            if descriptor.domain_id == source_domain_id:
                continue

            # Same dimension is preferred
            if descriptor.dimension == source.dimension:
                compatible.append(descriptor)
            # Time-varying domains can transition to constant curvature
            elif source.curvature_class == CurvatureClass.TIME_VARYING:
                compatible.append(descriptor)

        return compatible


# Global registry instance
_global_registry = None


def get_registry() -> DomainRegistry:
    """Get the global domain registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = DomainRegistry()
    return _global_registry


def reset_registry():
    """Reset the global registry (mainly for testing)"""
    global _global_registry
    _global_registry = None


# Convenience functions
def register_domain(descriptor: DomainDescriptor) -> None:
    """Register a domain in the global registry"""
    get_registry().register(descriptor)


def get_domain(domain_id: str) -> Optional[DomainDescriptor]:
    """Get a domain from the global registry"""
    return get_registry().get(domain_id)


def list_domains() -> List[DomainDescriptor]:
    """List all domains in the global registry"""
    return get_registry().list_all()


def list_domain_types() -> List[DomainType]:
    """List all available domain types"""
    return list(DomainType)


def list_curvature_classes() -> List[CurvatureClass]:
    """List all curvature classes"""
    return list(CurvatureClass)
