"""
Schema Registry for HyperSync Database

Stores entity metadata, geodesic constraints, and index manifests with
curvature-aware validation.
"""
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class FieldType(Enum):
    """Field data types."""
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    TIMESTAMP = "timestamp"
    UUID = "uuid"
    CURVATURE = "curvature"
    GEODESIC = "geodesic"
    HYPERBOLIC_POINT = "hyperbolic_point"


@dataclass
class FieldConstraint:
    """Constraint on a field."""
    name: str
    validator: Callable[[Any], bool]
    error_message: str


@dataclass
class FieldDefinition:
    """Definition of a schema field."""
    name: str
    field_type: FieldType
    nullable: bool = True
    default: Any = None
    curvature: Optional[float] = None
    precision: Optional[float] = None
    constraints: List[FieldConstraint] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self, value: Any) -> bool:
        """
        Validate value against field definition.

        Args:
            value: Value to validate

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        # Check nullable
        if value is None:
            if not self.nullable:
                raise ValueError(f"Field {self.name} cannot be null")
            return True

        # Check type
        if not self._check_type(value):
            raise ValueError(f"Field {self.name} has invalid type")

        # Check constraints
        for constraint in self.constraints:
            if not constraint.validator(value):
                raise ValueError(f"Field {self.name}: {constraint.error_message}")

        # Check curvature precision
        if self.field_type == FieldType.CURVATURE and self.precision:
            if abs(value - round(value / self.precision) * self.precision) > 1e-10:
                raise ValueError(f"Field {self.name} violates precision constraint")

        return True

    def _check_type(self, value: Any) -> bool:
        """Check if value matches field type."""
        type_checks = {
            FieldType.INTEGER: lambda v: isinstance(v, int),
            FieldType.FLOAT: lambda v: isinstance(v, (int, float)),
            FieldType.STRING: lambda v: isinstance(v, str),
            FieldType.BOOLEAN: lambda v: isinstance(v, bool),
            FieldType.CURVATURE: lambda v: isinstance(v, (int, float)),
            FieldType.HYPERBOLIC_POINT: lambda v: isinstance(v, (tuple, list)) and len(v) == 2
        }

        checker = type_checks.get(self.field_type)
        if checker:
            return checker(value)

        return True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'type': self.field_type.value,
            'nullable': self.nullable,
            'default': self.default,
            'curvature': self.curvature,
            'precision': self.precision,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FieldDefinition':
        """Create from dictionary."""
        return cls(
            name=data['name'],
            field_type=FieldType(data['type']),
            nullable=data.get('nullable', True),
            default=data.get('default'),
            curvature=data.get('curvature'),
            precision=data.get('precision'),
            metadata=data.get('metadata', {})
        )


@dataclass
class IndexDefinition:
    """Definition of an index."""
    name: str
    relation: str
    columns: List[str]
    index_type: str = "btree"  # btree, geodesic, hyperbolic
    unique: bool = False
    curvature_aware: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'relation': self.relation,
            'columns': self.columns,
            'index_type': self.index_type,
            'unique': self.unique,
            'curvature_aware': self.curvature_aware,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'IndexDefinition':
        """Create from dictionary."""
        return cls(
            name=data['name'],
            relation=data['relation'],
            columns=data['columns'],
            index_type=data.get('index_type', 'btree'),
            unique=data.get('unique', False),
            curvature_aware=data.get('curvature_aware', False),
            metadata=data.get('metadata', {})
        )


@dataclass
class RelationSchema:
    """Schema for a relation."""
    name: str
    fields: List[FieldDefinition]
    primary_key: Optional[List[str]] = None
    geodesic_constraints: List[dict] = field(default_factory=list)
    curvature: float = -1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_record(self, record: dict) -> bool:
        """
        Validate record against schema.

        Args:
            record: Record to validate

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        # Check all fields
        field_map = {f.name: f for f in self.fields}

        for field_name, field_def in field_map.items():
            value = record.get(field_name)
            field_def.validate(value)

        # Check for unknown fields
        for key in record.keys():
            if key not in field_map and not key.startswith('_'):
                logger.warning(f"Unknown field in record: {key}")

        return True

    def get_field(self, name: str) -> Optional[FieldDefinition]:
        """Get field definition by name."""
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'fields': [f.to_dict() for f in self.fields],
            'primary_key': self.primary_key,
            'geodesic_constraints': self.geodesic_constraints,
            'curvature': self.curvature,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RelationSchema':
        """Create from dictionary."""
        return cls(
            name=data['name'],
            fields=[FieldDefinition.from_dict(f) for f in data['fields']],
            primary_key=data.get('primary_key'),
            geodesic_constraints=data.get('geodesic_constraints', []),
            curvature=data.get('curvature', -1.0),
            metadata=data.get('metadata', {})
        )


class SchemaRegistry:
    """
    Registry for database schemas.

    Stores entity metadata, geodesic constraints, and index manifests.
    Provides schema validation DSL.
    """

    def __init__(self):
        self.schemas: Dict[str, RelationSchema] = {}
        self.indices: Dict[str, List[IndexDefinition]] = {}
        self._decorators = {}

    def register_schema(self, schema: RelationSchema):
        """
        Register schema.

        Args:
            schema: Schema to register
        """
        self.schemas[schema.name] = schema
        self.indices[schema.name] = []
        logger.info(f"Registered schema: {schema.name}")

    def get_schema(self, name: str) -> Optional[RelationSchema]:
        """Get schema by name."""
        return self.schemas.get(name)

    def register_index(self, index: IndexDefinition):
        """
        Register index.

        Args:
            index: Index definition
        """
        if index.relation not in self.indices:
            self.indices[index.relation] = []

        self.indices[index.relation].append(index)
        logger.info(f"Registered index: {index.name} on {index.relation}")

    def get_indices(self, relation: str) -> List[IndexDefinition]:
        """Get indices for relation."""
        return self.indices.get(relation, [])

    def validate_record(self, relation: str, record: dict) -> bool:
        """
        Validate record against schema.

        Args:
            relation: Relation name
            record: Record to validate

        Returns:
            True if valid
        """
        schema = self.get_schema(relation)
        if not schema:
            raise ValueError(f"Schema not found: {relation}")

        return schema.validate_record(record)

    def field(self, curvature: Optional[float] = None, precision: Optional[float] = None, **kwargs):
        """
        Decorator for field definitions.

        Usage:
            @schema.field(curvature="negative", precision=1e-3)
            class MyField:
                pass
        """
        def decorator(cls):
            # Store field metadata
            field_name = cls.__name__
            self._decorators[field_name] = {
                'curvature': curvature,
                'precision': precision,
                **kwargs
            }
            return cls

        return decorator

    def save(self, path: str):
        """Save registry to file."""
        data = {
            'schemas': {name: schema.to_dict() for name, schema in self.schemas.items()},
            'indices': {
                relation: [idx.to_dict() for idx in indices]
                for relation, indices in self.indices.items()
            }
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved schema registry to {path}")

    @classmethod
    def load(cls, path: str) -> 'SchemaRegistry':
        """Load registry from file."""
        registry = cls()

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            # Load schemas
            for name, schema_data in data.get('schemas', {}).items():
                schema = RelationSchema.from_dict(schema_data)
                registry.register_schema(schema)

            # Load indices
            for relation, indices_data in data.get('indices', {}).items():
                for idx_data in indices_data:
                    index = IndexDefinition.from_dict(idx_data)
                    registry.register_index(index)

            logger.info(f"Loaded schema registry from {path}")
        except FileNotFoundError:
            logger.info(f"No existing registry at {path}, starting fresh")

        return registry


# Helper functions for schema building
def create_field(
    name: str,
    field_type: FieldType,
    nullable: bool = True,
    default: Any = None,
    curvature: Optional[float] = None,
    precision: Optional[float] = None
) -> FieldDefinition:
    """Helper to create field definition."""
    return FieldDefinition(
        name=name,
        field_type=field_type,
        nullable=nullable,
        default=default,
        curvature=curvature,
        precision=precision
    )


def create_schema(
    name: str,
    fields: List[FieldDefinition],
    primary_key: Optional[List[str]] = None,
    curvature: float = -1.0
) -> RelationSchema:
    """Helper to create relation schema."""
    return RelationSchema(
        name=name,
        fields=fields,
        primary_key=primary_key,
        curvature=curvature
    )


# Export public API
__all__ = [
    'SchemaRegistry',
    'RelationSchema',
    'FieldDefinition',
    'IndexDefinition',
    'FieldType',
    'FieldConstraint',
    'create_field',
    'create_schema'
]
