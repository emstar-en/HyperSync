"""
HyperSync Database CLI

Command-line interface for database operations.
"""
import click
import asyncio
from pathlib import Path

from hypersync.db.migrations.runner import MigrationRunner
from hypersync.db.importer.bulk import BulkImporter, BackupManager
from hypersync.db.engine.core import HyperbolicStorageEngine


@click.group()
def cli():
    """HyperSync Database CLI"""
    pass


@cli.group()
def db():
    """Database operations"""
    pass


@db.command()
@click.option('--plan', is_flag=True, help='Show migration plan without applying')
@click.option('--apply', is_flag=True, help='Apply migrations')
@click.option('--rollback', is_flag=True, help='Rollback migrations')
@click.option('--target', help='Target migration ID')
@click.option('--data-dir', default='./data', help='Data directory')
def migrate(plan, apply, rollback, target, data_dir):
    """Run database migrations"""
    engine = HyperbolicStorageEngine(Path(data_dir))
    runner = MigrationRunner(engine)

    # Register migrations (would auto-discover)
    # runner.register(...)

    if plan:
        click.echo("Migration Plan:")
        migration_plan = runner.plan()
        for mid in migration_plan:
            click.echo(f"  - {mid}")

        # Dry run
        click.echo("\nDry Run:")
        dry_run = runner.dry_run()
        for mid, ops in dry_run.items():
            click.echo(f"\n{mid}:")
            for op in ops:
                click.echo(f"  {op['type']}: {op}")

    elif apply:
        click.echo("Applying migrations...")
        runner.apply(target)
        click.echo("✓ Migrations applied")

    elif rollback:
        click.echo("Rolling back migrations...")
        runner.rollback(target)
        click.echo("✓ Migrations rolled back")

    else:
        click.echo("Use --plan, --apply, or --rollback")

    engine.close()


@db.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('table')
@click.option('--format', type=click.Choice(['csv', 'json']), default='csv')
@click.option('--chunk-size', default=1000, help='Chunk size for import')
@click.option('--data-dir', default='./data', help='Data directory')
def import_data(file_path, table, format, chunk_size, data_dir):
    """Import data from file"""
    engine = HyperbolicStorageEngine(Path(data_dir))
    importer = BulkImporter(engine, chunk_size=chunk_size)

    file_path = Path(file_path)

    click.echo(f"Importing {file_path} -> {table}")

    if format == 'csv':
        checkpoint = importer.import_csv(file_path, table)
    elif format == 'json':
        checkpoint = importer.import_json(file_path, table)

    click.echo(f"✓ Imported {checkpoint.records_imported} records")

    engine.close()


@db.command()
@click.argument('backup_path', type=click.Path())
@click.option('--data-dir', default='./data', help='Data directory')
def backup(backup_path, data_dir):
    """Create database backup"""
    engine = HyperbolicStorageEngine(Path(data_dir))
    manager = BackupManager(engine)

    backup_path = Path(backup_path)

    click.echo(f"Creating backup: {backup_path}")
    metadata = manager.create_backup(backup_path)

    click.echo(f"✓ Backup created")
    click.echo(f"  Timestamp: {metadata['timestamp']}")
    click.echo(f"  Tables: {len(metadata['tables'])}")
    click.echo(f"  WAL Position: {metadata['wal_position']}")

    engine.close()


@db.command()
@click.argument('backup_path', type=click.Path(exists=True))
@click.option('--data-dir', default='./data', help='Data directory')
def restore(backup_path, data_dir):
    """Restore database from backup"""
    engine = HyperbolicStorageEngine(Path(data_dir))
    manager = BackupManager(engine)

    backup_path = Path(backup_path)

    click.echo(f"Restoring from: {backup_path}")
    manager.restore_backup(backup_path)

    click.echo(f"✓ Restore completed")

    engine.close()


@db.command()
@click.option('--data-dir', default='./data', help='Data directory')
def status(data_dir):
    """Show database status"""
    engine = HyperbolicStorageEngine(Path(data_dir))

    click.echo("Database Status:")
    click.echo(f"  Data Directory: {data_dir}")
    click.echo(f"  Relations: {len(engine.catalog.relations)}")

    for name in engine.catalog.relations.keys():
        records = engine.scan(name)
        click.echo(f"    - {name}: {len(records)} records")

    engine.close()


if __name__ == '__main__':
    cli()
