"""
CLI commands for budget management.
"""

import click
import json
from tabulate import tabulate
from hypersync.policy.budget.manager import get_budget_manager, BudgetLimit


@click.group()
def budget():
    """Manage token budgets."""
    pass


@budget.command()
@click.option('--user', help='User ID')
@click.option('--provider', help='Provider ID')
@click.option('--session', help='Session ID')
def status(user, provider, session):
    """Show budget status."""
    manager = get_budget_manager()

    # Determine scope ID
    if user:
        scope_id = f"user:{user}"
    elif provider:
        scope_id = f"provider:{provider}"
    elif session:
        scope_id = f"session:{session}"
    else:
        click.echo("Error: Must specify --user, --provider, or --session")
        return

    # Get usage and remaining
    usage = manager.get_usage(scope_id)
    remaining = manager.get_remaining(scope_id)

    if not usage:
        click.echo(f"No budget configured for {scope_id}")
        return

    click.echo("=" * 80)
    click.echo(f"BUDGET STATUS: {scope_id}")
    click.echo("=" * 80)
    click.echo()

    # Daily
    click.echo("Daily:")
    click.echo(f"  Tokens Used:       {usage.daily_tokens:,}")
    if remaining["daily_tokens"] != float('inf'):
        click.echo(f"  Tokens Remaining:  {int(remaining['daily_tokens']):,}")
    click.echo(f"  Cost:              ${usage.daily_cost_usd:.4f}")
    if remaining["daily_cost_usd"] != float('inf'):
        click.echo(f"  Cost Remaining:    ${remaining['daily_cost_usd']:.4f}")
    click.echo()

    # Monthly
    click.echo("Monthly:")
    click.echo(f"  Tokens Used:       {usage.monthly_tokens:,}")
    if remaining["monthly_tokens"] != float('inf'):
        click.echo(f"  Tokens Remaining:  {int(remaining['monthly_tokens']):,}")
    click.echo(f"  Cost:              ${usage.monthly_cost_usd:.4f}")
    if remaining["monthly_cost_usd"] != float('inf'):
        click.echo(f"  Cost Remaining:    ${remaining['monthly_cost_usd']:.4f}")


@budget.command()
@click.option('--user', help='User ID')
@click.option('--provider', help='Provider ID')
@click.option('--daily-tokens', type=int, help='Daily token limit')
@click.option('--monthly-tokens', type=int, help='Monthly token limit')
@click.option('--per-request-tokens', type=int, help='Per-request token limit')
@click.option('--daily-cost', type=float, help='Daily cost limit (USD)')
@click.option('--monthly-cost', type=float, help='Monthly cost limit (USD)')
def set_limit(user, provider, daily_tokens, monthly_tokens, per_request_tokens, daily_cost, monthly_cost):
    """Set budget limits."""
    manager = get_budget_manager()

    # Determine scope ID
    if user:
        scope_id = f"user:{user}"
    elif provider:
        scope_id = f"provider:{provider}"
    else:
        click.echo("Error: Must specify --user or --provider")
        return

    # Create limit
    limit = BudgetLimit(
        daily_tokens=daily_tokens,
        monthly_tokens=monthly_tokens,
        per_request_tokens=per_request_tokens,
        daily_cost_usd=daily_cost,
        monthly_cost_usd=monthly_cost
    )

    manager.set_limit(scope_id, limit)

    click.echo(f"✓ Budget limit set for {scope_id}")


@budget.command()
@click.argument('policy_file', type=click.Path(exists=True))
def load(policy_file):
    """Load budget policies from file."""
    from hypersync.policy.engine import get_policy_engine

    engine = get_policy_engine()
    engine.load_policies_from_file(policy_file)

    click.echo(f"✓ Policies loaded from {policy_file}")
