"""
Control Manifest Manager

Manages operator control manifests with CRUD operations,
schema validation, and governance integration.
"""

import json
import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
import jsonschema


class ManifestPhase(str, Enum):
    """Control manifest lifecycle phases."""
    PENDING = "pending"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Intent(str, Enum):
    """Operator intents."""
    DEPLOY = "deploy"
    SCALE = "scale"
    MIGRATE = "migrate"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class ManifestMetadata:
    """Manifest metadata."""
    name: str
    namespace: str = "default"
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class PlacementSpec:
    """Placement specification."""
    strategy: str = "hyperbolic"
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    preferences: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ResourceSpec:
    """Resource requirements."""
    requests: Dict[str, Any] = field(default_factory=dict)
    limits: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicySpec:
    """Policy overrides."""
    governance: Dict[str, Any] = field(default_factory=dict)
    budget: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchedulingSpec:
    """Scheduling parameters."""
    priority: int = 50
    preemptible: bool = False
    deadline: Optional[datetime] = None


@dataclass
class ControlManifestSpec:
    """Control manifest specification."""
    intent: Intent
    target: Dict[str, Any] = field(default_factory=dict)
    placement: Optional[PlacementSpec] = None
    resources: Optional[ResourceSpec] = None
    policy: Optional[PolicySpec] = None
    scheduling: Optional[SchedulingSpec] = None


@dataclass
class ManifestStatus:
    """Manifest status."""
    phase: ManifestPhase = ManifestPhase.PENDING
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    placement: Optional[Dict[str, Any]] = None
    receipt: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


@dataclass
class ControlManifest:
    """Complete control manifest."""
    api_version: str = "control.hypersync.io/v1"
    kind: str = "ControlManifest"
    metadata: ManifestMetadata = field(default_factory=ManifestMetadata)
    spec: ControlManifestSpec = field(default_factory=ControlManifestSpec)
    status: ManifestStatus = field(default_factory=ManifestStatus)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        def convert_value(v):
            if isinstance(v, datetime):
                return v.isoformat()
            elif isinstance(v, Enum):
                return v.value
            elif hasattr(v, '__dict__'):
                return {k: convert_value(val) for k, val in v.__dict__.items()}
            elif isinstance(v, list):
                return [convert_value(item) for item in v]
            elif isinstance(v, dict):
                return {k: convert_value(val) for k, val in v.items()}
            return v

        return {
            "apiVersion": self.api_version,
            "kind": self.kind,
            "metadata": convert_value(self.metadata),
            "spec": convert_value(self.spec),
            "status": convert_value(self.status)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ControlManifest':
        """Create from dictionary."""
        # Parse metadata
        meta_data = data.get("metadata", {})
        metadata = ManifestMetadata(
            name=meta_data["name"],
            namespace=meta_data.get("namespace", "default"),
            labels=meta_data.get("labels", {}),
            annotations=meta_data.get("annotations", {})
        )

        # Parse spec
        spec_data = data.get("spec", {})

        placement = None
        if "placement" in spec_data:
            placement = PlacementSpec(**spec_data["placement"])

        resources = None
        if "resources" in spec_data:
            resources = ResourceSpec(**spec_data["resources"])

        policy = None
        if "policy" in spec_data:
            policy = PolicySpec(**spec_data["policy"])

        scheduling = None
        if "scheduling" in spec_data:
            scheduling = SchedulingSpec(**spec_data["scheduling"])

        spec = ControlManifestSpec(
            intent=Intent(spec_data["intent"]),
            target=spec_data.get("target", {}),
            placement=placement,
            resources=resources,
            policy=policy,
            scheduling=scheduling
        )

        # Parse status
        status_data = data.get("status", {})
        status = ManifestStatus(
            phase=ManifestPhase(status_data.get("phase", "pending")),
            conditions=status_data.get("conditions", []),
            placement=status_data.get("placement"),
            receipt=status_data.get("receipt"),
            message=status_data.get("message")
        )

        return cls(
            api_version=data.get("apiVersion", "control.hypersync.io/v1"),
            kind=data.get("kind", "ControlManifest"),
            metadata=metadata,
            spec=spec,
            status=status
        )


class ControlManifestManager:
    """
    Manages control manifests with CRUD operations.

    Responsibilities:
    - Create, read, update, delete manifests
    - Schema validation
    - Governance integration
    - Telemetry emission
    - Status tracking
    """

    def __init__(self, 
                 storage_path: Optional[Path] = None,
                 schema_path: Optional[Path] = None,
                 governance_manager=None,
                 telemetry_manager=None):
        self.storage_path = storage_path or Path("data/manifests")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.schema_path = schema_path
        self.schema = self._load_schema() if schema_path else None

        self.governance_manager = governance_manager
        self.telemetry_manager = telemetry_manager

        self.manifests: Dict[str, ControlManifest] = {}
        self._load_manifests()

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """Load JSON schema for validation."""
        if not self.schema_path or not self.schema_path.exists():
            return None

        with open(self.schema_path) as f:
            return json.load(f)

    def _load_manifests(self):
        """Load existing manifests from storage."""
        if not self.storage_path.exists():
            return

        for manifest_file in self.storage_path.glob("*.yaml"):
            try:
                with open(manifest_file) as f:
                    data = yaml.safe_load(f)
                    manifest = ControlManifest.from_dict(data)
                    key = f"{manifest.metadata.namespace}/{manifest.metadata.name}"
                    self.manifests[key] = manifest
            except Exception as e:
                print(f"Warning: Failed to load manifest {manifest_file}: {e}")

    def validate(self, manifest_dict: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate manifest against schema.

        Returns:
            (is_valid, error_message)
        """
        if not self.schema:
            return True, None

        try:
            jsonschema.validate(instance=manifest_dict, schema=self.schema)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)

    def create(self, manifest: ControlManifest) -> tuple[bool, Optional[str]]:
        """
        Create a new control manifest.

        Returns:
            (success, error_message)
        """
        key = f"{manifest.metadata.namespace}/{manifest.metadata.name}"

        # Check if exists
        if key in self.manifests:
            return False, f"Manifest {key} already exists"

        # Validate
        manifest_dict = manifest.to_dict()
        is_valid, error = self.validate(manifest_dict)
        if not is_valid:
            return False, f"Validation failed: {error}"

        # Set timestamps
        manifest.metadata.created_at = datetime.utcnow()
        manifest.metadata.updated_at = datetime.utcnow()

        # Check governance if required
        if manifest.spec.policy and manifest.spec.policy.governance.get("require_approval"):
            manifest.status.phase = ManifestPhase.PENDING
            if self.governance_manager:
                # Submit for approval
                self._submit_for_approval(manifest)
        else:
            manifest.status.phase = ManifestPhase.APPROVED

        # Store
        self.manifests[key] = manifest
        self._save_manifest(manifest)

        # Emit telemetry
        if self.telemetry_manager:
            self._emit_telemetry("manifest_created", manifest)

        return True, None

    def get(self, name: str, namespace: str = "default") -> Optional[ControlManifest]:
        """Get manifest by name and namespace."""
        key = f"{namespace}/{name}"
        return self.manifests.get(key)

    def list(self, namespace: Optional[str] = None, 
             labels: Optional[Dict[str, str]] = None) -> List[ControlManifest]:
        """List manifests with optional filtering."""
        results = []

        for manifest in self.manifests.values():
            # Filter by namespace
            if namespace and manifest.metadata.namespace != namespace:
                continue

            # Filter by labels
            if labels:
                manifest_labels = manifest.metadata.labels
                if not all(manifest_labels.get(k) == v for k, v in labels.items()):
                    continue

            results.append(manifest)

        return results

    def update(self, manifest: ControlManifest) -> tuple[bool, Optional[str]]:
        """Update existing manifest."""
        key = f"{manifest.metadata.namespace}/{manifest.metadata.name}"

        # Check if exists
        if key not in self.manifests:
            return False, f"Manifest {key} not found"

        # Validate
        manifest_dict = manifest.to_dict()
        is_valid, error = self.validate(manifest_dict)
        if not is_valid:
            return False, f"Validation failed: {error}"

        # Update timestamp
        manifest.metadata.updated_at = datetime.utcnow()

        # Store
        self.manifests[key] = manifest
        self._save_manifest(manifest)

        # Emit telemetry
        if self.telemetry_manager:
            self._emit_telemetry("manifest_updated", manifest)

        return True, None

    def delete(self, name: str, namespace: str = "default") -> tuple[bool, Optional[str]]:
        """Delete manifest."""
        key = f"{namespace}/{name}"

        if key not in self.manifests:
            return False, f"Manifest {key} not found"

        manifest = self.manifests[key]

        # Remove from memory
        del self.manifests[key]

        # Remove from storage
        manifest_file = self.storage_path / f"{namespace}_{name}.yaml"
        if manifest_file.exists():
            manifest_file.unlink()

        # Emit telemetry
        if self.telemetry_manager:
            self._emit_telemetry("manifest_deleted", manifest)

        return True, None

    def update_status(self, name: str, namespace: str, 
                     phase: ManifestPhase, 
                     message: Optional[str] = None,
                     placement: Optional[Dict[str, Any]] = None,
                     receipt: Optional[Dict[str, Any]] = None) -> bool:
        """Update manifest status."""
        manifest = self.get(name, namespace)
        if not manifest:
            return False

        manifest.status.phase = phase
        if message:
            manifest.status.message = message
        if placement:
            manifest.status.placement = placement
        if receipt:
            manifest.status.receipt = receipt

        # Add condition
        condition = {
            "type": phase.value,
            "status": "True",
            "lastTransitionTime": datetime.utcnow().isoformat(),
            "message": message or f"Transitioned to {phase.value}"
        }
        manifest.status.conditions.append(condition)

        self._save_manifest(manifest)

        # Emit telemetry
        if self.telemetry_manager:
            self._emit_telemetry("manifest_status_updated", manifest)

        return True

    def _save_manifest(self, manifest: ControlManifest):
        """Save manifest to storage."""
        filename = f"{manifest.metadata.namespace}_{manifest.metadata.name}.yaml"
        filepath = self.storage_path / filename

        with open(filepath, 'w') as f:
            yaml.dump(manifest.to_dict(), f, default_flow_style=False)

    def _submit_for_approval(self, manifest: ControlManifest):
        """Submit manifest for governance approval."""
        if not self.governance_manager:
            return

        # Create governance change request
        change_request = {
            "type": "CONTROL_MANIFEST_UPDATE",
            "resource": f"{manifest.metadata.namespace}/{manifest.metadata.name}",
            "intent": manifest.spec.intent.value,
            "approvers": manifest.spec.policy.governance.get("approvers", []),
            "timeout": manifest.spec.policy.governance.get("timeout", 3600)
        }

        # Submit to governance manager
        # self.governance_manager.submit_change(change_request)

    def _emit_telemetry(self, event_type: str, manifest: ControlManifest):
        """Emit telemetry event."""
        if not self.telemetry_manager:
            return

        event = {
            "type": event_type,
            "manifest": f"{manifest.metadata.namespace}/{manifest.metadata.name}",
            "intent": manifest.spec.intent.value,
            "phase": manifest.status.phase.value,
            "timestamp": datetime.utcnow().isoformat()
        }

        # self.telemetry_manager.emit(event)


# Global instance
_manifest_manager: Optional[ControlManifestManager] = None


def get_manifest_manager() -> ControlManifestManager:
    """Get global manifest manager instance."""
    global _manifest_manager
    if _manifest_manager is None:
        _manifest_manager = ControlManifestManager()
    return _manifest_manager
