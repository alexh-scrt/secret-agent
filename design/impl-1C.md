# Phase 1C: Cache Service & Middleware

## Overview

This phase implements intelligent caching and middleware layers that automatically handle cross-cutting concerns like caching, graph updates, and telemetry across all MCP tools without modifying existing code.

---

## Task 1C.1: Cache Service

**Objective**: Create a comprehensive caching service with smart invalidation, TTL management, and cache analytics.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/services/cache_service.py
mcp-scrt/tests/unit/test_cache_service.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/services/cache_service.py

"""
Cache service for intelligent data caching.

This service provides:
- Smart cache key generation
- TTL management by data type
- Pattern-based invalidation
- Cache statistics and monitoring
- Multi-layer caching strategy
"""

import hashlib
import json
from typing import Any, Optional, Callable, Dict, List, Awaitable
from datetime import datetime
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheStatistics:
    """Cache performance statistics."""
    total_hits: int
    total_misses: int
    hit_rate: float
    total_keys: int
    memory_used: str
    top_keys: List[Dict[str, Any]]
    invalidations: int


# Cache key patterns with default TTLs (in seconds)
CACHE_PATTERNS = {
    # Rapidly changing data (30 seconds)
    "balance:{address}": 30,
    "gas_price": 30,
    "block:latest": 30,
    "account:{address}:sequence": 30,
    
    # Moderately changing data (5 minutes)
    "validator:{address}": 300,
    "delegations:{address}": 300,
    "rewards:{address}": 300,
    "account:{address}:info": 300,
    "tx:status:{hash}": 300,
    
    # Slowly changing data (1 hour)
    "validators:all": 3600,
    "proposals:all": 3600,
    "proposal:{id}": 3600,
    "code_info:{code_id}": 3600,
    "contract_info:{address}": 3600,
    "ibc:channels": 3600,
    
    # Static data (24 hours)
    "block:{height}": 86400,
    "tx:{hash}": 86400,
    "contract_code:{code_id}": 86400,
    
    # Knowledge base (1 hour)
    "knowledge:query:*": 3600,
    "embedding:*": 86400,
    
    # Graph analysis (5 minutes)
    "graph:*": 300,
}

# Invalidation rules: operation -> patterns to invalidate
INVALIDATION_RULES = {
    # Bank operations
    "secret_send_tokens": [
        "balance:{from_address}",
        "balance:{to_address}",
        "account:{from_address}:info",
    ],
    "secret_multi_send": [
        "balance:*",  # Invalidate all balances (multiple recipients)
    ],
    
    # Staking operations
    "secret_delegate": [
        "balance:{delegator}",
        "delegations:{delegator}",
        "validator:{validator}",
        "validators:all",
        "rewards:{delegator}",
    ],
    "secret_undelegate": [
        "balance:{delegator}",
        "delegations:{delegator}",
        "validator:{validator}",
        "validators:all",
    ],
    "secret_redelegate": [
        "delegations:{delegator}",
        "validator:{from_validator}",
        "validator:{to_validator}",
        "validators:all",
    ],
    "secret_withdraw_rewards": [
        "balance:{delegator}",
        "rewards:{delegator}",
        "delegations:{delegator}",
    ],
    
    # Governance operations
    "secret_submit_proposal": [
        "proposals:all",
        "balance:{proposer}",
    ],
    "secret_vote_proposal": [
        "proposal:{proposal_id}",
        "account:{voter}:info",
    ],
    "secret_deposit_proposal": [
        "proposal:{proposal_id}",
        "balance:{depositor}",
    ],
    
    # Contract operations
    "secret_instantiate_contract": [
        "balance:{sender}",
        "account:{sender}:info",
    ],
    "secret_execute_contract": [
        "balance:{sender}",
        "contract_info:{contract_address}",
    ],
    
    # Knowledge operations
    "knowledge_add_document": [
        "knowledge:query:*",
    ],
    "knowledge_update_document": [
        "knowledge:query:*",
    ],
    "knowledge_delete_document": [
        "knowledge:query:*",
    ],
}


class CacheService:
    """
    High-level caching service with smart invalidation.
    
    Features:
    - Automatic TTL based on data type
    - Pattern-based invalidation
    - Cache-aside pattern support
    - Performance analytics
    - Multi-layer caching
    """
    
    def __init__(
        self,
        redis_client,
        default_ttl: int = 300  # 5 minutes
    ):
        """
        Initialize cache service.
        
        Args:
            redis_client: Redis client
            default_ttl: Default TTL in seconds
        """
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.patterns = CACHE_PATTERNS
        self.invalidation_rules = INVALIDATION_RULES
        
        logger.info("Initialized CacheService")
    
    def _get_ttl_for_key(self, key: str) -> int:
        """
        Determine TTL for a cache key based on patterns.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds
        """
        # Check if key matches any pattern
        for pattern, ttl in self.patterns.items():
            # Simple pattern matching (could be enhanced with regex)
            if "*" in pattern:
                prefix = pattern.split("*")[0]
                if key.startswith(prefix):
                    return ttl
            elif pattern == key:
                return ttl
        
        # Default TTL
        return self.default_ttl
    
    def _normalize_value(self, value: Any) -> str:
        """
        Normalize value for caching (convert to JSON string).
        
        Args:
            value: Value to cache
            
        Returns:
            JSON string
        """
        if isinstance(value, str):
            return value
        return json.dumps(value, default=str)
    
    def _denormalize_value(self, value: Optional[str]) -> Any:
        """
        Denormalize cached value (parse JSON string).
        
        Args:
            value: Cached string value
            
        Returns:
            Parsed value or None
        """
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def get(
        self,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        value = self.redis.get(key)
        
        if value is not None:
            # Record cache hit
            await self._record_hit(key)
            logger.debug(f"Cache hit: {key}")
            return self._denormalize_value(value)
        
        # Record cache miss
        await self._record_miss(key)
        logger.debug(f"Cache miss: {key}")
        return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL (uses pattern-based if not provided)
            
        Returns:
            True if successful
        """
        # Determine TTL
        if ttl is None:
            ttl = self._get_ttl_for_key(key)
        
        # Normalize value
        normalized = self._normalize_value(value)
        
        # Set in Redis with TTL
        success = self.redis.set(key, normalized, ex=ttl)
        
        if success:
            logger.debug(f"Cached: {key} (TTL: {ttl}s)")
        
        return success
    
    async def delete(self, *keys: str) -> int:
        """
        Delete one or more keys.
        
        Args:
            keys: Keys to delete
            
        Returns:
            Number of keys deleted
        """
        if not keys:
            return 0
        
        deleted = self.redis.delete(*keys)
        logger.debug(f"Deleted {deleted} cache keys")
        return deleted
    
    async def get_or_fetch(
        self,
        key: str,
        fetch_fn: Callable[[], Awaitable[Any]],
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get from cache or fetch from source (cache-aside pattern).
        
        Args:
            key: Cache key
            fetch_fn: Async function to fetch data if not cached
            ttl: Optional TTL
            
        Returns:
            Cached or fetched value
        """
        # Try cache first
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        # Fetch from source
        logger.debug(f"Fetching data for cache key: {key}")
        data = await fetch_fn()
        
        # Cache the result
        if data is not None:
            await self.set(key, data, ttl=ttl)
        
        return data
    
    async def invalidate_related(
        self,
        operation: str,
        params: Dict[str, Any]
    ):
        """
        Invalidate cache keys related to an operation.
        
        Args:
            operation: Operation name (e.g., "secret_delegate")
            params: Operation parameters
        """
        if operation not in self.invalidation_rules:
            logger.debug(f"No invalidation rules for operation: {operation}")
            return
        
        patterns = self.invalidation_rules[operation]
        keys_to_delete = []
        
        for pattern in patterns:
            try:
                # Format pattern with parameters
                formatted_key = pattern.format(**params)
                
                # Handle wildcard patterns
                if "*" in formatted_key:
                    # Delete all matching keys
                    matching_keys = self.redis.keys(formatted_key)
                    keys_to_delete.extend(matching_keys)
                else:
                    keys_to_delete.append(formatted_key)
            
            except KeyError as e:
                # Parameter not provided, skip this pattern
                logger.debug(f"Skipping pattern {pattern}: missing parameter {e}")
                continue
        
        # Delete all collected keys
        if keys_to_delete:
            deleted = await self.delete(*keys_to_delete)
            await self._record_invalidation(operation, deleted)
            logger.info(f"Invalidated {deleted} cache keys for operation: {operation}")
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., "balance:*")
            
        Returns:
            Number of keys deleted
        """
        keys = self.redis.keys(pattern)
        
        if keys:
            deleted = self.redis.delete(*keys)
            logger.info(f"Invalidated {deleted} keys matching pattern: {pattern}")
            return deleted
        
        return 0
    
    async def _record_hit(self, key: str):
        """Record a cache hit for statistics."""
        self.redis.incr("cache:stats:hits")
        self.redis.hincrby("cache:stats:keys", key, 1)
    
    async def _record_miss(self, key: str):
        """Record a cache miss for statistics."""
        self.redis.incr("cache:stats:misses")
    
    async def _record_invalidation(self, operation: str, count: int):
        """Record cache invalidations for statistics."""
        self.redis.incr("cache:stats:invalidations", count)
        self.redis.hincrby("cache:stats:operations", operation, count)
    
    async def get_statistics(self) -> CacheStatistics:
        """
        Get cache performance statistics.
        
        Returns:
            Cache statistics
        """
        hits = int(self.redis.get("cache:stats:hits") or 0)
        misses = int(self.redis.get("cache:stats:misses") or 0)
        invalidations = int(self.redis.get("cache:stats:invalidations") or 0)
        
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0.0
        
        # Get memory info from Redis
        info = self.redis.health_check()
        memory_used = info.get("used_memory_human", "unknown")
        total_keys = info.get("total_keys", 0)
        
        # Get top cached keys
        top_keys_data = self.redis.hgetall("cache:stats:keys")
        top_keys = [
            {"key": k, "hits": v}
            for k, v in sorted(
                top_keys_data.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        ]
        
        return CacheStatistics(
            total_hits=hits,
            total_misses=misses,
            hit_rate=hit_rate,
            total_keys=total_keys,
            memory_used=memory_used,
            top_keys=top_keys,
            invalidations=invalidations
        )
    
    async def reset_statistics(self):
        """Reset cache statistics."""
        self.redis.delete(
            "cache:stats:hits",
            "cache:stats:misses",
            "cache:stats:invalidations"
        )
        self.redis.delete("cache:stats:keys")
        self.redis.delete("cache:stats:operations")
        logger.info("Cache statistics reset")
    
    async def warm_cache(
        self,
        keys_and_fetchers: List[tuple]
    ):
        """
        Warm cache with pre-fetched data.
        
        Args:
            keys_and_fetchers: List of (key, fetch_fn, ttl) tuples
        """
        logger.info(f"Warming cache with {len(keys_and_fetchers)} items")
        
        for item in keys_and_fetchers:
            if len(item) == 2:
                key, fetch_fn = item
                ttl = None
            else:
                key, fetch_fn, ttl = item
            
            try:
                # Check if already cached
                if await self.get(key) is not None:
                    logger.debug(f"Key already cached: {key}")
                    continue
                
                # Fetch and cache
                data = await fetch_fn()
                if data is not None:
                    await self.set(key, data, ttl=ttl)
                    logger.debug(f"Warmed cache: {key}")
            
            except Exception as e:
                logger.warning(f"Failed to warm cache for {key}: {e}")
                continue
    
    async def clear_all(self):
        """
        Clear all cache data.
        WARNING: This deletes all keys in the Redis database!
        """
        self.redis.flushdb()
        logger.warning("All cache data cleared")
    
    def get_cache_info(self, key: str) -> Dict[str, Any]:
        """
        Get information about a cached key.
        
        Args:
            key: Cache key
            
        Returns:
            Info dict with TTL, size, etc.
        """
        exists = self.redis.exists(key)
        
        if not exists:
            return {"exists": False}
        
        ttl = self.redis.ttl(key)
        value = self.redis.get(key)
        size = len(value) if value else 0
        
        return {
            "exists": True,
            "ttl": ttl,
            "size_bytes": size,
            "expires_at": datetime.utcnow().timestamp() + ttl if ttl > 0 else None
        }


# Export
__all__ = ["CacheService", "CacheStatistics", "CACHE_PATTERNS", "INVALIDATION_RULES"]
```

**Test File**:

```python
# mcp-scrt/tests/unit/test_cache_service.py

import pytest
from unittest.mock import Mock, AsyncMock, patch
from mcp_scrt.services.cache_service import CacheService, CacheStatistics


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis = Mock()
    redis.get.return_value = None
    redis.set.return_value = True
    redis.delete.return_value = 1
    redis.keys.return_value = []
    redis.incr.return_value = 1
    redis.hincrby.return_value = 1
    redis.hgetall.return_value = {}
    redis.exists.return_value = 1
    redis.ttl.return_value = 300
    redis.flushdb.return_value = True
    redis.health_check.return_value = {
        "used_memory_human": "10MB",
        "total_keys": 100
    }
    return redis


@pytest.fixture
def cache_service(mock_redis):
    """Create cache service with mock Redis."""
    return CacheService(redis_client=mock_redis)


def test_initialization(cache_service):
    """Test service initialization."""
    assert cache_service.default_ttl == 300
    assert len(cache_service.patterns) > 0
    assert len(cache_service.invalidation_rules) > 0


def test_get_ttl_for_key(cache_service):
    """Test TTL determination based on key patterns."""
    # Exact match
    ttl = cache_service._get_ttl_for_key("gas_price")
    assert ttl == 30
    
    # Pattern match
    ttl = cache_service._get_ttl_for_key("balance:secret1abc")
    assert ttl == 30
    
    # No match - use default
    ttl = cache_service._get_ttl_for_key("unknown:key")
    assert ttl == 300


@pytest.mark.asyncio
async def test_get_cache_hit(cache_service, mock_redis):
    """Test cache get with hit."""
    mock_redis.get.return_value = '{"balance": "1000"}'
    
    value = await cache_service.get("balance:secret1abc")
    
    assert value == {"balance": "1000"}
    mock_redis.get.assert_called_once_with("balance:secret1abc")


@pytest.mark.asyncio
async def test_get_cache_miss(cache_service, mock_redis):
    """Test cache get with miss."""
    mock_redis.get.return_value = None
    
    value = await cache_service.get("balance:secret1abc", default=0)
    
    assert value == 0


@pytest.mark.asyncio
async def test_set(cache_service, mock_redis):
    """Test cache set."""
    await cache_service.set("test:key", {"data": "value"})
    
    # Verify Redis set was called with TTL
    mock_redis.set.assert_called_once()
    args = mock_redis.set.call_args
    assert args[0][0] == "test:key"
    assert "ex" in args[1]  # TTL parameter


@pytest.mark.asyncio
async def test_set_with_custom_ttl(cache_service, mock_redis):
    """Test cache set with custom TTL."""
    await cache_service.set("test:key", "value", ttl=600)
    
    args = mock_redis.set.call_args
    assert args[1]["ex"] == 600


@pytest.mark.asyncio
async def test_delete(cache_service, mock_redis):
    """Test cache delete."""
    mock_redis.delete.return_value = 2
    
    deleted = await cache_service.delete("key1", "key2")
    
    assert deleted == 2
    mock_redis.delete.assert_called_once_with("key1", "key2")


@pytest.mark.asyncio
async def test_get_or_fetch_cached(cache_service, mock_redis):
    """Test get_or_fetch with cached value."""
    mock_redis.get.return_value = '"cached_value"'
    
    fetch_fn = AsyncMock(return_value="fetched_value")
    
    value = await cache_service.get_or_fetch("test:key", fetch_fn)
    
    assert value == "cached_value"
    fetch_fn.assert_not_called()  # Should not fetch if cached


@pytest.mark.asyncio
async def test_get_or_fetch_not_cached(cache_service, mock_redis):
    """Test get_or_fetch with cache miss."""
    mock_redis.get.return_value = None
    
    fetch_fn = AsyncMock(return_value="fetched_value")
    
    value = await cache_service.get_or_fetch("test:key", fetch_fn)
    
    assert value == "fetched_value"
    fetch_fn.assert_called_once()
    mock_redis.set.assert_called_once()  # Should cache result


@pytest.mark.asyncio
async def test_invalidate_related(cache_service, mock_redis):
    """Test invalidating related cache keys."""
    mock_redis.keys.return_value = ["balance:secret1abc"]
    
    await cache_service.invalidate_related(
        operation="secret_send_tokens",
        params={
            "from_address": "secret1abc",
            "to_address": "secret1def"
        }
    )
    
    # Should delete keys for both addresses
    mock_redis.delete.assert_called()


@pytest.mark.asyncio
async def test_invalidate_pattern(cache_service, mock_redis):
    """Test invalidating by pattern."""
    mock_redis.keys.return_value = ["balance:secret1abc", "balance:secret1def"]
    mock_redis.delete.return_value = 2
    
    deleted = await cache_service.invalidate_pattern("balance:*")
    
    assert deleted == 2
    mock_redis.keys.assert_called_with("balance:*")


@pytest.mark.asyncio
async def test_get_statistics(cache_service, mock_redis):
    """Test getting cache statistics."""
    mock_redis.get.side_effect = [100, 20, 5]  # hits, misses, invalidations
    
    stats = await cache_service.get_statistics()
    
    assert isinstance(stats, CacheStatistics)
    assert stats.total_hits == 100
    assert stats.total_misses == 20
    assert stats.hit_rate > 0


@pytest.mark.asyncio
async def test_warm_cache(cache_service, mock_redis):
    """Test cache warming."""
    mock_redis.get.return_value = None  # Not cached
    
    fetch_fn1 = AsyncMock(return_value="value1")
    fetch_fn2 = AsyncMock(return_value="value2")
    
    keys_and_fetchers = [
        ("key1", fetch_fn1, 300),
        ("key2", fetch_fn2, 600)
    ]
    
    await cache_service.warm_cache(keys_and_fetchers)
    
    fetch_fn1.assert_called_once()
    fetch_fn2.assert_called_once()
    assert mock_redis.set.call_count == 2


def test_get_cache_info(cache_service, mock_redis):
    """Test getting cache key info."""
    mock_redis.exists.return_value = 1
    mock_redis.ttl.return_value = 300
    mock_redis.get.return_value = "test_value"
    
    info = cache_service.get_cache_info("test:key")
    
    assert info["exists"] is True
    assert info["ttl"] == 300
    assert info["size_bytes"] > 0


@pytest.mark.asyncio
async def test_clear_all(cache_service, mock_redis):
    """Test clearing all cache."""
    await cache_service.clear_all()
    
    mock_redis.flushdb.assert_called_once()
```

**Success Criteria**:
- ✅ Service manages cache with automatic TTL
- ✅ Pattern-based invalidation works
- ✅ Cache-aside pattern implementation
- ✅ Statistics tracking functional
- ✅ All tests pass

---

## Task 1C.2: Cache Middleware

**Objective**: Create middleware that automatically caches MCP tool responses and invalidates cache on state-changing operations.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/middleware/__init__.py
mcp-scrt/src/mcp_scrt/middleware/cache_middleware.py
mcp-scrt/tests/unit/test_cache_middleware.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/middleware/cache_middleware.py

"""
Cache middleware for automatic caching of tool operations.

This middleware provides:
- Automatic caching of read operations
- Automatic invalidation on write operations
- Cache key generation from tool name and parameters
- Performance monitoring
"""

from typing import Any, Dict, Optional, Callable, Awaitable
from dataclasses import dataclass
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheContext:
    """Context for cache operations."""
    cache_key: Optional[str] = None
    cache_hit: bool = False
    ttl: Optional[int] = None
    should_cache: bool = True


class CacheMiddleware:
    """
    Middleware for automatic tool result caching.
    
    Features:
    - Automatic cache key generation
    - Read-through caching
    - Write-through invalidation
    - Selective caching based on tool type
    """
    
    # Tools that should NOT be cached (write operations, auth, etc.)
    UNCACHEABLE_TOOLS = {
        # Write operations
        "secret_send_tokens",
        "secret_multi_send",
        "secret_delegate",
        "secret_undelegate",
        "secret_redelegate",
        "secret_withdraw_rewards",
        "secret_submit_proposal",
        "secret_vote_proposal",
        "secret_deposit_proposal",
        "secret_instantiate_contract",
        "secret_execute_contract",
        "secret_upload_contract",
        "secret_migrate_contract",
        "secret_ibc_transfer",
        
        # Wallet operations (sensitive)
        "secret_create_wallet",
        "secret_import_wallet",
        "secret_set_active_wallet",
        "secret_remove_wallet",
        
        # Knowledge write operations
        "knowledge_add_document",
        "knowledge_update_document",
        "knowledge_delete_document",
        
        # Graph write operations (handled by graph middleware)
        "graph_create_node",
        "graph_create_relationship",
        "graph_delete_node",
    }
    
    # Tools with custom cache key patterns
    CACHE_KEY_PATTERNS = {
        "secret_get_balance": "balance:{address}",
        "secret_get_validators": "validators:all",
        "secret_get_validator": "validator:{validator_address}",
        "secret_get_delegations": "delegations:{address}",
        "secret_get_rewards": "rewards:{address}",
        "secret_get_proposals": "proposals:all",
        "secret_get_proposal": "proposal:{proposal_id}",
        "secret_get_block": "block:{height}",
        "secret_get_latest_block": "block:latest",
        "secret_get_transaction": "tx:{tx_hash}",
        "secret_get_code_info": "code_info:{code_id}",
        "secret_get_contract_info": "contract_info:{contract_address}",
        "secret_get_account": "account:{address}:info",
        "secret_get_gas_prices": "gas_price",
        "secret_get_ibc_channels": "ibc:channels",
    }
    
    def __init__(self, cache_service):
        """
        Initialize cache middleware.
        
        Args:
            cache_service: CacheService instance
        """
        self.cache = cache_service
        logger.info("Initialized CacheMiddleware")
    
    def _should_cache_tool(self, tool_name: str) -> bool:
        """
        Determine if a tool's results should be cached.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if should be cached
        """
        return tool_name not in self.UNCACHEABLE_TOOLS
    
    def _generate_cache_key(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> str:
        """
        Generate cache key for tool execution.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
            
        Returns:
            Cache key string
        """
        # Check if tool has custom key pattern
        if tool_name in self.CACHE_KEY_PATTERNS:
            pattern = self.CACHE_KEY_PATTERNS[tool_name]
            try:
                return pattern.format(**params)
            except KeyError:
                # Missing parameter, fall back to hash-based key
                pass
        
        # Default: hash-based key
        # Create stable string from parameters
        param_str = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        
        return f"tool:{tool_name}:{param_hash}"
    
    async def before_execute(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> CacheContext:
        """
        Execute before tool runs - check cache.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
            
        Returns:
            Cache context with cache hit data if available
        """
        context = CacheContext()
        
        # Check if tool should be cached
        if not self._should_cache_tool(tool_name):
            context.should_cache = False
            logger.debug(f"Tool {tool_name} marked as uncacheable")
            return context
        
        # Generate cache key
        cache_key = self._generate_cache_key(tool_name, params)
        context.cache_key = cache_key
        
        # Check cache
        cached_result = await self.cache.get(cache_key)
        
        if cached_result is not None:
            context.cache_hit = True
            logger.info(f"Cache hit for {tool_name}: {cache_key}")
            return context
        
        logger.debug(f"Cache miss for {tool_name}: {cache_key}")
        return context
    
    async def after_execute(
        self,
        tool_name: str,
        params: Dict[str, Any],
        result: Any,
        context: CacheContext,
        error: Optional[Exception] = None
    ):
        """
        Execute after tool runs - cache result and handle invalidation.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
            result: Tool execution result
            context: Cache context from before_execute
            error: Exception if tool failed
        """
        # Don't cache if error occurred
        if error is not None:
            logger.debug(f"Not caching {tool_name} due to error: {error}")
            return
        
        # Don't cache if marked as uncacheable
        if not context.should_cache:
            # But do handle invalidation for write operations
            if tool_name in self.UNCACHEABLE_TOOLS:
                await self._handle_invalidation(tool_name, params)
            return
        
        # Cache the result
        if context.cache_key:
            await self.cache.set(
                context.cache_key,
                result,
                ttl=context.ttl
            )
            logger.debug(f"Cached result for {tool_name}: {context.cache_key}")
    
    async def _handle_invalidation(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ):
        """
        Handle cache invalidation for write operations.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
        """
        # Use cache service's invalidation rules
        await self.cache.invalidate_related(tool_name, params)


# Export
__all__ = ["CacheMiddleware", "CacheContext"]
```

**Test File**:

```python
# mcp-scrt/tests/unit/test_cache_middleware.py

import pytest
from unittest.mock import Mock, AsyncMock
from mcp_scrt.middleware.cache_middleware import CacheMiddleware, CacheContext


@pytest.fixture
def mock_cache_service():
    """Mock cache service."""
    cache = Mock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    cache.invalidate_related = AsyncMock()
    return cache


@pytest.fixture
def middleware(mock_cache_service):
    """Create cache middleware with mock cache service."""
    return CacheMiddleware(cache_service=mock_cache_service)


def test_should_cache_tool(middleware):
    """Test determining if tool should be cached."""
    # Read operation - should cache
    assert middleware._should_cache_tool("secret_get_balance") is True
    
    # Write operation - should not cache
    assert middleware._should_cache_tool("secret_send_tokens") is False
    
    # Wallet operation - should not cache
    assert middleware._should_cache_tool("secret_create_wallet") is False


def test_generate_cache_key_with_pattern(middleware):
    """Test cache key generation with predefined pattern."""
    key = middleware._generate_cache_key(
        "secret_get_balance",
        {"address": "secret1abc123"}
    )
    
    assert key == "balance:secret1abc123"


def test_generate_cache_key_without_pattern(middleware):
    """Test cache key generation without pattern (hash-based)."""
    key = middleware._generate_cache_key(
        "unknown_tool",
        {"param1": "value1", "param2": "value2"}
    )
    
    assert key.startswith("tool:unknown_tool:")
    assert len(key) > len("tool:unknown_tool:")


def test_generate_cache_key_consistency(middleware):
    """Test that same parameters generate same key."""
    params = {"address": "secret1abc", "height": 100}
    
    key1 = middleware._generate_cache_key("test_tool", params)
    key2 = middleware._generate_cache_key("test_tool", params)
    
    assert key1 == key2


@pytest.mark.asyncio
async def test_before_execute_cache_hit(middleware, mock_cache_service):
    """Test before_execute with cache hit."""
    mock_cache_service.get.return_value = {"balance": "1000"}
    
    context = await middleware.before_execute(
        "secret_get_balance",
        {"address": "secret1abc"}
    )
    
    assert context.cache_hit is True
    assert context.cache_key == "balance:secret1abc"


@pytest.mark.asyncio
async def test_before_execute_cache_miss(middleware, mock_cache_service):
    """Test before_execute with cache miss."""
    mock_cache_service.get.return_value = None
    
    context = await middleware.before_execute(
        "secret_get_balance",
        {"address": "secret1abc"}
    )
    
    assert context.cache_hit is False
    assert context.cache_key is not None


@pytest.mark.asyncio
async def test_before_execute_uncacheable(middleware):
    """Test before_execute with uncacheable tool."""
    context = await middleware.before_execute(
        "secret_send_tokens",
        {"recipient": "secret1def", "amount": "1000"}
    )
    
    assert context.should_cache is False


@pytest.mark.asyncio
async def test_after_execute_caches_result(middleware, mock_cache_service):
    """Test after_execute caches successful result."""
    context = CacheContext(
        cache_key="test:key",
        should_cache=True
    )
    
    await middleware.after_execute(
        tool_name="secret_get_balance",
        params={"address": "secret1abc"},
        result={"balance": "1000"},
        context=context,
        error=None
    )
    
    mock_cache_service.set.assert_called_once()


@pytest.mark.asyncio
async def test_after_execute_skips_on_error(middleware, mock_cache_service):
    """Test after_execute doesn't cache on error."""
    context = CacheContext(
        cache_key="test:key",
        should_cache=True
    )
    
    await middleware.after_execute(
        tool_name="secret_get_balance",
        params={"address": "secret1abc"},
        result=None,
        context=context,
        error=Exception("Test error")
    )
    
    mock_cache_service.set.assert_not_called()


@pytest.mark.asyncio
async def test_after_execute_invalidates_on_write(middleware, mock_cache_service):
    """Test after_execute invalidates cache for write operations."""
    context = CacheContext(should_cache=False)
    
    await middleware.after_execute(
        tool_name="secret_send_tokens",
        params={"from_address": "secret1abc", "to_address": "secret1def"},
        result={"tx_hash": "ABC123"},
        context=context,
        error=None
    )
    
    mock_cache_service.invalidate_related.assert_called_once()
```

**Success Criteria**:
- ✅ Middleware automatically caches read operations
- ✅ Write operations trigger cache invalidation
- ✅ Cache keys are generated consistently
- ✅ Uncacheable tools are handled correctly
- ✅ All tests pass

---

## Task 1C.3: Graph Middleware

**Objective**: Create middleware that automatically records blockchain operations in the Neo4j graph database.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/middleware/graph_middleware.py
mcp-scrt/tests/unit/test_graph_middleware.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/middleware/graph_middleware.py

"""
Graph middleware for automatic graph database updates.

This middleware provides:
- Automatic graph recording for blockchain operations
- Non-blocking graph updates
- Error isolation (graph failures don't break operations)
- Operation type detection
"""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class GraphMiddleware:
    """
    Middleware for automatic graph database updates.
    
    Features:
    - Auto-record blockchain transactions
    - Non-blocking updates
    - Error isolation
    - Selective recording based on operation type
    """
    
    # Operations that should trigger graph updates
    GRAPH_OPERATIONS = {
        # Staking
        "secret_delegate": "delegation",
        "secret_undelegate": "undelegation",
        "secret_redelegate": "redelegation",
        
        # Transfers
        "secret_send_tokens": "transfer",
        "secret_multi_send": "multi_transfer",
        
        # Governance
        "secret_vote_proposal": "vote",
        "secret_submit_proposal": "proposal_submission",
        
        # Contracts
        "secret_instantiate_contract": "contract_instantiation",
        "secret_execute_contract": "contract_execution",
    }
    
    def __init__(
        self,
        graph_service,
        async_mode: bool = True
    ):
        """
        Initialize graph middleware.
        
        Args:
            graph_service: GraphService instance
            async_mode: Run updates asynchronously (non-blocking)
        """
        self.graph = graph_service
        self.async_mode = async_mode
        logger.info(f"Initialized GraphMiddleware (async_mode={async_mode})")
    
    def _should_record(self, tool_name: str) -> bool:
        """
        Determine if operation should be recorded in graph.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if should be recorded
        """
        return tool_name in self.GRAPH_OPERATIONS
    
    async def after_execute(
        self,
        tool_name: str,
        params: Dict[str, Any],
        result: Any,
        error: Optional[Exception] = None
    ):
        """
        Execute after tool runs - record in graph if applicable.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
            result: Tool execution result
            error: Exception if tool failed
        """
        # Don't record if error occurred
        if error is not None:
            logger.debug(f"Skipping graph update for {tool_name} due to error")
            return
        
        # Check if should record
        if not self._should_record(tool_name):
            return
        
        # Get operation type
        operation_type = self.GRAPH_OPERATIONS[tool_name]
        
        # Record in graph (async if enabled)
        if self.async_mode:
            # Non-blocking - don't wait for completion
            asyncio.create_task(
                self._record_operation(
                    operation_type,
                    tool_name,
                    params,
                    result
                )
            )
            logger.debug(f"Queued async graph update for {tool_name}")
        else:
            # Blocking - wait for completion
            await self._record_operation(
                operation_type,
                tool_name,
                params,
                result
            )
            logger.debug(f"Completed graph update for {tool_name}")
    
    async def _record_operation(
        self,
        operation_type: str,
        tool_name: str,
        params: Dict[str, Any],
        result: Dict[str, Any]
    ):
        """
        Record an operation in the graph database.
        
        Args:
            operation_type: Type of operation
            tool_name: Tool name
            params: Tool parameters
            result: Tool result
        """
        try:
            # Extract transaction hash from result
            tx_hash = result.get("tx_hash") or result.get("txhash")
            
            if not tx_hash:
                logger.warning(f"No tx_hash in result for {tool_name}")
                return
            
            timestamp = datetime.utcnow()
            
            # Route to appropriate graph service method
            if operation_type == "delegation":
                await self.graph.record_delegation(
                    delegator_address=params.get("address") or params.get("delegator"),
                    validator_address=params.get("validator_address") or params.get("validator"),
                    amount=params.get("amount"),
                    tx_hash=tx_hash,
                    timestamp=timestamp
                )
            
            elif operation_type == "undelegation":
                await self.graph.record_delegation(
                    delegator_address=params.get("address") or params.get("delegator"),
                    validator_address=params.get("validator_address") or params.get("validator"),
                    amount=f"-{params.get('amount')}",  # Negative for undelegation
                    tx_hash=tx_hash,
                    timestamp=timestamp
                )
            
            elif operation_type == "redelegation":
                # Record as two operations: undelegate from source, delegate to destination
                await self.graph.record_delegation(
                    delegator_address=params.get("address") or params.get("delegator"),
                    validator_address=params.get("dst_validator"),
                    amount=params.get("amount"),
                    tx_hash=tx_hash,
                    timestamp=timestamp
                )
            
            elif operation_type == "transfer":
                await self.graph.record_transfer(
                    from_address=params.get("address") or params.get("from_address"),
                    to_address=params.get("recipient") or params.get("to_address"),
                    amount=params.get("amount"),
                    tx_hash=tx_hash,
                    timestamp=timestamp
                )
            
            elif operation_type == "multi_transfer":
                # Record multiple transfers
                recipients = params.get("recipients", [])
                for recipient_data in recipients:
                    await self.graph.record_transfer(
                        from_address=params.get("address"),
                        to_address=recipient_data.get("address"),
                        amount=recipient_data.get("amount"),
                        tx_hash=tx_hash,
                        timestamp=timestamp
                    )
            
            elif operation_type == "vote":
                await self.graph.record_vote(
                    voter_address=params.get("address") or params.get("voter"),
                    proposal_id=params.get("proposal_id"),
                    vote_option=params.get("vote_option") or params.get("option"),
                    tx_hash=tx_hash,
                    timestamp=timestamp
                )
            
            elif operation_type == "proposal_submission":
                # Could record proposal node here
                logger.debug(f"Recorded proposal submission: {tx_hash}")
            
            elif operation_type in ["contract_instantiation", "contract_execution"]:
                await self.graph.record_contract_execution(
                    executor_address=params.get("address") or params.get("sender"),
                    contract_address=params.get("contract_address"),
                    method=params.get("execute_msg", {}).get("method", "unknown"),
                    tx_hash=tx_hash,
                    success=True,
                    timestamp=timestamp
                )
            
            logger.info(f"Recorded {operation_type} in graph: {tx_hash}")
        
        except Exception as e:
            # Log error but don't propagate (graph failures shouldn't break operations)
            logger.error(f"Failed to record {operation_type} in graph: {e}")


# Export
__all__ = ["GraphMiddleware"]
```

**Test File**:

```python
# mcp-scrt/tests/unit/test_graph_middleware.py

import pytest
from unittest.mock import Mock, AsyncMock
from mcp_scrt.middleware.graph_middleware import GraphMiddleware


@pytest.fixture
def mock_graph_service():
    """Mock graph service."""
    graph = Mock()
    graph.record_delegation = AsyncMock()
    graph.record_transfer = AsyncMock()
    graph.record_vote = AsyncMock()
    graph.record_contract_execution = AsyncMock()
    return graph


@pytest.fixture
def middleware(mock_graph_service):
    """Create graph middleware with mock graph service."""
    return GraphMiddleware(graph_service=mock_graph_service, async_mode=False)


def test_should_record(middleware):
    """Test determining if operation should be recorded."""
    # Should record
    assert middleware._should_record("secret_delegate") is True
    assert middleware._should_record("secret_send_tokens") is True
    
    # Should not record
    assert middleware._should_record("secret_get_balance") is False
    assert middleware._should_record("secret_create_wallet") is False


@pytest.mark.asyncio
async def test_after_execute_skips_on_error(middleware, mock_graph_service):
    """Test after_execute doesn't record on error."""
    await middleware.after_execute(
        tool_name="secret_delegate",
        params={},
        result={},
        error=Exception("Test error")
    )
    
    mock_graph_service.record_delegation.assert_not_called()


@pytest.mark.asyncio
async def test_after_execute_skips_non_graph_operations(middleware, mock_graph_service):
    """Test after_execute skips non-graph operations."""
    await middleware.after_execute(
        tool_name="secret_get_balance",
        params={},
        result={},
        error=None
    )
    
    mock_graph_service.record_delegation.assert_not_called()


@pytest.mark.asyncio
async def test_record_delegation(middleware, mock_graph_service):
    """Test recording a delegation."""
    await middleware.after_execute(
        tool_name="secret_delegate",
        params={
            "address": "secret1abc",
            "validator_address": "secretvaloper1xyz",
            "amount": "1000000"
        },
        result={"tx_hash": "ABC123"},
        error=None
    )
    
    mock_graph_service.record_delegation.assert_called_once()
    call_args = mock_graph_service.record_delegation.call_args[1]
    assert call_args["delegator_address"] == "secret1abc"
    assert call_args["validator_address"] == "secretvaloper1xyz"
    assert call_args["tx_hash"] == "ABC123"


@pytest.mark.asyncio
async def test_record_transfer(middleware, mock_graph_service):
    """Test recording a transfer."""
    await middleware.after_execute(
        tool_name="secret_send_tokens",
        params={
            "address": "secret1abc",
            "recipient": "secret1def",
            "amount": "500000"
        },
        result={"tx_hash": "XYZ789"},
        error=None
    )
    
    mock_graph_service.record_transfer.assert_called_once()
    call_args = mock_graph_service.record_transfer.call_args[1]
    assert call_args["from_address"] == "secret1abc"
    assert call_args["to_address"] == "secret1def"
    assert call_args["tx_hash"] == "XYZ789"


@pytest.mark.asyncio
async def test_record_vote(middleware, mock_graph_service):
    """Test recording a vote."""
    await middleware.after_execute(
        tool_name="secret_vote_proposal",
        params={
            "address": "secret1abc",
            "proposal_id": 42,
            "vote_option": "YES"
        },
        result={"tx_hash": "VOTE123"},
        error=None
    )
    
    mock_graph_service.record_vote.assert_called_once()
    call_args = mock_graph_service.record_vote.call_args[1]
    assert call_args["voter_address"] == "secret1abc"
    assert call_args["proposal_id"] == 42
    assert call_args["vote_option"] == "YES"


@pytest.mark.asyncio
async def test_record_contract_execution(middleware, mock_graph_service):
    """Test recording a contract execution."""
    await middleware.after_execute(
        tool_name="secret_execute_contract",
        params={
            "address": "secret1abc",
            "contract_address": "secret1contract",
            "execute_msg": {"method": "transfer"}
        },
        result={"tx_hash": "CONTRACT123"},
        error=None
    )
    
    mock_graph_service.record_contract_execution.assert_called_once()
    call_args = mock_graph_service.record_contract_execution.call_args[1]
    assert call_args["executor_address"] == "secret1abc"
    assert call_args["contract_address"] == "secret1contract"


@pytest.mark.asyncio
async def test_error_isolation(middleware, mock_graph_service):
    """Test that graph errors don't propagate."""
    # Make graph service raise an error
    mock_graph_service.record_delegation.side_effect = Exception("Graph error")
    
    # Should not raise exception
    await middleware.after_execute(
        tool_name="secret_delegate",
        params={
            "address": "secret1abc",
            "validator_address": "secretvaloper1xyz",
            "amount": "1000000"
        },
        result={"tx_hash": "ABC123"},
        error=None
    )
    
    # Error should be logged but not raised
    mock_graph_service.record_delegation.assert_called_once()
```

**Success Criteria**:
- ✅ Middleware automatically records blockchain operations
- ✅ Graph updates are non-blocking (async mode)
- ✅ Errors are isolated (don't break operations)
- ✅ All operation types are supported
- ✅ All tests pass

---

## Task 1C.4: Telemetry Middleware

**Objective**: Create middleware for performance monitoring and tool usage analytics.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/middleware/telemetry.py
mcp-scrt/tests/unit/test_telemetry.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/middleware/telemetry.py

"""
Telemetry middleware for performance monitoring and analytics.

This middleware provides:
- Tool execution time tracking
- Success/failure rate monitoring
- Parameter size tracking
- Result size tracking
- Usage analytics
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutionMetrics:
    """Metrics for a single tool execution."""
    tool_name: str
    start_time: float
    end_time: float
    duration_ms: float
    success: bool
    params_size: int
    result_size: int
    error_type: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class ToolStatistics:
    """Aggregated statistics for a tool."""
    tool_name: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    avg_duration_ms: float
    min_duration_ms: float
    max_duration_ms: float
    total_duration_ms: float


class TelemetryMiddleware:
    """
    Middleware for performance monitoring and analytics.
    
    Features:
    - Execution time tracking
    - Success/failure monitoring
    - Size metrics
    - Usage analytics
    - Performance statistics
    """
    
    def __init__(
        self,
        redis_client,
        retention_limit: int = 10000
    ):
        """
        Initialize telemetry middleware.
        
        Args:
            redis_client: Redis client for storing metrics
            retention_limit: Maximum number of metric records to retain
        """
        self.redis = redis_client
        self.retention_limit = retention_limit
        logger.info("Initialized TelemetryMiddleware")
    
    def before_execute(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute before tool runs - record start time.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
            
        Returns:
            Context dict with start time and sizes
        """
        context = {
            "tool_name": tool_name,
            "start_time": time.time(),
            "params_size": len(str(params))
        }
        
        return context
    
    async def after_execute(
        self,
        tool_name: str,
        params: Dict[str, Any],
        result: Any,
        context: Dict[str, Any],
        error: Optional[Exception] = None
    ):
        """
        Execute after tool runs - record metrics.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
            result: Tool execution result
            context: Context from before_execute
            error: Exception if tool failed
        """
        end_time = time.time()
        start_time = context.get("start_time", end_time)
        duration = end_time - start_time
        duration_ms = duration * 1000
        
        # Create metrics
        metrics = ExecutionMetrics(
            tool_name=tool_name,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            success=error is None,
            params_size=context.get("params_size", 0),
            result_size=len(str(result)) if result else 0,
            error_type=type(error).__name__ if error else None
        )
        
        # Store metrics
        await self._store_metrics(metrics)
        
        # Update statistics
        await self._update_statistics(metrics)
        
        # Log metrics
        status = "SUCCESS" if metrics.success else "FAILURE"
        logger.info(
            f"[{status}] {tool_name} completed in {duration_ms:.2f}ms"
        )
    
    async def _store_metrics(self, metrics: ExecutionMetrics):
        """
        Store execution metrics in Redis.
        
        Args:
            metrics: Execution metrics
        """
        # Store in time-series list
        self.redis.redis.lpush(
            "telemetry:metrics:all",
            metrics.__dict__
        )
        
        # Trim to retention limit
        self.redis.redis.ltrim(
            "telemetry:metrics:all",
            0,
            self.retention_limit - 1
        )
        
        # Store by tool name
        self.redis.redis.lpush(
            f"telemetry:metrics:tool:{metrics.tool_name}",
            metrics.__dict__
        )
        self.redis.redis.ltrim(
            f"telemetry:metrics:tool:{metrics.tool_name}",
            0,
            999  # Keep last 1000 per tool
        )
    
    async def _update_statistics(self, metrics: ExecutionMetrics):
        """
        Update aggregated statistics.
        
        Args:
            metrics: Execution metrics
        """
        tool_name = metrics.tool_name
        
        # Update counters
        self.redis.hincrby("telemetry:stats:total_executions", tool_name, 1)
        
        if metrics.success:
            self.redis.hincrby("telemetry:stats:successful", tool_name, 1)
        else:
            self.redis.hincrby("telemetry:stats:failed", tool_name, 1)
            # Track error types
            if metrics.error_type:
                self.redis.hincrby(
                    f"telemetry:stats:errors:{tool_name}",
                    metrics.error_type,
                    1
                )
        
        # Update duration statistics (using sorted set for min/max/avg)
        self.redis.redis.zadd(
            f"telemetry:stats:durations:{tool_name}",
            {metrics.timestamp: metrics.duration_ms}
        )
        
        # Keep only recent durations (last 1000)
        self.redis.redis.zremrangebyrank(
            f"telemetry:stats:durations:{tool_name}",
            0,
            -1001
        )
    
    async def get_tool_statistics(
        self,
        tool_name: str
    ) -> Optional[ToolStatistics]:
        """
        Get aggregated statistics for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool statistics or None if no data
        """
        # Get counters
        total = int(
            self.redis.hget("telemetry:stats:total_executions", tool_name) or 0
        )
        
        if total == 0:
            return None
        
        successful = int(
            self.redis.hget("telemetry:stats:successful", tool_name) or 0
        )
        failed = int(
            self.redis.hget("telemetry:stats:failed", tool_name) or 0
        )
        
        success_rate = (successful / total * 100) if total > 0 else 0.0
        
        # Get duration statistics
        durations_key = f"telemetry:stats:durations:{tool_name}"
        durations = [
            float(score)
            for score in self.redis.redis.zrange(
                durations_key, 0, -1, withscores=True
            )[1::2]  # Get only scores
        ]
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            total_duration = sum(durations)
        else:
            avg_duration = 0.0
            min_duration = 0.0
            max_duration = 0.0
            total_duration = 0.0
        
        return ToolStatistics(
            tool_name=tool_name,
            total_executions=total,
            successful_executions=successful,
            failed_executions=failed,
            success_rate=success_rate,
            avg_duration_ms=avg_duration,
            min_duration_ms=min_duration,
            max_duration_ms=max_duration,
            total_duration_ms=total_duration
        )
    
    async def get_all_statistics(self) -> Dict[str, ToolStatistics]:
        """
        Get statistics for all tools.
        
        Returns:
            Dict mapping tool name to statistics
        """
        # Get all tool names from counters
        tool_counts = self.redis.hgetall("telemetry:stats:total_executions")
        
        statistics = {}
        for tool_name in tool_counts.keys():
            stats = await self.get_tool_statistics(tool_name)
            if stats:
                statistics[tool_name] = stats
        
        return statistics
    
    async def get_recent_metrics(
        self,
        tool_name: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        Get recent execution metrics.
        
        Args:
            tool_name: Optional tool name filter
            limit: Maximum number of metrics to return
            
        Returns:
            List of recent metrics
        """
        if tool_name:
            key = f"telemetry:metrics:tool:{tool_name}"
        else:
            key = "telemetry:metrics:all"
        
        metrics_data = self.redis.redis.lrange(key, 0, limit - 1)
        
        return [
            ExecutionMetrics(**data)
            for data in metrics_data
        ]
    
    async def get_error_breakdown(
        self,
        tool_name: str
    ) -> Dict[str, int]:
        """
        Get breakdown of errors for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dict mapping error type to count
        """
        return self.redis.hgetall(f"telemetry:stats:errors:{tool_name}")
    
    async def reset_statistics(self):
        """Reset all telemetry statistics."""
        patterns = [
            "telemetry:stats:*",
            "telemetry:metrics:*"
        ]
        
        for pattern in patterns:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        
        logger.info("Telemetry statistics reset")


# Export
__all__ = ["TelemetryMiddleware", "ExecutionMetrics", "ToolStatistics"]
```

**Test File** (abbreviated):

```python
# mcp-scrt/tests/unit/test_telemetry.py

import pytest
from unittest.mock import Mock, MagicMock
import time
from mcp_scrt.middleware.telemetry import TelemetryMiddleware, ExecutionMetrics


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis = Mock()
    redis.redis = Mock()
    redis.redis.lpush = Mock()
    redis.redis.ltrim = Mock()
    redis.redis.zadd = Mock()
    redis.redis.zrange = Mock(return_value=[])
    redis.redis.zremrangebyrank = Mock()
    redis.redis.lrange = Mock(return_value=[])
    redis.hincrby = Mock()
    redis.hget = Mock(return_value=0)
    redis.hgetall = Mock(return_value={})
    return redis


@pytest.fixture
def middleware(mock_redis):
    """Create telemetry middleware with mock Redis."""
    return TelemetryMiddleware(redis_client=mock_redis)


def test_before_execute(middleware):
    """Test before_execute records context."""
    context = middleware.before_execute(
        "test_tool",
        {"param1": "value1"}
    )
    
    assert "tool_name" in context
    assert "start_time" in context
    assert "params_size" in context
    assert context["tool_name"] == "test_tool"


@pytest.mark.asyncio
async def test_after_execute_success(middleware, mock_redis):
    """Test after_execute records successful execution."""
    context = {
        "tool_name": "test_tool",
        "start_time": time.time() - 0.1,  # 100ms ago
        "params_size": 50
    }
    
    await middleware.after_execute(
        tool_name="test_tool",
        params={},
        result={"success": True},
        context=context,
        error=None
    )
    
    # Verify metrics were stored
    mock_redis.redis.lpush.assert_called()
    mock_redis.hincrby.assert_called()


@pytest.mark.asyncio
async def test_after_execute_failure(middleware, mock_redis):
    """Test after_execute records failed execution."""
    context = {
        "tool_name": "test_tool",
        "start_time": time.time(),
        "params_size": 50
    }
    
    await middleware.after_execute(
        tool_name="test_tool",
        params={},
        result=None,
        context=context,
        error=ValueError("Test error")
    )
    
    # Verify failure was recorded
    mock_redis.hincrby.assert_any_call(
        "telemetry:stats:failed",
        "test_tool",
        1
    )


@pytest.mark.asyncio
async def test_get_tool_statistics(middleware, mock_redis):
    """Test getting tool statistics."""
    mock_redis.hget.side_effect = [100, 90, 10]  # total, successful, failed
    mock_redis.redis.zrange.return_value = [100.0, 200.0, 150.0]
    
    stats = await middleware.get_tool_statistics("test_tool")
    
    assert stats is not None
    assert stats.total_executions == 100
    assert stats.successful_executions == 90
    assert stats.failed_executions == 10
    assert stats.success_rate == 90.0
```

**Success Criteria**:
- ✅ Middleware tracks execution metrics
- ✅ Statistics are aggregated correctly
- ✅ Error types are tracked
- ✅ Performance metrics are calculated
- ✅ All tests pass

---

## Summary of Part 1C Completed

You have now completed the **Cache Service & Middleware Layer**:

✅ **Cache Service**:
- Smart TTL management based on data types
- Pattern-based cache invalidation
- Cache-aside pattern implementation
- Performance statistics and analytics

✅ **Cache Middleware**:
- Automatic caching of read operations
- Automatic invalidation on write operations
- Consistent cache key generation
- Non-invasive integration

✅ **Graph Middleware**:
- Automatic graph recording for blockchain operations
- Non-blocking async updates
- Error isolation (graph failures don't break operations)
- Support for all operation types

✅ **Telemetry Middleware**:
- Execution time tracking
- Success/failure rate monitoring
- Performance statistics
- Error type tracking

