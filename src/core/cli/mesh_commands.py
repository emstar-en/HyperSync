"""Mesh CLI commands"""
import click
import json
from hypersync.mesh.geodesic_coordinator import GeodesicMeshCoordinator

@click.group()
def mesh():
    """Service mesh commands"""
    pass

@mesh.command()
@click.option('--capability', help='Filter by capability')
def discover(capability):
    """Discover services"""
    coordinator = GeodesicMeshCoordinator()
    services = coordinator.discover_services(capability=capability)

    for s in services:
        click.echo(f"{s.service_name} (tier {s.tier}): {', '.join(s.capabilities)}")

@mesh.command()
@click.argument('source')
@click.argument('destination')
def route(source, destination):
    """Compute route between services"""
    coordinator = GeodesicMeshCoordinator()
    route = coordinator.compute_route(source, destination)

    if route:
        click.echo(f"Route: {route.length:.2f} units, ~{route.estimated_latency:.1f}ms")
    else:
        click.echo("Route not found")

@mesh.command()
@click.argument('source')
@click.argument('destination')
@click.option('--paths', default=3, help='Number of paths')
def load_balance(source, destination, paths):
    """Generate load-balanced routes"""
    coordinator = GeodesicMeshCoordinator()
    routes = coordinator.load_balance_route(source, destination, paths)

    for i, r in enumerate(routes, 1):
        click.echo(f"Path {i}: {r.length:.2f} units, ~{r.estimated_latency:.1f}ms")

@mesh.command()
def topology():
    """Show mesh topology"""
    coordinator = GeodesicMeshCoordinator()
    topo = coordinator.get_mesh_topology()
    click.echo(json.dumps(topo, indent=2))
