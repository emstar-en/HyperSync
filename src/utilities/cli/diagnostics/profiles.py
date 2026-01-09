"""
Diagnostics Profile CLI
"""
import click
from diagnostics.profile_manager import activate_profile


@click.group()
def profiles():
    """Manage diagnostic profiles."""
    pass


@profiles.command()
def list():
    """List available profiles."""
    click.echo("Available profiles: standard, verbose, debug")


@profiles.command()
@click.argument('profile_id')
def activate(profile_id):
    """Activate a diagnostic profile."""
    result = activate_profile(profile_id)
    if result["activated"]:
        click.echo(f"✓ Activated profile: {profile_id}")
    else:
        click.echo(f"✗ Failed to activate profile")


@profiles.command()
def status():
    """Show active profile status."""
    click.echo("Active profile: standard")
