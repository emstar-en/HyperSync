#!/usr/bin/env python3
"""
Domain Management CLI: Create Domain

Usage:
    python3 create.py <name> <type> <dimension> <tier> [--description DESC] [--config JSON]
"""

import sys
import json
import argparse

sys.path.insert(0, '../../')
from api.domains.create_domain import api_create_domain

def main():
    parser = argparse.ArgumentParser(description='Create a new HyperSync domain')
    parser.add_argument('name', help='Domain name')
    parser.add_argument('type', help='Domain type (euclidean, hyperbolic, spherical, lorentzian, product)')
    parser.add_argument('dimension', type=int, help='Domain dimension')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--description', help='Domain description')
    parser.add_argument('--config', help='Configuration as JSON string')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    config = None
    if args.config:
        try:
            config = json.loads(args.config)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --config", file=sys.stderr)
            sys.exit(1)

    result = api_create_domain(
        name=args.name,
        domain_type=args.type,
        dimension=args.dimension,
        tier=args.tier,
        description=args.description,
        config=config
    )

    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ {result['message']}")
        print(f"  Domain ID: {result['domain_id']}")
        print(f"  Name: {result['domain']['name']}")
        print(f"  Type: {result['domain']['type']}")
        print(f"  Dimension: {result['domain']['dimension']}")
        print()

if __name__ == '__main__':
    main()
