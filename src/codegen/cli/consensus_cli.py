"""
Consensus CLI Commands
"""

import argparse
import json
import requests
from typing import Dict, Any


class ConsensusCLI:
    """CLI handler for consensus commands"""

    def __init__(self, subparsers):
        self.api_base = "https://api.hypersync.local/v1"
        self._setup_parser(subparsers)

    def _setup_parser(self, subparsers):
        """Setup consensus command parser"""
        consensus_parser = subparsers.add_parser('consensus', help='Geometric consensus operations')
        consensus_subparsers = consensus_parser.add_subparsers(dest='consensus_command')

        # consensus barycenter
        barycenter_parser = consensus_subparsers.add_parser('barycenter', help='Compute barycenter')
        barycenter_parser.add_argument('--points', type=str, required=True)
        barycenter_parser.add_argument('--kappa', type=float, required=True)
        barycenter_parser.add_argument('--weights', type=str)
        barycenter_parser.add_argument('--algorithm', choices=['gradient_descent', 'fixed_point', 'karcher_flow'], default='gradient_descent')
        barycenter_parser.add_argument('--tolerance', type=float, default=1e-6)
        barycenter_parser.add_argument('--max-iterations', type=int, default=100)
        barycenter_parser.add_argument('--output', type=str)

        # consensus byzantine
        byzantine_parser = consensus_subparsers.add_parser('byzantine', help='Byzantine consensus')
        byzantine_parser.add_argument('--proposals', type=str, required=True)
        byzantine_parser.add_argument('--kappa', type=float, required=True)
        byzantine_parser.add_argument('--max-byzantine', type=int)
        byzantine_parser.add_argument('--total-nodes', type=int, required=True)
        byzantine_parser.add_argument('--method', choices=['geometric_median', 'trimmed_barycenter'], default='geometric_median')
        byzantine_parser.add_argument('--outlier-detection', choices=['distance_based', 'density_based'], default='distance_based')
        byzantine_parser.add_argument('--output', type=str)

        # consensus sync
        sync_parser = consensus_subparsers.add_parser('sync', help='Synchronize states')
        sync_parser.add_argument('--states', type=str, required=True)
        sync_parser.add_argument('--target-kappa', type=float, required=True)
        sync_parser.add_argument('--method', choices=['consensus_pull', 'leader_push', 'peer_to_peer'], default='consensus_pull')
        sync_parser.add_argument('--timeout', type=int, default=30)
        sync_parser.add_argument('--output', type=str)

        # consensus validate
        validate_parser = consensus_subparsers.add_parser('validate', help='Validate consensus')
        validate_parser.add_argument('--result', type=str, required=True)
        validate_parser.add_argument('--proposals', type=str, required=True)
        validate_parser.add_argument('--kappa', type=float, required=True)

    def execute(self, args):
        """Execute consensus command"""
        if args.consensus_command == 'barycenter':
            return self.compute_barycenter(args)
        elif args.consensus_command == 'byzantine':
            return self.byzantine_consensus(args)
        elif args.consensus_command == 'sync':
            return self.synchronize_states(args)
        elif args.consensus_command == 'validate':
            return self.validate_consensus(args)
        return 1

    def _load_json(self, data_str):
        """Load JSON from string or file"""
        try:
            return json.loads(data_str)
        except:
            with open(data_str) as f:
                return json.load(f)

    def compute_barycenter(self, args):
        """Compute Riemannian barycenter"""
        payload = {
            'points': self._load_json(args.points),
            'kappa': args.kappa,
            'algorithm': args.algorithm,
            'convergence_tolerance': args.tolerance,
            'max_iterations': args.max_iterations
        }

        if args.weights:
            payload['weights'] = self._load_json(args.weights)

        response = requests.post(f"{self.api_base}/consensus/barycenter", json=payload)
        result = response.json()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))
        return 0

    def byzantine_consensus(self, args):
        """Byzantine fault-tolerant consensus"""
        max_byz = args.max_byzantine if args.max_byzantine else args.total_nodes // 3

        payload = {
            'proposals': self._load_json(args.proposals),
            'kappa': args.kappa,
            'fault_tolerance': {
                'max_byzantine_nodes': max_byz,
                'total_nodes': args.total_nodes
            },
            'consensus_method': args.method,
            'outlier_detection': {'method': args.outlier_detection}
        }

        response = requests.post(f"{self.api_base}/consensus/byzantine", json=payload)
        result = response.json()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))
            if result.get('byzantine_nodes'):
                print(f"\nWarning: Detected {len(result['byzantine_nodes'])} Byzantine nodes")
        return 0

    def synchronize_states(self, args):
        """Synchronize distributed states"""
        payload = {
            'node_states': self._load_json(args.states),
            'target_kappa': args.target_kappa,
            'sync_method': args.method,
            'convergence_criteria': {'timeout_seconds': args.timeout}
        }

        response = requests.post(f"{self.api_base}/consensus/synchronize", json=payload)
        result = response.json()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))
        return 0

    def validate_consensus(self, args):
        """Validate consensus result"""
        payload = {
            'consensus_result': self._load_json(args.result),
            'original_proposals': self._load_json(args.proposals),
            'kappa': args.kappa
        }

        response = requests.post(f"{self.api_base}/consensus/validate", json=payload)
        result = response.json()

        print(json.dumps(result, indent=2))
        if result.get('valid'):
            print("\n✓ Consensus is valid")
        else:
            print("\n✗ Consensus validation failed")
        return 0
