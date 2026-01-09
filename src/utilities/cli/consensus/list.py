#!/usr/bin/env python3
"""
CLI command: hypersync consensus list

Lists available consensus mechanisms for the current tier.
"""

import argparse
import json
import sys
from pathlib import Path

# Import API
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'api' / 'consensus'))
from list_mechanisms import api_list_mechanisms

def main():
    parser = argparse.ArgumentParser(
        description='List available consensus mechanisms'
    )
    parser.add_argument(
        'tier_id',
        help='Service tier identifier (e.g., CORE, PRO, Advanced)'
    )
    parser.add_argument(
        '--no-inherit',
        action='store_true',
        help='Do not include mechanisms from lower tiers'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format'
    )

    args = parser.parse_args()

    # Call API
    result = api_list_mechanisms(args.tier_id, include_inherited=not args.no_inherit)

    if result['status'] == 'error':
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    # Format output
    if args.format == 'json':
        print(json.dumps(result, indent=2))
    else:
        print(f"\nAvailable Consensus Mechanisms for {args.tier_id} tier:")
        print(f"Total: {result['total_mechanisms']}\n")
        print(f"{'ID':<25} {'Name':<30} {'Weight':<15} {'Use'}")
        print("-" * 100)
        for mech in result['mechanisms']:
            print(f"{mech['id']:<25} {mech['name']:<30} {mech['weight']:<15} {mech.get('primary_use', 'N/A')}")

if __name__ == '__main__':
    main()
