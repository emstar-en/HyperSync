"""
Model Registry & Invocation Wiring - Connects model operations.
"""
from hypersync.tokens.tracker import get_token_tracker
from hypersync.tokens.budget_enforcer import get_budget_enforcer

class ModelIntegration:
    """Complete model system wiring."""

    def __init__(self):
        self.token_tracker = get_token_tracker()
        self.budget_enforcer = get_budget_enforcer()
        self._model_registry = {}

    def register_model(self, model_id, model):
        """Register model."""
        self._model_registry[model_id] = model

    def invoke_model(self, model_id, prompt, user_id=None):
        """Invoke model with full tracking."""
        # Check budget
        if user_id and not self.budget_enforcer.can_consume(user_id, estimated_tokens=1000):
            raise Exception("Budget exceeded")

        # Track operation
        with self.token_tracker.track_operation("model_invoke") as ctx:
            model = self._model_registry.get(model_id)
            if not model:
                raise ValueError(f"Model not found: {model_id}")

            # Invoke model
            response = model.generate(prompt)

            # Record tokens
            ctx.record_tokens(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(response.split())
            )

            # Update budget
            if user_id:
                self.budget_enforcer.consume(user_id, actual_tokens=ctx.tracker.get_total_tokens())

            return response
