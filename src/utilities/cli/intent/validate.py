#!/usr/bin/env python3
"""Intent Alignment CLI"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.intent.validate import api_validate_intent

def main():
    parser = argparse.ArgumentParser(description='Validate intent alignment')
    parser.add_argument('domain_id', help='Domain ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--spec', required=True, help='Intent spec as JSON')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    spec = json.loads(args.spec)
    result = api_validate_intent(args.domain_id, spec, args.tier)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "✓ ALIGNED" if result['aligned'] else "✗ DRIFT DETECTED"
        print(f"\n{status}")
        print(f"  Alignment Score: {result['alignment_score']}")

if __name__ == '__main__':
    main()
