"""
Example: High-Risk Operation with Rollback
"""

import logging
from hypersync.safety.rollback_system import (
    RollbackManager,
    HighRiskController,
    RiskLevel,
    OperationType
)

logging.basicConfig(level=logging.INFO)


def main():
    print("=" * 80)
    print("High-Risk Operation with Rollback Example")
    print("=" * 80)

    # Initialize managers
    rollback_mgr = RollbackManager()
    controller = HighRiskController(rollback_mgr)

    # Define approval callback
    def approve_operation(operation):
        print(f"\nApproval Request:")
        print(f"  Risk Level: {operation.risk_level.value}")
        print(f"  Operation: {operation.description}")
        print(f"  Agent: {operation.agent_id}")

        # Auto-approve for demo
        if operation.risk_level == RiskLevel.CRITICAL:
            print("  Status: REQUIRES HUMAN APPROVAL")
            return False

        print("  Status: AUTO-APPROVED")
        return True

    controller.add_approval_callback(approve_operation)

    # Test file
    test_file = "/tmp/critical_data.txt"
    with open(test_file, 'w') as f:
        f.write("Original critical data")

    print(f"\nOriginal content: {open(test_file).read()}")

    # Execute high-risk operation
    print("\nExecuting HIGH risk operation...")

    def modify_file():
        with open(test_file, 'w') as f:
            f.write("Modified by agent")
        return "Modified"

    success, result, operation = controller.execute_operation(
        operation_type=OperationType.FILE_MODIFY,
        risk_level=RiskLevel.HIGH,
        description="Modify critical file",
        agent_id="agent-1",
        action=modify_file,
        affected_paths=[test_file]
    )

    print(f"\nOperation Result:")
    print(f"  Success: {success}")
    print(f"  Result: {result}")
    print(f"  Operation ID: {operation.operation_id}")
    print(f"  Snapshot ID: {operation.snapshot_id}")

    print(f"\nModified content: {open(test_file).read()}")

    # Rollback
    print("\nRolling back operation...")
    rollback_success = controller.rollback_operation(operation.operation_id)

    print(f"Rollback success: {rollback_success}")
    print(f"Content after rollback: {open(test_file).read()}")

    # Try CRITICAL operation (will be denied)
    print("\nAttempting CRITICAL risk operation...")

    def critical_action():
        return "This won't execute"

    success, result, operation = controller.execute_operation(
        operation_type=OperationType.SYSTEM_MODIFY,
        risk_level=RiskLevel.CRITICAL,
        description="System modification",
        agent_id="agent-1",
        action=critical_action
    )

    print(f"Critical operation success: {success}")

    # Show operation history
    print("\nOperation History:")
    operations = controller.get_operations()
    for op in operations:
        status = "ROLLED BACK" if op.rolled_back else "ACTIVE"
        print(f"  {op.operation_id}: {op.description} [{status}]")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
