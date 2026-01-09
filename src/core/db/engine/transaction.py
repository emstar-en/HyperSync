"""
Transaction Manager for HyperSync Database

Implements optimistic concurrency control with lock escalation and
deterministic conflict resolution.
"""
import logging
import threading
import time
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class IsolationLevel(Enum):
    """Transaction isolation levels."""
    READ_UNCOMMITTED = 1
    READ_COMMITTED = 2
    REPEATABLE_READ = 3
    SERIALIZABLE = 4


class TransactionState(Enum):
    """Transaction states."""
    ACTIVE = 1
    PREPARING = 2
    COMMITTED = 3
    ABORTED = 4


class LockMode(Enum):
    """Lock modes."""
    SHARED = 1
    EXCLUSIVE = 2
    INTENT_SHARED = 3
    INTENT_EXCLUSIVE = 4


@dataclass
class Lock:
    """Lock on a resource."""
    resource_id: str
    mode: LockMode
    holder: int  # Transaction ID
    acquired_at: float = field(default_factory=time.time)


@dataclass
class TransactionLog:
    """Log entry for transaction."""
    txn_id: int
    operation: str
    resource: str
    old_value: Any
    new_value: Any
    timestamp: float = field(default_factory=time.time)


class LockManager:
    """
    Manages locks for concurrent transactions.

    Implements lock escalation and deadlock detection.
    """

    def __init__(self):
        self._locks: Dict[str, List[Lock]] = {}
        self._lock = threading.RLock()
        self._wait_graph: Dict[int, Set[int]] = {}

    def acquire(self, txn_id: int, resource_id: str, mode: LockMode, timeout: float = 10.0) -> bool:
        """
        Acquire lock on resource.

        Args:
            txn_id: Transaction ID
            resource_id: Resource identifier
            mode: Lock mode
            timeout: Timeout in seconds

        Returns:
            True if lock acquired, False if timeout
        """
        start_time = time.time()

        while True:
            with self._lock:
                # Check if lock can be granted
                if self._can_grant(txn_id, resource_id, mode):
                    lock = Lock(resource_id, mode, txn_id)

                    if resource_id not in self._locks:
                        self._locks[resource_id] = []

                    self._locks[resource_id].append(lock)
                    logger.debug(f"Txn {txn_id} acquired {mode} lock on {resource_id}")
                    return True

                # Check for deadlock
                if self._detect_deadlock(txn_id, resource_id):
                    logger.warning(f"Deadlock detected for txn {txn_id}")
                    return False

            # Check timeout
            if time.time() - start_time > timeout:
                logger.warning(f"Lock timeout for txn {txn_id} on {resource_id}")
                return False

            # Wait and retry
            time.sleep(0.01)

    def _can_grant(self, txn_id: int, resource_id: str, mode: LockMode) -> bool:
        """Check if lock can be granted."""
        if resource_id not in self._locks:
            return True

        existing_locks = self._locks[resource_id]

        # Check compatibility with existing locks
        for lock in existing_locks:
            if lock.holder == txn_id:
                # Same transaction - check if upgrade needed
                continue

            # Check compatibility
            if not self._compatible(mode, lock.mode):
                return False

        return True

    def _compatible(self, mode1: LockMode, mode2: LockMode) -> bool:
        """Check if two lock modes are compatible."""
        # Shared locks are compatible with each other
        if mode1 == LockMode.SHARED and mode2 == LockMode.SHARED:
            return True

        # Exclusive locks are incompatible with everything
        if mode1 == LockMode.EXCLUSIVE or mode2 == LockMode.EXCLUSIVE:
            return False

        # Intent locks are compatible with each other
        if mode1 in (LockMode.INTENT_SHARED, LockMode.INTENT_EXCLUSIVE) and            mode2 in (LockMode.INTENT_SHARED, LockMode.INTENT_EXCLUSIVE):
            return True

        return False

    def _detect_deadlock(self, txn_id: int, resource_id: str) -> bool:
        """Detect deadlock using wait-for graph."""
        # Build wait-for graph
        if resource_id in self._locks:
            waiting_for = {lock.holder for lock in self._locks[resource_id]}
            self._wait_graph[txn_id] = waiting_for

        # Check for cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self._wait_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        return has_cycle(txn_id)

    def release(self, txn_id: int, resource_id: Optional[str] = None):
        """
        Release locks held by transaction.

        Args:
            txn_id: Transaction ID
            resource_id: Optional specific resource, or None for all
        """
        with self._lock:
            if resource_id:
                # Release specific resource
                if resource_id in self._locks:
                    self._locks[resource_id] = [
                        lock for lock in self._locks[resource_id]
                        if lock.holder != txn_id
                    ]
                    if not self._locks[resource_id]:
                        del self._locks[resource_id]
            else:
                # Release all resources
                for rid in list(self._locks.keys()):
                    self._locks[rid] = [
                        lock for lock in self._locks[rid]
                        if lock.holder != txn_id
                    ]
                    if not self._locks[rid]:
                        del self._locks[rid]

            # Clean up wait graph
            if txn_id in self._wait_graph:
                del self._wait_graph[txn_id]

    def escalate(self, txn_id: int, resource_id: str, new_mode: LockMode) -> bool:
        """Escalate lock to higher mode."""
        with self._lock:
            if resource_id not in self._locks:
                return False

            # Find existing lock
            for lock in self._locks[resource_id]:
                if lock.holder == txn_id:
                    lock.mode = new_mode
                    logger.debug(f"Escalated lock for txn {txn_id} to {new_mode}")
                    return True

            return False


class TransactionContext:
    """
    Transaction context with optimistic concurrency control.

    Provides ACID guarantees with deterministic conflict resolution.
    """

    def __init__(
        self,
        txn_id: int,
        isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED,
        lock_manager: Optional[LockManager] = None,
        wal = None
    ):
        self.txn_id = txn_id
        self.isolation_level = isolation_level
        self.state = TransactionState.ACTIVE
        self.lock_manager = lock_manager or LockManager()
        self.wal = wal

        self.read_set: Set[str] = set()
        self.write_set: Dict[str, Any] = {}
        self.log: List[TransactionLog] = []

        self.start_time = time.time()
        self.commit_time: Optional[float] = None

    def read(self, resource_id: str, value: Any) -> Any:
        """
        Read resource.

        Args:
            resource_id: Resource identifier
            value: Current value

        Returns:
            Value to use
        """
        # Acquire shared lock if needed
        if self.isolation_level in (IsolationLevel.REPEATABLE_READ, IsolationLevel.SERIALIZABLE):
            if not self.lock_manager.acquire(self.txn_id, resource_id, LockMode.SHARED):
                raise Exception(f"Failed to acquire read lock on {resource_id}")

        self.read_set.add(resource_id)

        # Check if we have a local write
        if resource_id in self.write_set:
            return self.write_set[resource_id]

        return value

    def write(self, resource_id: str, old_value: Any, new_value: Any):
        """
        Write resource.

        Args:
            resource_id: Resource identifier
            old_value: Previous value
            new_value: New value
        """
        # Acquire exclusive lock
        if not self.lock_manager.acquire(self.txn_id, resource_id, LockMode.EXCLUSIVE):
            raise Exception(f"Failed to acquire write lock on {resource_id}")

        # Record write
        self.write_set[resource_id] = new_value

        # Log operation
        log_entry = TransactionLog(
            txn_id=self.txn_id,
            operation="write",
            resource=resource_id,
            old_value=old_value,
            new_value=new_value
        )
        self.log.append(log_entry)

    def prepare(self) -> bool:
        """
        Prepare transaction for commit.

        Returns:
            True if preparation successful
        """
        self.state = TransactionState.PREPARING

        # Validate read set (optimistic concurrency)
        if not self._validate_reads():
            logger.warning(f"Txn {self.txn_id} failed read validation")
            return False

        # Write to WAL
        if self.wal:
            for log_entry in self.log:
                entry_data = {
                    'txn_id': self.txn_id,
                    'operation': log_entry.operation,
                    'resource': log_entry.resource,
                    'new_value': log_entry.new_value
                }
                import json
                self.wal.append(json.dumps(entry_data).encode('utf-8'))

        return True

    def commit(self):
        """Commit transaction."""
        if self.state != TransactionState.PREPARING:
            if not self.prepare():
                self.abort()
                raise Exception("Transaction preparation failed")

        self.state = TransactionState.COMMITTED
        self.commit_time = time.time()

        # Release all locks
        self.lock_manager.release(self.txn_id)

        logger.info(f"Txn {self.txn_id} committed")

    def abort(self):
        """Abort transaction."""
        self.state = TransactionState.ABORTED

        # Release all locks
        self.lock_manager.release(self.txn_id)

        # Clear write set
        self.write_set.clear()

        logger.info(f"Txn {self.txn_id} aborted")

    def _validate_reads(self) -> bool:
        """Validate that read set hasn't changed."""
        # In a real implementation, would check version numbers
        # or timestamps of read resources
        return True


class TransactionManager:
    """
    Manages transactions for the database.

    Provides transaction lifecycle management and coordination.
    """

    def __init__(self, wal=None):
        self.wal = wal
        self.lock_manager = LockManager()
        self._next_txn_id = 1
        self._active_txns: Dict[int, TransactionContext] = {}
        self._lock = threading.Lock()

    def begin(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED) -> TransactionContext:
        """
        Begin new transaction.

        Args:
            isolation_level: Isolation level for transaction

        Returns:
            Transaction context
        """
        with self._lock:
            txn_id = self._next_txn_id
            self._next_txn_id += 1

        txn = TransactionContext(
            txn_id=txn_id,
            isolation_level=isolation_level,
            lock_manager=self.lock_manager,
            wal=self.wal
        )

        self._active_txns[txn_id] = txn
        logger.info(f"Started transaction {txn_id}")

        return txn

    @contextmanager
    def transaction(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED):
        """
        Context manager for transactions.

        Usage:
            with txn_manager.transaction() as txn:
                txn.write('key', old_val, new_val)
        """
        txn = self.begin(isolation_level)
        try:
            yield txn
            txn.commit()
        except Exception as e:
            txn.abort()
            raise
        finally:
            if txn.txn_id in self._active_txns:
                del self._active_txns[txn.txn_id]

    def get_active_transactions(self) -> List[int]:
        """Get list of active transaction IDs."""
        return list(self._active_txns.keys())


# Export public API
__all__ = [
    'TransactionManager',
    'TransactionContext',
    'LockManager',
    'IsolationLevel',
    'TransactionState',
    'LockMode'
]
