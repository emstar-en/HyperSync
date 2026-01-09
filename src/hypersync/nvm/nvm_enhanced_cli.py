#!/usr/bin/env python3
"""
HyperSync NVM Enhanced CLI

Comprehensive CLI for NVM block management with hyperbolic embedding,
assignments, directory management, and preloading capabilities.
"""

import os
import sys
import json
import click
from pathlib import Path
from rich import print as rprint
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON
from rich.console import Console

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nvm.nvm_schema_manager import (
    NVMSchemaManager,
    NVMBlockSchema,
    NVMBlockClass,
    NVMAssignmentType,
    NVMAccessMode,
    NVMGeometryConfig,
    NVMIndexConfig,
    NVMCodebookConfig,
)

console = Console()


def get_manager() -> NVMSchemaManager:
    """Get NVM schema manager instance"""
    storage_path = Path(os.environ.get('NVM_STORAGE_PATH', './nvm_storage'))
    return NVMSchemaManager(storage_path)


@click.group()
def nvm_cli():
    """HyperSync NVM Block Management CLI"""
    pass


@nvm_cli.command('create')
@click.option('--block-id', required=True, help='Unique block identifier (e.g., nvm://docs/hypersync)')
@click.option('--name', required=True, help='Human-readable name')
@click.option('--description', required=True, help='Block description')
@click.option('--class', 'block_class', 
              type=click.Choice([c.value for c in NVMBlockClass]),
              default='documentation', help='Block classification')
@click.option('--geometry', type=click.Choice(['euclidean', 'spherical', 'poincare_ball', 'hyperboloid', 'spd_logeuclid']),
              default='poincare_ball', help='Hyperbolic geometry space')
@click.option('--curvature', type=float, default=-1.0, help='Curvature for hyperbolic spaces')
@click.option('--dimension', type=int, default=768, help='Vector dimensionality')
@click.option('--index-type', type=click.Choice(['hnsw_euclidean', 'hnsw_hyperbolic', 'ivfpq', 'bruteforce']),
              default='hnsw_hyperbolic', help='Index type')
@click.option('--max-vectors', type=int, default=None, help='Maximum number of vectors')
@click.option('--max-size-mb', type=int, default=None, help='Maximum size in MB')
@click.option('--retention-days', type=int, default=None, help='Retention period in days')
def create_block(block_id, name, description, block_class, geometry, curvature, dimension, 
                 index_type, max_vectors, max_size_mb, retention_days):
    """Create a new NVM block with hyperbolic embedding"""

    manager = get_manager()

    geometry_config = NVMGeometryConfig(
        space=geometry,
        curvature=curvature,
        dimension=dimension
    )

    index_config = NVMIndexConfig(
        index_type=index_type
    )

    codebook_config = NVMCodebookConfig(
        method="opq"
    )

    try:
        block = manager.create_block(
            block_id=block_id,
            name=name,
            description=description,
            block_class=NVMBlockClass(block_class),
            geometry=geometry_config,
            index=index_config,
            codebook=codebook_config,
            max_vectors=max_vectors,
            max_size_mb=max_size_mb,
            retention_days=retention_days
        )

        rprint(Panel.fit(
            f"[green]✓[/green] Created NVM block: [cyan]{block_id}[/cyan]\n"
            f"Name: {name}\n"
            f"Class: {block_class}\n"
            f"Geometry: {geometry} (dim={dimension}, κ={curvature})\n"
            f"Index: {index_type}",
            title="NVM Block Created",
            border_style="green"
        ))

        rprint(JSON(json.dumps(block.to_dict(), indent=2)))

    except Exception as e:
        rprint(f"[red]✗ Error creating block: {e}[/red]")
        sys.exit(1)


@nvm_cli.command('assign')
@click.option('--block-id', required=True, help='Block identifier')
@click.option('--type', 'assignment_type',
              type=click.Choice([t.value for t in NVMAssignmentType]),
              required=True, help='Assignment type')
@click.option('--target-id', required=True, help='Target entity ID')
@click.option('--target-name', default=None, help='Target entity name')
@click.option('--access-mode',
              type=click.Choice([m.value for m in NVMAccessMode]),
              default='read_write', help='Access mode')
@click.option('--priority', type=int, default=0, help='Assignment priority')
def assign_block(block_id, assignment_type, target_id, target_name, access_mode, priority):
    """Assign NVM block to a model, stack, network, or group"""

    manager = get_manager()

    try:
        assignment = manager.assign_block(
            block_id=block_id,
            assignment_type=NVMAssignmentType(assignment_type),
            target_id=target_id,
            target_name=target_name,
            access_mode=NVMAccessMode(access_mode),
            priority=priority
        )

        rprint(Panel.fit(
            f"[green]✓[/green] Assigned block to {assignment_type}\n"
            f"Block: [cyan]{block_id}[/cyan]\n"
            f"Target: {target_id} ({target_name or 'unnamed'})\n"
            f"Access: {access_mode}\n"
            f"Priority: {priority}",
            title="Assignment Created",
            border_style="green"
        ))

    except Exception as e:
        rprint(f"[red]✗ Error creating assignment: {e}[/red]")
        sys.exit(1)


@nvm_cli.command('add-directory')
@click.option('--block-id', required=True, help='Block identifier')
@click.option('--directory-id', required=True, help='Directory identifier')
@click.option('--path', required=True, help='Directory path')
@click.option('--purpose', required=True, help='Directory purpose')
@click.option('--max-size-mb', type=int, default=None, help='Maximum size in MB')
@click.option('--extensions', multiple=True, help='Allowed file extensions')
@click.option('--auto-embed/--no-auto-embed', default=True, help='Auto-embed files')
@click.option('--watch/--no-watch', default=False, help='Watch for changes')
def add_directory(block_id, directory_id, path, purpose, max_size_mb, extensions, auto_embed, watch):
    """Add directory to NVM block for file management"""

    manager = get_manager()

    try:
        directory = manager.add_directory(
            block_id=block_id,
            directory_id=directory_id,
            path=path,
            purpose=purpose,
            max_size_mb=max_size_mb,
            allowed_extensions=list(extensions) if extensions else [],
            auto_embed=auto_embed,
            watch_changes=watch
        )

        rprint(Panel.fit(
            f"[green]✓[/green] Added directory to block\n"
            f"Block: [cyan]{block_id}[/cyan]\n"
            f"Directory: {directory_id}\n"
            f"Path: {path}\n"
            f"Purpose: {purpose}\n"
            f"Auto-embed: {auto_embed}",
            title="Directory Added",
            border_style="green"
        ))

    except Exception as e:
        rprint(f"[red]✗ Error adding directory: {e}[/red]")
        sys.exit(1)


@nvm_cli.command('add-preload')
@click.option('--block-id', required=True, help='Block identifier')
@click.option('--preload-id', required=True, help='Preload identifier')
@click.option('--source-type', 
              type=click.Choice(['file', 'directory', 'url', 'inline']),
              required=True, help='Source type')
@click.option('--source-path', default=None, help='Source path (for file/directory/url)')
@click.option('--content', default=None, help='Inline content')
@click.option('--content-type', default='text/markdown', help='Content MIME type')
@click.option('--chunk-size', type=int, default=512, help='Chunk size for embedding')
@click.option('--overlap', type=int, default=50, help='Chunk overlap')
def add_preload(block_id, preload_id, source_type, source_path, content, content_type, chunk_size, overlap):
    """Add preload configuration to NVM block"""

    manager = get_manager()

    if source_type != 'inline' and not source_path:
        rprint("[red]✗ --source-path required for non-inline sources[/red]")
        sys.exit(1)

    if source_type == 'inline' and not content:
        rprint("[red]✗ --content required for inline sources[/red]")
        sys.exit(1)

    try:
        preload = manager.add_preload(
            block_id=block_id,
            preload_id=preload_id,
            source_type=source_type,
            source_path=source_path,
            content=content,
            content_type=content_type,
            chunk_size=chunk_size,
            overlap=overlap
        )

        rprint(Panel.fit(
            f"[green]✓[/green] Added preload configuration\n"
            f"Block: [cyan]{block_id}[/cyan]\n"
            f"Preload: {preload_id}\n"
            f"Source: {source_type}\n"
            f"Path: {source_path or 'inline'}\n"
            f"Chunk size: {chunk_size}",
            title="Preload Added",
            border_style="green"
        ))

    except Exception as e:
        rprint(f"[red]✗ Error adding preload: {e}[/red]")
        sys.exit(1)


@nvm_cli.command('list')
@click.option('--class', 'block_class',
              type=click.Choice([c.value for c in NVMBlockClass]),
              default=None, help='Filter by block class')
@click.option('--assignment-type',
              type=click.Choice([t.value for t in NVMAssignmentType]),
              default=None, help='Filter by assignment type')
@click.option('--target-id', default=None, help='Filter by target ID')
@click.option('--json-output', is_flag=True, help='Output as JSON')
def list_blocks(block_class, assignment_type, target_id, json_output):
    """List NVM blocks with optional filtering"""

    manager = get_manager()

    try:
        blocks = manager.list_blocks(
            block_class=NVMBlockClass(block_class) if block_class else None,
            assignment_type=NVMAssignmentType(assignment_type) if assignment_type else None,
            target_id=target_id
        )

        if json_output:
            output = [block.to_dict() for block in blocks]
            print(json.dumps(output, indent=2))
            return

        if not blocks:
            rprint("[yellow]No blocks found[/yellow]")
            return

        table = Table(title=f"NVM Blocks ({len(blocks)} found)")
        table.add_column("Block ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Class", style="yellow")
        table.add_column("Geometry", style="magenta")
        table.add_column("Assignments", style="green")
        table.add_column("Directories", style="blue")
        table.add_column("Preloads", style="red")

        for block in blocks:
            table.add_row(
                block.block_id,
                block.name,
                block.block_class.value,
                f"{block.geometry.space} (d={block.geometry.dimension})",
                str(len(block.assignments)),
                str(len(block.directories)),
                str(len(block.preloads))
            )

        console.print(table)

    except Exception as e:
        rprint(f"[red]✗ Error listing blocks: {e}[/red]")
        sys.exit(1)


@nvm_cli.command('get')
@click.argument('block_id')
@click.option('--json-output', is_flag=True, help='Output as JSON')
def get_block(block_id, json_output):
    """Get detailed information about an NVM block"""

    manager = get_manager()

    try:
        block = manager.get_block(block_id)

        if not block:
            rprint(f"[red]✗ Block not found: {block_id}[/red]")
            sys.exit(1)

        if json_output:
            print(json.dumps(block.to_dict(), indent=2))
            return

        # Display block information
        rprint(Panel.fit(
            f"[cyan]{block.block_id}[/cyan]\n"
            f"Name: {block.name}\n"
            f"Class: {block.block_class.value}\n"
            f"Description: {block.description}",
            title="NVM Block Details",
            border_style="cyan"
        ))

        # Geometry
        rprint("\n[bold]Geometry Configuration:[/bold]")
        geo_table = Table(show_header=False, box=None)
        geo_table.add_row("Space:", block.geometry.space)
        geo_table.add_row("Dimension:", str(block.geometry.dimension))
        geo_table.add_row("Curvature:", str(block.geometry.curvature))
        geo_table.add_row("Radius Cap:", str(block.geometry.radius_cap))
        console.print(geo_table)

        # Assignments
        if block.assignments:
            rprint("\n[bold]Assignments:[/bold]")
            assign_table = Table()
            assign_table.add_column("Type", style="yellow")
            assign_table.add_column("Target ID", style="cyan")
            assign_table.add_column("Access", style="green")
            assign_table.add_column("Priority", style="magenta")

            for assignment in block.assignments:
                assign_table.add_row(
                    assignment.assignment_type.value,
                    assignment.target_id,
                    assignment.access_mode.value,
                    str(assignment.priority)
                )

            console.print(assign_table)

        # Directories
        if block.directories:
            rprint("\n[bold]Directories:[/bold]")
            dir_table = Table()
            dir_table.add_column("ID", style="cyan")
            dir_table.add_column("Path", style="white")
            dir_table.add_column("Purpose", style="yellow")
            dir_table.add_column("Auto-embed", style="green")

            for directory in block.directories:
                dir_table.add_row(
                    directory.directory_id,
                    directory.path,
                    directory.purpose,
                    "✓" if directory.auto_embed else "✗"
                )

            console.print(dir_table)

        # Preloads
        if block.preloads:
            rprint("\n[bold]Preloads:[/bold]")
            preload_table = Table()
            preload_table.add_column("ID", style="cyan")
            preload_table.add_column("Source Type", style="yellow")
            preload_table.add_column("Source", style="white")
            preload_table.add_column("Chunk Size", style="magenta")

            for preload in block.preloads:
                preload_table.add_row(
                    preload.preload_id,
                    preload.source_type,
                    preload.source_path or "inline",
                    str(preload.chunk_size)
                )

            console.print(preload_table)

    except Exception as e:
        rprint(f"[red]✗ Error getting block: {e}[/red]")
        sys.exit(1)


@nvm_cli.command('delete')
@click.argument('block_id')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def delete_block(block_id, confirm):
    """Delete an NVM block"""

    manager = get_manager()

    if not confirm:
        response = click.prompt(
            f"Are you sure you want to delete block '{block_id}'? (yes/no)",
            type=str
        )
        if response.lower() != 'yes':
            rprint("[yellow]Deletion cancelled[/yellow]")
            return

    try:
        success = manager.delete_block(block_id)

        if success:
            rprint(f"[green]✓ Deleted block: {block_id}[/green]")
        else:
            rprint(f"[red]✗ Block not found: {block_id}[/red]")
            sys.exit(1)

    except Exception as e:
        rprint(f"[red]✗ Error deleting block: {e}[/red]")
        sys.exit(1)


@nvm_cli.command('create-preset')
@click.option('--preset', 
              type=click.Choice(['hypersync_docs', 'model_cache', 'training_data', 'logs']),
              required=True, help='Preset configuration')
@click.option('--target-id', required=True, help='Target entity ID (e.g., model://assistant/v1)')
@click.option('--target-name', default=None, help='Target entity name')
def create_preset(preset, target_id, target_name):
    """Create NVM block from preset configuration"""

    manager = get_manager()

    presets = {
        'hypersync_docs': {
            'block_id': f'nvm://docs/hypersync/{target_id.split("/")[-1]}',
            'name': 'HyperSync Documentation',
            'description': 'Preloaded HyperSync documentation for assistant model',
            'block_class': NVMBlockClass.DOCUMENTATION,
            'preloads': [
                {
                    'preload_id': 'hypersync_readme',
                    'source_type': 'directory',
                    'source_path': './docs',
                    'content_type': 'text/markdown'
                }
            ]
        },
        'model_cache': {
            'block_id': f'nvm://cache/{target_id.split("/")[-1]}',
            'name': 'Model Cache',
            'description': 'Hyperbolic cache for model computations',
            'block_class': NVMBlockClass.CACHE,
            'max_vectors': 100000,
            'retention_days': 7
        },
        'training_data': {
            'block_id': f'nvm://training/{target_id.split("/")[-1]}',
            'name': 'Training Data',
            'description': 'Training data with hyperbolic embeddings',
            'block_class': NVMBlockClass.TRAINING_DATA,
            'max_size_mb': 10240
        },
        'logs': {
            'block_id': f'nvm://logs/{target_id.split("/")[-1]}',
            'name': 'Operation Logs',
            'description': 'Operational logs and telemetry',
            'block_class': NVMBlockClass.LOGS,
            'retention_days': 30
        }
    }

    config = presets[preset]

    try:
        # Create block
        block = manager.create_block(
            block_id=config['block_id'],
            name=config['name'],
            description=config['description'],
            block_class=config['block_class'],
            max_vectors=config.get('max_vectors'),
            max_size_mb=config.get('max_size_mb'),
            retention_days=config.get('retention_days')
        )

        # Assign to target
        manager.assign_block(
            block_id=config['block_id'],
            assignment_type=NVMAssignmentType.MODEL,
            target_id=target_id,
            target_name=target_name,
            access_mode=NVMAccessMode.READ_WRITE
        )

        # Add preloads if specified
        for preload_config in config.get('preloads', []):
            manager.add_preload(
                block_id=config['block_id'],
                **preload_config
            )

        rprint(Panel.fit(
            f"[green]✓[/green] Created preset NVM block\n"
            f"Preset: [cyan]{preset}[/cyan]\n"
            f"Block: {config['block_id']}\n"
            f"Assigned to: {target_id}",
            title="Preset Created",
            border_style="green"
        ))

    except Exception as e:
        rprint(f"[red]✗ Error creating preset: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    nvm_cli()
