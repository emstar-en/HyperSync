#!/usr/bin/env python3
"""Model Coordination CLI"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.model.list_models import api_list_models

def main():
    parser = argparse.ArgumentParser(description='Model coordination operations')
    parser.add_argument('operation', choices=['list', 'sync'])
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--status', help='Filter by status')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    if args.operation == 'list':
        result = api_list_models(args.tier, args.status)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\nModels ({result['count']}):")
            for m in result['models']:
                print(f"  {m['id']}: {m['name']} v{m['version']} - {m['status']}")

if __name__ == '__main__':
    main()
