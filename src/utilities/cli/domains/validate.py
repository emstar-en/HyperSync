#!/usr/bin/env python3
"""
Domain Management CLI: Validate Domain Configuration

Usage:
    python3 validate.py <type> <dimension> <tier> --config JSON
"""

import sys
import json
import argparse

sys.path.insert(0, '../../')
from api.domains.validate_domain_config import api_validate_domain_config

def main():
    parser = argparse.ArgumentParser(description='Validate HyperSync domain configuration')
    parser.add_argument('type', help='Domain type')
    parser.add_argument('dimension', type=int, help='Domain dimension')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--config', required=True, help='Configuration as JSON string')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    try:
        config = json.loads(args.config)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in --config", file=sys.stderr)
        sys.exit(1)

    result = api_validate_domain_config(
        domain_type=args.type,
        dimension=args.dimension,
        config=config,
        tier=args.tier
    )

    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nValidation Result: {'✓ VALID' if result['valid'] else '✗ INVALID'}")
        print(f"  Domain Type: {result['domain_type']}")
        print(f"  Dimension: {result['dimension']}")
        print(f"  Tier: {result['tier']}")

        if result['errors']:
            print(f"\n  Errors:")
            for error in result['errors']:
                print(f"    ✗ {error}")

        if result['warnings']:
            print(f"\n  Warnings:")
            for warning in result['warnings']:
                print(f"    ⚠ {warning}")

        if result['valid']:
            print(f"\n✓ Configuration is valid")
        else:
            print(f"\n✗ Configuration has errors")
        print()

if __name__ == '__main__':
    main()
