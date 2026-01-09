#!/usr/bin/env python3
"""Security CLI: Create Policy"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.security.create_policy import api_create_security_policy

def main():
    parser = argparse.ArgumentParser(description='Create security policy')
    parser.add_argument('name', help='Policy name')
    parser.add_argument('category', help='Category')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--description', help='Description')
    parser.add_argument('--level', help='Security level')
    parser.add_argument('--config', help='Config as JSON')
    parser.add_argument('--json', action='store_true', help='JSON output')
    args = parser.parse_args()

    config = json.loads(args.config) if args.config else None
    result = api_create_security_policy(args.name, args.category, args.tier, 
                                        args.description, args.level, config)
    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ {result['message']}")
        print(f"  Policy ID: {result['policy_id']}")
        print()

if __name__ == '__main__':
    main()
