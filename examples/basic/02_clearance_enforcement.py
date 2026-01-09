#!/usr/bin/env python3
"""
Clearance Enforcement Example

Demonstrates clearance checking and redaction.
"""

from hypersync.security.policy.agent_policy_manager import AgentPolicyManager
from hypersync.agents.security.clearance_enforcer import ClearanceEnforcer
from hypersync.agents.redaction.pipeline import RedactionPipeline


def main():
    """Demonstrate clearance enforcement."""

    # Initialize policy manager
    policy_manager = AgentPolicyManager()

    # Load policy
    policy = {
        "policy_id": "policy-example",
        "version": "1.0.0",
        "rules": [
            {
                "rule_id": "rule-allow-internal",
                "effect": "allow",
                "principals": {
                    "types": ["agent"],
                    "clearance_levels": ["internal", "confidential"]
                },
                "actions": ["prompt:invoke"],
                "conditions": {
                    "clearance_escalation": True,
                    "require_redaction": True
                }
            }
        ]
    }

    policy_manager.load_policy(policy)

    # Create enforcer
    enforcer = ClearanceEnforcer(policy_manager)

    # Agent profile
    agent_profile = {
        'policy_bindings': {
            'clearance_level': 'confidential'
        }
    }

    # Check clearance
    result = enforcer.check_request_clearance(
        agent_id='agent-secure',
        requester_id='user-alice',
        agent_profile=agent_profile,
        action='prompt:invoke'
    )

    print(f"Clearance Check:")
    print(f"  Allowed: {result['allowed']}")
    print(f"  Escalation: {result['is_escalation']}")
    print(f"  Requires Redaction: {result['requires_redaction']}")

    # Apply redaction if needed
    if result['requires_redaction']:
        pipeline = RedactionPipeline.from_clearance(
            result['agent_clearance'],
            result['requester_clearance']
        )

        content = "Contact: john@example.com, Phone: 555-1234"
        redacted = pipeline.scrub(content, result['requester_clearance'])

        print(f"\nRedaction:")
        print(f"  Original: {content}")
        print(f"  Redacted: {redacted['content']}")
        print(f"  Items Redacted: {redacted['result']['items_redacted']}")


if __name__ == '__main__':
    main()
