"""
HyperSync Model Catalogue CLI

Command-line interface for model catalogue operations.
"""

import click
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich import print as rprint

from .model_catalogue_manager import ModelCatalogueManager


console = Console()


@click.group()
@click.option('--db', default='model_catalogue.db', help='Database path')
@click.pass_context
def catalogue(ctx, db):
    """Model Catalogue management commands."""
    ctx.ensure_object(dict)
    ctx.obj['manager'] = ModelCatalogueManager(db)


@catalogue.command()
@click.argument('path')
@click.option('--recursive/--no-recursive', default=True, help='Scan recursively')
@click.option('--auto-tag/--no-auto-tag', default=True, help='Auto-tag models')
@click.pass_context
def scan(ctx, path, recursive, auto_tag):
    """Scan directory or file for models."""
    manager = ctx.obj['manager']

    path_obj = Path(path)

    if path_obj.is_file():
        console.print(f"[cyan]Scanning file: {path}[/cyan]")
        model_id = manager.scan_model(path, auto_tag=auto_tag)
        console.print(f"[green]✓ Added model: {model_id}[/green]")

    elif path_obj.is_dir():
        console.print(f"[cyan]Scanning directory: {path}[/cyan]")
        console.print(f"Recursive: {recursive}")

        with console.status("[bold green]Scanning..."):
            model_ids = manager.scan_directory(path, recursive=recursive)

        console.print(f"[green]✓ Added {len(model_ids)} models[/green]")

        if model_ids:
            table = Table(title="Scanned Models")
            table.add_column("Model ID", style="cyan")

            for mid in model_ids[:10]:
                table.add_row(mid)

            if len(model_ids) > 10:
                table.add_row(f"... and {len(model_ids) - 10} more")

            console.print(table)
    else:
        console.print(f"[red]Error: Path not found: {path}[/red]")


@catalogue.command()
@click.option('--filter', 'filter_str', help='Filter (format:GGUF, family:uuid)')
@click.option('--sort', default='added_date', help='Sort field')
@click.option('--limit', default=50, help='Max results')
@click.pass_context
def list(ctx, filter_str, sort, limit):
    """List catalogued models."""
    manager = ctx.obj['manager']

    # Parse filter
    filter_dict = {}
    if filter_str:
        for item in filter_str.split(','):
            if ':' in item:
                key, value = item.split(':', 1)
                filter_dict[key.strip()] = value.strip()

    models = manager.list_models(filter_dict, sort, limit)

    if not models:
        console.print("[yellow]No models found[/yellow]")
        return

    table = Table(title=f"Model Catalogue ({len(models)} models)")
    table.add_column("Name", style="cyan")
    table.add_column("Format", style="green")
    table.add_column("Size", style="yellow")
    table.add_column("Added", style="magenta")
    table.add_column("ID", style="dim")

    for model in models:
        size_mb = model['size_bytes'] / (1024 * 1024)
        table.add_row(
            model['name'],
            model['format'],
            f"{size_mb:.1f} MB",
            model['added_date'][:10],
            model['model_id'][:8]
        )

    console.print(table)


@catalogue.command()
@click.argument('model_id')
@click.pass_context
def show(ctx, model_id):
    """Show detailed model information."""
    manager = ctx.obj['manager']

    model = manager.get_model(model_id)
    if not model:
        console.print(f"[red]Model not found: {model_id}[/red]")
        return

    console.print(f"\n[bold cyan]Model: {model['name']}[/bold cyan]")
    console.print(f"ID: {model['model_id']}")
    console.print(f"Format: {model['format']}")
    console.print(f"Size: {model['size_bytes'] / (1024**3):.2f} GB")
    console.print(f"Path: {model['path']}")
    console.print(f"Hash: {model['content_hash'][:20]}...")

    console.print(f"\n[bold]Lineage:[/bold]")
    console.print(f"  Family: {model['family_id'][:8]}...")
    console.print(f"  Generation: {model['generation']}")
    if model['parent_id']:
        console.print(f"  Parent: {model['parent_id'][:8]}...")

    if model.get('capabilities'):
        console.print(f"\n[bold]Capabilities:[/bold]")
        for cap in model['capabilities']:
            console.print(f"  • {cap}")

    if model.get('tags'):
        console.print(f"\n[bold]Tags:[/bold] {', '.join(model['tags'])}")

    if model.get('tuning_sessions'):
        console.print(f"\n[bold]Tuning History:[/bold]")
        for session in model['tuning_sessions']:
            console.print(f"  • {session['method']} - {session['timestamp'][:10]}")
            console.print(f"    Samples: {session.get('dataset_size', 'N/A')}")

    if model.get('nld_profile'):
        nld = model['nld_profile']
        console.print(f"\n[bold red]nLD Profile:[/bold red]")
        console.print(f"  Level: {nld['nld_level']}")
        if nld['is_nld_model']:
            sec = json.loads(nld['security_classification'])
            console.print(f"  Threat Level: {sec['threat_level'].upper()}")
            console.print(f"  Requires Auth: {sec['requires_authentication']}")


@catalogue.command()
@click.argument('query')
@click.pass_context
def search(ctx, query):
    """Search models by name, capability, or tag."""
    manager = ctx.obj['manager']

    results = manager.search_models(query)

    if not results:
        console.print(f"[yellow]No models found matching: {query}[/yellow]")
        return

    table = Table(title=f"Search Results: '{query}'")
    table.add_column("Name", style="cyan")
    table.add_column("Format", style="green")
    table.add_column("Size", style="yellow")
    table.add_column("ID", style="dim")

    for model in results:
        size_mb = model['size_bytes'] / (1024 * 1024)
        table.add_row(
            model['name'],
            model['format'],
            f"{size_mb:.1f} MB",
            model['model_id'][:8]
        )

    console.print(table)


@catalogue.command()
@click.argument('model_id')
@click.pass_context
def family(ctx, model_id):
    """Show model family tree."""
    manager = ctx.obj['manager']

    tree_data = manager.get_family_tree(model_id)
    if not tree_data:
        console.print(f"[red]Model not found: {model_id}[/red]")
        return

    family = tree_data['family']
    console.print(f"\n[bold cyan]Family: {family['family_name']}[/bold cyan]")
    console.print(f"Root Model: {family['root_model_id'][:8]}...")

    metadata = family['family_metadata']
    console.print(f"Total Members: {len(tree_data['members'])}")
    console.print(f"Total Tuning Hours: {metadata['total_tuning_hours']:.1f}h")
    console.print(f"Total Samples: {metadata['total_samples_used']}")

    console.print(f"\n[bold]Family Tree:[/bold]")

    tree = Tree(f"[bold]Generation 0[/bold]")

    for gen in sorted(tree_data['generations'].keys()):
        members = tree_data['generations'][gen]
        if gen == 0:
            for member in members:
                tree.add(f"[cyan]{member['name']}[/cyan] ({member['model_id'][:8]})")
        else:
            gen_branch = tree.add(f"[bold]Generation {gen}[/bold]")
            for member in members:
                gen_branch.add(f"[cyan]{member['name']}[/cyan] ({member['model_id'][:8]})")

    console.print(tree)


@catalogue.command()
@click.argument('model_id')
@click.option('--add', 'add_tags', multiple=True, help='Tags to add')
@click.option('--remove', 'remove_tags', multiple=True, help='Tags to remove')
@click.pass_context
def tag(ctx, model_id, add_tags, remove_tags):
    """Manage model tags."""
    manager = ctx.obj['manager']

    for tag in add_tags:
        manager.add_tag(model_id, tag)
        console.print(f"[green]✓ Added tag: {tag}[/green]")

    for tag in remove_tags:
        manager.remove_tag(model_id, tag)
        console.print(f"[yellow]✓ Removed tag: {tag}[/yellow]")


@catalogue.command()
@click.argument('model_id')
@click.option('--nld-level', type=int, required=True, help='nLD level')
@click.option('--instability', type=float, default=0.3, help='Instability score (0-1)')
@click.option('--threat', type=click.Choice(['safe', 'low', 'medium', 'high', 'critical']),
              default='medium', help='Threat level')
@click.pass_context
def set_nld(ctx, model_id, nld_level, instability, threat):
    """Set nLD profile for a model."""
    manager = ctx.obj['manager']

    # Placeholder training domains
    training_domains = [
        {
            "ld_id": "ld-" + str(i),
            "ld_schema": "mixed-geometry",
            "sample_count": 1000,
            "domain_characteristics": f"Domain {i}"
        }
        for i in range(nld_level)
    ]

    manager.set_nld_profile(model_id, nld_level, training_domains, instability, threat)
    console.print(f"[green]✓ nLD profile set[/green]")
    console.print(f"  Level: {nld_level}")
    console.print(f"  Instability: {instability}")
    console.print(f"  Threat: {threat}")


@catalogue.command()
@click.pass_context
def stats(ctx):
    """Show catalogue statistics."""
    manager = ctx.obj['manager']

    stats = manager.get_stats()

    console.print(f"\n[bold cyan]Catalogue Statistics[/bold cyan]")
    console.print(f"Total Models: {stats['total_models']}")
    console.print(f"Total Families: {stats['total_families']}")
    console.print(f"nLD Models: {stats['nld_models']}")

    console.print(f"\n[bold]By Format:[/bold]")
    for format_type, count in stats['by_format'].items():
        console.print(f"  {format_type}: {count}")


@catalogue.command()
@click.option('--output', default='catalogue_export.json', help='Output file')
@click.pass_context
def export(ctx, output):
    """Export catalogue to JSON."""
    manager = ctx.obj['manager']

    models = manager.list_models(limit=10000)

    export_data = {
        'exported_at': manager.conn.execute("SELECT datetime('now')").fetchone()[0],
        'total_models': len(models),
        'models': []
    }

    for model_summary in models:
        model = manager.get_model(model_summary['model_id'])
        export_data['models'].append(model)

    with open(output, 'w') as f:
        json.dump(export_data, f, indent=2)

    console.print(f"[green]✓ Exported {len(models)} models to {output}[/green]")


@catalogue.command()
@click.argument('model_id')
@click.pass_context
def verify(ctx, model_id):
    """Verify model file integrity."""
    manager = ctx.obj['manager']

    model = manager.get_model(model_id)
    if not model:
        console.print(f"[red]Model not found: {model_id}[/red]")
        return

    import os
    if not os.path.exists(model['path']):
        console.print(f"[red]✗ File not found: {model['path']}[/red]")
        return

    console.print(f"[cyan]Verifying: {model['name']}[/cyan]")

    with console.status("[bold green]Computing hash..."):
        current_hash = manager.compute_file_hash(model['path'])

    if current_hash == model['content_hash']:
        console.print(f"[green]✓ Hash verified[/green]")
    else:
        console.print(f"[red]✗ Hash mismatch![/red]")
        console.print(f"  Expected: {model['content_hash']}")
        console.print(f"  Got: {current_hash}")


if __name__ == '__main__':
    catalogue()
