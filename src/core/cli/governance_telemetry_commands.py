"""Governance and Telemetry CLI commands"""
import click
import json
from hypersync.governance.governance_manager import GovernanceManager, ChangeType
from hypersync.telemetry.exporters import TelemetryManager

@click.group()
def governance():
    """Governance commands"""
    pass

@governance.command()
def status():
    """Show governance status"""
    manager = GovernanceManager()
    status = manager.get_governance_status()
    click.echo(json.dumps(status, indent=2))

@governance.command()
@click.argument('request_id')
@click.option('--approver', required=True)
def approve(request_id, approver):
    """Approve change request"""
    manager = GovernanceManager()
    success = manager.approve_change_request(request_id, approver)
    if success:
        click.echo(f"Approved request {request_id}")
    else:
        click.echo(f"Failed to approve request {request_id}")

@click.group()
def telemetry():
    """Telemetry commands"""
    pass

@telemetry.command()
@click.option('--format', type=click.Choice(['prometheus', 'otlp']), default='prometheus')
def export(format):
    """Export telemetry metrics"""
    manager = TelemetryManager()

    if format == 'prometheus':
        output = manager.export_prometheus()
    else:
        output = manager.export_otlp()

    click.echo(output)

@telemetry.command()
def dashboard():
    """Open Grafana dashboard"""
    click.echo("Opening Grafana dashboard...")
    click.echo("URL: http://localhost:3000/d/hypersync")
