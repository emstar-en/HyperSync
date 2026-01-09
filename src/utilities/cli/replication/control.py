#!/usr/bin/env python3
"""Replication Control CLI"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.replication.configure_replication import api_configure_replication

def main():
    parser = argparse.ArgumentParser(description='Replication control')
    parser.add_argument('strategy', help='Replication strategy')
    parser.add_argument('--sources', nargs='+', required=True, help='Source nodes')
    parser.add_argument('--targets', nargs='+', required=True, help='Target nodes')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--mode', default='async', help='Sync mode')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    result = api_configure_replication(args.strategy, args.sources, args.targets, args.tier, args.mode)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ Configured {result['strategy']} replication ({result['sync_mode']} mode)")

if __name__ == '__main__':
    main()
