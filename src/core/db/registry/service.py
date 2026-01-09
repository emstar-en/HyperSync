"""
Public Registry Service

Provides signed metadata service for published datasets with REST endpoints.
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass
class DatasetMetadata:
    """Metadata for published dataset."""
    dataset_id: str
    name: str
    description: str
    owner: str
    version: str
    schema: dict
    curvature: float
    size_bytes: int
    record_count: int
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    signature: Optional[str] = None

    def sign(self, private_key: str):
        """Sign metadata."""
        # Simplified signing
        content = json.dumps(self.to_dict(), sort_keys=True)
        self.signature = hashlib.sha256((content + private_key).encode()).hexdigest()

    def verify(self, public_key: str) -> bool:
        """Verify signature."""
        if not self.signature:
            return False

        # Simplified verification
        content = json.dumps(self.to_dict(), sort_keys=True)
        expected = hashlib.sha256((content + public_key).encode()).hexdigest()
        return self.signature == expected

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'dataset_id': self.dataset_id,
            'name': self.name,
            'description': self.description,
            'owner': self.owner,
            'version': self.version,
            'schema': self.schema,
            'curvature': self.curvature,
            'size_bytes': self.size_bytes,
            'record_count': self.record_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': self.tags
        }


class RegistryService:
    """
    Public registry for datasets.

    Provides signed metadata service with REST endpoints.
    """

    def __init__(self):
        self._datasets: Dict[str, DatasetMetadata] = {}
        self._index: Dict[str, List[str]] = {}  # tag -> dataset_ids

    def publish_dataset(self, metadata: DatasetMetadata, private_key: str) -> str:
        """
        Publish dataset to registry.

        Args:
            metadata: Dataset metadata
            private_key: Private key for signing

        Returns:
            Dataset ID
        """
        # Sign metadata
        metadata.sign(private_key)

        # Store
        self._datasets[metadata.dataset_id] = metadata

        # Index tags
        for tag in metadata.tags:
            if tag not in self._index:
                self._index[tag] = []
            self._index[tag].append(metadata.dataset_id)

        logger.info(f"Published dataset: {metadata.dataset_id}")

        return metadata.dataset_id

    def get_dataset(self, dataset_id: str) -> Optional[DatasetMetadata]:
        """Get dataset metadata."""
        return self._datasets.get(dataset_id)

    def search_datasets(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        owner: Optional[str] = None
    ) -> List[DatasetMetadata]:
        """
        Search datasets.

        Args:
            query: Text query
            tags: Filter by tags
            owner: Filter by owner

        Returns:
            Matching datasets
        """
        results = list(self._datasets.values())

        # Filter by tags
        if tags:
            tag_matches = set()
            for tag in tags:
                tag_matches.update(self._index.get(tag, []))
            results = [d for d in results if d.dataset_id in tag_matches]

        # Filter by owner
        if owner:
            results = [d for d in results if d.owner == owner]

        # Filter by query
        if query:
            query_lower = query.lower()
            results = [
                d for d in results
                if query_lower in d.name.lower() or query_lower in d.description.lower()
            ]

        return results

    def update_dataset(self, dataset_id: str, updates: dict, private_key: str):
        """Update dataset metadata."""
        dataset = self._datasets.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset not found: {dataset_id}")

        # Apply updates
        for key, value in updates.items():
            if hasattr(dataset, key):
                setattr(dataset, key, value)

        dataset.updated_at = datetime.now()

        # Re-sign
        dataset.sign(private_key)

        logger.info(f"Updated dataset: {dataset_id}")

    def delete_dataset(self, dataset_id: str):
        """Delete dataset from registry."""
        if dataset_id in self._datasets:
            dataset = self._datasets[dataset_id]

            # Remove from index
            for tag in dataset.tags:
                if tag in self._index:
                    self._index[tag].remove(dataset_id)

            del self._datasets[dataset_id]
            logger.info(f"Deleted dataset: {dataset_id}")

    # REST API endpoints (simplified)
    def handle_post_dataset(self, request_body: dict) -> dict:
        """POST /registry/datasets"""
        metadata = DatasetMetadata(**request_body['metadata'])
        private_key = request_body['private_key']

        dataset_id = self.publish_dataset(metadata, private_key)

        return {'dataset_id': dataset_id, 'status': 'published'}

    def handle_get_dataset(self, dataset_id: str) -> dict:
        """GET /registry/datasets/{id}"""
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            return {'error': 'Dataset not found'}, 404

        return dataset.to_dict()

    def handle_search(self, params: dict) -> dict:
        """GET /registry/search"""
        results = self.search_datasets(
            query=params.get('q'),
            tags=params.get('tags', '').split(',') if params.get('tags') else None,
            owner=params.get('owner')
        )

        return {
            'results': [d.to_dict() for d in results],
            'count': len(results)
        }


__all__ = ['RegistryService', 'DatasetMetadata']
