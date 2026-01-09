#!/usr/bin/env python3
"""Security CLI: List Policies"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.security.list_policies import api_list_security_policies

def main():
    parser = argparse.ArgumentParser(description='List security policies')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--category', help='Filter by category')
    parser.add_argument('--status', help='Filter by status')
    parser.add_argument('--json', action='store_true', help='JSON output')
    args = parser.parse_args()

    result = api_list_security_policies(args.tier, args.category, args.status)
    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nSecurity Policies ({result['count']})\n")
        print(f"{'ID':<12} {'Name':<30} {'Category':<18} {'Level':<10}")
        print("-" * 72)
        for p in result['policies']:
            print(f"{p['id']:<12} {p['name']:<30} {p['category']:<18} {p['level']:<10}")
        print()

if __name__ == '__main__':
    main()
