"""
CLI commands for control manifest management.
"""

import click
import yaml
import json
from pathlib import Path
from tabulate import tabulate

from hypersync.control.manifest_manager import (
    ControlManifest,
    get_manifest_manager,
    ManifestPhase
)


@click.group(name='control')
def control_cli():
    """Manage control manifests and policies."""
    pass


@control_cli.group(name='manifest')
def manifest_cli():
    """Control manifest operations."""
    pass


@manifest_cli.command(name='create')
@click.argument('file', type=click.Path(exists=True))
@click.option('--validate-only', is_flag=True, help='Validate without creating')
def create_manifest(file: str, validate_only: bool):
    """Create a control manifest from file."""
    try:
        # Load manifest
        with open(file) as f:
            if file.endswith('.yaml') or file.endswith('.yml'):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        manager = get_manifest_manager()

        # Validate
        is_valid, error = manager.validate(data)
        if not is_valid:
            click.echo(f"❌ Validation failed: {error}", err=True)
            return

        if validate_only:
            click.echo("✓ Manifest is valid")
            return

        # Create
        manifest = ControlManifest.from_dict(data)
        success, error = manager.create(manifest)

        if success:
            click.echo(f"✓ Created manifest: {manifest.metadata.namespace}/{manifest.metadata.name}")
            click.echo(f"  Status: {manifest.status.phase.value}")
        else:
            click.echo(f"❌ Failed to create manifest: {error}", err=True)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@manifest_cli.command(name='get')
@click.argument('name')
@click.option('--namespace', '-n', default='default', help='Namespace')
@click.option('--format', type=click.Choice(['yaml', 'json', 'table']), default='yaml',
              help='Output format')
def get_manifest(name: str, namespace: str, format: str):
    """Get a control manifest."""
    manager = get_manifest_manager()
    manifest = manager.get(name, namespace)

    if not manifest:
        click.echo(f"❌ Manifest {namespace}/{name} not found", err=True)
        return

    if format == 'json':
        click.echo(json.dumps(manifest.to_dict(), indent=2))
    elif format == 'yaml':
        click.echo(yaml.dump(manifest.to_dict(), default_flow_style=False))
    else:  # table
        click.echo(f"Name: {manifest.metadata.name}")
        click.echo(f"Namespace: {manifest.metadata.namespace}")
        click.echo(f"Intent: {manifest.spec.intent.value}")
        click.echo(f"Phase: {manifest.status.phase.value}")
        if manifest.status.message:
            click.echo(f"Message: {manifest.status.message}")
        if manifest.spec.target:
            click.echo(f"Target: {manifest.spec.target}")


@manifest_cli.command(name='list')
@click.option('--namespace', '-n', help='Filter by namespace')
@click.option('--label', '-l', multiple=True, help='Filter by label (key=value)')
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']), default='table',
              help='Output format')
def list_manifests(namespace: str, label: tuple, format: str):
    """List control manifests."""
    manager = get_manifest_manager()

    # Parse labels
    labels = {}
    for l in label:
        if '=' in l:
            k, v = l.split('=', 1)
            labels[k] = v

    manifests = manager.list(namespace=namespace, labels=labels if labels else None)

    if format == 'json':
        output = [m.to_dict() for m in manifests]
        click.echo(json.dumps(output, indent=2))
    elif format == 'yaml':
        output = [m.to_dict() for m in manifests]
        click.echo(yaml.dump(output, default_flow_style=False))
    else:  # table
        if not manifests:
            click.echo("No manifests found")
            return

        table_data = []
        for m in manifests:
            table_data.append([
                m.metadata.namespace,
                m.metadata.name,
                m.spec.intent.value,
                m.status.phase.value,
                m.metadata.created_at.strftime('%Y-%m-%d %H:%M') if m.metadata.created_at else 'N/A'
            ])

        headers = ['Namespace', 'Name', 'Intent', 'Phase', 'Created']
        click.echo(tabulate(table_data, headers=headers, tablefmt='simple'))


@manifest_cli.command(name='delete')
@click.argument('name')
@click.option('--namespace', '-n', default='default', help='Namespace')
@click.option('--force', is_flag=True, help='Skip confirmation')
def delete_manifest(name: str, namespace: str, force: bool):
    """Delete a control manifest."""
    if not force:
        if not click.confirm(f"Delete manifest {namespace}/{name}?"):
            return

    manager = get_manifest_manager()
    success, error = manager.delete(name, namespace)

    if success:
        click.echo(f"✓ Deleted manifest: {namespace}/{name}")
    else:
        click.echo(f"❌ Failed to delete: {error}", err=True)


@manifest_cli.command(name='status')
@click.argument('name')
@click.option('--namespace', '-n', default='default', help='Namespace')
@click.option('--phase', type=click.Choice([p.value for p in ManifestPhase]),
              help='Update phase')
@click.option('--message', help='Status message')
def manifest_status(name: str, namespace: str, phase: str, message: str):
    """Get or update manifest status."""
    manager = get_manifest_manager()
    manifest = manager.get(name, namespace)

    if not manifest:
        click.echo(f"❌ Manifest {namespace}/{name} not found", err=True)
        return

    if phase:
        # Update status
        success = manager.update_status(
            name, namespace, ManifestPhase(phase), message
        )
        if success:
            click.echo(f"✓ Updated status to: {phase}")
        else:
            click.echo("❌ Failed to update status", err=True)
    else:
        # Show status
        click.echo(f"Phase: {manifest.status.phase.value}")
        if manifest.status.message:
            click.echo(f"Message: {manifest.status.message}")

        if manifest.status.conditions:
            click.echo("\nConditions:")
            for cond in manifest.status.conditions:
                click.echo(f"  • {cond.get('type')}: {cond.get('message')}")


@manifest_cli.command(name='validate')
@click.argument('file', type=click.Path(exists=True))
def validate_manifest_file(file: str):
    """Validate a manifest file."""
    try:
        with open(file) as f:
            if file.endswith('.yaml') or file.endswith('.yml'):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        manager = get_manifest_manager()
        is_valid, error = manager.validate(data)

        if is_valid:
            click.echo("✓ Manifest is valid")
        else:
            click.echo(f"❌ Validation failed: {error}", err=True)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@manifest_cli.command(name='apply')
@click.argument('file', type=click.Path(exists=True))
def apply_manifest(file: str):
    """Create or update a manifest from file."""
    try:
        with open(file) as f:
            if file.endswith('.yaml') or file.endswith('.yml'):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        manager = get_manifest_manager()
        manifest = ControlManifest.from_dict(data)

        # Check if exists
        existing = manager.get(manifest.metadata.name, manifest.metadata.namespace)

        if existing:
            # Update
            success, error = manager.update(manifest)
            action = "updated"
        else:
            # Create
            success, error = manager.create(manifest)
            action = "created"

        if success:
            click.echo(f"✓ Manifest {action}: {manifest.metadata.namespace}/{manifest.metadata.name}")
        else:
            click.echo(f"❌ Failed to {action[:-1]}: {error}", err=True)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


def register_control_commands(cli):
    """Register control commands with main CLI."""
    cli.add_command(control_cli)
