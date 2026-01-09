"""
CLI commands for integration mode management.

Provides commands to list, get, set, and validate integration modes.
"""

import click
import json
import yaml
from typing import Optional
from tabulate import tabulate

from hypersync.wiring.integration_modes import (
    IntegrationMode,
    IntegrationModeManager,
    get_mode_manager
)


@click.group(name='integration')
def integration_cli():
    """Manage HyperSync integration modes and capabilities."""
    pass


@integration_cli.group(name='mode')
def mode_cli():
    """Integration mode operations."""
    pass


@mode_cli.command(name='list')
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']), default='table',
              help='Output format')
@click.option('--verbose', is_flag=True, help='Show detailed information')
def list_modes(format: str, verbose: bool):
    """List all available integration modes."""
    manager = get_mode_manager()
    profiles = manager.list_modes()

    if format == 'json':
        output = [p.to_dict() for p in profiles]
        click.echo(json.dumps(output, indent=2))

    elif format == 'yaml':
        output = [p.to_dict() for p in profiles]
        click.echo(yaml.dump(output, default_flow_style=False))

    else:  # table
        if verbose:
            # Detailed table
            for profile in profiles:
                click.echo(f"\n{'='*80}")
                click.echo(f"Mode: {profile.mode.value}")
                click.echo(f"Name: {profile.name}")
                click.echo(f"Description: {profile.description}")
                click.echo(f"Risk Level: {profile.risk_level}")
                click.echo(f"\nCapabilities:")

                caps = profile.capabilities.__dict__
                cap_table = [[k, '✓' if v else '✗'] for k, v in caps.items()]
                click.echo(tabulate(cap_table, headers=['Capability', 'Enabled'], tablefmt='simple'))

                if profile.dependencies:
                    click.echo(f"\nDependencies: {', '.join(profile.dependencies)}")
        else:
            # Summary table
            current_mode = manager.get_mode()
            table_data = []
            for profile in profiles:
                is_current = '→' if profile.mode == current_mode else ' '
                caps_enabled = sum(1 for v in profile.capabilities.__dict__.values() if v)
                caps_total = len(profile.capabilities.__dict__)

                table_data.append([
                    is_current,
                    profile.mode.value,
                    profile.name,
                    profile.risk_level,
                    f"{caps_enabled}/{caps_total}",
                    len(profile.dependencies)
                ])

            headers = ['', 'Mode', 'Name', 'Risk', 'Capabilities', 'Dependencies']
            click.echo(tabulate(table_data, headers=headers, tablefmt='simple'))


@mode_cli.command(name='get')
@click.option('--format', type=click.Choice(['text', 'json', 'yaml']), default='text',
              help='Output format')
def get_mode(format: str):
    """Get current integration mode."""
    manager = get_mode_manager()
    current_mode = manager.get_mode()

    if not current_mode:
        click.echo("No integration mode set", err=True)
        return

    profile = manager.get_profile(current_mode)

    if format == 'json':
        click.echo(json.dumps(profile.to_dict(), indent=2))
    elif format == 'yaml':
        click.echo(yaml.dump(profile.to_dict(), default_flow_style=False))
    else:
        click.echo(f"Current Mode: {current_mode.value}")
        click.echo(f"Name: {profile.name}")
        click.echo(f"Description: {profile.description}")
        click.echo(f"Risk Level: {profile.risk_level}")


@mode_cli.command(name='set')
@click.argument('mode', type=click.Choice([m.value for m in IntegrationMode]))
@click.option('--force', is_flag=True, help='Skip validation checks')
@click.option('--dry-run', is_flag=True, help='Validate without applying')
def set_mode(mode: str, force: bool, dry_run: bool):
    """Set integration mode."""
    manager = get_mode_manager()
    target_mode = IntegrationMode(mode)
    current_mode = manager.get_mode()

    # Validate transition if current mode exists
    if current_mode and not force:
        is_valid, reason = manager.validate_transition(current_mode, target_mode)
        if not is_valid:
            click.echo(f"❌ Invalid transition: {reason}", err=True)
            click.echo(f"Use --force to override", err=True)
            return

    if dry_run:
        click.echo(f"✓ Transition validation passed")
        click.echo(f"Would set mode: {current_mode.value if current_mode else 'none'} → {target_mode.value}")
        return

    # Apply mode change
    success = manager.set_mode(target_mode)

    if success:
        click.echo(f"✓ Integration mode set to: {target_mode.value}")

        # Show what changed
        profile = manager.get_profile(target_mode)
        click.echo(f"\nEnabled capabilities:")
        caps = profile.capabilities.__dict__
        enabled = [k for k, v in caps.items() if v]
        for cap in enabled:
            click.echo(f"  • {cap}")

        click.echo(f"\nRequired dependencies:")
        for dep in profile.dependencies:
            click.echo(f"  • {dep}")
    else:
        click.echo(f"❌ Failed to set mode: {target_mode.value}", err=True)


@mode_cli.command(name='validate')
@click.argument('from_mode', type=click.Choice([m.value for m in IntegrationMode]))
@click.argument('to_mode', type=click.Choice([m.value for m in IntegrationMode]))
def validate_transition(from_mode: str, to_mode: str):
    """Validate mode transition."""
    manager = get_mode_manager()
    from_m = IntegrationMode(from_mode)
    to_m = IntegrationMode(to_mode)

    is_valid, reason = manager.validate_transition(from_m, to_m)

    if is_valid:
        click.echo(f"✓ Transition valid: {from_mode} → {to_mode}")
        click.echo(f"Reason: {reason}")
    else:
        click.echo(f"❌ Transition invalid: {from_mode} → {to_mode}")
        click.echo(f"Reason: {reason}")


@integration_cli.command(name='capabilities')
@click.option('--mode', type=click.Choice([m.value for m in IntegrationMode]),
              help='Show capabilities for specific mode (default: current)')
@click.option('--enabled-only', is_flag=True, help='Show only enabled capabilities')
def show_capabilities(mode: Optional[str], enabled_only: bool):
    """Show capabilities for integration mode."""
    manager = get_mode_manager()

    if mode:
        target_mode = IntegrationMode(mode)
        profile = manager.get_profile(target_mode)
    else:
        profile = manager.get_profile()

    if not profile:
        click.echo("No mode selected", err=True)
        return

    click.echo(f"Capabilities for mode: {profile.mode.value}")
    click.echo(f"{'='*60}")

    caps = profile.capabilities.__dict__
    table_data = []

    for cap, enabled in caps.items():
        if enabled_only and not enabled:
            continue

        status = '✓' if enabled else '✗'
        table_data.append([cap, status])

    click.echo(tabulate(table_data, headers=['Capability', 'Status'], tablefmt='simple'))


@integration_cli.command(name='export')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', type=click.Choice(['json', 'yaml']), default='yaml',
              help='Output format')
def export_config(output: Optional[str], format: str):
    """Export integration mode configuration."""
    manager = get_mode_manager()
    config = manager.export_config()

    if format == 'json':
        output_str = json.dumps(config, indent=2)
    else:
        output_str = yaml.dump(config, default_flow_style=False)

    if output:
        with open(output, 'w') as f:
            f.write(output_str)
        click.echo(f"✓ Configuration exported to: {output}")
    else:
        click.echo(output_str)


# Register with main CLI
def register_integration_commands(cli):
    """Register integration commands with main CLI."""
    cli.add_command(integration_cli)
