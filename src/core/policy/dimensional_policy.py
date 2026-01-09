"""
HyperSync Dimensional Policy Extension

Extends PromptPolicyManager with dimensional sharing and alignment verbs.
Implements clearance inheritance and dimension exposure limits.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SubjectType(Enum):
    """Subject types for clearances."""
    USER = "user"
    AGENT = "agent"
    WORKLOAD = "workload"
    NODE = "node"


class AccessLevel(Enum):
    """Per-dimension access levels."""
    READ = "read"
    WRITE = "write"
    NONE = "none"


class ClearanceLevel(Enum):
    """Clearance levels."""
    ADMIN = "admin"
    POWER_USER = "power_user"
    USER = "user"
    RESTRICTED = "restricted"


@dataclass
class DimensionRestriction:
    """Per-dimension access restriction."""
    dimension_id: int
    access_level: AccessLevel


@dataclass
class DimensionalPermissions:
    """Dimensional permissions for a subject."""
    max_dimensions: int
    allowed_actions: Set[str]
    dimension_restrictions: List[DimensionRestriction] = field(default_factory=list)
    curvature_min: float = -1.0
    curvature_max: float = 0.0

    def can_perform_action(self, action: str) -> bool:
        """Check if action is allowed."""
        # Support wildcard matching
        for allowed in self.allowed_actions:
            if allowed.endswith("*"):
                prefix = allowed[:-1]
                if action.startswith(prefix):
                    return True
            elif allowed == action:
                return True
        return False

    def can_access_dimension(self, dim_id: int, access_type: AccessLevel) -> bool:
        """Check if dimension access is allowed."""
        # Check if dimension has specific restriction
        for restriction in self.dimension_restrictions:
            if restriction.dimension_id == dim_id:
                if access_type == AccessLevel.READ:
                    return restriction.access_level in [AccessLevel.READ, AccessLevel.WRITE]
                elif access_type == AccessLevel.WRITE:
                    return restriction.access_level == AccessLevel.WRITE
                else:
                    return False

        # No specific restriction, allow if within max_dimensions
        return dim_id < self.max_dimensions

    def can_use_curvature(self, curvature: float) -> bool:
        """Check if curvature value is allowed."""
        return self.curvature_min <= curvature <= self.curvature_max


@dataclass
class DimensionalClearance:
    """
    Dimensional access clearance for a subject.
    """
    clearance_id: str
    subject_type: SubjectType
    subject_id: str
    permissions: DimensionalPermissions

    parent_clearance_id: Optional[str] = None
    inheritance_enabled: bool = True
    override_allowed: bool = False

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    revoked: bool = False

    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def is_valid(self) -> bool:
        """Check if clearance is currently valid."""
        if self.revoked:
            return False

        now = datetime.now()

        if self.start_time and now < self.start_time:
            return False

        if self.end_time and now > self.end_time:
            return False

        return True

    def to_dict(self) -> Dict:
        """Export clearance to dictionary."""
        return {
            "clearance_id": self.clearance_id,
            "subject": {
                "type": self.subject_type.value,
                "id": self.subject_id,
                "parent_clearance_id": self.parent_clearance_id
            },
            "dimensional_permissions": {
                "max_dimensions": self.permissions.max_dimensions,
                "allowed_actions": list(self.permissions.allowed_actions),
                "dimension_restrictions": [
                    {
                        "dimension_id": r.dimension_id,
                        "access_level": r.access_level.value
                    }
                    for r in self.permissions.dimension_restrictions
                ],
                "curvature_bounds": {
                    "min": self.permissions.curvature_min,
                    "max": self.permissions.curvature_max
                }
            },
            "inheritance": {
                "enabled": self.inheritance_enabled,
                "override_allowed": self.override_allowed
            },
            "validity": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "revoked": self.revoked
            },
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "created_by": self.created_by,
                "updated_at": self.updated_at.isoformat(),
                "tags": self.tags
            }
        }


@dataclass
class PolicyRule:
    """Dimensional policy rule."""
    rule_id: str
    action: str
    effect: str  # "allow" or "deny"
    conditions: Dict = field(default_factory=dict)
    priority: int = 0

    def matches(self, action: str, context: Dict) -> bool:
        """Check if rule matches action and context."""
        # Check action pattern
        if not self._matches_action(action):
            return False

        # Check conditions
        return self._matches_conditions(context)

    def _matches_action(self, action: str) -> bool:
        """Check if action matches rule pattern."""
        if self.action.endswith("*"):
            prefix = self.action[:-1]
            return action.startswith(prefix)
        return self.action == action

    def _matches_conditions(self, context: Dict) -> bool:
        """Check if context matches rule conditions."""
        for key, value in self.conditions.items():
            if key == "subject_type":
                if context.get("subject_type") not in value:
                    return False
            elif key == "clearance_level":
                if context.get("clearance_level") != value:
                    return False
            elif key == "dimension_count":
                dim_count = len(context.get("dimensions", []))
                if "min" in value and dim_count < value["min"]:
                    return False
                if "max" in value and dim_count > value["max"]:
                    return False
            elif key == "trust_level":
                if context.get("trust_level") not in value:
                    return False

        return True


class DimensionalPolicyManager:
    """
    Manages dimensional clearances and policy evaluation.

    Integrates with PromptPolicyManager to add dimensional verbs.
    """

    # Standard dimensional actions
    DIMENSIONAL_ACTIONS = {
        "dim:share",
        "dim:align",
        "dim:sync",
        "vector:attach",
        "vector:query",
        "contract:create",
        "contract:view",
        "route:negotiate"
    }

    def __init__(self, base_policy_manager=None):
        """
        Initialize policy manager.

        Args:
            base_policy_manager: Base PromptPolicyManager instance (optional)
        """
        self.base_manager = base_policy_manager
        self.clearances: Dict[str, DimensionalClearance] = {}
        self.rules: List[PolicyRule] = []

        # Clearance hierarchy: subject_id -> clearance_id
        self.subject_clearances: Dict[str, str] = {}

    def register_clearance(self, clearance: DimensionalClearance):
        """Register a dimensional clearance."""
        self.clearances[clearance.clearance_id] = clearance
        self.subject_clearances[clearance.subject_id] = clearance.clearance_id

    def add_rule(self, rule: PolicyRule):
        """Add a policy rule."""
        self.rules.append(rule)
        # Sort by priority (descending)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def get_clearance(self, subject_id: str) -> Optional[DimensionalClearance]:
        """Get clearance for subject."""
        clearance_id = self.subject_clearances.get(subject_id)
        if not clearance_id:
            return None
        return self.clearances.get(clearance_id)

    def get_effective_permissions(self, subject_id: str) -> Optional[DimensionalPermissions]:
        """
        Get effective permissions for subject, including inheritance.

        Args:
            subject_id: Subject identifier

        Returns:
            Effective DimensionalPermissions or None
        """
        clearance = self.get_clearance(subject_id)
        if not clearance or not clearance.is_valid():
            return None

        # Start with subject's own permissions
        effective = DimensionalPermissions(
            max_dimensions=clearance.permissions.max_dimensions,
            allowed_actions=clearance.permissions.allowed_actions.copy(),
            dimension_restrictions=clearance.permissions.dimension_restrictions.copy(),
            curvature_min=clearance.permissions.curvature_min,
            curvature_max=clearance.permissions.curvature_max
        )

        # Apply inheritance if enabled
        if clearance.inheritance_enabled and clearance.parent_clearance_id:
            parent = self.clearances.get(clearance.parent_clearance_id)
            if parent and parent.is_valid():
                # Inherit from parent (more restrictive wins)
                if not clearance.override_allowed:
                    effective.max_dimensions = min(
                        effective.max_dimensions,
                        parent.permissions.max_dimensions
                    )

                    # Intersect allowed actions
                    effective.allowed_actions &= parent.permissions.allowed_actions

                    # Narrow curvature bounds
                    effective.curvature_min = max(
                        effective.curvature_min,
                        parent.permissions.curvature_min
                    )
                    effective.curvature_max = min(
                        effective.curvature_max,
                        parent.permissions.curvature_max
                    )

        return effective

    def evaluate(self, action: str, subject_id: str, context: Dict) -> Dict:
        """
        Evaluate dimensional policy for an action.

        Args:
            action: Dimensional action (e.g., "dim:share")
            subject_id: Subject performing action
            context: Additional context (dimensions, curvature, etc.)

        Returns:
            Policy decision dict with "allowed" and "reason"
        """
        # Get effective permissions
        permissions = self.get_effective_permissions(subject_id)
        if not permissions:
            return {
                "allowed": False,
                "reason": "No valid clearance found for subject"
            }

        # Check if action is allowed
        if not permissions.can_perform_action(action):
            return {
                "allowed": False,
                "reason": f"Action '{action}' not permitted by clearance"
            }

        # Check dimension count
        dimensions = context.get("dimensions", [])
        if len(dimensions) > permissions.max_dimensions:
            return {
                "allowed": False,
                "reason": f"Dimension count {len(dimensions)} exceeds limit {permissions.max_dimensions}"
            }

        # Check per-dimension access
        access_type = AccessLevel.WRITE if "write" in action else AccessLevel.READ
        for dim_id in dimensions:
            if not permissions.can_access_dimension(dim_id, access_type):
                return {
                    "allowed": False,
                    "reason": f"Access denied for dimension {dim_id}"
                }

        # Check curvature bounds
        curvature = context.get("curvature")
        if curvature is not None:
            if not permissions.can_use_curvature(curvature):
                return {
                    "allowed": False,
                    "reason": f"Curvature {curvature} outside allowed bounds"
                }

        # Evaluate policy rules
        clearance = self.get_clearance(subject_id)
        rule_context = {
            "subject_type": clearance.subject_type.value,
            "dimensions": dimensions,
            **context
        }

        for rule in self.rules:
            if rule.matches(action, rule_context):
                if rule.effect == "deny":
                    return {
                        "allowed": False,
                        "reason": f"Denied by policy rule {rule.rule_id}"
                    }
                elif rule.effect == "allow":
                    return {
                        "allowed": True,
                        "reason": f"Allowed by policy rule {rule.rule_id}"
                    }

        # Default allow if no rules matched
        return {
            "allowed": True,
            "reason": "Allowed by clearance permissions"
        }

    def revoke_clearance(self, clearance_id: str):
        """Revoke a clearance."""
        if clearance_id in self.clearances:
            self.clearances[clearance_id].revoked = True
            self.clearances[clearance_id].updated_at = datetime.now()

    def get_statistics(self) -> Dict:
        """Get policy manager statistics."""
        valid_clearances = len([c for c in self.clearances.values() if c.is_valid()])

        return {
            "total_clearances": len(self.clearances),
            "valid_clearances": valid_clearances,
            "revoked_clearances": len([c for c in self.clearances.values() if c.revoked]),
            "total_rules": len(self.rules),
            "subjects": len(self.subject_clearances)
        }
