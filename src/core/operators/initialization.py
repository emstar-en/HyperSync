"""
Initialization Operator

Orchestrates prompt preprocessing, compression, and provider routing.
"""

from typing import Optional, Dict, Any
from hypersync.prompt.pipeline import (
    PipelineExecutor,
    PipelineContext,
    SummarizerStage,
    HyperbolicCompressionStage,
    DiffGeneratorStage
)
from hypersync.providers import get_registry, ProviderCapability
from hypersync.token import TokenEventEmitter
from hypersync.token.receipts import get_accumulator


class InitializationOperator:
    """
    Initialization operator for prompt processing.

    Responsibilities:
    - Run local preprocessing pipeline
    - Apply compression techniques
    - Route to appropriate provider
    - Generate receipts and telemetry
    """

    def __init__(
        self,
        enable_summarization: bool = True,
        enable_hyperbolic: bool = True,
        enable_diff: bool = True,
        summarization_threshold: int = 2000,
        compression_ratio: float = 0.3
    ):
        self.enable_summarization = enable_summarization
        self.enable_hyperbolic = enable_hyperbolic
        self.enable_diff = enable_diff

        # Build pipeline
        stages = []

        if enable_summarization:
            stages.append(SummarizerStage(
                threshold=summarization_threshold,
                target_ratio=0.5
            ))

        if enable_hyperbolic:
            stages.append(HyperbolicCompressionStage(
                compression_ratio=compression_ratio
            ))

        if enable_diff:
            stages.append(DiffGeneratorStage())

        # Create executor
        self.emitter = TokenEventEmitter(
            receipt_accumulator=get_accumulator()
        )
        self.pipeline = PipelineExecutor(stages, self.emitter)

        # Provider registry
        self.registry = get_registry()

    async def process(
        self,
        prompt: str,
        provider_id: Optional[str] = None,
        model: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a prompt through the pipeline and send to provider.

        Args:
            prompt: Input prompt text
            provider_id: Target provider (or auto-select)
            model: Target model
            request_id: Request identifier
            session_id: Session identifier
            user_id: User identifier
            **kwargs: Additional provider parameters

        Returns:
            Provider response with token accounting
        """
        import uuid

        # Generate request ID if not provided
        if request_id is None:
            request_id = f"req_{uuid.uuid4().hex[:16]}"

        # Create pipeline context
        context = PipelineContext(
            prompt=prompt,
            messages=[{"role": "user", "content": prompt}],
            request_id=request_id,
            session_id=session_id,
            user_id=user_id,
            metadata={}
        )

        # Emit input event
        from hypersync.token import TokenCounterFactory
        counter = TokenCounterFactory.create(model or "gpt-4")
        input_tokens = counter.count(prompt)

        self.emitter.emit(
            stage="input",
            tokens_in=input_tokens,
            tokens_out=input_tokens,
            request_id=request_id,
            session_id=session_id,
            user_id=user_id
        )

        # Run pipeline
        processed_context = await self.pipeline.execute(context)

        # Select provider
        if provider_id is None:
            provider_id = self._select_provider()

        provider = self.registry.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Provider not found: {provider_id}")

        # Call provider
        response = await provider.adapter.chat_complete(
            processed_context.messages,
            model=model,
            **kwargs
        )

        # Emit provider response event
        self.emitter.emit(
            stage="provider_response",
            tokens_in=response.get("metadata", {}).get("prompt_tokens", 0),
            tokens_out=response.get("tokens_used", 0),
            request_id=request_id,
            session_id=session_id,
            user_id=user_id,
            model=response.get("model"),
            provider=provider_id,
            metadata=response.get("metadata", {})
        )

        # Finalize receipt
        accumulator = get_accumulator()
        receipt = accumulator.finalize_receipt(request_id)

        # Add receipt to response
        response["receipt"] = receipt.to_dict() if receipt else None

        return response

    def _select_provider(self) -> str:
        """
        Auto-select a provider.

        Selection criteria:
        - Health status
        - Capabilities
        - Cost

        TODO: Implement sophisticated selection logic.
        """
        providers = self.registry.list_providers(
            capability=ProviderCapability.CHAT_COMPLETION
        )

        # Filter to healthy providers
        healthy = [p for p in providers if p.is_available()]

        if not healthy:
            raise ValueError("No healthy providers available")

        # Return first healthy provider
        # TODO: Implement cost-based selection
        return healthy[0].config.provider_id
