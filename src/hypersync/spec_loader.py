
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .utils.fs import resolve_root


class SpecLoader:
    """Lightweight index over the unzipped spec pack."""

    def __init__(self, spec_root: str | Path | None = None):
        self.root = resolve_root(spec_root)
        if not self.root.exists():
            raise FileNotFoundError(f"Spec root not found: {self.root}")

    def path(self, *parts: str) -> Path:
        return self.root.joinpath(*parts)

    def dirs(self) -> Dict[str, Path]:
        return {
            "spec_pack": self.path("spec-pack"),
            "schemas": self.path("spec-pack", "schemas"),
            "vectors": self.path("conformance", "vectors"),
            "operators": self.path("operators"),
            "tools": self.path("tools"),
        }

    def list_schemas(self) -> List[Path]:
        """Return sorted schema paths under the spec pack."""
        sdir = self.dirs()["schemas"]
        if sdir.exists():
            candidates = list(sdir.rglob("*.schema.json"))
            candidates.extend(sdir.rglob("*.schema.*.json"))
        else:
            candidates = list(self.root.rglob("*.schema.json"))
        deduped = {path.resolve(): path for path in candidates}
        return sorted(deduped.values())

    def list_vectors(self) -> List[Path]:
        """Return sorted vector fixture paths (json/jsonl)."""
        vdir = self.dirs()["vectors"]
        if not vdir.exists():
            return []
        candidates: List[Path] = []
        for pattern in ("*.json", "*.jsonl"):
            candidates.extend(vdir.rglob(pattern))
        deduped = {path.resolve(): path for path in candidates}
        return sorted(deduped.values())

    def list_operators(self) -> List[Path]:
        odir = self.dirs()["operators"]
        if not odir.exists():
            return []
        return sorted(odir.rglob("op_*.json"))

    def list_service_tier_caps(self) -> List[Path]:
        """Return sorted service tier capability descriptors."""
        base = self.path("refs", "caps")
        if not base.exists():
            return []
        return sorted(base.glob("*.caps.json"))

    def load_service_tier_profile(self, tier: str) -> Dict[str, Any]:
        """Load a service tier capability profile by tier name."""
        tier_lower = tier.lower()
        for path in self.list_service_tier_caps():
            payload = self.load_json(path)
            tier_name = str(payload.get("tier", "")).lower()
            if tier_name == tier_lower:
                return payload
        raise KeyError(f"Service tier not found: {tier}")

    def load_json(self, path: Path | str):
        p = Path(path)
        with p.open("r", encoding="utf-8") as fh:
            if p.suffix == ".jsonl":
                return [json.loads(line) for line in fh if line.strip()]
            return json.load(fh)

    def ensure_schema(self, schema_name: str) -> Path:
        for path in self.list_schemas():
            if path.name == schema_name:
                return path
        raise FileNotFoundError(f"Schema not found: {schema_name}")

    def find_examples(self, *subdirs: str, pattern: str = "*.json") -> List[Path]:
        base = self.path(*subdirs)
        if not base.exists():
            return []
        return sorted(base.rglob(pattern))
