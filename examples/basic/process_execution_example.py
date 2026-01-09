"""
Example: Process Execution with Policy Enforcement
"""

import logging
from hypersync.environment.process_manager import ProcessManager
from hypersync.policy.process_policy import (
    ProcessPolicyEngine,
    PolicyEnforcedProcessManager
)

logging.basicConfig(level=logging.INFO)


class MockSandbox:
    """Mock sandbox for example"""
    agent_id = "example-agent"
    sandbox_id = "example-sandbox"


def main():
    print("=" * 80)
    print("HyperSync Process Execution Example")
    print("=" * 80)

    # 1. Basic execution
    print("\n1. Basic Process Execution")
    print("-" * 80)

    manager = ProcessManager()

    result = manager.run(["echo", "Hello from HyperSync!"])
    print(f"Exit code: {result.exit_code}")
    print(f"Output: {result.stdout.strip()}")
    print(f"Duration: {result.duration_seconds:.3f}s")

    # 2. Policy-enforced execution
    print("\n2. Policy-Enforced Execution")
    print("-" * 80)

    policy_engine = ProcessPolicyEngine()
    sandbox = MockSandbox()

    enforced_manager = PolicyEnforcedProcessManager(
        manager,
        policy_engine,
        sandbox
    )

    # Allowed command
    print("\nExecuting allowed command...")
    result, receipt = enforced_manager.run(["echo", "Allowed!"])
    print(f"Success: {result.success}")
    print(f"Receipt ID: {receipt.receipt_id}")

    # Denied command
    print("\nExecuting denied command...")
    result, receipt = enforced_manager.run(["rm", "-rf", "/"])
    print(f"Success: {result.success}")
    print(f"Error: {result.stderr}")

    # 3. Execution with timeout
    print("\n3. Execution with Timeout")
    print("-" * 80)

    import sys
    if sys.platform != "win32":
        result = manager.run(["sleep", "5"], timeout=1.0)
        print(f"State: {result.state}")
        print(f"Timed out: {result.state.value == 'timeout'}")

    # 4. Statistics
    print("\n4. Process Statistics")
    print("-" * 80)

    stats = manager.get_stats()
    print(f"Total processes: {stats['total_processes']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Average duration: {stats['average_duration_seconds']:.3f}s")

    # 5. Receipts
    print("\n5. Execution Receipts")
    print("-" * 80)

    receipts = enforced_manager.get_receipts()
    print(f"Total receipts: {len(receipts)}")
    for r in receipts[-3:]:  # Last 3
        print(f"  {r.receipt_id}: {' '.join(r.command)} -> exit {r.exit_code}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
