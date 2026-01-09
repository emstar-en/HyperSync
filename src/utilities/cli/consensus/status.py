#!/usr/bin/env python3
"""
CLI command: hypersync consensus status

Shows the currently active consensus mechanism.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'api' / 'consensus'))
from get_current_mechanism import api_get_current_mechanism

def main():
    parser = argparse.ArgumentParser(
        description='Show current consensus mechanism status'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format'
    )

    args = parser.parse_args()

    result = api_get_current_mechanism()

    if args.format == 'json':
        print(json.dumps(result, indent=2))
    else:
        if not result.get('active', False):
            print("\nNo consensus mechanism currently selected")
        else:
            print(f"\nCurrent Consensus Mechanism:")
            print(f"  Name: {result['mechanism_name']}")
            print(f"  ID: {result['mechanism_id']}")
            print(f"  Tier: {result['tier_id']}")
            print(f"  Selected: {result['selected_at']}")

if __name__ == '__main__':
    main()
