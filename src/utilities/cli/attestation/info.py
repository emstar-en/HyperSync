#!/usr/bin/env python3
"""
Attestation Management CLI: Get Policy Info

Usage:
    python3 info.py <policy_id> <tier> [--rules] [--json]
"""

import sys
import json
import argparse

sys.path.insert(0, '../../')
from api.attestation.get_policy import api_get_attestation_policy

def main():
    parser = argparse.ArgumentParser(description='Get attestation policy information')
    parser.add_argument('policy_id', help='Policy ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--rules', action='store_true', help='Include validation rules')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    result = api_get_attestation_policy(
        policy_id=args.policy_id,
        tier=args.tier,
        include_rules=args.rules
    )

    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        policy = result['policy']
        print(f"\nPolicy Information:")
        print(f"  ID: {policy['id']}")
        print(f"  Name: {policy['name']}")
        print(f"  Type: {policy['type']}")
        print(f"  Status: {policy['status']}")
        print(f"  Description: {policy['description']}")
        print(f"  Requirements: {', '.join(policy['requirements'])}")

        if 'validation_rules' in policy:
            print(f"\n  Validation Rules:")
            for req, rules in policy['validation_rules'].items():
                print(f"    {req}:")
                for key, value in rules.items():
                    print(f"      {key}: {value}")
        print()

if __name__ == '__main__':
    main()
