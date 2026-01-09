#!/usr/bin/env python3
"""
CLI command: hypersync consensus recommend

Recommends a consensus mechanism based on requirements.
"""

import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(
        description='Recommend a consensus mechanism'
    )
    parser.add_argument(
        'tier_id',
        help='Service tier identifier'
    )
    parser.add_argument(
        '--use-case',
        choices=['safety_critical', 'high_throughput', 'low_latency', 'byzantine_protection', 'simple'],
        help='Primary use case'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='Output format'
    )

    args = parser.parse_args()

    # Simple recommendation logic
    recommendations = {
        'CORE': {
            'safety_critical': 'simple_bft',
            'high_throughput': 'gossip_protocol',
            'low_latency': 'vector_clock',
            'simple': 'crdt'
        },
        'Basic': {
            'safety_critical': 'simple_bft',
            'high_throughput': 'raft',
            'low_latency': 'quorum_based',
            'simple': 'raft'
        },
        'PRO': {
            'safety_critical': 'paxos',
            'high_throughput': 'raft',
            'low_latency': 'quorum_based',
            'byzantine_protection': 'proof_of_stake',
            'simple': 'raft'
        },
        'Advanced': {
            'safety_critical': 'byzantine_fault_tolerant',
            'high_throughput': 'hotstuff',
            'low_latency': 'tendermint',
            'byzantine_protection': 'byzantine_fault_tolerant',
            'simple': 'raft'
        }
    }

    use_case = args.use_case or 'simple'
    recommended = recommendations.get(args.tier_id, {}).get(use_case, 'raft')

    if args.format == 'json':
        print(json.dumps({
            "tier_id": args.tier_id,
            "use_case": use_case,
            "recommended": recommended
        }, indent=2))
    else:
        print(f"\nRecommended Consensus Mechanism:")
        print(f"  Tier: {args.tier_id}")
        print(f"  Use Case: {use_case}")
        print(f"  Recommendation: {recommended}")
        print(f"\nTo select this mechanism, run:")
        print(f"  hypersync consensus select {recommended} {args.tier_id}")

if __name__ == '__main__':
    main()
