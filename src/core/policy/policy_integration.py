"""
Policy Integration for Sandbox Manager
Connects policy engine with sandbox operations.
"""

import logging
from typing import Dict, Optional
from .environment_verbs import EnvironmentPolicyEngine, EnvironmentVerb

logger = logging.getLogger(__name__)


class PolicyEnforcedSandboxManager:
    """Sandbox manager with policy enforcement"""

    def __init__(self, sandbox_manager, policy_engine: EnvironmentPolicyEngine):
        self.sandbox_manager = sandbox_manager
        self.policy_engine = policy_engine

    def activate_with_policy(
        self,
        agent_id: str,
        agent_clearance: str,
        agent_tier: str,
        **kwargs
    ):
        """Activate sandbox with policy check"""
        context = {
            "agent": {
                "id": agent_id,
                "clearance": agent_clearance,
                "tier": agent_tier
            },
            "resource": kwargs.get("quotas", {})
        }

        # Check if agent can create sandbox
        if not self.policy_engine.evaluate(EnvironmentVerb.SANDBOX_CREATE, context):
            raise PermissionError(f"Agent {agent_id} not authorized to create sandbox")

        # Validate allowed paths against policy
        allowed_paths = kwargs.get("allowed_paths", [])
        for path in allowed_paths:
            path_context = {**context, "path": path}
            if not self.policy_engine.evaluate(EnvironmentVerb.FS_PATH_ALLOW, path_context):
                raise PermissionError(f"Agent {agent_id} not authorized for path {path}")

        # Create sandbox
        sandbox = self.sandbox_manager.activate(agent_id=agent_id, **kwargs)
        logger.info(f"Policy-enforced sandbox activated for {agent_id}")
        return sandbox

    def check_operation(
        self,
        sandbox_id: str,
        operation: str,
        path: str
    ) -> bool:
        """Check if operation is allowed by policy"""
        sandbox = self.sandbox_manager.get_sandbox(sandbox_id)
        if not sandbox:
            return False

        # Map operation to verb
        verb_map = {
            "read": EnvironmentVerb.FS_READ,
            "write": EnvironmentVerb.FS_WRITE,
            "execute": EnvironmentVerb.FS_EXECUTE,
            "list": EnvironmentVerb.FS_LIST,
            "delete": EnvironmentVerb.FS_DELETE
        }

        verb = verb_map.get(operation)
        if not verb:
            return False

        context = {
            "agent": {"id": sandbox.agent_id},
            "path": path
        }

        # Check both sandbox policy and global policy
        sandbox_allowed = sandbox.check_access(path, operation)
        policy_allowed = self.policy_engine.evaluate(verb, context)

        return sandbox_allowed and policy_allowed
