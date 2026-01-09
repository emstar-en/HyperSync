
from datetime import datetime, timezone

from hypersync.nvm import (
    BlockDescriptor,
    BlockWriteReceipt,
    build_block_write_receipt,
    sign_block_write_receipt,
    verify_block_write_receipt,
)


def _example_descriptor() -> BlockDescriptor:
    return BlockDescriptor.from_dict(
        {
            "block_id": "ld://E42/ADVANCED/memory/hyperbolic_kg.v3",
            "class": "embedding_pq",
            "geometry": {
                "space": "poincare_ball",
                "curvature": -1.0,
                "radius_cap": 0.98,
            },
            "index": {
                "type": "hnsw_hyperbolic",
                "params": {"M": 32, "ef_construction": 200, "ef_runtime": 64},
            },
            "codebook": {
                "type": "opq_pq",
                "opq_dim": 64,
                "pq_m": 16,
                "pq_bits": 8,
                "commitment": "sha256:codebook123",
            },
            "versions": {
                "current": 3,
                "history": [1, 2],
            },
            "retention": {
                "tier": "hot",
                "ttl_days": 90,
            },
            "policy_digest": "sha256:policyNVMv1",
        }
    )


def test_block_descriptor_commitment_deterministic():
    descriptor = _example_descriptor()
    commitment = descriptor.compute_payload_commitment()
    assert commitment.startswith("sha256:")
    assert len(commitment) == len("sha256:") + 64


def test_build_and_sign_block_write_receipt():
    descriptor = _example_descriptor()
    ts = datetime(2024, 12, 1, 12, 0, tzinfo=timezone.utc)
    receipt = build_block_write_receipt(
        descriptor,
        writer="entity://ops/team-alpha",
        profile="ADVANCED",
        input_commitments=["sha256:input1"],
        policy_hits=["sha256:policyNVMv1"],
        timestamp=ts,
    )
    assert receipt.hash is not None
    assert receipt.payload_commitment == descriptor.compute_payload_commitment()

    secret = "sup3rsecret"
    signed = sign_block_write_receipt(receipt, secret)
    ok, err = verify_block_write_receipt(signed, secret)
    assert ok is True
    assert err is None

    ok, err = verify_block_write_receipt(signed, "wrong")
    assert ok is False
    assert err == "Invalid signature"
