
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from ..receipts.codec import compute_receipt_hash
from ..utils.crypto import hmac_b64
from .block import BlockDescriptor


class BlockWriteReceipt(BaseModel):
    receipt_kind: str = Field(default="BlockWriteReceipt")
    block_id: str
    writer: str
    input_commitments: List[str] = Field(default_factory=list)
    payload_commitment: str
    profile: str
    timestamp: str
    policy_hits: List[str] = Field(default_factory=list)
    hash: Optional[str] = None
    signature: Optional[str] = None

    class Config:
        populate_by_name = True

    @classmethod
    def from_file(cls, path: Path | str) -> "BlockWriteReceipt":
        return cls.model_validate_json(Path(path).read_text())


def _canonical_payload(receipt: BlockWriteReceipt) -> Dict[str, Any]:
    payload = receipt.model_dump(mode="json", by_alias=True, exclude_none=True)
    payload.pop("hash", None)
    payload.pop("signature", None)
    return payload


def build_block_write_receipt(
    descriptor: BlockDescriptor,
    *,
    writer: str,
    profile: str,
    input_commitments: Optional[List[str]] = None,
    policy_hits: Optional[List[str]] = None,
    timestamp: Optional[datetime] = None,
    payload_commitment: Optional[str] = None,
    auto_hash: bool = True,
) -> BlockWriteReceipt:
    ts = (timestamp or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    commit = payload_commitment or descriptor.compute_payload_commitment()
    receipt = BlockWriteReceipt(
        block_id=descriptor.block_id,
        writer=writer,
        input_commitments=list(input_commitments or []),
        payload_commitment=commit,
        profile=profile,
        timestamp=ts,
        policy_hits=list(policy_hits or []),
    )
    if auto_hash:
        receipt.hash = compute_receipt_hash(_canonical_payload(receipt))
    return receipt


def sign_block_write_receipt(receipt: BlockWriteReceipt, secret: str) -> BlockWriteReceipt:
    payload = _canonical_payload(receipt)
    receipt.hash = compute_receipt_hash(payload)
    receipt.signature = hmac_b64(secret, receipt.hash)
    return receipt


def verify_block_write_receipt(
    receipt: BlockWriteReceipt,
    secret: str,
) -> Tuple[bool, Optional[str]]:
    payload = _canonical_payload(receipt)
    expected_hash = compute_receipt_hash(payload)
    if receipt.hash and receipt.hash != expected_hash:
        return False, "Receipt hash mismatch"
    provided = receipt.hash or expected_hash
    expected_signature = hmac_b64(secret, provided)
    if receipt.signature == expected_signature:
        return True, None
    return False, "Invalid signature"


def load_block_write_receipt(path: Path | str) -> BlockWriteReceipt:
    return BlockWriteReceipt.from_file(path)
