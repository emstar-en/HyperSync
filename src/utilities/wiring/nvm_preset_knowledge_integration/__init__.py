"""
HyperSync NVM Preset Knowledge Integration
Wires Patch 070 into the core system
"""

from hypersync.nvm.preset_knowledge import (
    PresetKnowledgeLoader,
    OperationsAssistant
)
from hypersync.nvm.core import create_hypersync_integration
from hypersync.nvm.embeddings import EmbeddingGenerator


async def initialize_preset_knowledge():
    """
    Initialize preset knowledge system.

    Called during system bootstrap to load operational intelligence
    into NVM for zero-shot operations.
    """
    nvm = await create_hypersync_integration()
    embedder = EmbeddingGenerator()
    loader = PresetKnowledgeLoader(nvm, embedder)

    result = await loader.load_operations_system()
    return result


async def get_operations_assistant():
    """
    Get an operations assistant instance.

    Returns:
        OperationsAssistant: Assistant for querying operational knowledge
    """
    nvm = await create_hypersync_integration()
    embedder = EmbeddingGenerator()
    return OperationsAssistant(nvm, embedder)


__all__ = [
    'PresetKnowledgeLoader',
    'OperationsAssistant',
    'initialize_preset_knowledge',
    'get_operations_assistant'
]
