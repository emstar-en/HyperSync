#!/usr/bin/env python3
"""
Domain Management CLI: List Domains

Usage:
    python3 list.py <tier> [--type TYPE] [--status STATUS] [--metadata]
"""

import sys
import json
import argparse

# Import API
sys.path.insert(0, '../../')
from api.domains.list_domains import api_list_domains

def format_table(domains):
    """Format domains as a table."""
    if not domains:
        return "No domains found."

    # Header
    print(f"{'ID':<15} {'Name':<25} {'Type':<12} {'Dim':<5} {'Status':<10}")
    print("-" * 70)

    # Rows
    for domain in domains:
        print(f"{domain['id']:<15} {domain['name']:<25} {domain['type']:<12} {domain['dimension']:<5} {domain['status']:<10}")

def main():
    parser = argparse.ArgumentParser(description='List HyperSync domains')
    parser.add_argument('tier', help='Service tier (CORE, Basic, PRO, Advanced, QM Venture, QM Campaign, QM Imperium)')
    parser.add_argument('--type', help='Filter by domain type')
    parser.add_argument('--status', help='Filter by status')
    parser.add_argument('--metadata', action='store_true', help='Include metadata')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    result = api_list_domains(
        tier=args.tier,
        filter_type=args.type,
        filter_status=args.status,
        include_metadata=args.metadata
    )

    if not result['success']:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nDomains for tier: {result['tier']}")
        print(f"Total: {result['count']}\n")
        format_table(result['domains'])
        print()

if __name__ == '__main__':
    main()
