"""
HyperSync CI/CD Module

Comprehensive CI/CD pipeline management with gold sample collection.
"""

from .pipeline_manager import PipelineManager, PipelineStatus, StageType
from .gold_sample_manager import GoldSampleManager
from .pipeline_executor import PipelineExecutor

__version__ = "1.0.0"
__all__ = [
    "PipelineManager",
    "PipelineStatus",
    "StageType",
    "GoldSampleManager",
    "PipelineExecutor"
]
