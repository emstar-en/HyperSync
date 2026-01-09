#!/usr/bin/env python3
"""
CLI command: hypersync consensus select <mechanism>

Selects a consensus mechanism for the current tier.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'api' / 'consensus'))
from select_mechanism import api_select_mechanism

def main():
    parser = argparse.ArgumentParser(
        description='Select a consensus mechanism'
    )
    parser.add_argument(
        'mechanism_id',
        help='Mechanism identifier'
    )
    parser.add_argument(
        'tier_id',
        help='Service tier identifier'
    )
    parser.add_argument(
        '--config',
        type=json.loads,
        help='Configuration JSON string'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format'
    )

    args = parser.parse_args()

    result = api_select_mechanism(args.mechanism_id, args.tier_id, args.config)

    if result['status'] == 'error':
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.format == 'json':
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ Successfully selected {result['mechanism_name']}")
        print(f"  Tier: {result['tier_id']}")
        print(f"  Mechanism ID: {result['mechanism_id']}")
        print(f"\n{result['message']}")

if __name__ == '__main__':
    main()
