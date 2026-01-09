"""
File Change Detection and Coordination
Monitors filesystem changes and coordinates access between agents.
"""

import os
import time
import threading
import logging
from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of file changes"""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class FileChange:
    """Represents a file change event"""
    path: str
    change_type: ChangeType
    timestamp: datetime
    agent_id: Optional[str] = None
    old_path: Optional[str] = None  # For moves
    checksum: Optional[str] = None
    size: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "change_type": self.change_type.value,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "old_path": self.old_path,
            "checksum": self.checksum,
            "size": self.size
        }


@dataclass
class FileLock:
    """Represents a file lock"""
    path: str
    agent_id: str
    lock_type: str  # "read" or "write"
    acquired_at: datetime
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if lock has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


class FileWatcher:
    """Watches files for changes"""

    def __init__(self, poll_interval: float = 1.0):
        """
        Initialize file watcher.

        Args:
            poll_interval: How often to check for changes (seconds)
        """
        self.poll_interval = poll_interval
        self.watched_paths: Dict[str, Dict] = {}  # path -> {mtime, size, checksum}
        self.callbacks: List[Callable[[FileChange], None]] = []
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        logger.info("FileWatcher initialized")

    def watch(self, path: str):
        """
        Start watching a path.

        Args:
            path: Path to watch
        """
        path = os.path.abspath(path)

        with self._lock:
            if path not in self.watched_paths:
                # Get initial state
                if os.path.exists(path):
                    stat = os.stat(path)
                    self.watched_paths[path] = {
                        "mtime": stat.st_mtime,
                        "size": stat.st_size,
                        "exists": True
                    }
                else:
                    self.watched_paths[path] = {
                        "exists": False
                    }

                logger.info(f"Watching path: {path}")

    def unwatch(self, path: str):
        """Stop watching a path"""
        path = os.path.abspath(path)

        with self._lock:
            if path in self.watched_paths:
                del self.watched_paths[path]
                logger.info(f"Stopped watching: {path}")

    def add_callback(self, callback: Callable[[FileChange], None]):
        """Add a callback for file changes"""
        self.callbacks.append(callback)

    def start(self):
        """Start watching for changes"""
        if self.running:
            logger.warning("FileWatcher already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
        logger.info("FileWatcher started")

    def stop(self):
        """Stop watching for changes"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
        logger.info("FileWatcher stopped")

    def _watch_loop(self):
        """Main watch loop"""
        while self.running:
            try:
                self._check_changes()
            except Exception as e:
                logger.error(f"Error in watch loop: {e}")

            time.sleep(self.poll_interval)

    def _check_changes(self):
        """Check for file changes"""
        with self._lock:
            paths = list(self.watched_paths.keys())

        for path in paths:
            try:
                self._check_path(path)
            except Exception as e:
                logger.error(f"Error checking {path}: {e}")

    def _check_path(self, path: str):
        """Check a specific path for changes"""
        with self._lock:
            old_state = self.watched_paths.get(path)
            if not old_state:
                return

        exists = os.path.exists(path)

        # File was deleted
        if old_state.get("exists") and not exists:
            change = FileChange(
                path=path,
                change_type=ChangeType.DELETED,
                timestamp=datetime.utcnow()
            )
            self._notify_change(change)

            with self._lock:
                self.watched_paths[path] = {"exists": False}
            return

        # File was created
        if not old_state.get("exists") and exists:
            stat = os.stat(path)
            change = FileChange(
                path=path,
                change_type=ChangeType.CREATED,
                timestamp=datetime.utcnow(),
                size=stat.st_size
            )
            self._notify_change(change)

            with self._lock:
                self.watched_paths[path] = {
                    "mtime": stat.st_mtime,
                    "size": stat.st_size,
                    "exists": True
                }
            return

        # File was modified
        if exists:
            stat = os.stat(path)
            old_mtime = old_state.get("mtime", 0)
            old_size = old_state.get("size", 0)

            if stat.st_mtime > old_mtime or stat.st_size != old_size:
                change = FileChange(
                    path=path,
                    change_type=ChangeType.MODIFIED,
                    timestamp=datetime.utcnow(),
                    size=stat.st_size
                )
                self._notify_change(change)

                with self._lock:
                    self.watched_paths[path] = {
                        "mtime": stat.st_mtime,
                        "size": stat.st_size,
                        "exists": True
                    }

    def _notify_change(self, change: FileChange):
        """Notify callbacks of a change"""
        logger.info(f"File change detected: {change.path} ({change.change_type.value})")

        for callback in self.callbacks:
            try:
                callback(change)
            except Exception as e:
                logger.error(f"Callback error: {e}")


class FileCoordinator:
    """Coordinates file access between agents"""

    def __init__(self):
        """Initialize file coordinator"""
        self.locks: Dict[str, FileLock] = {}
        self.change_history: List[FileChange] = []
        self.watcher = FileWatcher()
        self._lock = threading.Lock()

        # Register watcher callback
        self.watcher.add_callback(self._on_file_change)

        logger.info("FileCoordinator initialized")

    def start(self):
        """Start coordinator"""
        self.watcher.start()
        logger.info("FileCoordinator started")

    def stop(self):
        """Stop coordinator"""
        self.watcher.stop()
        logger.info("FileCoordinator stopped")

    def watch_file(self, path: str):
        """Start watching a file"""
        self.watcher.watch(path)

    def acquire_lock(
        self,
        path: str,
        agent_id: str,
        lock_type: str = "write",
        timeout: Optional[float] = None
    ) -> bool:
        """
        Acquire a lock on a file.

        Args:
            path: File path
            agent_id: Agent requesting lock
            lock_type: "read" or "write"
            timeout: Lock timeout in seconds

        Returns:
            True if lock acquired, False otherwise
        """
        path = os.path.abspath(path)

        with self._lock:
            # Check if already locked
            existing = self.locks.get(path)
            if existing:
                # Check if expired
                if existing.is_expired():
                    del self.locks[path]
                else:
                    # Can't acquire write lock if any lock exists
                    if lock_type == "write":
                        logger.warning(f"Lock denied: {path} (already locked)")
                        return False
                    # Can acquire read lock if existing is also read
                    if existing.lock_type == "write":
                        logger.warning(f"Lock denied: {path} (write locked)")
                        return False

            # Acquire lock
            expires_at = None
            if timeout:
                from datetime import timedelta
                expires_at = datetime.utcnow() + timedelta(seconds=timeout)

            lock = FileLock(
                path=path,
                agent_id=agent_id,
                lock_type=lock_type,
                acquired_at=datetime.utcnow(),
                expires_at=expires_at
            )

            self.locks[path] = lock
            logger.info(f"Lock acquired: {path} by {agent_id} ({lock_type})")
            return True

    def release_lock(self, path: str, agent_id: str) -> bool:
        """
        Release a lock on a file.

        Args:
            path: File path
            agent_id: Agent releasing lock

        Returns:
            True if released, False if not locked or wrong agent
        """
        path = os.path.abspath(path)

        with self._lock:
            lock = self.locks.get(path)
            if not lock:
                logger.warning(f"No lock to release: {path}")
                return False

            if lock.agent_id != agent_id:
                logger.warning(f"Lock release denied: {path} (wrong agent)")
                return False

            del self.locks[path]
            logger.info(f"Lock released: {path} by {agent_id}")
            return True

    def is_locked(self, path: str) -> bool:
        """Check if file is locked"""
        path = os.path.abspath(path)

        with self._lock:
            lock = self.locks.get(path)
            if not lock:
                return False

            if lock.is_expired():
                del self.locks[path]
                return False

            return True

    def get_changes(
        self,
        path: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[FileChange]:
        """Get file change history"""
        changes = self.change_history

        if path:
            path = os.path.abspath(path)
            changes = [c for c in changes if c.path == path]

        if since:
            changes = [c for c in changes if c.timestamp > since]

        if limit:
            changes = changes[-limit:]

        return changes

    def _on_file_change(self, change: FileChange):
        """Handle file change event"""
        with self._lock:
            self.change_history.append(change)

            # Keep history limited
            if len(self.change_history) > 10000:
                self.change_history = self.change_history[-5000:]


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    coordinator = FileCoordinator()
    coordinator.start()

    # Watch a file
    test_file = "/tmp/test_watch.txt"
    coordinator.watch_file(test_file)

    # Acquire lock
    if coordinator.acquire_lock(test_file, "agent-1", "write"):
        print("Lock acquired")

        # Simulate file modification
        with open(test_file, 'w') as f:
            f.write("Test content")

        time.sleep(2)

        # Release lock
        coordinator.release_lock(test_file, "agent-1")

    # Get changes
    time.sleep(1)
    changes = coordinator.get_changes(path=test_file)
    print(f"Changes: {len(changes)}")
    for c in changes:
        print(f"  {c.change_type.value}: {c.path}")

    coordinator.stop()
