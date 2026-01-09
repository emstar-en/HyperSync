"""
Schema Validator for Domain Descriptors
"""

import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class DomainSchemaValidator:
    """Validates domain descriptors against schema"""

    VALID_DOMAIN_TYPES = [
        "hyperboloid", "sphere", "flat_minkowski",
        "ads_space", "schwarzschild", "kerr",
        "frw_cosmology", "inflationary", "cyclic",
        "euclidean", "hyperbolic"
    ]

    VALID_CURVATURE_CLASSES = [
        "negative", "zero", "positive", "mixed", "time_varying"
    ]

    def __init__(self):
        self.errors = []

    def validate(self, descriptor: Dict[str, Any]) -> bool:
        """Validate a domain descriptor"""
        self.errors = []

        # Required fields
        if not self._validate_required_fields(descriptor):
            return False

        # Domain type
        if not self._validate_domain_type(descriptor.get('domain_type')):
            return False

        # Curvature class
        if not self._validate_curvature_class(descriptor.get('curvature_class')):
            return False

        # Dimension
        if not self._validate_dimension(descriptor.get('dimension')):
            return False

        # Capabilities
        if 'capabilities' in descriptor:
            self._validate_capabilities(descriptor['capabilities'])

        # Parameters
        if 'parameters' in descriptor:
            self._validate_parameters(
                descriptor.get('domain_type'),
                descriptor['parameters']
            )

        return len(self.errors) == 0

    def _validate_required_fields(self, descriptor: Dict[str, Any]) -> bool:
        """Validate required fields are present"""
        required = ['domain_id', 'domain_type', 'curvature_class', 'dimension']

        for field in required:
            if field not in descriptor:
                self.errors.append(f"Missing required field: {field}")
                return False

        return True

    def _validate_domain_type(self, domain_type: str) -> bool:
        """Validate domain type"""
        if domain_type not in self.VALID_DOMAIN_TYPES:
            self.errors.append(f"Invalid domain_type: {domain_type}")
            return False
        return True

    def _validate_curvature_class(self, curvature_class: str) -> bool:
        """Validate curvature class"""
        if curvature_class not in self.VALID_CURVATURE_CLASSES:
            self.errors.append(f"Invalid curvature_class: {curvature_class}")
            return False
        return True

    def _validate_dimension(self, dimension: int) -> bool:
        """Validate dimension"""
        if not isinstance(dimension, int):
            self.errors.append("dimension must be an integer")
            return False

        if dimension < 1 or dimension > 11:
            self.errors.append(f"dimension must be between 1 and 11, got {dimension}")
            return False

        return True

    def _validate_capabilities(self, capabilities: Dict[str, Any]) -> bool:
        """Validate capabilities"""
        valid_caps = [
            'supports_causality', 'supports_horizons', 'supports_ergosphere',
            'supports_time_evolution', 'supports_redshift', 'supports_geodesics',
            'supports_parallel_transport', 'supports_curvature_tensor',
            'max_dimension', 'requires_time_coordinate'
        ]

        for cap in capabilities:
            if cap not in valid_caps:
                self.errors.append(f"Unknown capability: {cap}")

        return True

    def _validate_parameters(self, domain_type: str, parameters: Dict[str, Any]) -> bool:
        """Validate domain-specific parameters"""
        if domain_type == 'schwarzschild':
            if 'mass' in parameters and parameters['mass'] <= 0:
                self.errors.append("schwarzschild mass must be positive")

        elif domain_type == 'kerr':
            if 'mass' in parameters and parameters['mass'] <= 0:
                self.errors.append("kerr mass must be positive")
            if 'angular_momentum' in parameters:
                a = parameters['angular_momentum']
                m = parameters.get('mass', 1.0)
                if abs(a) > m:
                    self.errors.append("kerr angular_momentum must satisfy |a| <= M")

        elif domain_type == 'hyperboloid':
            if 'curvature' in parameters and parameters['curvature'] >= 0:
                self.errors.append("hyperboloid curvature must be negative")

        elif domain_type == 'sphere':
            if 'radius' in parameters and parameters['radius'] <= 0:
                self.errors.append("sphere radius must be positive")

        return True

    def get_errors(self) -> List[str]:
        """Get validation errors"""
        return self.errors


def validate_descriptor(descriptor: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate a domain descriptor and return (is_valid, errors)"""
    validator = DomainSchemaValidator()
    is_valid = validator.validate(descriptor)
    return is_valid, validator.get_errors()
