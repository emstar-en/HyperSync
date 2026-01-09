"""
HyperSync Initialization Assistant - HTTP API

Flask blueprint providing REST API for the assistant.
"""

from flask import Blueprint, request, jsonify
from hypersync.assistant.runtime import AssistantRuntime
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Create blueprint
assistant_api = Blueprint("assistant_api", __name__, url_prefix="/api/v1/assistant")

# Initialize runtime (singleton)
runtime = AssistantRuntime()

# Simple in-memory session store (replace with persistent store in production)
sessions = {}


@assistant_api.route("/message", methods=["POST"])
def message():
    """
    Send a message to the assistant and get a response.

    Request:
        {
            "text": str (required),
            "context": dict (optional),
            "session_id": str (optional)
        }

    Response:
        {
            "status": "ok",
            "reply": str,
            "actions": List[dict],
            "suggestions": List[str],
            "session_id": str,
            "timestamp": str
        }
    """
    try:
        data = request.get_json(force=True) or {}

        # Validate required fields
        if "text" not in data or not data["text"]:
            return jsonify({
                "status": "error",
                "error": "Missing required field: text"
            }), 400

        text = data["text"]
        session_id = data.get("session_id") or str(uuid.uuid4())

        # Get or create session context
        if session_id not in sessions:
            sessions[session_id] = {
                "created_at": datetime.utcnow().isoformat(),
                "context": {}
            }

        ctx = sessions[session_id]["context"]
        ctx.update(data.get("context", {}))

        # Generate response
        res = runtime.respond(text, ctx)

        # Update session
        sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()

        logger.info(f"Session {session_id}: {text[:50]}... -> {res['reply'][:50]}...")

        return jsonify({
            "status": "ok",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            **res
        })

    except Exception as e:
        logger.error(f"Message handling failed: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@assistant_api.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id: str):
    """
    Get session information.

    Response:
        {
            "status": "ok",
            "session_id": str,
            "created_at": str,
            "last_activity": str,
            "context": dict
        }
    """
    if session_id not in sessions:
        return jsonify({
            "status": "error",
            "error": "Session not found"
        }), 404

    session = sessions[session_id]

    return jsonify({
        "status": "ok",
        "session_id": session_id,
        "created_at": session["created_at"],
        "last_activity": session.get("last_activity", session["created_at"]),
        "context": session["context"]
    })


@assistant_api.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id: str):
    """
    Delete a session.

    Response:
        {
            "status": "ok",
            "message": "Session deleted"
        }
    """
    if session_id in sessions:
        del sessions[session_id]
        logger.info(f"Deleted session {session_id}")

    return jsonify({
        "status": "ok",
        "message": "Session deleted"
    })


@assistant_api.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.

    Response:
        {
            "status": "ok",
            "service": "initialization_assistant",
            "version": "1.0.0"
        }
    """
    return jsonify({
        "status": "ok",
        "service": "initialization_assistant",
        "version": "1.0.0",
        "active_sessions": len(sessions)
    })
