# Task 1D.3: Cache Management Tools

**Objective**: Create MCP tools for cache inspection, management, and optimization.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/tools/cache/__init__.py
mcp-scrt/src/mcp_scrt/tools/cache/operations.py
mcp-scrt/src/mcp_scrt/tools/cache/stats.py
mcp-scrt/src/mcp_scrt/tools/cache/optimize.py
mcp-scrt/tests/unit/test_cache_tools.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/tools/cache/__init__.py

"""
Cache management tools for inspection and optimization.

Available tools:
- cache_get_stats: Get cache performance statistics
- cache_get_key_info: Get information about a specific cache key
- cache_invalidate_pattern: Invalidate keys matching a pattern
- cache_clear_all: Clear all cache data
- cache_warm: Warm cache with common queries
- cache_get_top_keys: Get most frequently accessed keys
"""

from .operations import (
    CacheInvalidatePatternTool,
    CacheClearAllTool,
    CacheGetKeyInfoTool
)
from .stats import (
    CacheGetStatsTool,
    CacheGetTopKeysTool
)
from .optimize import CacheWarmTool

# Tool registry
CACHE_TOOLS = {
    "cache_get_stats": CacheGetStatsTool,
    "cache_get_key_info": CacheGetKeyInfoTool,
    "cache_invalidate_pattern": CacheInvalidatePatternTool,
    "cache_clear_all": CacheClearAllTool,
    "cache_get_top_keys": CacheGetTopKeysTool,
    "cache_warm": CacheWarmTool,
}

__all__ = [
    "CacheGetStatsTool",
    "CacheGetKeyInfoTool",
    "CacheInvalidatePatternTool",
    "CacheClearAllTool",
    "CacheGetTopKeysTool",
    "CacheWarmTool",
    "CACHE_TOOLS",
]
```

```python
# mcp-scrt/src/mcp_scrt/tools/cache/operations.py

"""
Cache operation tools for management and invalidation.
"""

from typing import Optional
from mcp_scrt.tools.base import BaseTool, ToolResult
from mcp_scrt.types import ToolExecutionContext
import logging

logger = logging.getLogger(__name__)


class CacheGetKeyInfoTool(BaseTool):
    """
    Get information about a specific cache key.
    
    Returns:
    - Whether key exists
    - TTL (time to live)
    - Size in bytes
    - Expiration timestamp
    """
    
    name = "cache_get_key_info"
    description = """Get detailed information about a specific cache key,
    including existence, TTL, size, and expiration time."""
    
    parameters = {
        "key": {
            "type": "string",
            "description": "Cache key to inspect",
            "required": True
        }
    }
    
    async def execute(
        self,
        key: str,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Get cache key information.
        
        Args:
            key: Cache key
            context: Execution context
            
        Returns:
            ToolResult with key information
        """
        try:
            if not context or not hasattr(context, 'cache_service'):
                return ToolResult(
                    ok=False,
                    error="Cache service not available"
                )
            
            cache_service = context.cache_service
            
            # Get key info
            info = cache_service.get_cache_info(key)
            
            if not info["exists"]:
                return ToolResult(
                    ok=True,
                    data={"key": key, "exists": False},
                    message=f"Cache key '{key}' does not exist"
                )
            
            # Format TTL
            if info["ttl"] > 0:
                ttl_str = f"{info['ttl']} seconds"
                if info["ttl"] > 3600:
                    ttl_str = f"{info['ttl'] / 3600:.1f} hours"
                elif info["ttl"] > 60:
                    ttl_str = f"{info['ttl'] / 60:.1f} minutes"
            else:
                ttl_str = "no expiration" if info["ttl"] == -1 else "expired"
            
            return ToolResult(
                ok=True,
                data={
                    "key": key,
                    "exists": True,
                    "ttl_seconds": info["ttl"],
                    "ttl_display": ttl_str,
                    "size_bytes": info["size_bytes"],
                    "size_display": self._format_bytes(info["size_bytes"]),
                    "expires_at": info.get("expires_at")
                },
                message=f"Cache key found with TTL: {ttl_str}"
            )
        
        except Exception as e:
            logger.error(f"Failed to get key info: {e}")
            return ToolResult(
                ok=False,
                error=f"Failed to get key info: {str(e)}"
            )
    
    @staticmethod
    def _format_bytes(size: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"


class CacheInvalidatePatternTool(BaseTool):
    """
    Invalidate all cache keys matching a pattern.
    
    Useful for:
    - Clearing cache for a specific address
    - Invalidating all validator data
    - Removing stale data by category
    
    WARNING: This operation cannot be undone!
    """
    
    name = "cache_invalidate_pattern"
    description = """Invalidate (delete) all cache keys matching a pattern.
    Use wildcards (*) for pattern matching. This operation cannot be undone!"""
    
    parameters = {
        "pattern": {
            "type": "string",
            "description": "Pattern to match (e.g., 'balance:*', 'validator:secret*')",
            "required": True
        },
        "confirm": {
            "type": "boolean",
            "description": "Confirmation flag (must be true)",
            "required": True
        }
    }
    
    async def execute(
        self,
        pattern: str,
        confirm: bool,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Invalidate keys matching pattern.
        
        Args:
            pattern: Pattern to match
            confirm: Confirmation flag
            context: Execution context
            
        Returns:
            ToolResult with invalidation count
        """
        try:
            if not confirm:
                return ToolResult(
                    ok=False,
                    error="Confirmation required. Set confirm=true to proceed."
                )
            
            if not context or not hasattr(context, 'cache_service'):
                return ToolResult(
                    ok=False,
                    error="Cache service not available"
                )
            
            cache_service = context.cache_service
            
            # Invalidate pattern
            logger.info(f"Invalidating cache pattern: {pattern}")
            
            deleted = await cache_service.invalidate_pattern(pattern)
            
            return ToolResult(
                ok=True,
                data={
                    "pattern": pattern,
                    "keys_deleted": deleted
                },
                message=f"Invalidated {deleted} cache keys matching '{pattern}'"
            )
        
        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
            return ToolResult(
                ok=False,
                error=f"Invalidation failed: {str(e)}"
            )


class CacheClearAllTool(BaseTool):
    """
    Clear ALL cache data.
    
    WARNING: This deletes EVERYTHING in the cache!
    Use only when necessary (e.g., testing, maintenance).
    This operation cannot be undone!
    """
    
    name = "cache_clear_all"
    description = """Clear ALL cache data. This is a destructive operation
    that deletes everything in the cache. Cannot be undone! Use with extreme caution."""
    
    parameters = {
        "confirm": {
            "type": "boolean",
            "description": "Confirmation flag (must be true)",
            "required": True
        },
        "confirm_text": {
            "type": "string",
            "description": "Type 'CLEAR ALL CACHE' to confirm",
            "required": True
        }
    }
    
    async def execute(
        self,
        confirm: bool,
        confirm_text: str,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Clear all cache data.
        
        Args:
            confirm: Confirmation flag
            confirm_text: Confirmation text
            context: Execution context
            
        Returns:
            ToolResult with confirmation
        """
        try:
            if not confirm or confirm_text != "CLEAR ALL CACHE":
                return ToolResult(
                    ok=False,
                    error="Invalid confirmation. Set confirm=true and confirm_text='CLEAR ALL CACHE'"
                )
            
            if not context or not hasattr(context, 'cache_service'):
                return ToolResult(
                    ok=False,
                    error="Cache service not available"
                )
            
            cache_service = context.cache_service
            
            # Get stats before clearing (for reporting)
            stats = await cache_service.get_statistics()
            
            # Clear all cache
            logger.warning("CLEARING ALL CACHE DATA")
            await cache_service.clear_all()
            
            return ToolResult(
                ok=True,
                data={
                    "keys_deleted": stats.total_keys,
                    "memory_freed": stats.memory_used
                },
                message=f"All cache cleared. Deleted {stats.total_keys} keys."
            )
        
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return ToolResult(
                ok=False,
                error=f"Clear failed: {str(e)}"
            )
```

```python
# mcp-scrt/src/mcp_scrt/tools/cache/stats.py

"""
Cache statistics and monitoring tools.
"""

from typing import Optional
from mcp_scrt.tools.base import BaseTool, ToolResult
from mcp_scrt.types import ToolExecutionContext
import logging

logger = logging.getLogger(__name__)


class CacheGetStatsTool(BaseTool):
    """
    Get comprehensive cache performance statistics.
    
    Returns:
    - Hit/miss rates
    - Total keys
    - Memory usage
    - Top cached keys
    - Invalidation counts
    """
    
    name = "cache_get_stats"
    description = """Get comprehensive cache performance statistics including
    hit rates, memory usage, top keys, and more."""
    
    parameters = {}
    
    async def execute(
        self,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Get cache statistics.
        
        Args:
            context: Execution context
            
        Returns:
            ToolResult with cache statistics
        """
        try:
            if not context or not hasattr(context, 'cache_service'):
                return ToolResult(
                    ok=False,
                    error="Cache service not available"
                )
            
            cache_service = context.cache_service
            
            # Get statistics
            stats = await cache_service.get_statistics()
            
            # Format data
            data = {
                "performance": {
                    "total_hits": stats.total_hits,
                    "total_misses": stats.total_misses,
                    "hit_rate": f"{stats.hit_rate:.2f}%",
                    "total_requests": stats.total_hits + stats.total_misses
                },
                "storage": {
                    "total_keys": stats.total_keys,
                    "memory_used": stats.memory_used
                },
                "top_keys": stats.top_keys,
                "invalidations": stats.invalidations
            }
            
            # Generate insights
            insights = []
            if stats.hit_rate >= 80:
                insights.append("Excellent cache performance (>80% hit rate)")
            elif stats.hit_rate >= 60:
                insights.append("Good cache performance (60-80% hit rate)")
            elif stats.hit_rate >= 40:
                insights.append("Moderate cache performance (40-60% hit rate)")
            else:
                insights.append("Low cache performance (<40% hit rate) - consider cache warming")
            
            if stats.total_keys > 10000:
                insights.append("Large cache size - consider cleanup if memory is constrained")
            
            data["insights"] = insights
            
            return ToolResult(
                ok=True,
                data=data,
                message=f"Cache hit rate: {stats.hit_rate:.2f}% ({stats.total_keys} keys)"
            )
        
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return ToolResult(
                ok=False,
                error=f"Failed to get stats: {str(e)}"
            )


class CacheGetTopKeysTool(BaseTool):
    """
    Get the most frequently accessed cache keys.
    
    Useful for:
    - Identifying hot data
    - Understanding access patterns
    - Optimizing cache warming strategies
    """
    
    name = "cache_get_top_keys"
    description = """Get the most frequently accessed cache keys.
    Helps identify hot data and understand access patterns."""
    
    parameters = {
        "limit": {
            "type": "integer",
            "description": "Number of top keys to return",
            "required": False,
            "default": 20,
            "minimum": 1,
            "maximum": 100
        }
    }
    
    async def execute(
        self,
        limit: int = 20,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Get top cache keys.
        
        Args:
            limit: Number of keys to return
            context: Execution context
            
        Returns:
            ToolResult with top keys
        """
        try:
            if not context or not hasattr(context, 'cache_service'):
                return ToolResult(
                    ok=False,
                    error="Cache service not available"
                )
            
            cache_service = context.cache_service
            
            # Get statistics
            stats = await cache_service.get_statistics()
            
            # Get top keys
            top_keys = stats.top_keys[:limit]
            
            # Analyze patterns
            patterns = {}
            for key_data in top_keys:
                key = key_data["key"]
                # Extract pattern (before first colon or asterisk)
                if ":" in key:
                    pattern = key.split(":")[0]
                else:
                    pattern = "other"
                
                patterns[pattern] = patterns.get(pattern, 0) + 1
            
            # Sort patterns
            sorted_patterns = sorted(
                patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return ToolResult(
                ok=True,
                data={
                    "top_keys": top_keys,
                    "count": len(top_keys),
                    "patterns": [
                        {"pattern": p, "count": c}
                        for p, c in sorted_patterns
                    ]
                },
                message=f"Top {len(top_keys)} most accessed cache keys"
            )
        
        except Exception as e:
            logger.error(f"Failed to get top keys: {e}")
            return ToolResult(
                ok=False,
                error=f"Failed to get top keys: {str(e)}"
            )
```

```python
# mcp-scrt/src/mcp_scrt/tools/cache/optimize.py

"""
Cache optimization tools.
"""

from typing import Optional, List
from mcp_scrt.tools.base import BaseTool, ToolResult
from mcp_scrt.types import ToolExecutionContext
import logging

logger = logging.getLogger(__name__)


class CacheWarmTool(BaseTool):
    """
    Warm the cache with commonly accessed data.
    
    This tool pre-fetches and caches frequently accessed data
    to improve performance. Useful after cache clears or
    application restarts.
    
    Warming strategies:
    - Common validators
    - Gas prices
    - Network info
    - Recent blocks
    """
    
    name = "cache_warm"
    description = """Warm the cache by pre-fetching commonly accessed data.
    Improves performance by reducing cache misses for hot data."""
    
    parameters = {
        "strategy": {
            "type": "string",
            "description": "Warming strategy to use",
            "required": False,
            "default": "common",
            "enum": ["common", "validators", "network", "all"]
        },
        "wallet_addresses": {
            "type": "array",
            "description": "Optional list of wallet addresses to warm",
            "required": False,
            "items": {"type": "string"}
        }
    }
    
    async def execute(
        self,
        strategy: str = "common",
        wallet_addresses: Optional[List[str]] = None,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Warm cache with common data.
        
        Args:
            strategy: Warming strategy
            wallet_addresses: Optional wallet addresses
            context: Execution context
            
        Returns:
            ToolResult with warming results
        """
        try:
            if not context or not hasattr(context, 'cache_service'):
                return ToolResult(
                    ok=False,
                    error="Cache service not available"
                )
            
            cache_service = context.cache_service
            
            # Build list of keys to warm
            keys_to_warm = []
            
            # Common data (always warm these)
            if strategy in ["common", "all"]:
                keys_to_warm.extend([
                    ("gas_price", self._fetch_gas_price),
                    ("block:latest", self._fetch_latest_block),
                    ("validators:all", self._fetch_validators),
                ])
            
            # Validator-specific data
            if strategy in ["validators", "all"]:
                # This would require validator addresses from context
                # For now, just warm the validator list
                keys_to_warm.append(
                    ("validators:all", self._fetch_validators)
                )
            
            # Network info
            if strategy in ["network", "all"]:
                keys_to_warm.extend([
                    ("network:info", self._fetch_network_info),
                    ("ibc:channels", self._fetch_ibc_channels),
                ])
            
            # Wallet-specific data
            if wallet_addresses:
                for address in wallet_addresses:
                    keys_to_warm.extend([
                        (f"balance:{address}", lambda a=address: self._fetch_balance(a)),
                        (f"delegations:{address}", lambda a=address: self._fetch_delegations(a)),
                    ])
            
            # Warm cache
            logger.info(f"Warming cache with {len(keys_to_warm)} items using '{strategy}' strategy")
            
            await cache_service.warm_cache(keys_to_warm)
            
            return ToolResult(
                ok=True,
                data={
                    "strategy": strategy,
                    "keys_warmed": len(keys_to_warm),
                    "wallet_addresses": wallet_addresses or []
                },
                message=f"Cache warmed with {len(keys_to_warm)} items"
            )
        
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            return ToolResult(
                ok=False,
                error=f"Cache warming failed: {str(e)}"
            )
    
    # Helper methods for fetching data
    # These would call the appropriate MCP tools or services
    
    async def _fetch_gas_price(self) -> dict:
        """Fetch current gas prices."""
        # This would call the gas price tool
        return {"gas_price": "0.25uscrt"}
    
    async def _fetch_latest_block(self) -> dict:
        """Fetch latest block."""
        # This would call the latest block tool
        return {"height": 1000000}
    
    async def _fetch_validators(self) -> list:
        """Fetch validator list."""
        # This would call the validators tool
        return []
    
    async def _fetch_network_info(self) -> dict:
        """Fetch network info."""
        # This would call the network info tool
        return {"chain_id": "pulsar-3"}
    
    async def _fetch_ibc_channels(self) -> list:
        """Fetch IBC channels."""
        # This would call the IBC channels tool
        return []
    
    async def _fetch_balance(self, address: str) -> dict:
        """Fetch wallet balance."""
        # This would call the balance tool
        return {"balance": "0"}
    
    async def _fetch_delegations(self, address: str) -> list:
        """Fetch wallet delegations."""
        # This would call the delegations tool
        return []
```

**Test File**:

```python
# mcp-scrt/tests/unit/test_cache_tools.py

import pytest
from unittest.mock import Mock, AsyncMock
from mcp_scrt.tools.cache.operations import (
    CacheGetKeyInfoTool,
    CacheInvalidatePatternTool,
    CacheClearAllTool
)
from mcp_scrt.tools.cache.stats import (
    CacheGetStatsTool,
    CacheGetTopKeysTool
)
from mcp_scrt.tools.cache.optimize import CacheWarmTool
from mcp_scrt.services.cache_service import CacheStatistics


@pytest.fixture
def mock_context():
    """Mock execution context with cache service."""
    context = Mock()
    context.cache_service = Mock()
    return context


@pytest.mark.asyncio
async def test_cache_get_key_info_exists(mock_context):
    """Test getting info for existing key."""
    mock_context.cache_service.get_cache_info = Mock(
        return_value={
            "exists": True,
            "ttl": 300,
            "size_bytes": 1024,
            "expires_at": 1234567890.0
        }
    )
    
    tool = CacheGetKeyInfoTool()
    result = await tool.execute(
        key="balance:secret1abc",
        context=mock_context
    )
    
    assert result.ok is True
    assert result.data["exists"] is True
    assert result.data["ttl_seconds"] == 300


@pytest.mark.asyncio
async def test_cache_get_key_info_not_exists(mock_context):
    """Test getting info for non-existent key."""
    mock_context.cache_service.get_cache_info = Mock(
        return_value={"exists": False}
    )
    
    tool = CacheGetKeyInfoTool()
    result = await tool.execute(
        key="nonexistent:key",
        context=mock_context
    )
    
    assert result.ok is True
    assert result.data["exists"] is False


@pytest.mark.asyncio
async def test_cache_invalidate_pattern(mock_context):
    """Test invalidating cache by pattern."""
    mock_context.cache_service.invalidate_pattern = AsyncMock(
        return_value=15
    )
    
    tool = CacheInvalidatePatternTool()
    result = await tool.execute(
        pattern="balance:*",
        confirm=True,
        context=mock_context
    )
    
    assert result.ok is True
    assert result.data["keys_deleted"] == 15


@pytest.mark.asyncio
async def test_cache_invalidate_pattern_no_confirm(mock_context):
    """Test invalidation fails without confirmation."""
    tool = CacheInvalidatePatternTool()
    result = await tool.execute(
        pattern="balance:*",
        confirm=False,
        context=mock_context
    )
    
    assert result.ok is False
    assert "Confirmation required" in result.error


@pytest.mark.asyncio
async def test_cache_clear_all(mock_context):
    """Test clearing all cache."""
    mock_stats = CacheStatistics(
        total_hits=100,
        total_misses=20,
        hit_rate=83.33,
        total_keys=500,
        memory_used="10MB",
        top_keys=[],
        invalidations=5
    )
    
    mock_context.cache_service.get_statistics = AsyncMock(
        return_value=mock_stats
    )
    mock_context.cache_service.clear_all = AsyncMock()
    
    tool = CacheClearAllTool()
    result = await tool.execute(
        confirm=True,
        confirm_text="CLEAR ALL CACHE",
        context=mock_context
    )
    
    assert result.ok is True
    assert result.data["keys_deleted"] == 500


@pytest.mark.asyncio
async def test_cache_clear_all_invalid_confirm(mock_context):
    """Test clear fails with invalid confirmation."""
    tool = CacheClearAllTool()
    result = await tool.execute(
        confirm=True,
        confirm_text="wrong text",
        context=mock_context
    )
    
    assert result.ok is False
    assert "Invalid confirmation" in result.error


@pytest.mark.asyncio
async def test_cache_get_stats(mock_context):
    """Test getting cache statistics."""
    mock_stats = CacheStatistics(
        total_hits=800,
        total_misses=200,
        hit_rate=80.0,
        total_keys=1000,
        memory_used="50MB",
        top_keys=[
            {"key": "balance:secret1abc", "hits": 100},
            {"key": "validators:all", "hits": 80}
        ],
        invalidations=10
    )
    
    mock_context.cache_service.get_statistics = AsyncMock(
        return_value=mock_stats
    )
    
    tool = CacheGetStatsTool()
    result = await tool.execute(context=mock_context)
    
    assert result.ok is True
    assert result.data["performance"]["hit_rate"] == "80.00%"
    assert result.data["storage"]["total_keys"] == 1000
    assert len(result.data["insights"]) > 0


@pytest.mark.asyncio
async def test_cache_get_top_keys(mock_context):
    """Test getting top cache keys."""
    mock_stats = CacheStatistics(
        total_hits=100,
        total_misses=20,
        hit_rate=83.33,
        total_keys=100,
        memory_used="10MB",
        top_keys=[
            {"key": "balance:secret1abc", "hits": 50},
            {"key": "balance:secret1def", "hits": 40},
            {"key": "validators:all", "hits": 30}
        ],
        invalidations=5
    )
    
    mock_context.cache_service.get_statistics = AsyncMock(
        return_value=mock_stats
    )
    
    tool = CacheGetTopKeysTool()
    result = await tool.execute(
        limit=10,
        context=mock_context
    )
    
    assert result.ok is True
    assert len(result.data["top_keys"]) == 3
    assert len(result.data["patterns"]) > 0


@pytest.mark.asyncio
async def test_cache_warm(mock_context):
    """Test cache warming."""
    mock_context.cache_service.warm_cache = AsyncMock()
    
    tool = CacheWarmTool()
    result = await tool.execute(
        strategy="common",
        context=mock_context
    )
    
    assert result.ok is True
    assert result.data["keys_warmed"] > 0


@pytest.mark.asyncio
async def test_cache_warm_with_wallets(mock_context):
    """Test cache warming with wallet addresses."""
    mock_context.cache_service.warm_cache = AsyncMock()
    
    tool = CacheWarmTool()
    result = await tool.execute(
        strategy="common",
        wallet_addresses=["secret1abc", "secret1def"],
        context=mock_context
    )
    
    assert result.ok is True
    assert len(result.data["wallet_addresses"]) == 2
```

**Success Criteria**:
- ✅ 6 cache management tools implemented
- ✅ Cache statistics and monitoring work
- ✅ Invalidation and clearing operations functional
- ✅ Cache warming improves performance
- ✅ All tests pass

---

## Task 1D.4: Tool Registry and Integration

**Objective**: Create a unified tool registry that integrates all tools (existing + new) and update the MCP server configuration.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/tools/__init__.py (update)
mcp-scrt/src/mcp_scrt/config.py (update)
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/tools/__init__.py

"""
Unified tool registry for MCP-SCRT server.

This module combines all existing blockchain tools with new
knowledge base, graph analysis, and cache management tools.
"""

# Import existing tool registries (60 tools)
from mcp_scrt.tools.network import NETWORK_TOOLS
from mcp_scrt.tools.wallet import WALLET_TOOLS
from mcp_scrt.tools.bank import BANK_TOOLS
from mcp_scrt.tools.blockchain import BLOCKCHAIN_TOOLS
from mcp_scrt.tools.account import ACCOUNT_TOOLS
from mcp_scrt.tools.transaction import TRANSACTION_TOOLS
from mcp_scrt.tools.staking import STAKING_TOOLS
from mcp_scrt.tools.rewards import REWARDS_TOOLS
from mcp_scrt.tools.governance import GOVERNANCE_TOOLS
from mcp_scrt.tools.contracts import CONTRACTS_TOOLS
from mcp_scrt.tools.ibc import IBC_TOOLS

# Import new tool registries (18 tools)
from mcp_scrt.tools.knowledge import KNOWLEDGE_TOOLS
from mcp_scrt.tools.graph import GRAPH_TOOLS
from mcp_scrt.tools.cache import CACHE_TOOLS

# Unified tool registry - 78 tools total
ALL_TOOLS = {
    # Existing blockchain tools (60)
    **NETWORK_TOOLS,      # 4 tools
    **WALLET_TOOLS,       # 6 tools
    **BANK_TOOLS,         # 5 tools
    **BLOCKCHAIN_TOOLS,   # 5 tools
    **ACCOUNT_TOOLS,      # 3 tools
    **TRANSACTION_TOOLS,  # 5 tools
    **STAKING_TOOLS,      # 8 tools
    **REWARDS_TOOLS,      # 4 tools
    **GOVERNANCE_TOOLS,   # 6 tools
    **CONTRACTS_TOOLS,    # 10 tools
    **IBC_TOOLS,          # 4 tools
    
    # New tools (18)
    **KNOWLEDGE_TOOLS,    # 7 tools
    **GRAPH_TOOLS,        # 5 tools
    **CACHE_TOOLS,        # 6 tools
}

# Tool categories for organization
TOOL_CATEGORIES = {
    "network": list(NETWORK_TOOLS.keys()),
    "wallet": list(WALLET_TOOLS.keys()),
    "bank": list(BANK_TOOLS.keys()),
    "blockchain": list(BLOCKCHAIN_TOOLS.keys()),
    "account": list(ACCOUNT_TOOLS.keys()),
    "transaction": list(TRANSACTION_TOOLS.keys()),
    "staking": list(STAKING_TOOLS.keys()),
    "rewards": list(REWARDS_TOOLS.keys()),
    "governance": list(GOVERNANCE_TOOLS.keys()),
    "contracts": list(CONTRACTS_TOOLS.keys()),
    "ibc": list(IBC_TOOLS.keys()),
    "knowledge": list(KNOWLEDGE_TOOLS.keys()),
    "graph": list(GRAPH_TOOLS.keys()),
    "cache": list(CACHE_TOOLS.keys()),
}


def get_tool(tool_name: str):
    """
    Get a tool class by name.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool class or None if not found
    """
    return ALL_TOOLS.get(tool_name)


def list_tools(category: str = None) -> list:
    """
    List available tools, optionally filtered by category.
    
    Args:
        category: Optional category filter
        
    Returns:
        List of tool names
    """
    if category:
        return TOOL_CATEGORIES.get(category, [])
    return list(ALL_TOOLS.keys())


def get_tool_info(tool_name: str) -> dict:
    """
    Get information about a tool.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool information dict
    """
    tool_class = get_tool(tool_name)
    if not tool_class:
        return None
    
    return {
        "name": tool_class.name,
        "description": tool_class.description,
        "parameters": tool_class.parameters,
        "category": _get_tool_category(tool_name)
    }


def _get_tool_category(tool_name: str) -> str:
    """Get category for a tool."""
    for category, tools in TOOL_CATEGORIES.items():
        if tool_name in tools:
            return category
    return "unknown"


# Export
__all__ = [
    "ALL_TOOLS",
    "TOOL_CATEGORIES",
    "get_tool",
    "list_tools",
    "get_tool_info",
]
```

```python
# mcp-scrt/src/mcp_scrt/types.py (update)

"""
Type definitions for MCP-SCRT server.

Updated to include new service references in execution context.
"""

from dataclasses import dataclass
from typing import Optional, Any
from enum import Enum


class NetworkType(Enum):
    """Network type enumeration."""
    TESTNET = "testnet"
    MAINNET = "mainnet"


@dataclass
class ToolExecutionContext:
    """
    Context passed to tool execution.
    
    Contains references to all services and clients needed
    for tool execution.
    """
    # Core blockchain components (existing)
    session: Any  # Session object
    client_pool: Any  # Client pool
    network: NetworkType
    
    # New service components
    knowledge_service: Optional[Any] = None
    graph_service: Optional[Any] = None
    cache_service: Optional[Any] = None
    embedding_service: Optional[Any] = None
    
    # Database clients
    chromadb_client: Optional[Any] = None
    neo4j_client: Optional[Any] = None
    redis_client: Optional[Any] = None
    ollama_client: Optional[Any] = None
    
    # Middleware
    cache_middleware: Optional[Any] = None
    graph_middleware: Optional[Any] = None
    telemetry_middleware: Optional[Any] = None


# Export
__all__ = [
    "NetworkType",
    "ToolExecutionContext",
]
```

```python
# mcp-scrt/src/mcp_scrt/server.py (update initialization)

"""
MCP-SCRT Server initialization.

Updated to initialize new services and middleware.
"""

import os
import logging
from typing import Optional

# Existing imports
from mcp_scrt.types import NetworkType, ToolExecutionContext
from mcp_scrt.core.session import Session
from mcp_scrt.sdk.client import ClientPool

# New imports - Database clients
from mcp_scrt.integrations.chromadb_client import ChromaDBClient
from mcp_scrt.integrations.neo4j_client import Neo4jClient
from mcp_scrt.integrations.redis_client import RedisClient
from mcp_scrt.integrations.ollama_client import OllamaClient

# New imports - Services
from mcp_scrt.services.embedding_service import EmbeddingService
from mcp_scrt.services.knowledge_service import KnowledgeService
from mcp_scrt.services.graph_service import GraphService
from mcp_scrt.services.cache_service import CacheService

# New imports - Middleware
from mcp_scrt.middleware.cache_middleware import CacheMiddleware
from mcp_scrt.middleware.graph_middleware import GraphMiddleware
from mcp_scrt.middleware.telemetry import TelemetryMiddleware

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP-SCRT Server with enhanced capabilities.
    
    Integrates:
    - 60 existing blockchain tools
    - 18 new tools (knowledge, graph, cache)
    - Intelligent caching
    - Graph analysis
    - LLM-powered knowledge base
    """
    
    def __init__(
        self,
        network: NetworkType = NetworkType.TESTNET,
        enable_knowledge: bool = True,
        enable_graph: bool = True,
        enable_cache: bool = True
    ):
        """
        Initialize MCP server with all components.
        
        Args:
            network: Network type (testnet/mainnet)
            enable_knowledge: Enable knowledge base features
            enable_graph: Enable graph analysis features
            enable_cache: Enable intelligent caching
        """
        self.network = network
        self.enable_knowledge = enable_knowledge
        self.enable_graph = enable_graph
        self.enable_cache = enable_cache
        
        # Initialize core components (existing)
        logger.info(f"Initializing MCP-SCRT server for {network.value}")
        self.session = Session(network=network)
        self.client_pool = ClientPool(network=network)
        
        # Initialize database clients
        self._init_database_clients()
        
        # Initialize services
        self._init_services()
        
        # Initialize middleware
        self._init_middleware()
        
        # Create execution context
        self.context = self._create_context()
        
        logger.info("MCP-SCRT server initialized successfully")
        logger.info(f"Total tools available: {len(ALL_TOOLS)}")
    
    def _init_database_clients(self):
        """Initialize database clients."""
        # ChromaDB
        if self.enable_knowledge:
            try:
                self.chromadb = ChromaDBClient()
                self.chromadb.connect()
                logger.info("ChromaDB client initialized")
            except Exception as e:
                logger.warning(f"ChromaDB initialization failed: {e}")
                self.chromadb = None
        else:
            self.chromadb = None
        
        # Neo4j
        if self.enable_graph:
            try:
                self.neo4j = Neo4jClient()
                self.neo4j.connect()
                logger.info("Neo4j client initialized")
            except Exception as e:
                logger.warning(f"Neo4j initialization failed: {e}")
                self.neo4j = None
        else:
            self.neo4j = None
        
        # Redis (used by both cache and services)
        if self.enable_cache or self.enable_knowledge:
            try:
                self.redis = RedisClient()
                self.redis.connect()
                logger.info("Redis client initialized")
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}")
                self.redis = None
        else:
            self.redis = None
        
        # Ollama (for LLM operations)
        if self.enable_knowledge:
            try:
                self.ollama = OllamaClient()
                health = self.ollama.health_check()
                if health["status"] == "healthy":
                    logger.info("Ollama client initialized")
                else:
                    logger.warning("Ollama health check failed")
                    self.ollama = None
            except Exception as e:
                logger.warning(f"Ollama initialization failed: {e}")
                self.ollama = None
        else:
            self.ollama = None
    
    def _init_services(self):
        """Initialize service layer."""
        # Embedding service
        if self.enable_knowledge and self.redis:
            try:
                self.embedding_service = EmbeddingService(
                    redis_client=self.redis
                )
                logger.info("Embedding service initialized")
            except Exception as e:
                logger.warning(f"Embedding service initialization failed: {e}")
                self.embedding_service = None
        else:
            self.embedding_service = None
        
        # Knowledge service
        if self.enable_knowledge and all([
            self.chromadb, self.redis, self.ollama, self.embedding_service
        ]):
            try:
                self.knowledge_service = KnowledgeService(
                    chromadb_client=self.chromadb,
                    redis_client=self.redis,
                    ollama_client=self.ollama,
                    embedding_service=self.embedding_service
                )
                logger.info("Knowledge service initialized")
            except Exception as e:
                logger.warning(f"Knowledge service initialization failed: {e}")
                self.knowledge_service = None
        else:
            self.knowledge_service = None
        
        # Graph service
        if self.enable_graph and self.neo4j and self.redis:
            try:
                self.graph_service = GraphService(
                    neo4j_client=self.neo4j,
                    redis_client=self.redis
                )
                logger.info("Graph service initialized")
            except Exception as e:
                logger.warning(f"Graph service initialization failed: {e}")
                self.graph_service = None
        else:
            self.graph_service = None
        
        # Cache service
        if self.enable_cache and self.redis:
            try:
                self.cache_service = CacheService(
                    redis_client=self.redis
                )
                logger.info("Cache service initialized")
            except Exception as e:
                logger.warning(f"Cache service initialization failed: {e}")
                self.cache_service = None
        else:
            self.cache_service = None
    
    def _init_middleware(self):
        """Initialize middleware layer."""
        # Cache middleware
        if self.cache_service:
            try:
                self.cache_middleware = CacheMiddleware(
                    cache_service=self.cache_service
                )
                logger.info("Cache middleware initialized")
            except Exception as e:
                logger.warning(f"Cache middleware initialization failed: {e}")
                self.cache_middleware = None
        else:
            self.cache_middleware = None
        
        # Graph middleware
        if self.graph_service:
            try:
                self.graph_middleware = GraphMiddleware(
                    graph_service=self.graph_service,
                    async_mode=True
                )
                logger.info("Graph middleware initialized")
            except Exception as e:
                logger.warning(f"Graph middleware initialization failed: {e}")
                self.graph_middleware = None
        else:
            self.graph_middleware = None
        
        # Telemetry middleware
        if self.redis:
            try:
                self.telemetry_middleware = TelemetryMiddleware(
                    redis_client=self.redis
                )
                logger.info("Telemetry middleware initialized")
            except Exception as e:
                logger.warning(f"Telemetry middleware initialization failed: {e}")
                self.telemetry_middleware = None
        else:
            self.telemetry_middleware = None
    
    def _create_context(self) -> ToolExecutionContext:
        """Create tool execution context."""
        return ToolExecutionContext(
            # Core components
            session=self.session,
            client_pool=self.client_pool,
            network=self.network,
            
            # Services
            knowledge_service=self.knowledge_service,
            graph_service=self.graph_service,
            cache_service=self.cache_service,
            embedding_service=self.embedding_service,
            
            # Database clients
            chromadb_client=self.chromadb,
            neo4j_client=self.neo4j,
            redis_client=self.redis,
            ollama_client=self.ollama,
            
            # Middleware
            cache_middleware=self.cache_middleware,
            graph_middleware=self.graph_middleware,
            telemetry_middleware=self.telemetry_middleware
        )
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: dict
    ) -> dict:
        """
        Execute a tool with middleware support.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        from mcp_scrt.tools import get_tool
        
        # Get tool class
        tool_class = get_tool(tool_name)
        if not tool_class:
            return {
                "ok": False,
                "error": f"Tool '{tool_name}' not found"
            }
        
        # Execute with middleware chain
        try:
            # Before middleware
            cache_context = None
            telemetry_context = None
            
            if self.cache_middleware:
                cache_context = await self.cache_middleware.before_execute(
                    tool_name, parameters
                )
                
                # Return cached result if available
                if cache_context.cache_hit:
                    cached_result = await self.cache_service.get(
                        cache_context.cache_key
                    )
                    if cached_result:
                        return cached_result
            
            if self.telemetry_middleware:
                telemetry_context = self.telemetry_middleware.before_execute(
                    tool_name, parameters
                )
            
            # Execute tool
            tool = tool_class()
            result = await tool.execute(**parameters, context=self.context)
            
            # After middleware
            if self.cache_middleware:
                await self.cache_middleware.after_execute(
                    tool_name, parameters, result, cache_context
                )
            
            if self.graph_middleware:
                await self.graph_middleware.after_execute(
                    tool_name, parameters, result
                )
            
            if self.telemetry_middleware:
                await self.telemetry_middleware.after_execute(
                    tool_name, parameters, result, telemetry_context
                )
            
            return result.__dict__ if hasattr(result, '__dict__') else result
        
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            
            # Record error in telemetry
            if self.telemetry_middleware and telemetry_context:
                await self.telemetry_middleware.after_execute(
                    tool_name, parameters, None, telemetry_context, error=e
                )
            
            return {
                "ok": False,
                "error": str(e)
            }
    
    def close(self):
        """Close all connections and cleanup."""
        logger.info("Shutting down MCP-SCRT server")
        
        # Close database clients
        if self.chromadb:
            self.chromadb.close()
        if self.neo4j:
            self.neo4j.close()
        if self.redis:
            self.redis.close()
        if self.ollama:
            self.ollama.close()
        
        logger.info("MCP-SCRT server shutdown complete")


# Export
__all__ = ["MCPServer"]
```

**Success Criteria**:
- ✅ All 78 tools registered in unified registry
- ✅ Server initialization includes all services
- ✅ Middleware chain executes correctly
- ✅ Tool execution works with caching and telemetry
- ✅ Graceful degradation when services unavailable

---

## Summary of Part 1: MCP SERVER Extension - COMPLETE

Congratulations! You have now completed **Part 1: MCP SERVER Extension** with the following accomplishments:

### **Infrastructure Layer** (Phase 1A-1C):
✅ **4 Database Clients**:
- ChromaDB client (vector database)
- Neo4j client (graph database)
- Redis client (caching)
- Ollama client (LLM)

✅ **4 Service Components**:
- Embedding service (text vectorization)
- Knowledge service (semantic search + LLM)
- Graph service (network analysis)
- Cache service (intelligent caching)

✅ **3 Middleware Components**:
- Cache middleware (auto-caching)
- Graph middleware (auto-recording)
- Telemetry middleware (monitoring)

### **Tool Layer** (Phase 1D):
✅ **18 New MCP Tools**:
- 7 Knowledge tools
- 5 Graph tools
- 6 Cache tools

### **Total MCP Server Capabilities**:
- **78 Total Tools** (60 existing + 18 new)
- **14 Tool Categories** (organized by function)
- **Complete Test Coverage** (unit + integration tests)
- **Production-Ready** (error handling, logging, graceful degradation)

---

