"""
CLI commands for provider management.
"""

import asyncio
import click
import json
from pathlib import Path
from tabulate import tabulate

from hypersync.providers import get_registry, ProviderConfig
from hypersync.providers.adapters.factory import AdapterFactory
from hypersync.bootstrap.wizard import run_bootstrap


@click.group()
def providers():
    """Manage cloud provider integrations."""
    pass


@providers.command()
def bootstrap():
    """Run the bootstrap wizard to configure providers."""
    asyncio.run(run_bootstrap())


@providers.command()
@click.option('--config', type=click.Path(), help='Provider config file')
def list(config):
    """List configured providers."""
    config_file = Path(config) if config else Path.home() / ".hypersync" / "providers.json"

    if not config_file.exists():
        click.echo("No providers configured. Run 'hypersync providers bootstrap' first.")
        return

    with open(config_file) as f:
        data = json.load(f)

    providers_list = []
    for provider_id, config in data.get("providers", {}).items():
        providers_list.append([
            provider_id,
            config.get("adapter_class", "unknown"),
            "✓" if config.get("enabled") else "✗",
            config.get("api_base", "N/A")
        ])

    if providers_list:
        click.echo(tabulate(
            providers_list,
            headers=["Provider ID", "Adapter", "Enabled", "API Base"],
            tablefmt="grid"
        ))
    else:
        click.echo("No providers configured.")


@providers.command()
@click.option('--config', type=click.Path(), help='Provider config file')
def health():
    """Check health of all configured providers."""
    asyncio.run(_health_check(config))


async def _health_check(config):
    """Run health checks."""
    config_file = Path(config) if config else Path.home() / ".hypersync" / "providers.json"

    if not config_file.exists():
        click.echo("No providers configured.")
        return

    with open(config_file) as f:
        data = json.load(f)

    results = []
    for provider_id, config_dict in data.get("providers", {}).items():
        if not config_dict.get("enabled"):
            results.append([provider_id, "disabled", "-", "-"])
            continue

        try:
            adapter = AdapterFactory.create_from_dict(
                config_dict["adapter_class"],
                config_dict
            )

            await adapter.initialize()
            status = await adapter.health_check()
            await adapter.shutdown()

            status_icon = {
                "healthy": "✅",
                "degraded": "⚠️",
                "unavailable": "❌",
                "unauthorized": "🔒"
            }.get(status.value, "❓")

            results.append([
                provider_id,
                config_dict["adapter_class"],
                status_icon,
                status.value
            ])

        except Exception as e:
            results.append([provider_id, config_dict["adapter_class"], "❌", str(e)[:50]])

    click.echo(tabulate(
        results,
        headers=["Provider", "Adapter", "Status", "Details"],
        tablefmt="grid"
    ))


@providers.command()
@click.argument('provider_id')
@click.option('--adapter', required=True, help='Adapter class name')
@click.option('--api-key', required=True, help='API key')
@click.option('--api-base', help='API base URL')
def add(provider_id, adapter, api_key, api_base):
    """Add a new provider configuration."""
    config_file = Path.home() / ".hypersync" / "providers.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Load existing config
    if config_file.exists():
        with open(config_file) as f:
            data = json.load(f)
    else:
        data = {"version": "1.0", "providers": {}}

    # Add new provider
    data["providers"][provider_id] = {
        "provider_id": provider_id,
        "adapter_class": adapter,
        "api_key": api_key,
        "api_base": api_base,
        "timeout": 30,
        "max_retries": 3,
        "enabled": True
    }

    # Save
    with open(config_file, 'w') as f:
        json.dump(data, f, indent=2)

    click.echo(f"✓ Provider '{provider_id}' added successfully")


@providers.command()
@click.argument('provider_id')
def remove(provider_id):
    """Remove a provider configuration."""
    config_file = Path.home() / ".hypersync" / "providers.json"

    if not config_file.exists():
        click.echo("No providers configured.")
        return

    with open(config_file) as f:
        data = json.load(f)

    if provider_id in data.get("providers", {}):
        del data["providers"][provider_id]

        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)

        click.echo(f"✓ Provider '{provider_id}' removed")
    else:
        click.echo(f"Provider '{provider_id}' not found")
