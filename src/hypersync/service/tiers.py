
from __future__ import annotations

import json
from importlib import resources
from typing import Any, Dict, Iterable, List, Mapping, Optional

from pydantic import BaseModel, ConfigDict, Field

from ..spec_loader import SpecLoader


class ServiceTierProfile(BaseModel):
    """Canonical representation of a service tier specification."""

    tier: str
    max_dim: Optional[int | str] = None
    node_limit: Optional[int | str] = None
    orchestrators: List[str] = Field(default_factory=list)
    consensus: List[str] = Field(default_factory=list)
    db_adapters: List[str] = Field(default_factory=list)
    integrations: Dict[str, List[str]] = Field(default_factory=dict)
    features: Dict[str, Any] = Field(default_factory=dict)
    license: Dict[str, Any] = Field(default_factory=dict)
    source_path: Optional[str] = Field(default=None, exclude=True)

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any], *, source_path: Optional[str] = None) -> "ServiceTierProfile":
        profile = cls.model_validate(payload)
        profile.source_path = source_path
        return profile

    def summary(self) -> Dict[str, Any]:
        return {
            "tier": self.tier,
            "max_dim": self.max_dim,
            "node_limit": self.node_limit,
            "orchestrators": self.orchestrators,
            "db_adapters": self.db_adapters,
            "features": self.features,
        }

    def model_dump_with_source(self) -> Dict[str, Any]:
        data = self.model_dump(mode="json", by_alias=True, exclude_none=True)
        if self.source_path:
            data["_source_path"] = self.source_path
        if self.model_extra:
            data["_extra"] = self.model_extra
        return data


class ServiceTierRegistry:
    """Helper for discovering and loading tier specifications from the spec pack."""

    def __init__(self, loader: SpecLoader | str | None = None, *, allow_fallback: bool = True):
        self.loader: SpecLoader | None
        if isinstance(loader, SpecLoader):
            self.loader = loader
        else:
            try:
                self.loader = SpecLoader(loader)
            except FileNotFoundError:
                if allow_fallback:
                    self.loader = None
                else:
                    raise
        self._profiles: Dict[str, ServiceTierProfile] = {}
        self._load_profiles()
        if not self._profiles and allow_fallback:
            self._load_builtin_profiles()

    def _load_profiles(self) -> None:
        if not self.loader:
            return
        for path in self.loader.list_service_tier_caps():
            payload = self.loader.load_json(path)
            tier_name = str(payload.get("tier", "")).lower()
            if not tier_name:
                continue
            profile = ServiceTierProfile.from_payload(payload, source_path=str(path))
            self._profiles[tier_name] = profile

    def _load_builtin_profiles(self) -> None:
        try:
            data_path = resources.files('hypersync.service.data').joinpath('all_tiers.json')
        except (FileNotFoundError, ModuleNotFoundError):
            return
        if not data_path.is_file():
            return
        payloads = json.loads(data_path.read_text())
        for tier_name, payload in payloads.items():
            profile = ServiceTierProfile.from_payload(payload, source_path=str(data_path))
            self._profiles[tier_name] = profile

    def tiers(self) -> List[str]:
        return sorted(self._profiles.keys())

    def get(self, tier: str) -> ServiceTierProfile:
        key = tier.lower()
        if key not in self._profiles:
            raise KeyError(f"Unknown service tier: {tier}")
        return self._profiles[key]

    def summary(self) -> Dict[str, Dict[str, Any]]:
        return {name: profile.summary() for name, profile in self._profiles.items()}

    def as_dict(self, tier: str) -> Dict[str, Any]:
        return self.get(tier).model_dump_with_source()

    def __iter__(self) -> Iterable[ServiceTierProfile]:
        return iter(self._profiles.values())
