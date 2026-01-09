"""HyperSync Orchestrator Main Entry Point

Updated to use comprehensive component wiring.
"""

import logging
from flask import Flask
from hypersync.wiring import get_hub
from hypersync.wiring.api_integration import create_integrated_app
from hypersync.wiring.event_bus import get_event_bus, EventTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config=None):
    """Create and configure Flask application with full wiring"""

    logger.info("Initializing HyperSync Orchestrator with comprehensive wiring...")

    # Create integrated app (includes hub initialization)
    app = create_integrated_app(config)

    # Get hub and event bus
    hub = app.hub
    event_bus = get_event_bus()

    # Subscribe to key events for logging
    def log_deployment(event_data):
        logger.info(f"Service deployed: {event_data}")

    def log_governance(event_data):
        logger.info(f"Governance event: {event_data}")

    event_bus.subscribe(EventTypes.SERVICE_DEPLOYED, log_deployment)
    event_bus.subscribe(EventTypes.CHANGE_APPROVED, log_governance)

    # Start background services
    if hasattr(hub.curvature_manager, 'start_background_updates'):
        hub.curvature_manager.start_background_updates()

    logger.info("HyperSync Orchestrator started successfully")
    logger.info(f"Components wired: {len([c for c in dir(hub) if not c.startswith('_')])}")

    return app


def main():
    """Main entry point"""
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=False)


if __name__ == '__main__':
    main()
