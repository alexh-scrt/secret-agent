#!/usr/bin/env python3
"""
Test script for Secret Agent services on secretai-yyzz.scrtlabs.com

Usage:
    python scripts/test_services.py

    # Or with custom host
    HOST=myhost.com python scripts/test_services.py
"""

import os
import sys
import json
import base64
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ServiceTester:
    """Test suite for Secret Agent services."""

    def __init__(self):
        """Initialize tester with credentials."""
        self.host = os.getenv("HOST", "secretai-yyzz.scrtlabs.com")
        self.port = os.getenv("PORT", "18343")
        self.base_url = f"https://{self.host}:{self.port}"

        # Credentials
        self.api_key = os.getenv(
            "API_KEY",
            "sa-a3769c5072e3ae1c4d609601b11c0c75310bfa351efbe1593188a26b0071f012"
        )
        self.neo4j_password = os.getenv(
            "NEO4J_PASSWORD",
            "A9nspVlpN7apAjALDRJM7bmMYRMd9t6b"
        )
        self.redis_password = os.getenv(
            "REDIS_PASSWORD",
            "rVjZruAcJD6mfpTIZYTInUuRATpObfOb"
        )

        # Create session with API key
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": self.api_key})
        self.session.verify = False  # Disable SSL verification for self-signed certs

        # Results tracking
        self.results = {"passed": 0, "failed": 0, "tests": []}

    def print_header(self, text: str):
        """Print section header."""
        print(f"\n{'=' * 60}")
        print(f"{text}")
        print('=' * 60)

    def test(
        self,
        name: str,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200
    ) -> bool:
        """
        Run a test.

        Args:
            name: Test name
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            headers: Additional headers
            expected_status: Expected HTTP status code

        Returns:
            True if test passed
        """
        url = f"{self.base_url}{endpoint}"
        print(f"\n  Testing: {name}")
        print(f"  URL: {url}")

        try:
            # Merge headers
            req_headers = self.session.headers.copy()
            if headers:
                req_headers.update(headers)

            # Make request
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            # Check status
            if response.status_code == expected_status:
                print(f"  ✓ PASS (HTTP {response.status_code})")
                if response.text and len(response.text) < 200:
                    print(f"  Response: {response.text[:100]}")
                self.results["passed"] += 1
                self.results["tests"].append({"name": name, "status": "PASS"})
                return True
            else:
                print(f"  ✗ FAIL (Expected {expected_status}, got {response.status_code})")
                print(f"  Response: {response.text[:200]}")
                self.results["failed"] += 1
                self.results["tests"].append({
                    "name": name,
                    "status": "FAIL",
                    "error": f"Status {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"  ✗ ERROR: {str(e)}")
            self.results["failed"] += 1
            self.results["tests"].append({
                "name": name,
                "status": "ERROR",
                "error": str(e)
            })
            return False

    def test_health(self):
        """Test health endpoint."""
        self.print_header("Health Check")
        # Health endpoint doesn't require API key
        session = requests.Session()
        session.verify = False
        response = session.get(f"{self.base_url}/health")
        if response.status_code == 200:
            print("  ✓ Health check OK")
            self.results["passed"] += 1
            return True
        else:
            print(f"  ✗ Health check failed: {response.status_code}")
            self.results["failed"] += 1
            return False

    def test_ollama(self):
        """Test Ollama service."""
        self.print_header("Testing Ollama")

        # List models
        self.test("List models", "GET", "/ollama/api/tags")

        # Show model info
        self.test(
            "Show model info",
            "POST",
            "/ollama/api/show",
            data={"name": "llama3.3:70b"}
        )

        # Generate text (non-streaming)
        self.test(
            "Generate text",
            "POST",
            "/ollama/api/generate",
            data={
                "model": "llama3.3:70b",
                "prompt": "Say hello",
                "stream": False
            }
        )

    def test_chromadb(self):
        """Test ChromaDB service (API v2)."""
        self.print_header("Testing ChromaDB (API v2)")

        # Heartbeat
        self.test("Heartbeat", "GET", "/chroma/api/v2/heartbeat")

        # Version
        self.test("Version", "GET", "/chroma/api/v2/version")

        # List collections
        self.test("List collections", "GET", "/chroma/api/v2/collections")

        # Create test collection
        import time
        collection_name = f"test_collection_{int(time.time())}"

        self.test(
            "Create collection",
            "POST",
            "/chroma/api/v2/collections",
            data={"name": collection_name, "metadata": {}}
        )

        # Add documents
        self.test(
            "Add documents",
            "POST",
            f"/chroma/api/v2/collections/{collection_name}/add",
            data={
                "ids": ["doc1", "doc2"],
                "documents": ["First test document", "Second test document"],
                "metadatas": [{"source": "test"}, {"source": "test"}]
            }
        )

        # Query collection
        self.test(
            "Query collection",
            "POST",
            f"/chroma/api/v2/collections/{collection_name}/query",
            data={
                "query_texts": ["test"],
                "n_results": 2
            }
        )

        # Count documents
        self.test(
            "Count documents",
            "GET",
            f"/chroma/api/v2/collections/{collection_name}/count"
        )

        # Delete collection
        self.test(
            "Delete collection",
            "DELETE",
            f"/chroma/api/v2/collections/{collection_name}"
        )

    def test_neo4j(self):
        """Test Neo4j service."""
        self.print_header("Testing Neo4j")

        # Create basic auth header
        auth_string = f"neo4j:{self.neo4j_password}"
        auth_bytes = auth_string.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_string = base64_bytes.decode('ascii')

        headers = {"Authorization": f"Basic {base64_string}"}

        # Service root
        self.test("Service root", "GET", "/neo4j/", headers=headers)

        # Database info
        self.test("Database info", "GET", "/neo4j/db/data/", headers=headers)

        # Execute simple query
        self.test(
            "Execute Cypher query",
            "POST",
            "/neo4j/db/data/transaction/commit",
            data={
                "statements": [
                    {"statement": "RETURN 1 AS number"}
                ]
            },
            headers=headers
        )

    def test_redis(self):
        """Test Redis service."""
        self.print_header("Testing Redis (Direct Connection)")

        try:
            import redis

            client = redis.Redis(
                host=self.host,
                port=6379,
                password=self.redis_password,
                decode_responses=True
            )

            # PING
            if client.ping():
                print("  ✓ Redis PING")
                self.results["passed"] += 1
            else:
                print("  ✗ Redis PING failed")
                self.results["failed"] += 1

            # SET/GET
            client.set("test_key", "test_value")
            value = client.get("test_key")
            if value == "test_value":
                print("  ✓ Redis SET/GET")
                self.results["passed"] += 1
                client.delete("test_key")
            else:
                print("  ✗ Redis SET/GET failed")
                self.results["failed"] += 1

            # INFO
            info = client.info("server")
            if "redis_version" in info:
                print(f"  ✓ Redis INFO (version: {info['redis_version']})")
                self.results["passed"] += 1
            else:
                print("  ✗ Redis INFO failed")
                self.results["failed"] += 1

        except ImportError:
            print("  ! redis-py not installed")
            print("  Install with: pip install redis")
        except Exception as e:
            print(f"  ✗ Redis test error: {e}")
            self.results["failed"] += 1

    def test_authentication(self):
        """Test authentication mechanisms."""
        self.print_header("Testing Authentication")

        # Test without API key
        print("\n  Testing without API key (should fail)")
        session = requests.Session()
        session.verify = False
        response = session.get(f"{self.base_url}/ollama/api/tags")
        if response.status_code == 401:
            print(f"  ✓ Correctly rejected (HTTP {response.status_code})")
            self.results["passed"] += 1
        else:
            print(f"  ✗ Expected 401, got {response.status_code}")
            self.results["failed"] += 1

        # Test with wrong API key
        print("\n  Testing with wrong API key (should fail)")
        session = requests.Session()
        session.verify = False
        session.headers.update({"X-API-Key": "wrong-key"})
        response = session.get(f"{self.base_url}/ollama/api/tags")
        if response.status_code == 401:
            print(f"  ✓ Correctly rejected (HTTP {response.status_code})")
            self.results["passed"] += 1
        else:
            print(f"  ✗ Expected 401, got {response.status_code}")
            self.results["failed"] += 1

    def print_summary(self):
        """Print test summary."""
        self.print_header("Test Summary")

        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.results['passed']} ({pass_rate:.1f}%)")
        print(f"Failed: {self.results['failed']}")

        if self.results["failed"] > 0:
            print("\nFailed tests:")
            for test in self.results["tests"]:
                if test["status"] != "PASS":
                    print(f"  - {test['name']}: {test.get('error', 'Unknown error')}")

        print(f"\nHost: {self.base_url}")
        print("Protocol: HTTPS with TLS")
        print("Authentication: API Key + service-level auth")

    def run_all_tests(self):
        """Run all tests."""
        print(f"Starting tests for {self.base_url}")

        self.test_health()
        self.test_ollama()
        self.test_chromadb()
        self.test_neo4j()
        self.test_redis()
        self.test_authentication()

        self.print_summary()

        # Return exit code
        return 0 if self.results["failed"] == 0 else 1


def main():
    """Main entry point."""
    tester = ServiceTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
