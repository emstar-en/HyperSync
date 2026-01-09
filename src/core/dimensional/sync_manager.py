"""
HyperSync Intra-Network Synchronization Manager

Provides node-to-node hyperbolic alignment and selective dimension sharing
for 10 GbE-style fabrics.
"""

import uuid
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SessionState(Enum):
    """Sync session states."""
    PENDING = "pending"
    HANDSHAKE = "handshake"
    TRANSFORM = "transform"
    RECONCILE = "reconcile"
    COMPLETE = "complete"
    FAILED = "failed"


class PassType(Enum):
    """Synchronization pass types."""
    METADATA = "metadata"
    TRANSPORT = "transport"
    RECONCILE = "reconcile"


class PassStatus(Enum):
    """Pass execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class NodeCapabilities:
    """Node dimensional capabilities."""
    node_id: str
    dimensions: int
    curvature: float
    protocols: List[str] = field(default_factory=lambda: ["poincare", "lorentz"])


@dataclass
class SyncPass:
    """Synchronization pass execution record."""
    pass_type: PassType
    status: PassStatus = PassStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metrics: Dict = field(default_factory=dict)

    def start(self):
        """Mark pass as started."""
        self.status = PassStatus.RUNNING
        self.started_at = datetime.now()

    def complete(self, metrics: Optional[Dict] = None):
        """Mark pass as complete."""
        self.status = PassStatus.COMPLETE
        self.completed_at = datetime.now()
        if metrics:
            self.metrics.update(metrics)

    def fail(self, error: str):
        """Mark pass as failed."""
        self.status = PassStatus.FAILED
        self.completed_at = datetime.now()
        self.metrics["error"] = error


class HyperbolicTransform:
    """
    Manages coordinate transformations between hyperbolic spaces.

    Supports multiple models: Poincaré, Lorentz, Klein, Hyperboloid
    """

    def __init__(self, method: str = "poincare"):
        if method not in ["poincare", "lorentz", "klein", "hyperboloid"]:
            raise ValueError(f"Unknown transform method: {method}")
        self.method = method
        self.matrix: Optional[np.ndarray] = None
        self.curvature_adjustment: float = 0.0

    def compute_transform(self, source_dims: int, target_dims: int,
                         source_curvature: float, target_curvature: float) -> np.ndarray:
        """
        Compute transformation matrix between dimensional spaces.

        Args:
            source_dims: Source space dimensions
            target_dims: Target space dimensions
            source_curvature: Source space curvature
            target_curvature: Target space curvature

        Returns:
            Transformation matrix
        """
        # Use minimum dimensions for shared space
        shared_dims = min(source_dims, target_dims)

        # Compute curvature adjustment
        self.curvature_adjustment = target_curvature - source_curvature

        # Generate transformation matrix based on method
        if self.method == "poincare":
            # Poincaré disk model transformation
            self.matrix = self._poincare_transform(shared_dims, self.curvature_adjustment)
        elif self.method == "lorentz":
            # Lorentz model transformation
            self.matrix = self._lorentz_transform(shared_dims, self.curvature_adjustment)
        elif self.method == "klein":
            # Klein model transformation
            self.matrix = self._klein_transform(shared_dims, self.curvature_adjustment)
        else:  # hyperboloid
            # Hyperboloid model transformation
            self.matrix = self._hyperboloid_transform(shared_dims, self.curvature_adjustment)

        return self.matrix

    def _poincare_transform(self, dims: int, curvature_adj: float) -> np.ndarray:
        """Generate Poincaré disk transformation matrix."""
        # Identity with curvature scaling
        scale = 1.0 + (curvature_adj * 0.1)
        return np.eye(dims) * scale

    def _lorentz_transform(self, dims: int, curvature_adj: float) -> np.ndarray:
        """Generate Lorentz model transformation matrix."""
        # Lorentz boost-like transformation
        matrix = np.eye(dims)
        gamma = 1.0 / np.sqrt(1.0 - (curvature_adj ** 2) * 0.01)
        matrix[0, 0] = gamma
        return matrix

    def _klein_transform(self, dims: int, curvature_adj: float) -> np.ndarray:
        """Generate Klein model transformation matrix."""
        # Klein disk transformation
        scale = np.exp(curvature_adj * 0.1)
        return np.eye(dims) * scale

    def _hyperboloid_transform(self, dims: int, curvature_adj: float) -> np.ndarray:
        """Generate hyperboloid model transformation matrix."""
        # Hyperboloid embedding transformation
        matrix = np.eye(dims)
        # Add slight rotation based on curvature difference
        theta = curvature_adj * 0.05
        if dims >= 2:
            c, s = np.cos(theta), np.sin(theta)
            matrix[0, 0] = c
            matrix[0, 1] = -s
            matrix[1, 0] = s
            matrix[1, 1] = c
        return matrix

    def apply(self, vector: np.ndarray) -> np.ndarray:
        """Apply transformation to a vector."""
        if self.matrix is None:
            raise RuntimeError("Transform not computed. Call compute_transform first.")
        return self.matrix @ vector

    def to_dict(self) -> Dict:
        """Export transform to dictionary."""
        return {
            "method": self.method,
            "matrix": self.matrix.tolist() if self.matrix is not None else None,
            "curvature_adjustment": self.curvature_adjustment
        }


class SyncSession:
    """
    Manages a dimensional synchronization session between two nodes.
    """

    def __init__(self, initiator: NodeCapabilities, responder: NodeCapabilities,
                 shared_dims: List[int], policy_tag: str):
        self.session_id = str(uuid.uuid4())
        self.initiator = initiator
        self.responder = responder
        self.shared_dims = shared_dims
        self.policy_tag = policy_tag

        self.state = SessionState.PENDING
        self.passes: List[SyncPass] = []
        self.transform: Optional[HyperbolicTransform] = None

        self.convergence_threshold = 0.001
        self.max_iterations = 100
        self.current_error = float('inf')
        self.iterations_completed = 0

        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at: Optional[datetime] = None

    def handshake(self) -> bool:
        """
        Perform handshake between nodes.

        Returns:
            True if handshake successful
        """
        self.state = SessionState.HANDSHAKE

        # Validate shared dimensions
        if not self._validate_shared_dims():
            self.state = SessionState.FAILED
            return False

        # Negotiate protocol
        common_protocols = set(self.initiator.protocols) & set(self.responder.protocols)
        if not common_protocols:
            self.state = SessionState.FAILED
            return False

        # Select transform method
        protocol = list(common_protocols)[0]
        self.transform = HyperbolicTransform(method=protocol)

        self.state = SessionState.TRANSFORM
        self.updated_at = datetime.now()
        return True

    def _validate_shared_dims(self) -> bool:
        """Validate that shared dimensions are compatible."""
        max_dims = min(self.initiator.dimensions, self.responder.dimensions)
        return all(0 <= dim < max_dims for dim in self.shared_dims)

    def compute_transform(self) -> bool:
        """
        Compute coordinate transformation between node spaces.

        Returns:
            True if transform computed successfully
        """
        if self.state != SessionState.TRANSFORM:
            return False

        try:
            self.transform.compute_transform(
                source_dims=self.initiator.dimensions,
                target_dims=self.responder.dimensions,
                source_curvature=self.initiator.curvature,
                target_curvature=self.responder.curvature
            )

            self.state = SessionState.RECONCILE
            self.updated_at = datetime.now()
            return True

        except Exception:
            self.state = SessionState.FAILED
            return False

    def reconcile(self) -> bool:
        """
        Perform reconciliation passes to align dimensional spaces.

        Returns:
            True if reconciliation converged
        """
        if self.state != SessionState.RECONCILE:
            return False

        # Simulate reconciliation iterations
        for iteration in range(self.max_iterations):
            self.iterations_completed = iteration + 1

            # Compute alignment error (simulated)
            self.current_error = self._compute_alignment_error(iteration)

            if self.current_error < self.convergence_threshold:
                self.state = SessionState.COMPLETE
                self.completed_at = datetime.now()
                self.updated_at = datetime.now()
                return True

        # Failed to converge
        self.state = SessionState.FAILED
        self.updated_at = datetime.now()
        return False

    def _compute_alignment_error(self, iteration: int) -> float:
        """Compute alignment error (simulated)."""
        # Exponential decay with noise
        base_error = 1.0 * np.exp(-iteration * 0.1)
        noise = np.random.normal(0, 0.01)
        return max(0.0, base_error + noise)

    def run_passes(self, pass_types: List[str]) -> bool:
        """
        Execute synchronization passes in sequence.

        Args:
            pass_types: List of pass types to execute (e.g., ["metadata", "transport", "reconcile"])

        Returns:
            True if all passes completed successfully
        """
        for pass_type_str in pass_types:
            pass_type = PassType[pass_type_str.upper()]
            sync_pass = SyncPass(pass_type=pass_type)
            self.passes.append(sync_pass)

            sync_pass.start()

            if pass_type == PassType.METADATA:
                success = self.handshake()
            elif pass_type == PassType.TRANSPORT:
                success = self.compute_transform()
            elif pass_type == PassType.RECONCILE:
                success = self.reconcile()
            else:
                success = False

            if success:
                sync_pass.complete({
                    "duration_ms": (datetime.now() - sync_pass.started_at).total_seconds() * 1000
                })
            else:
                sync_pass.fail("Pass execution failed")
                return False

        return True

    def get_metrics(self) -> Dict:
        """Get session metrics."""
        duration_ms = None
        if self.completed_at:
            duration_ms = (self.completed_at - self.created_at).total_seconds() * 1000

        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "passes_completed": len([p for p in self.passes if p.status == PassStatus.COMPLETE]),
            "passes_total": len(self.passes),
            "convergence_error": self.current_error,
            "iterations": self.iterations_completed,
            "duration_ms": duration_ms
        }

    def to_dict(self) -> Dict:
        """Export session to dictionary."""
        return {
            "session_id": self.session_id,
            "initiator": {
                "node_id": self.initiator.node_id,
                "capabilities": {
                    "dimensions": self.initiator.dimensions,
                    "curvature": self.initiator.curvature,
                    "protocols": self.initiator.protocols
                }
            },
            "responder": {
                "node_id": self.responder.node_id,
                "capabilities": {
                    "dimensions": self.responder.dimensions,
                    "curvature": self.responder.curvature,
                    "protocols": self.responder.protocols
                }
            },
            "shared_dims": self.shared_dims,
            "policy_tag": self.policy_tag,
            "state": self.state.value,
            "passes": [
                {
                    "pass_type": p.pass_type.value,
                    "status": p.status.value,
                    "started_at": p.started_at.isoformat() if p.started_at else None,
                    "completed_at": p.completed_at.isoformat() if p.completed_at else None,
                    "metrics": p.metrics
                }
                for p in self.passes
            ],
            "transform": self.transform.to_dict() if self.transform else None,
            "reconciliation": {
                "convergence_threshold": self.convergence_threshold,
                "max_iterations": self.max_iterations,
                "current_error": self.current_error,
                "iterations_completed": self.iterations_completed
            },
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "completed_at": self.completed_at.isoformat() if self.completed_at else None
            }
        }


class SyncManager:
    """
    Manages dimensional synchronization sessions across nodes.
    """

    def __init__(self):
        self.sessions: Dict[str, SyncSession] = {}

    def open_session(self, initiator: NodeCapabilities, responder: NodeCapabilities,
                    shared_dims: List[int], policy_tag: str = "lan-default") -> SyncSession:
        """
        Open a new synchronization session.

        Args:
            initiator: Initiating node capabilities
            responder: Responding node capabilities
            shared_dims: Dimensions to share
            policy_tag: Policy governing this session

        Returns:
            SyncSession instance
        """
        session = SyncSession(initiator, responder, shared_dims, policy_tag)
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SyncSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def close_session(self, session_id: str):
        """Close and remove session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def list_sessions(self, state: Optional[SessionState] = None) -> List[SyncSession]:
        """List sessions, optionally filtered by state."""
        sessions = list(self.sessions.values())
        if state:
            sessions = [s for s in sessions if s.state == state]
        return sessions

    def get_statistics(self) -> Dict:
        """Get manager statistics."""
        states = {}
        for session in self.sessions.values():
            state = session.state.value
            states[state] = states.get(state, 0) + 1

        return {
            "total_sessions": len(self.sessions),
            "by_state": states,
            "active_sessions": len([s for s in self.sessions.values() 
                                   if s.state not in [SessionState.COMPLETE, SessionState.FAILED]])
        }
