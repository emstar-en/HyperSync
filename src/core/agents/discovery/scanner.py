"""
Autonomous Discovery Scanner - Survey registries and mounts for agent capabilities.

Computes relevance scores, negotiates permissions, and persists capability
manifests for audit and reuse.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio


@dataclass
class CapabilityManifest:
    """Agent capability manifest."""
    agent_id: str
    capabilities: List[str]
    permissions: Dict[str, List[str]]
    discovered_at: datetime
    metadata: Dict[str, Any]


@dataclass
class DiscoveryResult:
    """Result of discovery scan."""
    resources: List[Dict[str, Any]]
    relevance_scores: Dict[str, float]
    permissions_granted: Dict[str, List[str]]


class AutonomousScanner:
    """
    Autonomous discovery scanner for agent capabilities.

    Surveys available registries and mounts, computes relevance scores,
    and negotiates access permissions.
    """

    def __init__(self, registry_urls: List[str]):
        self.registry_urls = registry_urls
        self.capability_cache = {}
        self.permission_cache = {}

    async def discover(self, agent_id: str, intent: str) -> DiscoveryResult:
        """
        Discover relevant resources for agent intent.

        Args:
            agent_id: Agent identifier
            intent: Discovery intent description

        Returns:
            DiscoveryResult with resources and scores
        """
        # Survey all registries
        all_resources = []
        for registry_url in self.registry_urls:
            resources = await self._survey_registry(registry_url, intent)
            all_resources.extend(resources)

        # Compute relevance scores
        relevance_scores = {}
        for resource in all_resources:
            score = self._compute_relevance(resource, intent)
            relevance_scores[resource["id"]] = score

        # Negotiate permissions
        permissions_granted = {}
        for resource in all_resources:
            perms = await self._negotiate_permissions(agent_id, resource)
            permissions_granted[resource["id"]] = perms

        return DiscoveryResult(
            resources=all_resources,
            relevance_scores=relevance_scores,
            permissions_granted=permissions_granted
        )

    async def persist_manifest(self, manifest: CapabilityManifest) -> str:
        """
        Persist capability manifest for audit.

        Args:
            manifest: Capability manifest

        Returns:
            Manifest ID
        """
        manifest_id = f"manifest_{manifest.agent_id}_{int(datetime.now().timestamp())}"

        # Store in capability cache
        self.capability_cache[manifest_id] = manifest

        return manifest_id

    async def load_manifest(self, manifest_id: str) -> Optional[CapabilityManifest]:
        """
        Load capability manifest by ID.

        Args:
            manifest_id: Manifest identifier

        Returns:
            CapabilityManifest or None
        """
        return self.capability_cache.get(manifest_id)

    async def _survey_registry(self, registry_url: str, intent: str) -> List[Dict[str, Any]]:
        """Survey a single registry for resources."""
        # Simulate registry query
        await asyncio.sleep(0.01)

        return [
            {
                "id": f"resource_{i}",
                "name": f"Dataset {i}",
                "type": "database",
                "registry": registry_url,
                "metadata": {
                    "size_mb": 100 * i,
                    "records": 1000 * i
                }
            }
            for i in range(1, 4)
        ]

    def _compute_relevance(self, resource: Dict[str, Any], intent: str) -> float:
        """
        Compute relevance score for resource given intent.

        Args:
            resource: Resource metadata
            intent: Discovery intent

        Returns:
            Relevance score (0.0 to 1.0)
        """
        # Simple keyword matching (in production, use embeddings)
        intent_lower = intent.lower()
        name_lower = resource["name"].lower()

        if intent_lower in name_lower:
            return 0.9
        elif any(word in name_lower for word in intent_lower.split()):
            return 0.6
        else:
            return 0.3

    async def _negotiate_permissions(self, agent_id: str, resource: Dict[str, Any]) -> List[str]:
        """
        Negotiate permissions for agent to access resource.

        Args:
            agent_id: Agent identifier
            resource: Resource metadata

        Returns:
            List of granted permissions
        """
        # Check permission cache
        cache_key = f"{agent_id}:{resource['id']}"
        if cache_key in self.permission_cache:
            return self.permission_cache[cache_key]

        # Simulate permission negotiation
        await asyncio.sleep(0.01)

        # Grant read by default, write requires approval
        granted = ["read"]

        # Cache permissions
        self.permission_cache[cache_key] = granted

        return granted


async def scan_and_discover(agent_id: str, intent: str, registries: List[str]) -> DiscoveryResult:
    """
    High-level discovery function.

    Args:
        agent_id: Agent identifier
        intent: Discovery intent
        registries: List of registry URLs

    Returns:
        DiscoveryResult
    """
    scanner = AutonomousScanner(registries)
    return await scanner.discover(agent_id, intent)
