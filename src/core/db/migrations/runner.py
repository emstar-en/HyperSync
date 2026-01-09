"""
Migration Framework

DSL for schema evolution with forward/backward operations, dependency
graph, and dry-run validation.
"""
import logging
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class MigrationStatus(Enum):
    """Migration status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Column:
    """Column definition for migrations."""
    name: str
    data_type: str
    nullable: bool = True
    default: Optional[any] = None
    primary_key: bool = False
    unique: bool = False


@dataclass
class CurvatureColumn(Column):
    """Curvature-aware column."""
    curvature: float = -1.0
    precision: float = 1e-3

    def __init__(self, name: str, data_type: str, default: Optional[any] = None, **kwargs):
        super().__init__(name, data_type, default=default, **kwargs)
        self.curvature = kwargs.get('curvature', -1.0)
        self.precision = kwargs.get('precision', 1e-3)


class Migration(ABC):
    """
    Base migration class.

    Subclass and implement up() and down() methods.
    """

    id: str = ""
    dependencies: List[str] = []

    def __init__(self):
        self._operations: List[dict] = []

    @abstractmethod
    def up(self):
        """Forward migration."""
        pass

    @abstractmethod
    def down(self):
        """Backward migration (rollback)."""
        pass

    def create_table(self, name: str, columns: List[Column], **kwargs):
        """Create table operation."""
        self._operations.append({
            'type': 'create_table',
            'name': name,
            'columns': [self._column_to_dict(col) for col in columns],
            'metadata': kwargs
        })
        logger.debug(f"Migration {self.id}: create_table {name}")

    def drop_table(self, name: str):
        """Drop table operation."""
        self._operations.append({
            'type': 'drop_table',
            'name': name
        })
        logger.debug(f"Migration {self.id}: drop_table {name}")

    def add_column(self, table: str, column: Column):
        """Add column operation."""
        self._operations.append({
            'type': 'add_column',
            'table': table,
            'column': self._column_to_dict(column)
        })
        logger.debug(f"Migration {self.id}: add_column {table}.{column.name}")

    def drop_column(self, table: str, column_name: str):
        """Drop column operation."""
        self._operations.append({
            'type': 'drop_column',
            'table': table,
            'column': column_name
        })
        logger.debug(f"Migration {self.id}: drop_column {table}.{column_name}")

    def create_index(self, table: str, columns: List[str], name: Optional[str] = None, unique: bool = False):
        """Create index operation."""
        index_name = name or f"idx_{table}_{'_'.join(columns)}"
        self._operations.append({
            'type': 'create_index',
            'table': table,
            'name': index_name,
            'columns': columns,
            'unique': unique
        })
        logger.debug(f"Migration {self.id}: create_index {index_name}")

    def drop_index(self, name: str):
        """Drop index operation."""
        self._operations.append({
            'type': 'drop_index',
            'name': name
        })
        logger.debug(f"Migration {self.id}: drop_index {name}")

    def execute_sql(self, sql: str):
        """Execute raw SQL."""
        self._operations.append({
            'type': 'execute_sql',
            'sql': sql
        })
        logger.debug(f"Migration {self.id}: execute_sql")

    def _column_to_dict(self, column: Column) -> dict:
        """Convert column to dictionary."""
        result = {
            'name': column.name,
            'type': column.data_type,
            'nullable': column.nullable,
            'default': column.default,
            'primary_key': column.primary_key,
            'unique': column.unique
        }

        if isinstance(column, CurvatureColumn):
            result['curvature'] = column.curvature
            result['precision'] = column.precision

        return result

    def get_operations(self) -> List[dict]:
        """Get list of operations."""
        return self._operations


@dataclass
class MigrationRecord:
    """Record of applied migration."""
    migration_id: str
    applied_at: datetime
    status: MigrationStatus
    error_message: Optional[str] = None


class MigrationRunner:
    """
    Runs migrations with dependency resolution.

    Provides dry-run validation and rollback support.
    """

    def __init__(self, storage_engine=None):
        self.storage_engine = storage_engine
        self._migrations: Dict[str, Migration] = {}
        self._applied: Dict[str, MigrationRecord] = {}
        self._load_applied_migrations()

    def register(self, migration: Migration):
        """Register migration."""
        self._migrations[migration.id] = migration
        logger.info(f"Registered migration: {migration.id}")

    def _load_applied_migrations(self):
        """Load applied migrations from storage."""
        # In production, would query migration table
        # For now, use empty dict
        pass

    def _save_migration_record(self, record: MigrationRecord):
        """Save migration record."""
        self._applied[record.migration_id] = record
        # In production, would persist to database

    def plan(self) -> List[str]:
        """
        Generate migration plan.

        Returns:
            List of migration IDs in execution order
        """
        # Find pending migrations
        pending = [
            mid for mid in self._migrations.keys()
            if mid not in self._applied or self._applied[mid].status != MigrationStatus.COMPLETED
        ]

        # Topological sort based on dependencies
        sorted_migrations = self._topological_sort(pending)

        return sorted_migrations

    def _topological_sort(self, migration_ids: List[str]) -> List[str]:
        """Sort migrations by dependencies."""
        # Build dependency graph
        graph = {mid: self._migrations[mid].dependencies for mid in migration_ids}

        # Kahn's algorithm
        in_degree = {mid: 0 for mid in migration_ids}
        for mid in migration_ids:
            for dep in graph[mid]:
                if dep in in_degree:
                    in_degree[dep] += 1

        queue = [mid for mid in migration_ids if in_degree[mid] == 0]
        result = []

        while queue:
            mid = queue.pop(0)
            result.append(mid)

            for other_mid in migration_ids:
                if mid in graph[other_mid]:
                    in_degree[other_mid] -= 1
                    if in_degree[other_mid] == 0:
                        queue.append(other_mid)

        if len(result) != len(migration_ids):
            raise ValueError("Circular dependency detected in migrations")

        return result

    def dry_run(self) -> Dict[str, List[dict]]:
        """
        Perform dry run of migrations.

        Returns:
            Dictionary of migration_id -> operations
        """
        plan = self.plan()

        result = {}
        for mid in plan:
            migration = self._migrations[mid]

            # Execute up() to collect operations
            migration.up()
            result[mid] = migration.get_operations()

        return result

    def apply(self, target: Optional[str] = None):
        """
        Apply migrations.

        Args:
            target: Target migration ID, or None for all
        """
        plan = self.plan()

        # Filter to target
        if target:
            try:
                target_idx = plan.index(target)
                plan = plan[:target_idx + 1]
            except ValueError:
                raise ValueError(f"Target migration not found: {target}")

        # Apply each migration
        for mid in plan:
            self._apply_migration(mid)

    def _apply_migration(self, migration_id: str):
        """Apply single migration."""
        migration = self._migrations[migration_id]

        record = MigrationRecord(
            migration_id=migration_id,
            applied_at=datetime.now(),
            status=MigrationStatus.RUNNING
        )

        try:
            logger.info(f"Applying migration: {migration_id}")

            # Execute up()
            migration.up()

            # Execute operations
            for op in migration.get_operations():
                self._execute_operation(op)

            # Mark as completed
            record.status = MigrationStatus.COMPLETED
            self._save_migration_record(record)

            logger.info(f"Migration completed: {migration_id}")

        except Exception as e:
            record.status = MigrationStatus.FAILED
            record.error_message = str(e)
            self._save_migration_record(record)

            logger.error(f"Migration failed: {migration_id}, error: {e}")
            raise

    def _execute_operation(self, operation: dict):
        """Execute migration operation."""
        op_type = operation['type']

        if op_type == 'create_table':
            self._create_table(operation)
        elif op_type == 'drop_table':
            self._drop_table(operation)
        elif op_type == 'add_column':
            self._add_column(operation)
        elif op_type == 'drop_column':
            self._drop_column(operation)
        elif op_type == 'create_index':
            self._create_index(operation)
        elif op_type == 'drop_index':
            self._drop_index(operation)
        elif op_type == 'execute_sql':
            self._execute_sql(operation)
        else:
            raise ValueError(f"Unknown operation type: {op_type}")

    def _create_table(self, op: dict):
        """Execute create table."""
        if self.storage_engine:
            schema = {
                'name': op['name'],
                'fields': op['columns']
            }
            self.storage_engine.create_relation(op['name'], schema)

    def _drop_table(self, op: dict):
        """Execute drop table."""
        # Would call storage engine
        pass

    def _add_column(self, op: dict):
        """Execute add column."""
        # Would call storage engine
        pass

    def _drop_column(self, op: dict):
        """Execute drop column."""
        # Would call storage engine
        pass

    def _create_index(self, op: dict):
        """Execute create index."""
        # Would call storage engine
        pass

    def _drop_index(self, op: dict):
        """Execute drop index."""
        # Would call storage engine
        pass

    def _execute_sql(self, op: dict):
        """Execute raw SQL."""
        # Would call storage engine
        pass

    def rollback(self, target: Optional[str] = None):
        """
        Rollback migrations.

        Args:
            target: Target migration to rollback to
        """
        # Get applied migrations in reverse order
        applied = [
            mid for mid in self._migrations.keys()
            if mid in self._applied and self._applied[mid].status == MigrationStatus.COMPLETED
        ]
        applied.reverse()

        # Rollback until target
        for mid in applied:
            if target and mid == target:
                break

            self._rollback_migration(mid)

    def _rollback_migration(self, migration_id: str):
        """Rollback single migration."""
        migration = self._migrations[migration_id]

        try:
            logger.info(f"Rolling back migration: {migration_id}")

            # Execute down()
            migration.down()

            # Execute operations
            for op in migration.get_operations():
                self._execute_operation(op)

            # Update record
            if migration_id in self._applied:
                self._applied[migration_id].status = MigrationStatus.ROLLED_BACK

            logger.info(f"Migration rolled back: {migration_id}")

        except Exception as e:
            logger.error(f"Rollback failed: {migration_id}, error: {e}")
            raise


# Export public API
__all__ = [
    'Migration',
    'MigrationRunner',
    'Column',
    'CurvatureColumn',
    'MigrationStatus'
]
