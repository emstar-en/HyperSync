"""
High-Risk Capability Controls and Rollback System
Provides controls for dangerous operations with rollback capabilities.
"""

import os
import json
import shutil
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import tempfile

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OperationType(Enum):
    """Types of operations"""
    FILE_DELETE = "file_delete"
    FILE_MODIFY = "file_modify"
    PROCESS_EXEC = "process_exec"
    NETWORK_ACCESS = "network_access"
    SYSTEM_MODIFY = "system_modify"


@dataclass
class Snapshot:
    """Represents a system snapshot"""
    snapshot_id: str
    created_at: datetime
    description: str
    files: Dict[str, str] = field(default_factory=dict)  # path -> backup_path
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "created_at": self.created_at.isoformat(),
            "description": self.description,
            "files": self.files,
            "metadata": self.metadata
        }


@dataclass
class Operation:
    """Represents a high-risk operation"""
    operation_id: str
    operation_type: OperationType
    risk_level: RiskLevel
    description: str
    agent_id: str
    snapshot_id: Optional[str] = None
    executed_at: Optional[datetime] = None
    rolled_back: bool = False
    rollback_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type.value,
            "risk_level": self.risk_level.value,
            "description": self.description,
            "agent_id": self.agent_id,
            "snapshot_id": self.snapshot_id,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "rolled_back": self.rolled_back,
            "rollback_at": self.rollback_at.isoformat() if self.rollback_at else None
        }


class RollbackManager:
    """Manages snapshots and rollbacks"""

    def __init__(self, snapshot_dir: str = "/tmp/hypersync_snapshots"):
        """
        Initialize rollback manager.

        Args:
            snapshot_dir: Directory to store snapshots
        """
        self.snapshot_dir = snapshot_dir
        self.snapshots: Dict[str, Snapshot] = {}
        self.operations: List[Operation] = []

        # Create snapshot directory
        os.makedirs(snapshot_dir, exist_ok=True)

        logger.info("RollbackManager initialized")

    def create_snapshot(
        self,
        paths: List[str],
        description: str = ""
    ) -> Snapshot:
        """
        Create a snapshot of files.

        Args:
            paths: List of file paths to snapshot
            description: Snapshot description

        Returns:
            Snapshot object
        """
        snapshot_id = f"snapshot-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        logger.info(f"Creating snapshot: {snapshot_id}")

        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            created_at=datetime.utcnow(),
            description=description
        )

        # Backup each file
        for path in paths:
            if os.path.exists(path):
                backup_path = self._backup_file(path, snapshot_id)
                snapshot.files[path] = backup_path
                logger.info(f"Backed up: {path} -> {backup_path}")

        self.snapshots[snapshot_id] = snapshot

        # Save snapshot metadata
        self._save_snapshot_metadata(snapshot)

        logger.info(f"Snapshot created: {snapshot_id} ({len(snapshot.files)} files)")

        return snapshot

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore a snapshot.

        Args:
            snapshot_id: Snapshot to restore

        Returns:
            True if restored, False otherwise
        """
        snapshot = self.snapshots.get(snapshot_id)
        if not snapshot:
            logger.error(f"Snapshot not found: {snapshot_id}")
            return False

        logger.info(f"Restoring snapshot: {snapshot_id}")

        restored_count = 0
        for original_path, backup_path in snapshot.files.items():
            try:
                if os.path.exists(backup_path):
                    # Restore file
                    os.makedirs(os.path.dirname(original_path), exist_ok=True)
                    shutil.copy2(backup_path, original_path)
                    restored_count += 1
                    logger.info(f"Restored: {original_path}")
                else:
                    logger.warning(f"Backup not found: {backup_path}")
            except Exception as e:
                logger.error(f"Failed to restore {original_path}: {e}")

        logger.info(f"Restored {restored_count}/{len(snapshot.files)} files")

        return restored_count > 0

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot"""
        snapshot = self.snapshots.get(snapshot_id)
        if not snapshot:
            return False

        # Delete backup files
        for backup_path in snapshot.files.values():
            try:
                if os.path.exists(backup_path):
                    os.unlink(backup_path)
            except Exception as e:
                logger.error(f"Failed to delete backup {backup_path}: {e}")

        # Delete metadata
        metadata_path = os.path.join(self.snapshot_dir, f"{snapshot_id}.json")
        if os.path.exists(metadata_path):
            os.unlink(metadata_path)

        del self.snapshots[snapshot_id]
        logger.info(f"Deleted snapshot: {snapshot_id}")

        return True

    def list_snapshots(self) -> List[Snapshot]:
        """List all snapshots"""
        return list(self.snapshots.values())

    def _backup_file(self, path: str, snapshot_id: str) -> str:
        """Backup a file"""
        # Create backup filename
        filename = os.path.basename(path)
        backup_filename = f"{snapshot_id}_{filename}"
        backup_path = os.path.join(self.snapshot_dir, backup_filename)

        # Copy file
        shutil.copy2(path, backup_path)

        return backup_path

    def _save_snapshot_metadata(self, snapshot: Snapshot):
        """Save snapshot metadata"""
        metadata_path = os.path.join(self.snapshot_dir, f"{snapshot.snapshot_id}.json")
        with open(metadata_path, 'w') as f:
            json.dump(snapshot.to_dict(), f, indent=2)


class HighRiskController:
    """Controls high-risk operations with rollback support"""

    def __init__(self, rollback_manager: RollbackManager):
        """
        Initialize high-risk controller.

        Args:
            rollback_manager: RollbackManager instance
        """
        self.rollback_manager = rollback_manager
        self.operations: List[Operation] = []
        self.approval_callbacks: List[Callable[[Operation], bool]] = []

        logger.info("HighRiskController initialized")

    def add_approval_callback(self, callback: Callable[[Operation], bool]):
        """Add approval callback"""
        self.approval_callbacks.append(callback)

    def execute_operation(
        self,
        operation_type: OperationType,
        risk_level: RiskLevel,
        description: str,
        agent_id: str,
        action: Callable,
        affected_paths: Optional[List[str]] = None,
        require_approval: bool = True
    ) -> tuple:
        """
        Execute a high-risk operation with rollback support.

        Args:
            operation_type: Type of operation
            risk_level: Risk level
            description: Operation description
            agent_id: Agent performing operation
            action: Function to execute
            affected_paths: Paths that will be affected
            require_approval: Whether approval is required

        Returns:
            Tuple of (success, result, operation)
        """
        operation_id = f"op-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        operation = Operation(
            operation_id=operation_id,
            operation_type=operation_type,
            risk_level=risk_level,
            description=description,
            agent_id=agent_id
        )

        logger.info(f"Executing {risk_level.value} risk operation: {description}")

        # Check approval
        if require_approval:
            approved = self._check_approval(operation)
            if not approved:
                logger.warning(f"Operation denied: {operation_id}")
                return False, None, operation

        # Create snapshot if paths provided
        if affected_paths:
            snapshot = self.rollback_manager.create_snapshot(
                affected_paths,
                description=f"Before: {description}"
            )
            operation.snapshot_id = snapshot.snapshot_id

        # Execute operation
        try:
            result = action()
            operation.executed_at = datetime.utcnow()
            logger.info(f"Operation completed: {operation_id}")
            success = True
        except Exception as e:
            logger.error(f"Operation failed: {e}")
            result = None
            success = False

            # Auto-rollback on failure if snapshot exists
            if operation.snapshot_id:
                logger.info("Auto-rolling back due to failure")
                self.rollback_operation(operation_id)

        self.operations.append(operation)

        return success, result, operation

    def rollback_operation(self, operation_id: str) -> bool:
        """
        Rollback an operation.

        Args:
            operation_id: Operation to rollback

        Returns:
            True if rolled back, False otherwise
        """
        operation = self._get_operation(operation_id)
        if not operation:
            logger.error(f"Operation not found: {operation_id}")
            return False

        if not operation.snapshot_id:
            logger.error(f"No snapshot for operation: {operation_id}")
            return False

        if operation.rolled_back:
            logger.warning(f"Operation already rolled back: {operation_id}")
            return False

        logger.info(f"Rolling back operation: {operation_id}")

        success = self.rollback_manager.restore_snapshot(operation.snapshot_id)

        if success:
            operation.rolled_back = True
            operation.rollback_at = datetime.utcnow()
            logger.info(f"Operation rolled back: {operation_id}")

        return success

    def get_operations(
        self,
        agent_id: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None
    ) -> List[Operation]:
        """Get operations"""
        ops = self.operations

        if agent_id:
            ops = [o for o in ops if o.agent_id == agent_id]

        if risk_level:
            ops = [o for o in ops if o.risk_level == risk_level]

        return ops

    def _check_approval(self, operation: Operation) -> bool:
        """Check if operation is approved"""
        # If no callbacks, auto-approve low/medium risk
        if not self.approval_callbacks:
            return operation.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]

        # Check all callbacks
        for callback in self.approval_callbacks:
            try:
                if not callback(operation):
                    return False
            except Exception as e:
                logger.error(f"Approval callback error: {e}")
                return False

        return True

    def _get_operation(self, operation_id: str) -> Optional[Operation]:
        """Get operation by ID"""
        for op in self.operations:
            if op.operation_id == operation_id:
                return op
        return None


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    # Create managers
    rollback_mgr = RollbackManager()
    controller = HighRiskController(rollback_mgr)

    # Define approval callback
    def approve_operation(op):
        print(f"Approve {op.risk_level.value} operation: {op.description}? (y/n)")
        # Auto-approve for demo
        return True

    controller.add_approval_callback(approve_operation)

    # Execute high-risk operation
    test_file = "/tmp/test_rollback.txt"
    with open(test_file, 'w') as f:
        f.write("Original content")

    def risky_action():
        with open(test_file, 'w') as f:
            f.write("Modified content")
        return "Success"

    success, result, operation = controller.execute_operation(
        operation_type=OperationType.FILE_MODIFY,
        risk_level=RiskLevel.HIGH,
        description="Modify critical file",
        agent_id="agent-1",
        action=risky_action,
        affected_paths=[test_file]
    )

    print(f"Operation success: {success}")
    print(f"Operation ID: {operation.operation_id}")

    # Rollback
    print("\nRolling back...")
    controller.rollback_operation(operation.operation_id)

    with open(test_file, 'r') as f:
        print(f"Content after rollback: {f.read()}")
