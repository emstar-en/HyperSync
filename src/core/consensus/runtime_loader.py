"""
Consensus Runtime Loader
Manages consensus mechanism runtime activation and lifecycle.
"""
from typing import Dict, Any, Optional, List
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConsensusRuntime:
    """Represents an active consensus mechanism runtime."""

    def __init__(self, mechanism_id: str, config: Dict[str, Any]):
        self.runtime_id = str(uuid.uuid4())
        self.mechanism_id = mechanism_id
        self.config = config
        self.activated_at = datetime.utcnow().isoformat()
        self.status = "initializing"

    def start(self):
        """Start the consensus runtime."""
        logger.info(f"Starting consensus runtime {self.runtime_id} ({self.mechanism_id})")
        # Stub: actual runtime initialization would go here
        self.status = "active"
        return True

    def stop(self):
        """Stop the consensus runtime."""
        logger.info(f"Stopping consensus runtime {self.runtime_id}")
        self.status = "stopped"
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert runtime to dictionary representation."""
        return {
            "runtime_id": self.runtime_id,
            "mechanism_id": self.mechanism_id,
            "config": self.config,
            "activated_at": self.activated_at,
            "status": self.status
        }


class RuntimeManager:
    """Manages all consensus runtimes."""

    def __init__(self):
        self._runtimes: Dict[str, ConsensusRuntime] = {}

    def activate(self, mechanism_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Activate a consensus mechanism runtime.

        Returns:
            Activation result with runtime_id
        """
        try:
            runtime = ConsensusRuntime(mechanism_id, config)
            success = runtime.start()

            if success:
                self._runtimes[runtime.runtime_id] = runtime
                logger.info(f"Activated runtime {runtime.runtime_id}")

                return {
                    "activated": True,
                    "runtime_id": runtime.runtime_id,
                    "mechanism_id": mechanism_id,
                    "status": runtime.status
                }
            else:
                return {
                    "activated": False,
                    "error": "Runtime failed to start"
                }

        except Exception as e:
            logger.error(f"Activation failed: {e}")
            return {
                "activated": False,
                "error": str(e)
            }

    def deactivate(self, runtime_id: str) -> Dict[str, Any]:
        """
        Deactivate a consensus runtime.

        Returns:
            Deactivation result
        """
        if runtime_id not in self._runtimes:
            return {
                "deactivated": False,
                "error": f"Runtime {runtime_id} not found"
            }

        try:
            runtime = self._runtimes[runtime_id]
            runtime.stop()
            del self._runtimes[runtime_id]

            logger.info(f"Deactivated runtime {runtime_id}")
            return {
                "deactivated": True,
                "runtime_id": runtime_id
            }

        except Exception as e:
            logger.error(f"Deactivation failed: {e}")
            return {
                "deactivated": False,
                "error": str(e)
            }

    def get_active(self, tier: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of active runtimes, optionally filtered by tier."""
        runtimes = []

        for runtime in self._runtimes.values():
            if tier and runtime.config.get("tier") != tier:
                continue
            runtimes.append(runtime.to_dict())

        return runtimes

    def get_runtime(self, runtime_id: str) -> Optional[ConsensusRuntime]:
        """Get a specific runtime by ID."""
        return self._runtimes.get(runtime_id)


# Global runtime manager
_manager = RuntimeManager()


def activate_mechanism(mechanism_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Activate a consensus mechanism. Convenience function."""
    return _manager.activate(mechanism_id, config)


def deactivate_mechanism(runtime_id: str) -> Dict[str, Any]:
    """Deactivate a consensus runtime. Convenience function."""
    return _manager.deactivate(runtime_id)


def get_active_runtimes(tier: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get active runtimes. Convenience function."""
    return _manager.get_active(tier=tier)


def get_runtime(runtime_id: str) -> Optional[ConsensusRuntime]:
    """Get a specific runtime. Convenience function."""
    return _manager.get_runtime(runtime_id)
