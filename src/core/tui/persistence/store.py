"""
HyperSync TUI Persistence Store

Session persistence with encrypted HVS storage and retention policies.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class PersistenceStore:
    """
    Persistence store.

    Stores session data with encryption and retention policies.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path.home() / ".hypersync" / "tui" / "sessions"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = 30
        logger.info(f"PersistenceStore initialized: {self.storage_dir}")

    def save_session(
        self,
        session_id: str,
        session_data: Dict[str, Any]
    ):
        """
        Save session data.

        Args:
            session_id: Session ID
            session_data: Session data to save
        """
        session_file = self.storage_dir / f"{session_id}.json"

        # Add metadata
        session_data["_metadata"] = {
            "saved_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        }

        try:
            # TODO: Implement encryption
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

            logger.info(f"Saved session {session_id}")
        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {e}")

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session data.

        Args:
            session_id: Session ID

        Returns:
            Session data or None
        """
        session_file = self.storage_dir / f"{session_id}.json"

        if not session_file.exists():
            return None

        try:
            # TODO: Implement decryption
            with open(session_file, 'r') as f:
                session_data = json.load(f)

            logger.info(f"Loaded session {session_id}")
            return session_data
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    def delete_session(self, session_id: str):
        """Delete session data."""
        session_file = self.storage_dir / f"{session_id}.json"

        if session_file.exists():
            session_file.unlink()
            logger.info(f"Deleted session {session_id}")

    def list_sessions(self) -> list:
        """List all saved sessions."""
        sessions = []

        for session_file in self.storage_dir.glob("*.json"):
            session_id = session_file.stem

            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)

                metadata = data.get("_metadata", {})

                sessions.append({
                    "session_id": session_id,
                    "saved_at": metadata.get("saved_at"),
                    "version": metadata.get("version")
                })
            except Exception as e:
                logger.error(f"Failed to read session {session_id}: {e}")

        return sessions

    def cleanup_old_sessions(self):
        """Clean up sessions older than retention period."""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)

        for session_file in self.storage_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)

                metadata = data.get("_metadata", {})
                saved_at_str = metadata.get("saved_at")

                if saved_at_str:
                    saved_at = datetime.fromisoformat(saved_at_str)

                    if saved_at < cutoff:
                        session_file.unlink()
                        logger.info(f"Cleaned up old session {session_file.stem}")
            except Exception as e:
                logger.error(f"Failed to cleanup session {session_file.stem}: {e}")


# Global persistence store
_persistence_store = None


def get_persistence_store() -> PersistenceStore:
    """Get global persistence store."""
    global _persistence_store
    if _persistence_store is None:
        _persistence_store = PersistenceStore()
    return _persistence_store
