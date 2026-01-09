#!/usr/bin/env python3
"""Monitoring CLI"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.monitoring.get_metrics import api_get_metrics

def main():
    parser = argparse.ArgumentParser(description='Get system metrics')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--types', nargs='+', help='Metric types')
    parser.add_argument('--range', default='1h', help='Time range')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    result = api_get_metrics(args.tier, args.types, args.range)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nMetrics ({result['time_range']}):")
        for name, data in result['metrics'].items():
            print(f"  {name}: {data}")

if __name__ == '__main__':
    main()
