
from pathlib import Path

from hypersync.utils.fs import resolve_root


def test_resolve_root_packaged_fallback(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv('HYPERSYNC_SPEC_ROOT', raising=False)
    root = resolve_root(None)
    assert (root / 'spec-pack').exists()
    assert (root / 'refs').exists() or (root / 'spec-pack' / 'refs').exists()
