#!/usr/bin/env python3
"""
Attestation Management CLI: Validate Attestation

Usage:
    python3 validate.py <policy_id> <tier> --data JSON [--json]
"""

import sys
import json
import argparse

sys.path.insert(0, '../../')
from api.attestation.validate_attestation import api_validate_attestation

def main():
    parser = argparse.ArgumentParser(description='Validate attestation')
    parser.add_argument('policy_id', help='Policy ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--data', required=True, help='Attestation data as JSON')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    try:
        attestation_data = json.loads(args.data)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in --data", file=sys.stderr)
        sys.exit(1)

    result = api_validate_attestation(
        policy_id=args.policy_id,
        attestation_data=attestation_data,
        tier=args.tier
    )

    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nValidation Result: {'✓ VALID' if result['valid'] else '✗ INVALID'}")
        print(f"  Policy: {result['policy_id']}")
        print(f"\n  Results:")
        for req, res in result['validation_results'].items():
            status = "✓" if res['valid'] else "✗"
            msg = res.get('message') or res.get('error')
            print(f"    {status} {req}: {msg}")
        print()

if __name__ == '__main__':
    main()
