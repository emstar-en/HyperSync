from __future__ import annotations
from pathlib import Path
from typing import Optional
from rich.table import Table
from rich.console import Console
import json

class ConformanceRunner:
    def __init__(self, vectors_dir: Path):
        self.vectors_dir = vectors_dir
        self.console = Console()

    def smoke(self, limit: Optional[int] = 20):
        files = [p for p in self.vectors_dir.rglob('*.json')] if self.vectors_dir.exists() else []
        files = files[:limit] if limit else files
        table = Table(title="Conformance Vectors (smoke list)")
        table.add_column("#", justify="right")
        table.add_column("Path")
        table.add_column("Top Keys")
        for i, p in enumerate(files, 1):
            try:
                obj = json.loads(p.read_text())
                keys = ", ".join(list(obj.keys())[:6]) if isinstance(obj, dict) else type(obj).__name__
            except Exception as e:
                keys = f"<read error: {e}>"
            table.add_row(str(i), str(p), keys)
        self.console.print(table)
