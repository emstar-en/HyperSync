"""
HyperSync Integration Modes & Feature Flags

Defines orchestration adoption tiers and capability profiles.
Allows runtime configuration of integration behavior.
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
import yaml
import json
from pathlib import Path


class IntegrationMode(str, Enum):
    """
    Five-tier orchestration adoption model.

    Each mode represents a different level of HyperSync integration
    with existing orchestration infrastructure.
    """

    WRAPPER = "wrapper"
    """
    Monitoring/observability only. HyperSync observes but doesn't control.
    - Capability vectors computed but not enforced
    - Placement suggestions logged but not applied
    - Token accounting advisory only
    - External orchestrator remains authoritative
    """

    BACKEND_ROUTER = "backend_router"
    """
    HyperSync provides routing/placement advice to external orchestrator.
    - Placement engine computes optimal locations
    - External orchestrator queries HyperSync for decisions
    - HyperSync doesn't directly schedule
    - Bidirectional sync of state
    """

    HYBRID = "hybrid"
    """
    Mixed control: some workloads native, some delegated.
    - HyperSync manages tagged/opted-in workloads
    - External orchestrator handles others
    - Shared resource accounting
    - Coordinated placement decisions
    """

    NATIVE = "native"
    """
    Full HyperSync orchestration control.
    - HyperSync is primary scheduler
    - Direct pod/container lifecycle management
    - Native hyperbolic placement
    - External orchestrator optional/disabled
    """

    FEATURE_EXTRACTION = "feature_extraction"
    """
    Selective feature adoption (e.g., only token cloud, only placement).
    - Operators choose specific HyperSync capabilities
    - Rest handled by external orchestrator
    - Modular integration
    """


@dataclass
class IntegrationCapabilities:
    """Capabilities enabled for an integration mode."""

    # Core capabilities
    capability_detection: bool = False
    hyperbolic_placement: bool = False
    token_accounting: bool = False
    agent_composition: bool = False

    # Control capabilities
    direct_scheduling: bool = False
    lifecycle_management: bool = False
    resource_enforcement: bool = False

    # Integration capabilities
    external_sync: bool = False
    advisory_mode: bool = False
    receipt_generation: bool = True

    # Observability
    telemetry_export: bool = True
    verbose_receipts: bool = False

    # Governance
    policy_enforcement: bool = False
    approval_gates: bool = False


@dataclass
class IntegrationProfile:
    """Complete profile for an integration mode."""

    mode: IntegrationMode
    name: str
    description: str
    capabilities: IntegrationCapabilities
    dependencies: List[str] = field(default_factory=list)
    config_overrides: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "low"  # low, medium, high

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "mode": self.mode.value,
            "name": self.name,
            "description": self.description,
            "capabilities": {
                k: v for k, v in self.capabilities.__dict__.items()
            },
            "dependencies": self.dependencies,
            "config_overrides": self.config_overrides,
            "risk_level": self.risk_level
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntegrationProfile':
        """Create from dictionary representation."""
        caps_data = data.get("capabilities", {})
        capabilities = IntegrationCapabilities(**caps_data)

        return cls(
            mode=IntegrationMode(data["mode"]),
            name=data["name"],
            description=data["description"],
            capabilities=capabilities,
            dependencies=data.get("dependencies", []),
            config_overrides=data.get("config_overrides", {}),
            risk_level=data.get("risk_level", "low")
        )


class IntegrationModeManager:
    """
    Manages integration mode configuration and transitions.

    Responsibilities:
    - Load and validate integration profiles
    - Handle mode transitions with safety checks
    - Provide capability queries
    - Emit mode change events
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("configs/integration/default_modes.yaml")
        self.profiles: Dict[IntegrationMode, IntegrationProfile] = {}
        self.current_mode: Optional[IntegrationMode] = None
        self._load_profiles()

    def _load_profiles(self):
        """Load integration profiles from configuration."""
        # Define default profiles
        self.profiles = {
            IntegrationMode.WRAPPER: IntegrationProfile(
                mode=IntegrationMode.WRAPPER,
                name="Monitoring Wrapper",
                description="Observe-only mode with no control",
                capabilities=IntegrationCapabilities(
                    capability_detection=True,
                    hyperbolic_placement=False,
                    token_accounting=True,
                    agent_composition=False,
                    direct_scheduling=False,
                    lifecycle_management=False,
                    resource_enforcement=False,
                    external_sync=True,
                    advisory_mode=True,
                    receipt_generation=True,
                    telemetry_export=True,
                    verbose_receipts=True,
                    policy_enforcement=False,
                    approval_gates=False
                ),
                dependencies=["telemetry_manager", "capability_detector"],
                risk_level="low"
            ),

            IntegrationMode.BACKEND_ROUTER: IntegrationProfile(
                mode=IntegrationMode.BACKEND_ROUTER,
                name="Backend Router",
                description="Provide placement advice to external orchestrator",
                capabilities=IntegrationCapabilities(
                    capability_detection=True,
                    hyperbolic_placement=True,
                    token_accounting=True,
                    agent_composition=False,
                    direct_scheduling=False,
                    lifecycle_management=False,
                    resource_enforcement=False,
                    external_sync=True,
                    advisory_mode=True,
                    receipt_generation=True,
                    telemetry_export=True,
                    verbose_receipts=True,
                    policy_enforcement=True,
                    approval_gates=False
                ),
                dependencies=[
                    "telemetry_manager",
                    "capability_detector",
                    "placement_engine",
                    "token_cloud"
                ],
                risk_level="low"
            ),

            IntegrationMode.HYBRID: IntegrationProfile(
                mode=IntegrationMode.HYBRID,
                name="Hybrid Control",
                description="Mixed native and delegated workload management",
                capabilities=IntegrationCapabilities(
                    capability_detection=True,
                    hyperbolic_placement=True,
                    token_accounting=True,
                    agent_composition=True,
                    direct_scheduling=True,
                    lifecycle_management=True,
                    resource_enforcement=True,
                    external_sync=True,
                    advisory_mode=False,
                    receipt_generation=True,
                    telemetry_export=True,
                    verbose_receipts=True,
                    policy_enforcement=True,
                    approval_gates=True
                ),
                dependencies=[
                    "telemetry_manager",
                    "capability_detector",
                    "placement_engine",
                    "token_cloud",
                    "orchestrator",
                    "governance_manager"
                ],
                risk_level="medium"
            ),

            IntegrationMode.NATIVE: IntegrationProfile(
                mode=IntegrationMode.NATIVE,
                name="Native Orchestration",
                description="Full HyperSync control of all workloads",
                capabilities=IntegrationCapabilities(
                    capability_detection=True,
                    hyperbolic_placement=True,
                    token_accounting=True,
                    agent_composition=True,
                    direct_scheduling=True,
                    lifecycle_management=True,
                    resource_enforcement=True,
                    external_sync=False,
                    advisory_mode=False,
                    receipt_generation=True,
                    telemetry_export=True,
                    verbose_receipts=True,
                    policy_enforcement=True,
                    approval_gates=True
                ),
                dependencies=[
                    "telemetry_manager",
                    "capability_detector",
                    "placement_engine",
                    "token_cloud",
                    "orchestrator",
                    "governance_manager",
                    "agent_system"
                ],
                risk_level="high"
            ),

            IntegrationMode.FEATURE_EXTRACTION: IntegrationProfile(
                mode=IntegrationMode.FEATURE_EXTRACTION,
                name="Feature Extraction",
                description="Selective capability adoption",
                capabilities=IntegrationCapabilities(
                    capability_detection=True,
                    hyperbolic_placement=False,  # Configurable
                    token_accounting=False,  # Configurable
                    agent_composition=False,  # Configurable
                    direct_scheduling=False,
                    lifecycle_management=False,
                    resource_enforcement=False,
                    external_sync=True,
                    advisory_mode=True,
                    receipt_generation=True,
                    telemetry_export=True,
                    verbose_receipts=False,
                    policy_enforcement=False,
                    approval_gates=False
                ),
                dependencies=["telemetry_manager"],  # Minimal
                config_overrides={
                    "features": {
                        "token_cloud": False,
                        "placement": False,
                        "agents": False
                    }
                },
                risk_level="low"
            )
        }

        # Load overrides from config file if exists
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
                self._apply_config_overrides(config)

    def _apply_config_overrides(self, config: Dict[str, Any]):
        """Apply configuration file overrides to profiles."""
        for mode_str, overrides in config.get("profiles", {}).items():
            try:
                mode = IntegrationMode(mode_str)
                if mode in self.profiles:
                    profile = self.profiles[mode]

                    # Apply capability overrides
                    if "capabilities" in overrides:
                        for cap, value in overrides["capabilities"].items():
                            if hasattr(profile.capabilities, cap):
                                setattr(profile.capabilities, cap, value)

                    # Apply other overrides
                    if "config_overrides" in overrides:
                        profile.config_overrides.update(overrides["config_overrides"])

                    if "dependencies" in overrides:
                        profile.dependencies = overrides["dependencies"]

            except (ValueError, KeyError) as e:
                print(f"Warning: Invalid mode override {mode_str}: {e}")

    def set_mode(self, mode: IntegrationMode) -> bool:
        """
        Set the current integration mode.

        Returns:
            True if mode was set successfully, False otherwise
        """
        if mode not in self.profiles:
            return False

        # TODO: Add validation checks
        # - Verify dependencies are available
        # - Check for safe transition path
        # - Emit governance event if needed

        self.current_mode = mode
        return True

    def get_mode(self) -> Optional[IntegrationMode]:
        """Get the current integration mode."""
        return self.current_mode

    def get_profile(self, mode: Optional[IntegrationMode] = None) -> Optional[IntegrationProfile]:
        """Get profile for specified mode (or current mode)."""
        target_mode = mode or self.current_mode
        return self.profiles.get(target_mode) if target_mode else None

    def list_modes(self) -> List[IntegrationProfile]:
        """List all available integration modes."""
        return list(self.profiles.values())

    def has_capability(self, capability: str) -> bool:
        """Check if current mode has specified capability."""
        profile = self.get_profile()
        if not profile:
            return False

        return getattr(profile.capabilities, capability, False)

    def get_dependencies(self) -> List[str]:
        """Get dependencies for current mode."""
        profile = self.get_profile()
        return profile.dependencies if profile else []

    def validate_transition(self, from_mode: IntegrationMode, to_mode: IntegrationMode) -> tuple[bool, str]:
        """
        Validate if transition between modes is safe.

        Returns:
            (is_valid, reason)
        """
        from_profile = self.profiles.get(from_mode)
        to_profile = self.profiles.get(to_mode)

        if not from_profile or not to_profile:
            return False, "Invalid mode"

        # Check risk level transitions
        risk_order = {"low": 0, "medium": 1, "high": 2}
        from_risk = risk_order.get(from_profile.risk_level, 0)
        to_risk = risk_order.get(to_profile.risk_level, 0)

        if to_risk > from_risk + 1:
            return False, f"Risk jump too large: {from_profile.risk_level} -> {to_profile.risk_level}"

        # Check if downgrade requires approval
        if to_risk < from_risk:
            # Downgrade - generally safe but may need approval
            pass

        return True, "Transition valid"

    def export_config(self) -> Dict[str, Any]:
        """Export current configuration."""
        return {
            "current_mode": self.current_mode.value if self.current_mode else None,
            "profiles": {
                mode.value: profile.to_dict()
                for mode, profile in self.profiles.items()
            }
        }

    def save_config(self, path: Optional[Path] = None):
        """Save configuration to file."""
        target_path = path or self.config_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, 'w') as f:
            yaml.dump(self.export_config(), f, default_flow_style=False)


# Global instance
_mode_manager: Optional[IntegrationModeManager] = None


def get_mode_manager() -> IntegrationModeManager:
    """Get global integration mode manager instance."""
    global _mode_manager
    if _mode_manager is None:
        _mode_manager = IntegrationModeManager()
    return _mode_manager


def set_integration_mode(mode: IntegrationMode) -> bool:
    """Convenience function to set integration mode."""
    return get_mode_manager().set_mode(mode)


def get_integration_mode() -> Optional[IntegrationMode]:
    """Convenience function to get current integration mode."""
    return get_mode_manager().get_mode()


def has_capability(capability: str) -> bool:
    """Convenience function to check capability."""
    return get_mode_manager().has_capability(capability)
