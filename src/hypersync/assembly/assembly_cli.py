"""
Assembly CLI

Command-line interface for model stacks and node assemblies.
"""

import click
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from typing import Optional

from .assembly_manager import AssemblyManager

console = Console()


@click.group(name='stack')
def stack_cli():
    """Manage model stacks"""
    pass


@click.group(name='assembly')
def assembly_cli():
    """Manage node assemblies"""
    pass


# ============================================================================
# Stack Commands
# ============================================================================

@stack_cli.command(name='create')
@click.option('--name', required=True, help='Stack name')
@click.option('--description', help='Stack description')
@click.option('--model', 'models', multiple=True, required=True,
              help='Model in format role:model_id (e.g., reasoning:gpt-4)')
@click.option('--mode', type=click.Choice(['sequential', 'parallel', 'router', 'ensemble', 'pipeline']),
              default='sequential', help='Orchestration mode')
@click.option('--cpu', type=int, help='CPU cores')
@click.option('--memory', type=float, help='Memory in GB')
@click.option('--gpu', type=int, help='GPU count')
@click.option('--tags', multiple=True, help='Tags')
@click.option('--db', default='assembly.db', help='Database path')
def create_stack(name, description, models, mode, cpu, memory, gpu, tags, db):
    """Create a new model stack"""
    manager = AssemblyManager(db)

    # Parse models
    model_list = []
    for m in models:
        if ':' not in m:
            console.print(f"[red]✗[/red] Invalid model format: {m}. Use role:model_id")
            return

        role, model_id = m.split(':', 1)
        model_list.append({
            "role": role,
            "model_id": model_id,
            "catalogue_entry": model_id,
            "priority": 10
        })

    # Resource requirements
    resources = None
    if cpu or memory or gpu:
        resources = {}
        if cpu:
            resources["cpu_cores"] = cpu
        if memory:
            resources["memory_gb"] = memory
        if gpu:
            resources["gpu_count"] = gpu

    orchestration = {"mode": mode}

    stack = manager.create_stack(
        name=name,
        models=model_list,
        description=description,
        orchestration=orchestration,
        resource_requirements=resources,
        tags=list(tags) if tags else None
    )

    console.print(Panel.fit(
        f"[green]✓[/green] Created model stack\n\n"
        f"[cyan]ID:[/cyan] {stack.stack_id}\n"
        f"[cyan]Name:[/cyan] {stack.name}\n"
        f"[cyan]Models:[/cyan] {len(stack.models)}\n"
        f"[cyan]Mode:[/cyan] {mode}",
        title="Model Stack Created",
        border_style="green"
    ))


@stack_cli.command(name='list')
@click.option('--tags', multiple=True, help='Filter by tags')
@click.option('--limit', type=int, default=20, help='Maximum results')
@click.option('--db', default='assembly.db', help='Database path')
def list_stacks(tags, limit, db):
    """List model stacks"""
    manager = AssemblyManager(db)
    stacks = manager.list_stacks(tags=list(tags) if tags else None, limit=limit)

    if not stacks:
        console.print("[yellow]No stacks found[/yellow]")
        return

    table = Table(title=f"Model Stacks ({len(stacks)})")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Models", style="yellow")
    table.add_column("Mode", style="magenta")
    table.add_column("Resources", style="blue")
    table.add_column("Created", style="dim")

    for stack in stacks:
        resources = stack.resource_requirements or {}
        resource_str = f"{resources.get('cpu_cores', 0)}C/{resources.get('memory_gb', 0)}G"
        if resources.get('gpu_count', 0) > 0:
            resource_str += f"/{resources.get('gpu_count')}GPU"

        table.add_row(
            stack.stack_id[:16] + "...",
            stack.name,
            str(len(stack.models)),
            stack.orchestration.get("mode", "N/A") if stack.orchestration else "N/A",
            resource_str,
            stack.created_at[:10]
        )

    console.print(table)


@stack_cli.command(name='info')
@click.argument('stack_id')
@click.option('--db', default='assembly.db', help='Database path')
def stack_info(stack_id, db):
    """Show detailed stack information"""
    manager = AssemblyManager(db)
    stack = manager.get_stack(stack_id)

    if not stack:
        console.print(f"[red]✗[/red] Stack not found: {stack_id}")
        return

    # Build info tree
    tree = Tree(f"[cyan]{stack.name}[/cyan] ({stack.stack_id})")

    # Models
    models_branch = tree.add("[yellow]Models[/yellow]")
    for model in stack.models:
        model_info = f"{model['role']}: {model['model_id']}"
        if model.get('priority'):
            model_info += f" (priority: {model['priority']})"
        models_branch.add(model_info)

    # Orchestration
    if stack.orchestration:
        orch_branch = tree.add("[yellow]Orchestration[/yellow]")
        orch_branch.add(f"Mode: {stack.orchestration.get('mode', 'N/A')}")

    # Resources
    if stack.resource_requirements:
        res_branch = tree.add("[yellow]Resources[/yellow]")
        res = stack.resource_requirements
        if res.get('cpu_cores'):
            res_branch.add(f"CPU: {res['cpu_cores']} cores")
        if res.get('memory_gb'):
            res_branch.add(f"Memory: {res['memory_gb']} GB")
        if res.get('gpu_count'):
            res_branch.add(f"GPU: {res['gpu_count']} x {res.get('gpu_memory_gb', 0)} GB")

    # Capabilities
    if stack.capabilities:
        cap_branch = tree.add("[yellow]Capabilities[/yellow]")
        for cap in stack.capabilities:
            cap_branch.add(cap)

    # Metadata
    meta_branch = tree.add("[yellow]Metadata[/yellow]")
    meta_branch.add(f"Version: {stack.version}")
    meta_branch.add(f"Created: {stack.created_at}")
    if stack.tags:
        meta_branch.add(f"Tags: {', '.join(stack.tags)}")

    console.print(tree)


@stack_cli.command(name='delete')
@click.argument('stack_id')
@click.option('--yes', is_flag=True, help='Skip confirmation')
@click.option('--db', default='assembly.db', help='Database path')
def delete_stack(stack_id, yes, db):
    """Delete a model stack"""
    manager = AssemblyManager(db)

    stack = manager.get_stack(stack_id)
    if not stack:
        console.print(f"[red]✗[/red] Stack not found: {stack_id}")
        return

    if not yes:
        confirm = click.confirm(f"Delete stack '{stack.name}' ({stack_id})?")
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            return

    try:
        manager.delete_stack(stack_id)
        console.print(f"[green]✓[/green] Deleted stack: {stack_id}")
    except ValueError as e:
        console.print(f"[red]✗[/red] {str(e)}")


# ============================================================================
# Assembly Commands
# ============================================================================

@assembly_cli.command(name='create')
@click.option('--name', required=True, help='Assembly name')
@click.option('--stack-id', required=True, help='Stack ID to deploy')
@click.option('--target-ld', required=True, help='Target Lorentzian Domain')
@click.option('--description', help='Assembly description')
@click.option('--security', type=click.Choice(['public', 'restricted', 'secure', 'isolated']),
              default='secure', help='Security level')
@click.option('--tags', multiple=True, help='Tags')
@click.option('--db', default='assembly.db', help='Database path')
def create_assembly(name, stack_id, target_ld, description, security, tags, db):
    """Create a new node assembly"""
    manager = AssemblyManager(db)

    try:
        assembly = manager.create_assembly(
            name=name,
            stack_id=stack_id,
            target_ld=target_ld,
            description=description,
            security_level=security,
            tags=list(tags) if tags else None
        )

        console.print(Panel.fit(
            f"[green]✓[/green] Created node assembly\n\n"
            f"[cyan]ID:[/cyan] {assembly.assembly_id}\n"
            f"[cyan]Name:[/cyan] {assembly.name}\n"
            f"[cyan]Stack:[/cyan] {assembly.stack_id}\n"
            f"[cyan]Target LD:[/cyan] {target_ld}\n"
            f"[cyan]Security:[/cyan] {security}\n"
            f"[cyan]Status:[/cyan] {assembly.status}",
            title="Node Assembly Created",
            border_style="green"
        ))
    except ValueError as e:
        console.print(f"[red]✗[/red] {str(e)}")


@assembly_cli.command(name='list')
@click.option('--stack-id', help='Filter by stack ID')
@click.option('--status', type=click.Choice(['draft', 'validating', 'ready', 'deploying', 'deployed', 'failed', 'stopped']),
              help='Filter by status')
@click.option('--limit', type=int, default=20, help='Maximum results')
@click.option('--db', default='assembly.db', help='Database path')
def list_assemblies(stack_id, status, limit, db):
    """List node assemblies"""
    manager = AssemblyManager(db)
    assemblies = manager.list_assemblies(stack_id=stack_id, status=status, limit=limit)

    if not assemblies:
        console.print("[yellow]No assemblies found[/yellow]")
        return

    table = Table(title=f"Node Assemblies ({len(assemblies)})")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Stack", style="blue")
    table.add_column("Target LD", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Created", style="dim")

    for assembly in assemblies:
        status_color = {
            "draft": "yellow",
            "ready": "green",
            "deploying": "blue",
            "deployed": "green bold",
            "failed": "red",
            "stopped": "dim"
        }.get(assembly.status, "white")

        table.add_row(
            assembly.assembly_id[:16] + "...",
            assembly.name,
            assembly.stack_id[:12] + "...",
            assembly.deployment_config.get("target_ld", "N/A"),
            f"[{status_color}]{assembly.status}[/{status_color}]",
            assembly.created_at[:10]
        )

    console.print(table)


@assembly_cli.command(name='info')
@click.argument('assembly_id')
@click.option('--db', default='assembly.db', help='Database path')
def assembly_info(assembly_id, db):
    """Show detailed assembly information"""
    manager = AssemblyManager(db)
    assembly = manager.get_assembly(assembly_id)

    if not assembly:
        console.print(f"[red]✗[/red] Assembly not found: {assembly_id}")
        return

    # Get stack info
    stack = manager.get_stack(assembly.stack_id)

    info = f"""[cyan]Assembly ID:[/cyan] {assembly.assembly_id}
[cyan]Name:[/cyan] {assembly.name}
[cyan]Description:[/cyan] {assembly.description or 'N/A'}
[cyan]Status:[/cyan] {assembly.status}

[yellow]Stack:[/yellow]
  ID: {assembly.stack_id}
  Name: {stack.name if stack else 'N/A'}
  Models: {len(stack.models) if stack else 0}

[yellow]Deployment:[/yellow]
  Target LD: {assembly.deployment_config.get('target_ld', 'N/A')}
  Security Level: {assembly.deployment_config.get('security_level', 'N/A')}
"""

    if assembly.deployment_id:
        info += f"  Deployment ID: {assembly.deployment_id}\n"

        # Get deployment info
        deployment = manager.get_deployment(assembly.deployment_id)
        if deployment:
            info += f"  Node ID: {deployment.node_id}\n"
            info += f"  LD Address: {deployment.ld_address}\n"
            info += f"  Status: {deployment.status}\n"
            if deployment.health:
                info += f"  Health: {deployment.health.get('status', 'unknown')}\n"

    if assembly.validation_results:
        vr = assembly.validation_results
        info += f"""
[yellow]Validation:[/yellow]
  Passed: {'✓' if vr.get('passed') else '✗'}
  Checks: {len(vr.get('checks', []))}
  Errors: {len(vr.get('errors', []))}
  Warnings: {len(vr.get('warnings', []))}
"""

    info += f"""
[yellow]Metadata:[/yellow]
  Created: {assembly.created_at}
  Updated: {assembly.updated_at or 'N/A'}
"""

    if assembly.tags:
        info += f"  Tags: {', '.join(assembly.tags)}\n"

    console.print(Panel(info, title="Node Assembly Details", border_style="cyan"))


@assembly_cli.command(name='validate')
@click.argument('assembly_id')
@click.option('--db', default='assembly.db', help='Database path')
def validate_assembly(assembly_id, db):
    """Validate an assembly before deployment"""
    manager = AssemblyManager(db)

    try:
        results = manager.validate_assembly(assembly_id)

        status_icon = "[green]✓[/green]" if results["passed"] else "[red]✗[/red]"
        status_text = "PASSED" if results["passed"] else "FAILED"

        info = f"{status_icon} Validation {status_text}\n\n"
        info += f"[cyan]Checks:[/cyan] {len(results['checks'])}\n"

        for check in results['checks']:
            check_icon = "✓" if check['status'] == 'passed' else "✗"
            info += f"  {check_icon} {check['name']}\n"

        if results['errors']:
            info += f"\n[red]Errors:[/red]\n"
            for error in results['errors']:
                info += f"  • {error}\n"

        if results['warnings']:
            info += f"\n[yellow]Warnings:[/yellow]\n"
            for warning in results['warnings']:
                info += f"  • {warning}\n"

        border_style = "green" if results["passed"] else "red"
        console.print(Panel(info, title="Validation Results", border_style=border_style))

    except ValueError as e:
        console.print(f"[red]✗[/red] {str(e)}")


@assembly_cli.command(name='deploy')
@click.argument('assembly_id')
@click.option('--db', default='assembly.db', help='Database path')
def deploy_assembly(assembly_id, db):
    """Deploy an assembly to the ICO network"""
    manager = AssemblyManager(db)

    try:
        with console.status("[cyan]Deploying assembly...[/cyan]"):
            deployment = manager.deploy_assembly(assembly_id)

        console.print(Panel.fit(
            f"[green]✓[/green] Deployment successful\n\n"
            f"[cyan]Deployment ID:[/cyan] {deployment.deployment_id}\n"
            f"[cyan]Node ID:[/cyan] {deployment.node_id}\n"
            f"[cyan]LD Address:[/cyan] {deployment.ld_address}\n"
            f"[cyan]Status:[/cyan] {deployment.status}",
            title="Deployment Complete",
            border_style="green"
        ))
    except ValueError as e:
        console.print(f"[red]✗[/red] {str(e)}")


@assembly_cli.command(name='stop')
@click.argument('deployment_id')
@click.option('--db', default='assembly.db', help='Database path')
def stop_deployment(deployment_id, db):
    """Stop a deployment"""
    manager = AssemblyManager(db)

    try:
        manager.stop_deployment(deployment_id)
        console.print(f"[green]✓[/green] Stopped deployment: {deployment_id}")
    except Exception as e:
        console.print(f"[red]✗[/red] {str(e)}")


@assembly_cli.command(name='deployments')
@click.option('--assembly-id', help='Filter by assembly ID')
@click.option('--status', type=click.Choice(['deploying', 'running', 'degraded', 'stopped', 'failed']),
              help='Filter by status')
@click.option('--limit', type=int, default=20, help='Maximum results')
@click.option('--db', default='assembly.db', help='Database path')
def list_deployments(assembly_id, status, limit, db):
    """List deployments"""
    manager = AssemblyManager(db)
    deployments = manager.list_deployments(assembly_id=assembly_id, status=status, limit=limit)

    if not deployments:
        console.print("[yellow]No deployments found[/yellow]")
        return

    table = Table(title=f"Deployments ({len(deployments)})")
    table.add_column("Deployment ID", style="cyan")
    table.add_column("Assembly ID", style="blue")
    table.add_column("Node ID", style="magenta")
    table.add_column("LD Address", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Health", style="white")
    table.add_column("Deployed", style="dim")

    for deployment in deployments:
        status_color = {
            "deploying": "blue",
            "running": "green",
            "degraded": "yellow",
            "stopped": "dim",
            "failed": "red"
        }.get(deployment.status, "white")

        health_status = deployment.health.get("status", "unknown") if deployment.health else "unknown"
        health_icon = {"healthy": "✓", "unhealthy": "✗", "unknown": "?"}.get(health_status, "?")

        table.add_row(
            deployment.deployment_id[:16] + "...",
            deployment.assembly_id[:12] + "...",
            deployment.node_id[:12] + "...",
            deployment.ld_address or "N/A",
            f"[{status_color}]{deployment.status}[/{status_color}]",
            f"{health_icon} {health_status}",
            deployment.deployed_at[:19]
        )

    console.print(table)


def register_cli(cli_group):
    """Register assembly commands with main CLI"""
    cli_group.add_command(stack_cli)
    cli_group.add_command(assembly_cli)
