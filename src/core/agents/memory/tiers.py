"""
Tiered Memory Integration - Hot/warm/cold memory layers for agents.

Manages memory tiers with automatic promotion/demotion based on access
patterns and integrates vector cache for embeddings.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio


class MemoryTier(Enum):
    """Memory tier levels."""
    HOT = "hot"      # In-memory, <10ms access
    WARM = "warm"    # SSD-backed, <100ms access
    COLD = "cold"    # Object storage, <1s access


@dataclass
class MemoryRecord:
    """Memory record with tier metadata."""
    key: str
    value: Any
    tier: MemoryTier
    access_count: int
    last_accessed: datetime
    created_at: datetime
    size_bytes: int


class TieredMemoryManager:
    """
    Tiered memory manager for agent memory.

    Automatically promotes frequently accessed data to hot tier and
    demotes cold data to lower tiers based on access patterns.
    """

    def __init__(self, hot_capacity_mb: int = 100, warm_capacity_mb: int = 1000):
        self.hot_capacity_mb = hot_capacity_mb
        self.warm_capacity_mb = warm_capacity_mb

        self.hot_store: Dict[str, MemoryRecord] = {}
        self.warm_store: Dict[str, MemoryRecord] = {}
        self.cold_store: Dict[str, MemoryRecord] = {}

        self.vector_cache: Dict[str, List[float]] = {}

        self.stats = {
            "hot_hits": 0,
            "warm_hits": 0,
            "cold_hits": 0,
            "promotions": 0,
            "demotions": 0
        }

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from tiered memory.

        Args:
            key: Memory key

        Returns:
            Value or None if not found
        """
        # Check hot tier first
        if key in self.hot_store:
            record = self.hot_store[key]
            record.access_count += 1
            record.last_accessed = datetime.now()
            self.stats["hot_hits"] += 1
            return record.value

        # Check warm tier
        if key in self.warm_store:
            record = self.warm_store[key]
            record.access_count += 1
            record.last_accessed = datetime.now()
            self.stats["warm_hits"] += 1

            # Consider promotion to hot
            if record.access_count > 10:
                await self._promote(key, MemoryTier.WARM, MemoryTier.HOT)

            return record.value

        # Check cold tier
        if key in self.cold_store:
            record = self.cold_store[key]
            record.access_count += 1
            record.last_accessed = datetime.now()
            self.stats["cold_hits"] += 1

            # Consider promotion to warm
            if record.access_count > 5:
                await self._promote(key, MemoryTier.COLD, MemoryTier.WARM)

            return record.value

        return None

    async def put(self, key: str, value: Any, tier: MemoryTier = MemoryTier.WARM) -> None:
        """
        Store value in tiered memory.

        Args:
            key: Memory key
            value: Value to store
            tier: Target tier (default: WARM)
        """
        size_bytes = len(str(value).encode('utf-8'))

        record = MemoryRecord(
            key=key,
            value=value,
            tier=tier,
            access_count=0,
            last_accessed=datetime.now(),
            created_at=datetime.now(),
            size_bytes=size_bytes
        )

        if tier == MemoryTier.HOT:
            # Check capacity
            if self._get_tier_size(MemoryTier.HOT) + size_bytes > self.hot_capacity_mb * 1024 * 1024:
                await self._evict_from_hot()
            self.hot_store[key] = record
        elif tier == MemoryTier.WARM:
            if self._get_tier_size(MemoryTier.WARM) + size_bytes > self.warm_capacity_mb * 1024 * 1024:
                await self._evict_from_warm()
            self.warm_store[key] = record
        else:
            self.cold_store[key] = record

    async def put_embedding(self, key: str, embedding: List[float]) -> None:
        """
        Store embedding in vector cache.

        Args:
            key: Embedding key
            embedding: Vector embedding
        """
        self.vector_cache[key] = embedding

    async def get_embedding(self, key: str) -> Optional[List[float]]:
        """
        Retrieve embedding from vector cache.

        Args:
            key: Embedding key

        Returns:
            Embedding vector or None
        """
        return self.vector_cache.get(key)

    async def _promote(self, key: str, from_tier: MemoryTier, to_tier: MemoryTier) -> None:
        """Promote record to higher tier."""
        if from_tier == MemoryTier.WARM and to_tier == MemoryTier.HOT:
            record = self.warm_store.pop(key)
            record.tier = MemoryTier.HOT

            # Check capacity
            if self._get_tier_size(MemoryTier.HOT) + record.size_bytes > self.hot_capacity_mb * 1024 * 1024:
                await self._evict_from_hot()

            self.hot_store[key] = record
            self.stats["promotions"] += 1

        elif from_tier == MemoryTier.COLD and to_tier == MemoryTier.WARM:
            record = self.cold_store.pop(key)
            record.tier = MemoryTier.WARM

            if self._get_tier_size(MemoryTier.WARM) + record.size_bytes > self.warm_capacity_mb * 1024 * 1024:
                await self._evict_from_warm()

            self.warm_store[key] = record
            self.stats["promotions"] += 1

    async def _evict_from_hot(self) -> None:
        """Evict least recently used record from hot tier."""
        if not self.hot_store:
            return

        # Find LRU record
        lru_key = min(self.hot_store.keys(), key=lambda k: self.hot_store[k].last_accessed)
        record = self.hot_store.pop(lru_key)

        # Demote to warm
        record.tier = MemoryTier.WARM
        self.warm_store[lru_key] = record
        self.stats["demotions"] += 1

    async def _evict_from_warm(self) -> None:
        """Evict least recently used record from warm tier."""
        if not self.warm_store:
            return

        lru_key = min(self.warm_store.keys(), key=lambda k: self.warm_store[k].last_accessed)
        record = self.warm_store.pop(lru_key)

        # Demote to cold
        record.tier = MemoryTier.COLD
        self.cold_store[lru_key] = record
        self.stats["demotions"] += 1

    def _get_tier_size(self, tier: MemoryTier) -> int:
        """Get total size of tier in bytes."""
        if tier == MemoryTier.HOT:
            return sum(r.size_bytes for r in self.hot_store.values())
        elif tier == MemoryTier.WARM:
            return sum(r.size_bytes for r in self.warm_store.values())
        else:
            return sum(r.size_bytes for r in self.cold_store.values())

    def get_stats(self) -> Dict[str, Any]:
        """Get memory tier statistics."""
        return {
            **self.stats,
            "hot_size_mb": self._get_tier_size(MemoryTier.HOT) / (1024 * 1024),
            "warm_size_mb": self._get_tier_size(MemoryTier.WARM) / (1024 * 1024),
            "cold_size_mb": self._get_tier_size(MemoryTier.COLD) / (1024 * 1024),
            "hot_records": len(self.hot_store),
            "warm_records": len(self.warm_store),
            "cold_records": len(self.cold_store),
            "vector_cache_size": len(self.vector_cache)
        }
