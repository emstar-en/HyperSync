"""
Environment Policy Verbs
Extends HyperSync policy system with filesystem and sandbox operations.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class EnvironmentVerb(Enum):
    """Environment-specific policy verbs"""
    # Filesystem operations
    FS_PATH_ALLOW = "fs:path:allow"
    FS_PATH_DENY = "fs:path:deny"
    FS_READ = "fs:read"
    FS_WRITE = "fs:write"
    FS_EXECUTE = "fs:execute"
    FS_LIST = "fs:list"
    FS_DELETE = "fs:delete"
    FS_DELETE_RECURSIVE = "fs:delete:recursive"

    # Sandbox operations
    SANDBOX_CREATE = "sandbox:create"
    SANDBOX_ACTIVATE = "sandbox:activate"
    SANDBOX_SUSPEND = "sandbox:suspend"
    SANDBOX_TERMINATE = "sandbox:terminate"
    SANDBOX_INSPECT = "sandbox:inspect"

    # Mount operations
    MOUNT_BIND = "mount:bind"
    MOUNT_DEVICE = "mount:device"
    MOUNT_NETWORK = "mount:network"


@dataclass
class EnvironmentPolicyRule:
    """Policy rule for environment operations"""
    rule_id: str
    verb: EnvironmentVerb
    effect: str  # "allow" or "deny"
    conditions: Dict
    priority: int = 100

    def matches(self, context: Dict) -> bool:
        """Check if rule matches given context"""
        # Check agent conditions
        if "agent" in self.conditions:
            agent_conds = self.conditions["agent"]
            agent_ctx = context.get("agent", {})

            # Check tier
            if "tier" in agent_conds:
                if agent_ctx.get("tier") not in agent_conds["tier"]:
                    return False

            # Check clearance
            if "clearance" in agent_conds:
                clearance_levels = ["public", "internal", "confidential", "restricted", "critical"]
                required = agent_conds["clearance"]
                actual = agent_ctx.get("clearance", "internal")

                if clearance_levels.index(actual) < clearance_levels.index(required):
                    return False

        # Check path conditions
        if "path" in self.conditions:
            path_conds = self.conditions["path"]
            target_path = context.get("path", "")

            # Check prefix
            if "prefix" in path_conds:
                if not any(target_path.startswith(p) for p in path_conds["prefix"]):
                    return False

            # Check pattern
            if "pattern" in path_conds:
                import re
                if not any(re.match(p, target_path) for p in path_conds["pattern"]):
                    return False

        # Check resource conditions
        if "resource" in self.conditions:
            res_conds = self.conditions["resource"]
            res_ctx = context.get("resource", {})

            # Check quotas
            if "max_disk_mb" in res_conds:
                if res_ctx.get("disk_mb", 0) > res_conds["max_disk_mb"]:
                    return False

        return True

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "verb": self.verb.value,
            "effect": self.effect,
            "conditions": self.conditions,
            "priority": self.priority
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'EnvironmentPolicyRule':
        return cls(
            rule_id=data["rule_id"],
            verb=EnvironmentVerb(data["verb"]),
            effect=data["effect"],
            conditions=data["conditions"],
            priority=data.get("priority", 100)
        )


class EnvironmentPolicyEngine:
    """Evaluates environment policy rules"""

    def __init__(self):
        self.rules: List[EnvironmentPolicyRule] = []

    def add_rule(self, rule: EnvironmentPolicyRule):
        """Add a policy rule"""
        self.rules.append(rule)
        # Sort by priority (higher first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def load_rules(self, rules_file: str):
        """Load rules from JSON file"""
        with open(rules_file, 'r') as f:
            data = json.load(f)

        for rule_data in data.get("rules", []):
            rule = EnvironmentPolicyRule.from_dict(rule_data)
            self.add_rule(rule)

    def evaluate(self, verb: EnvironmentVerb, context: Dict) -> bool:
        """
        Evaluate if operation is allowed.

        Args:
            verb: Operation being attempted
            context: Context including agent, path, resource info

        Returns:
            True if allowed, False if denied
        """
        # Default deny
        result = False

        # Evaluate rules in priority order
        for rule in self.rules:
            if rule.verb != verb:
                continue

            if rule.matches(context):
                if rule.effect == "allow":
                    result = True
                elif rule.effect == "deny":
                    return False  # Explicit deny overrides

        return result

    def explain(self, verb: EnvironmentVerb, context: Dict) -> Dict:
        """Explain policy decision"""
        matched_rules = []

        for rule in self.rules:
            if rule.verb == verb and rule.matches(context):
                matched_rules.append(rule.to_dict())

        decision = self.evaluate(verb, context)

        return {
            "verb": verb.value,
            "context": context,
            "decision": "allow" if decision else "deny",
            "matched_rules": matched_rules
        }


# Example policy rules
EXAMPLE_RULES = {
    "rules": [
        {
            "rule_id": "allow-internal-read",
            "verb": "fs:read",
            "effect": "allow",
            "conditions": {
                "agent": {"clearance": "internal"},
                "path": {"prefix": ["/home", "/var/log"]}
            },
            "priority": 100
        },
        {
            "rule_id": "deny-system-write",
            "verb": "fs:write",
            "effect": "deny",
            "conditions": {
                "path": {"prefix": ["/etc", "/sys", "/proc"]}
            },
            "priority": 200
        },
        {
            "rule_id": "allow-confidential-write",
            "verb": "fs:write",
            "effect": "allow",
            "conditions": {
                "agent": {"clearance": "confidential"},
                "path": {"prefix": ["/home", "/var/log"]}
            },
            "priority": 100
        }
    ]
}


if __name__ == "__main__":
    # Example usage
    engine = EnvironmentPolicyEngine()

    for rule_data in EXAMPLE_RULES["rules"]:
        rule = EnvironmentPolicyRule.from_dict(rule_data)
        engine.add_rule(rule)

    # Test read access
    context = {
        "agent": {"clearance": "internal", "tier": "basic"},
        "path": "/home/user/document.txt"
    }

    result = engine.evaluate(EnvironmentVerb.FS_READ, context)
    print(f"Read access: {result}")

    explanation = engine.explain(EnvironmentVerb.FS_READ, context)
    print(f"Explanation: {json.dumps(explanation, indent=2)}")
