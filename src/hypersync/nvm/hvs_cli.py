"""
HyperSync HVS CLI Commands

Provides command-line interface for managing Hyperbolic Vector Storage instances.
"""

from __future__ import annotations

import json
import click
from pathlib import Path
from rich import print as rprint
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON

from ..nvm.hvs_manager import (
    HVSManager,
    HVSSchema,
    HVSCapacityConfig,
    HVSAttachmentConfig,
    HVSSyncConfig,
    HVSNetworkBridge,
    NVMGeometryConfig,
    NVMIndexConfig,
    NVMCodebookConfig,
)


@click.group(name='hvs')
def hvs_cli():
    """Manage Hyperbolic Vector Storage (HVS) instances."""
    pass


@hvs_cli.command('create')
@click.option('--name', required=True, help='Name for the HVS instance')
@click.option('--description', default=None, help='Description of the HVS')
@click.option('--geometry', type=click.Choice(['euclidean', 'spherical', 'poincare_ball', 'hyperboloid', 'spd_logeuclid']), 
              default='poincare_ball', help='Geometry space')
@click.option('--curvature', type=float, default=-1.0, help='Curvature for hyperbolic spaces')
@click.option('--radius-cap', type=float, default=0.98, help='Radius cap for bounded spaces')
@click.option('--index-type', type=click.Choice(['hnsw_euclidean', 'hnsw_hyperbolic', 'ivfpq', 'bruteforce']),
              default='hnsw_hyperbolic', help='Index type')
@click.option('--vector-dim', type=int, required=True, help='Vector dimensionality')
@click.option('--max-vectors', type=int, default=None, help='Maximum number of vectors')
@click.option('--attach-type', type=click.Choice(['model', 'stack', 'trunk', 'network', 'bridge']),
              default=None, help='Attachment type')
@click.option('--attach-id', default=None, help='Attachment ID')
@click.option('--attach-name', default=None, help='Attachment name')
@click.option('--tier', default=None, help='Service tier')
@click.option('--storage-root', type=click.Path(), default='./hypersync_data', help='Storage root directory')
@click.pass_context
def create_hvs(ctx, name, description, geometry, curvature, radius_cap, index_type, 
               vector_dim, max_vectors, attach_type, attach_id, attach_name, tier, storage_root):
    """Create a new HVS instance."""

    manager = HVSManager(Path(storage_root))

    # Build geometry config
    geom_config = NVMGeometryConfig(
        space=geometry,
        curvature=curvature if geometry in ['poincare_ball', 'hyperboloid'] else None,
        radius_cap=radius_cap if geometry in ['poincare_ball', 'spherical'] else None
    )

    # Build index config
    index_config = NVMIndexConfig(
        type=index_type,
        params={
            'M': 32,
            'ef_construction': 200,
            'ef_runtime': 64
        } if 'hnsw' in index_type else {}
    )

    # Build capacity config
    capacity_config = HVSCapacityConfig(
        vector_dim=vector_dim,
        max_vectors=max_vectors,
        growth_policy='auto_expand'
    )

    # Build schema
    schema = HVSSchema(
        name=name,
        description=description,
        geometry=geom_config,
        index=index_config,
        capacity=capacity_config,
        tier=tier
    )

    # Add attachment if specified
    if attach_type and attach_id:
        attachment = HVSAttachmentConfig(
            attachment_type=attach_type,
            attachment_id=attach_id,
            attachment_name=attach_name
        )
        schema.attachments.append(attachment)

    # Create the HVS
    created = manager.create(schema)

    rprint(Panel(f"[green]✓[/green] Created HVS: [bold]{created.name}[/bold]", 
                 title="HVS Created", border_style="green"))
    rprint(f"  HVS ID: {created.hvs_id}")
    rprint(f"  Geometry: {created.geometry.space}")
    rprint(f"  Vector Dim: {created.capacity.vector_dim}")
    rprint(f"  Schema Hash: {created.compute_schema_hash()}")


@hvs_cli.command('list')
@click.option('--attach-type', default=None, help='Filter by attachment type')
@click.option('--attach-id', default=None, help='Filter by attachment ID')
@click.option('--bridges-only', is_flag=True, help='Show only bridge HVS instances')
@click.option('--storage-root', type=click.Path(), default='./hypersync_data', help='Storage root directory')
@click.pass_context
def list_hvs(ctx, attach_type, attach_id, bridges_only, storage_root):
    """List HVS instances."""

    manager = HVSManager(Path(storage_root))

    if bridges_only:
        hvs_list = manager.list_bridges()
    elif attach_type and attach_id:
        hvs_list = manager.list_by_attachment(attach_type, attach_id)
    else:
        hvs_list = manager.list_all()

    if not hvs_list:
        rprint("[yellow]No HVS instances found[/yellow]")
        return

    table = Table(title=f"HVS Instances ({len(hvs_list)})")
    table.add_column("HVS ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Geometry", style="magenta")
    table.add_column("Dim", justify="right")
    table.add_column("Vectors", justify="right")
    table.add_column("Status", style="green")
    table.add_column("Attachments", justify="right")
    table.add_column("Bridges", justify="right")

    for hvs in hvs_list:
        table.add_row(
            hvs.hvs_id[:12] + "...",
            hvs.name,
            hvs.geometry.space,
            str(hvs.capacity.vector_dim),
            str(hvs.vector_count),
            hvs.status,
            str(len(hvs.attachments)),
            str(len(hvs.bridges))
        )

    rprint(table)


@hvs_cli.command('get')
@click.argument('hvs_id')
@click.option('--storage-root', type=click.Path(), default='./hypersync_data', help='Storage root directory')
@click.pass_context
def get_hvs(ctx, hvs_id, storage_root):
    """Get detailed information about an HVS instance."""

    manager = HVSManager(Path(storage_root))
    hvs = manager.get(hvs_id)

    if not hvs:
        rprint(f"[red]✗[/red] HVS not found: {hvs_id}")
        return

    rprint(Panel(JSON(hvs.model_dump_json(indent=2)), 
                 title=f"HVS: {hvs.name}", border_style="cyan"))


@hvs_cli.command('attach')
@click.argument('hvs_id')
@click.option('--attach-type', type=click.Choice(['model', 'stack', 'trunk', 'network', 'bridge']), required=True)
@click.option('--attach-id', required=True, help='Attachment ID')
@click.option('--attach-name', default=None, help='Attachment name')
@click.option('--priority', type=int, default=0, help='Attachment priority')
@click.option('--storage-root', type=click.Path(), default='./hypersync_data', help='Storage root directory')
@click.pass_context
def attach_hvs(ctx, hvs_id, attach_type, attach_id, attach_name, priority, storage_root):
    """Attach an HVS to a model, stack, trunk, or network."""

    manager = HVSManager(Path(storage_root))
    hvs = manager.get(hvs_id)

    if not hvs:
        rprint(f"[red]✗[/red] HVS not found: {hvs_id}")
        return

    attachment = HVSAttachmentConfig(
        attachment_type=attach_type,
        attachment_id=attach_id,
        attachment_name=attach_name,
        priority=priority
    )

    hvs.attachments.append(attachment)
    manager.update(hvs)

    rprint(f"[green]✓[/green] Attached HVS [bold]{hvs.name}[/bold] to {attach_type}:{attach_id}")


@hvs_cli.command('sync')
@click.argument('hvs_id')
@click.option('--enable/--disable', default=True, help='Enable or disable sync')
@click.option('--sync-dims', default=None, help='Comma-separated dimension indices to sync')
@click.option('--sync-mode', type=click.Choice(['full', 'partial', 'selective']), default='full')
@click.option('--conflict-resolution', type=click.Choice(['last_write_wins', 'vector_merge', 'manual']),
              default='last_write_wins')
@click.option('--storage-root', type=click.Path(), default='./hypersync_data', help='Storage root directory')
@click.pass_context
def configure_sync(ctx, hvs_id, enable, sync_dims, sync_mode, conflict_resolution, storage_root):
    """Configure synchronization for an HVS instance."""

    manager = HVSManager(Path(storage_root))
    hvs = manager.get(hvs_id)

    if not hvs:
        rprint(f"[red]✗[/red] HVS not found: {hvs_id}")
        return

    dims_list = []
    if sync_dims:
        dims_list = [int(d.strip()) for d in sync_dims.split(',')]

    sync_config = HVSSyncConfig(
        enabled=enable,
        sync_dims=dims_list,
        sync_mode=sync_mode,
        conflict_resolution=conflict_resolution
    )

    hvs.sync = sync_config
    manager.update(hvs)

    rprint(f"[green]✓[/green] Configured sync for HVS [bold]{hvs.name}[/bold]")
    rprint(f"  Enabled: {enable}")
    rprint(f"  Sync Dims: {dims_list if dims_list else 'all'}")
    rprint(f"  Mode: {sync_mode}")


@hvs_cli.command('bridge')
@click.argument('hvs_id')
@click.option('--network-ids', required=True, help='Comma-separated network IDs to bridge')
@click.option('--shared-dims', default=None, help='Comma-separated dimension indices to share')
@click.option('--isolation', type=click.Choice(['full_share', 'read_only', 'write_through', 'isolated_namespaces']),
              default='isolated_namespaces')
@click.option('--storage-root', type=click.Path(), default='./hypersync_data', help='Storage root directory')
@click.pass_context
def create_bridge(ctx, hvs_id, network_ids, shared_dims, isolation, storage_root):
    """Configure an HVS as a network bridge."""

    manager = HVSManager(Path(storage_root))
    hvs = manager.get(hvs_id)

    if not hvs:
        rprint(f"[red]✗[/red] HVS not found: {hvs_id}")
        return

    net_list = [n.strip() for n in network_ids.split(',')]
    dims_list = []
    if shared_dims:
        dims_list = [int(d.strip()) for d in shared_dims.split(',')]

    bridge = HVSNetworkBridge(
        network_ids=net_list,
        shared_dims=dims_list,
        isolation_policy=isolation
    )

    hvs.bridges.append(bridge)
    manager.update(hvs)

    rprint(f"[green]✓[/green] Created bridge in HVS [bold]{hvs.name}[/bold]")
    rprint(f"  Bridge ID: {bridge.bridge_id}")
    rprint(f"  Networks: {', '.join(net_list)}")
    rprint(f"  Shared Dims: {dims_list if dims_list else 'all'}")


@hvs_cli.command('delete')
@click.argument('hvs_id')
@click.option('--confirm', is_flag=True, help='Confirm deletion')
@click.option('--storage-root', type=click.Path(), default='./hypersync_data', help='Storage root directory')
@click.pass_context
def delete_hvs(ctx, hvs_id, confirm, storage_root):
    """Delete an HVS instance."""

    if not confirm:
        rprint("[yellow]⚠[/yellow] Use --confirm to delete the HVS instance")
        return

    manager = HVSManager(Path(storage_root))

    if manager.delete(hvs_id):
        rprint(f"[green]✓[/green] Deleted HVS: {hvs_id}")
    else:
        rprint(f"[red]✗[/red] HVS not found: {hvs_id}")
