# HyperSync Main Integration Coordinator
# Central coordination point for all database integrations

from typing import Dict, Any, Optional
import asyncio
from dataclasses import dataclass

from hypersync.wiring.database_integration import (
    DatabaseIntegrationWiring,
    DatabaseIntegrationMode,
    create_database_integration
)
from hypersync.wiring.orchestrator_integration import (
    OrchestratorDatabaseWiring,
    create_orchestrator_database_integration
)
from hypersync.wiring.agent_database_integration import (
    AgentDatabaseWiring,
    create_agent_database_integration
)

# Import core components
from hypersync.orchestrator.placement_engine import PlacementEngine
from hypersync.orchestrator.scheduler import CurvatureScheduler
from hypersync.orchestrator.service_mesh import GeodesicServiceMesh
from hypersync.agents.runtime import AgentRuntime
from hypersync.agents.composition import AgentCompositionEngine


@dataclass
class HyperSyncIntegrationConfig:
    database_mode: DatabaseIntegrationMode = DatabaseIntegrationMode.HYBRID
    enable_federation: bool = True
    enable_gpu: bool = False
    enable_quantum: bool = False
    enable_edge: bool = True
    enable_orchestrator: bool = True
    enable_agents: bool = True
    replication_factor: int = 3


class HyperSyncIntegrationCoordinator:
    def __init__(self, config: HyperSyncIntegrationConfig):
        self.config = config
        self.database = None
        self.orchestrator_integration = None
        self.agent_integration = None
        self.initialized = False

    async def initialize(self):
        print("=" * 60)
        print("HyperSync Integration Coordinator")
        print("=" * 60)

        # 1. Initialize database layer
        print("\n[1/4] Initializing database layer...")
        self.database = await create_database_integration(
            mode=self.config.database_mode,
            enable_federation=self.config.enable_federation,
            enable_gpu_acceleration=self.config.enable_gpu,
            enable_quantum_bridge=self.config.enable_quantum,
            enable_edge_optimization=self.config.enable_edge,
            replication_factor=self.config.replication_factor
        )
        print("✓ Database layer initialized")

        # 2. Initialize orchestrator integration
        if self.config.enable_orchestrator:
            print("\n[2/4] Initializing orchestrator integration...")

            # Create orchestrator components
            placement_engine = PlacementEngine()
            scheduler = CurvatureScheduler()
            service_mesh = GeodesicServiceMesh()

            await placement_engine.initialize()
            await scheduler.initialize()
            await service_mesh.initialize()

            # Wire to database
            self.orchestrator_integration = await create_orchestrator_database_integration(
                database=self.database,
                placement_engine=placement_engine,
                scheduler=scheduler,
                service_mesh=service_mesh
            )
            print("✓ Orchestrator integration initialized")
        else:
            print("\n[2/4] Orchestrator integration disabled")

        # 3. Initialize agent integration
        if self.config.enable_agents:
            print("\n[3/4] Initializing agent integration...")

            # Create agent components
            agent_runtime = AgentRuntime()
            composition_engine = AgentCompositionEngine()

            await agent_runtime.initialize()
            await composition_engine.initialize()

            # Wire to database
            self.agent_integration = await create_agent_database_integration(
                database=self.database,
                agent_runtime=agent_runtime,
                composition_engine=composition_engine
            )
            print("✓ Agent integration initialized")
        else:
            print("\n[3/4] Agent integration disabled")

        # 4. Finalize integration
        print("\n[4/4] Finalizing integration...")
        await self._finalize_integration()

        self.initialized = True

        print("\n" + "=" * 60)
        print("✓ HyperSync Integration Complete")
        print("=" * 60)
        self._print_status()

    async def _finalize_integration(self):
        '''Finalize cross-component integration'''

        # Wire orchestrator to agents if both enabled
        if self.orchestrator_integration and self.agent_integration:
            # Enable agent placement through orchestrator
            self.agent_integration.agent_runtime.set_placement_engine(
                self.orchestrator_integration.placement_engine
            )

            # Enable agent scheduling through orchestrator
            self.agent_integration.agent_runtime.set_scheduler(
                self.orchestrator_integration.scheduler
            )

    def _print_status(self):
        '''Print integration status'''
        print("\nIntegration Status:")
        print(f"  Database: ✓ {self.config.database_mode.value}")
        print(f"  Federation: {'✓ enabled' if self.config.enable_federation else '✗ disabled'}")
        print(f"  GPU Acceleration: {'✓ enabled' if self.config.enable_gpu else '✗ disabled'}")
        print(f"  Quantum Bridge: {'✓ enabled' if self.config.enable_quantum else '✗ disabled'}")
        print(f"  Edge Optimization: {'✓ enabled' if self.config.enable_edge else '✗ disabled'}")
        print(f"  Orchestrator: {'✓ enabled' if self.orchestrator_integration else '✗ disabled'}")
        print(f"  Agents: {'✓ enabled' if self.agent_integration else '✗ disabled'}")
        print(f"  Replication Factor: {self.config.replication_factor}")

    async def query(self, query: str, **kwargs) -> Any:
        '''Execute query through integrated system'''
        if not self.initialized:
            raise RuntimeError("Integration not initialized")

        return await self.database.query(query, **kwargs)

    async def store(self, data: Any, metadata: Optional[Dict] = None) -> str:
        '''Store data through integrated system'''
        if not self.initialized:
            raise RuntimeError("Integration not initialized")

        return await self.database.store(data, metadata=metadata)

    async def agent_query(self, agent_id: str, query: str, **kwargs):
        '''Execute agent query'''
        if not self.initialized or not self.agent_integration:
            raise RuntimeError("Agent integration not available")

        return await self.agent_integration.agent_query(agent_id, query, **kwargs)

    async def agent_store(self, agent_id: str, data: Any, metadata: Optional[Dict] = None):
        '''Store data for agent'''
        if not self.initialized or not self.agent_integration:
            raise RuntimeError("Agent integration not available")

        return await self.agent_integration.agent_store(agent_id, data, metadata)

    async def place_data(self, data_id: str, constraints: Optional[Dict] = None):
        '''Place data using orchestrator'''
        if not self.initialized or not self.orchestrator_integration:
            raise RuntimeError("Orchestrator integration not available")

        return await self.orchestrator_integration.place_data(data_id, constraints)

    async def shutdown(self):
        '''Shutdown all integrations'''
        print("\nShutting down HyperSync integration...")

        if self.agent_integration:
            # Agent integration shutdown handled by database
            pass

        if self.orchestrator_integration:
            # Orchestrator integration shutdown handled by database
            pass

        if self.database:
            await self.database.shutdown()

        print("✓ Shutdown complete")


async def create_hypersync_integration(
    mode: DatabaseIntegrationMode = DatabaseIntegrationMode.HYBRID,
    **kwargs
) -> HyperSyncIntegrationCoordinator:
    config = HyperSyncIntegrationConfig(database_mode=mode, **kwargs)
    coordinator = HyperSyncIntegrationCoordinator(config)
    await coordinator.initialize()
    return coordinator


__all__ = [
    'HyperSyncIntegrationCoordinator',
    'HyperSyncIntegrationConfig',
    'create_hypersync_integration'
]



# Patch 070: NVM Preset Knowledge Integration
from wiring.nvm_preset_knowledge_integration import (
    initialize_preset_knowledge,
    get_operations_assistant
)
from wiring.cli_commands.ops_commands import register_ops_commands
from wiring.initialization.bootstrap_integration import run_bootstrap_sequence

# Register in coordinator
PATCH_070_ENABLED = True
