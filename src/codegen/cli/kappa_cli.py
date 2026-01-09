"""
Kappa Channel CLI Commands
"""

import argparse
import json
import requests
from typing import Dict, Any


class KappaCLI:
    """CLI handler for kappa channel commands"""

    def __init__(self, subparsers):
        self.api_base = "https://api.hypersync.local/v1"
        self._setup_parser(subparsers)

    def _setup_parser(self, subparsers):
        """Setup kappa command parser"""
        kappa_parser = subparsers.add_parser(
            'kappa',
            help='Kappa channel management'
        )
        kappa_subparsers = kappa_parser.add_subparsers(
            dest='kappa_command',
            help='Kappa commands'
        )

        # kappa list
        list_parser = kappa_subparsers.add_parser('list', help='List kappa channels')
        list_parser.add_argument('--format', choices=['table', 'json', 'yaml'], default='table')
        list_parser.add_argument('--active-only', action='store_true')

        # kappa create
        create_parser = kappa_subparsers.add_parser('create', help='Create kappa channel')
        create_parser.add_argument('--kappa', type=float, required=True)
        create_parser.add_argument('--density', choices=['dense', 'standard', 'rarified'], default='standard')
        create_parser.add_argument('--name', type=str)

        # kappa info
        info_parser = kappa_subparsers.add_parser('info', help='Get channel info')
        info_parser.add_argument('channel_id', type=str)
        info_parser.add_argument('--verbose', action='store_true')

        # kappa transition
        transition_parser = kappa_subparsers.add_parser('transition', help='Transition between kappas')
        transition_parser.add_argument('--from', dest='source_kappa', type=float, required=True)
        transition_parser.add_argument('--to', dest='target_kappa', type=float, required=True)
        transition_parser.add_argument('--data', type=str, required=True)
        transition_parser.add_argument('--method', choices=['parallel_transport', 'exponential_map', 'direct'], default='parallel_transport')
        transition_parser.add_argument('--output', type=str)

        # kappa validate
        validate_parser = kappa_subparsers.add_parser('validate', help='Validate curvature')
        validate_parser.add_argument('--kappa', type=float, required=True)
        validate_parser.add_argument('--type', choices=['sectional', 'ricci', 'scalar', 'holonomy'], default='sectional')
        validate_parser.add_argument('--tolerance', type=float, default=1e-6)

    def execute(self, args):
        """Execute kappa command"""
        if args.kappa_command == 'list':
            return self.list_channels(args)
        elif args.kappa_command == 'create':
            return self.create_channel(args)
        elif args.kappa_command == 'info':
            return self.get_channel_info(args)
        elif args.kappa_command == 'transition':
            return self.transition_kappa(args)
        elif args.kappa_command == 'validate':
            return self.validate_curvature(args)
        else:
            print("Unknown kappa command")
            return 1

    def list_channels(self, args):
        """List kappa channels"""
        response = requests.get(f"{self.api_base}/kappa/channels")
        channels = response.json()

        if args.active_only:
            channels = [c for c in channels if c.get('active', True)]

        if args.format == 'json':
            print(json.dumps(channels, indent=2))
        elif args.format == 'table':
            print(f"{'Channel ID':<30} {'Kappa':<10} {'Density':<15} {'Active'}")
            print("-" * 70)
            for ch in channels:
                print(f"{ch['channel_id']:<30} {ch['kappa']:<10.2f} {ch['semantic_density']:<15} {ch['active']}")

        return 0

    def create_channel(self, args):
        """Create kappa channel"""
        data = {
            'kappa': args.kappa,
            'semantic_density': args.density
        }
        if args.name:
            data['name'] = args.name

        response = requests.post(f"{self.api_base}/kappa/channels", json=data)
        result = response.json()

        print(f"Created channel: {result['channel_id']}")
        return 0

    def get_channel_info(self, args):
        """Get channel info"""
        response = requests.get(f"{self.api_base}/kappa/channels/{args.channel_id}")
        info = response.json()

        print(json.dumps(info, indent=2))
        return 0

    def transition_kappa(self, args):
        """Transition between kappa values"""
        # Load data
        try:
            data = json.loads(args.data)
        except:
            with open(args.data) as f:
                data = json.load(f)

        payload = {
            'source_kappa': args.source_kappa,
            'target_kappa': args.target_kappa,
            'data': data,
            'method': args.method
        }

        response = requests.post(f"{self.api_base}/kappa/transition", json=payload)
        result = response.json()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))

        return 0

    def validate_curvature(self, args):
        """Validate curvature"""
        payload = {
            'kappa': args.kappa,
            'validation_type': args.type,
            'tolerance': args.tolerance
        }

        response = requests.post(f"{self.api_base}/kappa/validate", json=payload)
        result = response.json()

        print(json.dumps(result, indent=2))
        return 0
