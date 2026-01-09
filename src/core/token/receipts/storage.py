"""
Receipt Storage

Persists receipts to disk for audit and analysis.
"""

import json
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .accumulator import TokenReceipt


class ReceiptStorage:
    """
    Stores receipts to disk.

    Organizes receipts by date for efficient retrieval and cleanup.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path.home() / ".hypersync" / "receipts"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, receipt: TokenReceipt):
        """
        Save a receipt to disk.

        Receipts are organized by date: YYYY/MM/DD/receipt_id.json
        """
        # Parse timestamp
        timestamp = datetime.fromisoformat(receipt.timestamp.rstrip('Z'))

        # Create date-based directory
        date_dir = self.storage_dir / str(timestamp.year) / f"{timestamp.month:02d}" / f"{timestamp.day:02d}"
        date_dir.mkdir(parents=True, exist_ok=True)

        # Save receipt
        receipt_file = date_dir / f"{receipt.receipt_id}.json"
        with open(receipt_file, 'w') as f:
            json.dump(receipt.to_dict(), f, indent=2)

    def load(self, receipt_id: str) -> Optional[TokenReceipt]:
        """
        Load a receipt by ID.

        Searches all date directories.
        """
        for root, dirs, files in os.walk(self.storage_dir):
            for file in files:
                if file == f"{receipt_id}.json":
                    file_path = Path(root) / file
                    with open(file_path) as f:
                        data = json.load(f)
                    return TokenReceipt(**data)

        return None

    def list_by_date(self, year: int, month: int, day: int) -> List[TokenReceipt]:
        """Load all receipts for a specific date."""
        date_dir = self.storage_dir / str(year) / f"{month:02d}" / f"{day:02d}"

        if not date_dir.exists():
            return []

        receipts = []
        for file in date_dir.glob("*.json"):
            with open(file) as f:
                data = json.load(f)
            receipts.append(TokenReceipt(**data))

        return receipts

    def list_by_user(self, user_id: str, limit: int = 100) -> List[TokenReceipt]:
        """Load receipts for a specific user."""
        receipts = []

        for root, dirs, files in os.walk(self.storage_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = Path(root) / file
                    with open(file_path) as f:
                        data = json.load(f)

                    if data.get("user_id") == user_id:
                        receipts.append(TokenReceipt(**data))

                    if len(receipts) >= limit:
                        return receipts

        return receipts

    def cleanup_old(self, days: int = 90):
        """Delete receipts older than specified days."""
        cutoff = datetime.utcnow().timestamp() - (days * 86400)

        for root, dirs, files in os.walk(self.storage_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = Path(root) / file

                    # Check file modification time
                    if file_path.stat().st_mtime < cutoff:
                        file_path.unlink()
