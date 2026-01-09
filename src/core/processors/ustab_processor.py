
import csv
import io
from typing import Any, Dict
from .base import BaseProcessor
from ..uir.types import USTAB

class USTABProcessor(BaseProcessor):
    def __init__(self):
        super().__init__(
            id="core_ustab_processor",
            input_types=["text/csv", "application/json"],
            output_type="USTAB"
        )

    def process(self, data: Any, metadata: Dict[str, Any]) -> USTAB:
        """
        Converts CSV string or list of dicts to USTAB.
        """
        print(f"[USTABProcessor] Processing data with metadata: {metadata}")

        columns = []
        rows = []

        # Simple CSV parsing logic
        if metadata.get("mime") == "text/csv" or metadata.get("extension") == ".csv":
            if isinstance(data, bytes):
                data = data.decode('utf-8')

            f = io.StringIO(data)
            reader = csv.reader(f)
            try:
                columns = next(reader)
                for row in reader:
                    rows.append(row)
            except StopIteration:
                pass # Empty file

        payload = {
            "columns": columns,
            "row_count": len(rows),
            "data": rows # In a real system, this might be a reference to a dataframe
        }

        return USTAB.create("USTAB", payload, metadata)

# Auto-initialize
default_ustab_processor = USTABProcessor()
