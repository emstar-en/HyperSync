"""
HyperSync Security Policy Manager
Manages user/model policies, hierarchies, and nLD threat detection
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ThreatLevel(Enum):
    """nLD threat levels"""
    SAFE = "safe"           # nLD = 1
    LOW = "low"             # nLD = 2-3
    MEDIUM = "medium"       # nLD = 4-6
    HIGH = "high"           # nLD = 7-10
    CRITICAL = "critical"   # nLD > 10


class PolicyEffect(Enum):
    """Policy rule effects"""
    ALLOW = "allow"
    DENY = "deny"
    AUDIT = "audit"


@dataclass
class LDTrainingRecord:
    """Record of training in a Lorentzian Domain"""
    ld_id: str
    geometry_type: str  # euclidean, hyperbolic, spherical, mixed
    training_epochs: int = 0
    curvature: float = 0.0
    verified: bool = False


@dataclass
class nLDThreatProfile:
    """Threat profile for multi-LD trained agents"""
    agent_id: str
    ld_training_history: List[LDTrainingRecord]
    nld_score: int
    threat_level: ThreatLevel
    detection_signals: Dict
    risk_assessment: Dict
    last_assessed: str

    def to_dict(self):
        data = asdict(self)
        data['threat_level'] = self.threat_level.value
        data['ld_training_history'] = [
            {**asdict(ld), 'geometry_type': ld.geometry_type}
            for ld in self.ld_training_history
        ]
        return data


@dataclass
class SecurityPolicy:
    """User or model security policy"""
    policy_id: str
    owner: Dict
    rules: List[Dict]
    nld_protection: Dict
    authentication: Optional[Dict] = None
    hierarchy: Optional[Dict] = None
    metadata: Optional[Dict] = None

    def to_dict(self):
        return asdict(self)


class nLDThreatDetector:
    """Detects and assesses nLD threats"""

    # Threat level thresholds
    THRESHOLDS = {
        ThreatLevel.SAFE: (1, 1),
        ThreatLevel.LOW: (2, 3),
        ThreatLevel.MEDIUM: (4, 6),
        ThreatLevel.HIGH: (7, 10),
        ThreatLevel.CRITICAL: (11, float('inf'))
    }

    def __init__(self):
        self.threat_profiles: Dict[str, nLDThreatProfile] = {}

    def calculate_nld_score(self, ld_training_history: List[LDTrainingRecord]) -> int:
        """Calculate nLD score (number of distinct LDs)"""
        unique_lds = set(ld.ld_id for ld in ld_training_history)
        return len(unique_lds)

    def determine_threat_level(self, nld_score: int) -> ThreatLevel:
        """Determine threat level from nLD score"""
        for level, (min_score, max_score) in self.THRESHOLDS.items():
            if min_score <= nld_score <= max_score:
                return level
        return ThreatLevel.CRITICAL

    def assess_risk(self, nld_score: int, detection_signals: Dict) -> Dict:
        """Assess risk factors based on nLD score and signals"""
        # Cross-boundary capability increases with nLD
        if nld_score == 1:
            cross_boundary = "none"
        elif nld_score <= 3:
            cross_boundary = "limited"
        elif nld_score <= 6:
            cross_boundary = "moderate"
        elif nld_score <= 10:
            cross_boundary = "high"
        else:
            cross_boundary = "extreme"

        # Instability risk increases with nLD
        if nld_score == 1:
            instability = "stable"
        elif nld_score <= 3:
            instability = "minor"
        elif nld_score <= 6:
            instability = "moderate"
        elif nld_score <= 10:
            instability = "significant"
        else:
            instability = "critical"

        # Recommended action
        if nld_score == 1:
            action = "allow"
        elif nld_score <= 3:
            action = "allow"
        elif nld_score <= 6:
            action = "monitor"
        elif nld_score <= 10:
            action = "restrict"
        else:
            action = "block"

        # Adjust based on detection signals
        if detection_signals.get("holonomy_inconsistency", 0) > 0.5:
            action = "block"
        if detection_signals.get("boundary_violations", 0) > 10:
            action = "block"

        return {
            "cross_boundary_capability": cross_boundary,
            "instability_risk": instability,
            "recommended_action": action
        }

    def scan_agent(
        self,
        agent_id: str,
        ld_training_history: List[LDTrainingRecord],
        detection_signals: Optional[Dict] = None
    ) -> nLDThreatProfile:
        """Scan an agent for nLD threats"""
        if detection_signals is None:
            detection_signals = {
                "holonomy_inconsistency": 0.0,
                "route_flap_rate": 0.0,
                "boundary_violations": 0,
                "calibration_error": 0.0
            }

        nld_score = self.calculate_nld_score(ld_training_history)
        threat_level = self.determine_threat_level(nld_score)
        risk_assessment = self.assess_risk(nld_score, detection_signals)

        profile = nLDThreatProfile(
            agent_id=agent_id,
            ld_training_history=ld_training_history,
            nld_score=nld_score,
            threat_level=threat_level,
            detection_signals=detection_signals,
            risk_assessment=risk_assessment,
            last_assessed=datetime.utcnow().isoformat()
        )

        self.threat_profiles[agent_id] = profile
        return profile

    def is_threat_blocked(self, profile: nLDThreatProfile, policy: SecurityPolicy) -> bool:
        """Check if threat should be blocked by policy"""
        nld_config = policy.nld_protection

        # Auto-block critical threats if enabled
        if nld_config.get("auto_block_critical", True):
            if profile.threat_level == ThreatLevel.CRITICAL:
                return True

        # Check against max allowed nLD score
        max_nld = nld_config.get("max_nld_score", 6)
        if profile.nld_score > max_nld:
            return True

        # Check recommended action
        if profile.risk_assessment["recommended_action"] == "block":
            return True

        return False


class SecurityPolicyManager:
    """Manages security policies and enforcement"""

    def __init__(self, storage_path: str = ".hypersync/security"):
        self.storage_path = storage_path
        self.policies: Dict[str, SecurityPolicy] = {}
        self.identities: Dict[str, Dict] = {}
        self.threat_detector = nLDThreatDetector()
        self._load_policies()

    def _load_policies(self):
        """Load policies from storage"""
        import os
        if os.path.exists(f"{self.storage_path}/policies.json"):
            with open(f"{self.storage_path}/policies.json", 'r') as f:
                data = json.load(f)
                for policy_data in data:
                    policy = SecurityPolicy(**policy_data)
                    self.policies[policy.policy_id] = policy

    def _save_policies(self):
        """Save policies to storage"""
        import os
        os.makedirs(self.storage_path, exist_ok=True)
        with open(f"{self.storage_path}/policies.json", 'w') as f:
            json.dump([p.to_dict() for p in self.policies.values()], f, indent=2)

    def create_policy(
        self,
        policy_id: str,
        owner_type: str,
        owner_id: str,
        rules: List[Dict],
        nld_max_score: int = 6,
        priority: int = 50
    ) -> SecurityPolicy:
        """Create a new security policy"""
        policy = SecurityPolicy(
            policy_id=policy_id,
            owner={
                "type": owner_type,
                "id": owner_id,
                "priority": priority
            },
            rules=rules,
            nld_protection={
                "enabled": True,
                "max_nld_score": nld_max_score,
                "auto_block_critical": True,
                "audit_medium_threats": True
            },
            authentication={
                "enabled": False,
                "method": "none"
            },
            hierarchy={
                "parent_nodes": [],
                "child_nodes": [],
                "inherit_policies": True
            },
            metadata={
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        )

        self.policies[policy_id] = policy
        self._save_policies()
        return policy

    def get_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Get a policy by ID"""
        return self.policies.get(policy_id)

    def list_policies(self, owner_id: Optional[str] = None) -> List[SecurityPolicy]:
        """List all policies, optionally filtered by owner"""
        if owner_id:
            return [p for p in self.policies.values() if p.owner["id"] == owner_id]
        return list(self.policies.values())

    def update_policy(self, policy_id: str, updates: Dict) -> Optional[SecurityPolicy]:
        """Update an existing policy"""
        policy = self.policies.get(policy_id)
        if not policy:
            return None

        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)

        if policy.metadata:
            policy.metadata["updated_at"] = datetime.utcnow().isoformat()

        self._save_policies()
        return policy

    def delete_policy(self, policy_id: str) -> bool:
        """Delete a policy"""
        if policy_id in self.policies:
            del self.policies[policy_id]
            self._save_policies()
            return True
        return False

    def scan_threat(
        self,
        agent_id: str,
        ld_training_history: List[Dict],
        detection_signals: Optional[Dict] = None
    ) -> nLDThreatProfile:
        """Scan an agent for nLD threats"""
        ld_records = [LDTrainingRecord(**ld) for ld in ld_training_history]
        return self.threat_detector.scan_agent(agent_id, ld_records, detection_signals)

    def check_access(
        self,
        agent_id: str,
        action: str,
        policy_id: str,
        threat_profile: Optional[nLDThreatProfile] = None
    ) -> Tuple[bool, str]:
        """Check if an agent can perform an action under a policy"""
        policy = self.get_policy(policy_id)
        if not policy:
            return False, "Policy not found"

        # Check nLD threat if profile provided
        if threat_profile and policy.nld_protection.get("enabled", True):
            if self.threat_detector.is_threat_blocked(threat_profile, policy):
                return False, f"Blocked: nLD threat level {threat_profile.threat_level.value}"

        # Check policy rules
        for rule in policy.rules:
            if self._match_action(action, rule["action"]):
                if rule["effect"] == "deny":
                    return False, f"Denied by rule: {rule['rule_id']}"
                elif rule["effect"] == "allow":
                    return True, f"Allowed by rule: {rule['rule_id']}"

        # Default deny
        return False, "No matching allow rule"

    def _match_action(self, action: str, pattern: str) -> bool:
        """Match action against pattern (supports wildcards)"""
        import fnmatch
        return fnmatch.fnmatch(action, pattern)

    def set_node_hierarchy(
        self,
        node_id: str,
        parent_id: Optional[str] = None,
        priority: int = 50
    ):
        """Set node hierarchy and priority"""
        if node_id not in self.identities:
            self.identities[node_id] = {
                "node_id": node_id,
                "priority": priority,
                "hierarchy": {}
            }

        if parent_id:
            self.identities[node_id]["hierarchy"]["parent_id"] = parent_id

        self.identities[node_id]["priority"] = priority

    def get_effective_priority(self, node_id: str) -> int:
        """Get effective priority considering hierarchy"""
        if node_id not in self.identities:
            return 0
        return self.identities[node_id].get("priority", 0)


# Default system policy
def create_default_policy() -> Dict:
    """Create default system security policy"""
    return {
        "policy_id": "system_default",
        "owner": {
            "type": "system",
            "id": "hypersync",
            "priority": 100
        },
        "rules": [
            {
                "rule_id": "allow_safe_operations",
                "action": "nvm:read",
                "effect": "allow"
            },
            {
                "rule_id": "allow_routing",
                "action": "ico:route",
                "effect": "allow"
            },
            {
                "rule_id": "audit_policy_changes",
                "action": "policy:*",
                "effect": "audit"
            }
        ],
        "nld_protection": {
            "enabled": True,
            "max_nld_score": 6,
            "auto_block_critical": True,
            "audit_medium_threats": True
        },
        "authentication": {
            "enabled": False,
            "method": "none"
        }
    }
