
import json
from pathlib import Path

import pytest

from hypersync.service import ServiceTierRegistry


def test_service_tier_registry_fallback(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv('HYPERSYNC_SPEC_ROOT', raising=False)
    registry = ServiceTierRegistry(None, allow_fallback=True)
    tiers = registry.tiers()
    assert 'advanced' in tiers
    profile = registry.get('advanced')
    assert profile.features.get('diff_snapshots') is True


def test_service_tier_registry_custom_spec(tmp_path):
    spec_root = tmp_path / 'spec_pack_custom'
    caps_dir = spec_root / 'refs' / 'caps'
    caps_dir.mkdir(parents=True)
    payload = {
        'tier': 'Custom',
        'max_dim': 8,
        'node_limit': 2,
        'db_adapters': ['sqlite'],
        'orchestrators': ['local'],
        'features': {'diff_snapshots': False},
    }
    (caps_dir / 'custom.caps.json').write_text(json.dumps(payload))
    registry = ServiceTierRegistry(str(spec_root), allow_fallback=False)
    assert registry.tiers() == ['custom']
    custom = registry.get('custom')
    assert custom.tier == 'Custom'
    assert custom.max_dim == 8


def test_service_tier_registry_missing_tier_error(tmp_path):
    spec_root = tmp_path / 'spec_pack_empty'
    (spec_root / 'refs' / 'caps').mkdir(parents=True)
    registry = ServiceTierRegistry(str(spec_root), allow_fallback=True)
    with pytest.raises(KeyError):
        registry.get('nonexistent')
