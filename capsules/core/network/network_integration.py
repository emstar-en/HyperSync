"""
Network & Communication Wiring - Connects all network protocols.
"""
import logging

logger = logging.getLogger(__name__)

class NetworkIntegration:
    """Complete network wiring."""

    def __init__(self):
        self._protocols = {}
        self._service_discovery = None
        self._message_bus = None

    def register_protocol(self, name, protocol):
        """Register network protocol."""
        self._protocols[name] = protocol
        logger.info(f"Registered protocol: {name}")

    def send_message(self, destination, message, protocol="default"):
        """Send message with full integration."""
        # Discover service
        if self._service_discovery:
            endpoint = self._service_discovery.discover(destination)
        else:
            endpoint = destination

        # Send via protocol
        protocol_obj = self._protocols.get(protocol)
        if protocol_obj:
            return protocol_obj.send(endpoint, message)

        # Fallback to message bus
        if self._message_bus:
            return self._message_bus.publish(destination, message)
