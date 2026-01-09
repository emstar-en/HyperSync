"""Provider CLI - Manage cloud model providers"""
import click
from rich.console import Console
from .provider_manager import ProviderManager

console = Console()

@click.group(name='provider')
def provider_cli():
    """Manage cloud model providers"""
    pass

@provider_cli.command(name='add')
@click.option('--name', required=True)
@click.option('--type', 'provider_type', required=True, 
              type=click.Choice(['openai', 'anthropic', 'azure', 'google', 'cohere']))
@click.option('--api-key', required=True)
@click.option('--base-url', help='Custom base URL')
def add_provider(name, provider_type, api_key, base_url):
    """Add a new cloud provider"""
    manager = ProviderManager()

    # Create credential
    cred = manager.create_credential(
        name=f"{name}-key",
        provider_type=provider_type,
        value=api_key
    )

    # Create provider
    endpoint = {"base_url": base_url} if base_url else {}
    provider = manager.create_provider(
        name=name,
        provider_type=provider_type,
        credential_id=cred.credential_id,
        endpoint=endpoint
    )

    console.print(f"[green]✓[/green] Added provider: {provider.provider_id}")

@provider_cli.command(name='list')
def list_providers():
    """List cloud providers"""
    manager = ProviderManager()
    providers = manager.list_providers()

    for p in providers:
        console.print(f"{p.name} ({p.provider_type}) - {p.status}")

@provider_cli.command(name='models')
@click.argument('provider_id')
def list_models(provider_id):
    """List models from a provider"""
    manager = ProviderManager()
    models = manager.list_external_models(provider_id=provider_id)

    for m in models:
        console.print(f"{m.display_name} ({m.external_model_id})")

def register_cli(cli_group):
    """Register provider commands"""
    cli_group.add_command(provider_cli)
