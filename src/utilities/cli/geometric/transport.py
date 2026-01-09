#!/usr/bin/env python3
"""Geometric Transport CLI"""
import sys, json, argparse
sys.path.insert(0, '../../')

def main():
    parser = argparse.ArgumentParser(description='Geometric transport operations')
    parser.add_argument('operation', choices=['parallel', 'geodesic', 'exp_map'])
    parser.add_argument('domain_id', help='Domain ID')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    print(f"Geometric operation: {args.operation} on {args.domain_id}")

if __name__ == '__main__':
    main()
