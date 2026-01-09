"""
Pipeline Executor

Executes a sequence of pipeline stages with error handling and telemetry.
"""

import time
from typing import List, Optional
from hypersync.prompt.pipeline.stage import PipelineStage, PipelineContext, StageResult
from hypersync.token import TokenEventEmitter


class PipelineExecutor:
    """
    Executes a pipeline of stages.

    Features:
    - Sequential stage execution
    - Error handling and recovery
    - Token accounting
    - Telemetry emission
    """

    def __init__(
        self,
        stages: List[PipelineStage],
        emitter: Optional[TokenEventEmitter] = None
    ):
        self.stages = stages
        self.emitter = emitter or TokenEventEmitter()

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        Execute the pipeline.

        Args:
            context: Initial pipeline context

        Returns:
            Final pipeline context after all stages

        Raises:
            Exception: If a stage fails and no recovery is possible
        """
        current_context = context

        for stage in self.stages:
            # Check if stage is enabled
            if not stage.is_enabled(current_context):
                continue

            try:
                # Execute stage
                start_time = time.time()
                result = await stage.process(current_context)
                latency_ms = int((time.time() - start_time) * 1000)

                # Emit token event
                self.emitter.emit(
                    stage=stage.name,
                    tokens_in=result.tokens_in,
                    tokens_out=result.tokens_out,
                    request_id=context.request_id,
                    session_id=context.session_id,
                    user_id=context.user_id,
                    metadata={
                        "latency_ms": latency_ms,
                        **result.metadata
                    }
                )

                # Update context
                current_context = result.context

            except Exception as e:
                # Log error and continue or fail based on stage criticality
                print(f"Stage {stage.name} failed: {e}")

                # For now, re-raise
                # TODO: Add recovery strategies
                raise

        return current_context

    def add_stage(self, stage: PipelineStage, position: Optional[int] = None):
        """Add a stage to the pipeline."""
        if position is None:
            self.stages.append(stage)
        else:
            self.stages.insert(position, stage)

    def remove_stage(self, name: str):
        """Remove a stage by name."""
        self.stages = [s for s in self.stages if s.name != name]

    def get_stage(self, name: str) -> Optional[PipelineStage]:
        """Get a stage by name."""
        for stage in self.stages:
            if stage.name == name:
                return stage
        return None
