"""
HyperSync Redaction Pipeline

Modular sanitization pipeline for agent responses with attestable receipts.
Ensures outputs respect requester clearances when mediated by higher-cleared agents.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class RedactionLevel(Enum):
    """Redaction intensity levels."""
    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    STRICT = "strict"
    COMPLETE = "complete"


@dataclass
class RedactionResult:
    """Result of a redaction operation."""
    original_hash: str
    redacted_hash: str
    redaction_level: RedactionLevel
    filters_applied: List[str]
    items_redacted: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'original_hash': self.original_hash,
            'redacted_hash': self.redacted_hash,
            'redaction_level': self.redaction_level.value,
            'filters_applied': self.filters_applied,
            'items_redacted': self.items_redacted,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat() + 'Z'
        }


class RedactionFilter:
    """Base class for redaction filters."""

    def __init__(self, name: str, config: Optional[Dict] = None):
        """
        Initialize filter.

        Args:
            name: Filter name
            config: Optional configuration
        """
        self.name = name
        self.config = config or {}
        self.items_redacted = 0

    def apply(self, content: str) -> str:
        """
        Apply redaction filter to content.

        Args:
            content: Content to redact

        Returns:
            Redacted content
        """
        raise NotImplementedError("Subclasses must implement apply()")

    def reset_stats(self) -> None:
        """Reset redaction statistics."""
        self.items_redacted = 0


class RedactionPipeline:
    """
    Modular redaction pipeline with attestable receipts.

    Applies a series of filters to sanitize content based on
    clearance levels and policy requirements.
    """

    def __init__(self, filters: Optional[List[RedactionFilter]] = None):
        """
        Initialize redaction pipeline.

        Args:
            filters: List of redaction filters to apply
        """
        self.filters = filters or []
        self.attestation_enabled = True

    @classmethod
    def from_policy(cls, policy: Dict) -> 'RedactionPipeline':
        """
        Create pipeline from policy configuration.

        Args:
            policy: Policy dictionary with redaction config

        Returns:
            Configured RedactionPipeline
        """
        redaction_config = policy.get('redaction', {})
        filter_names = redaction_config.get('filters', [])

        filters = []
        for filter_name in filter_names:
            filter_class = cls._get_filter_class(filter_name)
            if filter_class:
                filters.append(filter_class(filter_name))

        return cls(filters=filters)

    @classmethod
    def from_clearance(cls, source_clearance: str, target_clearance: str) -> 'RedactionPipeline':
        """
        Create pipeline based on clearance levels.

        Args:
            source_clearance: Source clearance level
            target_clearance: Target clearance level

        Returns:
            Configured RedactionPipeline
        """
        from hypersync.agents.redaction.filters import (
            PIIFilter, ClassificationFilter, SecretsFilter, InternalRefsFilter
        )

        filters = []

        # Always apply PII filter
        filters.append(PIIFilter('pii'))

        # Add filters based on clearance gap
        clearance_order = ['public', 'internal', 'restricted', 'confidential', 'secret']
        source_idx = clearance_order.index(source_clearance.lower())
        target_idx = clearance_order.index(target_clearance.lower())

        if target_idx <= clearance_order.index('public'):
            filters.extend([
                InternalRefsFilter('internal-refs'),
                ClassificationFilter('classification'),
                SecretsFilter('secrets')
            ])
        elif target_idx <= clearance_order.index('internal'):
            filters.extend([
                ClassificationFilter('classification'),
                SecretsFilter('secrets')
            ])
        elif target_idx <= clearance_order.index('restricted'):
            filters.append(SecretsFilter('secrets'))

        return cls(filters=filters)

    @staticmethod
    def _get_filter_class(filter_name: str) -> Optional[type]:
        """Get filter class by name."""
        from hypersync.agents.redaction.filters import (
            PIIFilter, ClassificationFilter, SecretsFilter, InternalRefsFilter
        )

        filter_map = {
            'pii': PIIFilter,
            'classification': ClassificationFilter,
            'secrets': SecretsFilter,
            'internal-refs': InternalRefsFilter
        }

        return filter_map.get(filter_name)

    def scrub(self, content: str, requester_clearance: str,
             metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Scrub content through redaction pipeline.

        Args:
            content: Content to redact
            requester_clearance: Target clearance level
            metadata: Optional metadata to include in result

        Returns:
            Dictionary with redacted content and attestation
        """
        # Calculate original hash
        original_hash = self._hash_content(content)

        # Reset filter stats
        for filter in self.filters:
            filter.reset_stats()

        # Apply filters sequentially
        redacted_content = content
        filters_applied = []
        total_items_redacted = 0

        for filter in self.filters:
            logger.debug(f"Applying filter: {filter.name}")
            redacted_content = filter.apply(redacted_content)
            filters_applied.append(filter.name)
            total_items_redacted += filter.items_redacted

        # Calculate redacted hash
        redacted_hash = self._hash_content(redacted_content)

        # Determine redaction level
        redaction_level = self._determine_redaction_level(total_items_redacted)

        # Create result
        result = RedactionResult(
            original_hash=original_hash,
            redacted_hash=redacted_hash,
            redaction_level=redaction_level,
            filters_applied=filters_applied,
            items_redacted=total_items_redacted,
            metadata=metadata or {}
        )

        # Generate attestation if enabled
        attestation = None
        if self.attestation_enabled:
            attestation = self._generate_attestation(result)

        return {
            'content': redacted_content,
            'result': result.to_dict(),
            'attestation': attestation
        }

    def _hash_content(self, content: str) -> str:
        """Calculate SHA256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _determine_redaction_level(self, items_redacted: int) -> RedactionLevel:
        """Determine redaction level based on items redacted."""
        if items_redacted == 0:
            return RedactionLevel.NONE
        elif items_redacted <= 5:
            return RedactionLevel.MINIMAL
        elif items_redacted <= 20:
            return RedactionLevel.MODERATE
        elif items_redacted <= 50:
            return RedactionLevel.STRICT
        else:
            return RedactionLevel.COMPLETE

    def _generate_attestation(self, result: RedactionResult) -> Dict[str, Any]:
        """
        Generate cryptographic attestation for redaction.

        Args:
            result: Redaction result

        Returns:
            Attestation dictionary
        """
        # Create attestation payload
        payload = {
            'original_hash': result.original_hash,
            'redacted_hash': result.redacted_hash,
            'filters_applied': result.filters_applied,
            'items_redacted': result.items_redacted,
            'timestamp': result.timestamp.isoformat() + 'Z'
        }

        # Calculate attestation signature (simplified - use proper crypto in production)
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

        return {
            'payload': payload,
            'signature': signature,
            'algorithm': 'sha256',
            'version': '1.0'
        }

    def add_filter(self, filter: RedactionFilter) -> None:
        """Add a filter to the pipeline."""
        self.filters.append(filter)

    def remove_filter(self, filter_name: str) -> None:
        """Remove a filter from the pipeline."""
        self.filters = [f for f in self.filters if f.name != filter_name]

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            'filter_count': len(self.filters),
            'filters': [
                {
                    'name': f.name,
                    'items_redacted': f.items_redacted
                }
                for f in self.filters
            ]
        }
