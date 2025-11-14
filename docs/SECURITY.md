# Security Guide

This guide explains how to secure your Secret Agent infrastructure using the Caddy reverse proxy.

## Overview

The secure configuration provides:

- **Network Isolation**: Services not directly exposed to the host
- **Centralized Authentication**: Single API key for all HTTP services
- **Service-Level Authentication**: Native auth for Redis and Neo4j
- **Single Entry Point**: All traffic through Caddy on port 8080

## Quick Start

### 1. Generate API Key

```bash
# Generate a strong random API key
openssl rand -hex 32
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Edit `.env` and set:
```env
API_KEY=<your-generated-api-key>
NEO4J_PASSWORD=<your-neo4j-password>
REDIS_PASSWORD=<your-redis-password>
```

### 3. Start Secure Stack

```bash
docker-compose -f docker-compose-secure.yml up -d
```

### 4. Verify

```bash
# Health check (no auth)
curl http://localhost:8080/health

# Test Ollama (with auth)
curl -H "X-API-Key: your-api-key" http://localhost:8080/ollama/api/tags
```

## Client Configuration

### Python Clients

#### Ollama

```python
import os
import requests

API_KEY = os.getenv("API_KEY")
OLLAMA_URL = "http://localhost:8080/ollama"

# Custom session with API key header
session = requests.Session()
session.headers.update({"X-API-Key": API_KEY})

# Use ollama library with custom base URL
from ollama import Client

client = Client(
    host=OLLAMA_URL,
    # Add custom headers via monkey patching or wrapper
)

# Alternative: Use requests directly
response = session.post(
    f"{OLLAMA_URL}/api/generate",
    json={
        "model": "llama3.3:70b",
        "prompt": "Hello, world!"
    }
)
```

#### ChromaDB

```python
import os
import chromadb
from chromadb.config import Settings

API_KEY = os.getenv("API_KEY")
CHROMA_URL = "http://localhost:8080/chroma"

# ChromaDB with token authentication
client = chromadb.HttpClient(
    host="localhost",
    port=8080,
    settings=Settings(
        chroma_api_impl="chromadb.api.fastapi.FastAPI",
        chroma_server_host="localhost",
        chroma_server_http_port=8080,
        chroma_server_auth_credentials=API_KEY,
        chroma_server_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
    ),
    headers={"X-API-Key": API_KEY}  # Caddy layer
)

# Alternative: Using requests wrapper
from chromadb.api import API

class AuthenticatedChromaAPI(API):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._headers = {"X-API-Key": API_KEY}
```

#### Neo4j

```python
import os
from neo4j import GraphDatabase

NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
API_KEY = os.getenv("API_KEY")

# Neo4j driver with basic auth (native)
driver = GraphDatabase.driver(
    "bolt://localhost:7687",  # Use Bolt protocol directly (bypasses Caddy)
    auth=("neo4j", NEO4J_PASSWORD)
)

# Or via HTTP through Caddy (for REST API):
import requests

session = requests.Session()
session.headers.update({
    "X-API-Key": API_KEY,
    "Authorization": "Basic " + base64.b64encode(
        f"neo4j:{NEO4J_PASSWORD}".encode()
    ).decode()
})

response = session.get("http://localhost:8080/neo4j/db/data/")
```

#### Redis

```python
import os
import redis

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Redis uses native password authentication
# Connect directly (not through Caddy - Redis is not HTTP)
client = redis.Redis(
    host="localhost",
    port=6379,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# Test connection
client.ping()
```

## Security Wrapper

For easier client management, use this wrapper:

```python
# src/utils/secure_clients.py

import os
import requests
from typing import Optional


class SecureClientManager:
    """Manages authenticated connections to services."""

    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.redis_password = os.getenv("REDIS_PASSWORD")

        # Base URLs through Caddy
        self.ollama_url = "http://localhost:8080/ollama"
        self.chroma_url = "http://localhost:8080/chroma"
        self.neo4j_url = "http://localhost:8080/neo4j"

        # Session with API key
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": self.api_key})

    def get_ollama_client(self):
        """Get authenticated Ollama client."""
        # Return configured client
        pass

    def get_chroma_client(self):
        """Get authenticated ChromaDB client."""
        import chromadb

        return chromadb.HttpClient(
            host="localhost",
            port=8080,
            headers={"X-API-Key": self.api_key}
        )

    def get_neo4j_driver(self):
        """Get authenticated Neo4j driver."""
        from neo4j import GraphDatabase

        return GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", self.neo4j_password)
        )

    def get_redis_client(self):
        """Get authenticated Redis client."""
        import redis

        return redis.Redis(
            host="localhost",
            port=6379,
            password=self.redis_password,
            decode_responses=True
        )


# Usage
clients = SecureClientManager()
chroma = clients.get_chroma_client()
neo4j = clients.get_neo4j_driver()
redis = clients.get_redis_client()
```

## Network Configurations

### Option 1: Secure (Recommended for Production)

**File**: `docker-compose-secure.yml`

- All services behind Caddy
- No direct port exposure
- API key authentication
- Network isolation

```bash
docker-compose -f docker-compose-secure.yml up -d
```

### Option 2: Development (Current)

**File**: `docker-compose2.yml`

- Direct port exposure
- No reverse proxy
- Faster for development
- Less secure

```bash
docker-compose -f docker-compose2.yml up -d
```

## Firewall Configuration

### UFW (Ubuntu/Debian)

```bash
# Allow only Caddy port
sudo ufw allow 8080/tcp

# Block direct service access (if using secure config)
sudo ufw deny 11434/tcp  # Ollama
sudo ufw deny 8000/tcp   # ChromaDB
sudo ufw deny 7474/tcp   # Neo4j HTTP
sudo ufw deny 7687/tcp   # Neo4j Bolt
sudo ufw deny 6379/tcp   # Redis

# Enable firewall
sudo ufw enable
```

## Best Practices

1. **Rotate API Keys Regularly**
   ```bash
   # Generate new key
   NEW_KEY=$(openssl rand -hex 32)
   echo "API_KEY=$NEW_KEY" >> .env
   ```

2. **Use Strong Passwords**
   - Generate with: `openssl rand -base64 32`
   - Different password for each service

3. **Enable HTTPS in Production**
   - Update Caddyfile with domain name
   - Caddy auto-provisions Let's Encrypt certificates

4. **Monitor Access Logs**
   ```bash
   docker logs caddy-proxy -f
   ```

5. **Network Isolation**
   - Set `internal: true` in docker-compose for complete isolation
   - Use VPN for remote access

## Troubleshooting

### Authentication Failures

```bash
# Check API key in environment
docker exec caddy-proxy env | grep API_KEY

# Test with correct header
curl -H "X-API-Key: $(grep API_KEY .env | cut -d= -f2)" \
  http://localhost:8080/ollama/api/tags
```

### Service Connectivity

```bash
# Check if services are reachable from Caddy
docker exec caddy-proxy wget -qO- http://ollama:11434/api/tags
docker exec caddy-proxy wget -qO- http://chromadb:8000/api/v1/heartbeat
```

### Client Library Issues

If clients don't support custom headers:

1. Use requests/httpx wrapper
2. Modify service URLs in client
3. Add authentication in middleware layer

## Migration from Unsecured to Secured

1. **Backup data volumes**
   ```bash
   docker-compose -f docker-compose2.yml down
   docker volume ls | grep secret-agent
   ```

2. **Switch compose files**
   ```bash
   docker-compose -f docker-compose-secure.yml up -d
   ```

3. **Update application code**
   - Change service URLs to Caddy endpoints
   - Add API key headers
   - Test all integrations

4. **Remove old ports from firewall**
   ```bash
   sudo ufw delete allow 11434/tcp
   sudo ufw delete allow 8000/tcp
   # etc.
   ```

## Additional Security Layers

### 1. Rate Limiting (Caddy)

Add to Caddyfile:
```
rate_limit {
    zone static {
        key {remote_host}
        events 100
        window 1m
    }
}
```

### 2. IP Whitelisting

```
@allowed {
    remote_ip 192.168.1.0/24 10.0.0.0/8
}

handle @allowed {
    reverse_proxy ollama:11434
}
```

### 3. mTLS (Mutual TLS)

For production environments, consider client certificates.

## Reference

- [Caddy Documentation](https://caddyserver.com/docs/)
- [ChromaDB Authentication](https://docs.trychroma.com/deployment/auth)
- [Neo4j Security](https://neo4j.com/docs/operations-manual/current/security/)
- [Redis Security](https://redis.io/docs/management/security/)
