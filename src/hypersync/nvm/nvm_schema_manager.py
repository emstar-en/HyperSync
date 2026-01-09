"""
HyperSync NVM Schema Manager

Comprehensive NVM block management with hyperbolic vector embedding,
assignment capabilities, directory management, and preloading support.
"""

from __future__ import annotations

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, field, asdict
from enum import Enum


class NVMBlockClass(str, Enum):
    """NVM block classification"""
    KNOWLEDGE_GRAPH = "knowledge_graph"
    DOCUMENTATION = "documentation"
    PROGRAM_STATE = "program_state"
    TRAINING_DATA = "training_data"
    EMBEDDINGS = "embeddings"
    CACHE = "cache"
    LOGS = "logs"
    ARTIFACTS = "artifacts"
    CUSTOM = "custom"


class NVMAssignmentType(str, Enum):
    """Types of NVM assignments"""
    MODEL = "model"
    STACK = "stack"
    NETWORK = "network"
    TRUNK = "trunk"
    MODEL_GROUP = "model_group"
    BRIDGE = "bridge"
    GLOBAL = "global"


class NVMAccessMode(str, Enum):
    """Access modes for NVM blocks"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    APPEND_ONLY = "append_only"
    IMMUTABLE = "immutable"


@dataclass
class NVMGeometryConfig:
    """Hyperbolic geometry configuration for NVM embeddings"""
    space: Literal["euclidean", "spherical", "poincare_ball", "hyperboloid", "spd_logeuclid"]
    curvature: float = -1.0
    radius_cap: float = 0.98
    dimension: int = 768
    metric: str = "poincare"
    transport: str = "parallel"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NVMIndexConfig:
    """Index configuration for NVM vector search"""
    index_type: Literal["hnsw_euclidean", "hnsw_hyperbolic", "ivfpq", "bruteforce"]
    ef_construction: int = 200
    ef_search: int = 100
    m_neighbors: int = 32
    quantization: Optional[str] = "opq"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NVMCodebookConfig:
    """Codebook configuration for quantization"""
    method: Literal["opq", "pq", "sq", "none"]
    n_subvectors: int = 8
    bits_per_code: int = 8
    training_size: int = 10000

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NVMAssignment:
    """Assignment of NVM block to entity"""
    assignment_id: str
    assignment_type: NVMAssignmentType
    target_id: str
    target_name: Optional[str] = None
    access_mode: NVMAccessMode = NVMAccessMode.READ_WRITE
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assignment_id": self.assignment_id,
            "assignment_type": self.assignment_type.value,
            "target_id": self.target_id,
            "target_name": self.target_name,
            "access_mode": self.access_mode.value,
            "priority": self.priority,
            "metadata": self.metadata,
            "created_at": self.created_at
        }


@dataclass
class NVMDirectory:
    """Directory configuration for NVM file storage"""
    directory_id: str
    path: str
    purpose: str
    max_size_mb: Optional[int] = None
    allowed_extensions: List[str] = field(default_factory=list)
    auto_embed: bool = True
    watch_changes: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NVMPreloadConfig:
    """Configuration for preloading NVM blocks"""
    preload_id: str
    source_type: Literal["file", "directory", "url", "inline"]
    source_path: Optional[str] = None
    content: Optional[str] = None
    content_type: str = "text/markdown"
    chunk_size: int = 512
    overlap: int = 50
    auto_embed: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NVMBlockSchema:
    """Complete NVM block schema with all capabilities"""
    block_id: str
    name: str
    description: str
    block_class: NVMBlockClass

    # Hyperbolic vector embedding (default enabled)
    geometry: NVMGeometryConfig
    index: NVMIndexConfig
    codebook: NVMCodebookConfig

    # Capacity and retention
    max_vectors: Optional[int] = None
    max_size_mb: Optional[int] = None
    retention_days: Optional[int] = None

    # Assignments
    assignments: List[NVMAssignment] = field(default_factory=list)

    # Directory management
    directories: List[NVMDirectory] = field(default_factory=list)

    # Preload configuration
    preloads: List[NVMPreloadConfig] = field(default_factory=list)

    # Versioning
    version: str = "1.0.0"
    schema_version: str = "nvm_block"

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_id": self.block_id,
            "name": self.name,
            "description": self.description,
            "class": self.block_class.value,
            "geometry": self.geometry.to_dict(),
            "index": self.index.to_dict(),
            "codebook": self.codebook.to_dict(),
            "max_vectors": self.max_vectors,
            "max_size_mb": self.max_size_mb,
            "retention_days": self.retention_days,
            "assignments": [a.to_dict() for a in self.assignments],
            "directories": [d.to_dict() for d in self.directories],
            "preloads": [p.to_dict() for p in self.preloads],
            "version": self.version,
            "schema_version": self.schema_version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }


class NVMSchemaManager:
    """Manager for NVM block schemas with full lifecycle support"""

    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)
        self.blocks_dir = self.storage_path / "blocks"
        self.assignments_dir = self.storage_path / "assignments"
        self.receipts_dir = self.storage_path / "receipts"

        # Create directories
        self.blocks_dir.mkdir(parents=True, exist_ok=True)
        self.assignments_dir.mkdir(parents=True, exist_ok=True)
        self.receipts_dir.mkdir(parents=True, exist_ok=True)

    def create_block(
        self,
        block_id: str,
        name: str,
        description: str,
        block_class: NVMBlockClass,
        geometry: Optional[NVMGeometryConfig] = None,
        index: Optional[NVMIndexConfig] = None,
        codebook: Optional[NVMCodebookConfig] = None,
        **kwargs
    ) -> NVMBlockSchema:
        """Create a new NVM block with hyperbolic embedding by default"""

        # Default hyperbolic configuration
        if geometry is None:
            geometry = NVMGeometryConfig(
                space="poincare_ball",
                curvature=-1.0,
                radius_cap=0.98,
                dimension=768
            )

        if index is None:
            index = NVMIndexConfig(
                index_type="hnsw_hyperbolic",
                ef_construction=200,
                ef_search=100,
                m_neighbors=32
            )

        if codebook is None:
            codebook = NVMCodebookConfig(
                method="opq",
                n_subvectors=8,
                bits_per_code=8
            )

        block = NVMBlockSchema(
            block_id=block_id,
            name=name,
            description=description,
            block_class=block_class,
            geometry=geometry,
            index=index,
            codebook=codebook,
            **kwargs
        )

        self._save_block(block)
        return block

    def assign_block(
        self,
        block_id: str,
        assignment_type: NVMAssignmentType,
        target_id: str,
        target_name: Optional[str] = None,
        access_mode: NVMAccessMode = NVMAccessMode.READ_WRITE,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> NVMAssignment:
        """Assign NVM block to a model, stack, network, etc."""

        block = self.get_block(block_id)
        if not block:
            raise ValueError(f"Block {block_id} not found")

        assignment_id = f"{block_id}::{assignment_type.value}::{target_id}"

        assignment = NVMAssignment(
            assignment_id=assignment_id,
            assignment_type=assignment_type,
            target_id=target_id,
            target_name=target_name,
            access_mode=access_mode,
            priority=priority,
            metadata=metadata or {}
        )

        block.assignments.append(assignment)
        block.updated_at = datetime.utcnow().isoformat() + "Z"

        self._save_block(block)
        self._save_assignment(assignment, block_id)

        return assignment

    def add_directory(
        self,
        block_id: str,
        directory_id: str,
        path: str,
        purpose: str,
        **kwargs
    ) -> NVMDirectory:
        """Add directory to NVM block for file management"""

        block = self.get_block(block_id)
        if not block:
            raise ValueError(f"Block {block_id} not found")

        directory = NVMDirectory(
            directory_id=directory_id,
            path=path,
            purpose=purpose,
            **kwargs
        )

        block.directories.append(directory)
        block.updated_at = datetime.utcnow().isoformat() + "Z"

        self._save_block(block)
        return directory

    def add_preload(
        self,
        block_id: str,
        preload_id: str,
        source_type: Literal["file", "directory", "url", "inline"],
        source_path: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs
    ) -> NVMPreloadConfig:
        """Add preload configuration to NVM block"""

        block = self.get_block(block_id)
        if not block:
            raise ValueError(f"Block {block_id} not found")

        preload = NVMPreloadConfig(
            preload_id=preload_id,
            source_type=source_type,
            source_path=source_path,
            content=content,
            **kwargs
        )

        block.preloads.append(preload)
        block.updated_at = datetime.utcnow().isoformat() + "Z"

        self._save_block(block)
        return preload

    def get_block(self, block_id: str) -> Optional[NVMBlockSchema]:
        """Retrieve NVM block by ID"""
        block_file = self.blocks_dir / f"{self._sanitize_id(block_id)}.json"
        if not block_file.exists():
            raise ValueError(f"Block not found: {block_id}")

        with open(block_file, 'r') as f:
            data = json.load(f)
            return self._dict_to_block(data)

    def list_blocks(
        self,
        block_class: Optional[NVMBlockClass] = None,
        assignment_type: Optional[NVMAssignmentType] = None,
        target_id: Optional[str] = None
    ) -> List[NVMBlockSchema]:
        """List NVM blocks with optional filtering"""
        blocks = []

        for block_file in self.blocks_dir.glob("*.json"):
            with open(block_file, 'r') as f:
                data = json.load(f)
                block = self._dict_to_block(data)

                # Apply filters
                if block_class and block.block_class != block_class:
                    continue

                if assignment_type or target_id:
                    matching_assignment = False
                    for assignment in block.assignments:
                        if assignment_type and assignment.assignment_type != assignment_type:
                            continue
                        if target_id and assignment.target_id != target_id:
                            continue
                        matching_assignment = True
                        break

                    if not matching_assignment:
                        continue

                blocks.append(block)

        return blocks

    def delete_block(self, block_id: str) -> bool:
        """Delete NVM block"""
        block_file = self.blocks_dir / f"{self._sanitize_id(block_id)}.json"
        if block_file.exists():
            block_file.unlink()
            return True
        return False

    def _save_block(self, block: NVMBlockSchema):
        """Save block to storage"""
        block_file = self.blocks_dir / f"{self._sanitize_id(block.block_id)}.json"
        with open(block_file, 'w') as f:
            json.dump(block.to_dict(), f, indent=2)

    def _save_assignment(self, assignment: NVMAssignment, block_id: str):
        """Save assignment record"""
        assignment_file = self.assignments_dir / f"{self._sanitize_id(assignment.assignment_id)}.json"
        with open(assignment_file, 'w') as f:
            json.dump({
                "assignment": assignment.to_dict(),
                "block_id": block_id
            }, f, indent=2)

    def _sanitize_id(self, id_str: str) -> str:
        """Sanitize ID for filename"""
        return id_str.replace("://", "_").replace("/", "_").replace(":", "_")

    def _dict_to_block(self, data: Dict[str, Any]) -> NVMBlockSchema:
        """Convert dictionary to NVMBlockSchema"""
        return NVMBlockSchema(
            block_id=data["block_id"],
            name=data["name"],
            description=data["description"],
            block_class=NVMBlockClass(data["class"]),
            geometry=NVMGeometryConfig(**data["geometry"]),
            index=NVMIndexConfig(**data["index"]),
            codebook=NVMCodebookConfig(**data["codebook"]),
            max_vectors=data.get("max_vectors"),
            max_size_mb=data.get("max_size_mb"),
            retention_days=data.get("retention_days"),
            assignments=[
                NVMAssignment(
                    assignment_id=a["assignment_id"],
                    assignment_type=NVMAssignmentType(a["assignment_type"]),
                    target_id=a["target_id"],
                    target_name=a.get("target_name"),
                    access_mode=NVMAccessMode(a["access_mode"]),
                    priority=a.get("priority", 0),
                    metadata=a.get("metadata", {}),
                    created_at=a["created_at"]
                )
                for a in data.get("assignments", [])
            ],
            directories=[
                NVMDirectory(**d)
                for d in data.get("directories", [])
            ],
            preloads=[
                NVMPreloadConfig(**p)
                for p in data.get("preloads", [])
            ],
            version=data.get("version", "1.0.0"),
            schema_version=data.get("schema_version", "nvm_block"),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            metadata=data.get("metadata", {})
        )
