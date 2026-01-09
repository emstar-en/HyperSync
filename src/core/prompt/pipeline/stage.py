"""
Prompt Pipeline Stage Interface

Defines the interface for pipeline stages in the initialization operator.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PipelineContext:
    """
    Context passed through pipeline stages.

    Contains the prompt, metadata, and accumulated state.
    """
    prompt: str
    messages: list
    request_id: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class StageResult:
    """Result from a pipeline stage."""
    context: PipelineContext
    tokens_in: int
    tokens_out: int
    latency_ms: int
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PipelineStage(ABC):
    """
    Abstract base class for pipeline stages.

    Each stage processes the context and returns a modified version.
    """

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    @abstractmethod
    async def process(self, context: PipelineContext) -> StageResult:
        """
        Process the pipeline context.

        Args:
            context: Current pipeline context

        Returns:
            StageResult with modified context and metrics
        """
        pass

    def is_enabled(self, context: PipelineContext) -> bool:
        """
        Check if stage should run for this context.

        Can be overridden for conditional execution.
        """
        return self.enabled


class PassthroughStage(PipelineStage):
    """
    Passthrough stage that doesn't modify the context.

    Useful for testing and as a base for simple stages.
    """

    async def process(self, context: PipelineContext) -> StageResult:
        """Pass through without modification."""
        return StageResult(
            context=context,
            tokens_in=0,
            tokens_out=0,
            latency_ms=0
        )
