"""Federation CLI"""
import click
from rich.console import Console
from .federation_manager import FederationManager

console = Console()

@click.group(name='federation')
def federation_cli():
    """Manage ICO network federation"""
    pass

@federation_cli.command(name='create')
@click.option('--name', required=True)
@click.option('--network', 'networks', multiple=True, required=True)
def create_federation(name, networks):
    """Create a federation"""
    manager = FederationManager()
    fed = manager.create_federation(name=name, networks=list(networks))
    console.print(f"[green]✓[/green] Created federation: {fed.federation_id}")

@federation_cli.command(name='bridge')
@click.option('--source', required=True)
@click.option('--target', required=True)
@click.option('--type', 'bridge_type', default='direct')
def create_bridge(source, target, bridge_type):
    """Create a bridge between LDs"""
    manager = FederationManager()
    bridge = manager.create_bridge(source_ld=source, target_ld=target, bridge_type=bridge_type)
    console.print(f"[green]✓[/green] Created bridge: {bridge.bridge_id}")

@federation_cli.command(name='route')
@click.option('--from', 'source', required=True)
@click.option('--to', 'target', required=True)
def find_route(source, target):
    """Find route between LDs"""
    manager = FederationManager()
    route = manager.route_between_lds(source, target)
    if route:
        console.print(f"Route: {' → '.join(route)}")
    else:
        console.print("[yellow]No route found[/yellow]")

def register_cli(cli_group):
    """Register federation commands"""
    cli_group.add_command(federation_cli)
