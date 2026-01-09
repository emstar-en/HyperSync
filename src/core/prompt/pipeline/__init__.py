"""
Prompt Pipeline

Pipeline framework for prompt preprocessing and compression.
"""

from .stage import PipelineStage, PipelineContext, StageResult, PassthroughStage
from .executor import PipelineExecutor
from .stages import SummarizerStage, HyperbolicCompressionStage, DiffGeneratorStage

__all__ = [
    "PipelineStage",
    "PipelineContext",
    "StageResult",
    "PassthroughStage",
    "PipelineExecutor",
    "SummarizerStage",
    "HyperbolicCompressionStage",
    "DiffGeneratorStage"
]
