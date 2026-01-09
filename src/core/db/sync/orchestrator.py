"""
Sync Orchestrator

Manages connectors, handles incremental fetches, and applies conflict
resolution strategies.
"""
import logging
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from hypersync.db.adapters.base import DatabaseAdapter, Watermark, DeltaBatch

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Sync job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class ConflictResolution(Enum):
    """Conflict resolution strategies."""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL = "manual"
    CUSTOM = "custom"


@dataclass
class SyncJob:
    """
    Sync job definition.

    Persisted in catalog with status transitions.
    """
    job_id: str
    source_adapter: str
    target_adapter: str
    tables: List[str]
    status: SyncStatus = SyncStatus.PENDING
    conflict_resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS
    watermark: Optional[Watermark] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    stats: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'job_id': self.job_id,
            'source_adapter': self.source_adapter,
            'target_adapter': self.target_adapter,
            'tables': self.tables,
            'status': self.status.value,
            'conflict_resolution': self.conflict_resolution.value,
            'watermark': self.watermark.__dict__ if self.watermark else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'error_message': self.error_message,
            'stats': self.stats
        }


class SyncOrchestrator:
    """
    Orchestrates data synchronization between adapters.

    Manages connectors, handles incremental fetches, and applies
    conflict resolution.
    """

    def __init__(self):
        self._adapters: Dict[str, DatabaseAdapter] = {}
        self._jobs: Dict[str, SyncJob] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}

    def register_adapter(self, name: str, adapter: DatabaseAdapter):
        """
        Register database adapter.

        Args:
            name: Adapter name
            adapter: Adapter instance
        """
        self._adapters[name] = adapter
        logger.info(f"Registered adapter: {name} ({adapter.driver})")

    def get_adapter(self, name: str) -> Optional[DatabaseAdapter]:
        """Get adapter by name."""
        return self._adapters.get(name)

    def create_sync_job(
        self,
        job_id: str,
        source: str,
        target: str,
        tables: List[str],
        conflict_resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS
    ) -> SyncJob:
        """
        Create sync job.

        Args:
            job_id: Unique job identifier
            source: Source adapter name
            target: Target adapter name
            tables: Tables to sync
            conflict_resolution: Conflict resolution strategy

        Returns:
            Created sync job
        """
        job = SyncJob(
            job_id=job_id,
            source_adapter=source,
            target_adapter=target,
            tables=tables,
            conflict_resolution=conflict_resolution
        )

        self._jobs[job_id] = job
        logger.info(f"Created sync job: {job_id}")

        return job

    async def start_sync(self, job_id: str):
        """
        Start sync job.

        Args:
            job_id: Job identifier
        """
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        if job.status == SyncStatus.RUNNING:
            logger.warning(f"Job already running: {job_id}")
            return

        # Create task
        task = asyncio.create_task(self._run_sync(job))
        self._running_tasks[job_id] = task

        logger.info(f"Started sync job: {job_id}")

    async def stop_sync(self, job_id: str):
        """Stop sync job."""
        task = self._running_tasks.get(job_id)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

            del self._running_tasks[job_id]

        job = self._jobs.get(job_id)
        if job:
            job.status = SyncStatus.PAUSED
            job.updated_at = datetime.now()

        logger.info(f"Stopped sync job: {job_id}")

    async def _run_sync(self, job: SyncJob):
        """Run sync job."""
        try:
            job.status = SyncStatus.RUNNING
            job.updated_at = datetime.now()

            # Get adapters
            source = self._adapters.get(job.source_adapter)
            target = self._adapters.get(job.target_adapter)

            if not source or not target:
                raise ValueError("Source or target adapter not found")

            # Ensure connected
            if source.status.value != "connected":
                await source.connect()
            if target.status.value != "connected":
                await target.connect()

            # Initial sync if no watermark
            if not job.watermark:
                await self._initial_sync(job, source, target)

            # Incremental sync
            while True:
                await self._incremental_sync(job, source, target)

                # Wait before next sync
                await asyncio.sleep(10)

        except asyncio.CancelledError:
            logger.info(f"Sync job cancelled: {job.job_id}")
            raise
        except Exception as e:
            job.status = SyncStatus.FAILED
            job.error_message = str(e)
            job.updated_at = datetime.now()
            logger.error(f"Sync job failed: {job.job_id}, error: {e}")

    async def _initial_sync(self, job: SyncJob, source: DatabaseAdapter, target: DatabaseAdapter):
        """Perform initial full sync."""
        logger.info(f"Starting initial sync for job: {job.job_id}")

        # Introspect source
        snapshot = await source.introspect()

        # For each table
        for table in job.tables:
            if table not in snapshot.tables:
                logger.warning(f"Table not found in source: {table}")
                continue

            # Pull all data (simplified - would use pagination)
            watermark = Watermark(position=0, timestamp=0.0, metadata={})
            batch = await source.pull_delta(watermark)

            # Push to target
            await target.push_delta(batch)

            # Update stats
            job.stats[table] = len(batch.inserts)

        # Set watermark
        job.watermark = Watermark(
            position="initial",
            timestamp=datetime.now().timestamp(),
            metadata={}
        )
        job.updated_at = datetime.now()

        logger.info(f"Initial sync completed for job: {job.job_id}")

    async def _incremental_sync(self, job: SyncJob, source: DatabaseAdapter, target: DatabaseAdapter):
        """Perform incremental sync."""
        logger.debug(f"Incremental sync for job: {job.job_id}")

        # Pull delta
        batch = await source.pull_delta(job.watermark)

        if not batch.inserts and not batch.updates and not batch.deletes:
            # No changes
            return

        # Apply conflict resolution
        resolved_batch = self._resolve_conflicts(batch, job.conflict_resolution)

        # Push to target
        await target.push_delta(resolved_batch)

        # Update watermark
        job.watermark = batch.watermark
        job.updated_at = datetime.now()

        # Update stats
        for table in job.tables:
            if table not in job.stats:
                job.stats[table] = 0
            job.stats[table] += len(batch.inserts) + len(batch.updates)

        logger.debug(f"Synced {len(batch.inserts)} inserts, {len(batch.updates)} updates, {len(batch.deletes)} deletes")

    def _resolve_conflicts(self, batch: DeltaBatch, strategy: ConflictResolution) -> DeltaBatch:
        """
        Resolve conflicts in batch.

        Args:
            batch: Delta batch
            strategy: Resolution strategy

        Returns:
            Resolved batch
        """
        if strategy == ConflictResolution.LAST_WRITE_WINS:
            # Keep all changes (last write wins)
            return batch
        elif strategy == ConflictResolution.FIRST_WRITE_WINS:
            # Would need to check existing data
            return batch
        elif strategy == ConflictResolution.MANUAL:
            # Would queue for manual resolution
            return batch
        else:
            return batch

    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get job status."""
        job = self._jobs.get(job_id)
        if job:
            return job.to_dict()
        return None

    def list_jobs(self) -> List[dict]:
        """List all jobs."""
        return [job.to_dict() for job in self._jobs.values()]


# Export public API
__all__ = [
    'SyncOrchestrator',
    'SyncJob',
    'SyncStatus',
    'ConflictResolution'
]
