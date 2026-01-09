from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Literal, Optional

from pydantic import BaseModel, Field, validator

GeometrySpace = Literal["poincare_ball", "hyperboloid", "euclidean", "spherical"]
AnnIndex = Literal["hnsw_h", "hnsw_e", "ivfpq", "bruteforce"]
RefineMode = Literal["none", "exact_within_radius", "exact_topk"]
RadiusStrategy = Literal["pivot_k_plus_eps", "fixed", "quantile"]
TieBreakStrategy = Literal["lexicographic", "stable_index"]


class GeometryConfig(BaseModel):
    space: GeometrySpace
    curvature: Optional[float] = Field(default=None, description="Curvature parameter when applicable")
    radius_cap: Optional[float] = Field(default=None, ge=0.0)


class ANNConfig(BaseModel):
    index: AnnIndex
    M: Optional[int] = Field(default=None, ge=1)
    ef_construction: Optional[int] = Field(default=None, ge=1)
    ef_runtime: Optional[int] = Field(default=None, ge=1)
    k: Optional[int] = Field(default=None, ge=1)


class RefineConfig(BaseModel):
    mode: RefineMode = Field(default="none")
    radius_strategy: Optional[RadiusStrategy] = None
    r: Optional[float] = Field(default=None, gt=0)
    eps: Optional[float] = Field(default=None, ge=0)
    k: Optional[int] = Field(default=None, ge=1)

    @validator("radius_strategy", always=True)
    def _validate_radius_strategy(cls, value, values):
        mode: RefineMode = values.get("mode", "none")
        if mode == "exact_within_radius" and value is None:
            return "pivot_k_plus_eps"
        return value

    @validator("k", always=True)
    def _ensure_k(cls, value, values):
        mode: RefineMode = values.get("mode", "none")
        if mode in {"exact_within_radius", "exact_topk"} and value is None:
            return 50
        return value


class ReceiptsConfig(BaseModel):
    emit: List[str] = Field(default_factory=list)
    fields: List[str] = Field(default_factory=list)

    def wants_exactness_receipt(self) -> bool:
        return any(e.lower() == "retrievalexactnessreceipt" for e in self.emit)


class DeterminismConfig(BaseModel):
    seed: Optional[int] = None
    tie_break: Optional[TieBreakStrategy] = None


class HybridRetrievalConfig(BaseModel):
    geometry: GeometryConfig
    ann: ANNConfig
    refine: RefineConfig
    receipts: ReceiptsConfig = Field(default_factory=ReceiptsConfig)
    determinism: DeterminismConfig = Field(default_factory=DeterminismConfig)

    @classmethod
    def from_file(cls, path: Path | str) -> "HybridRetrievalConfig":
        return cls.model_validate_json(Path(path).read_text())

    @classmethod
    def from_dict(cls, data: dict) -> "HybridRetrievalConfig":
        return cls.model_validate(data)

    def candidate_pool_size(self, total_items: int) -> int:
        m = self.ann.M or 0
        if m <= 0:
            return total_items
        return min(m, total_items)

    def effective_k(self) -> int:
        cfg_k = self.refine.k or self.ann.k or 50
        return max(1, cfg_k)

    def determinism_seed(self, default: int = 0) -> int:
        if self.determinism.seed is not None:
            return self.determinism.seed
        return default

    def determinism_tie_break(self, default: TieBreakStrategy = "lexicographic") -> TieBreakStrategy:
        if self.determinism.tie_break:
            return self.determinism.tie_break
        return default

    def included_receipt_fields(self) -> Iterable[str]:
        return self.receipts.fields or []
