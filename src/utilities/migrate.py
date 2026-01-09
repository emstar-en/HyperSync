#!/usr/bin/env python3
"""
Database Migration Orchestrator
Applies all gap analysis migrations in correct order.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import psycopg2
except ImportError:
    logger.error("psycopg2 module not found. Please install it with: pip install psycopg2-binary")
    sys.exit(1)


class MigrationOrchestrator:
    """Orchestrate database migrations for gap analysis patches."""

    def __init__(self, db_config: dict, migrations_dir: str = 'patches'):
        """Initialize migration orchestrator.

        Args:
            db_config: Database configuration dictionary
            migrations_dir: Root directory to search for migrations
        """
        self.db_config = db_config
        self.migrations_dir = Path(migrations_dir)
        self.migrations = self._discover_migrations()

    def _discover_migrations(self) -> List[Tuple[str, str]]:
        """Discover migrations dynamically from the filesystem."""
        migrations = []
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory {self.migrations_dir} does not exist.")
            return []

        # Walk through the directory to find .sql files in 'migrations' subdirectories
        for root, _, files in os.walk(self.migrations_dir):
            if 'migrations' in Path(root).parts:
                for file in files:
                    if file.endswith('.sql') and not file.endswith('_rollback.sql'):
                        # Extract a migration ID from the filename (assuming format XXX_name.sql)
                        try:
                            migration_id = file.split('_')[0]
                            # Ensure it's a number/id
                            int(migration_id) 
                            full_path = os.path.join(root, file)
                            migrations.append((migration_id, full_path))
                        except ValueError:
                            logger.debug(f"Skipping file {file} as it does not start with a numeric ID")
                            continue

        # Sort by migration ID
        return sorted(migrations, key=lambda x: x[0])

    def connect(self):
        """Connect to database."""
        try:
            return psycopg2.connect(
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 5432),
                database=self.db_config.get('database', 'hypersync'),
                user=self.db_config.get('user', 'hypersync'),
                password=self.db_config.get('password', 'hypersync')
            )
        except psycopg2.Error as e:
            logger.error(f"Unable to connect to database: {e}")
            raise

    def create_migrations_table(self):
        """Create migrations tracking table."""
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS gap_analysis_migrations (
                        id SERIAL PRIMARY KEY,
                        migration_id VARCHAR(50) NOT NULL UNIQUE,
                        migration_name VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                conn.commit()
        logger.info("✓ Migrations table ensured")

    def is_migration_applied(self, migration_id: str) -> bool:
        """Check if migration is already applied."""
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM gap_analysis_migrations WHERE migration_id = %s",
                    (migration_id,)
                )
                return cursor.fetchone()[0] > 0

    def apply_migration(self, migration_id: str, migration_path: str):
        """Apply a single migration."""
        if self.is_migration_applied(migration_id):
            logger.info(f"⊘ Migration {migration_id} already applied, skipping")
            return

        logger.info(f"→ Applying migration {migration_id}: {migration_path}")

        sql_path = Path(migration_path)
        if not sql_path.exists():
            logger.error(f"⚠ Migration file not found: {migration_path}")
            return

        try:
            with open(sql_path, 'r') as f:
                sql = f.read()

            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    cursor.execute(
                        """
                        INSERT INTO gap_analysis_migrations (migration_id, migration_name)
                        VALUES (%s, %s)
                        """,
                        (migration_id, sql_path.name)
                    )
                    conn.commit()
            logger.info(f"✓ Migration {migration_id} applied successfully")

        except Exception as e:
            logger.error(f"✗ Migration {migration_id} failed: {e}")
            raise

    def apply_all_migrations(self):
        """Apply all discovered migrations."""
        logger.info("="*60)
        logger.info("APPLYING GAP ANALYSIS MIGRATIONS")
        logger.info("="*60)

        try:
            self.create_migrations_table()
        except Exception:
            logger.critical("Failed to initialize migrations table. Aborting.")
            return

        if not self.migrations:
            logger.info("No migrations found.")
            return

        for migration_id, migration_path in self.migrations:
            try:
                self.apply_migration(migration_id, migration_path)
            except Exception:
                logger.error(f"Stopping migration process due to error in {migration_id}")
                break

        logger.info("="*60)
        logger.info("✅ MIGRATION PROCESS COMPLETED")
        logger.info("="*60)

    def rollback_migration(self, migration_id: str):
        """Rollback a specific migration."""
        logger.info(f"↶ Rolling back migration {migration_id}")

        # Find the migration path to determine the rollback path
        migration_path = next((path for mid, path in self.migrations if mid == migration_id), None)

        if not migration_path:
             # Try to find it even if it's not in the list (maybe file was moved, but we can guess)
             # For now, just fail if we can't find the source file to derive rollback name
             logger.error(f"Could not find original migration file for ID {migration_id} to determine rollback script.")
             return

        rollback_path = str(migration_path).replace('.sql', '_rollback.sql')

        if not Path(rollback_path).exists():
            logger.error(f"✗ Rollback file not found: {rollback_path}")
            return

        try:
            with open(rollback_path, 'r') as f:
                sql = f.read()

            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    cursor.execute(
                        "DELETE FROM gap_analysis_migrations WHERE migration_id = %s",
                        (migration_id,)
                    )
                    conn.commit()
            logger.info(f"✓ Migration {migration_id} rolled back")

        except Exception as e:
            logger.error(f"✗ Rollback failed: {e}")
            raise


if __name__ == '__main__':
    # Load config from environment variables
    db_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': int(os.environ.get('DB_PORT', 5432)),
        'database': os.environ.get('DB_NAME', 'hypersync'),
        'user': os.environ.get('DB_USER', 'hypersync'),
        'password': os.environ.get('DB_PASSWORD', 'hypersync')
    }

    # Allow overriding migrations directory
    migrations_dir = os.environ.get('MIGRATIONS_DIR', 'patches')

    orchestrator = MigrationOrchestrator(db_config, migrations_dir)

    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        if len(sys.argv) > 2:
            orchestrator.rollback_migration(sys.argv[2])
        else:
            print("Usage: python migrate.py rollback <migration_id>")
    else:
        orchestrator.apply_all_migrations()
