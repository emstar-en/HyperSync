"""
Transport CLI Commands
"""

import argparse
import json
import requests
from typing import Dict, Any


class TransportCLI:
    """CLI handler for transport commands"""

    def __init__(self, subparsers):
        self.api_base = "https://api.hypersync.local/v1"
        self._setup_parser(subparsers)

    def _setup_parser(self, subparsers):
        """Setup transport command parser"""
        transport_parser = subparsers.add_parser('transport', help='Geodesic transport operations')
        transport_subparsers = transport_parser.add_subparsers(dest='transport_command')

        # transport parallel
        parallel_parser = transport_subparsers.add_parser('parallel', help='Parallel transport')
        parallel_parser.add_argument('--vector', type=str, required=True)
        parallel_parser.add_argument('--from', dest='start_point', type=str, required=True)
        parallel_parser.add_argument('--to', dest='end_point', type=str, required=True)
        parallel_parser.add_argument('--kappa', type=float, required=True)
        parallel_parser.add_argument('--connection', choices=['levi_civita', 'affine'], default='levi_civita')
        parallel_parser.add_argument('--output', type=str)

        # transport exp
        exp_parser = transport_subparsers.add_parser('exp', help='Exponential map')
        exp_parser.add_argument('--base', type=str, required=True)
        exp_parser.add_argument('--vector', type=str, required=True)
        exp_parser.add_argument('--kappa', type=float, required=True)
        exp_parser.add_argument('--time', type=float, default=1.0)
        exp_parser.add_argument('--method', choices=['runge_kutta', 'euler', 'adaptive'], default='runge_kutta')

        # transport log
        log_parser = transport_subparsers.add_parser('log', help='Logarithm map')
        log_parser.add_argument('--base', type=str, required=True)
        log_parser.add_argument('--target', type=str, required=True)
        log_parser.add_argument('--kappa', type=float, required=True)

        # transport holonomy
        holonomy_parser = transport_subparsers.add_parser('holonomy', help='Validate holonomy')
        holonomy_parser.add_argument('--loop', type=str, required=True)
        holonomy_parser.add_argument('--vector', type=str, required=True)
        holonomy_parser.add_argument('--kappa', type=float, required=True)
        holonomy_parser.add_argument('--tolerance', type=float, default=1e-6)

        # transport geodesic
        geodesic_parser = transport_subparsers.add_parser('geodesic', help='Compute geodesic')
        geodesic_parser.add_argument('--from', dest='start_point', type=str, required=True)
        geodesic_parser.add_argument('--to', dest='end_point', type=str, required=True)
        geodesic_parser.add_argument('--kappa', type=float, required=True)
        geodesic_parser.add_argument('--points', type=int, default=100)
        geodesic_parser.add_argument('--output', type=str)

    def execute(self, args):
        """Execute transport command"""
        if args.transport_command == 'parallel':
            return self.parallel_transport(args)
        elif args.transport_command == 'exp':
            return self.exponential_map(args)
        elif args.transport_command == 'log':
            return self.logarithm_map(args)
        elif args.transport_command == 'holonomy':
            return self.validate_holonomy(args)
        elif args.transport_command == 'geodesic':
            return self.compute_geodesic(args)
        return 1

    def _load_json(self, data_str):
        """Load JSON from string or file"""
        try:
            return json.loads(data_str)
        except:
            with open(data_str) as f:
                return json.load(f)

    def parallel_transport(self, args):
        """Parallel transport vector"""
        payload = {
            'vector': self._load_json(args.vector),
            'start_point': self._load_json(args.start_point),
            'end_point': self._load_json(args.end_point),
            'kappa': args.kappa,
            'connection_type': args.connection
        }

        response = requests.post(f"{self.api_base}/transport/parallel", json=payload)
        result = response.json()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))
        return 0

    def exponential_map(self, args):
        """Exponential map"""
        payload = {
            'base_point': self._load_json(args.base),
            'tangent_vector': self._load_json(args.vector),
            'kappa': args.kappa,
            'time_parameter': args.time,
            'numerical_method': args.method
        }

        response = requests.post(f"{self.api_base}/transport/exponential", json=payload)
        print(json.dumps(response.json(), indent=2))
        return 0

    def logarithm_map(self, args):
        """Logarithm map"""
        payload = {
            'base_point': self._load_json(args.base),
            'target_point': self._load_json(args.target),
            'kappa': args.kappa
        }

        response = requests.post(f"{self.api_base}/transport/logarithm", json=payload)
        print(json.dumps(response.json(), indent=2))
        return 0

    def validate_holonomy(self, args):
        """Validate holonomy"""
        payload = {
            'closed_loop': self._load_json(args.loop),
            'initial_vector': self._load_json(args.vector),
            'kappa': args.kappa,
            'tolerance': args.tolerance
        }

        response = requests.post(f"{self.api_base}/transport/holonomy/validate", json=payload)
        print(json.dumps(response.json(), indent=2))
        return 0

    def compute_geodesic(self, args):
        """Compute geodesic"""
        payload = {
            'start_point': self._load_json(args.start_point),
            'end_point': self._load_json(args.end_point),
            'kappa': args.kappa,
            'num_points': args.points
        }

        response = requests.post(f"{self.api_base}/transport/geodesic/compute", json=payload)
        result = response.json()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))
        return 0
