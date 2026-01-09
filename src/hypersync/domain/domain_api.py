"""
Domain API - REST endpoints for domain management and operations

Provides HTTP API for:
- Domain discovery and listing
- Domain instantiation and configuration
- Domain transitions and routing
- Domain validation and capabilities
"""

from typing import Dict, List, Any, Optional
from dataclasses import asdict
import json
import logging

logger = logging.getLogger(__name__)


class DomainAPI:
    """REST API for domain operations"""

    def __init__(self, registry, factory):
        self.registry = registry
        self.factory = factory

    # ========================================================================
    # DISCOVERY ENDPOINTS
    # ========================================================================

    def list_domains(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        GET /api/v1/domains
        List all available domains with optional filtering

        Query params:
        - domain_type: Filter by domain type
        - curvature_class: Filter by curvature class
        - capability: Filter by capability
        - feature_trait: Filter by feature trait
        """
        try:
            domains = self.registry.list_all()

            # Apply filters
            if filters:
                if 'domain_type' in filters:
                    from registry import DomainType
                    dtype = DomainType(filters['domain_type'])
                    domains = self.registry.get_by_type(dtype)

                if 'curvature_class' in filters:
                    from registry import CurvatureClass
                    cclass = CurvatureClass(filters['curvature_class'])
                    domains = self.registry.get_by_curvature(cclass)

                if 'capability' in filters:
                    domains = self.registry.get_by_capability(filters['capability'])

                if 'feature_trait' in filters:
                    domains = self.registry.get_by_feature_trait(filters['feature_trait'])

            return {
                'status': 'success',
                'count': len(domains),
                'domains': [self._serialize_descriptor(d) for d in domains]
            }
        except Exception as e:
            logger.error(f"Error listing domains: {e}")
            return {'status': 'error', 'message': str(e)}

    def get_domain(self, domain_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/domains/{domain_id}
        Get details for a specific domain
        """
        try:
            descriptor = self.registry.get(domain_id)
            if not descriptor:
                return {'status': 'error', 'message': f'Domain not found: {domain_id}'}

            return {
                'status': 'success',
                'domain': self._serialize_descriptor(descriptor)
            }
        except Exception as e:
            logger.error(f"Error getting domain {domain_id}: {e}")
            return {'status': 'error', 'message': str(e)}

    def list_domain_types(self) -> Dict[str, Any]:
        """
        GET /api/v1/domains/types
        List all available domain types
        """
        try:
            from registry import list_domain_types
            types = list_domain_types()

            return {
                'status': 'success',
                'count': len(types),
                'types': [t.value for t in types]
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def list_curvature_classes(self) -> Dict[str, Any]:
        """
        GET /api/v1/domains/curvatures
        List all curvature classes
        """
        try:
            from registry import list_curvature_classes
            classes = list_curvature_classes()

            return {
                'status': 'success',
                'count': len(classes),
                'curvature_classes': [c.value for c in classes]
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    # ========================================================================
    # INSTANTIATION ENDPOINTS
    # ========================================================================

    def create_domain_instance(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/v1/domains/instances
        Create a new domain instance

        Request body:
        {
            "domain_type": "hyperboloid",
            "parameters": {"dimension": 4, "curvature": -1.0},
            "instance_id": "my_hyperboloid_1"
        }
        """
        try:
            domain_type = request.get('domain_type')
            parameters = request.get('parameters', {})
            instance_id = request.get('instance_id')

            if not domain_type:
                return {'status': 'error', 'message': 'domain_type required'}

            # Create instance
            instance = self.factory.create(domain_type, parameters)

            if not instance:
                return {'status': 'error', 'message': f'Failed to create domain: {domain_type}'}

            return {
                'status': 'success',
                'instance_id': instance_id,
                'domain_type': domain_type,
                'parameters': parameters
            }
        except Exception as e:
            logger.error(f"Error creating domain instance: {e}")
            return {'status': 'error', 'message': str(e)}

    # ========================================================================
    # CAPABILITY ENDPOINTS
    # ========================================================================

    def get_domain_capabilities(self, domain_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/domains/{domain_id}/capabilities
        Get capabilities for a specific domain
        """
        try:
            descriptor = self.registry.get(domain_id)
            if not descriptor:
                return {'status': 'error', 'message': f'Domain not found: {domain_id}'}

            return {
                'status': 'success',
                'domain_id': domain_id,
                'capabilities': asdict(descriptor.capabilities)
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def query_by_capability(self, capability: str) -> Dict[str, Any]:
        """
        GET /api/v1/domains/query/capability/{capability}
        Find all domains with a specific capability
        """
        try:
            domains = self.registry.get_by_capability(capability)

            return {
                'status': 'success',
                'capability': capability,
                'count': len(domains),
                'domains': [self._serialize_descriptor(d) for d in domains]
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    # ========================================================================
    # TRANSITION ENDPOINTS
    # ========================================================================

    def get_compatible_domains(self, domain_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/domains/{domain_id}/compatible
        Get domains compatible for transitions from this domain
        """
        try:
            compatible = self.registry.get_compatible_domains(domain_id)

            return {
                'status': 'success',
                'source_domain': domain_id,
                'count': len(compatible),
                'compatible_domains': [self._serialize_descriptor(d) for d in compatible]
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def plan_transition(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/v1/domains/transitions/plan
        Plan a transition between domains

        Request body:
        {
            "source_domain": "frw_default",
            "target_domain": "ads_default",
            "transition_type": "smooth"
        }
        """
        try:
            source_id = request.get('source_domain')
            target_id = request.get('target_domain')
            transition_type = request.get('transition_type', 'smooth')

            source = self.registry.get(source_id)
            target = self.registry.get(target_id)

            if not source or not target:
                return {'status': 'error', 'message': 'Invalid domain IDs'}

            # Check compatibility
            compatible = self.registry.get_compatible_domains(source_id)
            is_compatible = any(d.domain_id == target_id for d in compatible)

            return {
                'status': 'success',
                'source': self._serialize_descriptor(source),
                'target': self._serialize_descriptor(target),
                'compatible': is_compatible,
                'transition_type': transition_type,
                'requires_adapter': source.curvature_class != target.curvature_class
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    # ========================================================================
    # VALIDATION ENDPOINTS
    # ========================================================================

    def validate_domain(self, domain_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/domains/{domain_id}/validate
        Validate a domain configuration
        """
        try:
            is_valid = self.registry.validate_domain(domain_id)
            descriptor = self.registry.get(domain_id)

            return {
                'status': 'success',
                'domain_id': domain_id,
                'valid': is_valid,
                'descriptor': self._serialize_descriptor(descriptor) if descriptor else None
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def validate_parameters(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/v1/domains/validate/parameters
        Validate parameters for a domain type

        Request body:
        {
            "domain_type": "schwarzschild",
            "parameters": {"mass": 1.0, "schwarzschild_radius": 2.0}
        }
        """
        try:
            domain_type = request.get('domain_type')
            parameters = request.get('parameters', {})

            # Basic validation
            errors = []

            if domain_type in ['schwarzschild', 'kerr']:
                if 'mass' not in parameters or parameters['mass'] <= 0:
                    errors.append('mass must be positive')

            if domain_type == 'hyperboloid':
                if 'curvature' not in parameters or parameters['curvature'] >= 0:
                    errors.append('curvature must be negative for hyperboloid')

            if domain_type == 'sphere':
                if 'radius' not in parameters or parameters['radius'] <= 0:
                    errors.append('radius must be positive')

            return {
                'status': 'success',
                'valid': len(errors) == 0,
                'errors': errors
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _serialize_descriptor(self, descriptor) -> Dict[str, Any]:
        """Serialize a domain descriptor to JSON-compatible dict"""
        return {
            'domain_id': descriptor.domain_id,
            'domain_type': descriptor.domain_type.value,
            'curvature_class': descriptor.curvature_class.value,
            'dimension': descriptor.dimension,
            'capabilities': asdict(descriptor.capabilities),
            'parameters': descriptor.parameters,
            'feature_traits': descriptor.feature_traits,
            'policy_constraints': descriptor.policy_constraints,
            'metadata': descriptor.metadata
        }


def create_api(registry, factory):
    """Create a DomainAPI instance"""
    return DomainAPI(registry, factory)
