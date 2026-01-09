"""Deployment CLI commands"""
import click
from hypersync.deployment.placement_engine import PlacementEngine, CapabilityVector

@click.group()
def deploy():
    """Deployment commands"""
    pass

@deploy.command()
@click.argument('service_name')
@click.option('--compute', type=float, required=True)
@click.option('--memory', type=float, required=True)
@click.option('--storage', type=float, required=True)
@click.option('--latency-sensitivity', type=float, default=0.5)
@click.option('--security-level', type=int, default=2)
@click.option('--bandwidth', type=float, default=1000.0)
def service(service_name, compute, memory, storage, latency_sensitivity, security_level, bandwidth):
    """Deploy a service"""
    engine = PlacementEngine()
    capability = CapabilityVector(compute, memory, storage, latency_sensitivity, security_level, bandwidth)
    node = engine.deploy_service(service_name, capability)
    click.echo(f"Deployed {service_name} to tier {node.position.tier} (radius {node.position.radius:.2f})")

@deploy.command()
@click.argument('tier', type=int)
def tier_capacity(tier):
    """Check tier capacity"""
    engine = PlacementEngine()
    capacity = engine.get_tier_capacity(tier)
    click.echo(f"Tier {tier} capacity:")
    click.echo(f"  Available: {capacity['available']}")
    click.echo(f"  Used: {capacity['used']}")
