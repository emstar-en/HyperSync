#!/usr/bin/env python3
"""
Domain Management CLI: Get Domain Info

Usage:
    python3 info.py <domain_id> <tier> [--metrics] [--config]
"""

import sys
import json
import argparse

sys.path.insert(0, '../../')
from api.domains.get_domain_info import api_get_domain_info

def main():
    parser = argparse.ArgumentParser(description='Get HyperSync domain information')
    parser.add_argument('domain_id', help='Domain ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--metrics', action='store_true', help='Include metrics')
    parser.add_argument('--config', action='store_true', help='Include configuration')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    result = api_get_domain_info(
        domain_id=args.domain_id,
        tier=args.tier,
        include_metrics=args.metrics,
        include_config=args.config
    )

    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        domain = result['domain']
        print(f"\nDomain Information:")
        print(f"  ID: {domain['id']}")
        print(f"  Name: {domain['name']}")
        print(f"  Type: {domain['type']}")
        print(f"  Dimension: {domain['dimension']}")
        print(f"  Status: {domain['status']}")
        print(f"  Created: {domain['created']}")
        print(f"  Description: {domain.get('description', 'N/A')}")

        if 'properties' in domain:
            print(f"\n  Properties:")
            for key, value in domain['properties'].items():
                print(f"    {key}: {value}")

        if 'config' in domain:
            print(f"\n  Configuration:")
            for key, value in domain['config'].items():
                print(f"    {key}: {value}")

        if 'metrics' in domain:
            print(f"\n  Metrics:")
            for key, value in domain['metrics'].items():
                print(f"    {key}: {value}")
        print()

if __name__ == '__main__':
    main()
