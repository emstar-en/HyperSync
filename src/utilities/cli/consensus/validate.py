#!/usr/bin/env python3
"""
CLI command: hypersync consensus validate <config>

Validates a consensus mechanism configuration.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'api' / 'consensus'))
from validate_mechanism_config import api_validate_mechanism_config

def main():
    parser = argparse.ArgumentParser(
        description='Validate consensus mechanism configuration'
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
        'config',
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

    result = api_validate_mechanism_config(args.mechanism_id, args.tier_id, args.config)

    if args.format == 'json':
        print(json.dumps(result, indent=2))
    else:
        if result['valid']:
            print(f"\n✓ Configuration is valid")
        else:
            print(f"\n✗ Configuration is invalid")
            if result['errors']:
                print(f"\nErrors:")
                for error in result['errors']:
                    print(f"  • {error}")

        if result.get('warnings'):
            print(f"\nWarnings:")
            for warning in result['warnings']:
                print(f"  ⚠ {warning}")

if __name__ == '__main__':
    main()
