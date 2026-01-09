# HyperSync Database CLI Commands
# Command-line interface for database operations

import click
import asyncio
import json
from typing import Optional
from pathlib import Path

from hypersync.wiring.database_integration import (
    DatabaseIntegrationWiring,
    DatabaseIntegrationMode,
    create_database_integration
)


@click.group(name='database')
def database_cli():
    '''HyperSync Database Operations'''
    pass


@database_cli.command('init')
@click.option('--mode', type=click.Choice(['standalone', 'federated', 'hybrid', 'edge_optimized']),
              default='hybrid', help='Database integration mode')
@click.option('--federation/--no-federation', default=True, help='Enable federation')
@click.option('--gpu/--no-gpu', default=False, help='Enable GPU acceleration')
@click.option('--edge/--no-edge', default=True, help='Enable edge optimization')
@click.option('--replication-factor', type=int, default=3, help='Replication factor')
def init_database(mode, federation, gpu, edge, replication_factor):
    '''Initialize HyperSync database'''
    async def _init():
        click.echo(f"Initializing database in {mode} mode...")

        db = await create_database_integration(
            mode=DatabaseIntegrationMode(mode),
            enable_federation=federation,
            enable_gpu_acceleration=gpu,
            enable_edge_optimization=edge,
            replication_factor=replication_factor
        )

        click.echo("✓ Database initialized successfully")
        click.echo(f"  Mode: {mode}")
        click.echo(f"  Federation: {'enabled' if federation else 'disabled'}")
        click.echo(f"  GPU: {'enabled' if gpu else 'disabled'}")
        click.echo(f"  Edge optimization: {'enabled' if edge else 'disabled'}")
        click.echo(f"  Replication factor: {replication_factor}")

        await db.shutdown()

    asyncio.run(_init())


@database_cli.command('store')
@click.argument('data')
@click.option('--metadata', type=str, help='JSON metadata')
@click.option('--file', type=click.Path(exists=True), help='Store from file')
def store_data(data, metadata, file):
    '''Store data in database'''
    async def _store():
        db = await create_database_integration()

        if file:
            data_content = Path(file).read_text()
        else:
            data_content = data

        metadata_dict = None
        if metadata:
            metadata_dict = json.loads(metadata)

        data_id = await db.store(data_content, metadata=metadata_dict)

        click.echo(f"✓ Data stored successfully")
        click.echo(f"  ID: {data_id}")

        await db.shutdown()

    asyncio.run(_store())


@database_cli.command('query')
@click.argument('query')
@click.option('--limit', type=int, default=100, help='Result limit')
@click.option('--offset', type=int, default=0, help='Result offset')
@click.option('--format', type=click.Choice(['json', 'table', 'csv']), default='json')
def query_data(query, limit, offset, format):
    '''Query data from database'''
    async def _query():
        db = await create_database_integration()

        results = await db.query(query, limit=limit, offset=offset)

        if format == 'json':
            click.echo(json.dumps(results, indent=2))
        elif format == 'table':
            # Simple table format
            if results:
                keys = results[0].keys()
                click.echo(' | '.join(keys))
                click.echo('-' * (len(keys) * 20))
                for result in results:
                    click.echo(' | '.join(str(result.get(k, '')) for k in keys))
        elif format == 'csv':
            if results:
                keys = results[0].keys()
                click.echo(','.join(keys))
                for result in results:
                    click.echo(','.join(str(result.get(k, '')) for k in keys))

        click.echo(f"\n✓ Found {len(results)} results")

        await db.shutdown()

    asyncio.run(_query())


@database_cli.command('get')
@click.argument('data_id')
def get_data(data_id):
    '''Get data by ID'''
    async def _get():
        db = await create_database_integration()

        result = await db.query(f"id:{data_id}")

        if result:
            click.echo(json.dumps(result[0], indent=2))
        else:
            click.echo(f"Data not found: {data_id}", err=True)

        await db.shutdown()

    asyncio.run(_get())


@database_cli.command('federate')
@click.argument('remote_node')
@click.argument('data_id')
def federate_data(remote_node, data_id):
    '''Federate data to remote node'''
    async def _federate():
        db = await create_database_integration(enable_federation=True)

        if 'federation' not in db.components:
            click.echo("Federation not enabled", err=True)
            return

        await db.federate(remote_node, data_id)

        click.echo(f"✓ Data federated to {remote_node}")
        click.echo(f"  Data ID: {data_id}")

        await db.shutdown()

    asyncio.run(_federate())


@database_cli.command('migrate')
@click.argument('target_version')
@click.option('--dry-run', is_flag=True, help='Perform dry run')
def migrate_database(target_version, dry_run):
    '''Migrate database to target version'''
    async def _migrate():
        db = await create_database_integration()

        if dry_run:
            click.echo(f"Dry run: would migrate to {target_version}")
        else:
            click.echo(f"Migrating to version {target_version}...")
            result = await db.migrate(target_version)
            click.echo(f"✓ Migration complete")
            click.echo(f"  Result: {result}")

        await db.shutdown()

    asyncio.run(_migrate())


@database_cli.command('health')
def health_check():
    '''Check database health'''
    async def _health():
        db = await create_database_integration()

        click.echo("Database Health Check")
        click.echo("=" * 50)

        for name, component in db.components.items():
            status = "✓ healthy" if component else "✗ unhealthy"
            click.echo(f"  {name}: {status}")

        click.echo("=" * 50)
        click.echo(f"Overall status: {'✓ healthy' if db.initialized else '✗ unhealthy'}")

        await db.shutdown()

    asyncio.run(_health())


@database_cli.command('metrics')
@click.option('--watch', is_flag=True, help='Watch metrics continuously')
@click.option('--interval', type=int, default=5, help='Watch interval in seconds')
def show_metrics(watch, interval):
    '''Show database metrics'''
    async def _metrics():
        db = await create_database_integration()

        def display_metrics():
            click.clear()
            click.echo("Database Metrics")
            click.echo("=" * 50)
            click.echo(f"  Mode: {db.config.mode.value}")
            click.echo(f"  Replication factor: {db.config.replication_factor}")
            click.echo(f"  Cache levels: {db.config.cache_levels}")
            click.echo(f"  Compression: {'enabled' if db.config.compression_enabled else 'disabled'}")
            click.echo("=" * 50)

        if watch:
            try:
                while True:
                    display_metrics()
                    await asyncio.sleep(interval)
            except KeyboardInterrupt:
                pass
        else:
            display_metrics()

        await db.shutdown()

    asyncio.run(_metrics())


def register_database_cli(cli):
    '''Register database CLI commands'''
    cli.add_command(database_cli)


__all__ = ['database_cli', 'register_database_cli']
