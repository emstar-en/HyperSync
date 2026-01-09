#!/usr/bin/env python3
"""Security CLI: Get Policy Info"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.security.get_policy import api_get_security_policy

def main():
    parser = argparse.ArgumentParser(description='Get security policy info')
    parser.add_argument('policy_id', help='Policy ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--config', action='store_true', help='Include config')
    parser.add_argument('--json', action='store_true', help='JSON output')
    args = parser.parse_args()

    result = api_get_security_policy(args.policy_id, args.tier, args.config)
    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        p = result['policy']
        print(f"\nPolicy: {p['name']}")
        print(f"  ID: {p['id']}")
        print(f"  Category: {p['category']}")
        print(f"  Level: {p['level']}")
        print(f"  Status: {p['status']}")
        print(f"  Description: {p['description']}")
        if 'config' in p:
            print(f"  Config: {json.dumps(p['config'], indent=4)}")
        print()

if __name__ == '__main__':
    main()
