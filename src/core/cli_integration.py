"""
Updated CLI integration to wire bootstrap into TUI launch.

This file shows the changes needed to hypersync/tui/cli.py
"""

# ADD THIS IMPORT at the top of hypersync/tui/cli.py:
# from hypersync.tui.server.bootstrap import get_bootstrap

# MODIFY the launch_tui function to include bootstrap:

async def launch_tui_with_bootstrap(mode: str = "full", config: dict = None):
    """
    Launch TUI with full data adapter wiring.

    Args:
        mode: TUI mode (full, minimal, monitoring)
        config: Optional configuration overrides
    """
    import asyncio
    import logging
    from hypersync.tui.server.bootstrap import get_bootstrap
    from hypersync.tui.client.runtime import TUIRuntime

    logger = logging.getLogger(__name__)

    # Get bootstrap instance
    bootstrap = get_bootstrap()

    try:
        # Initialize adapters and handlers
        logger.info("Initializing TUI with data adapters...")
        await bootstrap.initialize()

        # Create TUI runtime
        runtime = TUIRuntime(mode=mode, config=config)

        # Start TUI (this blocks until exit)
        logger.info("Starting TUI runtime...")
        await runtime.run()

    except KeyboardInterrupt:
        logger.info("TUI interrupted by user")
    except Exception as e:
        logger.error(f"TUI error: {e}", exc_info=True)
    finally:
        # Graceful shutdown
        logger.info("Shutting down TUI...")
        await bootstrap.shutdown()


# EXAMPLE: Updated CLI command
def cli_main():
    """Main CLI entry point with bootstrap integration."""
    import argparse
    import asyncio
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description="HyperSync TUI")
    parser.add_argument(
        "--mode",
        choices=["full", "minimal", "monitoring"],
        default="full",
        help="TUI mode"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run with bootstrap
    asyncio.run(launch_tui_with_bootstrap(mode=args.mode))


if __name__ == "__main__":
    cli_main()
