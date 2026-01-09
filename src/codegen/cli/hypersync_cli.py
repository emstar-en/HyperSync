#!/usr/bin/env python3
"""
HyperSync CLI - Command Line Interface
Main entry point for all HyperSync CLI commands
"""

import sys
import argparse
import json
from typing import Dict, Any

from .kappa_cli import KappaCLI
from .transport_cli import TransportCLI
from .consensus_cli import ConsensusCLI


class HyperSyncCLI:
    """Main CLI handler for HyperSync"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog='hypersync',
            description='HyperSync - Geometric Semantic Synchronization',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        self.subparsers = self.parser.add_subparsers(
            dest='command_group',
            help='Command groups'
        )

        # Register command groups
        self.kappa_cli = KappaCLI(self.subparsers)
        self.transport_cli = TransportCLI(self.subparsers)
        self.consensus_cli = ConsensusCLI(self.subparsers)

    def run(self, args=None):
        """Run CLI with given arguments"""
        parsed_args = self.parser.parse_args(args)

        if not parsed_args.command_group:
            self.parser.print_help()
            return 1

        # Route to appropriate command group
        if parsed_args.command_group == 'kappa':
            return self.kappa_cli.execute(parsed_args)
        elif parsed_args.command_group == 'transport':
            return self.transport_cli.execute(parsed_args)
        elif parsed_args.command_group == 'consensus':
            return self.consensus_cli.execute(parsed_args)
        else:
            print(f"Unknown command group: {parsed_args.command_group}")
            return 1


def main():
    """Main entry point"""
    cli = HyperSyncCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
