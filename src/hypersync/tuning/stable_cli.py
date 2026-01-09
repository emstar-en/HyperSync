"""
Tuning Stable CLI

Command-line interface for managing tuning stables.
"""

import click
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime
from typing import Optional

from .stable_manager import TuningStableManager

console = Console()


@click.group(name='stable')
def stable_cli():
    """Manage tuning stables for continuous model tuning"""
    pass


@stable_cli.command(name='create')
@click.option('--name', required=True, help='Stable name')
@click.option('--model-id', required=True, help='Base model ID from catalogue')
@click.option('--description', help='Stable description')
@click.option('--method', type=click.Choice(['lora', 'qlora', 'full_finetune', 'prefix_tuning', 'adapter', 'ia3']), 
              default='lora', help='Tuning method')
@click.option('--learning-rate', type=float, default=2e-4, help='Learning rate')
@click.option('--batch-size', type=int, default=4, help='Batch size')
@click.option('--epochs', type=int, default=3, help='Number of epochs')
@click.option('--lora-r', type=int, default=8, help='LoRA rank')
@click.option('--lora-alpha', type=int, default=16, help='LoRA alpha')
@click.option('--gold-suite', help='Gold sample suite ID for validation')
@click.option('--pipeline-id', help='CI/CD pipeline ID for integration')
@click.option('--tags', multiple=True, help='Tags for the stable')
@click.option('--db', default='tuning_stables.db', help='Database path')
def create_stable(name, model_id, description, method, learning_rate, batch_size, 
                  epochs, lora_r, lora_alpha, gold_suite, pipeline_id, tags, db):
    """Create a new tuning stable"""
    manager = TuningStableManager(db)

    base_model = {
        "model_id": model_id,
        "catalogue_entry": model_id
    }

    tuning_config = {
        "method": method,
        "hyperparameters": {
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "epochs": epochs,
            "lora_r": lora_r,
            "lora_alpha": lora_alpha,
            "lora_dropout": 0.05
        },
        "target_modules": ["q_proj", "v_proj"],
        "optimization": {
            "optimizer": "adamw",
            "scheduler": "cosine",
            "gradient_accumulation_steps": 4,
            "max_grad_norm": 1.0
        }
    }

    validation_config = None
    if gold_suite:
        validation_config = {
            "gold_sample_suite": gold_suite,
            "validation_frequency": "every_epoch",
            "quality_gates": {
                "min_gold_sample_pass_rate": 0.8,
                "max_regression_tolerance": 0.05
            }
        }

    cicd_integration = None
    if pipeline_id:
        cicd_integration = {
            "pipeline_id": pipeline_id,
            "auto_trigger": False,
            "trigger_on": ["quality_gate_pass"]
        }

    stable = manager.create_stable(
        name=name,
        base_model=base_model,
        description=description,
        tuning_config=tuning_config,
        validation_config=validation_config,
        cicd_integration=cicd_integration,
        tags=list(tags) if tags else None
    )

    console.print(Panel.fit(
        f"[green]✓[/green] Created tuning stable\n\n"
        f"[cyan]ID:[/cyan] {stable.stable_id}\n"
        f"[cyan]Name:[/cyan] {stable.name}\n"
        f"[cyan]Base Model:[/cyan] {model_id}\n"
        f"[cyan]Method:[/cyan] {method}\n"
        f"[cyan]Status:[/cyan] {stable.status}",
        title="Tuning Stable Created",
        border_style="green"
    ))


@stable_cli.command(name='list')
@click.option('--status', type=click.Choice(['idle', 'running', 'paused', 'completed', 'failed']), 
              help='Filter by status')
@click.option('--tags', multiple=True, help='Filter by tags')
@click.option('--limit', type=int, default=20, help='Maximum number of results')
@click.option('--db', default='tuning_stables.db', help='Database path')
def list_stables(status, tags, limit, db):
    """List tuning stables"""
    manager = TuningStableManager(db)
    stables = manager.list_stables(status=status, tags=list(tags) if tags else None, limit=limit)

    if not stables:
        console.print("[yellow]No stables found[/yellow]")
        return

    table = Table(title=f"Tuning Stables ({len(stables)})")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Base Model", style="blue")
    table.add_column("Method", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Current Run", style="yellow")
    table.add_column("Created", style="dim")

    for stable in stables:
        status_color = {
            "idle": "white",
            "running": "green",
            "paused": "yellow",
            "completed": "blue",
            "failed": "red"
        }.get(stable.status, "white")

        table.add_row(
            stable.stable_id[:16] + "...",
            stable.name,
            stable.base_model.get("model_id", "N/A")[:20],
            stable.tuning_config.get("method", "N/A") if stable.tuning_config else "N/A",
            f"[{status_color}]{stable.status}[/{status_color}]",
            stable.current_run[:12] + "..." if stable.current_run else "-",
            stable.created_at[:10]
        )

    console.print(table)


@stable_cli.command(name='info')
@click.argument('stable_id')
@click.option('--db', default='tuning_stables.db', help='Database path')
def stable_info(stable_id, db):
    """Show detailed information about a stable"""
    manager = TuningStableManager(db)
    stable = manager.get_stable(stable_id)

    if not stable:
        console.print(f"[red]✗[/red] Stable not found: {stable_id}")
        return

    # Basic info
    info = f"""[cyan]Stable ID:[/cyan] {stable.stable_id}
[cyan]Name:[/cyan] {stable.name}
[cyan]Description:[/cyan] {stable.description or 'N/A'}
[cyan]Status:[/cyan] {stable.status}
[cyan]Created:[/cyan] {stable.created_at}
[cyan]Updated:[/cyan] {stable.updated_at or 'N/A'}

[yellow]Base Model:[/yellow]
  Model ID: {stable.base_model.get('model_id', 'N/A')}
  Catalogue Entry: {stable.base_model.get('catalogue_entry', 'N/A')}
"""

    # Tuning config
    if stable.tuning_config:
        tc = stable.tuning_config
        info += f"""
[yellow]Tuning Configuration:[/yellow]
  Method: {tc.get('method', 'N/A')}
  Learning Rate: {tc.get('hyperparameters', {}).get('learning_rate', 'N/A')}
  Batch Size: {tc.get('hyperparameters', {}).get('batch_size', 'N/A')}
  Epochs: {tc.get('hyperparameters', {}).get('epochs', 'N/A')}
  LoRA Rank: {tc.get('hyperparameters', {}).get('lora_r', 'N/A')}
"""

    # Validation config
    if stable.validation_config:
        vc = stable.validation_config
        info += f"""
[yellow]Validation:[/yellow]
  Gold Suite: {vc.get('gold_sample_suite', 'N/A')}
  Frequency: {vc.get('validation_frequency', 'N/A')}
  Min Pass Rate: {vc.get('quality_gates', {}).get('min_gold_sample_pass_rate', 'N/A')}
"""

    # CI/CD integration
    if stable.cicd_integration:
        ci = stable.cicd_integration
        info += f"""
[yellow]CI/CD Integration:[/yellow]
  Pipeline ID: {ci.get('pipeline_id', 'N/A')}
  Auto Trigger: {ci.get('auto_trigger', False)}
"""

    # Current run
    if stable.current_run:
        info += f"""
[yellow]Current Run:[/yellow] {stable.current_run}
"""

    # Tags
    if stable.tags:
        info += f"""
[yellow]Tags:[/yellow] {', '.join(stable.tags)}
"""

    console.print(Panel(info, title="Tuning Stable Details", border_style="cyan"))

    # Show recent runs
    runs = manager.list_runs(stable_id=stable_id, limit=5)
    if runs:
        console.print("\n[yellow]Recent Runs:[/yellow]")
        table = Table()
        table.add_column("Run ID", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Started", style="dim")
        table.add_column("Completed", style="dim")
        table.add_column("Progress", style="yellow")

        for run in runs:
            progress = run.progress or {}
            progress_str = f"{progress.get('percent_complete', 0):.1f}%"

            table.add_row(
                run.run_id[:16] + "...",
                run.status,
                run.started_at[:19],
                run.completed_at[:19] if run.completed_at else "-",
                progress_str
            )

        console.print(table)


@stable_cli.command(name='start')
@click.argument('stable_id')
@click.option('--db', default='tuning_stables.db', help='Database path')
def start_run(stable_id, db):
    """Start a tuning run"""
    manager = TuningStableManager(db)

    try:
        run = manager.start_run(stable_id)

        console.print(Panel.fit(
            f"[green]✓[/green] Started tuning run\n\n"
            f"[cyan]Run ID:[/cyan] {run.run_id}\n"
            f"[cyan]Stable:[/cyan] {stable_id}\n"
            f"[cyan]Status:[/cyan] {run.status}\n"
            f"[cyan]Started:[/cyan] {run.started_at}",
            title="Tuning Run Started",
            border_style="green"
        ))

        console.print("\n[dim]Note: This starts the run record. Actual training must be executed separately.[/dim]")

    except ValueError as e:
        console.print(f"[red]✗[/red] {str(e)}")


@stable_cli.command(name='runs')
@click.option('--stable-id', help='Filter by stable ID')
@click.option('--status', type=click.Choice(['initializing', 'running', 'validating', 'completed', 'failed', 'stopped']), 
              help='Filter by status')
@click.option('--limit', type=int, default=20, help='Maximum number of results')
@click.option('--db', default='tuning_stables.db', help='Database path')
def list_runs(stable_id, status, limit, db):
    """List tuning runs"""
    manager = TuningStableManager(db)
    runs = manager.list_runs(stable_id=stable_id, status=status, limit=limit)

    if not runs:
        console.print("[yellow]No runs found[/yellow]")
        return

    table = Table(title=f"Tuning Runs ({len(runs)})")
    table.add_column("Run ID", style="cyan")
    table.add_column("Stable ID", style="blue")
    table.add_column("Status", style="green")
    table.add_column("Progress", style="yellow")
    table.add_column("Started", style="dim")
    table.add_column("Duration", style="dim")

    for run in runs:
        progress = run.progress or {}
        progress_str = f"{progress.get('percent_complete', 0):.1f}%"

        # Calculate duration
        if run.completed_at:
            start = datetime.fromisoformat(run.started_at.replace('Z', '+00:00'))
            end = datetime.fromisoformat(run.completed_at.replace('Z', '+00:00'))
            duration = str(end - start).split('.')[0]
        else:
            duration = "In progress"

        table.add_row(
            run.run_id[:16] + "...",
            run.stable_id[:16] + "...",
            run.status,
            progress_str,
            run.started_at[:19],
            duration
        )

    console.print(table)


@stable_cli.command(name='checkpoints')
@click.option('--stable-id', help='Filter by stable ID')
@click.option('--run-id', help='Filter by run ID')
@click.option('--best-only', is_flag=True, help='Show only best checkpoints')
@click.option('--db', default='tuning_stables.db', help='Database path')
def list_checkpoints(stable_id, run_id, best_only, db):
    """List checkpoints"""
    manager = TuningStableManager(db)
    checkpoints = manager.get_checkpoints(
        stable_id=stable_id,
        run_id=run_id,
        best_only=best_only
    )

    if not checkpoints:
        console.print("[yellow]No checkpoints found[/yellow]")
        return

    table = Table(title=f"Checkpoints ({len(checkpoints)})")
    table.add_column("Checkpoint ID", style="cyan")
    table.add_column("Run ID", style="blue")
    table.add_column("Epoch", style="yellow")
    table.add_column("Step", style="yellow")
    table.add_column("Best", style="green")
    table.add_column("Catalogue", style="magenta")
    table.add_column("Created", style="dim")

    for ckpt in checkpoints:
        table.add_row(
            ckpt['checkpoint_id'][:16] + "...",
            ckpt['run_id'][:12] + "...",
            str(ckpt['epoch']),
            str(ckpt['step']),
            "✓" if ckpt['is_best'] else "",
            ckpt['catalogue_entry'][:16] + "..." if ckpt['catalogue_entry'] else "-",
            ckpt['created_at'][:19]
        )

    console.print(table)


@stable_cli.command(name='delete')
@click.argument('stable_id')
@click.option('--yes', is_flag=True, help='Skip confirmation')
@click.option('--db', default='tuning_stables.db', help='Database path')
def delete_stable(stable_id, yes, db):
    """Delete a tuning stable"""
    manager = TuningStableManager(db)

    stable = manager.get_stable(stable_id)
    if not stable:
        console.print(f"[red]✗[/red] Stable not found: {stable_id}")
        return

    if not yes:
        confirm = click.confirm(f"Delete stable '{stable.name}' ({stable_id}) and all its runs?")
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            return

    manager.delete_stable(stable_id)
    console.print(f"[green]✓[/green] Deleted stable: {stable_id}")


def register_cli(cli_group):
    """Register tuning stable commands with main CLI"""
    cli_group.add_command(stable_cli)
