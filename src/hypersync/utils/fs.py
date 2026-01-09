
from __future__ import annotations

import os
import shutil
import tempfile
from contextlib import suppress
from importlib import resources
from pathlib import Path
from typing import Iterator


_DEFAULT_HINTS = (
    "spec_pack",
    "spec-pack",
    "spec-pack/spec-pack",
)


_PACKAGED_SPEC_ROOT: Path | None = None


def _packaged_spec_root() -> Path | None:
    global _PACKAGED_SPEC_ROOT
    if _PACKAGED_SPEC_ROOT and _PACKAGED_SPEC_ROOT.exists():
        return _PACKAGED_SPEC_ROOT
    with suppress(ModuleNotFoundError, FileNotFoundError):
        package_root = resources.files('hypersync.specpack')
        try:
            filesystem_root = Path(package_root)  # type: ignore[arg-type]
        except TypeError:
            filesystem_root = None
        if filesystem_root and filesystem_root.exists():
            _PACKAGED_SPEC_ROOT = filesystem_root
            return _PACKAGED_SPEC_ROOT
        with resources.as_file(package_root) as tmp_path:
            src = Path(tmp_path)
            if not src.exists():
                return None
            target_root = Path(tempfile.mkdtemp(prefix='hypersync_specpack_'))
            dst = target_root / 'spec-pack'
            shutil.copytree(src, dst, dirs_exist_ok=True)
            _PACKAGED_SPEC_ROOT = dst
            return _PACKAGED_SPEC_ROOT
    return None



def _normalize(path: Path | str) -> Path:
    return Path(path).expanduser()


def _iter_candidate_roots(spec_root: str | None) -> Iterator[Path]:
    seen: set[Path] = set()

    def register(candidate: Path | str | None) -> Path | None:
        if not candidate:
            return None
        path = _normalize(candidate)
        resolved = path.resolve() if path.exists() else path
        if resolved in seen:
            return None
        seen.add(resolved)
        if path.exists():
            return path.resolve()
        return None

    initial = register(spec_root)
    if initial:
        yield initial

    env_root = register(os.getenv("HYPERSYNC_SPEC_ROOT"))
    if env_root:
        yield env_root

    bases = {Path.cwd(), *Path.cwd().parents}
    for base in bases:
        for hint in _DEFAULT_HINTS:
            candidate = register(base / hint)
            if candidate:
                yield candidate
        for glob in base.glob("spec-pack.*"):
            candidate = register(glob)
            if candidate:
                yield candidate


def resolve_root(spec_root: str | None) -> Path:
    for candidate in _iter_candidate_roots(spec_root):
        return candidate
    fallback_input = spec_root or os.getenv("HYPERSYNC_SPEC_ROOT", "spec_pack")
    fallback = _normalize(fallback_input)
    if fallback.exists():
        return fallback.resolve()
    packaged = _packaged_spec_root()
    if packaged:
        return packaged.resolve()
    raise FileNotFoundError(
        "Unable to resolve spec root. Provide --spec-root or set HYPERSYNC_SPEC_ROOT."
    )


def iter_files(base: Path, exts=(".json", ".jsonl", ".md", ".yaml", ".yml")):
    for p in base.rglob("*"):
        if p.is_file() and (not exts or p.suffix in exts):
            yield p
