"""
Embedding Warehouse - Centralized embedding storage with versioning.

Provides centralized embedding storage, versioning, metadata management,
quantization pipelines, and tenancy-aware access controls.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import struct


class QuantizationType(Enum):
    """Embedding quantization types."""
    NONE = "none"
    INT8 = "int8"
    BINARY = "binary"


@dataclass
class EmbeddingMetadata:
    """Embedding metadata."""
    embedding_id: str
    entity_id: str
    model: str
    version: str
    dimension: int
    quantization: QuantizationType
    created_at: datetime
    tenant_id: str
    tags: Dict[str, str]


class EmbeddingWarehouse:
    """
    Centralized embedding storage with versioning and quantization.

    Manages embeddings across tenants with version control, metadata,
    and efficient storage through quantization.
    """

    def __init__(self):
        self.embeddings: Dict[str, List[float]] = {}
        self.metadata: Dict[str, EmbeddingMetadata] = {}
        self.quantized: Dict[str, bytes] = {}
        self.tenant_index: Dict[str, List[str]] = {}  # tenant_id -> embedding_ids
        self.version_index: Dict[str, Dict[str, str]] = {}  # entity_id -> version -> embedding_id

    def store(self, entity_id: str, embedding: List[float],
             model: str, version: str, tenant_id: str,
             quantization: QuantizationType = QuantizationType.NONE,
             tags: Optional[Dict[str, str]] = None) -> str:
        """
        Store embedding with metadata.

        Args:
            entity_id: Entity identifier
            embedding: Embedding vector
            model: Model name
            version: Model version
            tenant_id: Tenant identifier
            quantization: Quantization type
            tags: Optional tags

        Returns:
            Embedding ID
        """
        embedding_id = f"{tenant_id}_{entity_id}_{model}_{version}"

        # Store embedding
        self.embeddings[embedding_id] = embedding

        # Store metadata
        metadata = EmbeddingMetadata(
            embedding_id=embedding_id,
            entity_id=entity_id,
            model=model,
            version=version,
            dimension=len(embedding),
            quantization=quantization,
            created_at=datetime.now(),
            tenant_id=tenant_id,
            tags=tags or {}
        )
        self.metadata[embedding_id] = metadata

        # Quantize if requested
        if quantization != QuantizationType.NONE:
            self.quantized[embedding_id] = self._quantize(embedding, quantization)

        # Update indices
        if tenant_id not in self.tenant_index:
            self.tenant_index[tenant_id] = []
        self.tenant_index[tenant_id].append(embedding_id)

        if entity_id not in self.version_index:
            self.version_index[entity_id] = {}
        self.version_index[entity_id][version] = embedding_id

        return embedding_id

    def retrieve(self, embedding_id: str, tenant_id: str) -> Optional[List[float]]:
        """
        Retrieve embedding with access control.

        Args:
            embedding_id: Embedding identifier
            tenant_id: Requesting tenant ID

        Returns:
            Embedding vector or None
        """
        if embedding_id not in self.metadata:
            return None

        metadata = self.metadata[embedding_id]

        # Check tenant access
        if metadata.tenant_id != tenant_id:
            return None

        # Return quantized or full precision
        if metadata.quantization != QuantizationType.NONE and embedding_id in self.quantized:
            return self._dequantize(self.quantized[embedding_id], metadata.quantization, metadata.dimension)

        return self.embeddings.get(embedding_id)

    def list_versions(self, entity_id: str, tenant_id: str) -> List[str]:
        """
        List all versions for entity.

        Args:
            entity_id: Entity identifier
            tenant_id: Tenant identifier

        Returns:
            List of version strings
        """
        if entity_id not in self.version_index:
            return []

        versions = []
        for version, embedding_id in self.version_index[entity_id].items():
            metadata = self.metadata.get(embedding_id)
            if metadata and metadata.tenant_id == tenant_id:
                versions.append(version)

        return versions

    def search_by_tags(self, tags: Dict[str, str], tenant_id: str) -> List[str]:
        """
        Search embeddings by tags.

        Args:
            tags: Tag filters
            tenant_id: Tenant identifier

        Returns:
            List of matching embedding IDs
        """
        matches = []

        for embedding_id in self.tenant_index.get(tenant_id, []):
            metadata = self.metadata[embedding_id]

            if all(metadata.tags.get(k) == v for k, v in tags.items()):
                matches.append(embedding_id)

        return matches

    def get_storage_stats(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get storage statistics.

        Args:
            tenant_id: Optional tenant filter

        Returns:
            Storage statistics
        """
        if tenant_id:
            embedding_ids = self.tenant_index.get(tenant_id, [])
        else:
            embedding_ids = list(self.embeddings.keys())

        total_bytes = 0
        quantized_bytes = 0

        for embedding_id in embedding_ids:
            if embedding_id in self.embeddings:
                total_bytes += len(self.embeddings[embedding_id]) * 4  # float32

            if embedding_id in self.quantized:
                quantized_bytes += len(self.quantized[embedding_id])

        return {
            "num_embeddings": len(embedding_ids),
            "total_bytes": total_bytes,
            "quantized_bytes": quantized_bytes,
            "compression_ratio": total_bytes / max(quantized_bytes, 1)
        }

    def _quantize(self, embedding: List[float], quantization: QuantizationType) -> bytes:
        """Quantize embedding to reduce storage."""
        if quantization == QuantizationType.INT8:
            # Scale to int8 range
            min_val = min(embedding)
            max_val = max(embedding)
            scale = 255.0 / (max_val - min_val) if max_val != min_val else 1.0

            quantized = [int((v - min_val) * scale) for v in embedding]

            # Pack as bytes with scale and offset
            data = struct.pack('ff', min_val, scale)
            data += bytes(quantized)
            return data

        elif quantization == QuantizationType.BINARY:
            # Binary quantization (sign bit)
            bits = [1 if v > 0 else 0 for v in embedding]

            # Pack bits into bytes
            data = bytearray()
            for i in range(0, len(bits), 8):
                byte = 0
                for j in range(8):
                    if i + j < len(bits) and bits[i + j]:
                        byte |= (1 << j)
                data.append(byte)

            return bytes(data)

        return b''

    def _dequantize(self, data: bytes, quantization: QuantizationType, dimension: int) -> List[float]:
        """Dequantize embedding."""
        if quantization == QuantizationType.INT8:
            # Unpack scale and offset
            min_val, scale = struct.unpack('ff', data[:8])
            quantized = list(data[8:])

            # Dequantize
            return [min_val + (v / scale) for v in quantized]

        elif quantization == QuantizationType.BINARY:
            # Unpack bits
            bits = []
            for byte in data:
                for j in range(8):
                    bits.append(1.0 if (byte & (1 << j)) else -1.0)

            return bits[:dimension]

        return []
