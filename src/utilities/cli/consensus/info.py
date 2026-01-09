#!/usr/bin/env python3
"""
CLI command: hypersync consensus info <mechanism>

Shows detailed information about a consensus mechanism.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'api' / 'consensus'))
from get_mechanism_info import api_get_mechanism_info

def main():
    parser = argparse.ArgumentParser(
        description='Get detailed information about a consensus mechanism'
    )
    parser.add_argument(
        'mechanism_id',
        help='Mechanism identifier'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format'
    )

    args = parser.parse_args()

    result = api_get_mechanism_info(args.mechanism_id)

    if result['status'] == 'error':
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.format == 'json':
        print(json.dumps(result, indent=2))
    else:
        info = result['info']
        print(f"\nConsensus Mechanism: {info['name']}")
        print(f"ID: {info['id']}")
        print(f"Category: {info['category']}")
        print(f"Weight: {info['weight']}")
        print(f"\nResource Requirements:")
        res = info['resources']
        print(f"  CPU Cores: {res['cpu_cores_min']} (min) / {res.get('cpu_cores_recommended', 'N/A')} (recommended)")
        print(f"  Memory: {res['memory_mb_min']}MB (min) / {res.get('memory_mb_recommended', 'N/A')}MB (recommended)")
        print(f"  GPU Required: {res['gpu_required']}")
        if 'available_in_tiers' in info:
            print(f"\nAvailable in Tiers:")
            for tier in info['available_in_tiers']:
                print(f"  • {tier['display_name']} (position {tier['tier_position']})")

if __name__ == '__main__':
    main()
