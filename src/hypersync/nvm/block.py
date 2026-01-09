
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from typing_extensions import Literal


class NVMGeometryConfig(BaseModel):
    space: Literal[
        "euclidean",
        "spherical",
        "poincare_ball",
        "hyperboloid",
        "spd_logeuclid",
    ]
    curvature: Optional[float] = None
    radius_cap: Optional[float] = Field(default=None, alias="radius_cap")


class NVMIndexConfig(BaseModel):
    type: Literal["hnsw_euclidean", "hnsw_hyperbolic", "ivfpq", "bruteforce"]
    params: Dict[str, Any] = Field(default_factory=dict)


class NVMCodebookConfig(BaseModel):
    type: Literal["opq_pq", "pq"]
    opq_dim: Optional[int] = None
    pq_m: Optional[int] = None
    pq_bits: Optional[int] = None
    commitment: Optional[str] = None

    def model_post_init(self, __ctx: Any) -> None:
        if self.type == "opq_pq" and self.opq_dim is None:
            raise ValueError("opq_pq codebooks require opq_dim")
        if self.pq_m is None or self.pq_bits is None:
            raise ValueError("pq_m and pq_bits are required for codebooks")


class BlockVersions(BaseModel):
    current: int
    history: List[int] = Field(default_factory=list)

    def model_post_init(self, __ctx: Any) -> None:
        if self.current < 0:
            raise ValueError("current version must be non-negative")
        for entry in self.history:
            if entry > self.current:
                raise ValueError("history versions cannot exceed current")


class RetentionPolicy(BaseModel):
    tier: Optional[Literal["hot", "cold"]] = None
    ttl_days: Optional[int] = Field(default=None, ge=0)


class BlockDescriptor(BaseModel):
    block_id: str
    class_: Literal[
        "commitment",
        "sketch",
        "stats",
        "embedding_pq",
        "index_ivfpq",
        "plan_hints",
    ] = Field(alias="class")
    geometry: NVMGeometryConfig
    index: NVMIndexConfig
    codebook: Optional[NVMCodebookConfig] = None
    versions: BlockVersions
    retention: Optional[RetentionPolicy] = None
    policy_digest: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "use_enum_values": True,
    }

    @classmethod
    def from_file(cls, path: Path | str) -> "BlockDescriptor":
        return cls.model_validate_json(Path(path).read_text())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlockDescriptor":
        return cls.model_validate(data)

    def payload(self) -> Dict[str, Any]:
        """Return the canonical payload dictionary for hashing."""
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)

    def payload_bytes(self) -> bytes:
        canonical = json.dumps(self.payload(), sort_keys=True, separators=(",", ":"))
        return canonical.encode("utf-8")

    def compute_payload_commitment(self) -> str:
        digest = hashlib.sha256(self.payload_bytes()).hexdigest()
        return f"sha256:{digest}"


def load_block_descriptor(path: Path | str) -> BlockDescriptor:
    return BlockDescriptor.from_file(path)
