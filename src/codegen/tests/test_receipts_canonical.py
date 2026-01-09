from datetime import timedelta

from hypersync_python.hypersync.core.models import Intent
from hypersync_python.hypersync.receipts.codec import (
    compute_receipt_hash,
    make_receipt,
    sign_receipt,
    verify_receipt,
)


def test_receipt_hash_ignores_timestamp():
    intent = Intent(id="intent-ts", params={"x": 1})
    receipt = make_receipt(intent, "sync.op", {"value": 42.0})
    later = receipt.model_copy(update={"ts": receipt.ts + timedelta(minutes=5)})

    assert compute_receipt_hash(receipt) == compute_receipt_hash(later)


def test_receipt_hash_quantizes_fp16():
    hash_a = compute_receipt_hash("sync.op", {"score": 0.123456}, "intent-ref")
    hash_b = compute_receipt_hash("sync.op", {"score": 0.123456 + 1e-6}, "intent-ref")

    assert hash_a == hash_b


def test_sign_and_verify_receipt_round_trip():
    intent = Intent(id="intent-verify")
    receipt = make_receipt(intent, "sync.op", {"value": 1.0})

    signed = sign_receipt(receipt, "super-secret")
    ok, err = verify_receipt(signed, "super-secret")
    assert ok
    assert err is None

    tampered = signed.model_copy(deep=True)
    tampered.outputs["value"] = 2.0

    ok, err = verify_receipt(tampered, "super-secret")
    assert not ok
    assert err == "Receipt hash mismatch"
