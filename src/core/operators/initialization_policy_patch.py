"""
Initialization Operator - Policy Integration Patch

This patch adds policy enforcement to the initialization operator.
"""

# Add to initialization.py:

from hypersync.policy.engine import get_policy_engine, PolicyVerb, PolicyContext, PolicyDecision

class InitializationOperator:
    """
    Initialization operator with policy enforcement.

    Changes:
    - Check budget policy before processing
    - Check preprocessing policy
    - Record usage after completion
    """

    def __init__(self, *args, **kwargs):
        # ... existing init code ...
        self.policy_engine = get_policy_engine()

    async def process(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Process with policy enforcement."""
        # ... existing code to create context ...

        # Create policy context
        policy_ctx = PolicyContext(
            user_id=user_id,
            session_id=session_id,
            provider_id=provider_id,
            tokens=input_tokens,
            cost_usd=0.0,  # Estimated
            metadata={"preprocessed": True}
        )

        # Check budget policy
        decision = self.policy_engine.evaluate(
            PolicyVerb.TOKEN_BUDGET,
            policy_ctx
        )

        if not decision.allowed:
            raise Exception(f"Policy denied: {decision.reason}")

        # Check preprocessing policy
        preprocess_decision = self.policy_engine.evaluate(
            PolicyVerb.PROMPT_PREPROCESS,
            policy_ctx
        )

        if not preprocess_decision.allowed:
            # Preprocessing required
            pass  # Already enabled

        # ... existing processing code ...

        # Record usage
        policy_ctx.tokens = response.get("tokens_used", 0)
        policy_ctx.cost_usd = response.get("metadata", {}).get("cost_usd", 0.0)
        self.policy_engine.record_usage(policy_ctx)

        return response
