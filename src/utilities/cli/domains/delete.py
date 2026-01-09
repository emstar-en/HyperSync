#!/usr/bin/env python3
"""
Domain Management CLI: Delete Domain

Usage:
    python3 delete.py <domain_id> <tier> [--force]
"""

import sys
import json
import argparse

sys.path.insert(0, '../../')
from api.domains.delete_domain import api_delete_domain

def main():
    parser = argparse.ArgumentParser(description='Delete a HyperSync domain')
    parser.add_argument('domain_id', help='Domain ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--force', action='store_true', help='Force deletion even with active operations')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')

    args = parser.parse_args()

    # Confirmation
    if not args.yes:
        response = input(f"Are you sure you want to delete domain '{args.domain_id}'? [y/N]: ")
        if response.lower() != 'y':
            print("Deletion cancelled.")
            sys.exit(0)

    result = api_delete_domain(
        domain_id=args.domain_id,
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
        if result['forced']:
            print("  (Forced deletion)")
        print()

if __name__ == '__main__':
    main()
