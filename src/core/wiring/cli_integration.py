"""CLI Integration Layer

Wires all CLI commands to the integration hub.
"""

import click
from hypersync.wiring import get_hub

# Import CLI command groups
try:
    from hypersync.cli.deployment_commands import deployment
except ImportError:
    deployment = None

try:
    from hypersync.cli.mesh_commands import mesh
except ImportError:
    mesh = None

try:
    from hypersync.cli.scheduler_commands import scheduler
except ImportError:
    scheduler = None

try:
    from hypersync.cli.replication_commands import replication
except ImportError:
    replication = None

try:
    from hypersync.cli.edge_commands import edge
except ImportError:
    edge = None

try:
    from hypersync.cli.governance_telemetry_commands import governance, telemetry
except ImportError:
    governance = None
    telemetry = None


@click.group()
@click.pass_context
def hypersync(ctx):
    """HyperSync Orchestrator CLI"""
    ctx.ensure_object(dict)
    ctx.obj['hub'] = get_hub()


@hypersync.command()
@click.pass_context
def status(ctx):
    """Show system status"""
    hub = ctx.obj['hub']
    status = hub.get_status()

    click.echo("HyperSync Orchestrator Status")
    click.echo("=" * 60)

    # Orchestrator status
    orch = status.get('orchestrator', {})
    click.echo(f"\nPlacement: {orch.get('placement', {}).get('nodes', 0)} nodes")
    click.echo(f"Scheduler: {orch.get('scheduler', {}).get('nodes_tracked', 0)} tracked")
    click.echo(f"Mesh: {orch.get('mesh', {}).get('services', 0)} services")
    click.echo(f"Replication: {orch.get('replication', {}).get('replica_sets', 0)} sets")
    click.echo(f"Edge: {orch.get('edge', {}).get('edge_nodes', 0)} nodes")

    # Governance
    gov = orch.get('governance', {})
    click.echo(f"\nGovernance:")
    click.echo(f"  Pending requests: {gov.get('pending_requests', 0)}")
    click.echo(f"  Active freezes: {gov.get('active_freezes', 0)}")


# Register command groups
if deployment:
    hypersync.add_command(deployment, name='deploy')

if mesh:
    hypersync.add_command(mesh)

if scheduler:
    hypersync.add_command(scheduler)

if replication:
    hypersync.add_command(replication)

if edge:
    hypersync.add_command(edge)

if governance:
    hypersync.add_command(governance)

if telemetry:
    hypersync.add_command(telemetry)


if __name__ == '__main__':
    hypersync()
