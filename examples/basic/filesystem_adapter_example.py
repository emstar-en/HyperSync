"""
Example: Using Filesystem Adapters with Policy Enforcement
"""

import logging
from hypersync.environment.fs_adapters import FileSystemAdapter
from hypersync.environment.policy_fs_adapter import PolicyEnforcedFileSystemAdapter
from hypersync.environment.sandbox_manager import SandboxManager

logging.basicConfig(level=logging.INFO)


def telemetry_handler(operation):
    """Handle telemetry events"""
    print(f"\n[TELEMETRY]")
    print(f"  Operation: {operation.operation}")
    print(f"  Path: {operation.path}")
    print(f"  Success: {operation.success}")
    print(f"  Duration: {operation.duration_ms:.2f}ms")
    if operation.bytes_transferred > 0:
        print(f"  Bytes: {operation.bytes_transferred}")
    if operation.error:
        print(f"  Error: {operation.error}")


def main():
    print("=" * 80)
    print("HyperSync Filesystem Adapter Example")
    print("=" * 80)

    # 1. Create sandbox
    print("\n1. Creating sandbox...")
    manager = SandboxManager()
    sandbox = manager.activate(
        agent_id="example-agent",
        allowed_paths=["/tmp/hypersync_example"],
        default_dirs=["/tmp/hypersync_example/workspace"]
    )
    print(f"   Sandbox created: {sandbox.sandbox_id}")

    # 2. Create filesystem adapters
    print("\n2. Creating filesystem adapters...")
    base_fs = FileSystemAdapter.for_host()
    enforced_fs = PolicyEnforcedFileSystemAdapter(
        base_fs,
        sandbox,
        telemetry_callback=telemetry_handler
    )
    print(f"   Using {base_fs.fs_type.value} adapter")

    # 3. Write files (allowed)
    print("\n3. Writing files to allowed path...")
    workspace = "/tmp/hypersync_example/workspace"

    enforced_fs.write_text(
        f"{workspace}/README.md",
        "# Example Project\n\nThis is a test project.\n"
    )

    enforced_fs.write_text(
        f"{workspace}/data.txt",
        "Line 1\n",
        append=False
    )

    enforced_fs.write_text(
        f"{workspace}/data.txt",
        "Line 2\n",
        append=True
    )

    # 4. Read files
    print("\n4. Reading files...")
    content = enforced_fs.read_text(f"{workspace}/README.md")
    print(f"   README.md content:\n{content}")

    # 5. List directory
    print("\n5. Listing workspace directory...")
    entries = enforced_fs.list_dir(workspace)
    print(f"   Found {len(entries)} entries:")
    for entry in entries:
        print(f"     - {entry}")

    # 6. Try denied operation
    print("\n6. Attempting denied operation...")
    try:
        enforced_fs.write_text("/etc/test.txt", "This should fail")
    except PermissionError as e:
        print(f"   Expected error: {e}")

    # 7. Get statistics
    print("\n7. Adapter statistics:")
    stats = enforced_fs.get_stats()
    print(f"   Operations: {stats['operation_count']}")
    print(f"   Bytes read: {stats['bytes_read']}")
    print(f"   Bytes written: {stats['bytes_written']}")

    # 8. Cleanup
    print("\n8. Cleaning up...")
    enforced_fs.delete(workspace, recursive=True)
    sandbox.terminate()
    print("   Done!")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
