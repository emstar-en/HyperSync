#!/usr/bin/env python3
"""Kappa Channels CLI"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.kappa.list_channels import api_list_kappa_channels

def main():
    parser = argparse.ArgumentParser(description='Kappa channel operations')
    parser.add_argument('operation', choices=['list', 'select'])
    parser.add_argument('domain_id', help='Domain ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--level', type=int, help='Kappa level')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    if args.operation == 'list':
        result = api_list_kappa_channels(args.domain_id, args.tier, args.level)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\nKappa Channels ({result['count']}):")
            for ch in result['channels']:
                print(f"  Level {ch['level']}: {ch['name']} - {ch['description']}")

if __name__ == '__main__':
    main()
