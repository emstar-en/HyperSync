"""Compatibility Layer

Provides native API compatibility for HyperSync deployments.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CompatibilityRegistry:
    """
    Registry mapping HyperSync deployments to native representations.

    Mode 6: Native with Compatibility Layer
    """

    def __init__(self, orchestrator: str):
        self.orchestrator = orchestrator
        self.registry: Dict[str, Dict[str, Any]] = {}

    def register(self, hypersync_id: str, native_view: Dict[str, Any]):
        """
        Register HyperSync deployment with native view.

        Args:
            hypersync_id: HyperSync node ID
            native_view: Native orchestrator representation
        """
        self.registry[hypersync_id] = native_view
        logger.info(f"Registered {hypersync_id} in compatibility layer")

    def get_native_view(self, hypersync_id: str) -> Optional[Dict[str, Any]]:
        """Get native view of HyperSync deployment"""
        return self.registry.get(hypersync_id)

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """List all registered deployments"""
        return self.registry.copy()


class CompatibilityLayer:
    """
    Provides full API compatibility with native orchestrators.

    Translates native API calls to HyperSync operations.
    """

    def __init__(self, native_mode: str, emulate: List[str]):
        """
        Initialize compatibility layer.

        Args:
            native_mode: Native orchestrator mode (hypersync)
            emulate: List of orchestrators to emulate (kubernetes, docker-swarm, etc.)
        """
        self.native_mode = native_mode
        self.emulate = emulate
        self.api_servers = {}

    def start_k8s_api_server(self, port: int = 6443):
        """Start Kubernetes API server emulation"""
        logger.info(f"Starting Kubernetes API server on port {port}")

        from hypersync.integration.compatibility.k8s_api import K8sAPIServer
        server = K8sAPIServer(port)
        server.start()

        self.api_servers['kubernetes'] = server

    def start_swarm_api_server(self, port: int = 2375):
        """Start Docker Swarm API server emulation"""
        logger.info(f"Starting Docker Swarm API server on port {port}")

        from hypersync.integration.compatibility.swarm_api import SwarmAPIServer
        server = SwarmAPIServer(port)
        server.start()

        self.api_servers['docker-swarm'] = server

    def stop_all(self):
        """Stop all API servers"""
        for name, server in self.api_servers.items():
            logger.info(f"Stopping {name} API server")
            server.stop()
