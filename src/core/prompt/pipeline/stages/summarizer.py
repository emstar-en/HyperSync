"""
Summarizer Stage

Summarizes long prompts to reduce token count.
"""

import time
from hypersync.prompt.pipeline.stage import PipelineStage, PipelineContext, StageResult
from hypersync.token import TokenCounterFactory


class SummarizerStage(PipelineStage):
    """
    Summarizes prompts that exceed a token threshold.

    Uses extractive summarization to preserve key information
    while reducing token count.
    """

    def __init__(
        self,
        threshold: int = 2000,
        target_ratio: float = 0.5,
        model: str = "gpt-4"
    ):
        super().__init__("summarization")
        self.threshold = threshold
        self.target_ratio = target_ratio
        self.counter = TokenCounterFactory.create(model)

    async def process(self, context: PipelineContext) -> StageResult:
        """Summarize if prompt exceeds threshold."""
        start_time = time.time()

        # Count input tokens
        tokens_in = self.counter.count(context.prompt)

        # Check if summarization is needed
        if tokens_in < self.threshold:
            # No summarization needed
            return StageResult(
                context=context,
                tokens_in=tokens_in,
                tokens_out=tokens_in,
                latency_ms=int((time.time() - start_time) * 1000),
                metadata={"summarized": False}
            )

        # Perform summarization
        summary = self._summarize(context.prompt)
        tokens_out = self.counter.count(summary)

        # Update context
        context.prompt = summary
        context.metadata["summarized"] = True
        context.metadata["original_tokens"] = tokens_in

        return StageResult(
            context=context,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=int((time.time() - start_time) * 1000),
            metadata={
                "summarized": True,
                "compression_ratio": tokens_out / tokens_in
            }
        )

    def _summarize(self, text: str) -> str:
        """
        Perform extractive summarization.

        Simple implementation: extract key sentences.
        TODO: Use more sophisticated summarization.
        """
        sentences = text.split('. ')
        target_count = max(1, int(len(sentences) * self.target_ratio))

        # Take first N sentences (simple heuristic)
        summary_sentences = sentences[:target_count]

        return '. '.join(summary_sentences) + '.'
