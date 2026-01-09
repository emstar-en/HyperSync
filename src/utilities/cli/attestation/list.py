#!/usr/bin/env python3
"""
Attestation Management CLI: List Policies

Usage:
    python3 list.py <tier> [--type TYPE] [--status STATUS] [--json]
"""

import sys
import json
import argparse

sys.path.insert(0, '../../')
from api.attestation.list_policies import api_list_attestation_policies

def main():
    parser = argparse.ArgumentParser(description='List attestation policies')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--type', help='Filter by policy type')
    parser.add_argument('--status', help='Filter by status')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    result = api_list_attestation_policies(
        tier=args.tier,
        filter_type=args.type,
        filter_status=args.status
    )

    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nAttestation Policies for tier: {result['tier']}")
        print(f"Total: {result['count']}\n")
        print(f"{'ID':<15} {'Name':<25} {'Type':<12} {'Status':<10}")
        print("-" * 65)
        for policy in result['policies']:
            print(f"{policy['id']:<15} {policy['name']:<25} {policy['type']:<12} {policy['status']:<10}")
        print()

if __name__ == '__main__':
    main()
