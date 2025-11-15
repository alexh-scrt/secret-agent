# Phase 1D: MCP Tools Implementation

## Overview

This phase implements the actual MCP tools that expose knowledge base, graph analysis, and cache management capabilities. These tools integrate with the services and middleware layers we built in previous phases.

---

## Task 1D.1: Knowledge Base Tools

**Objective**: Create MCP tools for knowledge base operations including semantic search, document management, and collection queries.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/tools/knowledge/__init__.py
mcp-scrt/src/mcp_scrt/tools/knowledge/search.py
mcp-scrt/src/mcp_scrt/tools/knowledge/add.py
mcp-scrt/src/mcp_scrt/tools/knowledge/update.py
mcp-scrt/src/mcp_scrt/tools/knowledge/delete.py
mcp-scrt/src/mcp_scrt/tools/knowledge/collections.py
mcp-scrt/tests/unit/test_knowledge_tools.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/tools/knowledge/__init__.py

"""
Knowledge base tools for semantic search and document management.

Available tools:
- knowledge_search: Semantic search with LLM synthesis
- knowledge_add_document: Add new document to knowledge base
- knowledge_update_document: Update existing document
- knowledge_delete_document: Delete document
- knowledge_list_collections: List available collections
- knowledge_get_collection_stats: Get collection statistics
"""

from .search import KnowledgeSearchTool, KnowledgeSearchAdvancedTool
from .add import KnowledgeAddDocumentTool
from .update import KnowledgeUpdateDocumentTool
from .delete import KnowledgeDeleteDocumentTool
from .collections import (
    KnowledgeListCollectionsTool,
    KnowledgeGetCollectionStatsTool
)

# Tool registry
KNOWLEDGE_TOOLS = {
    "knowledge_search": KnowledgeSearchTool,
    "knowledge_search_advanced": KnowledgeSearchAdvancedTool,
    "knowledge_add_document": KnowledgeAddDocumentTool,
    "knowledge_update_document": KnowledgeUpdateDocumentTool,
    "knowledge_delete_document": KnowledgeDeleteDocumentTool,
    "knowledge_list_collections": KnowledgeListCollectionsTool,
    "knowledge_get_collection_stats": KnowledgeGetCollectionStatsTool,
}

__all__ = [
    "KnowledgeSearchTool",
    "KnowledgeSearchAdvancedTool",
    "KnowledgeAddDocumentTool",
    "KnowledgeUpdateDocumentTool",
    "KnowledgeDeleteDocumentTool",
    "KnowledgeListCollectionsTool",
    "KnowledgeGetCollectionStatsTool",
    "KNOWLEDGE_TOOLS",
]
```

```python
# mcp-scrt/src/mcp_scrt/tools/knowledge/search.py

"""
Knowledge search tools for semantic search and LLM-synthesized responses.
"""

from typing import Optional, List, Dict, Any
from mcp_scrt.tools.base import BaseTool, ToolResult
from mcp_scrt.types import ToolExecutionContext
import logging

logger = logging.getLogger(__name__)


class KnowledgeSearchTool(BaseTool):
    """
    Search the knowledge base and get an LLM-synthesized natural response.
    
    This tool performs semantic search across the Secret Network knowledge base
    and uses an LLM to synthesize a natural, well-cited response.
    
    Perfect for:
    - Answering user questions about Secret Network
    - Providing educational content
    - Explaining concepts with sources
    """
    
    name = "knowledge_search"
    description = """Search the Secret Network knowledge base and get a comprehensive, 
    well-cited answer to your question. The response includes sources and relevance scores."""
    
    parameters = {
        "query": {
            "type": "string",
            "description": "Natural language question or search query",
            "required": True
        },
        "collection": {
            "type": "string",
            "description": "Optional collection to search (e.g., 'fundamentals', 'staking')",
            "required": False,
            "enum": [
                "fundamentals",
                "privacy_tech",
                "tokens",
                "staking",
                "contracts",
                "security",
                "faq"
            ]
        },
        "top_k": {
            "type": "integer",
            "description": "Number of source documents to use (1-10)",
            "required": False,
            "default": 5,
            "minimum": 1,
            "maximum": 10
        }
    }
    
    async def execute(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = 5,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Execute semantic search and synthesize response.
        
        Args:
            query: Search query
            collection: Optional collection filter
            top_k: Number of sources to use
            context: Execution context
            
        Returns:
            ToolResult with synthesized response and sources
        """
        try:
            # Get knowledge service from context
            if not context or not hasattr(context, 'knowledge_service'):
                return ToolResult(
                    ok=False,
                    error="Knowledge service not available"
                )
            
            knowledge_service = context.knowledge_service
            
            # Perform search and synthesis
            logger.info(f"Searching knowledge base: {query[:50]}...")
            
            response = await knowledge_service.search_and_synthesize(
                query=query,
                collection=collection,
                top_k=top_k,
                use_cache=True
            )
            
            # Format sources for display
            sources = [
                {
                    "title": result.document.title,
                    "collection": result.document.collection,
                    "similarity": f"{result.similarity:.1%}",
                    "rank": result.rank,
                    "snippet": result.document.content[:200] + "..."
                }
                for result in response.sources
            ]
            
            return ToolResult(
                ok=True,
                data={
                    "query": response.query,
                    "answer": response.response,
                    "sources": sources,
                    "confidence": f"{response.confidence:.1%}",
                    "source_count": len(sources),
                    "cached": response.cached
                },
                message=f"Found {len(sources)} relevant sources"
            )
        
        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return ToolResult(
                ok=False,
                error=f"Search failed: {str(e)}"
            )


class KnowledgeSearchAdvancedTool(BaseTool):
    """
    Advanced semantic search without LLM synthesis (raw results).
    
    This tool returns raw search results without LLM processing,
    useful for retrieving specific documents or when you need
    direct access to source content.
    """
    
    name = "knowledge_search_advanced"
    description = """Advanced semantic search that returns raw results without LLM synthesis.
    Use this when you need direct access to source documents."""
    
    parameters = {
        "query": {
            "type": "string",
            "description": "Natural language search query",
            "required": True
        },
        "collection": {
            "type": "string",
            "description": "Optional collection to search",
            "required": False
        },
        "top_k": {
            "type": "integer",
            "description": "Number of results to return (1-20)",
            "required": False,
            "default": 10,
            "minimum": 1,
            "maximum": 20
        },
        "min_similarity": {
            "type": "number",
            "description": "Minimum similarity threshold (0.0-1.0)",
            "required": False,
            "default": 0.6,
            "minimum": 0.0,
            "maximum": 1.0
        }
    }
    
    async def execute(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = 10,
        min_similarity: float = 0.6,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Execute advanced search without LLM synthesis.
        
        Args:
            query: Search query
            collection: Optional collection filter
            top_k: Number of results
            min_similarity: Minimum similarity threshold
            context: Execution context
            
        Returns:
            ToolResult with raw search results
        """
        try:
            if not context or not hasattr(context, 'knowledge_service'):
                return ToolResult(
                    ok=False,
                    error="Knowledge service not available"
                )
            
            knowledge_service = context.knowledge_service
            
            # Perform search
            results = await knowledge_service.search(
                query=query,
                collection=collection,
                top_k=top_k,
                min_similarity=min_similarity,
                use_cache=True
            )
            
            # Format results
            formatted_results = [
                {
                    "id": result.document.id,
                    "title": result.document.title,
                    "collection": result.document.collection,
                    "content": result.document.content,
                    "metadata": result.document.metadata,
                    "similarity": result.similarity,
                    "rank": result.rank
                }
                for result in results
            ]
            
            return ToolResult(
                ok=True,
                data={
                    "query": query,
                    "results": formatted_results,
                    "count": len(formatted_results)
                },
                message=f"Found {len(formatted_results)} matching documents"
            )
        
        except Exception as e:
            logger.error(f"Advanced search failed: {e}")
            return ToolResult(
                ok=False,
                error=f"Search failed: {str(e)}"
            )
```

```python
# mcp-scrt/src/mcp_scrt/tools/knowledge/add.py

"""
Tool for adding documents to the knowledge base.
"""

from typing import Optional, Dict, Any
from mcp_scrt.tools.base import BaseTool, ToolResult
from mcp_scrt.types import ToolExecutionContext
import logging

logger = logging.getLogger(__name__)


class KnowledgeAddDocumentTool(BaseTool):
    """
    Add a new document to the knowledge base.
    
    This tool adds a document to a specified collection, automatically
    generates embeddings, and makes it searchable.
    """
    
    name = "knowledge_add_document"
    description = """Add a new document to the Secret Network knowledge base.
    The document will be automatically embedded and made searchable."""
    
    parameters = {
        "collection": {
            "type": "string",
            "description": "Collection to add document to",
            "required": True,
            "enum": [
                "fundamentals",
                "privacy_tech",
                "tokens",
                "staking",
                "contracts",
                "security",
                "faq"
            ]
        },
        "title": {
            "type": "string",
            "description": "Document title",
            "required": True
        },
        "content": {
            "type": "string",
            "description": "Document content (markdown supported)",
            "required": True
        },
        "metadata": {
            "type": "object",
            "description": "Optional metadata (tags, author, version, etc.)",
            "required": False
        },
        "doc_id": {
            "type": "string",
            "description": "Optional document ID (auto-generated if not provided)",
            "required": False
        }
    }
    
    async def execute(
        self,
        collection: str,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Add document to knowledge base.
        
        Args:
            collection: Collection name
            title: Document title
            content: Document content
            metadata: Optional metadata
            doc_id: Optional document ID
            context: Execution context
            
        Returns:
            ToolResult with created document info
        """
        try:
            if not context or not hasattr(context, 'knowledge_service'):
                return ToolResult(
                    ok=False,
                    error="Knowledge service not available"
                )
            
            knowledge_service = context.knowledge_service
            
            # Add document
            logger.info(f"Adding document '{title}' to collection '{collection}'")
            
            document = await knowledge_service.add_document(
                collection=collection,
                title=title,
                content=content,
                metadata=metadata,
                doc_id=doc_id
            )
            
            return ToolResult(
                ok=True,
                data={
                    "id": document.id,
                    "collection": document.collection,
                    "title": document.title,
                    "content_length": len(document.content),
                    "metadata": document.metadata
                },
                message=f"Document '{title}' added successfully to '{collection}'"
            )
        
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return ToolResult(
                ok=False,
                error=f"Failed to add document: {str(e)}"
            )
```

```python
# mcp-scrt/src/mcp_scrt/tools/knowledge/update.py

"""
Tool for updating documents in the knowledge base.
"""

from typing import Optional, Dict, Any
from mcp_scrt.tools.base import BaseTool, ToolResult
from mcp_scrt.types import ToolExecutionContext
import logging

logger = logging.getLogger(__name__)


class KnowledgeUpdateDocumentTool(BaseTool):
    """
    Update an existing document in the knowledge base.
    
    This tool updates a document's title, content, or metadata.
    Embeddings are automatically regenerated if content changes.
    """
    
    name = "knowledge_update_document"
    description = """Update an existing document in the knowledge base.
    Provide the document ID and the fields you want to update."""
    
    parameters = {
        "collection": {
            "type": "string",
            "description": "Collection containing the document",
            "required": True
        },
        "doc_id": {
            "type": "string",
            "description": "Document ID to update",
            "required": True
        },
        "title": {
            "type": "string",
            "description": "New title (optional)",
            "required": False
        },
        "content": {
            "type": "string",
            "description": "New content (optional)",
            "required": False
        },
        "metadata": {
            "type": "object",
            "description": "New metadata (optional)",
            "required": False
        }
    }
    
    async def execute(
        self,
        collection: str,
        doc_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Update document in knowledge base.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            title: New title
            content: New content
            metadata: New metadata
            context: Execution context
            
        Returns:
            ToolResult with update confirmation
        """
        try:
            if not context or not hasattr(context, 'knowledge_service'):
                return ToolResult(
                    ok=False,
                    error="Knowledge service not available"
                )
            
            knowledge_service = context.knowledge_service
            
            # Update document
            logger.info(f"Updating document {doc_id} in collection '{collection}'")
            
            await knowledge_service.update_document(
                collection=collection,
                doc_id=doc_id,
                title=title,
                content=content,
                metadata=metadata
            )
            
            # Build update summary
            updated_fields = []
            if title:
                updated_fields.append("title")
            if content:
                updated_fields.append("content")
            if metadata:
                updated_fields.append("metadata")
            
            return ToolResult(
                ok=True,
                data={
                    "doc_id": doc_id,
                    "collection": collection,
                    "updated_fields": updated_fields
                },
                message=f"Document {doc_id} updated successfully"
            )
        
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return ToolResult(
                ok=False,
                error=f"Failed to update document: {str(e)}"
            )
```

```python
# mcp-scrt/src/mcp_scrt/tools/knowledge/delete.py

"""
Tool for deleting documents from the knowledge base.
"""

from mcp_scrt.tools.base import BaseTool, ToolResult
from mcp_scrt.types import ToolExecutionContext
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class KnowledgeDeleteDocumentTool(BaseTool):
    """
    Delete a document from the knowledge base.
    
    This permanently removes a document and its embeddings.
    """
    
    name = "knowledge_delete_document"
    description = """Delete a document from the knowledge base.
    This action is permanent and cannot be undone."""
    
    parameters = {
        "collection": {
            "type": "string",
            "description": "Collection containing the document",
            "required": True
        },
        "doc_id": {
            "type": "string",
            "description": "Document ID to delete",
            "required": True
        }
    }
    
    async def execute(
        self,
        collection: str,
        doc_id: str,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Delete document from knowledge base.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            context: Execution context
            
        Returns:
            ToolResult with deletion confirmation
        """
        try:
            if not context or not hasattr(context, 'knowledge_service'):
                return ToolResult(
                    ok=False,
                    error="Knowledge service not available"
                )
            
            knowledge_service = context.knowledge_service
            
            # Delete document
            logger.info(f"Deleting document {doc_id} from collection '{collection}'")
            
            await knowledge_service.delete_document(
                collection=collection,
                doc_id=doc_id
            )
            
            return ToolResult(
                ok=True,
                data={
                    "doc_id": doc_id,
                    "collection": collection
                },
                message=f"Document {doc_id} deleted successfully"
            )
        
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return ToolResult(
                ok=False,
                error=f"Failed to delete document: {str(e)}"
            )
```

```python
# mcp-scrt/src/mcp_scrt/tools/knowledge/collections.py

"""
Tools for managing knowledge base collections.
"""

from typing import Optional
from mcp_scrt.tools.base import BaseTool, ToolResult
from mcp_scrt.types import ToolExecutionContext
import logging

logger = logging.getLogger(__name__)


class KnowledgeListCollectionsTool(BaseTool):
    """
    List all available knowledge base collections.
    
    Returns all collections with their topics and document counts.
    """
    
    name = "knowledge_list_collections"
    description = """List all available knowledge base collections.
    Shows collection names, topics, and document counts."""
    
    parameters = {}
    
    async def execute(
        self,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        List all collections.
        
        Args:
            context: Execution context
            
        Returns:
            ToolResult with collection list
        """
        try:
            if not context or not hasattr(context, 'knowledge_service'):
                return ToolResult(
                    ok=False,
                    error="Knowledge service not available"
                )
            
            knowledge_service = context.knowledge_service
            
            # Get collections
            collections = knowledge_service.list_collections()
            
            # Get stats for each collection
            collection_info = []
            for collection in collections:
                stats = await knowledge_service.get_collection_stats(collection)
                collection_info.append({
                    "name": collection,
                    "document_count": stats["document_count"],
                    "embedding_dimension": stats["embedding_dimension"]
                })
            
            return ToolResult(
                ok=True,
                data={
                    "collections": collection_info,
                    "count": len(collection_info)
                },
                message=f"Found {len(collection_info)} collections"
            )
        
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return ToolResult(
                ok=False,
                error=f"Failed to list collections: {str(e)}"
            )


class KnowledgeGetCollectionStatsTool(BaseTool):
    """
    Get detailed statistics for a specific collection.
    
    Returns document count, embedding info, and other metrics.
    """
    
    name = "knowledge_get_collection_stats"
    description = """Get detailed statistics for a specific knowledge base collection."""
    
    parameters = {
        "collection": {
            "type": "string",
            "description": "Collection name",
            "required": True,
            "enum": [
                "fundamentals",
                "privacy_tech",
                "tokens",
                "staking",
                "contracts",
                "security",
                "faq"
            ]
        }
    }
    
    async def execute(
        self,
        collection: str,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Get collection statistics.
        
        Args:
            collection: Collection name
            context: Execution context
            
        Returns:
            ToolResult with collection statistics
        """
        try:
            if not context or not hasattr(context, 'knowledge_service'):
                return ToolResult(
                    ok=False,
                    error="Knowledge service not available"
                )
            
            knowledge_service = context.knowledge_service
            
            # Get stats
            stats = await knowledge_service.get_collection_stats(collection)
            
            return ToolResult(
                ok=True,
                data=stats,
                message=f"Collection '{collection}' has {stats['document_count']} documents"
            )
        
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return ToolResult(
                ok=False,
                error=f"Failed to get collection stats: {str(e)}"
            )
```

**Test File**:

```python
# mcp-scrt/tests/unit/test_knowledge_tools.py

import pytest
from unittest.mock import Mock, AsyncMock
from mcp_scrt.tools.knowledge.search import KnowledgeSearchTool, KnowledgeSearchAdvancedTool
from mcp_scrt.tools.knowledge.add import KnowledgeAddDocumentTool
from mcp_scrt.tools.knowledge.collections import KnowledgeListCollectionsTool
from mcp_scrt.services.knowledge_service import (
    SynthesizedResponse,
    KnowledgeSearchResult,
    KnowledgeDocument
)


@pytest.fixture
def mock_context():
    """Mock execution context with knowledge service."""
    context = Mock()
    context.knowledge_service = Mock()
    return context


@pytest.mark.asyncio
async def test_knowledge_search_tool(mock_context):
    """Test knowledge search tool."""
    # Mock synthesized response
    mock_response = SynthesizedResponse(
        query="What is Secret Network?",
        response="Secret Network is a blockchain...",
        sources=[
            KnowledgeSearchResult(
                document=KnowledgeDocument(
                    id="doc1",
                    collection="fundamentals",
                    title="Introduction",
                    content="Secret Network is...",
                    metadata={}
                ),
                similarity=0.95,
                rank=1
            )
        ],
        confidence=0.95,
        cached=False
    )
    
    mock_context.knowledge_service.search_and_synthesize = AsyncMock(
        return_value=mock_response
    )
    
    # Execute tool
    tool = KnowledgeSearchTool()
    result = await tool.execute(
        query="What is Secret Network?",
        context=mock_context
    )
    
    assert result.ok is True
    assert "answer" in result.data
    assert len(result.data["sources"]) == 1


@pytest.mark.asyncio
async def test_knowledge_search_advanced_tool(mock_context):
    """Test advanced search tool."""
    mock_results = [
        KnowledgeSearchResult(
            document=KnowledgeDocument(
                id="doc1",
                collection="fundamentals",
                title="Test",
                content="Content",
                metadata={}
            ),
            similarity=0.9,
            rank=1
        )
    ]
    
    mock_context.knowledge_service.search = AsyncMock(
        return_value=mock_results
    )
    
    tool = KnowledgeSearchAdvancedTool()
    result = await tool.execute(
        query="test query",
        context=mock_context
    )
    
    assert result.ok is True
    assert len(result.data["results"]) == 1


@pytest.mark.asyncio
async def test_knowledge_add_document_tool(mock_context):
    """Test adding document."""
    mock_doc = KnowledgeDocument(
        id="new_doc",
        collection="fundamentals",
        title="Test Doc",
        content="Test content",
        metadata={}
    )
    
    mock_context.knowledge_service.add_document = AsyncMock(
        return_value=mock_doc
    )
    
    tool = KnowledgeAddDocumentTool()
    result = await tool.execute(
        collection="fundamentals",
        title="Test Doc",
        content="Test content",
        context=mock_context
    )
    
    assert result.ok is True
    assert result.data["id"] == "new_doc"


@pytest.mark.asyncio
async def test_knowledge_list_collections_tool(mock_context):
    """Test listing collections."""
    mock_context.knowledge_service.list_collections = Mock(
        return_value=["fundamentals", "staking"]
    )
    mock_context.knowledge_service.get_collection_stats = AsyncMock(
        return_value={
            "collection": "fundamentals",
            "document_count": 10,
            "embedding_dimension": 384
        }
    )
    
    tool = KnowledgeListCollectionsTool()
    result = await tool.execute(context=mock_context)
    
    assert result.ok is True
    assert len(result.data["collections"]) == 2
```

**Success Criteria**:
- ✅ 7 knowledge tools implemented
- ✅ Semantic search with LLM synthesis works
- ✅ Document CRUD operations functional
- ✅ Collection management tools work
- ✅ All tests pass

---

## Task 1D.2: Graph Analysis Tools

**Objective**: Create MCP tools for graph database queries and network analysis.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/tools/graph/__init__.py
mcp-scrt/src/mcp_scrt/tools/graph/validators.py
mcp-scrt/src/mcp_scrt/tools/graph/wallet.py
mcp-scrt/src/mcp_scrt/tools/graph/query.py
mcp-scrt/tests/unit/test_graph_tools.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/tools/graph/__init__.py

"""
Graph database tools for network analysis and relationship tracking.

Available tools:
- graph_analyze_validator_network: Analyze validator delegation patterns
- graph_recommend_validators: Get validator recommendations
- graph_get_wallet_activity: Get wallet activity summary
- graph_find_path: Find paths between entities
- graph_query_custom: Execute custom Cypher query
"""

from .validators import (
    GraphAnalyzeValidatorNetworkTool,
    GraphRecommendValidatorsTool
)
from .wallet import GraphGetWalletActivityTool
from .query import GraphFindPathTool, GraphQueryCustomTool

# Tool registry
GRAPH_TOOLS = {
    "graph_analyze_validator_network": GraphAnalyzeValidatorNetworkTool,
    "graph_recommend_validators": GraphRecommendValidatorsTool,
    "graph_get_wallet_activity": GraphGetWalletActivityTool,
    "graph_find_path": GraphFindPathTool,
    "graph_query_custom": GraphQueryCustomTool,
}

__all__ = [
    "GraphAnalyzeValidatorNetworkTool",
    "GraphRecommendValidatorsTool",
    "GraphGetWalletActivityTool",
    "GraphFindPathTool",
    "GraphQueryCustomTool",
    "GRAPH_TOOLS",
]
```

```python
# mcp-scrt/src/mcp_scrt/tools/graph/validators.py

"""
Graph tools for validator network analysis.
"""

from typing import Optional
from mcp_scrt.tools.base import BaseTool, ToolResult
from mcp_scrt.types import ToolExecutionContext
import logging

logger = logging.getLogger(__name__)


class GraphAnalyzeValidatorNetworkTool(BaseTool):
    """
    Analyze validator delegation network patterns.
    
    This tool provides insights into:
    - Delegation distribution
    - Network centrality
    - Validator relationships
    - Community clusters
    """
    
    name = "graph_analyze_validator_network"
    description = """Analyze the validator delegation network to understand
    delegation patterns, identify central validators, and detect communities."""
    
    parameters = {
        "validator_address": {
            "type": "string",
            "description": "Optional validator address to focus analysis on",
            "required": False
        },
        "depth": {
            "type": "integer",
            "description": "Analysis depth (1-3)",
            "required": False,
            "default": 2,
            "minimum": 1,
            "maximum": 3
        }
    }
    
    async def execute(
        self,
        validator_address: Optional[str] = None,
        depth: int = 2,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Analyze validator network.
        
        Args:
            validator_address: Optional validator to focus on
            depth: Analysis depth
            context: Execution context
            
        Returns:
            ToolResult with network analysis
        """
        try:
            if not context or not hasattr(context, 'graph_service'):
                return ToolResult(
                    ok=False,
                    error="Graph service not available"
                )
            
            graph_service = context.graph_service
            
            # Perform analysis
            logger.info(f"Analyzing validator network (depth={depth})")
            
            analysis = await graph_service.analyze_validator_network(
                validator_address=validator_address,
                depth=depth,
                use_cache=True
            )
            
            # Format central nodes
            central_validators = [
                {
                    "address": address,
                    "delegator_count": count,
                    "centrality_rank": rank + 1
                }
                for rank, (address, count) in enumerate(analysis.central_nodes)
            ]
            
            return ToolResult(
                ok=True,
                data={
                    "node_count": analysis.node_count,
                    "relationship_count": analysis.relationship_count,
                    "network_density": f"{analysis.density:.2%}",
                    "central_validators": central_validators[:10],
                    "insights": analysis.insights,
                    "focus_validator": validator_address
                },
                message=f"Analyzed network with {analysis.node_count} validators"
            )
        
        except Exception as e:
            logger.error(f"Network analysis failed: {e}")
            return ToolResult(
                ok=False,
                error=f"Analysis failed: {str(e)}"
            )


class GraphRecommendValidatorsTool(BaseTool):
    """
    Get personalized validator recommendations.
    
    This tool analyzes validators based on:
    - Decentralization (voting power)
    - Commission rates
    - Uptime and reliability
    - Community support (delegator count)
    
    Returns top validators with scores and reasons.
    """
    
    name = "graph_recommend_validators"
    description = """Get smart validator recommendations based on decentralization,
    commission, uptime, and community metrics. Returns scored and ranked validators."""
    
    parameters = {
        "wallet_address": {
            "type": "string",
            "description": "Wallet address for personalized recommendations",
            "required": True
        },
        "count": {
            "type": "integer",
            "description": "Number of validators to recommend (1-10)",
            "required": False,
            "default": 5,
            "minimum": 1,
            "maximum": 10
        }
    }
    
    async def execute(
        self,
        wallet_address: str,
        count: int = 5,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Get validator recommendations.
        
        Args:
            wallet_address: Wallet address
            count: Number of recommendations
            context: Execution context
            
        Returns:
            ToolResult with recommendations
        """
        try:
            if not context or not hasattr(context, 'graph_service'):
                return ToolResult(
                    ok=False,
                    error="Graph service not available"
                )
            
            graph_service = context.graph_service
            
            # Get recommendations
            logger.info(f"Getting validator recommendations for {wallet_address}")
            
            recommendations = await graph_service.recommend_validators(
                wallet_address=wallet_address,
                count=count
            )
            
            # Format recommendations
            formatted = [
                {
                    "rank": idx + 1,
                    "address": rec.address,
                    "moniker": rec.moniker,
                    "score": f"{rec.score:.1f}/10",
                    "reasons": rec.reasons,
                    "metrics": {
                        "voting_power": f"{rec.metrics.get('voting_power', 0):.2f}%",
                        "commission": f"{rec.metrics.get('commission', 0):.2f}%",
                        "uptime": f"{rec.metrics.get('uptime', 0):.2f}%",
                        "delegators": rec.metrics.get('delegator_count', 0)
                    }
                }
                for idx, rec in enumerate(recommendations)
            ]
            
            return ToolResult(
                ok=True,
                data={
                    "recommendations": formatted,
                    "count": len(formatted),
                    "wallet": wallet_address
                },
                message=f"Found {len(formatted)} recommended validators"
            )
        
        except Exception as e:
            logger.error(f"Validator recommendations failed: {e}")
            return ToolResult(
                ok=False,
                error=f"Recommendations failed: {str(e)}"
            )
```

```python
# mcp-scrt/src/mcp_scrt/tools/graph/wallet.py

"""
Graph tools for wallet activity analysis.
"""

from typing import Optional
from mcp_scrt.tools.base import BaseTool, ToolResult
from mcp_scrt.types import ToolExecutionContext
import logging

logger = logging.getLogger(__name__)


class GraphGetWalletActivityTool(BaseTool):
    """
    Get comprehensive wallet activity from the graph.
    
    This tool provides:
    - Delegation history
    - Transfer patterns
    - Governance participation
    - Contract interactions
    - Related entities
    """
    
    name = "graph_get_wallet_activity"
    description = """Get comprehensive activity summary for a wallet from the graph database.
    Shows delegations, transfers, votes, contract interactions, and related entities."""
    
    parameters = {
        "wallet_address": {
            "type": "string",
            "description": "Wallet address to analyze",
            "required": True
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of activities to return",
            "required": False,
            "default": 50,
            "minimum": 1,
            "maximum": 200
        }
    }
    
    async def execute(
        self,
        wallet_address: str,
        limit: int = 50,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Get wallet activity.
        
        Args:
            wallet_address: Wallet address
            limit: Activity limit
            context: Execution context
            
        Returns:
            ToolResult with activity summary
        """
        try:
            if not context or not hasattr(context, 'graph_service'):
                return ToolResult(
                    ok=False,
                    error="Graph service not available"
                )
            
            graph_service = context.graph_service
            
            # Get activity
            logger.info(f"Getting activity for wallet {wallet_address}")
            
            activity = await graph_service.get_wallet_activity(
                wallet_address=wallet_address,
                limit=limit
            )
            
            # Calculate activity score
            total_activities = (
                activity["delegations"] +
                activity["transfers"] +
                activity["votes"] +
                activity["contract_executions"]
            )
            
            # Generate insights
            insights = []
            if activity["delegations"] > 0:
                insights.append(
                    f"Delegated to {len(activity['related_validators'])} validators"
                )
            if activity["votes"] > 0:
                insights.append(
                    f"Participated in {activity['votes']} governance proposals"
                )
            if activity["contract_executions"] > 0:
                insights.append(
                    f"Interacted with {len(activity['related_contracts'])} contracts"
                )
            
            return ToolResult(
                ok=True,
                data={
                    "wallet": wallet_address,
                    "total_activities": total_activities,
                    "delegations": activity["delegations"],
                    "transfers": activity["transfers"],
                    "votes": activity["votes"],
                    "contract_executions": activity["contract_executions"],
                    "related_validators": activity["related_validators"][:10],
                    "related_wallets": activity["related_wallets"][:10],
                    "related_contracts": activity["related_contracts"][:10],
                    "related_proposals": activity["related_proposals"][:10],
                    "insights": insights
                },
                message=f"Found {total_activities} activities for wallet"
            )
        
        except Exception as e:
            logger.error(f"Wallet activity query failed: {e}")
            return ToolResult(
                ok=False,
                error=f"Activity query failed: {str(e)}"
            )
```

```python
# mcp-scrt/src/mcp_scrt/tools/graph/query.py

"""
Graph tools for path finding and custom queries.
"""

from typing import Optional
from mcp_scrt.tools.base import BaseTool, ToolResult
from mcp_scrt.types import ToolExecutionContext
import logging

logger = logging.getLogger(__name__)


class GraphFindPathTool(BaseTool):
    """
    Find paths between two entities in the graph.
    
    Useful for:
    - Tracing delegation chains
    - Finding transaction paths
    - Analyzing relationships
    """
    
    name = "graph_find_path"
    description = """Find shortest paths between two entities (wallets, validators, etc.)
    in the graph. Useful for tracing relationships and connections."""
    
    parameters = {
        "from_address": {
            "type": "string",
            "description": "Starting entity address",
            "required": True
        },
        "to_address": {
            "type": "string",
            "description": "Target entity address",
            "required": True
        },
        "max_depth": {
            "type": "integer",
            "description": "Maximum path length (1-5)",
            "required": False,
            "default": 3,
            "minimum": 1,
            "maximum": 5
        }
    }
    
    async def execute(
        self,
        from_address: str,
        to_address: str,
        max_depth: int = 3,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Find path between entities.
        
        Args:
            from_address: Start address
            to_address: End address
            max_depth: Maximum path depth
            context: Execution context
            
        Returns:
            ToolResult with path information
        """
        try:
            if not context or not hasattr(context, 'graph_service'):
                return ToolResult(
                    ok=False,
                    error="Graph service not available"
                )
            
            graph_service = context.graph_service
            
            # Find path using Neo4j client
            logger.info(f"Finding path: {from_address} -> {to_address}")
            
            paths = graph_service.neo4j.find_path(
                from_label="Wallet",
                from_prop="address",
                from_value=from_address,
                to_label="Wallet",
                to_prop="address",
                to_value=to_address,
                max_depth=max_depth
            )
            
            if not paths:
                return ToolResult(
                    ok=True,
                    data={
                        "from": from_address,
                        "to": to_address,
                        "paths_found": 0
                    },
                    message="No path found between entities"
                )
            
            # Format paths
            formatted_paths = [
                {
                    "length": len(path.get("path", [])),
                    "path": str(path.get("path", []))
                }
                for path in paths[:5]  # Return top 5 paths
            ]
            
            return ToolResult(
                ok=True,
                data={
                    "from": from_address,
                    "to": to_address,
                    "paths_found": len(formatted_paths),
                    "paths": formatted_paths
                },
                message=f"Found {len(formatted_paths)} paths"
            )
        
        except Exception as e:
            logger.error(f"Path finding failed: {e}")
            return ToolResult(
                ok=False,
                error=f"Path finding failed: {str(e)}"
            )


class GraphQueryCustomTool(BaseTool):
    """
    Execute a custom Cypher query on the graph database.
    
    WARNING: This is an advanced tool. Incorrect queries can be slow
    or return large result sets. Use with caution.
    """
    
    name = "graph_query_custom"
    description = """Execute a custom Cypher query on the graph database.
    Advanced tool for custom analysis. Use with caution."""
    
    parameters = {
        "query": {
            "type": "string",
            "description": "Cypher query to execute",
            "required": True
        },
        "parameters": {
            "type": "object",
            "description": "Query parameters",
            "required": False
        },
        "limit": {
            "type": "integer",
            "description": "Result limit (safety feature)",
            "required": False,
            "default": 100,
            "minimum": 1,
            "maximum": 1000
        }
    }
    
    async def execute(
        self,
        query: str,
        parameters: Optional[dict] = None,
        limit: int = 100,
        context: Optional[ToolExecutionContext] = None
    ) -> ToolResult:
        """
        Execute custom Cypher query.
        
        Args:
            query: Cypher query
            parameters: Query parameters
            limit: Result limit
            context: Execution context
            
        Returns:
            ToolResult with query results
        """
        try:
            if not context or not hasattr(context, 'graph_service'):
                return ToolResult(
                    ok=False,
                    error="Graph service not available"
                )
            
            graph_service = context.graph_service
            
            # Add LIMIT to query if not present (safety)
            if "LIMIT" not in query.upper():
                query = f"{query} LIMIT {limit}"
            
            # Execute query
            logger.info(f"Executing custom Cypher query")
            
            results = graph_service.neo4j.execute_query(
                query=query,
                parameters=parameters or {}
            )
            
            return ToolResult(
                ok=True,
                data={
                    "results": results[:limit],  # Enforce limit
                    "count": len(results),
                    "limited": len(results) >= limit
                },
                message=f"Query returned {len(results)} results"
            )
        
        except Exception as e:
            logger.error(f"Custom query failed: {e}")
            return ToolResult(
                ok=False,
                error=f"Query failed: {str(e)}"
            )
```

**Test File** (abbreviated):

```python
# mcp-scrt/tests/unit/test_graph_tools.py

import pytest
from unittest.mock import Mock, AsyncMock
from mcp_scrt.tools.graph.validators import (
    GraphAnalyzeValidatorNetworkTool,
    GraphRecommendValidatorsTool
)
from mcp_scrt.tools.graph.wallet import GraphGetWalletActivityTool
from mcp_scrt.services.graph_service import NetworkAnalysis, ValidatorScore


@pytest.fixture
def mock_context():
    """Mock execution context with graph service."""
    context = Mock()
    context.graph_service = Mock()
    return context


@pytest.mark.asyncio
async def test_analyze_validator_network_tool(mock_context):
    """Test validator network analysis tool."""
    mock_analysis = NetworkAnalysis(
        node_count=50,
        relationship_count=200,
        density=0.08,
        clusters=[],
        central_nodes=[("val1", 100), ("val2", 80)],
        insights=["Top validator has 100 delegators"]
    )
    
    mock_context.graph_service.analyze_validator_network = AsyncMock(
        return_value=mock_analysis
    )
    
    tool = GraphAnalyzeValidatorNetworkTool()
    result = await tool.execute(context=mock_context)
    
    assert result.ok is True
    assert result.data["node_count"] == 50
    assert len(result.data["central_validators"]) > 0


@pytest.mark.asyncio
async def test_recommend_validators_tool(mock_context):
    """Test validator recommendations tool."""
    mock_recommendations = [
        ValidatorScore(
            address="val1",
            moniker="Validator 1",
            score=9.2,
            reasons=["Good uptime", "Low voting power"],
            metrics={"voting_power": 3.0, "commission": 5.0, "uptime": 99.9}
        )
    ]
    
    mock_context.graph_service.recommend_validators = AsyncMock(
        return_value=mock_recommendations
    )
    
    tool = GraphRecommendValidatorsTool()
    result = await tool.execute(
        wallet_address="secret1abc",
        context=mock_context
    )
    
    assert result.ok is True
    assert len(result.data["recommendations"]) == 1
    assert result.data["recommendations"][0]["score"] == "9.2/10"
```

**Success Criteria**:
- ✅ 5 graph analysis tools implemented
- ✅ Validator network analysis works
- ✅ Validator recommendations functional
- ✅ Wallet activity tracking works
- ✅ All tests pass

---

## Summary of Part 1D Progress

At this point, you have completed:

✅ **Knowledge Base Tools** (7 tools):
- `knowledge_search` - Semantic search with LLM synthesis
- `knowledge_search_advanced` - Raw search results
- `knowledge_add_document` - Add documents
- `knowledge_update_document` - Update documents
- `knowledge_delete_document` - Delete documents
- `knowledge_list_collections` - List collections
- `knowledge_get_collection_stats` - Collection statistics

✅ **Graph Analysis Tools** (5 tools):
- `graph_analyze_validator_network` - Network analysis
- `graph_recommend_validators` - Smart recommendations
- `graph_get_wallet_activity` - Activity summary
- `graph_find_path` - Path finding
- `graph_query_custom` - Custom Cypher queries
