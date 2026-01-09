"""
Migration 011: Seed Agent Clearances

Seeds initial clearance levels and policies for agent-based access control.
"""

import json
from datetime import datetime


def seed_default_policies():
    """Create default agent policies."""

    policies = [
        {
            "policy_id": "policy-agent-default",
            "version": "1.0.0",
            "name": "Default Agent Policy",
            "description": "Default policy for agent-mediated requests",
            "rules": [
                {
                    "rule_id": "rule-allow-internal-agents",
                    "effect": "allow",
                    "principals": {
                        "types": ["agent"],
                        "clearance_levels": ["internal", "restricted", "confidential", "secret"]
                    },
                    "actions": ["prompt:invoke", "node:delegate"],
                    "conditions": {
                        "clearance_escalation": True,
                        "require_redaction": True,
                        "max_delegation_depth": 3
                    }
                },
                {
                    "rule_id": "rule-deny-public-escalation",
                    "effect": "deny",
                    "principals": {
                        "types": ["agent"],
                        "clearance_levels": ["public"]
                    },
                    "actions": ["prompt:invoke"],
                    "conditions": {
                        "clearance_escalation": True
                    }
                }
            ],
            "clearance_matrix": {
                "levels": ["public", "internal", "restricted", "confidential", "secret"],
                "inheritance": {
                    "public": [],
                    "internal": ["public"],
                    "restricted": ["public", "internal"],
                    "confidential": ["public", "internal", "restricted"],
                    "secret": ["public", "internal", "restricted", "confidential"]
                }
            },
            "metadata": {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "created_by": "system:migration-011"
            }
        },
        {
            "policy_id": "policy-agent-strict",
            "version": "1.0.0",
            "name": "Strict Agent Policy",
            "description": "Strict policy preventing clearance escalation",
            "rules": [
                {
                    "rule_id": "rule-no-escalation",
                    "effect": "deny",
                    "principals": {
                        "types": ["agent"]
                    },
                    "actions": ["prompt:invoke"],
                    "conditions": {
                        "clearance_escalation": True
                    }
                },
                {
                    "rule_id": "rule-allow-same-level",
                    "effect": "allow",
                    "principals": {
                        "types": ["agent"]
                    },
                    "actions": ["prompt:invoke", "node:delegate"],
                    "conditions": {
                        "clearance_escalation": False,
                        "max_delegation_depth": 2
                    }
                }
            ],
            "metadata": {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "created_by": "system:migration-011"
            }
        }
    ]

    return policies


def seed_clearance_mappings():
    """Create default clearance mappings for users/agents."""

    return {
        "users": {
            "user-admin": "secret",
            "user-operator": "confidential",
            "user-developer": "internal",
            "user-guest": "public"
        },
        "agents": {
            "agent-default": "internal",
            "agent-secure": "confidential",
            "agent-public": "public"
        }
    }


def run_migration(policy_store_path: str = "~/.hypersync/policies.json",
                 clearance_store_path: str = "~/.hypersync/clearances.json"):
    """
    Execute migration to seed agent clearances.

    Args:
        policy_store_path: Path to policy storage
        clearance_store_path: Path to clearance storage
    """
    import os
    from pathlib import Path

    # Expand paths
    policy_path = Path(policy_store_path).expanduser()
    clearance_path = Path(clearance_store_path).expanduser()

    # Create directories
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    clearance_path.parent.mkdir(parents=True, exist_ok=True)

    # Seed policies
    policies = seed_default_policies()
    policy_data = {
        "policies": {p["policy_id"]: p for p in policies},
        "migrated_at": datetime.utcnow().isoformat() + "Z",
        "migration_version": "011"
    }

    with open(policy_path, 'w') as f:
        json.dump(policy_data, f, indent=2)

    print(f"✓ Seeded {len(policies)} policies to {policy_path}")

    # Seed clearances
    clearances = seed_clearance_mappings()
    clearance_data = {
        "clearances": clearances,
        "migrated_at": datetime.utcnow().isoformat() + "Z",
        "migration_version": "011"
    }

    with open(clearance_path, 'w') as f:
        json.dump(clearance_data, f, indent=2)

    print(f"✓ Seeded clearance mappings to {clearance_path}")
    print("\nMigration 011 complete!")


if __name__ == '__main__':
    run_migration()
