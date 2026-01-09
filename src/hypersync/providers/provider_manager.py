"""
Provider Manager

Manages external model providers and credentials.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)


@dataclass
class ModelProvider:
    """Represents an external model provider"""
    provider_id: str
    name: str
    provider_type: str
    created_at: str
    description: Optional[str] = None
    endpoint: Optional[Dict] = None
    authentication: Optional[Dict] = None
    capabilities: Optional[List[str]] = None
    models: Optional[List[Dict]] = None
    rate_limits: Optional[Dict] = None
    retry_config: Optional[Dict] = None
    status: str = "active"
    health: Optional[Dict] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None


@dataclass
class Credential:
    """Represents an encrypted credential"""
    credential_id: str
    provider_type: str
    encrypted_value: str
    created_at: str
    name: Optional[str] = None
    credential_type: str = "api_key"
    encryption_method: str = "fernet"
    key_id: Optional[str] = None
    expires_at: Optional[str] = None
    scopes: Optional[List[str]] = None
    status: str = "active"
    last_used: Optional[str] = None
    created_by: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class ExternalModel:
    """Represents an external model reference"""
    model_id: str
    provider_id: str
    external_model_id: str
    display_name: Optional[str] = None
    model_type: Optional[str] = None
    capabilities: Optional[List[str]] = None
    parameters: Optional[Dict] = None
    pricing: Optional[Dict] = None
    default_config: Optional[Dict] = None
    catalogue_entry: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None


class ProviderManager:
    """Manages external model providers and credentials"""

    def __init__(self, db_path: str = "providers.db", encryption_key: Optional[bytes] = None):
        self.db_path = db_path

        # Initialize encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            # Generate a key (in production, this should be stored securely)
            self.cipher = Fernet(Fernet.generate_key())

        self._init_db()

    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Providers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS providers (
                provider_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                provider_type TEXT NOT NULL,
                endpoint TEXT,
                authentication TEXT,
                capabilities TEXT,
                models TEXT,
                rate_limits TEXT,
                retry_config TEXT,
                status TEXT NOT NULL,
                health TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                created_by TEXT,
                tags TEXT,
                metadata TEXT
            )
        """)

        # Credentials table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                credential_id TEXT PRIMARY KEY,
                name TEXT,
                provider_type TEXT NOT NULL,
                credential_type TEXT NOT NULL,
                encrypted_value TEXT NOT NULL,
                encryption_method TEXT NOT NULL,
                key_id TEXT,
                expires_at TEXT,
                scopes TEXT,
                status TEXT NOT NULL,
                last_used TEXT,
                created_at TEXT NOT NULL,
                created_by TEXT,
                metadata TEXT
            )
        """)

        # External models table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS external_models (
                model_id TEXT PRIMARY KEY,
                provider_id TEXT NOT NULL,
                external_model_id TEXT NOT NULL,
                display_name TEXT,
                model_type TEXT,
                capabilities TEXT,
                parameters TEXT,
                pricing TEXT,
                default_config TEXT,
                catalogue_entry TEXT,
                created_at TEXT,
                updated_at TEXT,
                tags TEXT,
                metadata TEXT,
                FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
            )
        """)

        # Indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_providers_type ON providers(provider_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_providers_status ON providers(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_credentials_type ON credentials(provider_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_external_models_provider ON external_models(provider_id)")

        conn.commit()
        conn.close()

    # ========================================================================
    # Provider Operations
    # ========================================================================

    def create_provider(
        self,
        name: str,
        provider_type: str,
        description: Optional[str] = None,
        endpoint: Optional[Dict] = None,
        credential_id: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        rate_limits: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> ModelProvider:
        """Create a new model provider"""
        provider_id = f"provider-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        authentication = None
        if credential_id:
            authentication = {
                "method": "api_key",
                "credential_id": credential_id,
                "encrypted": True
            }

        provider = ModelProvider(
            provider_id=provider_id,
            name=name,
            description=description,
            provider_type=provider_type,
            endpoint=endpoint or {},
            authentication=authentication,
            capabilities=capabilities or [],
            models=[],
            rate_limits=rate_limits or {},
            retry_config={"max_retries": 3, "backoff_factor": 2.0, "timeout_seconds": 60},
            status="active",
            created_at=now,
            updated_at=now,
            tags=tags or [],
            metadata=metadata or {}
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO providers (
                provider_id, name, description, provider_type, endpoint,
                authentication, capabilities, models, rate_limits, retry_config,
                status, created_at, updated_at, tags, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            provider.provider_id,
            provider.name,
            provider.description,
            provider.provider_type,
            json.dumps(provider.endpoint),
            json.dumps(provider.authentication) if provider.authentication else None,
            json.dumps(provider.capabilities),
            json.dumps(provider.models),
            json.dumps(provider.rate_limits),
            json.dumps(provider.retry_config),
            provider.status,
            provider.created_at,
            provider.updated_at,
            json.dumps(provider.tags),
            json.dumps(provider.metadata)
        ))

        conn.commit()
        conn.close()

        logger.info(f"Created provider: {provider_id} ({name})")
        return provider

    def get_provider(self, provider_id: str) -> Optional[ModelProvider]:
        """Get a provider by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM providers WHERE provider_id = ?", (provider_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_provider(row)

    def list_providers(
        self,
        provider_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[ModelProvider]:
        """List providers with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM providers WHERE 1=1"
        params = []

        if provider_type:
            query += " AND provider_type = ?"
            params.append(provider_type)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_provider(row) for row in rows]

    def update_provider_health(self, provider_id: str, health: Dict):
        """Update provider health status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE providers
            SET health = ?, updated_at = ?
            WHERE provider_id = ?
        """, (json.dumps(health), datetime.utcnow().isoformat() + "Z", provider_id))

        conn.commit()
        conn.close()

    def delete_provider(self, provider_id: str):
        """Delete a provider"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if provider has external models
        cursor.execute("SELECT COUNT(*) FROM external_models WHERE provider_id = ?", (provider_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            conn.close()
            raise ValueError(f"Provider has {count} external models. Cannot delete.")

        cursor.execute("DELETE FROM providers WHERE provider_id = ?", (provider_id,))
        conn.commit()
        conn.close()

        logger.info(f"Deleted provider: {provider_id}")

    # ========================================================================
    # Credential Operations
    # ========================================================================

    def create_credential(
        self,
        name: str,
        provider_type: str,
        value: str,
        credential_type: str = "api_key",
        expires_at: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Credential:
        """Create a new encrypted credential"""
        credential_id = f"cred-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        # Encrypt the value
        encrypted_value = self.cipher.encrypt(value.encode()).decode()

        credential = Credential(
            credential_id=credential_id,
            name=name,
            provider_type=provider_type,
            credential_type=credential_type,
            encrypted_value=encrypted_value,
            encryption_method="fernet",
            expires_at=expires_at,
            scopes=scopes or [],
            status="active",
            created_at=now,
            metadata=metadata or {}
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO credentials (
                credential_id, name, provider_type, credential_type,
                encrypted_value, encryption_method, expires_at, scopes,
                status, created_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            credential.credential_id,
            credential.name,
            credential.provider_type,
            credential.credential_type,
            credential.encrypted_value,
            credential.encryption_method,
            credential.expires_at,
            json.dumps(credential.scopes),
            credential.status,
            credential.created_at,
            json.dumps(credential.metadata)
        ))

        conn.commit()
        conn.close()

        logger.info(f"Created credential: {credential_id} ({name})")
        return credential

    def get_credential(self, credential_id: str, decrypt: bool = False) -> Optional[Credential]:
        """Get a credential by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM credentials WHERE credential_id = ?", (credential_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        credential = self._row_to_credential(row)

        if decrypt:
            # Decrypt the value
            decrypted = self.cipher.decrypt(credential.encrypted_value.encode()).decode()
            credential.encrypted_value = decrypted

        return credential

    def list_credentials(
        self,
        provider_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Credential]:
        """List credentials (encrypted)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM credentials WHERE 1=1"
        params = []

        if provider_type:
            query += " AND provider_type = ?"
            params.append(provider_type)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_credential(row) for row in rows]

    def revoke_credential(self, credential_id: str):
        """Revoke a credential"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE credentials
            SET status = 'revoked'
            WHERE credential_id = ?
        """, (credential_id,))

        conn.commit()
        conn.close()

        logger.info(f"Revoked credential: {credential_id}")

    # ========================================================================
    # External Model Operations
    # ========================================================================

    def register_external_model(
        self,
        provider_id: str,
        external_model_id: str,
        display_name: str,
        model_type: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        parameters: Optional[Dict] = None,
        pricing: Optional[Dict] = None,
        default_config: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> ExternalModel:
        """Register an external model"""
        # Verify provider exists
        provider = self.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Provider not found: {provider_id}")

        model_id = f"ext-model-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        model = ExternalModel(
            model_id=model_id,
            provider_id=provider_id,
            external_model_id=external_model_id,
            display_name=display_name,
            model_type=model_type,
            capabilities=capabilities or [],
            parameters=parameters or {},
            pricing=pricing or {},
            default_config=default_config or {},
            created_at=now,
            updated_at=now,
            tags=tags or [],
            metadata=metadata or {}
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO external_models (
                model_id, provider_id, external_model_id, display_name,
                model_type, capabilities, parameters, pricing, default_config,
                created_at, updated_at, tags, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            model.model_id,
            model.provider_id,
            model.external_model_id,
            model.display_name,
            model.model_type,
            json.dumps(model.capabilities),
            json.dumps(model.parameters),
            json.dumps(model.pricing),
            json.dumps(model.default_config),
            model.created_at,
            model.updated_at,
            json.dumps(model.tags),
            json.dumps(model.metadata)
        ))

        conn.commit()
        conn.close()

        logger.info(f"Registered external model: {model_id} ({display_name})")
        return model

    def get_external_model(self, model_id: str) -> Optional[ExternalModel]:
        """Get an external model by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM external_models WHERE model_id = ?", (model_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_external_model(row)

    def list_external_models(
        self,
        provider_id: Optional[str] = None,
        model_type: Optional[str] = None,
        limit: int = 100
    ) -> List[ExternalModel]:
        """List external models"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM external_models WHERE 1=1"
        params = []

        if provider_id:
            query += " AND provider_id = ?"
            params.append(provider_id)

        if model_type:
            query += " AND model_type = ?"
            params.append(model_type)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_external_model(row) for row in rows]

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _row_to_provider(self, row) -> ModelProvider:
        """Convert database row to ModelProvider"""
        return ModelProvider(
            provider_id=row[0],
            name=row[1],
            description=row[2],
            provider_type=row[3],
            endpoint=json.loads(row[4]) if row[4] else {},
            authentication=json.loads(row[5]) if row[5] else None,
            capabilities=json.loads(row[6]) if row[6] else [],
            models=json.loads(row[7]) if row[7] else [],
            rate_limits=json.loads(row[8]) if row[8] else {},
            retry_config=json.loads(row[9]) if row[9] else {},
            status=row[10],
            health=json.loads(row[11]) if row[11] else None,
            created_at=row[12],
            updated_at=row[13],
            created_by=row[14],
            tags=json.loads(row[15]) if row[15] else [],
            metadata=json.loads(row[16]) if row[16] else {}
        )

    def _row_to_credential(self, row) -> Credential:
        """Convert database row to Credential"""
        return Credential(
            credential_id=row[0],
            name=row[1],
            provider_type=row[2],
            credential_type=row[3],
            encrypted_value=row[4],
            encryption_method=row[5],
            key_id=row[6],
            expires_at=row[7],
            scopes=json.loads(row[8]) if row[8] else [],
            status=row[9],
            last_used=row[10],
            created_at=row[11],
            created_by=row[12],
            metadata=json.loads(row[13]) if row[13] else {}
        )

    def _row_to_external_model(self, row) -> ExternalModel:
        """Convert database row to ExternalModel"""
        return ExternalModel(
            model_id=row[0],
            provider_id=row[1],
            external_model_id=row[2],
            display_name=row[3],
            model_type=row[4],
            capabilities=json.loads(row[5]) if row[5] else [],
            parameters=json.loads(row[6]) if row[6] else {},
            pricing=json.loads(row[7]) if row[7] else {},
            default_config=json.loads(row[8]) if row[8] else {},
            catalogue_entry=row[9],
            created_at=row[10],
            updated_at=row[11],
            tags=json.loads(row[12]) if row[12] else [],
            metadata=json.loads(row[13]) if row[13] else {}
        )
