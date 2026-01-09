#!/usr/bin/env python3
"""Security CLI: Update Policy"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.security.update_policy import api_update_security_policy

def main():
    parser = argparse.ArgumentParser(description='Update security policy')
    parser.add_argument('policy_id', help='Policy ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--name', help='New name')
    parser.add_argument('--description', help='New description')
    parser.add_argument('--status', help='New status')
    parser.add_argument('--level', help='New level')
    parser.add_argument('--config', help='Config as JSON')
    parser.add_argument('--json', action='store_true', help='JSON output')
    args = parser.parse_args()

    config = json.loads(args.config) if args.config else None
    result = api_update_security_policy(args.policy_id, args.tier, args.name,
                                        args.description, config, args.status, args.level)
    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ {result['message']}")
        print()

if __name__ == '__main__':
    main()
