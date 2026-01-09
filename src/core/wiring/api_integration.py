"""API Integration Layer

Wires all API endpoints to the integration hub.
"""

from flask import Flask, jsonify
from hypersync.wiring import get_hub

# Import all API blueprints
try:
    from api.deployment.placement_api import deployment_api
except ImportError:
    deployment_api = None

try:
    from api.mesh.mesh_api import mesh_api
except ImportError:
    mesh_api = None

try:
    from api.replication.replication_api import replication_api
except ImportError:
    replication_api = None

try:
    from api.edge.edge_api import edge_api
except ImportError:
    edge_api = None

try:
    from api.dimensional.sync_api import dimensional_api
except ImportError:
    dimensional_api = None


def create_integrated_app(config=None):
    """Create Flask app with all integrated APIs"""
    app = Flask(__name__)

    # Initialize hub
    hub = get_hub(config)

    # Store hub in app context
    app.hub = hub

    # Register blueprints
    if deployment_api:
        app.register_blueprint(deployment_api)

    if mesh_api:
        app.register_blueprint(mesh_api)

    if replication_api:
        app.register_blueprint(replication_api)

    if edge_api:
        app.register_blueprint(edge_api)

    if dimensional_api:
        app.register_blueprint(dimensional_api)

    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'version': '1.0.0'})

    # Status endpoint
    @app.route('/status')
    def status():
        return jsonify(hub.get_status())

    # Metrics endpoint
    @app.route('/metrics')
    def metrics():
        return hub.telemetry_manager.export_prometheus(), 200, {'Content-Type': 'text/plain'}

    return app
