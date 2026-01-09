"""
REST API routes for control manifest management.
"""

from flask import Blueprint, request, jsonify
from typing import Optional
import yaml

from hypersync.control.manifest_manager import (
    ControlManifest,
    ControlManifestManager,
    get_manifest_manager,
    ManifestPhase
)

control_bp = Blueprint('control', __name__, url_prefix='/api/v1/control')


@control_bp.route('/manifests', methods=['POST'])
def create_manifest():
    """Create a new control manifest."""
    try:
        # Parse request
        content_type = request.headers.get('Content-Type', '')
        if 'yaml' in content_type:
            data = yaml.safe_load(request.data)
        else:
            data = request.get_json()

        # Create manifest
        manifest = ControlManifest.from_dict(data)
        manager = get_manifest_manager()

        success, error = manager.create(manifest)

        if success:
            return jsonify({
                "status": "created",
                "manifest": manifest.to_dict()
            }), 201
        else:
            return jsonify({
                "status": "error",
                "message": error
            }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@control_bp.route('/manifests/<namespace>/<name>', methods=['GET'])
def get_manifest(namespace: str, name: str):
    """Get a specific manifest."""
    manager = get_manifest_manager()
    manifest = manager.get(name, namespace)

    if manifest:
        return jsonify(manifest.to_dict())
    else:
        return jsonify({
            "status": "error",
            "message": f"Manifest {namespace}/{name} not found"
        }), 404


@control_bp.route('/manifests', methods=['GET'])
def list_manifests():
    """List manifests with optional filtering."""
    namespace = request.args.get('namespace')
    labels = {}

    # Parse label selectors
    for key, value in request.args.items():
        if key.startswith('label.'):
            label_key = key[6:]  # Remove 'label.' prefix
            labels[label_key] = value

    manager = get_manifest_manager()
    manifests = manager.list(namespace=namespace, labels=labels if labels else None)

    return jsonify({
        "items": [m.to_dict() for m in manifests],
        "count": len(manifests)
    })


@control_bp.route('/manifests/<namespace>/<name>', methods=['PUT'])
def update_manifest(namespace: str, name: str):
    """Update an existing manifest."""
    try:
        # Parse request
        content_type = request.headers.get('Content-Type', '')
        if 'yaml' in content_type:
            data = yaml.safe_load(request.data)
        else:
            data = request.get_json()

        # Ensure name/namespace match
        if data.get('metadata', {}).get('name') != name:
            return jsonify({
                "status": "error",
                "message": "Name mismatch"
            }), 400

        if data.get('metadata', {}).get('namespace', 'default') != namespace:
            return jsonify({
                "status": "error",
                "message": "Namespace mismatch"
            }), 400

        # Update manifest
        manifest = ControlManifest.from_dict(data)
        manager = get_manifest_manager()

        success, error = manager.update(manifest)

        if success:
            return jsonify({
                "status": "updated",
                "manifest": manifest.to_dict()
            })
        else:
            return jsonify({
                "status": "error",
                "message": error
            }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@control_bp.route('/manifests/<namespace>/<name>', methods=['DELETE'])
def delete_manifest(namespace: str, name: str):
    """Delete a manifest."""
    manager = get_manifest_manager()
    success, error = manager.delete(name, namespace)

    if success:
        return jsonify({
            "status": "deleted",
            "manifest": f"{namespace}/{name}"
        })
    else:
        return jsonify({
            "status": "error",
            "message": error
        }), 404


@control_bp.route('/manifests/<namespace>/<name>/status', methods=['PATCH'])
def update_manifest_status(namespace: str, name: str):
    """Update manifest status."""
    try:
        data = request.get_json()

        phase_str = data.get('phase')
        if not phase_str:
            return jsonify({
                "status": "error",
                "message": "Phase required"
            }), 400

        phase = ManifestPhase(phase_str)
        message = data.get('message')
        placement = data.get('placement')
        receipt = data.get('receipt')

        manager = get_manifest_manager()
        success = manager.update_status(
            name, namespace, phase, message, placement, receipt
        )

        if success:
            manifest = manager.get(name, namespace)
            return jsonify({
                "status": "updated",
                "manifest": manifest.to_dict()
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Manifest {namespace}/{name} not found"
            }), 404

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@control_bp.route('/manifests/<namespace>/<name>/validate', methods=['POST'])
def validate_manifest(namespace: str, name: str):
    """Validate a manifest without creating it."""
    try:
        content_type = request.headers.get('Content-Type', '')
        if 'yaml' in content_type:
            data = yaml.safe_load(request.data)
        else:
            data = request.get_json()

        manager = get_manifest_manager()
        is_valid, error = manager.validate(data)

        if is_valid:
            return jsonify({
                "status": "valid",
                "message": "Manifest is valid"
            })
        else:
            return jsonify({
                "status": "invalid",
                "message": error
            }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def register_control_routes(app):
    """Register control routes with Flask app."""
    app.register_blueprint(control_bp)
