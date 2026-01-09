#!/usr/bin/env python3
"""Performance Tuning CLI"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.performance.configure import api_configure_performance

def main():
    parser = argparse.ArgumentParser(description='Configure performance')
    parser.add_argument('target', help='Target component')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--params', required=True, help='Parameters as JSON')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    params = json.loads(args.params)
    result = api_configure_performance(args.target, params, args.tier)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ Configured performance for {result['target']}")

if __name__ == '__main__':
    main()
