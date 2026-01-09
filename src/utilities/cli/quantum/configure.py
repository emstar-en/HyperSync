#!/usr/bin/env python3
"""Quantum Features CLI"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.quantum.configure import api_configure_quantum

def main():
    parser = argparse.ArgumentParser(description='Configure quantum features')
    parser.add_argument('domain_id', help='Domain ID')
    parser.add_argument('qm_tier', help='QM tier (Venture, Campaign, Imperium)')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--hsm', help='HSM config as JSON')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    hsm_config = json.loads(args.hsm) if args.hsm else None
    result = api_configure_quantum(args.domain_id, args.qm_tier, args.tier, hsm_config)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ Quantum features enabled for {result['domain_id']} (QM {result['qm_tier']})")

if __name__ == '__main__':
    main()
