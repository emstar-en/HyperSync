
from typing import Any, Dict, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

class UIRHeader(BaseModel):
    id: str
    type: str
    created_at: datetime
    source_metadata: Dict[str, Any]

class BaseUIR(BaseModel):
    header: UIRHeader
    payload: Any

    @classmethod
    def create(cls, type_name: str, payload: Any, metadata: Dict[str, Any] = None):
        return cls(
            header=UIRHeader(
                id=str(uuid.uuid4()),
                type=type_name,
                created_at=datetime.now(),
                source_metadata=metadata or {}
            ),
            payload=payload
        )
