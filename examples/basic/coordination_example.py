"""
Example: File Change Detection and Coordination
"""

import time
import logging
from hypersync.coordination.file_watcher import FileCoordinator

logging.basicConfig(level=logging.INFO)


def main():
    print("=" * 80)
    print("File Change Detection & Coordination Example")
    print("=" * 80)

    coordinator = FileCoordinator()
    coordinator.start()

    test_file = "/tmp/hypersync_shared.txt"

    # Watch file
    print(f"\nWatching: {test_file}")
    coordinator.watch_file(test_file)

    # Agent 1 acquires lock and writes
    print("\nAgent 1: Acquiring lock...")
    if coordinator.acquire_lock(test_file, "agent-1", "write"):
        print("Agent 1: Lock acquired")

        with open(test_file, 'w') as f:
            f.write("Agent 1 was here\n")

        print("Agent 1: File written")
        time.sleep(1)

        coordinator.release_lock(test_file, "agent-1")
        print("Agent 1: Lock released")

    # Wait for change detection
    time.sleep(1)

    # Agent 2 tries to acquire lock
    print("\nAgent 2: Acquiring lock...")
    if coordinator.acquire_lock(test_file, "agent-2", "write"):
        print("Agent 2: Lock acquired")

        with open(test_file, 'a') as f:
            f.write("Agent 2 was here\n")

        print("Agent 2: File written")
        coordinator.release_lock(test_file, "agent-2")
        print("Agent 2: Lock released")

    # Wait for change detection
    time.sleep(1)

    # Get change history
    print("\nChange History:")
    changes = coordinator.get_changes(path=test_file)
    for change in changes:
        print(f"  {change.timestamp.strftime('%H:%M:%S')}: {change.change_type.value}")

    coordinator.stop()
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
