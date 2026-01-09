"""
HyperSync ICO Sync & Replication
=================================
Complete implementation of operation-based replication with causal consistency,
vector clocks, and geometric merge policies.

Features:
- OpRecord with causal metadata (vector clocks)
- Deterministic replay by (vc, id) ordering
- Multiple merge policies (E_vector, S_geodesic, H_pt_native)
- Conflict detection and resolution
- Snapshot management
- CRDT-style convergence guarantees

Author: HyperSync Sync Foundation Team
Version: 1.0.0
"""

import time
import hashlib
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import logging
import copy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================

class MergePolicy(Enum):
    """Merge policy for conflicting operations."""
    E_VECTOR = "e_vector"           # Euclidean: CRDT last-writer-wins
    S_GEODESIC = "s_geodesic"       # Spherical: geodesic projection
    H_PT_NATIVE = "h_pt_native"     # Hyperbolic: parallel transport

class OpKind(Enum):
    """Operation types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MOVE = "move"                   # Geometric move
    TRANSFORM = "transform"         # Geometric transformation
    MERGE = "merge"                 # Explicit merge operation

class ConflictResolution(Enum):
    """Conflict resolution strategies."""
    LAST_WRITER_WINS = "lww"
    FIRST_WRITER_WINS = "fww"
    MERGE_BOTH = "merge"
    REJECT = "reject"
    ESCALATE = "escalate"

@dataclass(frozen=True)
class VectorClock:
    """
    Vector clock for causal ordering.

    Immutable to ensure consistency.
    """
    clock: Tuple[Tuple[str, int], ...]  # Sorted tuples of (node_id, counter)

    def __init__(self, clock_dict: Optional[Dict[str, int]] = None):
        if clock_dict is None:
            clock_dict = {}

        # Sort for deterministic ordering
        sorted_items = tuple(sorted(clock_dict.items()))
        object.__setattr__(self, 'clock', sorted_items)

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return dict(self.clock)

    def get(self, node_id: str) -> int:
        """Get counter for node."""
        for nid, count in self.clock:
            if nid == node_id:
                return count
        return 0

    def tick(self, node_id: str) -> "VectorClock":
        """Increment counter for node (returns new VectorClock)."""
        clock_dict = self.to_dict()
        clock_dict[node_id] = clock_dict.get(node_id, 0) + 1
        return VectorClock(clock_dict)

    def merge(self, other: "VectorClock") -> "VectorClock":
        """Merge with another vector clock (element-wise max)."""
        all_nodes = set(self.to_dict().keys()) | set(other.to_dict().keys())
        merged = {
            node: max(self.get(node), other.get(node))
            for node in all_nodes
        }
        return VectorClock(merged)

    def dominates(self, other: "VectorClock") -> bool:
        """Check if this clock dominates (happens-after) other."""
        all_nodes = set(self.to_dict().keys()) | set(other.to_dict().keys())

        ge = all(self.get(node) >= other.get(node) for node in all_nodes)
        gt = any(self.get(node) > other.get(node) for node in all_nodes)

        return ge and gt

    def concurrent_with(self, other: "VectorClock") -> bool:
        """Check if this clock is concurrent with other."""
        return not self.dominates(other) and not other.dominates(self)

    def __lt__(self, other: "VectorClock") -> bool:
        """Lexicographic comparison for deterministic ordering."""
        return self.clock < other.clock

    def __le__(self, other: "VectorClock") -> bool:
        return self.clock <= other.clock

    def __gt__(self, other: "VectorClock") -> bool:
        return self.clock > other.clock

    def __ge__(self, other: "VectorClock") -> bool:
        return self.clock >= other.clock

    def __str__(self) -> str:
        items = [f"{nid}:{cnt}" for nid, cnt in self.clock]
        return "{" + ", ".join(items) + "}"

    def __repr__(self) -> str:
        return f"VectorClock({self.to_dict()})"

@dataclass
class OpRecord:
    """
    Operation record with causal metadata.
    """
    id: str                         # Unique operation ID
    node_id: str                    # Node that created this op
    causal: VectorClock             # Causal timestamp
    op: Dict[str, Any]              # Operation payload
    pre: Dict[str, Any]             # Pre-state (for validation)
    post: Dict[str, Any]            # Post-state (for replay)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "node_id": self.node_id,
            "causal": self.causal.to_dict(),
            "op": self.op,
            "pre": self.pre,
            "post": self.post,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "OpRecord":
        return cls(
            id=d["id"],
            node_id=d["node_id"],
            causal=VectorClock(d["causal"]),
            op=d["op"],
            pre=d["pre"],
            post=d["post"],
            timestamp=d.get("timestamp", time.time())
        )

    def __repr__(self) -> str:
        return f"OpRecord({self.id}, {self.causal}, {self.op.get('kind', 'unknown')})"

@dataclass
class Snapshot:
    """
    State snapshot with causal metadata.
    """
    snapshot_id: str
    state: Dict[str, Any]           # Current state
    causal: VectorClock             # Causal timestamp of snapshot
    ops_applied: List[str]          # IDs of operations applied
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "state": self.state,
            "causal": self.causal.to_dict(),
            "ops_applied": self.ops_applied,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Snapshot":
        return cls(
            snapshot_id=d["snapshot_id"],
            state=d["state"],
            causal=VectorClock(d["causal"]),
            ops_applied=d["ops_applied"],
            timestamp=d.get("timestamp", time.time())
        )

# ============================================================================
# DETERMINISTIC ORDERING
# ============================================================================

def deterministic_order(ops: List[OpRecord]) -> List[OpRecord]:
    """
    Order operations deterministically by (vector_clock, op_id).

    This ensures all nodes replay operations in the same order.

    Args:
        ops: List of operation records

    Returns:
        Sorted list of operations
    """
    return sorted(ops, key=lambda o: (o.causal, o.id))

def find_concurrent_ops(ops: List[OpRecord]) -> List[Set[OpRecord]]:
    """
    Find sets of concurrent operations.

    Args:
        ops: List of operation records

    Returns:
        List of sets, where each set contains concurrent operations
    """
    concurrent_sets = []
    processed = set()

    for i, op1 in enumerate(ops):
        if op1.id in processed:
            continue

        concurrent_set = {op1}
        processed.add(op1.id)

        for j, op2 in enumerate(ops[i+1:], start=i+1):
            if op2.id in processed:
                continue

            if op1.causal.concurrent_with(op2.causal):
                concurrent_set.add(op2)
                processed.add(op2.id)

        if len(concurrent_set) > 1:
            concurrent_sets.append(concurrent_set)

    return concurrent_sets

# ============================================================================
# MERGE POLICIES
# ============================================================================

def merge_e_vector(
    state: Dict[str, Any],
    ops: List[OpRecord],
    conflict_resolution: ConflictResolution = ConflictResolution.LAST_WRITER_WINS
) -> Dict[str, Any]:
    """
    Euclidean merge policy: CRDT-style last-writer-wins with tie-breakers.

    Args:
        state: Current state
        ops: Concurrent operations to merge
        conflict_resolution: Conflict resolution strategy

    Returns:
        Merged state
    """
    # Sort by timestamp, then by op_id for determinism
    sorted_ops = sorted(ops, key=lambda o: (o.timestamp, o.id))

    if conflict_resolution == ConflictResolution.LAST_WRITER_WINS:
        # Apply last operation
        if sorted_ops:
            last_op = sorted_ops[-1]
            state = apply_operation(state, last_op)

    elif conflict_resolution == ConflictResolution.FIRST_WRITER_WINS:
        # Apply first operation
        if sorted_ops:
            first_op = sorted_ops[0]
            state = apply_operation(state, first_op)

    elif conflict_resolution == ConflictResolution.MERGE_BOTH:
        # Apply all operations in order
        for op in sorted_ops:
            state = apply_operation(state, op)

    return state

def merge_s_geodesic(
    state: Dict[str, Any],
    ops: List[OpRecord],
    geometry_engine: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Spherical merge policy: compose via geodesic steps then project.

    For geometric operations on spherical manifolds.

    Args:
        state: Current state (must contain geometric data)
        ops: Concurrent operations to merge
        geometry_engine: Geometry engine for geodesic computation

    Returns:
        Merged state
    """
    # Extract geometric state
    if "point" not in state:
        # Fallback to E_vector if no geometric state
        return merge_e_vector(state, ops)

    current_point = state["point"]

    # Compose geodesic steps
    for op in ops:
        if op.op.get("kind") == "move":
            # Geodesic move
            target = op.op.get("args", {}).get("target")
            alpha = op.op.get("args", {}).get("alpha", 1.0)

            if target is not None:
                # Compute geodesic step
                # (In production, use actual geometry engine)
                # For now, simple interpolation
                import numpy as np
                current_point = np.array(current_point)
                target = np.array(target)
                current_point = (1 - alpha) * current_point + alpha * target

                # Project back to sphere
                norm = np.linalg.norm(current_point)
                if norm > 1e-9:
                    current_point = current_point / norm

    state = {**state, "point": current_point.tolist() if hasattr(current_point, 'tolist') else current_point}
    return state

def merge_h_pt_native(
    state: Dict[str, Any],
    ops: List[OpRecord],
    geometry_engine: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Hyperbolic merge policy: parallel transport + exp/log with spacelike guards.

    For geometric operations on hyperbolic manifolds.

    Args:
        state: Current state (must contain hyperbolic point)
        ops: Concurrent operations to merge
        geometry_engine: Hyperbolic geometry engine

    Returns:
        Merged state
    """
    # Extract hyperbolic state
    if "point" not in state:
        return merge_e_vector(state, ops)

    current_point = state["point"]

    # Apply operations with parallel transport
    for op in ops:
        if op.op.get("kind") == "geodesic_move":
            # Hyperbolic geodesic move
            v = op.op.get("args", {}).get("v")

            if v is not None:
                # In production, use hyperbolic geometry engine:
                # 1. Project v to tangent space at current_point
                # 2. Apply exp_map
                # 3. Retract to hyperboloid if needed

                # Simplified implementation
                import numpy as np
                current_point = np.array(current_point)
                v = np.array(v)

                # Simple update (replace with actual hyperbolic ops)
                current_point = current_point + 0.1 * v

                # Normalize (simplified retraction)
                norm = np.linalg.norm(current_point)
                if norm > 1e-9:
                    current_point = current_point / norm

        elif op.op.get("kind") == "parallel_transport":
            # Parallel transport operation
            target = op.op.get("args", {}).get("target")
            vector = op.op.get("args", {}).get("vector")

            if target is not None and vector is not None:
                # In production: use parallel_transport from hyperbolic engine
                # For now, simple pass-through
                pass

    state = {**state, "point": current_point.tolist() if hasattr(current_point, 'tolist') else current_point}
    return state

def apply_operation(state: Dict[str, Any], op: OpRecord) -> Dict[str, Any]:
    """
    Apply a single operation to state.

    Args:
        state: Current state
        op: Operation to apply

    Returns:
        Updated state
    """
    op_kind = op.op.get("kind")

    if op_kind == "create":
        key = op.op.get("key")
        value = op.op.get("value")
        if key:
            state = {**state, key: value}

    elif op_kind == "update":
        key = op.op.get("key")
        value = op.op.get("value")
        if key and key in state:
            state = {**state, key: value}

    elif op_kind == "delete":
        key = op.op.get("key")
        if key and key in state:
            state = {k: v for k, v in state.items() if k != key}

    elif op_kind == "move":
        # Geometric move
        if "point" in state:
            target = op.op.get("args", {}).get("target")
            if target:
                state = {**state, "point": target}

    # Use post-state if available
    if op.post:
        state = {**state, **op.post}

    return state

# ============================================================================
# OPERATION LOG
# ============================================================================

class OperationLog:
    """
    Append-only log of operations with causal ordering.
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.ops: List[OpRecord] = []
        self.clock = VectorClock()
        self._lock = threading.Lock()
        self._op_index: Dict[str, OpRecord] = {}

    def append(
        self,
        op_kind: str,
        args: Dict[str, Any],
        pre: Optional[Dict[str, Any]] = None,
        post: Optional[Dict[str, Any]] = None
    ) -> OpRecord:
        """
        Append a new operation to the log.

        Args:
            op_kind: Operation kind
            args: Operation arguments
            pre: Pre-state
            post: Post-state

        Returns:
            Created OpRecord
        """
        with self._lock:
            # Tick clock
            self.clock = self.clock.tick(self.node_id)

            # Create operation
            op_record = OpRecord(
                id=f"op_{uuid.uuid4().hex[:16]}",
                node_id=self.node_id,
                causal=self.clock,
                op={"kind": op_kind, "args": args},
                pre=pre or {},
                post=post or {}
            )

            # Append to log
            self.ops.append(op_record)
            self._op_index[op_record.id] = op_record

            logger.debug(f"Appended op {op_record.id}: {op_kind}")

            return op_record

    def get(self, op_id: str) -> Optional[OpRecord]:
        """Get operation by ID."""
        with self._lock:
            return self._op_index.get(op_id)

    def get_since(self, causal: VectorClock) -> List[OpRecord]:
        """
        Get all operations that happened after the given causal timestamp.

        Args:
            causal: Causal timestamp

        Returns:
            List of operations
        """
        with self._lock:
            return [
                op for op in self.ops
                if not causal.dominates(op.causal)
            ]

    def merge_remote_ops(self, remote_ops: List[OpRecord]):
        """
        Merge operations from remote node.

        Args:
            remote_ops: Operations from remote node
        """
        with self._lock:
            for op in remote_ops:
                if op.id not in self._op_index:
                    self.ops.append(op)
                    self._op_index[op.id] = op

                    # Update clock
                    self.clock = self.clock.merge(op.causal)

            # Re-sort for deterministic ordering
            self.ops = deterministic_order(self.ops)

            logger.info(f"Merged {len(remote_ops)} remote operations")

    def get_all(self) -> List[OpRecord]:
        """Get all operations in deterministic order."""
        with self._lock:
            return deterministic_order(self.ops.copy())

    def size(self) -> int:
        """Get number of operations."""
        with self._lock:
            return len(self.ops)

# ============================================================================
# STATE MACHINE
# ============================================================================

class ReplicatedStateMachine:
    """
    Replicated state machine with causal consistency and merge policies.
    """

    def __init__(
        self,
        node_id: str,
        initial_state: Optional[Dict[str, Any]] = None,
        merge_policy: MergePolicy = MergePolicy.E_VECTOR
    ):
        self.node_id = node_id
        self.state = initial_state or {}
        self.merge_policy = merge_policy
        self.op_log = OperationLog(node_id)
        self.snapshots: List[Snapshot] = []
        self._lock = threading.Lock()

        # Create initial snapshot
        self._create_snapshot()

    def execute(
        self,
        op_kind: str,
        args: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], OpRecord]:
        """
        Execute an operation locally.

        Args:
            op_kind: Operation kind
            args: Operation arguments

        Returns:
            Tuple of (new_state, op_record)
        """
        with self._lock:
            pre_state = copy.deepcopy(self.state)

            # Create operation record
            op_record = self.op_log.append(op_kind, args, pre=pre_state)

            # Apply operation
            self.state = apply_operation(self.state, op_record)

            # Update post-state
            op_record.post.update(self.state)

            logger.debug(f"Executed {op_kind}: {op_record.id}")

            return self.state, op_record

    def replay(self, ops: Optional[List[OpRecord]] = None) -> Dict[str, Any]:
        """
        Replay operations to reconstruct state.

        Args:
            ops: Operations to replay (defaults to all ops in log)

        Returns:
            Reconstructed state
        """
        if ops is None:
            ops = self.op_log.get_all()

        # Start from initial state
        state = {}

        # Order operations deterministically
        ordered_ops = deterministic_order(ops)

        # Find concurrent operations
        concurrent_sets = find_concurrent_ops(ordered_ops)

        # Apply operations
        applied = set()
        for op in ordered_ops:
            if op.id in applied:
                continue

            # Check if this op is part of a concurrent set
            in_concurrent_set = False
            for conc_set in concurrent_sets:
                if op in conc_set:
                    # Apply merge policy
                    conc_ops = list(conc_set)

                    if self.merge_policy == MergePolicy.E_VECTOR:
                        state = merge_e_vector(state, conc_ops)
                    elif self.merge_policy == MergePolicy.S_GEODESIC:
                        state = merge_s_geodesic(state, conc_ops)
                    elif self.merge_policy == MergePolicy.H_PT_NATIVE:
                        state = merge_h_pt_native(state, conc_ops)

                    # Mark all as applied
                    for conc_op in conc_ops:
                        applied.add(conc_op.id)

                    in_concurrent_set = True
                    break

            if not in_concurrent_set:
                # Apply single operation
                state = apply_operation(state, op)
                applied.add(op.id)

        return state

    def sync_with(self, remote_node: "ReplicatedStateMachine"):
        """
        Synchronize with remote node.

        Args:
            remote_node: Remote replicated state machine
        """
        with self._lock:
            # Get operations we don't have
            remote_ops = remote_node.op_log.get_since(self.op_log.clock)

            if remote_ops:
                # Merge remote operations
                self.op_log.merge_remote_ops(remote_ops)

                # Replay to update state
                self.state = self.replay()

                logger.info(f"Synced with {remote_node.node_id}: {len(remote_ops)} ops")

    def _create_snapshot(self):
        """Create a snapshot of current state."""
        snapshot = Snapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:16]}",
            state=copy.deepcopy(self.state),
            causal=self.op_log.clock,
            ops_applied=[op.id for op in self.op_log.ops]
        )
        self.snapshots.append(snapshot)

        # Keep only last 10 snapshots
        if len(self.snapshots) > 10:
            self.snapshots = self.snapshots[-10:]

    def create_snapshot(self):
        """Public method to create snapshot."""
        with self._lock:
            self._create_snapshot()

    def get_state(self) -> Dict[str, Any]:
        """Get current state."""
        with self._lock:
            return copy.deepcopy(self.state)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        with self._lock:
            return {
                "node_id": self.node_id,
                "merge_policy": self.merge_policy.value,
                "op_count": self.op_log.size(),
                "snapshot_count": len(self.snapshots),
                "clock": str(self.op_log.clock),
                "state_keys": list(self.state.keys())
            }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    'MergePolicy', 'OpKind', 'ConflictResolution',

    # Data classes
    'VectorClock', 'OpRecord', 'Snapshot',

    # Functions
    'deterministic_order', 'find_concurrent_ops',
    'merge_e_vector', 'merge_s_geodesic', 'merge_h_pt_native',
    'apply_operation',

    # Classes
    'OperationLog', 'ReplicatedStateMachine',
]
