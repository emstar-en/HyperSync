# HyperSync Agent-Database Integration
# Enables agents to use database for knowledge storage and retrieval

from typing import Dict, Any, Optional, List
import asyncio
from dataclasses import dataclass

from hypersync.wiring.database_integration import DatabaseIntegrationWiring
from hypersync.agents.runtime import AgentRuntime
from hypersync.agents.composition import AgentCompositionEngine
from hypersync.agents.knowledge import KnowledgeBase


@dataclass
class AgentDatabaseConfig:
    enable_autonomous_queries: bool = True
    enable_knowledge_sync: bool = True
    enable_vector_search: bool = True
    sync_interval: float = 5.0
    cache_agent_queries: bool = True


class AgentDatabaseWiring:
    def __init__(
        self,
        database: DatabaseIntegrationWiring,
        agent_runtime: AgentRuntime,
        composition_engine: AgentCompositionEngine,
        config: AgentDatabaseConfig
    ):
        self.database = database
        self.agent_runtime = agent_runtime
        self.composition_engine = composition_engine
        self.config = config
        self.initialized = False
        self.knowledge_bases = {}

    async def initialize(self):
        print("Initializing agent-database integration...")

        # Wire agent runtime to database
        await self._wire_agent_runtime()

        # Wire composition engine to database
        await self._wire_composition_engine()

        # Setup knowledge sync
        if self.config.enable_knowledge_sync:
            await self._setup_knowledge_sync()

        # Enable autonomous queries
        if self.config.enable_autonomous_queries:
            await self._enable_autonomous_queries()

        self.initialized = True
        print("✓ Agent-database integration complete")

    async def _wire_agent_runtime(self):
        '''Wire agent runtime to use database for state persistence'''

        # Register database as agent state backend
        self.agent_runtime.register_state_backend(
            name='hyperbolic_db',
            backend=self.database.components['database']['database']
        )

        # Enable vector search for agent queries
        if self.config.enable_vector_search:
            self.agent_runtime.enable_vector_search(
                index=self.database.components['database']['index']
            )

    async def _wire_composition_engine(self):
        '''Wire composition engine to use database for agent coordination'''

        # Register database for agent composition state
        self.composition_engine.set_coordination_backend(
            self.database.components['database']['database']
        )

        # Use hyperbolic space for agent placement
        self.composition_engine.set_hyperbolic_space(
            self.database.components['database']['space']
        )

    async def _setup_knowledge_sync(self):
        '''Setup automatic knowledge synchronization'''

        # Start knowledge sync manager
        sync_manager = self.database.components['agent_bridge']['knowledge_sync']

        # Configure sync for all agents
        for agent_id in self.agent_runtime.get_agent_ids():
            await sync_manager.register_agent(
                agent_id=agent_id,
                sync_interval=self.config.sync_interval
            )

    async def _enable_autonomous_queries(self):
        '''Enable agents to perform autonomous database queries'''

        # Get autonomous query engine
        autonomous_query = self.database.components['agent_bridge']['autonomous_query']

        # Register with agent runtime
        self.agent_runtime.register_tool(
            name='database_query',
            handler=autonomous_query.execute_query
        )

        self.agent_runtime.register_tool(
            name='database_store',
            handler=autonomous_query.store_data
        )

    async def create_agent_knowledge_base(
        self,
        agent_id: str,
        namespace: Optional[str] = None
    ) -> KnowledgeBase:
        '''Create a knowledge base for an agent'''

        if not self.initialized:
            raise RuntimeError("Integration not initialized")

        # Create knowledge base backed by database
        kb = KnowledgeBase(
            agent_id=agent_id,
            namespace=namespace or f"agent_{agent_id}",
            database=self.database.components['database']['database'],
            vector_index=self.database.components['database']['index']
        )

        await kb.initialize()

        self.knowledge_bases[agent_id] = kb

        return kb

    async def agent_query(
        self,
        agent_id: str,
        query: str,
        context: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        '''Execute a query on behalf of an agent'''

        if not self.initialized:
            raise RuntimeError("Integration not initialized")

        # Get or create knowledge base
        if agent_id not in self.knowledge_bases:
            await self.create_agent_knowledge_base(agent_id)

        kb = self.knowledge_bases[agent_id]

        # Execute query with agent context
        results = await kb.query(query, context=context)

        # Cache if enabled
        if self.config.cache_agent_queries:
            await self._cache_query_result(agent_id, query, results)

        return results

    async def agent_store(
        self,
        agent_id: str,
        data: Any,
        metadata: Optional[Dict] = None
    ) -> str:
        '''Store data on behalf of an agent'''

        if not self.initialized:
            raise RuntimeError("Integration not initialized")

        # Get or create knowledge base
        if agent_id not in self.knowledge_bases:
            await self.create_agent_knowledge_base(agent_id)

        kb = self.knowledge_bases[agent_id]

        # Add agent metadata
        full_metadata = metadata or {}
        full_metadata['agent_id'] = agent_id
        full_metadata['timestamp'] = asyncio.get_event_loop().time()

        # Store in knowledge base
        data_id = await kb.store(data, metadata=full_metadata)

        return data_id

    async def sync_agent_knowledge(self, agent_id: str):
        '''Manually trigger knowledge sync for an agent'''

        if not self.initialized:
            raise RuntimeError("Integration not initialized")

        sync_manager = self.database.components['agent_bridge']['knowledge_sync']
        await sync_manager.sync_agent(agent_id)

    async def _cache_query_result(
        self,
        agent_id: str,
        query: str,
        results: List[Dict[str, Any]]
    ):
        '''Cache query results for faster retrieval'''

        cache_key = f"query_cache:{agent_id}:{hash(query)}"

        await self.database.store(
            {'query': query, 'results': results},
            metadata={'type': 'query_cache', 'agent_id': agent_id}
        )


async def create_agent_database_integration(
    database: DatabaseIntegrationWiring,
    agent_runtime: AgentRuntime,
    composition_engine: AgentCompositionEngine,
    **kwargs
) -> AgentDatabaseWiring:
    config = AgentDatabaseConfig(**kwargs)
    wiring = AgentDatabaseWiring(
        database=database,
        agent_runtime=agent_runtime,
        composition_engine=composition_engine,
        config=config
    )
    await wiring.initialize()
    return wiring


__all__ = [
    'AgentDatabaseWiring',
    'AgentDatabaseConfig',
    'create_agent_database_integration'
]
