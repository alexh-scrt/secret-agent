# Detailed Implementation Plan for Claude Code

## Overview

This plan breaks down the implementation into two major parts with specific, actionable tasks for Claude Code. Each task includes file paths, code structure, dependencies, and success criteria.

---

# PART 1: MCP SERVER EXTENSION

## Phase 1A: Database Client Infrastructure (Foundation)

### Task 1A.1: ChromaDB Client Wrapper

**Objective**: Create a robust ChromaDB client with connection management, error handling, and health checks.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/integrations/__init__.py
mcp-scrt/src/mcp_scrt/integrations/chromadb_client.py
mcp-scrt/tests/integration/test_chromadb_client.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/integrations/chromadb_client.py

"""
ChromaDB client wrapper with connection pooling and error handling.

This module provides a clean interface to ChromaDB with:
- Automatic connection management
- Error handling and retries
- Health checks
- Collection management
- Embedding integration
"""

import os
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
import logging

logger = logging.getLogger(__name__)


class ChromaDBClient:
    """
    Wrapper for ChromaDB operations.
    
    Features:
    - Connection pooling
    - Health checks
    - Collection lifecycle management
    - Batch operations
    - Error handling
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        use_ssl: bool = False,
        api_key: Optional[str] = None
    ):
        """
        Initialize ChromaDB client.
        
        Args:
            host: ChromaDB host (default: from env CHROMADB_HOST)
            port: ChromaDB port (default: from env CHROMADB_PORT)
            use_ssl: Use SSL/TLS connection
            api_key: API key for authentication (default: from env API_KEY)
        """
        self.host = host or os.getenv("CHROMADB_HOST", "localhost")
        self.port = port or int(os.getenv("CHROMADB_PORT", "8000"))
        self.use_ssl = use_ssl
        self.api_key = api_key or os.getenv("API_KEY")
        
        self._client = None
        self._collections_cache: Dict[str, Collection] = {}
    
    def connect(self) -> chromadb.Client:
        """
        Establish connection to ChromaDB.
        
        Returns:
            ChromaDB client instance
            
        Raises:
            ConnectionError: If connection fails
        """
        if self._client is not None:
            return self._client
        
        try:
            settings = Settings(
                chroma_api_impl="chromadb.api.fastapi.FastAPI",
                chroma_server_host=self.host,
                chroma_server_http_port=self.port,
            )
            
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            self._client = chromadb.HttpClient(
                host=self.host,
                port=self.port,
                ssl=self.use_ssl,
                headers=headers,
                settings=settings
            )
            
            # Test connection
            self._client.heartbeat()
            logger.info(f"Connected to ChromaDB at {self.host}:{self.port}")
            
            return self._client
            
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise ConnectionError(f"ChromaDB connection failed: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check ChromaDB health status.
        
        Returns:
            Health status dict with status and metrics
        """
        try:
            client = self.connect()
            heartbeat = client.heartbeat()
            
            return {
                "status": "healthy",
                "heartbeat": heartbeat,
                "host": self.host,
                "port": self.port,
                "collections_count": len(self.list_collections())
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "host": self.host,
                "port": self.port
            }
    
    def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict] = None,
        embedding_function: Optional[Any] = None
    ) -> Collection:
        """
        Get existing collection or create if doesn't exist.
        
        Args:
            name: Collection name
            metadata: Collection metadata
            embedding_function: Custom embedding function
            
        Returns:
            Collection instance
        """
        # Check cache
        if name in self._collections_cache:
            return self._collections_cache[name]
        
        client = self.connect()
        
        try:
            collection = client.get_collection(
                name=name,
                embedding_function=embedding_function
            )
            logger.info(f"Retrieved existing collection: {name}")
        except Exception:
            # Collection doesn't exist, create it
            collection = client.create_collection(
                name=name,
                metadata=metadata or {},
                embedding_function=embedding_function
            )
            logger.info(f"Created new collection: {name}")
        
        # Cache collection
        self._collections_cache[name] = collection
        return collection
    
    def list_collections(self) -> List[str]:
        """
        List all collections.
        
        Returns:
            List of collection names
        """
        client = self.connect()
        collections = client.list_collections()
        return [c.name for c in collections]
    
    def delete_collection(self, name: str):
        """
        Delete a collection.
        
        Args:
            name: Collection name to delete
        """
        client = self.connect()
        client.delete_collection(name=name)
        
        # Remove from cache
        if name in self._collections_cache:
            del self._collections_cache[name]
        
        logger.info(f"Deleted collection: {name}")
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict],
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None
    ):
        """
        Add documents to collection.
        
        Args:
            collection_name: Target collection
            documents: Document texts
            metadatas: Document metadata
            ids: Document IDs
            embeddings: Pre-computed embeddings (optional)
        """
        collection = self.get_or_create_collection(collection_name)
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        
        logger.info(f"Added {len(documents)} documents to {collection_name}")
    
    def query(
        self,
        collection_name: str,
        query_texts: Optional[List[str]] = None,
        query_embeddings: Optional[List[List[float]]] = None,
        n_results: int = 5,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ) -> Dict:
        """
        Query collection for similar documents.
        
        Args:
            collection_name: Collection to query
            query_texts: Query texts (will be embedded)
            query_embeddings: Pre-computed query embeddings
            n_results: Number of results to return
            where: Metadata filters
            where_document: Document content filters
            
        Returns:
            Query results with documents, distances, metadatas
        """
        collection = self.get_or_create_collection(collection_name)
        
        results = collection.query(
            query_texts=query_texts,
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            where_document=where_document
        )
        
        return results
    
    def update_documents(
        self,
        collection_name: str,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict]] = None,
        embeddings: Optional[List[List[float]]] = None
    ):
        """
        Update existing documents.
        
        Args:
            collection_name: Collection name
            ids: Document IDs to update
            documents: New document texts
            metadatas: New metadata
            embeddings: New embeddings
        """
        collection = self.get_or_create_collection(collection_name)
        
        collection.update(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        logger.info(f"Updated {len(ids)} documents in {collection_name}")
    
    def delete_documents(
        self,
        collection_name: str,
        ids: List[str]
    ):
        """
        Delete documents from collection.
        
        Args:
            collection_name: Collection name
            ids: Document IDs to delete
        """
        collection = self.get_or_create_collection(collection_name)
        collection.delete(ids=ids)
        
        logger.info(f"Deleted {len(ids)} documents from {collection_name}")
    
    def count_documents(self, collection_name: str) -> int:
        """
        Count documents in collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Number of documents
        """
        collection = self.get_or_create_collection(collection_name)
        return collection.count()
    
    def close(self):
        """Close client connection and clear cache."""
        self._client = None
        self._collections_cache.clear()
        logger.info("ChromaDB client closed")
```

**Test File**:
```python
# mcp-scrt/tests/integration/test_chromadb_client.py

import pytest
from mcp_scrt.integrations.chromadb_client import ChromaDBClient


@pytest.fixture
def chroma_client():
    """Fixture for ChromaDB client."""
    client = ChromaDBClient()
    yield client
    client.close()


def test_connection(chroma_client):
    """Test basic connection."""
    client_instance = chroma_client.connect()
    assert client_instance is not None


def test_health_check(chroma_client):
    """Test health check."""
    health = chroma_client.health_check()
    assert health["status"] == "healthy"
    assert "heartbeat" in health


def test_collection_lifecycle(chroma_client):
    """Test collection CRUD operations."""
    # Create collection
    collection = chroma_client.get_or_create_collection("test_collection")
    assert collection is not None
    
    # List collections
    collections = chroma_client.list_collections()
    assert "test_collection" in collections
    
    # Delete collection
    chroma_client.delete_collection("test_collection")
    collections = chroma_client.list_collections()
    assert "test_collection" not in collections


def test_add_and_query_documents(chroma_client):
    """Test adding and querying documents."""
    collection_name = "test_docs"
    
    # Add documents
    chroma_client.add_documents(
        collection_name=collection_name,
        documents=["Secret Network is a blockchain", "Privacy is important"],
        metadatas=[{"source": "test1"}, {"source": "test2"}],
        ids=["doc1", "doc2"]
    )
    
    # Query
    results = chroma_client.query(
        collection_name=collection_name,
        query_texts=["blockchain privacy"],
        n_results=2
    )
    
    assert len(results["ids"][0]) == 2
    
    # Cleanup
    chroma_client.delete_collection(collection_name)


def test_update_documents(chroma_client):
    """Test document updates."""
    collection_name = "test_updates"
    
    # Add initial documents
    chroma_client.add_documents(
        collection_name=collection_name,
        documents=["Original text"],
        metadatas=[{"version": 1}],
        ids=["doc1"]
    )
    
    # Update
    chroma_client.update_documents(
        collection_name=collection_name,
        ids=["doc1"],
        documents=["Updated text"],
        metadatas=[{"version": 2}]
    )
    
    # Verify update
    results = chroma_client.query(
        collection_name=collection_name,
        query_texts=["Updated text"],
        n_results=1
    )
    
    assert results["metadatas"][0][0]["version"] == 2
    
    # Cleanup
    chroma_client.delete_collection(collection_name)
```

**Success Criteria**:
- ✅ Client connects to remote ChromaDB
- ✅ Health check returns status
- ✅ Collections can be created, listed, deleted
- ✅ Documents can be added, queried, updated, deleted
- ✅ All tests pass

---

### Task 1A.2: Neo4j Client Wrapper

**Objective**: Create Neo4j client with connection pooling, transaction management, and Cypher query execution.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/integrations/neo4j_client.py
mcp-scrt/tests/integration/test_neo4j_client.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/integrations/neo4j_client.py

"""
Neo4j client wrapper with connection pooling and transaction management.

This module provides a clean interface to Neo4j with:
- Connection pooling
- Transaction management
- Cypher query execution
- Health checks
- Graph operations
"""

import os
from typing import List, Dict, Optional, Any
from neo4j import GraphDatabase, AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
import logging

logger = logging.getLogger(__name__)


class Neo4jClient:
    """
    Wrapper for Neo4j operations.
    
    Features:
    - Connection pooling
    - Transaction management
    - Cypher query execution
    - Batch operations
    - Health checks
    """
    
    def __init__(
        self,
        uri: str = None,
        username: str = None,
        password: str = None,
        database: str = "neo4j"
    ):
        """
        Initialize Neo4j client.
        
        Args:
            uri: Neo4j connection URI (default: from env NEO4J_URL)
            username: Neo4j username (default: from env NEO4J_USER)
            password: Neo4j password (default: from env NEO4J_PASSWORD)
            database: Database name (default: neo4j)
        """
        self.uri = uri or os.getenv("NEO4J_URL", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD")
        self.database = database
        
        self._driver = None
    
    def connect(self):
        """
        Establish connection to Neo4j.
        
        Returns:
            Neo4j driver instance
            
        Raises:
            ConnectionError: If connection fails
            AuthError: If authentication fails
        """
        if self._driver is not None:
            return self._driver
        
        try:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            
            # Test connection
            self._driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
            
            return self._driver
            
        except AuthError as e:
            logger.error(f"Neo4j authentication failed: {e}")
            raise AuthError(f"Invalid Neo4j credentials: {e}")
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable: {e}")
            raise ConnectionError(f"Cannot connect to Neo4j: {e}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise ConnectionError(f"Neo4j connection failed: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check Neo4j health status.
        
        Returns:
            Health status dict with status and metrics
        """
        try:
            driver = self.connect()
            
            with driver.session(database=self.database) as session:
                result = session.run("RETURN 1 AS health")
                record = result.single()
                
                # Get database info
                db_info = session.run("""
                    CALL dbms.components()
                    YIELD name, versions, edition
                    RETURN name, versions, edition
                """).data()
                
                return {
                    "status": "healthy",
                    "health_check": record["health"],
                    "database": self.database,
                    "uri": self.uri,
                    "info": db_info
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "uri": self.uri
            }
    
    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records as dicts
        """
        driver = self.connect()
        
        with driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return result.data()
    
    def execute_write_query(
        self,
        query: str,
        parameters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Execute a write query in a transaction.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records as dicts
        """
        driver = self.connect()
        
        def _execute_write(tx):
            result = tx.run(query, parameters or {})
            return result.data()
        
        with driver.session(database=self.database) as session:
            return session.execute_write(_execute_write)
    
    def create_node(
        self,
        label: str,
        properties: Dict,
        merge: bool = True
    ) -> Dict:
        """
        Create or merge a node.
        
        Args:
            label: Node label (e.g., "Wallet", "Validator")
            properties: Node properties
            merge: Use MERGE instead of CREATE (avoid duplicates)
            
        Returns:
            Created node properties
        """
        # Build properties string for Cypher
        props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        
        if merge:
            # Use unique property for merge (typically address or id)
            unique_key = properties.get("address") or properties.get("id")
            if not unique_key:
                raise ValueError("Must provide 'address' or 'id' for MERGE")
            
            unique_prop = "address" if "address" in properties else "id"
            query = f"""
                MERGE (n:{label} {{{unique_prop}: ${unique_prop}}})
                ON CREATE SET n = $properties
                ON MATCH SET n = $properties
                RETURN n
            """
            params = {unique_prop: unique_key, "properties": properties}
        else:
            query = f"""
                CREATE (n:{label} {{{props_str}}})
                RETURN n
            """
            params = properties
        
        result = self.execute_write_query(query, params)
        return result[0]["n"] if result else {}
    
    def create_relationship(
        self,
        from_label: str,
        from_prop: str,
        from_value: Any,
        to_label: str,
        to_prop: str,
        to_value: Any,
        rel_type: str,
        rel_properties: Optional[Dict] = None
    ) -> Dict:
        """
        Create a relationship between two nodes.
        
        Args:
            from_label: Source node label
            from_prop: Source node property to match on
            from_value: Source node property value
            to_label: Target node label
            to_prop: Target node property to match on
            to_value: Target node property value
            rel_type: Relationship type (e.g., "DELEGATES", "SENT")
            rel_properties: Relationship properties
            
        Returns:
            Created relationship properties
        """
        rel_props = rel_properties or {}
        props_str = ", ".join([f"{k}: ${k}" for k in rel_props.keys()])
        props_clause = f"{{{props_str}}}" if props_str else ""
        
        query = f"""
            MATCH (from:{from_label} {{{from_prop}: $from_value}})
            MATCH (to:{to_label} {{{to_prop}: $to_value}})
            CREATE (from)-[r:{rel_type} {props_clause}]->(to)
            RETURN r
        """
        
        params = {
            "from_value": from_value,
            "to_value": to_value,
            **rel_props
        }
        
        result = self.execute_write_query(query, params)
        return result[0]["r"] if result else {}
    
    def find_path(
        self,
        from_label: str,
        from_prop: str,
        from_value: Any,
        to_label: str,
        to_prop: str,
        to_value: Any,
        max_depth: int = 3
    ) -> List[Dict]:
        """
        Find shortest path between two nodes.
        
        Args:
            from_label: Source node label
            from_prop: Source node property
            from_value: Source node value
            to_label: Target node label
            to_prop: Target node property
            to_value: Target node value
            max_depth: Maximum path depth
            
        Returns:
            List of paths
        """
        query = f"""
            MATCH path = shortestPath(
                (from:{from_label} {{{from_prop}: $from_value}})
                -[*..{max_depth}]-
                (to:{to_label} {{{to_prop}: $to_value}})
            )
            RETURN path
            LIMIT 10
        """
        
        params = {
            "from_value": from_value,
            "to_value": to_value
        }
        
        return self.execute_query(query, params)
    
    def get_neighbors(
        self,
        label: str,
        prop: str,
        value: Any,
        depth: int = 1,
        direction: str = "both"
    ) -> List[Dict]:
        """
        Get neighboring nodes.
        
        Args:
            label: Node label
            prop: Node property to match
            value: Node property value
            depth: Relationship depth
            direction: "in", "out", or "both"
            
        Returns:
            List of neighbor nodes
        """
        direction_pattern = {
            "in": "<-[*1..%d]-",
            "out": "-[*1..%d]->",
            "both": "-[*1..%d]-"
        }
        
        pattern = direction_pattern[direction] % depth
        
        query = f"""
            MATCH (n:{label} {{{prop}: $value}})
            {pattern}(neighbor)
            RETURN DISTINCT neighbor
            LIMIT 100
        """
        
        return self.execute_query(query, {"value": value})
    
    def delete_node(
        self,
        label: str,
        prop: str,
        value: Any,
        detach: bool = True
    ):
        """
        Delete a node and optionally its relationships.
        
        Args:
            label: Node label
            prop: Node property to match
            value: Node property value
            detach: Delete relationships too
        """
        detach_clause = "DETACH " if detach else ""
        
        query = f"""
            MATCH (n:{label} {{{prop}: $value}})
            {detach_clause}DELETE n
        """
        
        self.execute_write_query(query, {"value": value})
        logger.info(f"Deleted {label} node with {prop}={value}")
    
    def clear_database(self):
        """
        Clear all nodes and relationships.
        WARNING: Use only in testing!
        """
        query = "MATCH (n) DETACH DELETE n"
        self.execute_write_query(query)
        logger.warning("Database cleared - all nodes and relationships deleted")
    
    def close(self):
        """Close driver connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j driver closed")
```

**Test File**:
```python
# mcp-scrt/tests/integration/test_neo4j_client.py

import pytest
from mcp_scrt.integrations.neo4j_client import Neo4jClient


@pytest.fixture
def neo4j_client():
    """Fixture for Neo4j client."""
    client = Neo4jClient()
    yield client
    # Cleanup test data
    client.execute_write_query("MATCH (n:TestNode) DETACH DELETE n")
    client.close()


def test_connection(neo4j_client):
    """Test basic connection."""
    driver = neo4j_client.connect()
    assert driver is not None


def test_health_check(neo4j_client):
    """Test health check."""
    health = neo4j_client.health_check()
    assert health["status"] == "healthy"
    assert health["health_check"] == 1


def test_create_node(neo4j_client):
    """Test node creation."""
    node = neo4j_client.create_node(
        label="TestNode",
        properties={"id": "test1", "name": "Test Node"},
        merge=True
    )
    assert node["id"] == "test1"
    assert node["name"] == "Test Node"


def test_create_relationship(neo4j_client):
    """Test relationship creation."""
    # Create two nodes
    neo4j_client.create_node(
        label="TestNode",
        properties={"id": "node1", "name": "Node 1"}
    )
    neo4j_client.create_node(
        label="TestNode",
        properties={"id": "node2", "name": "Node 2"}
    )
    
    # Create relationship
    rel = neo4j_client.create_relationship(
        from_label="TestNode",
        from_prop="id",
        from_value="node1",
        to_label="TestNode",
        to_prop="id",
        to_value="node2",
        rel_type="CONNECTS_TO",
        rel_properties={"weight": 1.0}
    )
    
    assert rel["weight"] == 1.0


def test_find_path(neo4j_client):
    """Test path finding."""
    # Create chain: node1 -> node2 -> node3
    for i in range(1, 4):
        neo4j_client.create_node(
            label="TestNode",
            properties={"id": f"node{i}", "name": f"Node {i}"}
        )
    
    neo4j_client.create_relationship(
        "TestNode", "id", "node1",
        "TestNode", "id", "node2",
        "CONNECTS_TO"
    )
    neo4j_client.create_relationship(
        "TestNode", "id", "node2",
        "TestNode", "id", "node3",
        "CONNECTS_TO"
    )
    
    # Find path
    paths = neo4j_client.find_path(
        "TestNode", "id", "node1",
        "TestNode", "id", "node3",
        max_depth=3
    )
    
    assert len(paths) > 0


def test_get_neighbors(neo4j_client):
    """Test getting neighbor nodes."""
    # Create hub node with connections
    neo4j_client.create_node(
        label="TestNode",
        properties={"id": "hub", "name": "Hub"}
    )
    
    for i in range(3):
        neo4j_client.create_node(
            label="TestNode",
            properties={"id": f"spoke{i}", "name": f"Spoke {i}"}
        )
        neo4j_client.create_relationship(
            "TestNode", "id", "hub",
            "TestNode", "id", f"spoke{i}",
            "CONNECTS_TO"
        )
    
    # Get neighbors
    neighbors = neo4j_client.get_neighbors(
        label="TestNode",
        prop="id",
        value="hub",
        depth=1,
        direction="out"
    )
    
    assert len(neighbors) == 3


def test_delete_node(neo4j_client):
    """Test node deletion."""
    # Create node
    neo4j_client.create_node(
        label="TestNode",
        properties={"id": "delete_me", "name": "Delete Me"}
    )
    
    # Delete node
    neo4j_client.delete_node(
        label="TestNode",
        prop="id",
        value="delete_me"
    )
    
    # Verify deletion
    result = neo4j_client.execute_query(
        "MATCH (n:TestNode {id: 'delete_me'}) RETURN n"
    )
    assert len(result) == 0
```

**Success Criteria**:
- ✅ Client connects to remote Neo4j
- ✅ Health check returns status
- ✅ Nodes can be created, queried, deleted
- ✅ Relationships can be created
- ✅ Path finding works
- ✅ All tests pass

---

### Task 1A.3: Redis Client Wrapper

**Objective**: Create Redis client with connection pooling, caching operations, and pattern-based key management.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/integrations/redis_client.py
mcp-scrt/tests/integration/test_redis_client.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/integrations/redis_client.py

"""
Redis client wrapper with connection pooling and caching utilities.

This module provides a clean interface to Redis with:
- Connection pooling
- Key pattern management
- TTL management
- Batch operations
- Health checks
"""

import os
import json
from typing import Any, Optional, List, Dict
import redis
from redis.connection import ConnectionPool
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Wrapper for Redis operations.
    
    Features:
    - Connection pooling
    - JSON serialization
    - TTL management
    - Pattern-based operations
    - Health checks
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        password: str = None,
        db: int = 0,
        decode_responses: bool = True
    ):
        """
        Initialize Redis client.
        
        Args:
            host: Redis host (default: from env REDIS_HOST)
            port: Redis port (default: from env REDIS_PORT)
            password: Redis password (default: from env REDIS_PASSWORD)
            db: Database number (default: 0)
            decode_responses: Decode responses to strings
        """
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.password = password or os.getenv("REDIS_PASSWORD")
        self.db = db
        self.decode_responses = decode_responses
        
        self._client = None
        self._pool = None
    
    def connect(self) -> redis.Redis:
        """
        Establish connection to Redis.
        
        Returns:
            Redis client instance
            
        Raises:
            ConnectionError: If connection fails
        """
        if self._client is not None:
            return self._client
        
        try:
            # Create connection pool
            self._pool = ConnectionPool(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=self.decode_responses,
                max_connections=10
            )
            
            # Create client
            self._client = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            self._client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
            
            return self._client
            
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Redis connection failed: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check Redis health status.
        
        Returns:
            Health status dict with status and metrics
        """
        try:
            client = self.connect()
            
            # Ping test
            ping = client.ping()
            
            # Get info
            info = client.info()
            
            return {
                "status": "healthy",
                "ping": ping,
                "host": self.host,
                "port": self.port,
                "db": self.db,
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "total_keys": client.dbsize()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "host": self.host,
                "port": self.port
            }
    
    def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        Set a key-value pair.
        
        Args:
            key: Cache key
            value: Value (will be JSON serialized if not string)
            ex: Expiry in seconds
            px: Expiry in milliseconds
            nx: Only set if key doesn't exist
            xx: Only set if key exists
            
        Returns:
            True if successful
        """
        client = self.connect()
        
        # Serialize value if needed
        if not isinstance(value, (str, bytes)):
            value = json.dumps(value)
        
        return client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value by key.
        
        Args:
            key: Cache key
            
        Returns:
            Value (JSON deserialized if possible), or None if not found
        """
        client = self.connect()
        value = client.get(key)
        
        if value is None:
            return None
        
        # Try to deserialize JSON
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def delete(self, *keys: str) -> int:
        """
        Delete one or more keys.
        
        Args:
            keys: Keys to delete
            
        Returns:
            Number of keys deleted
        """
        client = self.connect()
        return client.delete(*keys)
    
    def exists(self, *keys: str) -> int:
        """
        Check if keys exist.
        
        Args:
            keys: Keys to check
            
        Returns:
            Number of keys that exist
        """
        client = self.connect()
        return client.exists(*keys)
    
    def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiry on a key.
        
        Args:
            key: Key to set expiry on
            seconds: Seconds until expiry
            
        Returns:
            True if successful
        """
        client = self.connect()
        return client.expire(key, seconds)
    
    def ttl(self, key: str) -> int:
        """
        Get time to live for a key.
        
        Args:
            key: Key to check
            
        Returns:
            TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        client = self.connect()
        return client.ttl(key)
    
    def keys(self, pattern: str = "*") -> List[str]:
        """
        Get keys matching pattern.
        
        Args:
            pattern: Pattern to match (e.g., "balance:*")
            
        Returns:
            List of matching keys
        """
        client = self.connect()
        return client.keys(pattern)
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Pattern to match (e.g., "balance:*")
            
        Returns:
            Number of keys deleted
        """
        keys = self.keys(pattern)
        if keys:
            return self.delete(*keys)
        return 0
    
    def mget(self, keys: List[str]) -> List[Optional[Any]]:
        """
        Get multiple values at once.
        
        Args:
            keys: List of keys
            
        Returns:
            List of values (None for missing keys)
        """
        client = self.connect()
        values = client.mget(keys)
        
        # Deserialize JSON values
        result = []
        for value in values:
            if value is None:
                result.append(None)
            else:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(value)
        
        return result
    
    def mset(self, mapping: Dict[str, Any]) -> bool:
        """
        Set multiple key-value pairs at once.
        
        Args:
            mapping: Dict of key-value pairs
            
        Returns:
            True if successful
        """
        client = self.connect()
        
        # Serialize values
        serialized = {}
        for key, value in mapping.items():
            if not isinstance(value, (str, bytes)):
                serialized[key] = json.dumps(value)
            else:
                serialized[key] = value
        
        return client.mset(serialized)
    
    def incr(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter.
        
        Args:
            key: Counter key
            amount: Amount to increment
            
        Returns:
            New value
        """
        client = self.connect()
        return client.incrby(key, amount)
    
    def decr(self, key: str, amount: int = 1) -> int:
        """
        Decrement a counter.
        
        Args:
            key: Counter key
            amount: Amount to decrement
            
        Returns:
            New value
        """
        client = self.connect()
        return client.decrby(key, amount)
    
    def hincrby(self, name: str, key: str, amount: int = 1) -> int:
        """
        Increment a hash field.
        
        Args:
            name: Hash name
            key: Field key
            amount: Amount to increment
            
        Returns:
            New value
        """
        client = self.connect()
        return client.hincrby(name, key, amount)
    
    def hset(self, name: str, mapping: Dict[str, Any]) -> int:
        """
        Set hash fields.
        
        Args:
            name: Hash name
            mapping: Field-value mapping
            
        Returns:
            Number of fields added
        """
        client = self.connect()
        
        # Serialize values
        serialized = {}
        for key, value in mapping.items():
            if not isinstance(value, (str, bytes)):
                serialized[key] = json.dumps(value)
            else:
                serialized[key] = value
        
        return client.hset(name, mapping=serialized)
    
    def hget(self, name: str, key: str) -> Optional[Any]:
        """
        Get hash field value.
        
        Args:
            name: Hash name
            key: Field key
            
        Returns:
            Field value or None
        """
        client = self.connect()
        value = client.hget(name, key)
        
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def hgetall(self, name: str) -> Dict[str, Any]:
        """
        Get all hash fields.
        
        Args:
            name: Hash name
            
        Returns:
            Dict of field-value pairs
        """
        client = self.connect()
        data = client.hgetall(name)
        
        # Deserialize values
        result = {}
        for key, value in data.items():
            try:
                result[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                result[key] = value
        
        return result
    
    def flushdb(self):
        """
        Clear current database.
        WARNING: Deletes all keys in current DB!
        """
        client = self.connect()
        client.flushdb()
        logger.warning(f"Flushed Redis database {self.db}")
    
    def close(self):
        """Close client connection."""
        if self._client:
            self._client.close()
            self._client = None
        if self._pool:
            self._pool.disconnect()
            self._pool = None
        logger.info("Redis client closed")
```

**Test File** (abbreviated):
```python
# mcp-scrt/tests/integration/test_redis_client.py

import pytest
from mcp_scrt.integrations.redis_client import RedisClient


@pytest.fixture
def redis_client():
    """Fixture for Redis client."""
    client = RedisClient(db=15)  # Use test DB
    yield client
    client.flushdb()  # Clean up after tests
    client.close()


def test_connection(redis_client):
    """Test basic connection."""
    client_instance = redis_client.connect()
    assert client_instance is not None


def test_health_check(redis_client):
    """Test health check."""
    health = redis_client.health_check()
    assert health["status"] == "healthy"
    assert health["ping"] is True


def test_set_get(redis_client):
    """Test set and get operations."""
    # String value
    redis_client.set("test:key1", "value1")
    assert redis_client.get("test:key1") == "value1"
    
    # JSON value
    redis_client.set("test:key2", {"foo": "bar"})
    assert redis_client.get("test:key2") == {"foo": "bar"}


def test_set_with_expiry(redis_client):
    """Test set with TTL."""
    redis_client.set("test:expire", "value", ex=10)
    ttl = redis_client.ttl("test:expire")
    assert 0 < ttl <= 10


def test_delete(redis_client):
    """Test delete operation."""
    redis_client.set("test:delete", "value")
    deleted = redis_client.delete("test:delete")
    assert deleted == 1
    assert redis_client.get("test:delete") is None


def test_pattern_operations(redis_client):
    """Test pattern-based operations."""
    # Set multiple keys with pattern
    redis_client.set("balance:addr1", "100")
    redis_client.set("balance:addr2", "200")
    redis_client.set("other:key", "300")
    
    # Get keys by pattern
    keys = redis_client.keys("balance:*")
    assert len(keys) == 2
    
    # Delete by pattern
    deleted = redis_client.delete_pattern("balance:*")
    assert deleted == 2


def test_counters(redis_client):
    """Test counter operations."""
    # Increment
    val = redis_client.incr("test:counter", 5)
    assert val == 5
    
    val = redis_client.incr("test:counter", 3)
    assert val == 8
    
    # Decrement
    val = redis_client.decr("test:counter", 2)
    assert val == 6


def test_hash_operations(redis_client):
    """Test hash operations."""
    # Set hash fields
    redis_client.hset("test:hash", {"field1": "value1", "field2": "value2"})
    
    # Get field
    assert redis_client.hget("test:hash", "field1") == "value1"
    
    # Get all fields
    data = redis_client.hgetall("test:hash")
    assert data == {"field1": "value1", "field2": "value2"}
    
    # Increment hash field
    redis_client.hincrby("test:hash", "counter", 5)
    assert redis_client.hget("test:hash", "counter") == 5
```

**Success Criteria**:
- ✅ Client connects to remote Redis
- ✅ Health check returns status
- ✅ Set/get operations work with TTL
- ✅ Pattern-based operations work
- ✅ Counter operations work
- ✅ Hash operations work
- ✅ All tests pass

---

### Task 1A.4: Ollama Client Wrapper

**Objective**: Create Ollama LLM client for text generation and embeddings.

**Files to Create**:
```
mcp-scrt/src/mcp_scrt/integrations/ollama_client.py
mcp-scrt/tests/integration/test_ollama_client.py
```

**Implementation Details**:

```python
# mcp-scrt/src/mcp_scrt/integrations/ollama_client.py

"""
Ollama client wrapper for LLM operations.

This module provides a clean interface to Ollama with:
- Text generation
- Streaming responses
- Embeddings generation
- Model management
- Health checks
"""

import os
import json
from typing import Dict, List, Optional, Generator, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Wrapper for Ollama LLM operations.
    
    Features:
    - Text generation (streaming and non-streaming)
    - Embeddings generation
    - Model management
    - Health checks
    - Retry logic
    """
    
    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        timeout: int = 120
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama API base URL (default: from env OLLAMA_URL)
            model: Default model name (default: from env OLLAMA_MODEL)
            timeout: Request timeout in seconds
        """
        self.base_url = (base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.3:70b")
        self.timeout = timeout
        
        # Create session with retry logic
        self._session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check Ollama health status.
        
        Returns:
            Health status dict with status and available models
        """
        try:
            # Try to list models
            models = self.list_models()
            
            return {
                "status": "healthy",
                "base_url": self.base_url,
                "default_model": self.model,
                "available_models": [m["name"] for m in models],
                "model_count": len(models)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "base_url": self.base_url
            }
    
    def list_models(self) -> List[Dict]:
        """
        List available models.
        
        Returns:
            List of model dicts with name, size, modified date
        """
        try:
            response = self._session.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("models", [])
            
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        template: Optional[str] = None,
        context: Optional[List[int]] = None,
        options: Optional[Dict] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate text completion.
        
        Args:
            prompt: Input prompt
            model: Model name (default: self.model)
            system: System prompt
            template: Prompt template
            context: Context from previous generation
            options: Model parameters (temperature, top_p, etc.)
            stream: Stream response
            
        Returns:
            Generation result dict or generator if streaming
        """
        model = model or self.model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        if system:
            payload["system"] = system
        if template:
            payload["template"] = template
        if context:
            payload["context"] = context
        if options:
            payload["options"] = options
        
        try:
            response = self._session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream(response)
            else:
                return response.json()
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        options: Optional[Dict] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Chat completion with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (default: self.model)
            options: Model parameters
            stream: Stream response
            
        Returns:
            Chat response dict or generator if streaming
        """
        model = model or self.model
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        if options:
            payload["options"] = options
        
        try:
            response = self._session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream(response)
            else:
                return response.json()
                
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            raise
    
    def embeddings(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            text: Input text
            model: Model name (default: self.model)
            
        Returns:
            Embedding vector as list of floats
        """
        model = model or self.model
        
        payload = {
            "model": model,
            "prompt": text
        }
        
        try:
            response = self._session.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("embedding", [])
            
        except Exception as e:
            logger.error(f"Ollama embeddings failed: {e}")
            raise
    
    def _handle_stream(self, response: requests.Response) -> Generator[Dict, None, None]:
        """
        Handle streaming response.
        
        Args:
            response: Streaming response object
            
        Yields:
            Response chunks as dicts
        """
        for line in response.iter_lines():
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to decode stream line: {line}")
                    continue
    
    def pull_model(self, model: str) -> Dict[str, Any]:
        """
        Pull/download a model.
        
        Args:
            model: Model name to pull
            
        Returns:
            Pull status dict
        """
        payload = {"name": model}
        
        try:
            response = self._session.post(
                f"{self.base_url}/api/pull",
                json=payload,
                timeout=600,  # 10 minutes for large models
                stream=True
            )
            response.raise_for_status()
            
            # Get final status
            status = {}
            for line in response.iter_lines():
                if line:
                    status = json.loads(line)
            
            return status
            
        except Exception as e:
            logger.error(f"Model pull failed: {e}")
            raise
    
    def close(self):
        """Close session."""
        if self._session:
            self._session.close()
            logger.info("Ollama client session closed")
```

**Test File** (abbreviated):
```python
# mcp-scrt/tests/integration/test_ollama_client.py

import pytest
from mcp_scrt.integrations.ollama_client import OllamaClient


@pytest.fixture
def ollama_client():
    """Fixture for Ollama client."""
    client = OllamaClient()
    yield client
    client.close()


def test_health_check(ollama_client):
    """Test health check."""
    health = ollama_client.health_check()
    assert health["status"] == "healthy"
    assert len(health["available_models"]) > 0


def test_list_models(ollama_client):
    """Test listing models."""
    models = ollama_client.list_models()
    assert len(models) > 0
    assert any("llama" in m["name"].lower() for m in models)


def test_generate(ollama_client):
    """Test text generation."""
    result = ollama_client.generate(
        prompt="What is 2+2?",
        options={"temperature": 0.1}
    )
    
    assert "response" in result
    assert len(result["response"]) > 0
    assert "4" in result["response"]


def test_chat(ollama_client):
    """Test chat completion."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Secret Network?"}
    ]
    
    result = ollama_client.chat(messages=messages)
    
    assert "message" in result
    assert result["message"]["role"] == "assistant"
    assert len(result["message"]["content"]) > 0


def test_embeddings(ollama_client):
    """Test embeddings generation."""
    embedding = ollama_client.embeddings("Secret Network is a blockchain")
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


def test_streaming_generate(ollama_client):
    """Test streaming generation."""
    stream = ollama_client.generate(
        prompt="Count to 3",
        stream=True
    )
    
    chunks = list(stream)
    assert len(chunks) > 0
    
    # Concatenate response
    full_response = "".join(chunk.get("response", "") for chunk in chunks)
    assert len(full_response) > 0
```

**Success Criteria**:
- ✅ Client connects to remote Ollama
- ✅ Health check returns status and models
- ✅ Text generation works
- ✅ Chat completion works
- ✅ Embeddings generation works
- ✅ Streaming works
- ✅ All tests pass

---

## Summary of Part 1A

At this point, you will have completed:

✅ **4 Database Client Wrappers**:
- ChromaDB client with collections and vector search
- Neo4j client with graph operations
- Redis client with caching operations
- Ollama client with LLM operations

✅ **Complete Test Coverage**:
- Unit tests for each client
- Integration tests with real services
- Health checks for all services

✅ **Foundation Ready**:
- All database clients functional
- Connection pooling implemented
- Error handling in place
- Ready for service layer

