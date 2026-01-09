#!/usr/bin/env python3
"""
Domain Management CLI: Update Domain

Usage:
    python3 update.py <domain_id> <tier> [--name NAME] [--description DESC] [--status STATUS] [--config JSON]
"""

import sys
import json
import argparse

sys.path.insert(0, '../../')
from api.domains.update_domain import api_update_domain

def main():
    parser = argparse.ArgumentParser(description='Update a HyperSync domain')
    parser.add_argument('domain_id', help='Domain ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--name', help='New domain name')
    parser.add_argument('--description', help='New description')
    parser.add_argument('--status', help='New status (active, inactive, maintenance)')
    parser.add_argument('--config', help='Configuration updates as JSON string')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    config = None
    if args.config:
        try:
            config = json.loads(args.config)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --config", file=sys.stderr)
            sys.exit(1)

    result = api_update_domain(
        domain_id=args.domain_id,
        tier=args.tier,
        name=args.name,
        description=args.description,
        config=config,
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
