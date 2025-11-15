# Phase 1B: Service Layer Implementation

## Overview

The service layer sits between MCP tools and database clients, providing high-level business logic, intelligent caching, LLM integration, and orchestration. This layer enables complex operations like semantic search with LLM synthesis, graph analysis, and smart cache invalidation.

---

## Task 1B.1: Embedding Service

**Objective**: Create a service for generating and managing text embeddings using sentence-transformers with caching.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/services/__init__.py
mcp-scrt/src/mcp_scrt/services/embedding_service.py
mcp-scrt/tests/unit/test_embedding_service.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/services/embedding_service.py

"""
Embedding service for text vectorization.

This service provides:
- Text embedding generation using sentence-transformers
- Batch embedding processing
- Embedding caching in Redis
- Multiple embedding model support
"""

import hashlib
from typing import List, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating and caching text embeddings.
    
    Features:
    - Multiple embedding models
    - Batch processing
    - Redis caching
    - Dimension reduction (optional)
    """
    
    # Supported models with their dimensions
    MODELS = {
        "all-MiniLM-L6-v2": 384,       # Fast, good quality
        "all-mpnet-base-v2": 768,      # Better quality, slower
        "paraphrase-MiniLM-L6-v2": 384 # Paraphrase detection
    }
    
    def __init__(
        self,
        redis_client,
        model_name: str = "all-MiniLM-L6-v2",
        cache_ttl: int = 86400  # 24 hours
    ):
        """
        Initialize embedding service.
        
        Args:
            redis_client: Redis client for caching
            model_name: Name of sentence-transformer model
            cache_ttl: Cache TTL in seconds (default: 24 hours)
        """
        self.redis = redis_client
        self.model_name = model_name
        self.cache_ttl = cache_ttl
        
        # Load model lazily
        self._model = None
        self._dimension = self.MODELS.get(model_name, 384)
        
        logger.info(f"Initialized EmbeddingService with model: {model_name}")
    
    @property
    def model(self) -> SentenceTransformer:
        """
        Lazy load the embedding model.
        
        Returns:
            SentenceTransformer model instance
        """
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully")
        
        return self._model
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension for this model."""
        return self._dimension
    
    def _generate_cache_key(self, text: str) -> str:
        """
        Generate cache key for text.
        
        Args:
            text: Input text
            
        Returns:
            Cache key string
        """
        # Hash text for consistent key
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"embedding:{self.model_name}:{text_hash}"
    
    def embed(
        self,
        text: str,
        use_cache: bool = True,
        normalize: bool = True
    ) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            use_cache: Use cached embedding if available
            normalize: Normalize embedding to unit length
            
        Returns:
            Embedding vector as list of floats
        """
        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(text)
            cached = self.redis.get(cache_key)
            
            if cached is not None:
                logger.debug(f"Cache hit for embedding: {text[:50]}...")
                return cached
        
        # Generate embedding
        logger.debug(f"Generating embedding for: {text[:50]}...")
        embedding = self.model.encode(
            text,
            normalize_embeddings=normalize,
            convert_to_numpy=True
        )
        
        # Convert to list
        embedding_list = embedding.tolist()
        
        # Cache result
        if use_cache:
            self.redis.set(cache_key, embedding_list, ex=self.cache_ttl)
        
        return embedding_list
    
    def embed_batch(
        self,
        texts: List[str],
        use_cache: bool = True,
        normalize: bool = True,
        batch_size: int = 32,
        show_progress: bool = False
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            use_cache: Use cached embeddings if available
            normalize: Normalize embeddings to unit length
            batch_size: Batch size for encoding
            show_progress: Show progress bar
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        texts_to_embed = []
        text_indices = []
        
        # Check cache for each text
        if use_cache:
            for idx, text in enumerate(texts):
                cache_key = self._generate_cache_key(text)
                cached = self.redis.get(cache_key)
                
                if cached is not None:
                    embeddings.append(cached)
                    logger.debug(f"Cache hit for text {idx}")
                else:
                    embeddings.append(None)
                    texts_to_embed.append(text)
                    text_indices.append(idx)
        else:
            texts_to_embed = texts
            text_indices = list(range(len(texts)))
            embeddings = [None] * len(texts)
        
        # Generate embeddings for uncached texts
        if texts_to_embed:
            logger.info(f"Generating {len(texts_to_embed)} embeddings")
            
            new_embeddings = self.model.encode(
                texts_to_embed,
                normalize_embeddings=normalize,
                convert_to_numpy=True,
                batch_size=batch_size,
                show_progress_bar=show_progress
            )
            
            # Convert to list and cache
            for idx, text, embedding in zip(text_indices, texts_to_embed, new_embeddings):
                embedding_list = embedding.tolist()
                embeddings[idx] = embedding_list
                
                if use_cache:
                    cache_key = self._generate_cache_key(text)
                    self.redis.set(cache_key, embedding_list, ex=self.cache_ttl)
        
        return embeddings
    
    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        similarity = dot_product / (norm1 * norm2)
        
        return float(similarity)
    
    def find_most_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[tuple]:
        """
        Find most similar embeddings to query.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embeddings
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples, sorted by score
        """
        similarities = []
        
        for idx, candidate in enumerate(candidate_embeddings):
            similarity = self.cosine_similarity(query_embedding, candidate)
            similarities.append((idx, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def clear_cache(self, pattern: str = None):
        """
        Clear embedding cache.
        
        Args:
            pattern: Optional pattern to match (e.g., "embedding:all-MiniLM-*")
                    If None, clears all embeddings for this model
        """
        if pattern is None:
            pattern = f"embedding:{self.model_name}:*"
        
        deleted = self.redis.delete_pattern(pattern)
        logger.info(f"Cleared {deleted} cached embeddings matching: {pattern}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for embeddings.
        
        Returns:
            Dict with cache stats
        """
        pattern = f"embedding:{self.model_name}:*"
        keys = self.redis.keys(pattern)
        
        return {
            "model": self.model_name,
            "dimension": self._dimension,
            "cached_count": len(keys),
            "cache_ttl": self.cache_ttl
        }


# Export
__all__ = ["EmbeddingService"]
```

**Test File**:

```python
# mcp-scrt/tests/unit/test_embedding_service.py

import pytest
from unittest.mock import Mock, MagicMock
from mcp_scrt.services.embedding_service import EmbeddingService


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis = Mock()
    redis.get.return_value = None
    redis.set.return_value = True
    redis.keys.return_value = []
    redis.delete_pattern.return_value = 0
    return redis


@pytest.fixture
def embedding_service(mock_redis):
    """Create embedding service with mock Redis."""
    return EmbeddingService(redis_client=mock_redis)


def test_initialization(embedding_service):
    """Test service initialization."""
    assert embedding_service.model_name == "all-MiniLM-L6-v2"
    assert embedding_service.dimension == 384
    assert embedding_service._model is None  # Lazy loading


def test_lazy_model_loading(embedding_service):
    """Test that model is loaded on first use."""
    # Model not loaded initially
    assert embedding_service._model is None
    
    # Access model property triggers loading
    model = embedding_service.model
    assert model is not None
    assert embedding_service._model is not None


def test_cache_key_generation(embedding_service):
    """Test cache key generation."""
    text = "Secret Network is a blockchain"
    key1 = embedding_service._generate_cache_key(text)
    key2 = embedding_service._generate_cache_key(text)
    
    # Same text should generate same key
    assert key1 == key2
    assert key1.startswith("embedding:all-MiniLM-L6-v2:")
    
    # Different text should generate different key
    key3 = embedding_service._generate_cache_key("Different text")
    assert key3 != key1


def test_embed_single_text(embedding_service, mock_redis):
    """Test embedding a single text."""
    text = "Secret Network is a blockchain"
    
    # First call - not cached
    embedding = embedding_service.embed(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
    assert all(isinstance(x, float) for x in embedding)
    
    # Verify cache was set
    mock_redis.set.assert_called_once()


def test_embed_with_cache_hit(embedding_service, mock_redis):
    """Test embedding with cache hit."""
    text = "Secret Network"
    cached_embedding = [0.1] * 384
    
    # Mock cache hit
    mock_redis.get.return_value = cached_embedding
    
    embedding = embedding_service.embed(text)
    
    # Should return cached embedding
    assert embedding == cached_embedding
    
    # Model should not be loaded (lazy loading)
    assert embedding_service._model is None


def test_embed_batch(embedding_service):
    """Test batch embedding."""
    texts = [
        "Secret Network is a blockchain",
        "Privacy is important",
        "Smart contracts on Secret"
    ]
    
    embeddings = embedding_service.embed_batch(texts)
    
    assert len(embeddings) == 3
    assert all(len(emb) == 384 for emb in embeddings)


def test_cosine_similarity(embedding_service):
    """Test cosine similarity calculation."""
    # Identical vectors should have similarity of 1.0
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    similarity = embedding_service.cosine_similarity(vec1, vec2)
    assert abs(similarity - 1.0) < 0.001
    
    # Orthogonal vectors should have similarity close to 0
    vec3 = [1.0, 0.0, 0.0]
    vec4 = [0.0, 1.0, 0.0]
    similarity = embedding_service.cosine_similarity(vec3, vec4)
    assert abs(similarity - 0.0) < 0.001


def test_find_most_similar(embedding_service):
    """Test finding most similar embeddings."""
    query = [1.0, 0.0, 0.0]
    
    candidates = [
        [0.9, 0.1, 0.0],   # Very similar
        [0.0, 1.0, 0.0],   # Orthogonal
        [0.8, 0.2, 0.0],   # Similar
        [-1.0, 0.0, 0.0],  # Opposite
    ]
    
    results = embedding_service.find_most_similar(query, candidates, top_k=2)
    
    assert len(results) == 2
    # First result should be index 0 (most similar)
    assert results[0][0] == 0
    # Second result should be index 2
    assert results[1][0] == 2


def test_clear_cache(embedding_service, mock_redis):
    """Test cache clearing."""
    embedding_service.clear_cache()
    
    # Verify delete_pattern was called
    mock_redis.delete_pattern.assert_called_once()
    call_args = mock_redis.delete_pattern.call_args[0][0]
    assert "embedding:all-MiniLM-L6-v2" in call_args


def test_get_cache_stats(embedding_service, mock_redis):
    """Test getting cache statistics."""
    mock_redis.keys.return_value = ["key1", "key2", "key3"]
    
    stats = embedding_service.get_cache_stats()
    
    assert stats["model"] == "all-MiniLM-L6-v2"
    assert stats["dimension"] == 384
    assert stats["cached_count"] == 3
```

**Success Criteria**:
- ✅ Service initializes with lazy model loading
- ✅ Embeddings are generated correctly
- ✅ Caching works (cache hits and misses)
- ✅ Batch processing works
- ✅ Cosine similarity calculations are accurate
- ✅ All tests pass

---

## Task 1B.2: Knowledge Service

**Objective**: Create a high-level service for knowledge base operations including semantic search, document management, and LLM synthesis.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/services/knowledge_service.py
mcp-scrt/tests/unit/test_knowledge_service.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/services/knowledge_service.py

"""
Knowledge service for semantic search and document management.

This service provides:
- Semantic search across knowledge base
- Document CRUD operations
- LLM-powered response synthesis
- Query result caching
- Multi-collection queries
"""

import hashlib
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeDocument:
    """Knowledge document with metadata."""
    id: str
    collection: str
    title: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class KnowledgeSearchResult:
    """Search result with relevance information."""
    document: KnowledgeDocument
    similarity: float
    rank: int


@dataclass
class SynthesizedResponse:
    """LLM-synthesized response with sources."""
    query: str
    response: str
    sources: List[KnowledgeSearchResult]
    confidence: float
    cached: bool = False


class KnowledgeService:
    """
    High-level service for knowledge base operations.
    
    Features:
    - Semantic search with ChromaDB
    - Document lifecycle management
    - LLM synthesis with Ollama
    - Intelligent caching
    - Multi-modal retrieval (vector + keyword)
    """
    
    # Knowledge collections (topics)
    COLLECTIONS = [
        "fundamentals",
        "privacy_tech",
        "tokens",
        "staking",
        "contracts",
        "security",
        "faq"
    ]
    
    def __init__(
        self,
        chromadb_client,
        redis_client,
        ollama_client,
        embedding_service,
        cache_ttl: int = 3600  # 1 hour
    ):
        """
        Initialize knowledge service.
        
        Args:
            chromadb_client: ChromaDB client
            redis_client: Redis client for caching
            ollama_client: Ollama client for LLM
            embedding_service: Embedding service
            cache_ttl: Cache TTL in seconds
        """
        self.chroma = chromadb_client
        self.redis = redis_client
        self.ollama = ollama_client
        self.embeddings = embedding_service
        self.cache_ttl = cache_ttl
        
        logger.info("Initialized KnowledgeService")
    
    def _generate_query_hash(self, query: str, **params) -> str:
        """
        Generate hash for query caching.
        
        Args:
            query: Search query
            params: Additional parameters
            
        Returns:
            Cache key string
        """
        # Create stable string from query and params
        cache_string = f"{query}:{sorted(params.items())}"
        query_hash = hashlib.sha256(cache_string.encode()).hexdigest()[:16]
        return f"knowledge:query:{query_hash}"
    
    async def search(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.6,
        use_cache: bool = True
    ) -> List[KnowledgeSearchResult]:
        """
        Semantic search across knowledge base.
        
        Args:
            query: Natural language query
            collection: Optional collection filter
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            use_cache: Use cached results if available
            
        Returns:
            List of search results with relevance scores
        """
        # Check cache
        if use_cache:
            cache_key = self._generate_query_hash(
                query,
                collection=collection,
                top_k=top_k
            )
            cached = self.redis.get(cache_key)
            
            if cached:
                logger.info(f"Cache hit for query: {query[:50]}...")
                return [
                    KnowledgeSearchResult(**result)
                    for result in cached
                ]
        
        # Generate query embedding
        query_embedding = self.embeddings.embed(query)
        
        # Determine which collections to search
        collections = [collection] if collection else self.COLLECTIONS
        
        all_results = []
        
        # Search each collection
        for coll_name in collections:
            try:
                results = self.chroma.query(
                    collection_name=coll_name,
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=None
                )
                
                # Process results
                if results and results['ids']:
                    for idx in range(len(results['ids'][0])):
                        doc_id = results['ids'][0][idx]
                        document = results['documents'][0][idx]
                        metadata = results['metadatas'][0][idx]
                        distance = results['distances'][0][idx]
                        
                        # Convert distance to similarity (cosine distance -> similarity)
                        similarity = 1 - distance
                        
                        if similarity >= min_similarity:
                            doc = KnowledgeDocument(
                                id=doc_id,
                                collection=coll_name,
                                title=metadata.get('title', 'Untitled'),
                                content=document,
                                metadata=metadata
                            )
                            
                            all_results.append((doc, similarity))
            
            except Exception as e:
                logger.warning(f"Failed to search collection {coll_name}: {e}")
                continue
        
        # Sort by similarity and rank
        all_results.sort(key=lambda x: x[1], reverse=True)
        all_results = all_results[:top_k]
        
        # Create search results with ranking
        search_results = [
            KnowledgeSearchResult(
                document=doc,
                similarity=sim,
                rank=rank + 1
            )
            for rank, (doc, sim) in enumerate(all_results)
        ]
        
        # Cache results
        if use_cache and search_results:
            cache_data = [
                {
                    'document': result.document.to_dict(),
                    'similarity': result.similarity,
                    'rank': result.rank
                }
                for result in search_results
            ]
            self.redis.set(cache_key, cache_data, ex=self.cache_ttl)
        
        logger.info(f"Found {len(search_results)} results for query: {query[:50]}...")
        return search_results
    
    async def search_and_synthesize(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = 5,
        use_cache: bool = True
    ) -> SynthesizedResponse:
        """
        Search knowledge base and synthesize natural response with LLM.
        
        Args:
            query: Natural language query
            collection: Optional collection filter
            top_k: Number of source documents to use
            use_cache: Use cached response if available
            
        Returns:
            Synthesized response with sources
        """
        # Check cache for synthesized response
        if use_cache:
            cache_key = self._generate_query_hash(
                f"synthesized:{query}",
                collection=collection,
                top_k=top_k
            )
            cached = self.redis.get(cache_key)
            
            if cached:
                logger.info(f"Cache hit for synthesized query: {query[:50]}...")
                cached['cached'] = True
                return SynthesizedResponse(**cached)
        
        # Search for relevant documents
        search_results = await self.search(
            query=query,
            collection=collection,
            top_k=top_k,
            use_cache=use_cache
        )
        
        if not search_results:
            return SynthesizedResponse(
                query=query,
                response="I couldn't find relevant information to answer your question.",
                sources=[],
                confidence=0.0
            )
        
        # Build context from search results
        context_parts = []
        for result in search_results:
            context_parts.append(
                f"[Source {result.rank}: {result.document.title}]\n"
                f"{result.document.content}\n"
                f"(Relevance: {result.similarity:.2%})"
            )
        
        context = "\n\n".join(context_parts)
        
        # Create prompt for LLM
        system_prompt = """You are a knowledgeable assistant specializing in Secret Network.
Using the provided context, answer the user's question naturally and accurately.
Include citations to sources using [Source N] format.
If the context doesn't fully answer the question, say so honestly."""
        
        user_prompt = f"""Context:
{context}

Question: {query}

Please provide a comprehensive answer using the context above. Include citations to specific sources."""
        
        # Generate response with Ollama
        try:
            llm_response = self.ollama.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={
                    "temperature": 0.3,  # Low temperature for factual responses
                    "top_p": 0.9
                }
            )
            
            synthesized_text = llm_response['message']['content']
            
            # Calculate confidence based on average similarity
            avg_similarity = sum(r.similarity for r in search_results) / len(search_results)
            confidence = avg_similarity
            
        except Exception as e:
            logger.error(f"LLM synthesis failed: {e}")
            synthesized_text = "I apologize, but I encountered an error generating a response."
            confidence = 0.0
        
        # Create response object
        response = SynthesizedResponse(
            query=query,
            response=synthesized_text,
            sources=search_results,
            confidence=confidence
        )
        
        # Cache synthesized response
        if use_cache:
            cache_data = {
                'query': response.query,
                'response': response.response,
                'sources': [
                    {
                        'document': r.document.to_dict(),
                        'similarity': r.similarity,
                        'rank': r.rank
                    }
                    for r in response.sources
                ],
                'confidence': response.confidence
            }
            self.redis.set(cache_key, cache_data, ex=self.cache_ttl)
        
        return response
    
    async def add_document(
        self,
        collection: str,
        title: str,
        content: str,
        metadata: Optional[Dict] = None,
        doc_id: Optional[str] = None
    ) -> KnowledgeDocument:
        """
        Add a document to the knowledge base.
        
        Args:
            collection: Collection name
            title: Document title
            content: Document content
            metadata: Additional metadata
            doc_id: Optional document ID (auto-generated if not provided)
            
        Returns:
            Created knowledge document
        """
        # Generate ID if not provided
        if doc_id is None:
            doc_id = f"{collection}_{hashlib.md5(title.encode()).hexdigest()[:12]}"
        
        # Prepare metadata
        full_metadata = {
            'title': title,
            'collection': collection,
            'added_at': datetime.utcnow().isoformat(),
            **(metadata or {})
        }
        
        # Generate embedding
        embedding = self.embeddings.embed(content)
        
        # Add to ChromaDB
        self.chroma.add_documents(
            collection_name=collection,
            documents=[content],
            metadatas=[full_metadata],
            ids=[doc_id],
            embeddings=[embedding]
        )
        
        logger.info(f"Added document '{title}' to collection '{collection}'")
        
        # Clear cache for this collection
        self.redis.delete_pattern(f"knowledge:query:*")
        
        return KnowledgeDocument(
            id=doc_id,
            collection=collection,
            title=title,
            content=content,
            metadata=full_metadata,
            embedding=embedding
        )
    
    async def update_document(
        self,
        collection: str,
        doc_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Update an existing document.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            title: New title (optional)
            content: New content (optional)
            metadata: New metadata (optional)
        """
        # Prepare update data
        update_data = {}
        
        if content is not None:
            update_data['documents'] = [content]
            # Regenerate embedding
            update_data['embeddings'] = [self.embeddings.embed(content)]
        
        if metadata is not None or title is not None:
            new_metadata = metadata or {}
            if title:
                new_metadata['title'] = title
            new_metadata['updated_at'] = datetime.utcnow().isoformat()
            update_data['metadatas'] = [new_metadata]
        
        # Update in ChromaDB
        if update_data:
            self.chroma.update_documents(
                collection_name=collection,
                ids=[doc_id],
                **update_data
            )
            
            logger.info(f"Updated document {doc_id} in collection {collection}")
            
            # Clear cache
            self.redis.delete_pattern(f"knowledge:query:*")
    
    async def delete_document(self, collection: str, doc_id: str):
        """
        Delete a document from the knowledge base.
        
        Args:
            collection: Collection name
            doc_id: Document ID
        """
        self.chroma.delete_documents(
            collection_name=collection,
            ids=[doc_id]
        )
        
        logger.info(f"Deleted document {doc_id} from collection {collection}")
        
        # Clear cache
        self.redis.delete_pattern(f"knowledge:query:*")
    
    def list_collections(self) -> List[str]:
        """
        List all available collections.
        
        Returns:
            List of collection names
        """
        return self.chroma.list_collections()
    
    async def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """
        Get statistics for a collection.
        
        Args:
            collection: Collection name
            
        Returns:
            Statistics dict
        """
        count = self.chroma.count_documents(collection)
        
        return {
            'collection': collection,
            'document_count': count,
            'embedding_dimension': self.embeddings.dimension
        }
    
    def clear_cache(self):
        """Clear all knowledge query cache."""
        deleted = self.redis.delete_pattern("knowledge:query:*")
        logger.info(f"Cleared {deleted} cached knowledge queries")


# Export
__all__ = ["KnowledgeService", "KnowledgeDocument", "KnowledgeSearchResult", "SynthesizedResponse"]
```

**Test File** (abbreviated):

```python
# mcp-scrt/tests/unit/test_knowledge_service.py

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from mcp_scrt.services.knowledge_service import (
    KnowledgeService,
    KnowledgeDocument,
    KnowledgeSearchResult,
    SynthesizedResponse
)


@pytest.fixture
def mock_chroma():
    """Mock ChromaDB client."""
    chroma = Mock()
    chroma.query.return_value = {
        'ids': [['doc1', 'doc2']],
        'documents': [['Content 1', 'Content 2']],
        'metadatas': [[{'title': 'Title 1'}, {'title': 'Title 2'}]],
        'distances': [[0.2, 0.3]]
    }
    chroma.add_documents.return_value = None
    chroma.update_documents.return_value = None
    chroma.delete_documents.return_value = None
    chroma.list_collections.return_value = ['fundamentals', 'staking']
    chroma.count_documents.return_value = 10
    return chroma


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis = Mock()
    redis.get.return_value = None
    redis.set.return_value = True
    redis.delete_pattern.return_value = 5
    return redis


@pytest.fixture
def mock_ollama():
    """Mock Ollama client."""
    ollama = Mock()
    ollama.chat.return_value = {
        'message': {
            'role': 'assistant',
            'content': 'Secret Network is a blockchain focused on privacy.'
        }
    }
    return ollama


@pytest.fixture
def mock_embeddings():
    """Mock embedding service."""
    embeddings = Mock()
    embeddings.embed.return_value = [0.1] * 384
    embeddings.dimension = 384
    return embeddings


@pytest.fixture
def knowledge_service(mock_chroma, mock_redis, mock_ollama, mock_embeddings):
    """Create knowledge service with mocks."""
    return KnowledgeService(
        chromadb_client=mock_chroma,
        redis_client=mock_redis,
        ollama_client=mock_ollama,
        embedding_service=mock_embeddings
    )


@pytest.mark.asyncio
async def test_search_basic(knowledge_service, mock_chroma, mock_embeddings):
    """Test basic search functionality."""
    results = await knowledge_service.search(
        query="What is Secret Network?",
        top_k=5
    )
    
    assert len(results) == 2
    assert all(isinstance(r, KnowledgeSearchResult) for r in results)
    assert results[0].similarity > results[1].similarity  # Sorted by similarity
    
    # Verify embedding was generated
    mock_embeddings.embed.assert_called_once()


@pytest.mark.asyncio
async def test_search_with_cache(knowledge_service, mock_redis):
    """Test search with cache hit."""
    # Mock cache hit
    cached_data = [{
        'document': {
            'id': 'doc1',
            'collection': 'fundamentals',
            'title': 'Test',
            'content': 'Content',
            'metadata': {}
        },
        'similarity': 0.9,
        'rank': 1
    }]
    mock_redis.get.return_value = cached_data
    
    results = await knowledge_service.search(
        query="test query",
        use_cache=True
    )
    
    assert len(results) == 1
    assert results[0].similarity == 0.9


@pytest.mark.asyncio
async def test_search_and_synthesize(knowledge_service, mock_ollama):
    """Test search with LLM synthesis."""
    response = await knowledge_service.search_and_synthesize(
        query="What is Secret Network?",
        top_k=3
    )
    
    assert isinstance(response, SynthesizedResponse)
    assert response.query == "What is Secret Network?"
    assert len(response.response) > 0
    assert len(response.sources) > 0
    assert 0 <= response.confidence <= 1
    
    # Verify LLM was called
    mock_ollama.chat.assert_called_once()


@pytest.mark.asyncio
async def test_add_document(knowledge_service, mock_chroma, mock_embeddings):
    """Test adding a document."""
    doc = await knowledge_service.add_document(
        collection="fundamentals",
        title="Test Document",
        content="This is test content",
        metadata={"author": "test"}
    )
    
    assert isinstance(doc, KnowledgeDocument)
    assert doc.title == "Test Document"
    assert doc.collection == "fundamentals"
    
    # Verify ChromaDB was called
    mock_chroma.add_documents.assert_called_once()
    
    # Verify cache was cleared
    mock_redis.delete_pattern.assert_called()


@pytest.mark.asyncio
async def test_update_document(knowledge_service, mock_chroma):
    """Test updating a document."""
    await knowledge_service.update_document(
        collection="fundamentals",
        doc_id="doc1",
        title="Updated Title",
        content="Updated content"
    )
    
    # Verify ChromaDB was called
    mock_chroma.update_documents.assert_called_once()


@pytest.mark.asyncio
async def test_delete_document(knowledge_service, mock_chroma):
    """Test deleting a document."""
    await knowledge_service.delete_document(
        collection="fundamentals",
        doc_id="doc1"
    )
    
    # Verify ChromaDB was called
    mock_chroma.delete_documents.assert_called_once()


def test_list_collections(knowledge_service, mock_chroma):
    """Test listing collections."""
    collections = knowledge_service.list_collections()
    
    assert len(collections) == 2
    assert "fundamentals" in collections


@pytest.mark.asyncio
async def test_get_collection_stats(knowledge_service, mock_chroma):
    """Test getting collection statistics."""
    stats = await knowledge_service.get_collection_stats("fundamentals")
    
    assert stats['collection'] == "fundamentals"
    assert stats['document_count'] == 10
    assert stats['embedding_dimension'] == 384


def test_clear_cache(knowledge_service, mock_redis):
    """Test clearing cache."""
    knowledge_service.clear_cache()
    
    mock_redis.delete_pattern.assert_called_with("knowledge:query:*")
```

**Success Criteria**:
- ✅ Service performs semantic search across collections
- ✅ LLM synthesis generates natural responses with citations
- ✅ Document CRUD operations work correctly
- ✅ Caching reduces redundant searches
- ✅ All tests pass

---

## Task 1B.3: Graph Service

**Objective**: Create service for graph database operations including network analysis, relationship tracking, and pattern detection.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/services/graph_service.py
mcp-scrt/tests/unit/test_graph_service.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/services/graph_service.py

"""
Graph service for blockchain network analysis.

This service provides:
- Validator network analysis
- Transaction relationship tracking
- Contract interaction mapping
- Governance pattern detection
- Graph-based recommendations
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Represents a node in the graph."""
    id: str
    label: str
    properties: Dict[str, Any]


@dataclass
class GraphRelationship:
    """Represents a relationship between nodes."""
    from_node: str
    to_node: str
    rel_type: str
    properties: Dict[str, Any]


@dataclass
class ValidatorScore:
    """Validator scoring result."""
    address: str
    moniker: str
    score: float
    reasons: List[str]
    metrics: Dict[str, float]


@dataclass
class NetworkAnalysis:
    """Network analysis results."""
    node_count: int
    relationship_count: int
    density: float
    clusters: List[Dict[str, Any]]
    central_nodes: List[Tuple[str, float]]
    insights: List[str]


class GraphService:
    """
    High-level service for graph database operations.
    
    Features:
    - Automatic node/relationship creation
    - Validator network analysis
    - Contract interaction tracking
    - Governance pattern detection
    - Intelligent caching
    """
    
    def __init__(
        self,
        neo4j_client,
        redis_client,
        cache_ttl: int = 300  # 5 minutes
    ):
        """
        Initialize graph service.
        
        Args:
            neo4j_client: Neo4j client
            redis_client: Redis client for caching
            cache_ttl: Cache TTL in seconds
        """
        self.neo4j = neo4j_client
        self.redis = redis_client
        self.cache_ttl = cache_ttl
        
        logger.info("Initialized GraphService")
    
    async def record_delegation(
        self,
        delegator_address: str,
        validator_address: str,
        amount: str,
        tx_hash: str,
        timestamp: Optional[datetime] = None
    ):
        """
        Record a delegation in the graph.
        
        Args:
            delegator_address: Delegator wallet address
            validator_address: Validator address
            amount: Delegation amount
            tx_hash: Transaction hash
            timestamp: Transaction timestamp
        """
        timestamp = timestamp or datetime.utcnow()
        
        # Create/update wallet node
        self.neo4j.create_node(
            label="Wallet",
            properties={
                "address": delegator_address,
                "last_active": timestamp.isoformat()
            },
            merge=True
        )
        
        # Create/update validator node
        self.neo4j.create_node(
            label="Validator",
            properties={
                "address": validator_address,
                "last_updated": timestamp.isoformat()
            },
            merge=True
        )
        
        # Create delegation relationship
        self.neo4j.create_relationship(
            from_label="Wallet",
            from_prop="address",
            from_value=delegator_address,
            to_label="Validator",
            to_prop="address",
            to_value=validator_address,
            rel_type="DELEGATES",
            rel_properties={
                "amount": amount,
                "timestamp": timestamp.isoformat(),
                "tx_hash": tx_hash
            }
        )
        
        # Clear related caches
        self.redis.delete_pattern(f"graph:validator_network:*")
        self.redis.delete_pattern(f"graph:wallet:{delegator_address}:*")
        
        logger.info(f"Recorded delegation: {delegator_address} -> {validator_address}")
    
    async def record_transfer(
        self,
        from_address: str,
        to_address: str,
        amount: str,
        tx_hash: str,
        timestamp: Optional[datetime] = None
    ):
        """
        Record a token transfer in the graph.
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            amount: Transfer amount
            tx_hash: Transaction hash
            timestamp: Transaction timestamp
        """
        timestamp = timestamp or datetime.utcnow()
        
        # Create/update both wallet nodes
        for address in [from_address, to_address]:
            self.neo4j.create_node(
                label="Wallet",
                properties={
                    "address": address,
                    "last_active": timestamp.isoformat()
                },
                merge=True
            )
        
        # Create transfer relationship
        self.neo4j.create_relationship(
            from_label="Wallet",
            from_prop="address",
            from_value=from_address,
            to_label="Wallet",
            to_prop="address",
            to_value=to_address,
            rel_type="SENT",
            rel_properties={
                "amount": amount,
                "timestamp": timestamp.isoformat(),
                "tx_hash": tx_hash
            }
        )
        
        logger.info(f"Recorded transfer: {from_address} -> {to_address}")
    
    async def record_vote(
        self,
        voter_address: str,
        proposal_id: int,
        vote_option: str,
        tx_hash: str,
        timestamp: Optional[datetime] = None
    ):
        """
        Record a governance vote in the graph.
        
        Args:
            voter_address: Voter wallet address
            proposal_id: Proposal ID
            vote_option: Vote option (YES, NO, ABSTAIN, etc.)
            tx_hash: Transaction hash
            timestamp: Transaction timestamp
        """
        timestamp = timestamp or datetime.utcnow()
        
        # Create/update wallet node
        self.neo4j.create_node(
            label="Wallet",
            properties={
                "address": voter_address,
                "last_active": timestamp.isoformat()
            },
            merge=True
        )
        
        # Create/update proposal node
        self.neo4j.create_node(
            label="Proposal",
            properties={
                "id": proposal_id,
                "last_updated": timestamp.isoformat()
            },
            merge=True
        )
        
        # Create vote relationship
        self.neo4j.create_relationship(
            from_label="Wallet",
            from_prop="address",
            from_value=voter_address,
            to_label="Proposal",
            to_prop="id",
            to_value=proposal_id,
            rel_type="VOTED",
            rel_properties={
                "option": vote_option,
                "timestamp": timestamp.isoformat(),
                "tx_hash": tx_hash
            }
        )
        
        logger.info(f"Recorded vote: {voter_address} on proposal {proposal_id}")
    
    async def record_contract_execution(
        self,
        executor_address: str,
        contract_address: str,
        method: str,
        tx_hash: str,
        success: bool = True,
        timestamp: Optional[datetime] = None
    ):
        """
        Record a contract execution in the graph.
        
        Args:
            executor_address: Executor wallet address
            contract_address: Contract address
            method: Contract method executed
            tx_hash: Transaction hash
            success: Whether execution succeeded
            timestamp: Transaction timestamp
        """
        timestamp = timestamp or datetime.utcnow()
        
        # Create/update wallet node
        self.neo4j.create_node(
            label="Wallet",
            properties={
                "address": executor_address,
                "last_active": timestamp.isoformat()
            },
            merge=True
        )
        
        # Create/update contract node
        self.neo4j.create_node(
            label="Contract",
            properties={
                "address": contract_address,
                "last_updated": timestamp.isoformat()
            },
            merge=True
        )
        
        # Create execution relationship
        self.neo4j.create_relationship(
            from_label="Wallet",
            from_prop="address",
            from_value=executor_address,
            to_label="Contract",
            to_prop="address",
            to_value=contract_address,
            rel_type="EXECUTED",
            rel_properties={
                "method": method,
                "success": success,
                "timestamp": timestamp.isoformat(),
                "tx_hash": tx_hash
            }
        )
        
        logger.info(f"Recorded contract execution: {executor_address} -> {contract_address}")
    
    async def analyze_validator_network(
        self,
        validator_address: Optional[str] = None,
        depth: int = 2,
        use_cache: bool = True
    ) -> NetworkAnalysis:
        """
        Analyze validator delegation network.
        
        Args:
            validator_address: Optional validator to focus on
            depth: Analysis depth (1-3)
            use_cache: Use cached results
            
        Returns:
            Network analysis results
        """
        # Check cache
        if use_cache:
            cache_key = f"graph:validator_network:{validator_address}:{depth}"
            cached = self.redis.get(cache_key)
            if cached:
                logger.info("Cache hit for validator network analysis")
                return NetworkAnalysis(**cached)
        
        # Build query
        if validator_address:
            # Focused analysis
            query = f"""
            MATCH (v:Validator {{address: $validator_address}})
            OPTIONAL MATCH path = (w:Wallet)-[:DELEGATES*1..{depth}]->(v)
            WITH v, collect(path) as paths, count(w) as delegator_count
            OPTIONAL MATCH (v)<-[d:DELEGATES]-(w2:Wallet)
            WITH v, paths, delegator_count, sum(toFloat(d.amount)) as total_delegated
            RETURN v, paths, delegator_count, total_delegated
            """
            params = {"validator_address": validator_address}
        else:
            # Global analysis
            query = """
            MATCH (v:Validator)
            OPTIONAL MATCH (v)<-[d:DELEGATES]-(w:Wallet)
            WITH v, count(w) as delegator_count, sum(toFloat(d.amount)) as total_delegated
            RETURN v, delegator_count, total_delegated
            ORDER BY total_delegated DESC
            LIMIT 50
            """
            params = {}
        
        # Execute query
        results = self.neo4j.execute_query(query, params)
        
        # Process results
        node_count = len(results)
        relationship_count = sum(r.get('delegator_count', 0) for r in results)
        
        # Calculate density (simplified)
        max_edges = node_count * (node_count - 1) if node_count > 1 else 1
        density = relationship_count / max_edges if max_edges > 0 else 0
        
        # Identify central nodes (validators with most delegators)
        central_nodes = [
            (r['v']['address'], r.get('delegator_count', 0))
            for r in results[:10]
        ]
        
        # Generate insights
        insights = []
        if results:
            top_validator = results[0]
            insights.append(
                f"Top validator has {top_validator.get('delegator_count', 0)} delegators"
            )
            
            if relationship_count > 0:
                avg_delegations = relationship_count / node_count
                insights.append(
                    f"Average {avg_delegations:.1f} delegations per validator"
                )
        
        analysis = NetworkAnalysis(
            node_count=node_count,
            relationship_count=relationship_count,
            density=density,
            clusters=[],  # Could implement community detection
            central_nodes=central_nodes,
            insights=insights
        )
        
        # Cache results
        if use_cache:
            self.redis.set(cache_key, asdict(analysis), ex=self.cache_ttl)
        
        return analysis
    
    async def recommend_validators(
        self,
        wallet_address: str,
        count: int = 5
    ) -> List[ValidatorScore]:
        """
        Recommend validators based on network analysis.
        
        Args:
            wallet_address: Wallet address for personalized recommendations
            count: Number of validators to recommend
            
        Returns:
            List of validator scores with reasons
        """
        # Get all validators with metrics
        query = """
        MATCH (v:Validator)
        OPTIONAL MATCH (v)<-[d:DELEGATES]-(w:Wallet)
        WITH v, 
             count(w) as delegator_count,
             sum(toFloat(d.amount)) as total_delegated,
             avg(toFloat(d.amount)) as avg_delegation
        RETURN v.address as address,
               v.moniker as moniker,
               v.commission as commission,
               v.voting_power as voting_power,
               v.uptime as uptime,
               delegator_count,
               total_delegated,
               avg_delegation
        ORDER BY total_delegated DESC
        LIMIT 50
        """
        
        results = self.neo4j.execute_query(query, {})
        
        scores = []
        for result in results:
            # Calculate score based on multiple factors
            score = 0.0
            reasons = []
            metrics = {}
            
            # Factor 1: Decentralization (penalize high voting power)
            voting_power = float(result.get('voting_power', 0))
            if voting_power < 5:
                score += 30
                reasons.append("Good decentralization (low voting power)")
            elif voting_power < 10:
                score += 20
            else:
                score += 5
                reasons.append("High voting power (less decentralized)")
            
            metrics['voting_power'] = voting_power
            
            # Factor 2: Commission (favor 5-10% range)
            commission = float(result.get('commission', 10))
            if 5 <= commission <= 10:
                score += 25
                reasons.append(f"Reasonable commission ({commission}%)")
            elif commission < 5:
                score += 15
                reasons.append(f"Low commission ({commission}%) - verify sustainability")
            else:
                score += 10
            
            metrics['commission'] = commission
            
            # Factor 3: Uptime
            uptime = float(result.get('uptime', 99))
            if uptime >= 99.9:
                score += 25
                reasons.append(f"Excellent uptime ({uptime}%)")
            elif uptime >= 99:
                score += 20
            else:
                score += 10
                reasons.append(f"Moderate uptime ({uptime}%)")
            
            metrics['uptime'] = uptime
            
            # Factor 4: Community (delegator count)
            delegator_count = int(result.get('delegator_count', 0))
            if delegator_count > 100:
                score += 20
                reasons.append(f"Strong community ({delegator_count} delegators)")
            elif delegator_count > 50:
                score += 15
            else:
                score += 10
            
            metrics['delegator_count'] = delegator_count
            
            # Normalize score to 0-10 scale
            final_score = min(score / 10, 10.0)
            
            scores.append(ValidatorScore(
                address=result['address'],
                moniker=result.get('moniker', 'Unknown'),
                score=final_score,
                reasons=reasons[:3],  # Top 3 reasons
                metrics=metrics
            ))
        
        # Sort by score and return top N
        scores.sort(key=lambda x: x.score, reverse=True)
        return scores[:count]
    
    async def get_wallet_activity(
        self,
        wallet_address: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get comprehensive activity for a wallet.
        
        Args:
            wallet_address: Wallet address
            limit: Maximum number of activities
            
        Returns:
            Activity summary with relationships
        """
        query = """
        MATCH (w:Wallet {address: $wallet_address})
        OPTIONAL MATCH (w)-[r]->(target)
        WITH w, type(r) as rel_type, collect(target) as targets, count(r) as count
        RETURN w, rel_type, targets, count
        ORDER BY count DESC
        LIMIT $limit
        """
        
        results = self.neo4j.execute_query(
            query,
            {"wallet_address": wallet_address, "limit": limit}
        )
        
        # Aggregate results
        activities = {
            "wallet": wallet_address,
            "delegations": 0,
            "transfers": 0,
            "votes": 0,
            "contract_executions": 0,
            "related_validators": [],
            "related_wallets": [],
            "related_contracts": [],
            "related_proposals": []
        }
        
        for result in results:
            rel_type = result.get('rel_type')
            count = result.get('count', 0)
            
            if rel_type == 'DELEGATES':
                activities['delegations'] = count
                activities['related_validators'] = [
                    t['address'] for t in result.get('targets', [])
                ]
            elif rel_type == 'SENT':
                activities['transfers'] = count
                activities['related_wallets'] = [
                    t['address'] for t in result.get('targets', [])
                ]
            elif rel_type == 'VOTED':
                activities['votes'] = count
                activities['related_proposals'] = [
                    t['id'] for t in result.get('targets', [])
                ]
            elif rel_type == 'EXECUTED':
                activities['contract_executions'] = count
                activities['related_contracts'] = [
                    t['address'] for t in result.get('targets', [])
                ]
        
        return activities
    
    def clear_cache(self):
        """Clear all graph analysis cache."""
        deleted = self.redis.delete_pattern("graph:*")
        logger.info(f"Cleared {deleted} cached graph analyses")


# Export
__all__ = [
    "GraphService",
    "GraphNode",
    "GraphRelationship",
    "ValidatorScore",
    "NetworkAnalysis"
]
```

**Test File** (abbreviated for brevity - follow same pattern as previous tests):

```python
# mcp-scrt/tests/unit/test_graph_service.py

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from mcp_scrt.services.graph_service import GraphService, ValidatorScore, NetworkAnalysis


@pytest.fixture
def mock_neo4j():
    """Mock Neo4j client."""
    neo4j = Mock()
    neo4j.create_node.return_value = {}
    neo4j.create_relationship.return_value = {}
    neo4j.execute_query.return_value = []
    return neo4j


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis = Mock()
    redis.get.return_value = None
    redis.set.return_value = True
    redis.delete_pattern.return_value = 5
    return redis


@pytest.fixture
def graph_service(mock_neo4j, mock_redis):
    """Create graph service with mocks."""
    return GraphService(
        neo4j_client=mock_neo4j,
        redis_client=mock_redis
    )


@pytest.mark.asyncio
async def test_record_delegation(graph_service, mock_neo4j):
    """Test recording a delegation."""
    await graph_service.record_delegation(
        delegator_address="secret1abc",
        validator_address="secretvaloper1xyz",
        amount="1000000",
        tx_hash="ABC123"
    )
    
    # Verify nodes were created
    assert mock_neo4j.create_node.call_count == 2
    
    # Verify relationship was created
    mock_neo4j.create_relationship.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_validator_network(graph_service, mock_neo4j):
    """Test validator network analysis."""
    # Mock query results
    mock_neo4j.execute_query.return_value = [
        {'v': {'address': 'val1'}, 'delegator_count': 100, 'total_delegated': 1000000},
        {'v': {'address': 'val2'}, 'delegator_count': 50, 'total_delegated': 500000}
    ]
    
    analysis = await graph_service.analyze_validator_network()
    
    assert isinstance(analysis, NetworkAnalysis)
    assert analysis.node_count == 2
    assert len(analysis.central_nodes) > 0


@pytest.mark.asyncio
async def test_recommend_validators(graph_service, mock_neo4j):
    """Test validator recommendations."""
    # Mock validator data
    mock_neo4j.execute_query.return_value = [
        {
            'address': 'val1',
            'moniker': 'Validator 1',
            'commission': 5.0,
            'voting_power': 3.0,
            'uptime': 99.9,
            'delegator_count': 150
        }
    ]
    
    recommendations = await graph_service.recommend_validators(
        wallet_address="secret1abc",
        count=5
    )
    
    assert len(recommendations) > 0
    assert all(isinstance(r, ValidatorScore) for r in recommendations)
    assert recommendations[0].score > 0
```

**Success Criteria**:
- ✅ Service records blockchain activities in graph
- ✅ Network analysis identifies patterns
- ✅ Validator recommendations use multi-factor scoring
- ✅ Caching improves performance
- ✅ All tests pass

---

## Summary of Part 1B Completed

At this point, you have completed the **Service Layer** with three core services:

✅ **Embedding Service**:
- Text vectorization with sentence-transformers
- Batch processing
- Redis caching for embeddings
- Cosine similarity calculations

✅ **Knowledge Service**:
- Semantic search across ChromaDB collections
- LLM synthesis with Ollama for natural responses
- Document lifecycle management
- Intelligent query caching

✅ **Graph Service**:
- Automatic graph recording for blockchain activities
- Validator network analysis
- Multi-factor validator recommendations
- Wallet activity tracking

