#!/usr/bin/env python3
"""Deployment CLI"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.deployment.deploy import api_deploy

def main():
    parser = argparse.ArgumentParser(description='Deploy components')
    parser.add_argument('component', help='Component name')
    parser.add_argument('version', help='Version')
    parser.add_argument('targets', nargs='+', help='Target nodes')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--strategy', default='rolling', help='Deployment strategy')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    result = api_deploy(args.component, args.version, args.targets, args.tier, args.strategy)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ Deploying {result['component']} v{result['version']} ({result['strategy']} strategy)")

if __name__ == '__main__':
    main()
