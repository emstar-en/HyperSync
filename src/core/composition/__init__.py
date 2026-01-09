"""HyperSync Agent Composition Module"""

from .composition_engine import (
    CompositionEngine, AgentComposition, AgentRole,
    CompositionPattern, RoutingStrategy, SyncPolicy,
    FailureHandling, ExecutionStatus
)

__all__ = [
    "CompositionEngine", "AgentComposition", "AgentRole",
    "CompositionPattern", "RoutingStrategy", "SyncPolicy",
    "FailureHandling", "ExecutionStatus"
]
