from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..receipts.codec import compute_receipt_hash
from .config import HybridRetrievalConfig
from .hybrid import HybridRetrievalRun


class RetrievalResultEntry(BaseModel):
    id: str
    d: float = Field(alias="distance")
    rank: int
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True


class RetrievalExactnessReceipt(BaseModel):
    receipt_kind: str = Field(default="RetrievalExactnessReceipt")
    metric_id: str
    index_commitment: str
    query_commitment: str
    k: int
    ann_params: Dict[str, Any] = Field(default_factory=dict)
    refine: Dict[str, Any]
    candidate_count: int
    determinism: Dict[str, Any] = Field(default_factory=dict)
    results: List[Dict[str, Any]] = Field(default_factory=list)
    verification: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str
    codebook_commitment: Optional[str] = None
    hash: Optional[str] = None
    signature: Optional[str] = None

    class Config:
        populate_by_name = True


def build_exactness_receipt(
    config: HybridRetrievalConfig,
    run: HybridRetrievalRun,
    *,
    query_commitment: str,
    index_commitment: str,
    codebook_commitment: Optional[str] = None,
    metric_id: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    extra_determinism: Optional[Dict[str, Any]] = None,
) -> RetrievalExactnessReceipt:
    ts = (timestamp or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    metric = metric_id or _default_metric_id(config)

determinism = {
    "seed": config.determinism.seed,
    "tie_break": config.determinism.tie_break,
}
if extra_determinism:
    determinism.update(extra_determinism)
determinism = {k: v for k, v in determinism.items() if v is not None}
refine_block = {
    "mode": config.refine.mode,
}
if config.refine.r is not None:
    refine_block["r"] = config.refine.r
if config.refine.eps is not None:
    refine_block["eps"] = config.refine.eps
if config.refine.radius_strategy:
    refine_block["radius_strategy"] = config.refine.radius_strategy
verification: Dict[str, Any] = {
    "mode": config.refine.mode,
    "radius_strategy": config.refine.radius_strategy,
}
if run.radius_used is not None:
    verification["r_used"] = run.radius_used
if run.outside_min_distance is not None:
    verification["outside_min_distance"] = run.outside_min_distance
if run.diagnostics and _field_in_receipt(config, "diagnostics"):
    verification["diagnostics"] = run.diagnostics
if _field_in_receipt(config, "candidate_count"):
    verification.setdefault("summary", {})["candidate_count"] = run.candidate_count
assertion = _build_verification_assertion(config, run)
if assertion:
    verification["assertion"] = assertion
results_payload = []
for res in run.results:
    entry: Dict[str, Any] = {"id": res.id, "d": res.distance, "rank": res.rank}
    if res.metadata:
        entry["metadata"] = res.metadata
    results_payload.append(entry)
    receipt = RetrievalExactnessReceipt(
        metric_id=metric,
        index_commitment=index_commitment,
        codebook_commitment=codebook_commitment,
        query_commitment=query_commitment,
        k=len(run.results) if run.results else config.effective_k(),
        ann_params={**run.ann_params, "index": run.ann_index},
        refine=refine_block,
        candidate_count=run.candidate_count,
        determinism=determinism,
        results=results_payload,
        verification={k: v for k, v in verification.items() if v is not None},
        timestamp=ts,
    )
    if _field_in_receipt(config, "diagnostics") and run.diagnostics:
        receipt.verification.setdefault("diagnostics", run.diagnostics)
    if _field_in_receipt(config, "ann_index"):
        receipt.verification["ann_index"] = run.ann_index
    return receipt


def hash_exactness_receipt(receipt: RetrievalExactnessReceipt) -> str:
    payload = receipt.model_dump(mode="json", by_alias=True, exclude_none=True)
    digest = compute_receipt_hash(payload)
    receipt.hash = digest
    return digest


def sign_exactness_receipt(
    receipt: RetrievalExactnessReceipt,
    secret: Optional[str] = None,
) -> RetrievalExactnessReceipt:
    digest = hash_exactness_receipt(receipt)
    key = secret or os.getenv("HYPERSYNC_HMAC_SECRET")
    if not key:
        return receipt
    sig_bytes = hmac.new(key.encode("utf-8"), msg=digest.encode("utf-8"), digestmod=hashlib.sha256).digest()
    receipt.signature = base64.urlsafe_b64encode(sig_bytes).decode("ascii")
    return receipt


def _build_verification_assertion(config: HybridRetrievalConfig, run: HybridRetrievalRun) -> Optional[str]:
    """Produce the verification assertion text required by the spec."""
    mode = config.refine.mode
    if mode == "exact_within_radius":
        if run.radius_used is not None:
            return "All items with d <= r evaluated exactly; no item with d < best_k omitted"
        return "Exact radius evaluation performed"
    if mode == "exact_topk":
        return "Top-k candidates reevaluated exactly; no closer item exists beyond evaluated set"
    return None


def _default_metric_id(config: HybridRetrievalConfig) -> str:
    curvature = config.geometry.curvature
    if curvature is not None:
        return f"{config.geometry.space}:c={curvature}"
    return config.geometry.space


def _field_in_receipt(config: HybridRetrievalConfig, field_name: str) -> bool:
    return any(f.lower() == field_name.lower() for f in config.included_receipt_fields())
