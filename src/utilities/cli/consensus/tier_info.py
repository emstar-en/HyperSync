#!/usr/bin/env python3
"""
CLI command: hypersync tier info

Shows tier capabilities and limits.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'api' / 'consensus'))
from tier_capabilities import api_get_tier_capabilities

def main():
    parser = argparse.ArgumentParser(
        description='Show tier capabilities and limits'
    )
    parser.add_argument(
        'tier_id',
        help='Service tier identifier'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format'
    )

    args = parser.parse_args()

    result = api_get_tier_capabilities(args.tier_id)

    if result['status'] == 'error':
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.format == 'json':
        print(json.dumps(result, indent=2))
    else:
        cap = result['capabilities']
        print(f"\nTier: {cap['tier_id']}")
        print(f"Total Mechanisms: {cap['mechanisms_count']}")
        print(f"\nResource Limits:")
        limits = cap['resource_limits']
        print(f"  Max Nodes: {limits['max_nodes'] or 'Unlimited'}")
        print(f"  Max Dimensions: {limits['max_dimensions']}")
        print(f"  Max Memory: {limits['max_memory_mb']}MB")
        print(f"\nFeatures:")
        for feature, enabled in cap['features'].items():
            status = "✓" if enabled else "✗"
            print(f"  {status} {feature}")

if __name__ == '__main__':
    main()
