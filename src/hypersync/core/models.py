from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
from datetime import datetime

class Intent(BaseModel):
    id: Optional[str] = None
    op: Optional[str] = Field(None, description="Operator id or routing key")
    params: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)

class ReceiptProvenance(BaseModel):
    spec_version: Optional[str] = None
    policy: Optional[str] = None
    operator: Optional[str] = None
    runtime: Optional[str] = "hypersync-python/0.0.9"

class Receipt(BaseModel):
    id: str
    status: str = Field("OK", regex="^(OK|FAIL)$")
    op: Optional[str] = None
    outputs: Dict[str, Any] = Field(default_factory=dict)
    errors: Optional[List[str]] = None
    ts: datetime = Field(default_factory=datetime.utcnow)
    intent_ref: Optional[str] = None
    provenance: ReceiptProvenance = Field(default_factory=ReceiptProvenance)
    hash: Optional[str] = Field(default=None, description="Canonical hash of receipt core payload")
    signature: Optional[str] = Field(default=None, description="HMAC signature over the receipt hash")
