#!/usr/bin/env python3
"""Shadow Operations CLI"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.shadow.enable import api_enable_shadow_mode

def main():
    parser = argparse.ArgumentParser(description='Shadow mode operations')
    parser.add_argument('target', help='Target component')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--config', required=True, help='Config as JSON')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    config = json.loads(args.config)
    result = api_enable_shadow_mode(args.target, config, args.tier)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ Shadow mode enabled for {result['target']}")

if __name__ == '__main__':
    main()
