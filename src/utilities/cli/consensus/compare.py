#!/usr/bin/env python3
"""
CLI command: hypersync consensus compare <mech1> <mech2>

Compares two consensus mechanisms.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'api' / 'consensus'))
from get_mechanism_info import MechanismInfoProvider

def main():
    parser = argparse.ArgumentParser(
        description='Compare two consensus mechanisms'
    )
    parser.add_argument(
        'mechanism_1',
        help='First mechanism identifier'
    )
    parser.add_argument(
        'mechanism_2',
        help='Second mechanism identifier'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format'
    )

    args = parser.parse_args()

    provider = MechanismInfoProvider()
    result = provider.compare_mechanisms(args.mechanism_1, args.mechanism_2)

    if args.format == 'json':
        print(json.dumps(result, indent=2))
    else:
        print(f"\nComparison: {result['mechanism_1']['name']} vs {result['mechanism_2']['name']}")
        print(f"\n{'Attribute':<30} {'Mechanism 1':<30} {'Mechanism 2':<30}")
        print("-" * 90)
        print(f"{'Weight':<30} {result['mechanism_1']['weight']:<30} {result['mechanism_2']['weight']:<30}")
        print(f"{'CPU Cores (min)':<30} {result['mechanism_1']['resources']['cpu_cores_min']:<30} {result['mechanism_2']['resources']['cpu_cores_min']:<30}")
        print(f"{'Memory (min)':<30} {result['mechanism_1']['resources']['memory_mb_min']}MB{'':<26} {result['mechanism_2']['resources']['memory_mb_min']}MB")
        print(f"\nComparison Summary:")
        print(f"  Lighter: {result['comparison']['lighter']}")
        print(f"  More CPU Intensive: {result['comparison']['more_cpu_intensive']}")
        print(f"  More Memory Intensive: {result['comparison']['more_memory_intensive']}")

if __name__ == '__main__':
    main()
