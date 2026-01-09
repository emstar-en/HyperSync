"""
CI/CD Pipeline CLI
"""
import click
from hypersync.cicd.pipeline_manager import PipelineManager


@click.group()
def pipelines():
    """Manage CI/CD pipelines."""
    pass


@pipelines.command()
@click.argument('pipeline_id')
def run(pipeline_id):
    """Run a pipeline."""
    click.echo(f"Running pipeline: {pipeline_id}")


@pipelines.command()
def list():
    """List available pipelines."""
    click.echo("Available pipelines: build, test, deploy")
