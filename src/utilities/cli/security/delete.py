#!/usr/bin/env python3
"""Security CLI: Delete Policy"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.security.delete_policy import api_delete_security_policy

def main():
    parser = argparse.ArgumentParser(description='Delete security policy')
    parser.add_argument('policy_id', help='Policy ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--force', action='store_true', help='Force deletion')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')
    parser.add_argument('--json', action='store_true', help='JSON output')
    args = parser.parse_args()

    if not args.yes:
        response = input(f"Delete policy '{args.policy_id}'? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)

    result = api_delete_security_policy(args.policy_id, args.tier, args.force)
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
