"""Secure client connections with authentication.

This module provides authenticated clients for all infrastructure services
when using the Caddy reverse proxy configuration.
"""

import os
import base64
from typing import Optional
import requests


class SecureClientManager:
    """Manages authenticated connections to infrastructure services."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        redis_password: Optional[str] = None,
        use_caddy: bool = True,
        verify_ssl: bool = True,
        ssl_cert_path: Optional[str] = None,
    ):
        """
        Initialize secure client manager.

        Args:
            api_key: API key for Caddy authentication (reads from env if not provided)
            neo4j_password: Neo4j password (reads from env if not provided)
            redis_password: Redis password (reads from env if not provided)
            use_caddy: Whether to use Caddy reverse proxy URLs (default: True)
            verify_ssl: Whether to verify SSL certificates (default: True)
            ssl_cert_path: Path to SSL certificate for verification (optional)
        """
        self.api_key = api_key or os.getenv("API_KEY")
        self.neo4j_password = neo4j_password or os.getenv("NEO4J_PASSWORD")
        self.redis_password = redis_password or os.getenv("REDIS_PASSWORD")
        self.use_caddy = use_caddy
        self.verify_ssl = verify_ssl
        self.ssl_cert_path = ssl_cert_path or os.getenv("SSL_CERT_PATH")

        # Configure URLs based on deployment mode
        if use_caddy:
            # Through Caddy reverse proxy (secure with HTTPS)
            self.ollama_url = os.getenv("OLLAMA_URL", "https://localhost:18343/ollama")
            self.chroma_url = os.getenv("CHROMA_URL", "https://localhost:18343/chroma")
            self.neo4j_http_url = os.getenv("NEO4J_URL", "https://localhost:18343/neo4j")
            self.neo4j_bolt_url = "bolt://localhost:7687"  # Bolt bypasses Caddy
        else:
            # Direct access (development)
            self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            self.chroma_url = os.getenv("CHROMA_URL", "http://localhost:8000")
            self.neo4j_http_url = "http://localhost:7474"
            self.neo4j_bolt_url = "bolt://localhost:7687"

        # Create authenticated HTTP session
        self.session = requests.Session()
        if use_caddy and self.api_key:
            self.session.headers.update({"X-API-Key": self.api_key})

        # Configure SSL verification
        if self.ssl_cert_path:
            self.session.verify = self.ssl_cert_path
        elif not self.verify_ssl:
            self.session.verify = False
            # Suppress SSL warnings if verification is disabled
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get_ollama_session(self) -> requests.Session:
        """
        Get authenticated requests session for Ollama.

        Returns:
            Authenticated requests.Session

        Example:
            >>> manager = SecureClientManager()
            >>> session = manager.get_ollama_session()
            >>> response = session.post(
            ...     f"{manager.ollama_url}/api/generate",
            ...     json={"model": "llama3.3:70b", "prompt": "Hello!"}
            ... )
        """
        return self.session

    def get_chroma_client(self):
        """
        Get authenticated ChromaDB client.

        Returns:
            ChromaDB HttpClient

        Example:
            >>> manager = SecureClientManager()
            >>> client = manager.get_chroma_client()
            >>> collection = client.get_or_create_collection("my_collection")
        """
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError(
                "chromadb not installed. Install with: pip install chromadb"
            )

        # Parse URL
        from urllib.parse import urlparse

        parsed = urlparse(self.chroma_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 8000

        headers = {}
        settings_kwargs = {}

        if self.use_caddy and self.api_key:
            # Add Caddy authentication
            headers["X-API-Key"] = self.api_key

            # ChromaDB native token auth (if enabled in docker-compose)
            settings_kwargs.update(
                {
                    "chroma_server_auth_credentials": self.api_key,
                    "chroma_server_auth_provider": "chromadb.auth.token.TokenAuthClientProvider",
                }
            )

        return chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(**settings_kwargs) if settings_kwargs else None,
            headers=headers,
        )

    def get_neo4j_driver(self):
        """
        Get authenticated Neo4j driver.

        Returns:
            Neo4j GraphDatabase driver

        Example:
            >>> manager = SecureClientManager()
            >>> driver = manager.get_neo4j_driver()
            >>> with driver.session() as session:
            ...     result = session.run("RETURN 1 AS num")
            ...     print(result.single()["num"])
        """
        try:
            from neo4j import GraphDatabase
        except ImportError:
            raise ImportError("neo4j not installed. Install with: pip install neo4j")

        # Neo4j Bolt protocol bypasses Caddy - uses native auth
        return GraphDatabase.driver(
            self.neo4j_bolt_url, auth=("neo4j", self.neo4j_password)
        )

    def get_neo4j_http_session(self) -> requests.Session:
        """
        Get authenticated requests session for Neo4j HTTP API.

        Note: Prefer get_neo4j_driver() for most use cases.
        This is for HTTP REST API access.

        Returns:
            Authenticated requests.Session
        """
        session = requests.Session()

        if self.use_caddy and self.api_key:
            session.headers.update({"X-API-Key": self.api_key})

        # Add Neo4j basic auth
        if self.neo4j_password:
            credentials = base64.b64encode(
                f"neo4j:{self.neo4j_password}".encode()
            ).decode()
            session.headers.update({"Authorization": f"Basic {credentials}"})

        return session

    def get_redis_client(self):
        """
        Get authenticated Redis client.

        Note: Redis uses direct connection (not through Caddy).

        Returns:
            Redis client

        Example:
            >>> manager = SecureClientManager()
            >>> redis_client = manager.get_redis_client()
            >>> redis_client.set("key", "value")
            >>> print(redis_client.get("key"))
        """
        try:
            import redis
        except ImportError:
            raise ImportError("redis not installed. Install with: pip install redis")

        # Redis always uses direct connection with password
        return redis.Redis(
            host="localhost",
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=self.redis_password,
            decode_responses=True,
        )

    def test_connections(self) -> dict:
        """
        Test all service connections.

        Returns:
            Dictionary with connection status for each service
        """
        results = {}

        # Test Ollama
        try:
            session = self.get_ollama_session()
            response = session.get(f"{self.ollama_url}/api/tags", timeout=5)
            results["ollama"] = response.status_code == 200
        except Exception as e:
            results["ollama"] = f"Error: {str(e)}"

        # Test ChromaDB
        try:
            chroma = self.get_chroma_client()
            chroma.heartbeat()
            results["chromadb"] = True
        except Exception as e:
            results["chromadb"] = f"Error: {str(e)}"

        # Test Neo4j
        try:
            driver = self.get_neo4j_driver()
            with driver.session() as session:
                result = session.run("RETURN 1")
                results["neo4j"] = result.single() is not None
            driver.close()
        except Exception as e:
            results["neo4j"] = f"Error: {str(e)}"

        # Test Redis
        try:
            redis_client = self.get_redis_client()
            results["redis"] = redis_client.ping()
        except Exception as e:
            results["redis"] = f"Error: {str(e)}"

        return results


# Global instance for easy access
_client_manager: Optional[SecureClientManager] = None


def get_client_manager(force_reload: bool = False) -> SecureClientManager:
    """
    Get global SecureClientManager instance.

    Args:
        force_reload: Force creation of new instance

    Returns:
        SecureClientManager instance
    """
    global _client_manager
    if _client_manager is None or force_reload:
        _client_manager = SecureClientManager()
    return _client_manager


# Convenience functions
def get_ollama_session() -> requests.Session:
    """Get Ollama session (convenience function)."""
    return get_client_manager().get_ollama_session()


def get_chroma_client():
    """Get ChromaDB client (convenience function)."""
    return get_client_manager().get_chroma_client()


def get_neo4j_driver():
    """Get Neo4j driver (convenience function)."""
    return get_client_manager().get_neo4j_driver()


def get_redis_client():
    """Get Redis client (convenience function)."""
    return get_client_manager().get_redis_client()
