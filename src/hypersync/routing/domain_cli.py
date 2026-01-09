"""
Domain CLI - Command-line interface for domain operations

Provides CLI commands for:
- Domain discovery and inspection
- Domain instantiation and management
- Domain transitions and routing
- Domain validation and testing
"""

import sys
import json
import argparse
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class DomainCLI:
    """Command-line interface for domain operations"""

    def __init__(self):
        from registry import get_registry
        from domain_factory import get_factory
        from domain_api import create_api

        self.registry = get_registry()
        self.factory = get_factory()
        self.api = create_api(self.registry, self.factory)

    # ========================================================================
    # LIST COMMANDS
    # ========================================================================

    def cmd_list(self, args):
        """List all domains or filter by criteria"""
        filters = {}

        if args.type:
            filters['domain_type'] = args.type
        if args.curvature:
            filters['curvature_class'] = args.curvature
        if args.capability:
            filters['capability'] = args.capability
        if args.trait:
            filters['feature_trait'] = args.trait

        result = self.api.list_domains(filters if filters else None)

        if result['status'] == 'success':
            print(f"\nFound {result['count']} domains:\n")
            for domain in result['domains']:
                self._print_domain_summary(domain)
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")
            return 1

        return 0

    def cmd_types(self, args):
        """List all available domain types"""
        result = self.api.list_domain_types()

        if result['status'] == 'success':
            print(f"\nAvailable domain types ({result['count']}):\n")
            for dtype in result['types']:
                print(f"  - {dtype}")
        else:
            print(f"Error: {result.get('message')}")
            return 1

        return 0

    def cmd_curvatures(self, args):
        """List all curvature classes"""
        result = self.api.list_curvature_classes()

        if result['status'] == 'success':
            print(f"\nCurvature classes ({result['count']}):\n")
            for cclass in result['curvature_classes']:
                print(f"  - {cclass}")
        else:
            print(f"Error: {result.get('message')}")
            return 1

        return 0

    # ========================================================================
    # INSPECT COMMANDS
    # ========================================================================

    def cmd_inspect(self, args):
        """Inspect a specific domain"""
        result = self.api.get_domain(args.domain_id)

        if result['status'] == 'success':
            self._print_domain_details(result['domain'])
        else:
            print(f"Error: {result.get('message')}")
            return 1

        return 0

    def cmd_capabilities(self, args):
        """Show capabilities for a domain"""
        result = self.api.get_domain_capabilities(args.domain_id)

        if result['status'] == 'success':
            print(f"\nCapabilities for {args.domain_id}:\n")
            for cap, value in result['capabilities'].items():
                status = "✓" if value else "✗"
                print(f"  {status} {cap}: {value}")
        else:
            print(f"Error: {result.get('message')}")
            return 1

        return 0

    # ========================================================================
    # CREATE COMMANDS
    # ========================================================================

    def cmd_create(self, args):
        """Create a new domain instance"""
        # Parse parameters
        parameters = {}
        if args.params:
            try:
                parameters = json.loads(args.params)
            except json.JSONDecodeError:
                print("Error: Invalid JSON for parameters")
                return 1

        request = {
            'domain_type': args.type,
            'parameters': parameters,
            'instance_id': args.instance_id
        }

        result = self.api.create_domain_instance(request)

        if result['status'] == 'success':
            print(f"\n✓ Created domain instance:")
            print(f"  Instance ID: {result['instance_id']}")
            print(f"  Domain type: {result['domain_type']}")
            print(f"  Parameters: {json.dumps(result['parameters'], indent=2)}")
        else:
            print(f"Error: {result.get('message')}")
            return 1

        return 0

    # ========================================================================
    # TRANSITION COMMANDS
    # ========================================================================

    def cmd_compatible(self, args):
        """Show compatible domains for transitions"""
        result = self.api.get_compatible_domains(args.domain_id)

        if result['status'] == 'success':
            print(f"\nCompatible domains for {args.domain_id} ({result['count']}):\n")
            for domain in result['compatible_domains']:
                print(f"  - {domain['domain_id']} ({domain['domain_type']})")
                print(f"    Curvature: {domain['curvature_class']}, Dimension: {domain['dimension']}")
        else:
            print(f"Error: {result.get('message')}")
            return 1

        return 0

    def cmd_plan(self, args):
        """Plan a transition between domains"""
        request = {
            'source_domain': args.source,
            'target_domain': args.target,
            'transition_type': args.transition_type
        }

        result = self.api.plan_transition(request)

        if result['status'] == 'success':
            print(f"\nTransition Plan:\n")
            print(f"  Source: {result['source']['domain_id']} ({result['source']['domain_type']})")
            print(f"  Target: {result['target']['domain_id']} ({result['target']['domain_type']})")
            print(f"  Compatible: {'✓' if result['compatible'] else '✗'}")
            print(f"  Requires adapter: {'Yes' if result['requires_adapter'] else 'No'}")
            print(f"  Transition type: {result['transition_type']}")
        else:
            print(f"Error: {result.get('message')}")
            return 1

        return 0

    # ========================================================================
    # VALIDATE COMMANDS
    # ========================================================================

    def cmd_validate(self, args):
        """Validate a domain configuration"""
        result = self.api.validate_domain(args.domain_id)

        if result['status'] == 'success':
            status = "✓ Valid" if result['valid'] else "✗ Invalid"
            print(f"\n{status}: {args.domain_id}")
        else:
            print(f"Error: {result.get('message')}")
            return 1

        return 0

    # ========================================================================
    # QUERY COMMANDS
    # ========================================================================

    def cmd_query(self, args):
        """Query domains by various criteria"""
        if args.by_capability:
            result = self.api.query_by_capability(args.by_capability)
            if result['status'] == 'success':
                print(f"\nDomains with capability '{args.by_capability}' ({result['count']}):\n")
                for domain in result['domains']:
                    self._print_domain_summary(domain)
            else:
                print(f"Error: {result.get('message')}")
                return 1

        return 0

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _print_domain_summary(self, domain):
        """Print a one-line summary of a domain"""
        print(f"  {domain['domain_id']}")
        print(f"    Type: {domain['domain_type']}, Curvature: {domain['curvature_class']}, Dim: {domain['dimension']}")
        if domain['feature_traits']:
            print(f"    Traits: {', '.join(domain['feature_traits'][:3])}")
        print()

    def _print_domain_details(self, domain):
        """Print detailed information about a domain"""
        print(f"\n{'=' * 70}")
        print(f"Domain: {domain['domain_id']}")
        print(f"{'=' * 70}\n")

        print(f"Type: {domain['domain_type']}")
        print(f"Curvature Class: {domain['curvature_class']}")
        print(f"Dimension: {domain['dimension']}\n")

        print("Capabilities:")
        for cap, value in domain['capabilities'].items():
            status = "✓" if value else "✗"
            print(f"  {status} {cap}")

        if domain['parameters']:
            print(f"\nParameters:")
            for key, value in domain['parameters'].items():
                print(f"  {key}: {value}")

        if domain['feature_traits']:
            print(f"\nFeature Traits:")
            for trait in domain['feature_traits']:
                print(f"  - {trait}")

        if domain['policy_constraints']:
            print(f"\nPolicy Constraints:")
            for policy in domain['policy_constraints']:
                print(f"  - {policy}")

        if domain['metadata']:
            print(f"\nMetadata:")
            for key, value in domain['metadata'].items():
                print(f"  {key}: {value}")

        print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='HyperSync Domain Management CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all domains
  %(prog)s list

  # List only black holes
  %(prog)s list --trait black_hole

  # List domains with horizons
  %(prog)s list --capability supports_horizons

  # Inspect a specific domain
  %(prog)s inspect schwarzschild_default

  # Create a new Schwarzschild black hole
  %(prog)s create schwarzschild --params '{"mass": 2.0}' --id my_bh_1

  # Plan transition from FRW to AdS
  %(prog)s plan frw_default ads_default

  # Show compatible domains
  %(prog)s compatible frw_default
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # List command
    list_parser = subparsers.add_parser('list', help='List domains')
    list_parser.add_argument('--type', help='Filter by domain type')
    list_parser.add_argument('--curvature', help='Filter by curvature class')
    list_parser.add_argument('--capability', help='Filter by capability')
    list_parser.add_argument('--trait', help='Filter by feature trait')

    # Types command
    subparsers.add_parser('types', help='List all domain types')

    # Curvatures command
    subparsers.add_parser('curvatures', help='List all curvature classes')

    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect a domain')
    inspect_parser.add_argument('domain_id', help='Domain ID to inspect')

    # Capabilities command
    cap_parser = subparsers.add_parser('capabilities', help='Show domain capabilities')
    cap_parser.add_argument('domain_id', help='Domain ID')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create domain instance')
    create_parser.add_argument('type', help='Domain type')
    create_parser.add_argument('--params', help='Parameters as JSON')
    create_parser.add_argument('--id', dest='instance_id', help='Instance ID')

    # Compatible command
    compat_parser = subparsers.add_parser('compatible', help='Show compatible domains')
    compat_parser.add_argument('domain_id', help='Source domain ID')

    # Plan command
    plan_parser = subparsers.add_parser('plan', help='Plan a transition')
    plan_parser.add_argument('source', help='Source domain ID')
    plan_parser.add_argument('target', help='Target domain ID')
    plan_parser.add_argument('--type', dest='transition_type', default='smooth',
                           help='Transition type (default: smooth)')

    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate a domain')
    val_parser.add_argument('domain_id', help='Domain ID to validate')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query domains')
    query_parser.add_argument('--by-capability', help='Query by capability')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    cli = DomainCLI()

    # Dispatch to command handler
    command_map = {
        'list': cli.cmd_list,
        'types': cli.cmd_types,
        'curvatures': cli.cmd_curvatures,
        'inspect': cli.cmd_inspect,
        'capabilities': cli.cmd_capabilities,
        'create': cli.cmd_create,
        'compatible': cli.cmd_compatible,
        'plan': cli.cmd_plan,
        'validate': cli.cmd_validate,
        'query': cli.cmd_query
    }

    handler = command_map.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
