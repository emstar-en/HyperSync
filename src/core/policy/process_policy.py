"""
Process Execution Policy Verbs and Enforcement
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ProcessVerb(Enum):
    """Process execution policy verbs"""
    PROC_SPAWN = "proc:spawn"
    PROC_SIGNAL = "proc:signal"
    PROC_ATTACH = "proc:attach"
    PROC_KILL = "proc:kill"
    PROC_INSPECT = "proc:inspect"


@dataclass
class ProcessReceipt:
    """Receipt for process execution"""
    receipt_id: str
    agent_id: str
    sandbox_id: str
    command: List[str]
    cwd: Optional[str]
    exit_code: int
    state: str
    duration_seconds: float
    stdout_size: int
    stderr_size: int
    pid: Optional[int]
    started_at: datetime
    completed_at: datetime
    touched_paths: List[str] = None

    def to_dict(self) -> dict:
        return {
            "receipt_id": self.receipt_id,
            "agent_id": self.agent_id,
            "sandbox_id": self.sandbox_id,
            "command": self.command,
            "cwd": self.cwd,
            "exit_code": self.exit_code,
            "state": self.state,
            "duration_seconds": self.duration_seconds,
            "stdout_size": self.stdout_size,
            "stderr_size": self.stderr_size,
            "pid": self.pid,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "touched_paths": self.touched_paths or []
        }


class ProcessPolicyEngine:
    """Policy engine for process execution"""

    def __init__(self):
        self.rules: List[Dict] = []
        self.receipts: List[ProcessReceipt] = []

    def add_rule(self, rule: Dict):
        """Add a policy rule"""
        self.rules.append(rule)
        logger.info(f"Added process policy rule: {rule.get('rule_id')}")

    def check_spawn(self, context: Dict) -> bool:
        """
        Check if process spawn is allowed.

        Args:
            context: Context with agent, command, cwd, etc.

        Returns:
            True if allowed, False otherwise
        """
        # Default allow for now
        # In production, evaluate against rules

        command = context.get("command", [])
        agent = context.get("agent", {})

        # Check if command is in denied list
        denied_commands = ["rm", "dd", "mkfs", "fdisk"]
        if command and command[0] in denied_commands:
            logger.warning(f"Denied dangerous command: {command[0]}")
            return False

        # Check clearance for sensitive commands
        sensitive_commands = ["sudo", "su", "passwd"]
        if command and command[0] in sensitive_commands:
            clearance = agent.get("clearance", "internal")
            if clearance not in ["restricted", "critical"]:
                logger.warning(f"Insufficient clearance for {command[0]}")
                return False

        return True

    def create_receipt(
        self,
        agent_id: str,
        sandbox_id: str,
        process_result
    ) -> ProcessReceipt:
        """
        Create receipt for process execution.

        Args:
            agent_id: Agent ID
            sandbox_id: Sandbox ID
            process_result: ProcessResult object

        Returns:
            ProcessReceipt
        """
        from datetime import datetime

        receipt_id = f"proc-receipt-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        receipt = ProcessReceipt(
            receipt_id=receipt_id,
            agent_id=agent_id,
            sandbox_id=sandbox_id,
            command=process_result.command,
            cwd=None,  # Would be extracted from config
            exit_code=process_result.exit_code,
            state=process_result.state.value,
            duration_seconds=process_result.duration_seconds,
            stdout_size=len(process_result.stdout),
            stderr_size=len(process_result.stderr),
            pid=process_result.pid,
            started_at=process_result.started_at or datetime.utcnow(),
            completed_at=process_result.completed_at or datetime.utcnow(),
            touched_paths=[]  # Would be tracked via filesystem monitoring
        )

        self.receipts.append(receipt)
        logger.info(f"Created process receipt: {receipt_id}")

        return receipt

    def get_receipts(
        self,
        agent_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[ProcessReceipt]:
        """Get process receipts"""
        receipts = self.receipts

        if agent_id:
            receipts = [r for r in receipts if r.agent_id == agent_id]

        if limit:
            receipts = receipts[-limit:]

        return receipts


class PolicyEnforcedProcessManager:
    """Process manager with policy enforcement and receipt generation"""

    def __init__(self, process_manager, policy_engine: ProcessPolicyEngine, sandbox=None):
        """
        Initialize policy-enforced process manager.

        Args:
            process_manager: Base ProcessManager instance
            policy_engine: ProcessPolicyEngine instance
            sandbox: Optional sandbox for context
        """
        self.process_manager = process_manager
        self.policy_engine = policy_engine
        self.sandbox = sandbox

    def run(self, command: List[str], **kwargs) -> tuple:
        """
        Run command with policy check and receipt generation.

        Returns:
            Tuple of (ProcessResult, ProcessReceipt)
        """
        # Build context
        context = {
            "command": command,
            "cwd": kwargs.get("cwd"),
            "agent": {
                "id": self.sandbox.agent_id if self.sandbox else "unknown",
                "clearance": kwargs.get("clearance", "internal")
            }
        }

        # Check policy
        if not self.policy_engine.check_spawn(context):
            # Create failed result
            from hypersync.environment.process_manager import ProcessResult, ProcessState
            from datetime import datetime

            result = ProcessResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr="Execution denied by policy",
                state=ProcessState.FAILED,
                duration_seconds=0.0,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                error="Policy violation"
            )

            receipt = self.policy_engine.create_receipt(
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                process_result=result
            )

            return result, receipt

        # Execute process
        result = self.process_manager.run(command, **kwargs)

        # Create receipt
        receipt = self.policy_engine.create_receipt(
            agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
            sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
            process_result=result
        )

        return result, receipt

    def get_receipts(self, **kwargs) -> List[ProcessReceipt]:
        """Get process receipts"""
        return self.policy_engine.get_receipts(**kwargs)


# Example policy rules
EXAMPLE_PROCESS_RULES = {
    "rules": [
        {
            "rule_id": "allow-basic-commands",
            "verb": "proc:spawn",
            "effect": "allow",
            "conditions": {
                "command": {
                    "whitelist": ["ls", "cat", "echo", "grep", "find", "python", "node"]
                }
            },
            "priority": 100
        },
        {
            "rule_id": "deny-dangerous-commands",
            "verb": "proc:spawn",
            "effect": "deny",
            "conditions": {
                "command": {
                    "blacklist": ["rm", "dd", "mkfs", "fdisk", "format"]
                }
            },
            "priority": 200
        },
        {
            "rule_id": "require-clearance-for-sudo",
            "verb": "proc:spawn",
            "effect": "allow",
            "conditions": {
                "command": {"prefix": ["sudo", "su"]},
                "agent": {"clearance": "restricted"}
            },
            "priority": 150
        }
    ]
}


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    # Example usage
    engine = ProcessPolicyEngine()

    # Test spawn check
    context = {
        "command": ["ls", "-la"],
        "agent": {"clearance": "internal"}
    }

    allowed = engine.check_spawn(context)
    print(f"Spawn allowed: {allowed}")

    # Test denied command
    context = {
        "command": ["rm", "-rf", "/"],
        "agent": {"clearance": "internal"}
    }

    allowed = engine.check_spawn(context)
    print(f"Dangerous command allowed: {allowed}")
