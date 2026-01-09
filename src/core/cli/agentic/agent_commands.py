"""
HyperSync Agentic CLI Commands

Command-line interface for agent lifecycle management.
"""

import click
import asyncio
import json
from typing import Optional
from tabulate import tabulate
from hypersync.agents.profile_registry import AgentProfileRegistry
from hypersync.agents.composition_engine import CompositionEngine
from hypersync.agents.tasks.lifecycle import LifecycleTaskManager


@click.group(name='agent')
def agent_cli():
    """Agent lifecycle management commands."""
    pass


@agent_cli.command('create')
@click.option('--name', required=True, help='Agent name')
@click.option('--nodes', required=True, multiple=True, help='Node IDs (can specify multiple)')
@click.option('--routing-strategy', default='best_fit', 
              type=click.Choice(['best_fit', 'round_robin', 'priority_weighted', 
                               'capability_match', 'load_balanced', 'explicit_sequence']),
              help='Routing strategy')
@click.option('--clearance', type=click.Choice(['public', 'internal', 'restricted', 
                                                'confidential', 'secret']),
              help='Clearance level')
@click.option('--redaction-profile', help='Redaction profile name')
@click.option('--description', help='Agent description')
@click.option('--annotation', multiple=True, help='Annotations in key=value format')
@click.option('--no-activate', is_flag=True, help='Do not auto-activate after creation')
@click.option('--output', type=click.Choice(['json', 'table']), default='table',
              help='Output format')
def create_agent(name: str, nodes: tuple, routing_strategy: str,
                clearance: Optional[str], redaction_profile: Optional[str],
                description: Optional[str], annotation: tuple,
                no_activate: bool, output: str):
    """Create a new agent profile."""

    # Build profile data
    profile_data = {
        'name': name,
        'version': '1.0.0',
        'nodes': list(nodes),
        'routing_strategy': routing_strategy
    }

    if description:
        profile_data['description'] = description

    # Policy bindings
    if clearance or redaction_profile:
        profile_data['policy_bindings'] = {}
        if clearance:
            profile_data['policy_bindings']['clearance_level'] = clearance
        if redaction_profile:
            profile_data['policy_bindings']['redaction_profile'] = redaction_profile

    # Annotations
    if annotation:
        profile_data['annotations'] = {}
        for ann in annotation:
            if '=' in ann:
                key, value = ann.split('=', 1)
                profile_data['annotations'][key] = value

    # Initialize components
    registry = AgentProfileRegistry()
    engine = CompositionEngine(capability_registry=None)  # TODO: inject real registry
    task_manager = LifecycleTaskManager(registry, engine)

    # Execute creation
    result = asyncio.run(task_manager.create_agent(
        profile_data, 
        auto_activate=not no_activate
    ))

    # Output result
    if output == 'json':
        click.echo(json.dumps(result, indent=2))
    else:
        if result['success']:
            click.secho(f"✓ Agent created: {result['agent_id']}", fg='green')
            click.echo(f"  Duration: {result['duration_ms']:.2f}ms")
            click.echo(f"  Activated: {result['activated']}")
        else:
            click.secho(f"✗ Creation failed: {result.get('error')}", fg='red')


@agent_cli.command('list')
@click.option('--state', type=click.Choice(['draft', 'active', 'deprecated', 'archived']),
              help='Filter by lifecycle state')
@click.option('--output', type=click.Choice(['json', 'table']), default='table',
              help='Output format')
def list_agents(state: Optional[str], output: str):
    """List all agent profiles."""

    registry = AgentProfileRegistry()

    filters = {}
    if state:
        filters['lifecycle.state'] = state

    profiles = registry.list_profiles(filters)

    if output == 'json':
        click.echo(json.dumps(profiles, indent=2))
    else:
        if not profiles:
            click.echo("No agents found.")
            return

        table_data = []
        for profile in profiles:
            table_data.append([
                profile['agent_id'],
                profile['name'],
                profile['version'],
                profile.get('lifecycle', {}).get('state', 'unknown'),
                len(profile.get('nodes', [])),
                profile.get('routing_strategy', 'N/A')
            ])

        headers = ['Agent ID', 'Name', 'Version', 'State', 'Nodes', 'Strategy']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


@agent_cli.command('get')
@click.argument('agent_id')
@click.option('--output', type=click.Choice(['json', 'yaml']), default='json',
              help='Output format')
def get_agent(agent_id: str, output: str):
    """Get detailed information about an agent."""

    registry = AgentProfileRegistry()
    profile = registry.get_profile(agent_id)

    if not profile:
        click.secho(f"✗ Agent {agent_id} not found", fg='red')
        return

    if output == 'json':
        click.echo(json.dumps(profile, indent=2))
    else:
        # YAML output
        import yaml
        click.echo(yaml.dump(profile, default_flow_style=False))


@agent_cli.command('update')
@click.argument('agent_id')
@click.option('--description', help='Update description')
@click.option('--add-node', multiple=True, help='Add node(s)')
@click.option('--remove-node', multiple=True, help='Remove node(s)')
@click.option('--clearance', type=click.Choice(['public', 'internal', 'restricted',
                                                'confidential', 'secret']),
              help='Update clearance level')
@click.option('--no-rebuild', is_flag=True, help='Skip rebuild after update')
@click.option('--output', type=click.Choice(['json', 'table']), default='table',
              help='Output format')
def update_agent(agent_id: str, description: Optional[str],
                add_node: tuple, remove_node: tuple,
                clearance: Optional[str], no_rebuild: bool, output: str):
    """Update an existing agent profile."""

    registry = AgentProfileRegistry()
    profile = registry.get_profile(agent_id)

    if not profile:
        click.secho(f"✗ Agent {agent_id} not found", fg='red')
        return

    # Build updates
    updates = {}

    if description:
        updates['description'] = description

    if add_node or remove_node:
        current_nodes = set(profile.get('nodes', []))
        current_nodes.update(add_node)
        current_nodes.difference_update(remove_node)
        updates['nodes'] = list(current_nodes)

    if clearance:
        if 'policy_bindings' not in updates:
            updates['policy_bindings'] = profile.get('policy_bindings', {}).copy()
        updates['policy_bindings']['clearance_level'] = clearance

    if not updates:
        click.secho("No updates specified", fg='yellow')
        return

    # Execute update
    engine = CompositionEngine(capability_registry=None)
    task_manager = LifecycleTaskManager(registry, engine)

    result = asyncio.run(task_manager.update_agent(
        agent_id,
        updates,
        rebuild=not no_rebuild
    ))

    # Output result
    if output == 'json':
        click.echo(json.dumps(result, indent=2))
    else:
        if result['success']:
            click.secho(f"✓ Agent updated: {agent_id}", fg='green')
            click.echo(f"  Duration: {result['duration_ms']:.2f}ms")
            click.echo(f"  Rebuilt: {result['rebuilt']}")
        else:
            click.secho(f"✗ Update failed: {result.get('error')}", fg='red')


@agent_cli.command('delete')
@click.argument('agent_id')
@click.option('--force', is_flag=True, help='Force deletion even if active')
@click.confirmation_option(prompt='Are you sure you want to delete this agent?')
def delete_agent(agent_id: str, force: bool):
    """Delete an agent profile."""

    registry = AgentProfileRegistry()
    engine = CompositionEngine(capability_registry=None)
    task_manager = LifecycleTaskManager(registry, engine)

    result = asyncio.run(task_manager.delete_agent(agent_id, force=force))

    if result['success']:
        click.secho(f"✓ Agent deleted: {agent_id}", fg='green')
    else:
        click.secho(f"✗ Deletion failed: {result.get('error')}", fg='red')


@agent_cli.command('activate')
@click.argument('agent_id')
def activate_agent(agent_id: str):
    """Activate an agent profile."""

    registry = AgentProfileRegistry()

    try:
        registry.activate_profile(agent_id)
        click.secho(f"✓ Agent activated: {agent_id}", fg='green')
    except ValueError as e:
        click.secho(f"✗ Activation failed: {e}", fg='red')


@agent_cli.command('suspend')
@click.argument('agent_id')
def suspend_agent(agent_id: str):
    """Suspend an active agent."""

    registry = AgentProfileRegistry()
    engine = CompositionEngine(capability_registry=None)
    task_manager = LifecycleTaskManager(registry, engine)

    result = asyncio.run(task_manager.suspend_agent(agent_id))

    if result['success']:
        click.secho(f"✓ Agent suspended: {agent_id}", fg='green')
    else:
        click.secho(f"✗ Suspension failed: {result.get('error')}", fg='red')


@agent_cli.command('resume')
@click.argument('agent_id')
def resume_agent(agent_id: str):
    """Resume a suspended agent."""

    registry = AgentProfileRegistry()
    engine = CompositionEngine(capability_registry=None)
    task_manager = LifecycleTaskManager(registry, engine)

    result = asyncio.run(task_manager.resume_agent(agent_id))

    if result['success']:
        click.secho(f"✓ Agent resumed: {agent_id}", fg='green')
    else:
        click.secho(f"✗ Resume failed: {result.get('error')}", fg='red')


@agent_cli.command('restart')
@click.argument('agent_id')
def restart_agent(agent_id: str):
    """Restart an agent (suspend + resume)."""

    registry = AgentProfileRegistry()
    engine = CompositionEngine(capability_registry=None)
    task_manager = LifecycleTaskManager(registry, engine)

    result = asyncio.run(task_manager.restart_agent(agent_id))

    if result['success']:
        click.secho(f"✓ Agent restarted: {agent_id}", fg='green')
    else:
        click.secho(f"✗ Restart failed: {result.get('error')}", fg='red')


@agent_cli.command('validate')
@click.argument('agent_id')
@click.option('--output', type=click.Choice(['json', 'table']), default='table',
              help='Output format')
def validate_agent(agent_id: str, output: str):
    """Validate agent capabilities against nodes."""

    registry = AgentProfileRegistry()
    report = registry.validate_node_capabilities(agent_id)

    if output == 'json':
        click.echo(json.dumps(report, indent=2))
    else:
        if report.get('valid'):
            click.secho(f"✓ Agent {agent_id} validation passed", fg='green')
        else:
            click.secho(f"✗ Agent {agent_id} validation failed", fg='red')
            for error in report.get('errors', []):
                click.echo(f"  • {error}")


@agent_cli.command('nodes')
@click.argument('agent_id')
def list_agent_nodes(agent_id: str):
    """List nodes associated with an agent."""

    registry = AgentProfileRegistry()
    nodes = registry.get_profile_nodes(agent_id)

    if not nodes:
        click.echo(f"No nodes found for agent {agent_id}")
        return

    click.echo(f"Nodes for {agent_id}:")
    for node in nodes:
        click.echo(f"  • {node}")


if __name__ == '__main__':
    agent_cli()
