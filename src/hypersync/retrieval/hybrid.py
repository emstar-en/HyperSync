
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from .config import HybridRetrievalConfig, RadiusStrategy


@dataclass
class RetrievalItem:
    id: str
    vector: Sequence[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    id: str
    distance: float
    rank: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HybridRetrievalRun:
    results: List[RetrievalResult]
    candidate_count: int
    radius_used: Optional[float]
    ann_index: str
    ann_params: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    outside_min_distance: Optional[float] = None


class HybridRetrievalEngine:
    """Two-stage retrieval engine that follows the hybrid spec."""

    def __init__(self, config: HybridRetrievalConfig):
        self.config = config

    def run(
        self,
        query: Sequence[float],
        items: Iterable[RetrievalItem],
        *,
        top_k: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> HybridRetrievalRun:
        items_list = list(items)
        if not items_list:
            raise ValueError("No candidate items provided")
        cfg = self.config
        rng = np.random.default_rng(cfg.determinism_seed(seed or 0))

        approx = self._ann_stage(query, items_list, rng)
        candidate_pool = cfg.candidate_pool_size(len(approx))
        ann_candidates = approx[:candidate_pool]
        radius, refined, outside_min, exact_distances = self._refine_stage(query, ann_candidates, top_k)
        ann_params = {
            key: getattr(cfg.ann, key)
            for key in ("index", "M", "ef_runtime", "ef_construction", "k")
            if getattr(cfg.ann, key) is not None
        }
        diagnostics: Dict[str, Any] = {}
        if ann_candidates:
            approx_scores = [score for score, _ in ann_candidates]
            diagnostics.update(
                {
                    "approx_mean": float(np.mean(approx_scores)),
                    "approx_std": float(np.std(approx_scores)),
                    "approx_min": float(min(approx_scores)),
                    "approx_max": float(max(approx_scores)),
                    "candidate_count": len(ann_candidates),
                }
            )
        if exact_distances:
            diagnostics.update(
                {
                    "exact_mean": float(np.mean(exact_distances)),
                    "exact_std": float(np.std(exact_distances)),
                    "exact_min": float(min(exact_distances)),
                    "exact_max": float(max(exact_distances)),
                    "exact_count": len(exact_distances),
                }
            )
        if outside_min is not None:
            diagnostics["outside_min_distance"] = float(outside_min)

        results = [
            RetrievalResult(id=item.id, distance=dist, rank=idx + 1, metadata=item.metadata)
            for idx, (dist, item) in enumerate(refined)
        ]
        return HybridRetrievalRun(
            results=results,
            candidate_count=len(ann_candidates),
            radius_used=radius,
            ann_index=cfg.ann.index,
            ann_params=ann_params,
            diagnostics=diagnostics,
            outside_min_distance=outside_min,
        )

    def _ann_stage(
        self,
        query: Sequence[float],
        items: List[RetrievalItem],
        rng: np.random.Generator,
    ) -> List[Tuple[float, RetrievalItem]]:
        cfg = self.config
        jitter = self._ann_jitter_scale(cfg.ann.index)
        approx_with_index: List[Tuple[float, RetrievalItem, int]] = []
        tie_strategy = cfg.determinism_tie_break()
        for idx, item in enumerate(items):
            approx_dist = self._distance(query, item.vector)
            if jitter > 0.0:
                approx_dist += float(rng.normal(0.0, jitter))
            approx_with_index.append((approx_dist, item, idx))
        if tie_strategy == "lexicographic":
            approx_with_index.sort(key=lambda t: (t[0], t[1].id))
        else:
            approx_with_index.sort(key=lambda t: (t[0], t[2]))
        return [(score, item) for score, item, _ in approx_with_index]

    def _refine_stage(
        self,
        query: Sequence[float],
        candidates: List[Tuple[float, RetrievalItem]],
        top_k: Optional[int],
    ) -> Tuple[Optional[float], List[Tuple[float, RetrievalItem]], Optional[float], List[float]]:
        cfg = self.config
        exact: List[Tuple[float, RetrievalItem]] = []
        for _, item in candidates:
            dist = self._distance(query, item.vector)
            exact.append((dist, item))
        if not exact:
            return None, [], None, []
        exact.sort(key=lambda t: t[0])
        eff_k = top_k or cfg.effective_k()
        mode = cfg.refine.mode
        exact_distances = [dist for dist, _ in exact]
        outside_min: Optional[float] = None
        if mode == "exact_topk":
            trimmed = exact[:eff_k]
            if len(exact) > eff_k:
                outside_min = exact[eff_k][0]
            return None, trimmed, outside_min, exact_distances
        if mode == "exact_within_radius":
            radius = self._determine_radius(exact, eff_k)
            filtered = [pair for pair in exact if pair[0] <= radius + 1e-12]
            outside_candidates = [dist for dist in exact_distances if dist > radius + 1e-12]
            if outside_candidates:
                outside_min = min(outside_candidates)
            return radius, filtered, outside_min, exact_distances
        trimmed = exact[:eff_k]
        if len(exact) > eff_k:
            outside_min = exact[eff_k][0]
        return None, trimmed, outside_min, exact_distances

    def _ann_jitter_scale(self, index: str) -> float:
        if index == "bruteforce":
            return 0.0
        if index.startswith("hnsw"):
            return 0.01
        if index == "ivfpq":
            return 0.02
        return 0.005

    def _determine_radius(
        self,
        exact: List[Tuple[float, RetrievalItem]],
        eff_k: int,
    ) -> float:
        cfg = self.config
        strategy: RadiusStrategy | None = cfg.refine.radius_strategy
        eps = cfg.refine.eps or 0.0
        if strategy == "fixed" and cfg.refine.r is not None:
            return float(cfg.refine.r)
        if strategy == "quantile" and cfg.refine.r is not None:
            q = max(0.0, min(1.0, cfg.refine.r))
            idx = min(int(round(q * (len(exact) - 1))), len(exact) - 1)
            return float(exact[idx][0] + eps)
        pivot_idx = min(max(eff_k, 1), len(exact)) - 1
        pivot = exact[pivot_idx][0]
        return float(pivot + eps)

    def _distance(self, a: Sequence[float], b: Sequence[float]) -> float:
        space = self.config.geometry.space
        if space == "euclidean":
            return float(np.linalg.norm(np.asarray(a) - np.asarray(b)))
        if space == "poincare_ball":
            return self._poincare_distance(np.asarray(a), np.asarray(b))
        if space == "hyperboloid":
            return self._hyperboloid_distance(np.asarray(a), np.asarray(b))
        if space == "spherical":
            return self._spherical_distance(np.asarray(a), np.asarray(b))
        raise ValueError(f"Unsupported geometry space: {space}")

    def _poincare_distance(self, u: np.ndarray, v: np.ndarray) -> float:
        cu = float(np.linalg.norm(u) ** 2)
        cv = float(np.linalg.norm(v) ** 2)
        diff = float(np.linalg.norm(u - v) ** 2)
        curvature = self.config.geometry.curvature or -1.0
        denom = (1 - curvature * cu) * (1 - curvature * cv)
        argument = 1 + 2 * curvature * diff / max(1e-12, denom)
        argument = max(1.0, argument)
        return float(np.arccosh(argument))

    def _hyperboloid_distance(self, u: np.ndarray, v: np.ndarray) -> float:
        curvature = self.config.geometry.curvature or -1.0
        minkowski = -u[0] * v[0] + np.dot(u[1:], v[1:])
        argument = -curvature * minkowski
        argument = max(1.0, argument)
        return float(np.arccosh(argument))

    def _spherical_distance(self, u: np.ndarray, v: np.ndarray) -> float:
        dot = float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))
        dot = max(-1.0, min(1.0, dot))
        radius = self.config.geometry.radius_cap or 1.0
        return float(radius * math.acos(dot))
