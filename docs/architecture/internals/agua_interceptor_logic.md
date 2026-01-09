# AGUA Interceptor Logic

## Overview
The AGUA Interceptor is a middleware layer that sits between the API and the Core Engine. It intercepts every request, checks the current PCT phase of the agent, and enforces the corresponding rules.

## Logic Flow

```python
class AguaInterceptor:
    def intercept(self, request: Request, context: Context) -> Response:
        # 1. Identify Agent & Phase
        agent_id = context.agent_id
        phase = self.get_agent_phase(agent_id) # Pathfinder, Cartographer, Trailblazer

        # 2. Load Ruleset
        rules = self.load_rules(phase)

        # 3. Validate Request against Rules
        if not rules.allow_network and request.is_network_call():
            raise PolicyViolation("Network access denied in Trailblazer phase")

        if not rules.allow_filesystem and request.is_write_op():
            raise PolicyViolation("Filesystem write denied in Cartographer phase")

        # 4. Enforce Determinism
        if phase == "Trailblazer":
            self.enforce_determinism(request)

        # 5. Execute & Record
        try:
            response = next_middleware(request)

            # 6. Record Trace (if Pathfinder)
            if phase == "Pathfinder":
                self.recorder.capture(agent_id, request, response)

            return response

        except Exception as e:
            self.recorder.capture_error(agent_id, request, e)
            raise e

    def enforce_determinism(self, request):
        # Ensure no random seeds, timestamps, or floating point non-determinism
        if "seed" not in request.params:
            raise DeterminismError("Missing seed in Trailblazer request")
```

## Key Components
1.  **Phase Resolver**: Looks up the agent's current assignment in the Geometry Engine.
2.  **Rule Engine**: Evaluates the request against `geometry_control_rulesets.json`.
3.  **Determinism Guard**: Inspects payloads for non-deterministic elements.
