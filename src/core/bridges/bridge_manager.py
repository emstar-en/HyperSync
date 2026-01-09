"""
Bridge Manager - Manages all orchestrator bridges
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

from hypersync.bridges.base_bridge import (
    OrchestratorBridge,
    BridgeConfig,
    BridgeType,
    BridgeStatus
)
from hypersync.bridges.adapters.k8s_bridge import KubernetesBridge
from hypersync.bridges.adapters.nomad_bridge import NomadBridge
from hypersync.bridges.adapters.airflow_bridge import AirflowBridge


class BridgeManager:
    """
    Manages all orchestrator bridges.

    Responsibilities:
    - Load bridge configurations
    - Initialize and manage bridge connections
    - Route requests to appropriate bridges
    - Aggregate receipts and telemetry
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("configs/bridges")
        self.bridges: Dict[str, OrchestratorBridge] = {}
        self._load_bridges()

    def _load_bridges(self):
        """Load bridge configurations."""
        if not self.config_path.exists():
            return

        for config_file in self.config_path.glob("*.yaml"):
            try:
                with open(config_file) as f:
                    config_data = yaml.safe_load(f)
                    self._initialize_bridge(config_data)
            except Exception as e:
                print(f"Error loading bridge config {config_file}: {e}")

    def _initialize_bridge(self, config_data: Dict[str, Any]):
        """Initialize bridge from configuration."""
        bridge_type = BridgeType(config_data["type"])
        config = BridgeConfig(
            bridge_type=bridge_type,
            name=config_data["name"],
            endpoint=config_data["endpoint"],
            credentials=config_data.get("credentials", {}),
            options=config_data.get("options", {}),
            enabled=config_data.get("enabled", True)
        )

        if not config.enabled:
            return

        # Create appropriate bridge
        if bridge_type == BridgeType.KUBERNETES:
            bridge = KubernetesBridge(config)
        elif bridge_type == BridgeType.NOMAD:
            bridge = NomadBridge(config)
        elif bridge_type == BridgeType.AIRFLOW:
            bridge = AirflowBridge(config)
        else:
            print(f"Unknown bridge type: {bridge_type}")
            return

        self.bridges[config.name] = bridge

    def add_bridge(self, name: str, bridge: OrchestratorBridge):
        """Add a bridge manually."""
        self.bridges[name] = bridge

    def get_bridge(self, name: str) -> Optional[OrchestratorBridge]:
        """Get bridge by name."""
        return self.bridges.get(name)

    def list_bridges(self) -> List[str]:
        """List all bridge names."""
        return list(self.bridges.keys())

    def connect_all(self) -> Dict[str, bool]:
        """Connect all bridges."""
        results = {}
        for name, bridge in self.bridges.items():
            results[name] = bridge.connect()
        return results

    def disconnect_all(self) -> Dict[str, bool]:
        """Disconnect all bridges."""
        results = {}
        for name, bridge in self.bridges.items():
            results[name] = bridge.disconnect()
        return results

    def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Health check all bridges."""
        results = {}
        for name, bridge in self.bridges.items():
            results[name] = bridge.health_check()
        return results

    def get_all_workloads(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get workloads from all bridges."""
        results = {}
        for name, bridge in self.bridges.items():
            if bridge.status == BridgeStatus.CONNECTED:
                results[name] = bridge.get_workloads()
        return results

    def get_all_receipts(self) -> Dict[str, List]:
        """Get receipts from all bridges."""
        results = {}
        for name, bridge in self.bridges.items():
            results[name] = [r.to_dict() for r in bridge.get_receipts()]
        return results


# Global instance
_bridge_manager: Optional[BridgeManager] = None


def get_bridge_manager() -> BridgeManager:
    """Get global bridge manager instance."""
    global _bridge_manager
    if _bridge_manager is None:
        _bridge_manager = BridgeManager()
    return _bridge_manager
