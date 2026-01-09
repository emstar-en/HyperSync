"""
HyperSync CI/CD CLI

Command-line interface for CI/CD pipeline management.
"""

import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from .pipeline_manager import PipelineManager
from .gold_sample_manager import GoldSampleManager
from .pipeline_executor import PipelineExecutor

console = Console()


@click.group()
def cicd():
    """HyperSync CI/CD Pipeline Management"""
    pass


# Pipeline Commands
@cicd.group()
def pipeline():
    """Manage CI/CD pipelines"""
    pass


@pipeline.command('create')
@click.argument('definition_file', type=click.Path(exists=True))
def pipeline_create(definition_file):
    """Create a new pipeline from definition file"""
    with open(definition_file, 'r') as f:
        definition = json.load(f)

    manager = PipelineManager()
    pipeline_id = manager.create_pipeline(definition)

    console.print(f"✅ Created pipeline: [bold green]{pipeline_id}[/bold green]")
    console.print(f"   Name: {definition['name']}")
    console.print(f"   Version: {definition['version']}")


@pipeline.command('list')
def pipeline_list():
    """List all pipelines"""
    manager = PipelineManager()
    pipelines = manager.list_pipelines()

    if not pipelines:
        console.print("No pipelines found")
        return

    table = Table(title="CI/CD Pipelines")
    table.add_column("Pipeline ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Created", style="magenta")

    for p in pipelines:
        table.add_row(
            p['pipeline_id'][:8] + "...",
            p['name'],
            p['version'],
            p['created_at']
        )

    console.print(table)


@pipeline.command('show')
@click.argument('pipeline_id')
def pipeline_show(pipeline_id):
    """Show pipeline details"""
    manager = PipelineManager()
    pipeline = manager.get_pipeline(pipeline_id)

    if not pipeline:
        console.print(f"❌ Pipeline not found: {pipeline_id}", style="bold red")
        return

    console.print(Panel.fit(
        f"[bold]{pipeline['name']}[/bold] v{pipeline['version']}\n"
        f"ID: {pipeline['pipeline_id']}\n"
        f"Description: {pipeline.get('description', 'N/A')}\n"
        f"Stages: {len(pipeline['stages'])}",
        title="Pipeline Details"
    ))

    # Show stages
    table = Table(title="Stages")
    table.add_column("Stage", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Steps", style="yellow")

    for stage in pipeline['stages']:
        table.add_row(
            stage['name'],
            stage['type'],
            str(len(stage['steps']))
        )

    console.print(table)


@pipeline.command('run')
@click.argument('pipeline_id')
@click.option('--trigger', default='manual', help='Trigger type')
@click.option('--source', default='cli', help='Trigger source')
def pipeline_run(pipeline_id, trigger, source):
    """Execute a pipeline"""
    manager = PipelineManager()
    gold_manager = GoldSampleManager()
    executor = PipelineExecutor(manager, gold_manager)

    console.print(f"🚀 Starting pipeline execution: {pipeline_id}")

    try:
        result = executor.execute_pipeline(pipeline_id, trigger, source)

        if result['status'] == 'success':
            console.print(f"✅ Pipeline completed successfully", style="bold green")
        else:
            console.print(f"❌ Pipeline failed", style="bold red")

        console.print(f"   Run ID: {result['run_id']}")
        console.print(f"   Duration: {result.get('duration_seconds', 0):.2f}s")

    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="bold red")


@pipeline.command('delete')
@click.argument('pipeline_id')
@click.confirmation_option(prompt='Are you sure you want to delete this pipeline?')
def pipeline_delete(pipeline_id):
    """Delete a pipeline"""
    manager = PipelineManager()
    manager.delete_pipeline(pipeline_id)
    console.print(f"✅ Deleted pipeline: {pipeline_id}")


# Run Commands
@cicd.group()
def run():
    """Manage pipeline runs"""
    pass


@run.command('list')
@click.option('--pipeline', help='Filter by pipeline ID')
@click.option('--limit', default=20, help='Number of runs to show')
def run_list(pipeline, limit):
    """List pipeline runs"""
    manager = PipelineManager()
    runs = manager.list_runs(pipeline, limit)

    if not runs:
        console.print("No runs found")
        return

    table = Table(title="Pipeline Runs")
    table.add_column("Run ID", style="cyan")
    table.add_column("Pipeline", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Started", style="magenta")
    table.add_column("Duration", style="blue")

    for r in runs:
        status_style = "green" if r['status'] == 'success' else "red"
        duration = f"{r.get('duration_seconds', 0):.1f}s" if r.get('duration_seconds') else "N/A"

        table.add_row(
            r['run_id'][:8] + "...",
            r['pipeline_id'][:8] + "...",
            f"[{status_style}]{r['status']}[/{status_style}]",
            r['started_at'],
            duration
        )

    console.print(table)


@run.command('show')
@click.argument('run_id')
def run_show(run_id):
    """Show run details"""
    manager = PipelineManager()
    run = manager.get_run(run_id)

    if not run:
        console.print(f"❌ Run not found: {run_id}", style="bold red")
        return

    status_style = "green" if run['status'] == 'success' else "red"

    console.print(Panel.fit(
        f"Run ID: {run['run_id']}\n"
        f"Pipeline: {run['pipeline_id']}\n"
        f"Status: [{status_style}]{run['status']}[/{status_style}]\n"
        f"Started: {run['started_at']}\n"
        f"Duration: {run.get('duration_seconds', 0):.2f}s",
        title="Run Details"
    ))

    # Show artifacts
    artifacts = manager.get_artifacts(run_id)
    if artifacts:
        table = Table(title="Artifacts")
        table.add_column("Name", style="cyan")
        table.add_column("Stage", style="green")
        table.add_column("Size", style="yellow")

        for artifact in artifacts:
            size_mb = artifact['size_bytes'] / (1024 * 1024)
            table.add_row(
                artifact['name'],
                artifact.get('stage_name', 'N/A'),
                f"{size_mb:.2f} MB"
            )

        console.print(table)


# Gold Sample Commands
@cicd.group()
def gold():
    """Manage gold samples"""
    pass


@gold.command('create')
@click.argument('pipeline_id')
@click.argument('stage')
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--step', help='Step name')
@click.option('--version', help='Version')
def gold_create(pipeline_id, stage, data_file, step, version):
    """Create a new gold sample"""
    with open(data_file, 'r') as f:
        data = json.load(f)

    manager = GoldSampleManager()
    sample_id = manager.create_sample(
        pipeline_id, stage, data, step=step, version=version
    )

    console.print(f"✅ Created gold sample: [bold green]{sample_id}[/bold green]")


@gold.command('list')
@click.option('--pipeline', help='Filter by pipeline ID')
@click.option('--stage', help='Filter by stage')
@click.option('--version', help='Filter by version')
def gold_list(pipeline, stage, version):
    """List gold samples"""
    manager = GoldSampleManager()
    samples = manager.list_samples(pipeline, stage, version)

    if not samples:
        console.print("No gold samples found")
        return

    table = Table(title="Gold Samples")
    table.add_column("Sample ID", style="cyan")
    table.add_column("Pipeline", style="green")
    table.add_column("Stage", style="yellow")
    table.add_column("Version", style="magenta")
    table.add_column("Created", style="blue")

    for s in samples:
        table.add_row(
            s['sample_id'][:8] + "...",
            s['pipeline_id'][:8] + "...",
            s['stage'],
            s.get('version', 'N/A'),
            s['timestamp']
        )

    console.print(table)


@gold.command('show')
@click.argument('sample_id')
def gold_show(sample_id):
    """Show gold sample details"""
    manager = GoldSampleManager()
    sample = manager.get_sample(sample_id)

    if not sample:
        console.print(f"❌ Sample not found: {sample_id}", style="bold red")
        return

    console.print(Panel.fit(
        f"Sample ID: {sample['sample_id']}\n"
        f"Pipeline: {sample['pipeline_id']}\n"
        f"Stage: {sample['stage']}\n"
        f"Step: {sample.get('step', 'N/A')}\n"
        f"Version: {sample.get('version', 'N/A')}\n"
        f"Created: {sample['timestamp']}",
        title="Gold Sample Details"
    ))

    # Show validation history
    history = manager.get_validation_history(sample_id)
    if history:
        table = Table(title="Validation History")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Score", style="yellow")
        table.add_column("Passed", style="green")

        for v in history[:10]:  # Show last 10
            passed_icon = "✅" if v['passed'] else "❌"
            table.add_row(
                v['timestamp'],
                f"{v['similarity_score']:.3f}",
                passed_icon
            )

        console.print(table)


@gold.command('validate')
@click.argument('sample_id')
@click.argument('test_data_file', type=click.Path(exists=True))
@click.option('--method', default='fuzzy', help='Comparison method')
@click.option('--threshold', default=0.95, help='Similarity threshold')
def gold_validate(sample_id, test_data_file, method, threshold):
    """Validate test data against a gold sample"""
    with open(test_data_file, 'r') as f:
        test_data = json.load(f)

    manager = GoldSampleManager()
    passed, score, differences = manager.validate_against_sample(
        sample_id, test_data, comparison_method=method, threshold=threshold
    )

    if passed:
        console.print(f"✅ Validation PASSED", style="bold green")
    else:
        console.print(f"❌ Validation FAILED", style="bold red")

    console.print(f"   Similarity Score: {score:.3f}")
    console.print(f"   Threshold: {threshold}")

    if differences:
        console.print(f"\n   Differences found: {len(differences)}")
        for key, diff in list(differences.items())[:5]:  # Show first 5
            console.print(f"     • {key}: {diff}")


@gold.command('cleanup')
@click.option('--max-age', default=365, help='Max age in days')
@click.option('--max-samples', default=100, help='Max samples per pipeline')
def gold_cleanup(max_age, max_samples):
    """Clean up old gold samples"""
    manager = GoldSampleManager()
    manager.cleanup_old_samples(max_age, max_samples)
    console.print(f"✅ Cleaned up old gold samples")


if __name__ == '__main__':
    cicd()
