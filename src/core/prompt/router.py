"""
Prompt Router

Routes prompts through preprocessing pipeline before cloud invocation.
"""

from typing import Optional, Dict, Any
from hypersync.operators.initialization import InitializationOperator


class PromptRouter:
    """
    Routes prompts with policy enforcement.

    Ensures local preprocessing is performed before cloud calls
    unless policies override.
    """

    def __init__(self, operator: Optional[InitializationOperator] = None):
        self.operator = operator or InitializationOperator()
        self._policy_engine = None  # TODO: Integrate with policy engine

    async def route(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        local_preprocess: bool = True,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Route a prompt to a provider.

        Args:
            prompt: Input prompt
            provider: Target provider
            model: Target model
            local_preprocess: Whether to run local preprocessing
            request_id: Request identifier
            session_id: Session identifier
            user_id: User identifier
            **kwargs: Additional parameters

        Returns:
            Provider response with receipt
        """
        # Check policy
        if self._policy_engine:
            # TODO: Check if local_preprocess is required by policy
            pass

        # Route through operator
        if local_preprocess:
            return await self.operator.process(
                prompt=prompt,
                provider_id=provider,
                model=model,
                request_id=request_id,
                session_id=session_id,
                user_id=user_id,
                **kwargs
            )
        else:
            # Direct provider call (bypass preprocessing)
            # TODO: Implement direct routing
            raise NotImplementedError("Direct routing not yet implemented")

    def set_policy_engine(self, engine):
        """Set the policy engine for enforcement."""
        self._policy_engine = engine


# Global router instance
_global_router = None


def get_router() -> PromptRouter:
    """Get the global prompt router."""
    global _global_router
    if _global_router is None:
        _global_router = PromptRouter()
    return _global_router
