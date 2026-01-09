from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import os
import struct
from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Tuple
import logging

from ..core.models import Intent, Receipt, ReceiptProvenance

logger = logging.getLogger(__name__)

CANON_SEPARATORS = (",", ":")
_EXCLUDED_RECEIPT_KEYS = {"hash", "signature", "ts", "logical_time"}


def _quantize_float(value: float) -> float:
    """Quantize a float to fp16 with round-to-even, then promote to fp32."""
    if math.isnan(value) or math.isinf(value):
        return value
    quantized = value
    try:
        quantized = struct.unpack("<e", struct.pack("<e", quantized))[0]
    except (struct.error, OverflowError) as e:
        # Value outside fp16 range - fall back to fp32 quantization only.
        logger.debug(f"FP16 quantization failed for {value}, falling back to FP32: {e}")
    try:
        quantized = struct.unpack("<f", struct.pack("<f", quantized))[0]
    except (struct.error, OverflowError) as e:
        # If promotion fails, retain the current value.
        logger.warning(f"FP32 quantization failed for {value}, retaining original: {e}")
    return quantized


def _normalize_value(value: Any) -> Any:
    """Recursively normalize values for canonical JSON serialization."""
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (float, Decimal)):
        return _quantize_float(float(value))
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "model_dump"):
        return _normalize_value(value.model_dump(exclude_none=True))
    if isinstance(value, Mapping):
        return {str(k): _normalize_value(v) for k, v in value.items()}
    if isinstance(value, set):
        normalized_items = [_normalize_value(item) for item in value]
        return sorted(normalized_items, key=lambda obj: json.dumps(obj, sort_keys=True, default=str))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalize_value(item) for item in value]
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(value).decode("ascii")
    return str(value)


def _canonical_json(payload: Mapping[str, Any]) -> str:
    normalized = _normalize_value(payload)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=CANON_SEPARATORS,
        allow_nan=False,
    )


def _core_receipt_payload(receipt: Receipt) -> Dict[str, Any]:
    data = receipt.model_dump(mode="json", exclude_none=True)
    for key in _EXCLUDED_RECEIPT_KEYS:
        data.pop(key, None)
    return data


def compute_receipt_hash(
    subject: Receipt | Mapping[str, Any] | str | None,
    outputs: Dict[str, Any] | None = None,
    intent_ref: str | None = None,
    *,
    status: str | None = None,
    receipt_id: str | None = None,
    provenance: ReceiptProvenance | Mapping[str, Any] | None = None,
    errors: Sequence[str] | None = None,
) -> str:
    """Compute a canonical SHA-256 hash for a receipt or its core payload."""
    if subject is None:
        raise ValueError("Must provide a receipt, payload, or operator identifier")

    if isinstance(subject, Receipt):
        payload: Dict[str, Any] = _core_receipt_payload(subject)
    elif isinstance(subject, Mapping) and not isinstance(subject, str):
        payload = {str(k): v for k, v in subject.items()}
    else:
        payload = {
            "op": subject,
            "outputs": outputs or {},
            "intent_ref": intent_ref,
        }
        if status is not None:
            payload["status"] = status
        if receipt_id is not None:
            payload["id"] = receipt_id
        if errors is not None:
            payload["errors"] = list(errors)
        if provenance is not None:
            if isinstance(provenance, ReceiptProvenance):
                payload["provenance"] = provenance.model_dump(exclude_none=True)
            else:
                payload["provenance"] = dict(provenance)

    for key in _EXCLUDED_RECEIPT_KEYS:
        payload.pop(key, None)

    canonical = f"{_canonical_json(payload)}\n"
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return digest


def _hash_intent(intent: Intent) -> str:
    payload = intent.model_dump(mode="json", exclude_none=True)
    canonical = f"{_canonical_json(payload)}\n"
    digest = hashlib.sha256(canonical.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest[:16]).decode("ascii")


def _maybe_sign(hash_text: str, secret: str | None) -> str | None:
    if not secret:
        return None
    sig = hmac.new(secret.encode("utf-8"), msg=hash_text.encode("utf-8"), digestmod=hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode("ascii")


def sign_receipt(receipt: Receipt, secret: str) -> Receipt:
    receipt.hash = compute_receipt_hash(receipt)
    receipt.signature = _maybe_sign(receipt.hash, secret)
    return receipt


def verify_receipt(receipt: Receipt, secret: str) -> Tuple[bool, str | None]:
    expected_hash = compute_receipt_hash(receipt)
    if receipt.hash and receipt.hash != expected_hash:
        return False, "Receipt hash mismatch"
    hash_text = receipt.hash or expected_hash
    signature = _maybe_sign(hash_text, secret)
    if signature and receipt.signature == signature:
        return True, None
    return False, "Invalid signature or secret"


def make_receipt(
    intent: Intent,
    op: str,
    outputs: Dict[str, Any],
    status: str = "OK",
    provenance: ReceiptProvenance | None = None,
) -> Receipt:
    rid = _hash_intent(intent)
    prov = provenance or ReceiptProvenance(operator=op)
    receipt = Receipt(
        id=f"rcpt_{rid}",
        status=status,
        op=op,
        outputs=outputs,
        intent_ref=intent.id or f"intent_{rid}",
        provenance=prov,
    )
    receipt.hash = compute_receipt_hash(receipt)
    secret = os.getenv("HYPERSYNC_HMAC_SECRET")
    if secret:
        receipt.signature = _maybe_sign(receipt.hash, secret)
    return receipt
