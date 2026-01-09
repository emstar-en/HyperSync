
from __future__ import annotations

from datetime import datetime

import numpy as np

from hypersync.retrieval import (
    HybridRetrievalConfig,
    HybridRetrievalEngine,
    RetrievalItem,
    build_exactness_receipt,
    hash_exactness_receipt,
)


def _make_config():
    return HybridRetrievalConfig.from_dict({
        "geometry": {"space": "euclidean"},
        "ann": {"index": "hnsw_e", "M": 4, "ef_runtime": 32, "k": 3},
        "refine": {"mode": "exact_within_radius", "radius_strategy": "pivot_k_plus_eps", "eps": 0.05, "k": 2},
        "receipts": {"emit": ["RetrievalExactnessReceipt"], "fields": ["diagnostics", "r_used", "candidate_count"]},
        "determinism": {"seed": 1234, "tie_break": "lexicographic"},
    })


def test_hybrid_retrieval_run_basic():
    cfg = _make_config()
    engine = HybridRetrievalEngine(cfg)
    query = [0.0, 0.0]
    items = [
        RetrievalItem(id="a", vector=[0.1, 0.05]),
        RetrievalItem(id="b", vector=[0.2, 0.01]),
        RetrievalItem(id="c", vector=[0.3, 0.3]),
        RetrievalItem(id="d", vector=[0.15, 0.04]),
    ]
    run = engine.run(query=query, items=items)
    assert run.candidate_count <= len(items)
    assert run.results[0].id in {"a", "d"}
    assert run.results[0].distance <= run.results[1].distance
    assert run.radius_used is not None
    assert run.diagnostics.get("candidate_count") == run.candidate_count
    if run.outside_min_distance is not None and run.radius_used is not None:
        assert run.outside_min_distance >= run.radius_used


def test_exactness_receipt_hash_stable():
    cfg = _make_config()
    engine = HybridRetrievalEngine(cfg)
    query = [0.05, 0.05]
    items = [
        RetrievalItem(id=str(i), vector=[float(i) / 10.0, 0.0])
        for i in range(6)
    ]
    run = engine.run(query=query, items=items)
    receipt = build_exactness_receipt(
        cfg,
        run,
        query_commitment="sha256:Q",
        index_commitment="sha256:IDX",
        codebook_commitment="sha256:CB",
        timestamp=datetime.utcfromtimestamp(0),
    )
    digest = hash_exactness_receipt(receipt)
    assert len(digest) == 64
    assert receipt.hash == digest
    assert receipt.results
    assert receipt.determinism["seed"] == 1234
    verification = receipt.verification
    assert "candidate_count" in verification.get("summary", {})


def test_exactness_receipt_verification_block():
    cfg = _make_config()
    engine = HybridRetrievalEngine(cfg)
    query = [0.05, -0.02]
    items = [
        RetrievalItem(id=str(i), vector=[float(i) * 0.03, float(i) * 0.01])
        for i in range(1, 8)
    ]
    run = engine.run(query=query, items=items)
    receipt = build_exactness_receipt(
        cfg,
        run,
        query_commitment="sha256:Q",
        index_commitment="sha256:IDX",
        codebook_commitment=None,
    )
    verification = receipt.verification
    assert verification["mode"] == cfg.refine.mode
    assert verification.get("outside_min_distance") is not None
    assert verification["outside_min_distance"] >= min(entry["d"] for entry in receipt.results)
    assert "assertion" in verification
    assert verification["summary"]["candidate_count"] == run.candidate_count
