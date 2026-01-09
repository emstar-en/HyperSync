"""
CLI commands for prompt operations.
"""

import asyncio
import click
from hypersync.prompt.router import get_router
from hypersync.prompt.format.verbose import get_formatter


@click.group()
def prompt():
    """Prompt operations with token tracking."""
    pass


@prompt.command()
@click.argument('text')
@click.option('--provider', '-p', help='Provider ID')
@click.option('--model', '-m', help='Model name')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed token breakdown')
@click.option('--no-compress', is_flag=True, help='Disable compression pipeline')
@click.option('--temperature', type=float, default=0.7, help='Sampling temperature')
@click.option('--max-tokens', type=int, default=2048, help='Maximum tokens to generate')
def send(text, provider, model, verbose, no_compress, temperature, max_tokens):
    """Send a prompt to a provider."""
    asyncio.run(_send_prompt(
        text, provider, model, verbose, no_compress, temperature, max_tokens
    ))


async def _send_prompt(text, provider, model, verbose, no_compress, temperature, max_tokens):
    """Send prompt implementation."""
    router = get_router()
    formatter = get_formatter()

    try:
        # Send prompt
        response = await router.route(
            prompt=text,
            provider=provider,
            model=model,
            local_preprocess=not no_compress,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Format output
        if verbose:
            output = formatter.format_response(response, verbose=True)
            click.echo(output)
        else:
            # Just the text
            click.echo(response.get("text", ""))

            # Compact summary
            receipt = response.get("receipt")
            if receipt:
                summary = formatter.format_compact(receipt)
                click.echo(f"
[{summary}]", err=True)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@prompt.command()
@click.option('--today', is_flag=True, help='Show stats for today')
@click.option('--user', help='Filter by user ID')
@click.option('--provider', help='Filter by provider')
@click.option('--session', help='Filter by session ID')
def stats(today, user, provider, session):
    """Show token usage statistics."""
    asyncio.run(_show_stats(today, user, provider, session))


async def _show_stats(today, user, provider, session):
    """Show statistics implementation."""
    from hypersync.token.receipts import get_accumulator
    from hypersync.token.telemetry import get_token_metrics
    from tabulate import tabulate

    # Get metrics
    metrics = get_token_metrics()
    data = metrics.get_metrics()

    # Overall stats
    click.echo("=" * 80)
    click.echo("TOKEN USAGE STATISTICS")
    click.echo("=" * 80)
    click.echo(f"Total Tokens:          {data['total_tokens']:,}")
    click.echo(f"Tokens Saved:          {data['tokens_saved']:,}")
    click.echo(f"Total Requests:        {data['requests']:,}")
    click.echo("")

    # By stage
    if data.get('by_stage'):
        click.echo("By Stage:")
        click.echo("-" * 80)

        stage_rows = []
        for stage, stats in data['by_stage'].items():
            stage_rows.append([
                stage,
                f"{stats['tokens']:,}",
                f"{stats['saved']:,}",
                stats['count']
            ])

        click.echo(tabulate(
            stage_rows,
            headers=["Stage", "Tokens", "Saved", "Count"],
            tablefmt="grid"
        ))
        click.echo("")

    # By provider
    if data.get('by_provider'):
        click.echo("By Provider:")
        click.echo("-" * 80)

        provider_rows = []
        for prov, stats in data['by_provider'].items():
            provider_rows.append([
                prov,
                f"{stats['tokens']:,}",
                stats['requests']
            ])

        click.echo(tabulate(
            provider_rows,
            headers=["Provider", "Tokens", "Requests"],
            tablefmt="grid"
        ))
        click.echo("")

    # By user
    if data.get('by_user') and user:
        user_stats = data['by_user'].get(user)
        if user_stats:
            click.echo(f"User: {user}")
            click.echo("-" * 80)
            click.echo(f"Tokens:                {user_stats['tokens']:,}")
            click.echo(f"Requests:              {user_stats['requests']}")
