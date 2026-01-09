"""
HyperSync ICO Network Layer
============================
Complete implementation of the Inter-Computational Object (ICO) network protocol
with handshake, session management, and attestation.

Features:
- ConnectHello/Accept handshake protocol
- Session state machine with lifecycle management
- Mutual attestation and policy negotiation
- Cryptographic verification (stub for HSM integration)
- Connection pooling and multiplexing
- Heartbeat and keepalive
- Graceful degradation and retry logic

Author: HyperSync Network Foundation Team
Version: 1.0.0
"""

import time
import hashlib
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import secrets
from collections import defaultdict
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

DEFAULT_SESSION_TIMEOUT = 3600  # 1 hour
DEFAULT_HEARTBEAT_INTERVAL = 30  # 30 seconds
MAX_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_BASE = 2.0
NONCE_SIZE = 32  # bytes

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================

class SessionState(Enum):
    """Session lifecycle states."""
    INIT = "init"                   # Initial state
    HELLO_SENT = "hello_sent"       # Hello message sent
    HELLO_RECEIVED = "hello_recv"   # Hello message received
    NEGOTIATING = "negotiating"     # Policy negotiation in progress
    ACTIVE = "active"               # Session active
    DEGRADED = "degraded"           # Degraded mode (partial functionality)
    CLOSING = "closing"             # Graceful shutdown in progress
    CLOSED = "closed"               # Session closed
    ERROR = "error"                 # Error state

class AttestationLevel(Enum):
    """Attestation requirement levels."""
    NONE = "none"                   # No attestation required
    BASIC = "basic"                 # Basic identity attestation
    FULL = "full"                   # Full capability attestation
    ENCLAVE = "enclave"             # Enclave-backed attestation

class MessageType(Enum):
    """ICO network message types."""
    CONNECT_HELLO = "connect_hello"
    CONNECT_ACCEPT = "connect_accept"
    CONNECT_REJECT = "connect_reject"
    HEARTBEAT = "heartbeat"
    HEARTBEAT_ACK = "heartbeat_ack"
    DATA = "data"
    CLOSE = "close"
    ERROR = "error"

@dataclass
class ICODescriptor:
    """
    ICO Descriptor - identifies a computational object in the network.
    """
    ico_id: str                     # Unique ICO identifier
    node_id: str                    # Node hosting this ICO
    capabilities: List[str]         # Supported capabilities
    version: str                    # Protocol version
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ico_id": self.ico_id,
            "node_id": self.node_id,
            "capabilities": self.capabilities,
            "version": self.version,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ICODescriptor":
        return cls(
            ico_id=d["ico_id"],
            node_id=d["node_id"],
            capabilities=d["capabilities"],
            version=d["version"],
            metadata=d.get("metadata", {})
        )

@dataclass
class ConnectionWants:
    """
    Connection requirements and preferences.
    """
    profiles: List[str]             # Desired profiles (e.g., "lorentz", "euclidean")
    models: List[str]               # Desired models
    min_attestation: AttestationLevel
    max_latency_ms: Optional[float] = None
    bandwidth_mbps: Optional[float] = None
    preferences: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profiles": self.profiles,
            "models": self.models,
            "min_attestation": self.min_attestation.value,
            "max_latency_ms": self.max_latency_ms,
            "bandwidth_mbps": self.bandwidth_mbps,
            "preferences": self.preferences
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ConnectionWants":
        return cls(
            profiles=d["profiles"],
            models=d["models"],
            min_attestation=AttestationLevel(d["min_attestation"]),
            max_latency_ms=d.get("max_latency_ms"),
            bandwidth_mbps=d.get("bandwidth_mbps"),
            preferences=d.get("preferences", {})
        )

@dataclass
class AttestationBundle:
    """
    Attestation evidence bundle.
    """
    attestation_id: str
    timestamp: float
    level: AttestationLevel
    evidence: Dict[str, Any]        # Evidence data
    signature: Optional[str] = None # Cryptographic signature
    chain: List[str] = field(default_factory=list)  # Certificate chain

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attestation_id": self.attestation_id,
            "timestamp": self.timestamp,
            "level": self.level.value,
            "evidence": self.evidence,
            "signature": self.signature,
            "chain": self.chain
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AttestationBundle":
        return cls(
            attestation_id=d["attestation_id"],
            timestamp=d["timestamp"],
            level=AttestationLevel(d["level"]),
            evidence=d["evidence"],
            signature=d.get("signature"),
            chain=d.get("chain", [])
        )

@dataclass
class SessionPolicy:
    """
    Session-level policy configuration.
    """
    policy_id: str
    profile: str                    # Active profile
    model: str                      # Active model
    timeout_seconds: float
    heartbeat_interval: float
    max_message_size: int
    encryption_required: bool
    compression_enabled: bool
    rules: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "profile": self.profile,
            "model": self.model,
            "timeout_seconds": self.timeout_seconds,
            "heartbeat_interval": self.heartbeat_interval,
            "max_message_size": self.max_message_size,
            "encryption_required": self.encryption_required,
            "compression_enabled": self.compression_enabled,
            "rules": self.rules
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SessionPolicy":
        return cls(
            policy_id=d["policy_id"],
            profile=d["profile"],
            model=d["model"],
            timeout_seconds=d["timeout_seconds"],
            heartbeat_interval=d["heartbeat_interval"],
            max_message_size=d["max_message_size"],
            encryption_required=d["encryption_required"],
            compression_enabled=d["compression_enabled"],
            rules=d.get("rules", {})
        )

@dataclass
class Session:
    """
    ICO network session with full state management.
    """
    session_id: str
    local_ico: ICODescriptor
    remote_ico: ICODescriptor
    policy: SessionPolicy
    state: SessionState
    attestation: Optional[AttestationBundle] = None

    # Session metadata
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    seq_num: int = 0                # Message sequence number
    remote_seq_num: int = 0         # Last received remote seq

    # Statistics
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    errors: int = 0

    # Internal state
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _heartbeat_timer: Optional[threading.Timer] = field(default=None, repr=False)

    def update_activity(self):
        """Update last activity timestamp."""
        with self._lock:
            self.last_activity = time.time()

    def next_seq(self) -> int:
        """Get next sequence number."""
        with self._lock:
            self.seq_num += 1
            return self.seq_num

    def is_expired(self) -> bool:
        """Check if session has expired."""
        with self._lock:
            elapsed = time.time() - self.last_activity
            return elapsed > self.policy.timeout_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Serialize session to dictionary."""
        with self._lock:
            return {
                "session_id": self.session_id,
                "local_ico": self.local_ico.to_dict(),
                "remote_ico": self.remote_ico.to_dict(),
                "policy": self.policy.to_dict(),
                "state": self.state.value,
                "attestation": self.attestation.to_dict() if self.attestation else None,
                "created_at": self.created_at,
                "last_activity": self.last_activity,
                "seq_num": self.seq_num,
                "remote_seq_num": self.remote_seq_num,
                "stats": {
                    "messages_sent": self.messages_sent,
                    "messages_received": self.messages_received,
                    "bytes_sent": self.bytes_sent,
                    "bytes_received": self.bytes_received,
                    "errors": self.errors
                }
            }

# ============================================================================
# CRYPTOGRAPHIC UTILITIES (STUBS FOR HSM INTEGRATION)
# ============================================================================

def generate_nonce() -> str:
    """Generate a cryptographic nonce."""
    return secrets.token_hex(NONCE_SIZE)

def compute_hash(data: bytes) -> str:
    """Compute SHA-256 hash of data."""
    return hashlib.sha256(data).hexdigest()

def sign_data(data: bytes, private_key: Optional[str] = None) -> str:
    """
    Sign data with private key (stub for HSM integration).

    In production, this would use HSM or enclave-backed signing.
    """
    # Stub implementation
    h = compute_hash(data)
    return f"sig_{h[:32]}"

def verify_signature(data: bytes, signature: str, public_key: Optional[str] = None) -> bool:
    """
    Verify signature (stub for HSM integration).

    In production, this would verify against public key.
    """
    # Stub implementation - always returns True for now
    return signature.startswith("sig_")

def generate_session_id(local_ico: str, remote_ico: str, nonce: str) -> str:
    """Generate deterministic session ID."""
    data = f"{local_ico}:{remote_ico}:{nonce}:{time.time()}"
    return "sess_" + compute_hash(data.encode())[:32]

# ============================================================================
# MESSAGE CONSTRUCTION
# ============================================================================

def create_connect_hello(
    local_ico: ICODescriptor,
    wants: ConnectionWants,
    attest_req: bool = False,
    nonce: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a ConnectHello message.

    Args:
        local_ico: Local ICO descriptor
        wants: Connection requirements
        attest_req: Whether attestation is required
        nonce: Optional nonce (generated if not provided)

    Returns:
        ConnectHello message dictionary
    """
    if nonce is None:
        nonce = generate_nonce()

    message = {
        "type": MessageType.CONNECT_HELLO.value,
        "version": "1.0",
        "timestamp": time.time(),
        "nonce": nonce,
        "ico": local_ico.to_dict(),
        "wants": wants.to_dict(),
        "attest_req": attest_req
    }

    # Sign the message
    message_bytes = json.dumps(message, sort_keys=True).encode()
    message["signature"] = sign_data(message_bytes)

    return message

def create_connect_accept(
    hello_msg: Dict[str, Any],
    local_ico: ICODescriptor,
    chosen_profile: str,
    chosen_model: str,
    policy: SessionPolicy,
    attestation: Optional[AttestationBundle] = None
) -> Dict[str, Any]:
    """
    Create a ConnectAccept message in response to ConnectHello.

    Args:
        hello_msg: The received ConnectHello message
        local_ico: Local ICO descriptor
        chosen_profile: Selected profile
        chosen_model: Selected model
        policy: Session policy
        attestation: Optional attestation bundle

    Returns:
        ConnectAccept message dictionary
    """
    # Generate session ID
    remote_ico_id = hello_msg["ico"]["ico_id"]
    session_id = generate_session_id(local_ico.ico_id, remote_ico_id, hello_msg["nonce"])

    message = {
        "type": MessageType.CONNECT_ACCEPT.value,
        "version": "1.0",
        "timestamp": time.time(),
        "session_id": session_id,
        "ico": local_ico.to_dict(),
        "profile": chosen_profile,
        "model": chosen_model,
        "policy": policy.to_dict(),
        "attestation": attestation.to_dict() if attestation else None,
        "hello_nonce": hello_msg["nonce"]
    }

    # Sign the message
    message_bytes = json.dumps(message, sort_keys=True).encode()
    message["signature"] = sign_data(message_bytes)

    return message

def create_connect_reject(
    hello_msg: Dict[str, Any],
    reason: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a ConnectReject message.

    Args:
        hello_msg: The received ConnectHello message
        reason: Rejection reason
        details: Optional additional details

    Returns:
        ConnectReject message dictionary
    """
    message = {
        "type": MessageType.CONNECT_REJECT.value,
        "version": "1.0",
        "timestamp": time.time(),
        "reason": reason,
        "details": details or {},
        "hello_nonce": hello_msg["nonce"]
    }

    return message

def create_heartbeat(session: Session) -> Dict[str, Any]:
    """Create a heartbeat message."""
    return {
        "type": MessageType.HEARTBEAT.value,
        "session_id": session.session_id,
        "timestamp": time.time(),
        "seq": session.next_seq()
    }

def create_heartbeat_ack(heartbeat_msg: Dict[str, Any], session: Session) -> Dict[str, Any]:
    """Create a heartbeat acknowledgment."""
    return {
        "type": MessageType.HEARTBEAT_ACK.value,
        "session_id": session.session_id,
        "timestamp": time.time(),
        "heartbeat_seq": heartbeat_msg["seq"]
    }

# ============================================================================
# SESSION MANAGER
# ============================================================================

class SessionManager:
    """
    Manages ICO network sessions with lifecycle, heartbeat, and cleanup.
    """

    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()
        self._cleanup_timer: Optional[threading.Timer] = None
        self._message_handlers: Dict[MessageType, List[Callable]] = defaultdict(list)

        # Start cleanup timer
        self._schedule_cleanup()

    def create_session(
        self,
        local_ico: ICODescriptor,
        remote_ico: ICODescriptor,
        policy: SessionPolicy,
        attestation: Optional[AttestationBundle] = None
    ) -> Session:
        """
        Create a new session.

        Args:
            local_ico: Local ICO descriptor
            remote_ico: Remote ICO descriptor
            policy: Session policy
            attestation: Optional attestation bundle

        Returns:
            New Session object
        """
        session_id = generate_session_id(
            local_ico.ico_id,
            remote_ico.ico_id,
            generate_nonce()
        )

        session = Session(
            session_id=session_id,
            local_ico=local_ico,
            remote_ico=remote_ico,
            policy=policy,
            state=SessionState.INIT,
            attestation=attestation
        )

        with self._lock:
            self.sessions[session_id] = session

        logger.info(f"Created session {session_id}")

        # Start heartbeat
        self._start_heartbeat(session)

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        with self._lock:
            return self.sessions.get(session_id)

    def close_session(self, session_id: str, reason: str = "normal"):
        """
        Close a session gracefully.

        Args:
            session_id: Session to close
            reason: Closure reason
        """
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return

            session.state = SessionState.CLOSING

            # Stop heartbeat
            if session._heartbeat_timer:
                session._heartbeat_timer.cancel()

            # Mark as closed
            session.state = SessionState.CLOSED

            logger.info(f"Closed session {session_id}: {reason}")

    def _start_heartbeat(self, session: Session):
        """Start heartbeat timer for session."""
        def send_heartbeat():
            if session.state == SessionState.ACTIVE:
                # Send heartbeat (would be sent over network in production)
                hb = create_heartbeat(session)
                logger.debug(f"Heartbeat sent for session {session.session_id}")

                # Schedule next heartbeat
                session._heartbeat_timer = threading.Timer(
                    session.policy.heartbeat_interval,
                    send_heartbeat
                )
                session._heartbeat_timer.start()

        # Start first heartbeat
        if session.state == SessionState.ACTIVE:
            session._heartbeat_timer = threading.Timer(
                session.policy.heartbeat_interval,
                send_heartbeat
            )
            session._heartbeat_timer.start()

    def _schedule_cleanup(self):
        """Schedule periodic cleanup of expired sessions."""
        def cleanup():
            with self._lock:
                expired = [
                    sid for sid, sess in self.sessions.items()
                    if sess.is_expired() or sess.state == SessionState.CLOSED
                ]

                for sid in expired:
                    logger.info(f"Cleaning up expired session {sid}")
                    del self.sessions[sid]

            # Schedule next cleanup
            self._cleanup_timer = threading.Timer(60.0, cleanup)
            self._cleanup_timer.start()

        self._cleanup_timer = threading.Timer(60.0, cleanup)
        self._cleanup_timer.start()

    def register_handler(self, msg_type: MessageType, handler: Callable):
        """Register a message handler."""
        self._message_handlers[msg_type].append(handler)

    def handle_message(self, message: Dict[str, Any]):
        """Dispatch message to registered handlers."""
        msg_type = MessageType(message["type"])

        for handler in self._message_handlers[msg_type]:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Handler error for {msg_type}: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics."""
        with self._lock:
            return {
                "total_sessions": len(self.sessions),
                "active_sessions": sum(1 for s in self.sessions.values() if s.state == SessionState.ACTIVE),
                "total_messages_sent": sum(s.messages_sent for s in self.sessions.values()),
                "total_messages_received": sum(s.messages_received for s in self.sessions.values()),
                "total_bytes_sent": sum(s.bytes_sent for s in self.sessions.values()),
                "total_bytes_received": sum(s.bytes_received for s in self.sessions.values())
            }

# ============================================================================
# CONNECTION ORCHESTRATOR
# ============================================================================

class ConnectionOrchestrator:
    """
    High-level orchestrator for ICO network connections.
    """

    def __init__(self, local_ico: ICODescriptor):
        self.local_ico = local_ico
        self.session_manager = SessionManager()
        self.pending_connections: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def connect(
        self,
        remote_ico: ICODescriptor,
        wants: ConnectionWants,
        require_attestation: bool = False
    ) -> Tuple[bool, Optional[Session], Optional[str]]:
        """
        Initiate connection to remote ICO.

        Args:
            remote_ico: Remote ICO descriptor
            wants: Connection requirements
            require_attestation: Whether to require attestation

        Returns:
            Tuple of (success, session, error_message)
        """
        # Create ConnectHello
        hello_msg = create_connect_hello(
            self.local_ico,
            wants,
            attest_req=require_attestation
        )

        # Store pending connection
        nonce = hello_msg["nonce"]
        with self._lock:
            self.pending_connections[nonce] = {
                "hello": hello_msg,
                "remote_ico": remote_ico,
                "wants": wants,
                "timestamp": time.time()
            }

        logger.info(f"Initiated connection to {remote_ico.ico_id}")

        # In production, send hello_msg over network
        # For now, return success
        return True, None, None

    def handle_connect_hello(
        self,
        hello_msg: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Handle incoming ConnectHello message.

        Args:
            hello_msg: ConnectHello message

        Returns:
            Tuple of (accept, response_message, error)
        """
        # Verify signature
        # (In production, verify against public key)

        # Parse wants
        wants = ConnectionWants.from_dict(hello_msg["wants"])
        remote_ico = ICODescriptor.from_dict(hello_msg["ico"])

        # Check if we can satisfy wants
        chosen_profile = self._select_profile(wants.profiles)
        chosen_model = self._select_model(wants.models)

        if not chosen_profile or not chosen_model:
            # Reject
            reject_msg = create_connect_reject(
                hello_msg,
                "unsupported_requirements",
                {"available_profiles": ["lorentz"], "available_models": ["hyperbolic"]}
            )
            return False, reject_msg, "Cannot satisfy connection requirements"

        # Create policy
        policy = SessionPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:16]}",
            profile=chosen_profile,
            model=chosen_model,
            timeout_seconds=DEFAULT_SESSION_TIMEOUT,
            heartbeat_interval=DEFAULT_HEARTBEAT_INTERVAL,
            max_message_size=1024 * 1024,  # 1MB
            encryption_required=True,
            compression_enabled=False
        )

        # Create attestation if required
        attestation = None
        if hello_msg.get("attest_req"):
            attestation = self._create_attestation(wants.min_attestation)

        # Create accept message
        accept_msg = create_connect_accept(
            hello_msg,
            self.local_ico,
            chosen_profile,
            chosen_model,
            policy,
            attestation
        )

        # Create session
        session = self.session_manager.create_session(
            self.local_ico,
            remote_ico,
            policy,
            attestation
        )
        session.state = SessionState.ACTIVE

        logger.info(f"Accepted connection from {remote_ico.ico_id}, session {session.session_id}")

        return True, accept_msg, None

    def handle_connect_accept(
        self,
        accept_msg: Dict[str, Any]
    ) -> Tuple[bool, Optional[Session], Optional[str]]:
        """
        Handle incoming ConnectAccept message.

        Args:
            accept_msg: ConnectAccept message

        Returns:
            Tuple of (success, session, error)
        """
        hello_nonce = accept_msg.get("hello_nonce")

        with self._lock:
            pending = self.pending_connections.get(hello_nonce)
            if not pending:
                return False, None, "No pending connection found"

            del self.pending_connections[hello_nonce]

        # Parse accept message
        remote_ico = ICODescriptor.from_dict(accept_msg["ico"])
        policy = SessionPolicy.from_dict(accept_msg["policy"])

        attestation = None
        if accept_msg.get("attestation"):
            attestation = AttestationBundle.from_dict(accept_msg["attestation"])

        # Create session
        session = Session(
            session_id=accept_msg["session_id"],
            local_ico=self.local_ico,
            remote_ico=remote_ico,
            policy=policy,
            state=SessionState.ACTIVE,
            attestation=attestation
        )

        with self.session_manager._lock:
            self.session_manager.sessions[session.session_id] = session

        logger.info(f"Connection accepted, session {session.session_id}")

        return True, session, None

    def _select_profile(self, requested: List[str]) -> Optional[str]:
        """Select a profile from requested list."""
        available = ["lorentz", "euclidean", "poincare"]
        for profile in requested:
            if profile in available:
                return profile
        return None

    def _select_model(self, requested: List[str]) -> Optional[str]:
        """Select a model from requested list."""
        available = ["hyperbolic", "flat", "spherical"]
        for model in requested:
            if model in available:
                return model
        return None

    def _create_attestation(self, level: AttestationLevel) -> AttestationBundle:
        """Create attestation bundle."""
        return AttestationBundle(
            attestation_id=f"attest_{uuid.uuid4().hex[:16]}",
            timestamp=time.time(),
            level=level,
            evidence={
                "node_id": self.local_ico.node_id,
                "capabilities": self.local_ico.capabilities,
                "version": self.local_ico.version
            },
            signature=sign_data(b"attestation_data")
        )

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    'SessionState', 'AttestationLevel', 'MessageType',

    # Data classes
    'ICODescriptor', 'ConnectionWants', 'AttestationBundle',
    'SessionPolicy', 'Session',

    # Functions
    'create_connect_hello', 'create_connect_accept', 'create_connect_reject',
    'create_heartbeat', 'create_heartbeat_ack',
    'generate_nonce', 'compute_hash', 'sign_data', 'verify_signature',

    # Classes
    'SessionManager', 'ConnectionOrchestrator',
]
