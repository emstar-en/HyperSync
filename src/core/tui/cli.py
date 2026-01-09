"""
HyperSync TUI CLI Command

CLI command to launch TUI.
"""

import asyncio
import logging
import sys
from typing import Optional

from hypersync.tui.server import get_session_hub
from hypersync.tui.client.runtime import create_runtime
from hypersync.tui.capabilities.detector import detect_capabilities


logger = logging.getLogger(__name__)


async def launch_tui(
    operator_id: Optional[str] = None,
    dry_run: bool = False,
    record_capabilities: bool = False
):
    """
    Launch TUI client and server.

    Args:
        operator_id: Operator identifier
        dry_run: Dry run mode (detect capabilities only)
        record_capabilities: Record capabilities to file
    """
    # Detect capabilities
    capabilities = detect_capabilities()

    if record_capabilities:
        import json
        with open('tui_capabilities.json', 'w') as f:
            json.dump(capabilities.to_dict(), f, indent=2)
        print(f"Capabilities recorded to tui_capabilities.json")

    if dry_run:
        print("Dry run mode - capabilities detected:")
        print(f"  Terminal: {capabilities.term}")
        print(f"  Size: {capabilities.rows}x{capabilities.cols}")
        print(f"  Color: {capabilities.color_support.name}")
        print(f"  Unicode: {capabilities.unicode_support}")
        print(f"  Mouse: {capabilities.mouse_support}")
        print(f"  Tier: {capabilities.tier.name}")
        return

    # Get operator ID
    if not operator_id:
        import getpass
        operator_id = getpass.getuser()

    # Create session
    hub = get_session_hub()
    session_id = await hub.create_session(operator_id, capabilities.to_dict())

    logger.info(f"Created TUI session {session_id} for operator {operator_id}")

    # Create runtime
    runtime = create_runtime()

    try:
        # Start runtime
        runtime.start()

        # Main loop
        while runtime.running:
            # Check for resize
            if runtime.check_resize():
                # TODO: Handle resize
                pass

            # Read input
            key = runtime.read_input(timeout=0.1)
            if key:
                if key == 'q':
                    break
                # TODO: Handle input

            # Get messages from server
            messages = await hub.get_messages(session_id, timeout=0.1)
            for message in messages:
                # TODO: Handle messages
                pass

            # Render
            runtime.clear_buffer()

            # TODO: Render panels
            runtime.write_text(0, 0, "HyperSync TUI")
            runtime.write_text(1, 0, f"Session: {session_id}")
            runtime.write_text(2, 0, f"Operator: {operator_id}")
            runtime.write_text(3, 0, f"Tier: {capabilities.tier.name}")
            runtime.write_text(5, 0, "Press 'q' to quit")

            runtime.render()

            await asyncio.sleep(0.01)

    finally:
        # Stop runtime
        runtime.stop()

        # Destroy session
        await hub.destroy_session(session_id)

        logger.info(f"TUI session {session_id} ended")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Launch HyperSync TUI')
    parser.add_argument('--operator', help='Operator ID')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (detect capabilities only)')
    parser.add_argument('--record-capabilities', action='store_true', help='Record capabilities to file')

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='tui.log'
    )

    # Run
    try:
        asyncio.run(launch_tui(
            operator_id=args.operator,
            dry_run=args.dry_run,
            record_capabilities=args.record_capabilities
        ))
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(0)


if __name__ == '__main__':
    main()
