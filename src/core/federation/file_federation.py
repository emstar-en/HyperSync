"""
Cross-Node File Federation
Enables file access across multiple HyperSync nodes with transparent sync.
"""

import os
import json
import logging
import hashlib
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SyncStrategy(Enum):
    """File synchronization strategies"""
    PULL = "pull"  # Pull from remote on access
    PUSH = "push"  # Push to remote on write
    BIDIRECTIONAL = "bidirectional"  # Sync both ways
    CACHE = "cache"  # Cache locally, sync periodically


@dataclass
class RemoteNode:
    """Represents a remote HyperSync node"""
    node_id: str
    hostname: str
    port: int
    protocol: str = "https"
    api_key: Optional[str] = None

    def get_url(self) -> str:
        return f"{self.protocol}://{self.hostname}:{self.port}"


@dataclass
class FederatedFile:
    """Represents a file federated across nodes"""
    path: str
    owner_node: str
    replicas: Set[str] = field(default_factory=set)
    checksum: Optional[str] = None
    size: int = 0
    modified_at: Optional[datetime] = None
    sync_strategy: SyncStrategy = SyncStrategy.PULL

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "owner_node": self.owner_node,
            "replicas": list(self.replicas),
            "checksum": self.checksum,
            "size": self.size,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "sync_strategy": self.sync_strategy.value
        }


class FileFederationManager:
    """Manages file federation across nodes"""

    def __init__(self, local_node_id: str):
        """
        Initialize federation manager.

        Args:
            local_node_id: ID of local node
        """
        self.local_node_id = local_node_id
        self.remote_nodes: Dict[str, RemoteNode] = {}
        self.federated_files: Dict[str, FederatedFile] = {}
        self.cache_dir = "/tmp/hypersync_federation_cache"

        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)

        logger.info(f"FileFederationManager initialized for node {local_node_id}")

    def register_node(self, node: RemoteNode):
        """Register a remote node"""
        self.remote_nodes[node.node_id] = node
        logger.info(f"Registered remote node: {node.node_id} at {node.get_url()}")

    def federate_file(
        self,
        path: str,
        owner_node: Optional[str] = None,
        sync_strategy: SyncStrategy = SyncStrategy.PULL
    ) -> FederatedFile:
        """
        Federate a file across nodes.

        Args:
            path: File path
            owner_node: Node that owns the file (defaults to local)
            sync_strategy: How to sync the file

        Returns:
            FederatedFile object
        """
        if owner_node is None:
            owner_node = self.local_node_id

        # Check if already federated
        if path in self.federated_files:
            logger.warning(f"File already federated: {path}")
            return self.federated_files[path]

        # Get file info
        checksum = None
        size = 0
        modified_at = None

        if os.path.exists(path):
            size = os.path.getsize(path)
            modified_at = datetime.fromtimestamp(os.path.getmtime(path))
            checksum = self._compute_checksum(path)

        federated = FederatedFile(
            path=path,
            owner_node=owner_node,
            replicas={self.local_node_id},
            checksum=checksum,
            size=size,
            modified_at=modified_at,
            sync_strategy=sync_strategy
        )

        self.federated_files[path] = federated
        logger.info(f"Federated file: {path} (owner: {owner_node})")

        return federated

    def read_file(self, path: str) -> bytes:
        """
        Read a federated file.

        Args:
            path: File path

        Returns:
            File contents
        """
        federated = self.federated_files.get(path)
        if not federated:
            raise ValueError(f"File not federated: {path}")

        # Check if available locally
        if os.path.exists(path):
            logger.info(f"Reading local file: {path}")
            with open(path, 'rb') as f:
                return f.read()

        # Check cache
        cache_path = self._get_cache_path(path)
        if os.path.exists(cache_path):
            logger.info(f"Reading cached file: {path}")
            with open(cache_path, 'rb') as f:
                return f.read()

        # Pull from remote
        if federated.owner_node != self.local_node_id:
            logger.info(f"Pulling file from {federated.owner_node}: {path}")
            content = self._pull_from_remote(path, federated.owner_node)

            # Cache locally
            self._cache_file(path, content)

            return content

        raise FileNotFoundError(f"File not found: {path}")

    def write_file(self, path: str, content: bytes):
        """
        Write to a federated file.

        Args:
            path: File path
            content: File contents
        """
        federated = self.federated_files.get(path)
        if not federated:
            raise ValueError(f"File not federated: {path}")

        # Write locally
        logger.info(f"Writing local file: {path}")
        with open(path, 'wb') as f:
            f.write(content)

        # Update metadata
        federated.checksum = self._compute_checksum_bytes(content)
        federated.size = len(content)
        federated.modified_at = datetime.utcnow()

        # Push to replicas if needed
        if federated.sync_strategy in [SyncStrategy.PUSH, SyncStrategy.BIDIRECTIONAL]:
            self._push_to_replicas(path, content, federated)

    def sync_file(self, path: str):
        """
        Manually sync a file across nodes.

        Args:
            path: File path
        """
        federated = self.federated_files.get(path)
        if not federated:
            raise ValueError(f"File not federated: {path}")

        logger.info(f"Syncing file: {path}")

        # If we're the owner, push to replicas
        if federated.owner_node == self.local_node_id:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    content = f.read()
                self._push_to_replicas(path, content, federated)
        else:
            # Pull from owner
            content = self._pull_from_remote(path, federated.owner_node)
            with open(path, 'wb') as f:
                f.write(content)

    def list_federated_files(self) -> List[FederatedFile]:
        """List all federated files"""
        return list(self.federated_files.values())

    def get_file_info(self, path: str) -> Optional[FederatedFile]:
        """Get info about a federated file"""
        return self.federated_files.get(path)

    def _compute_checksum(self, path: str) -> str:
        """Compute file checksum"""
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _compute_checksum_bytes(self, content: bytes) -> str:
        """Compute checksum of bytes"""
        return hashlib.sha256(content).hexdigest()

    def _get_cache_path(self, path: str) -> str:
        """Get cache path for a file"""
        # Use hash of path as cache filename
        path_hash = hashlib.md5(path.encode()).hexdigest()
        return os.path.join(self.cache_dir, path_hash)

    def _cache_file(self, path: str, content: bytes):
        """Cache file locally"""
        cache_path = self._get_cache_path(path)
        with open(cache_path, 'wb') as f:
            f.write(content)
        logger.info(f"Cached file: {path}")

    def _pull_from_remote(self, path: str, node_id: str) -> bytes:
        """Pull file from remote node"""
        node = self.remote_nodes.get(node_id)
        if not node:
            raise ValueError(f"Unknown node: {node_id}")

        # In production, this would make HTTP request to remote node
        # For now, simulate by reading from local filesystem
        logger.info(f"Simulating pull from {node_id}: {path}")

        if os.path.exists(path):
            with open(path, 'rb') as f:
                return f.read()

        raise FileNotFoundError(f"File not found on remote: {path}")

    def _push_to_replicas(self, path: str, content: bytes, federated: FederatedFile):
        """Push file to replica nodes"""
        for replica_id in federated.replicas:
            if replica_id == self.local_node_id:
                continue

            node = self.remote_nodes.get(replica_id)
            if not node:
                logger.warning(f"Unknown replica node: {replica_id}")
                continue

            # In production, this would make HTTP request to remote node
            logger.info(f"Simulating push to {replica_id}: {path}")

    def get_stats(self) -> Dict:
        """Get federation statistics"""
        total_files = len(self.federated_files)
        owned_files = sum(1 for f in self.federated_files.values() 
                         if f.owner_node == self.local_node_id)
        remote_files = total_files - owned_files
        total_size = sum(f.size for f in self.federated_files.values())

        return {
            "local_node_id": self.local_node_id,
            "remote_nodes": len(self.remote_nodes),
            "total_files": total_files,
            "owned_files": owned_files,
            "remote_files": remote_files,
            "total_size_bytes": total_size
        }


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    # Create federation manager
    manager = FileFederationManager(local_node_id="node-1")

    # Register remote node
    remote = RemoteNode(
        node_id="node-2",
        hostname="node2.hypersync.local",
        port=8443
    )
    manager.register_node(remote)

    # Federate a file
    test_file = "/tmp/federated_test.txt"
    with open(test_file, 'w') as f:
        f.write("Federated content")

    federated = manager.federate_file(test_file)
    print(f"Federated: {federated.path}")

    # Read file
    content = manager.read_file(test_file)
    print(f"Content: {content.decode()}")

    # Get stats
    stats = manager.get_stats()
    print(f"Stats: {stats}")
