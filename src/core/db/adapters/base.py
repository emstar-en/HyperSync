"""
Database Adapter Base Contract

Defines interface for connecting HyperSync to external data systems
while preserving curvature semantics.
"""
import logging
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class AdapterStatus(Enum):
    """Adapter connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class SchemaSnapshot:
    """Snapshot of external schema."""
    tables: Dict[str, dict]
    version: str
    timestamp: float
    curvature_mapping: Dict[str, float]

    @classmethod
    def from_relation(cls, metadata: List[dict], curvature: str = "negative") -> 'SchemaSnapshot':
        """Create snapshot from relation metadata."""
        import time

        tables = {}
        curvature_mapping = {}

        # Group by table
        for row in metadata:
            table_name = row.get('table_name', 'unknown')
            if table_name not in tables:
                tables[table_name] = {'columns': []}

            tables[table_name]['columns'].append({
                'name': row.get('column_name'),
                'type': row.get('data_type'),
                'nullable': row.get('is_nullable', 'YES') == 'YES'
            })

            # Map curvature
            if curvature == "negative":
                curvature_mapping[table_name] = -1.0
            elif curvature == "zero":
                curvature_mapping[table_name] = 0.0
            else:
                curvature_mapping[table_name] = float(curvature)

        return cls(
            tables=tables,
            version="1.0",
            timestamp=time.time(),
            curvature_mapping=curvature_mapping
        )


@dataclass
class Watermark:
    """Watermark for incremental sync."""
    position: Any
    timestamp: float
    metadata: Dict[str, Any]


@dataclass
class DeltaBatch:
    """Batch of changes."""
    inserts: List[dict]
    updates: List[dict]
    deletes: List[dict]
    watermark: Watermark

    @classmethod
    def from_rows(cls, rows: List[dict]) -> 'DeltaBatch':
        """Create delta batch from rows."""
        import time

        # Simplified - would parse operation type
        return cls(
            inserts=rows,
            updates=[],
            deletes=[],
            watermark=Watermark(
                position=len(rows),
                timestamp=time.time(),
                metadata={}
            )
        )


class DatabaseAdapter(ABC):
    """
    Abstract base class for database adapters.

    Provides interface for connecting to external databases while
    preserving HyperSync's curvature semantics.
    """

    driver: str = "generic"

    def __init__(self, connection_string: str, **kwargs):
        self.connection_string = connection_string
        self.config = kwargs
        self.status = AdapterStatus.DISCONNECTED
        self._connection = None
        self._instrumentation_hooks = []

    @abstractmethod
    async def connect(self):
        """Establish connection to external database."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Close connection."""
        pass

    @abstractmethod
    async def introspect(self) -> SchemaSnapshot:
        """
        Introspect external schema.

        Returns:
            Schema snapshot with curvature mappings
        """
        pass

    @abstractmethod
    async def pull_delta(self, since: Watermark) -> DeltaBatch:
        """
        Pull incremental changes since watermark.

        Args:
            since: Last watermark

        Returns:
            Batch of changes
        """
        pass

    @abstractmethod
    async def push_delta(self, batch: DeltaBatch):
        """
        Push changes to external database.

        Args:
            batch: Changes to push
        """
        pass

    @abstractmethod
    async def stream_changes(self) -> AsyncIterator[dict]:
        """
        Stream changes in real-time.

        Yields:
            Change records
        """
        pass

    def add_instrumentation_hook(self, hook: callable):
        """Add instrumentation hook for policy enforcement."""
        self._instrumentation_hooks.append(hook)

    def _instrument(self, operation: str, context: dict):
        """Call instrumentation hooks."""
        for hook in self._instrumentation_hooks:
            try:
                hook(operation, context)
            except Exception as e:
                logger.error(f"Instrumentation hook failed: {e}")

    async def health_check(self) -> bool:
        """Check adapter health."""
        try:
            # Simple ping
            await self.introspect()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_status(self) -> AdapterStatus:
        """Get adapter status."""
        return self.status


# Export public API
__all__ = [
    'DatabaseAdapter',
    'SchemaSnapshot',
    'Watermark',
    'DeltaBatch',
    'AdapterStatus'
]
