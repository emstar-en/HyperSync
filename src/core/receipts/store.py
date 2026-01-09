"""
Receipt Store
Emits and stores audit receipts for all operator invocations.
"""
from typing import Dict, Any, Optional
import uuid
import json
import time
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ReceiptStore:
    """Persistent store for audit receipts."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("/var/hypersync/receipts")
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def emit(
        self,
        event: str,
        tier: str,
        payload: Dict[str, Any],
        result: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        status: str = "success"
    ) -> str:
        """
        Emit an audit receipt.

        Returns:
            Receipt ID (UUID)
        """
        receipt_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        receipt = {
            "receipt_id": receipt_id,
            "event": event,
            "tier": tier,
            "timestamp": timestamp,
            "status": status,
            "user_id": user_id,
            "session_id": session_id,
            "payload": payload,
            "result": result
        }

        # Write to storage
        receipt_file = self.storage_path / f"{receipt_id}.json"
        try:
            with open(receipt_file, 'w') as f:
                json.dump(receipt, f, indent=2)
            logger.debug(f"Emitted receipt {receipt_id} for event '{event}'")
        except Exception as e:
            logger.error(f"Failed to write receipt {receipt_id}: {e}")

        return receipt_id

    def get(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a receipt by ID."""
        receipt_file = self.storage_path / f"{receipt_id}.json"
        if not receipt_file.exists():
            return None

        with open(receipt_file, 'r') as f:
            return json.load(f)

    def query(
        self,
        event: Optional[str] = None,
        tier: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """Query receipts by criteria."""
        results = []

        for receipt_file in sorted(self.storage_path.glob("*.json"), reverse=True):
            if len(results) >= limit:
                break

            try:
                with open(receipt_file, 'r') as f:
                    receipt = json.load(f)

                # Apply filters
                if event and receipt.get("event") != event:
                    continue
                if tier and receipt.get("tier") != tier:
                    continue
                if user_id and receipt.get("user_id") != user_id:
                    continue

                results.append(receipt)
            except Exception as e:
                logger.warning(f"Could not read receipt {receipt_file}: {e}")

        return results


# Global receipt store
_store = ReceiptStore()


def emit_receipt(
    event: str,
    tier: str,
    payload: Dict[str, Any],
    result: Dict[str, Any],
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    status: str = "success"
) -> str:
    """Convenience function to emit a receipt."""
    return _store.emit(
        event=event,
        tier=tier,
        payload=payload,
        result=result,
        user_id=user_id,
        session_id=session_id,
        status=status
    )


def get_receipt(receipt_id: str) -> Optional[Dict[str, Any]]:
    """Convenience function to retrieve a receipt."""
    return _store.get(receipt_id)


def query_receipts(**kwargs) -> list:
    """Convenience function to query receipts."""
    return _store.query(**kwargs)
