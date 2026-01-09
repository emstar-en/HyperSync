"""
Diff Generator Stage

Generates diffs for incremental prompts.
"""

import time
from typing import Optional
from hypersync.prompt.pipeline.stage import PipelineStage, PipelineContext, StageResult
from hypersync.token import TokenCounterFactory


class DiffGeneratorStage(PipelineStage):
    """
    Generates diffs for incremental prompts.

    When a prompt is similar to a previous one, sends only the diff
    instead of the full prompt.
    """

    def __init__(self, model: str = "gpt-4"):
        super().__init__("diff_generation")
        self.counter = TokenCounterFactory.create(model)
        self._previous_prompt: Optional[str] = None

    async def process(self, context: PipelineContext) -> StageResult:
        """Generate diff if applicable."""
        start_time = time.time()

        # Count input tokens
        tokens_in = self.counter.count(context.prompt)

        # Check if we have a previous prompt
        if self._previous_prompt is None:
            # First prompt, no diff possible
            self._previous_prompt = context.prompt
            return StageResult(
                context=context,
                tokens_in=tokens_in,
                tokens_out=tokens_in,
                latency_ms=int((time.time() - start_time) * 1000),
                metadata={"diff_generated": False}
            )

        # Generate diff
        diff = self._generate_diff(self._previous_prompt, context.prompt)
        tokens_out = self.counter.count(diff)

        # Only use diff if it's actually smaller
        if tokens_out < tokens_in * 0.8:  # 20% savings threshold
            context.prompt = diff
            context.metadata["diff_generated"] = True
            context.metadata["diff_base"] = self._previous_prompt[:100]  # Store reference

            self._previous_prompt = context.prompt

            return StageResult(
                context=context,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                latency_ms=int((time.time() - start_time) * 1000),
                metadata={
                    "diff_generated": True,
                    "compression_ratio": tokens_out / tokens_in
                }
            )
        else:
            # Diff not beneficial, use full prompt
            self._previous_prompt = context.prompt
            return StageResult(
                context=context,
                tokens_in=tokens_in,
                tokens_out=tokens_in,
                latency_ms=int((time.time() - start_time) * 1000),
                metadata={"diff_generated": False, "reason": "not_beneficial"}
            )

    def _generate_diff(self, old: str, new: str) -> str:
        """
        Generate a diff between old and new text.

        Simple implementation using line-based diff.
        TODO: Use more sophisticated diff algorithm.
        """
        old_lines = old.split('
')
        new_lines = new.split('
')

        diff_lines = []

        for i, new_line in enumerate(new_lines):
            if i >= len(old_lines) or old_lines[i] != new_line:
                diff_lines.append(f"+ {new_line}")

        return '
'.join(diff_lines)
