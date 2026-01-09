#!/usr/bin/env python3
"""
Attestation Management CLI: Update Policy

Usage:
    python3 update.py <policy_id> <tier> [--name NAME] [--description DESC] [--status STATUS] [--json]
"""

import sys
import json
import argparse

sys.path.insert(0, '../../')
from api.attestation.update_policy import api_update_attestation_policy

def main():
    parser = argparse.ArgumentParser(description='Update attestation policy')
    parser.add_argument('policy_id', help='Policy ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--name', help='New policy name')
    parser.add_argument('--description', help='New description')
    parser.add_argument('--status', help='New status (active, inactive, draft)')
    parser.add_argument('--requirements', help='Comma-separated requirements')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    requirements = None
    if args.requirements:
        requirements = [r.strip() for r in args.requirements.split(',')]

    result = api_update_attestation_policy(
        policy_id=args.policy_id,
        tier=args.tier,
        name=args.name,
        description=args.description,
        requirements=requirements,
        status=args.status
    )

    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ {result['message']}")
        print(f"  Updates applied:")
        for key, value in result['updates_applied'].items():
            print(f"    {key}: {value}")
        print()

if __name__ == '__main__':
    main()
