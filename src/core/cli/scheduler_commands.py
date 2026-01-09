"""Scheduler CLI commands"""
import click
import json
from hypersync.scheduler.curvature_manager import CurvatureManager, AutoscalePolicy

@click.group()
def scheduler():
    """Scheduler commands"""
    pass

@scheduler.command()
def curvature_status():
    """Show curvature field status"""
    manager = CurvatureManager()
    status = manager.get_status()
    click.echo(json.dumps(status, indent=2))

@scheduler.command()
@click.option('--tier', type=int, required=True)
@click.option('--threshold', type=float, required=True)
def autoscale_policy(tier, threshold):
    """Set autoscale policy"""
    manager = CurvatureManager()
    policy = AutoscalePolicy(tier=tier, scale_up_threshold=threshold)
    manager.set_autoscale_policy(tier, policy)
    click.echo(f"Set autoscale policy for tier {tier}")

@scheduler.command()
@click.argument('node_id')
def node_metrics(node_id):
    """Show metrics for a node"""
    manager = CurvatureManager()
    if node_id in manager.fields:
        field = manager.fields[node_id]
        click.echo(f"Node: {node_id}")
        click.echo(f"  Effective curvature: {field.effective_curvature:.3f}")
        click.echo(f"  Load curvature: {field.load_curvature:.3f}")
        click.echo(f"  Traffic curvature: {field.traffic_curvature:.3f}")
    else:
        click.echo(f"Node {node_id} not found")
