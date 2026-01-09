#!/usr/bin/env python3
"""
Attestation Management CLI: Delete Policy

Usage:
    python3 delete.py <policy_id> <tier> [--force] [--yes] [--json]
"""

import sys
import json
import argparse

sys.path.insert(0, '../../')
from api.attestation.delete_policy import api_delete_attestation_policy

def main():
    parser = argparse.ArgumentParser(description='Delete attestation policy')
    parser.add_argument('policy_id', help='Policy ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--force', action='store_true', help='Force deletion')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if not args.yes:
        response = input(f"Delete policy '{args.policy_id}'? [y/N]: ")
        if response.lower() != 'y':
            print("Deletion cancelled.")
            sys.exit(0)

    result = api_delete_attestation_policy(
        policy_id=args.policy_id,
        tier=args.tier,
        force=args.force
    )

    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ {result['message']}")
        print()

if __name__ == '__main__':
    main()
