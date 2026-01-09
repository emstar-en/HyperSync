"""
HyperSync Security REST API
RESTful endpoints for policy and threat management
"""

from flask import Flask, request, jsonify
from typing import Dict, Any
import json

from hypersync.security.policy_manager import (
    SecurityPolicyManager,
    LDTrainingRecord
)


class SecurityAPI:
    """REST API for security management"""

    def __init__(self, app: Flask = None):
        self.manager = SecurityPolicyManager()
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize Flask app with security routes"""

        @app.route("/api/v1/security/policies", methods=["POST"])
        def create_policy():
            """Create a new security policy"""
            data = request.json

            try:
                policy = self.manager.create_policy(
                    policy_id=data["policy_id"],
                    owner_type=data["owner_type"],
                    owner_id=data["owner_id"],
                    rules=data.get("rules", []),
                    nld_max_score=data.get("nld_max_score", 6),
                    priority=data.get("priority", 50)
                )

                return jsonify({
                    "status": "success",
                    "policy": policy.to_dict()
                }), 201
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 400

        @app.route("/api/v1/security/policies/<policy_id>", methods=["GET"])
        def get_policy(policy_id: str):
            """Get policy by ID"""
            policy = self.manager.get_policy(policy_id)

            if not policy:
                return jsonify({
                    "status": "error",
                    "message": "Policy not found"
                }), 404

            return jsonify({
                "status": "success",
                "policy": policy.to_dict()
            })

        @app.route("/api/v1/security/policies", methods=["GET"])
        def list_policies():
            """List all policies"""
            owner_id = request.args.get("owner_id")
            policies = self.manager.list_policies(owner_id=owner_id)

            return jsonify({
                "status": "success",
                "count": len(policies),
                "policies": [p.to_dict() for p in policies]
            })

        @app.route("/api/v1/security/policies/<policy_id>", methods=["PUT"])
        def update_policy(policy_id: str):
            """Update a policy"""
            data = request.json
            policy = self.manager.update_policy(policy_id, data)

            if not policy:
                return jsonify({
                    "status": "error",
                    "message": "Policy not found"
                }), 404

            return jsonify({
                "status": "success",
                "policy": policy.to_dict()
            })

        @app.route("/api/v1/security/policies/<policy_id>", methods=["DELETE"])
        def delete_policy(policy_id: str):
            """Delete a policy"""
            success = self.manager.delete_policy(policy_id)

            if not success:
                return jsonify({
                    "status": "error",
                    "message": "Policy not found"
                }), 404

            return jsonify({
                "status": "success",
                "message": f"Policy {policy_id} deleted"
            })

        @app.route("/api/v1/security/threats/scan", methods=["POST"])
        def scan_threat():
            """Scan an agent for nLD threats"""
            data = request.json

            try:
                profile = self.manager.scan_threat(
                    agent_id=data["agent_id"],
                    ld_training_history=data["ld_training_history"],
                    detection_signals=data.get("detection_signals")
                )

                return jsonify({
                    "status": "success",
                    "threat_profile": profile.to_dict()
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 400

        @app.route("/api/v1/security/access/check", methods=["POST"])
        def check_access():
            """Check if an agent can perform an action"""
            data = request.json

            try:
                # Get or create threat profile if LD history provided
                threat_profile = None
                if "ld_training_history" in data:
                    threat_profile = self.manager.scan_threat(
                        agent_id=data["agent_id"],
                        ld_training_history=data["ld_training_history"]
                    )

                allowed, reason = self.manager.check_access(
                    agent_id=data["agent_id"],
                    action=data["action"],
                    policy_id=data["policy_id"],
                    threat_profile=threat_profile
                )

                return jsonify({
                    "status": "success",
                    "allowed": allowed,
                    "reason": reason,
                    "threat_profile": threat_profile.to_dict() if threat_profile else None
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 400

        @app.route("/api/v1/security/hierarchy", methods=["POST"])
        def set_hierarchy():
            """Set node hierarchy"""
            data = request.json

            try:
                self.manager.set_node_hierarchy(
                    node_id=data["node_id"],
                    parent_id=data.get("parent_id"),
                    priority=data.get("priority", 50)
                )

                return jsonify({
                    "status": "success",
                    "message": "Hierarchy updated"
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 400

        @app.route("/api/v1/security/hierarchy/<node_id>", methods=["GET"])
        def get_hierarchy(node_id: str):
            """Get node hierarchy info"""
            priority = self.manager.get_effective_priority(node_id)

            return jsonify({
                "status": "success",
                "node_id": node_id,
                "priority": priority
            })

        @app.route("/api/v1/security/init", methods=["POST"])
        def init_security():
            """Initialize security system"""
            from hypersync.security.policy_manager import create_default_policy

            try:
                default_policy_data = create_default_policy()

                # Check if already exists
                if self.manager.get_policy("system_default"):
                    return jsonify({
                        "status": "success",
                        "message": "Security already initialized"
                    })

                # Create default policy
                policy = self.manager.create_policy(
                    policy_id=default_policy_data["policy_id"],
                    owner_type=default_policy_data["owner"]["type"],
                    owner_id=default_policy_data["owner"]["id"],
                    rules=default_policy_data["rules"],
                    nld_max_score=default_policy_data["nld_protection"]["max_nld_score"],
                    priority=default_policy_data["owner"]["priority"]
                )

                return jsonify({
                    "status": "success",
                    "message": "Security initialized",
                    "default_policy": policy.to_dict()
                }), 201
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 400


def create_security_api_app() -> Flask:
    """Create Flask app with security API"""
    app = Flask(__name__)
    api = SecurityAPI(app)
    return app


if __name__ == "__main__":
    app = create_security_api_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
