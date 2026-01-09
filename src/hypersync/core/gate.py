from __future__ import annotations
from pathlib import Path
import json
from typing import Tuple, Optional

class PolicyGate:

    def _tier_allowed(self, operator_meta: dict) -> tuple[bool, str|None]:
        try:
            gating = (self.policy or {}).get('tier_gating', 'off')
            tier = (self.policy or {}).get('tier')
            deny = set((operator_meta or {}).get('deny_tiers') or [])
            if str(gating).lower() == 'enforced' and tier and tier in deny:
                return False, f"Tier {tier} denied for this operator"
        except Exception:
            pass
        return True, None

    def _privacy_allowed(self, operator_meta: dict) -> tuple[bool, str|None]:
        try:
            required = bool((self.policy or {}).get('privacy_enforced'))
            if required:
                tags = set((operator_meta or {}).get('tags') or [])
                if 'compliance' not in tags and 'privacy' not in tags:
                    return False, 'Privacy enforcement requires compliance or privacy tag'
        except Exception:
            pass
        return True, None
    def __init__(self, policy_path: Optional[Path] = None):
        self.policy_path = policy_path
        self.policy = {}
        if policy_path and policy_path.exists():
            try:
                self.policy = json.loads(policy_path.read_text())
            except Exception:
                self.policy = {}

    def check(self, intent: dict) -> Tuple[bool, Optional[str]]:
        try:
            tier = intent.get("meta", {}).get("tier")
            req = intent.get("params", {}).get("capability")
            if tier == "core" and req == "actuation":
                return False, "Actuation not allowed for core tier"
        except Exception:
            pass
        return True, None

    def check_operator(self, operator_meta: dict):
        """Enforce basic operator constraints from policy (e.g., deterministic)."""
        try:
            require_det = bool(self.policy.get('deterministic'))
            if require_det:
                if not operator_meta:
                    return True, None
                if not operator_meta.get('deterministic', False):
                    return False, 'Operator not deterministic under policy'
        except Exception:
            pass
        return True, None
