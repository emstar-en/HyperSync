#!/usr/bin/env python3
"""Network Topology CLI"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.network.configure_network import api_configure_network

def main():
    parser = argparse.ArgumentParser(description='Network topology operations')
    parser.add_argument('topology', help='Topology type')
    parser.add_argument('nodes', nargs='+', help='Node IDs')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    result = api_configure_network(args.topology, args.nodes, args.tier)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ Configured {result['topology_type']} topology with {result['node_count']} nodes")

if __name__ == '__main__':
    main()
