"""
Document Store - JSON document storage with schema inference.

Provides flexible document storage with automatic schema inference,
query DSL, and MongoDB adapter compatibility.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class DocumentSchema:
    """Inferred document schema."""
    collection: str
    fields: Dict[str, str]  # field_name -> type
    sample_count: int


class DocumentStore:
    """
    Document-oriented storage engine.

    Stores JSON documents with automatic schema inference and
    flexible query capabilities.
    """

    def __init__(self):
        self.collections: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)  # collection -> doc_id -> document
        self.schemas: Dict[str, DocumentSchema] = {}
        self.indices: Dict[str, Dict[str, Dict[Any, List[str]]]] = defaultdict(lambda: defaultdict(dict))  # collection -> field -> value -> doc_ids

    def insert(self, collection: str, doc_id: str, document: Dict[str, Any]) -> None:
        """
        Insert document into collection.

        Args:
            collection: Collection name
            doc_id: Document identifier
            document: Document data
        """
        self.collections[collection][doc_id] = document

        # Update schema
        self._update_schema(collection, document)

        # Update indices
        for field, value in document.items():
            if isinstance(value, (str, int, float, bool)):
                self.indices[collection][field][value].append(doc_id)

    def find(self, collection: str, query: Optional[Dict[str, Any]] = None,
            limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find documents matching query.

        Args:
            collection: Collection name
            query: Query filter (None for all documents)
            limit: Maximum results

        Returns:
            List of matching documents
        """
        if collection not in self.collections:
            return []

        documents = list(self.collections[collection].values())

        if query:
            documents = [doc for doc in documents if self._matches_query(doc, query)]

        return documents[:limit]

    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find single document matching query.

        Args:
            collection: Collection name
            query: Query filter

        Returns:
            Matching document or None
        """
        results = self.find(collection, query, limit=1)
        return results[0] if results else None

    def update(self, collection: str, doc_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update document.

        Args:
            collection: Collection name
            doc_id: Document identifier
            updates: Field updates

        Returns:
            True if updated successfully
        """
        if collection not in self.collections or doc_id not in self.collections[collection]:
            return False

        document = self.collections[collection][doc_id]
        document.update(updates)

        # Update schema
        self._update_schema(collection, document)

        return True

    def delete(self, collection: str, doc_id: str) -> bool:
        """
        Delete document.

        Args:
            collection: Collection name
            doc_id: Document identifier

        Returns:
            True if deleted successfully
        """
        if collection not in self.collections or doc_id not in self.collections[collection]:
            return False

        del self.collections[collection][doc_id]
        return True

    def get_schema(self, collection: str) -> Optional[DocumentSchema]:
        """Get inferred schema for collection."""
        return self.schemas.get(collection)

    def _update_schema(self, collection: str, document: Dict[str, Any]) -> None:
        """Update schema based on document."""
        if collection not in self.schemas:
            self.schemas[collection] = DocumentSchema(
                collection=collection,
                fields={},
                sample_count=0
            )

        schema = self.schemas[collection]
        schema.sample_count += 1

        for field, value in document.items():
            field_type = type(value).__name__

            if field not in schema.fields:
                schema.fields[field] = field_type
            elif schema.fields[field] != field_type:
                schema.fields[field] = "mixed"

    def _matches_query(self, document: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if document matches query."""
        for field, condition in query.items():
            if field not in document:
                return False

            doc_value = document[field]

            if isinstance(condition, dict):
                # Operator query (e.g., {"$gt": 10})
                for op, value in condition.items():
                    if op == "$gt" and not (doc_value > value):
                        return False
                    elif op == "$lt" and not (doc_value < value):
                        return False
                    elif op == "$gte" and not (doc_value >= value):
                        return False
                    elif op == "$lte" and not (doc_value <= value):
                        return False
                    elif op == "$ne" and not (doc_value != value):
                        return False
            else:
                # Equality query
                if doc_value != condition:
                    return False

        return True

    def get_stats(self, collection: str) -> Dict[str, Any]:
        """Get collection statistics."""
        if collection not in self.collections:
            return {}

        return {
            "num_documents": len(self.collections[collection]),
            "schema": self.schemas.get(collection),
            "indexed_fields": list(self.indices[collection].keys())
        }
