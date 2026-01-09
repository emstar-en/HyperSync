#!/usr/bin/env python3
"""
Attestation Management CLI: Create Policy

Usage:
    python3 create.py <name> <type> <tier> [--description DESC] [--requirements REQ1,REQ2] [--json]
"""

import sys
import json
import argparse

sys.path.insert(0, '../../')
from api.attestation.create_policy import api_create_attestation_policy

def main():
    parser = argparse.ArgumentParser(description='Create attestation policy')
    parser.add_argument('name', help='Policy name')
    parser.add_argument('type', help='Policy type (basic, standard, strict, quantum)')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--description', help='Policy description')
    parser.add_argument('--requirements', help='Comma-separated requirements')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    requirements = None
    if args.requirements:
        requirements = [r.strip() for r in args.requirements.split(',')]

    result = api_create_attestation_policy(
        name=args.name,
        policy_type=args.type,
        tier=args.tier,
        description=args.description,
        requirements=requirements
    )

    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ {result['message']}")
        print(f"  Policy ID: {result['policy_id']}")
        print(f"  Type: {result['policy']['type']}")
        print(f"  Requirements: {', '.join(result['policy']['requirements'])}")
        print()

if __name__ == '__main__':
    main()
