"""
HyperSync Sandbox Manager
Provides lightweight isolation for agent filesystem operations with real path access.
"""

import os
import sys
import json
import logging
import subprocess
import threading
from typing import Dict, List, Optional, Set
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SandboxState(Enum):
    """Sandbox lifecycle states"""
    INACTIVE = "inactive"
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATING = "terminating"
    TERMINATED = "terminated"


class IsolationMode(Enum):
    """Isolation technology options"""
    NONE = "none"
    NAMESPACE = "namespace"
    CGROUP = "cgroup"
    CONTAINER = "container"
    VM = "vm"


@dataclass
class PathPermission:
    """Represents permissions for a specific path"""
    path: str
    permissions: Set[str]
    recursive: bool = True
    clearance_required: str = "internal"

    def allows(self, operation: str) -> bool:
        """Check if operation is permitted"""
        return operation in self.permissions

    def matches_path(self, target_path: str) -> bool:
        """Check if this permission applies to target path"""
        target = Path(target_path).resolve()
        allowed = Path(self.path).resolve()

        if self.recursive:
            try:
                target.relative_to(allowed)
                return True
            except ValueError:
                return False
        else:
            return target == allowed


@dataclass
class ResourceQuotas:
    """Resource limits for sandbox"""
    max_disk_mb: int = 10240  # 10GB default
    max_inodes: int = 100000
    max_open_files: int = 1024
    cpu_shares: int = 512
    memory_mb: int = 2048

    def to_dict(self) -> dict:
        return {
            "max_disk_mb": self.max_disk_mb,
            "max_inodes": self.max_inodes,
            "max_open_files": self.max_open_files,
            "cpu_shares": self.cpu_shares,
            "memory_mb": self.memory_mb
        }


@dataclass
class SandboxMetrics:
    """Current resource usage metrics"""
    disk_used_mb: float = 0.0
    inodes_used: int = 0
    open_files: int = 0
    cpu_usage_percent: float = 0.0
    memory_used_mb: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "disk_used_mb": self.disk_used_mb,
            "inodes_used": self.inodes_used,
            "open_files": self.open_files,
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_used_mb": self.memory_used_mb,
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class AccessPolicy:
    """Complete access policy for an agent"""
    policy_id: str
    agent_id: str
    version: str
    allowed_paths: List[PathPermission]
    denied_paths: List[str]
    default_dirs: List[str]
    quotas: ResourceQuotas
    isolation_mode: IsolationMode = IsolationMode.NAMESPACE
    network_isolated: bool = False
    pid_isolated: bool = True
    metadata: Dict = field(default_factory=dict)

    def check_access(self, path: str, operation: str, clearance: str = "internal") -> bool:
        """
        Check if access to path with operation is allowed.

        Args:
            path: Target filesystem path
            operation: Operation type (read, write, execute, list, delete)
            clearance: Agent's clearance level

        Returns:
            True if access is allowed, False otherwise
        """
        # Check denied paths first (they override allowed)
        resolved_path = str(Path(path).resolve())
        for denied in self.denied_paths:
            denied_resolved = str(Path(denied).resolve())
            if resolved_path.startswith(denied_resolved):
                logger.warning(f"Access denied to {path}: explicitly denied")
                return False

        # Check allowed paths
        for perm in self.allowed_paths:
            if perm.matches_path(path):
                if not perm.allows(operation):
                    logger.warning(f"Access denied to {path}: operation {operation} not permitted")
                    return False

                # Check clearance
                clearance_levels = ["public", "internal", "confidential", "restricted", "critical"]
                required_idx = clearance_levels.index(perm.clearance_required)
                agent_idx = clearance_levels.index(clearance)

                if agent_idx < required_idx:
                    logger.warning(f"Access denied to {path}: insufficient clearance")
                    return False

                return True

        logger.warning(f"Access denied to {path}: no matching permission")
        return False

    @classmethod
    def from_dict(cls, data: dict) -> 'AccessPolicy':
        """Create policy from dictionary"""
        allowed_paths = [
            PathPermission(
                path=p["path"],
                permissions=set(p["permissions"]),
                recursive=p.get("recursive", True),
                clearance_required=p.get("clearance_required", "internal")
            )
            for p in data["paths"]["allowed"]
        ]

        quotas = ResourceQuotas(**data.get("quotas", {}))
        isolation = data.get("isolation", {})

        return cls(
            policy_id=data["policy_id"],
            agent_id=data["agent_id"],
            version=data["version"],
            allowed_paths=allowed_paths,
            denied_paths=data["paths"]["denied"],
            default_dirs=data["paths"]["default_dirs"],
            quotas=quotas,
            isolation_mode=IsolationMode(isolation.get("mode", "namespace")),
            network_isolated=isolation.get("network_isolated", False),
            pid_isolated=isolation.get("pid_isolated", True),
            metadata=data.get("metadata", {})
        )

    def to_dict(self) -> dict:
        """Convert policy to dictionary"""
        return {
            "policy_id": self.policy_id,
            "agent_id": self.agent_id,
            "version": self.version,
            "paths": {
                "allowed": [
                    {
                        "path": p.path,
                        "permissions": list(p.permissions),
                        "recursive": p.recursive,
                        "clearance_required": p.clearance_required
                    }
                    for p in self.allowed_paths
                ],
                "denied": self.denied_paths,
                "default_dirs": self.default_dirs
            },
            "quotas": self.quotas.to_dict(),
            "isolation": {
                "mode": self.isolation_mode.value,
                "network_isolated": self.network_isolated,
                "pid_isolated": self.pid_isolated
            },
            "metadata": self.metadata
        }


class Sandbox:
    """Represents an active agent sandbox"""

    def __init__(
        self,
        sandbox_id: str,
        agent_id: str,
        policy: AccessPolicy,
        root_path: Optional[str] = None
    ):
        self.sandbox_id = sandbox_id
        self.agent_id = agent_id
        self.policy = policy
        self.root_path = root_path or f"/var/hypersync/sandboxes/{sandbox_id}"
        self.state = SandboxState.INACTIVE
        self.metrics = SandboxMetrics()
        self.mounts: List[Dict] = []
        self.environment: Dict[str, str] = {}
        self._lock = threading.Lock()

    def provision(self) -> bool:
        """Provision sandbox resources"""
        with self._lock:
            if self.state != SandboxState.INACTIVE:
                logger.error(f"Cannot provision sandbox {self.sandbox_id}: not inactive")
                return False

            self.state = SandboxState.PROVISIONING
            logger.info(f"Provisioning sandbox {self.sandbox_id} for agent {self.agent_id}")

            try:
                # Create root directory
                os.makedirs(self.root_path, exist_ok=True)

                # Create default directories
                for default_dir in self.policy.default_dirs:
                    os.makedirs(default_dir, exist_ok=True)
                    logger.info(f"Created default directory: {default_dir}")

                # Apply isolation based on mode
                self._apply_isolation()

                # Set up resource limits
                self._apply_quotas()

                self.state = SandboxState.ACTIVE
                logger.info(f"Sandbox {self.sandbox_id} provisioned successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to provision sandbox {self.sandbox_id}: {e}")
                self.state = SandboxState.INACTIVE
                return False

    def _apply_isolation(self):
        """Apply isolation mechanisms based on policy"""
        mode = self.policy.isolation_mode

        if mode == IsolationMode.NONE:
            logger.info("No isolation applied")
            return

        if mode == IsolationMode.NAMESPACE:
            # Linux namespace isolation
            if sys.platform == "linux":
                logger.info("Applying namespace isolation")
                # In production, use unshare() syscall or container runtime
                # For now, log the intent
            else:
                logger.warning(f"Namespace isolation not supported on {sys.platform}")

        elif mode == IsolationMode.CGROUP:
            # cgroup resource limits
            if sys.platform == "linux":
                logger.info("Applying cgroup isolation")
                # In production, configure cgroups v2
            else:
                logger.warning(f"cgroup isolation not supported on {sys.platform}")

        elif mode == IsolationMode.CONTAINER:
            logger.info("Container isolation would be applied via runtime")

        elif mode == IsolationMode.VM:
            logger.info("VM isolation would be applied via hypervisor")

    def _apply_quotas(self):
        """Apply resource quotas"""
        quotas = self.policy.quotas
        logger.info(f"Applying quotas: {quotas.to_dict()}")

        # In production, set actual limits via:
        # - Filesystem quotas (setquota, ZFS quotas, etc.)
        # - ulimit for open files
        # - cgroups for CPU/memory

        # For now, store for enforcement
        self.metrics.last_updated = datetime.utcnow()

    def check_access(self, path: str, operation: str, clearance: str = "internal") -> bool:
        """Check if access is allowed"""
        if self.state != SandboxState.ACTIVE:
            logger.error(f"Sandbox {self.sandbox_id} not active")
            return False

        return self.policy.check_access(path, operation, clearance)

    def update_metrics(self):
        """Update resource usage metrics"""
        # In production, query actual usage from OS
        # For now, placeholder
        self.metrics.last_updated = datetime.utcnow()

    def suspend(self):
        """Suspend sandbox operations"""
        with self._lock:
            if self.state == SandboxState.ACTIVE:
                self.state = SandboxState.SUSPENDED
                logger.info(f"Sandbox {self.sandbox_id} suspended")

    def resume(self):
        """Resume sandbox operations"""
        with self._lock:
            if self.state == SandboxState.SUSPENDED:
                self.state = SandboxState.ACTIVE
                logger.info(f"Sandbox {self.sandbox_id} resumed")

    def terminate(self):
        """Terminate sandbox and cleanup resources"""
        with self._lock:
            self.state = SandboxState.TERMINATING
            logger.info(f"Terminating sandbox {self.sandbox_id}")

            # Cleanup would happen here
            # - Unmount filesystems
            # - Remove cgroups
            # - Clean temporary files

            self.state = SandboxState.TERMINATED
            logger.info(f"Sandbox {self.sandbox_id} terminated")

    def to_dict(self) -> dict:
        """Convert sandbox to dictionary"""
        return {
            "sandbox_id": self.sandbox_id,
            "agent_id": self.agent_id,
            "state": self.state.value,
            "policy_id": self.policy.policy_id,
            "root_path": self.root_path,
            "mounts": self.mounts,
            "environment": self.environment,
            "metrics": self.metrics.to_dict()
        }


class SandboxManager:
    """Manages agent sandboxes with real path access"""

    def __init__(self, config_dir: str = "/etc/hypersync/sandboxes"):
        self.config_dir = config_dir
        self.sandboxes: Dict[str, Sandbox] = {}
        self.policies: Dict[str, AccessPolicy] = {}
        self._lock = threading.Lock()

        os.makedirs(config_dir, exist_ok=True)
        logger.info(f"SandboxManager initialized with config_dir={config_dir}")

    def load_policy(self, policy_path: str) -> AccessPolicy:
        """Load access policy from file"""
        with open(policy_path, 'r') as f:
            data = json.load(f)

        policy = AccessPolicy.from_dict(data)
        self.policies[policy.policy_id] = policy
        logger.info(f"Loaded policy {policy.policy_id} for agent {policy.agent_id}")
        return policy

    def create_policy(
        self,
        agent_id: str,
        allowed_paths: List[str],
        default_dirs: Optional[List[str]] = None,
        **kwargs
    ) -> AccessPolicy:
        """Create a new access policy"""
        policy_id = f"env-policy-{agent_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Convert simple path list to PathPermission objects
        path_perms = [
            PathPermission(
                path=p,
                permissions={"read", "write", "list"},
                recursive=True
            )
            for p in allowed_paths
        ]

        policy = AccessPolicy(
            policy_id=policy_id,
            agent_id=agent_id,
            version="1.0.0",
            allowed_paths=path_perms,
            denied_paths=kwargs.get("denied_paths", []),
            default_dirs=default_dirs or [],
            quotas=ResourceQuotas(**kwargs.get("quotas", {})),
            isolation_mode=IsolationMode(kwargs.get("isolation_mode", "namespace")),
            metadata={
                "created_at": datetime.utcnow().isoformat(),
                "created_by": kwargs.get("created_by", "system")
            }
        )

        self.policies[policy_id] = policy

        # Save to disk
        policy_file = os.path.join(self.config_dir, f"{policy_id}.json")
        with open(policy_file, 'w') as f:
            json.dump(policy.to_dict(), f, indent=2)

        logger.info(f"Created policy {policy_id} for agent {agent_id}")
        return policy

    def activate(
        self,
        agent_id: str,
        allowed_paths: Optional[List[str]] = None,
        default_dirs: Optional[List[str]] = None,
        policy_id: Optional[str] = None,
        **kwargs
    ) -> Sandbox:
        """
        Activate a sandbox for an agent.

        Args:
            agent_id: Agent identifier
            allowed_paths: List of allowed filesystem paths
            default_dirs: Default working directories
            policy_id: Existing policy ID to use
            **kwargs: Additional policy parameters

        Returns:
            Active Sandbox instance
        """
        with self._lock:
            # Check if sandbox already exists
            for sandbox in self.sandboxes.values():
                if sandbox.agent_id == agent_id and sandbox.state == SandboxState.ACTIVE:
                    logger.info(f"Returning existing sandbox for agent {agent_id}")
                    return sandbox

            # Get or create policy
            if policy_id:
                policy = self.policies.get(policy_id)
                if not policy:
                    raise ValueError(f"Policy {policy_id} not found")
            else:
                if not allowed_paths:
                    raise ValueError("Must provide allowed_paths or policy_id")
                policy = self.create_policy(agent_id, allowed_paths, default_dirs, **kwargs)

            # Create sandbox
            sandbox_id = f"sandbox-{agent_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            sandbox = Sandbox(sandbox_id, agent_id, policy)

            # Provision
            if not sandbox.provision():
                raise RuntimeError(f"Failed to provision sandbox {sandbox_id}")

            self.sandboxes[sandbox_id] = sandbox
            logger.info(f"Activated sandbox {sandbox_id} for agent {agent_id}")
            return sandbox

    def get_sandbox(self, sandbox_id: str) -> Optional[Sandbox]:
        """Get sandbox by ID"""
        return self.sandboxes.get(sandbox_id)

    def get_agent_sandbox(self, agent_id: str) -> Optional[Sandbox]:
        """Get active sandbox for agent"""
        for sandbox in self.sandboxes.values():
            if sandbox.agent_id == agent_id and sandbox.state == SandboxState.ACTIVE:
                return sandbox
        return None

    def terminate_sandbox(self, sandbox_id: str):
        """Terminate a sandbox"""
        sandbox = self.sandboxes.get(sandbox_id)
        if sandbox:
            sandbox.terminate()
            logger.info(f"Terminated sandbox {sandbox_id}")

    def list_sandboxes(self) -> List[Dict]:
        """List all sandboxes"""
        return [s.to_dict() for s in self.sandboxes.values()]

    def cleanup_terminated(self):
        """Remove terminated sandboxes from memory"""
        with self._lock:
            terminated = [
                sid for sid, s in self.sandboxes.items()
                if s.state == SandboxState.TERMINATED
            ]
            for sid in terminated:
                del self.sandboxes[sid]

            if terminated:
                logger.info(f"Cleaned up {len(terminated)} terminated sandboxes")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    manager = SandboxManager()

    # Activate sandbox with real paths
    sandbox = manager.activate(
        agent_id="core-agent-1",
        allowed_paths=["/home/core/projects", "/var/log/shared"],
        default_dirs=["/home/core/projects/Documents"],
        quotas={"cpu_shares": 512, "memory_mb": 2048}
    )

    # Check access
    can_read = sandbox.check_access("/home/core/projects/README.md", "read")
    print(f"Can read README.md: {can_read}")

    can_write = sandbox.check_access("/etc/passwd", "write")
    print(f"Can write /etc/passwd: {can_write}")
