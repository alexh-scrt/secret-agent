# Security Setup - Quick Start Guide

This guide shows how to secure your Secret Agent infrastructure with Caddy reverse proxy.

## TL;DR

```bash
# 1. Ensure certificates are in place
ls /mnt/secure/cert/fullchain.pem /mnt/secure/cert/privkey.pem

# 2. Generate API key
openssl rand -hex 32

# 3. Add to .env
echo "API_KEY=<your-generated-key>" >> .env
echo "SSL_CERT_PATH=/mnt/secure/cert/fullchain.pem" >> .env

# 4. Start secure stack with HTTPS
docker-compose -f docker-compose-secure.yml up -d

# 5. Update your code to use secure clients
```

**Note**: The secure stack now uses **HTTPS** on port **${REMOTE_PORT}** with your TLS certificates.
For detailed TLS setup, see [TLS Setup Guide](docs/TLS_SETUP.md).

## What Changed?

### Before (Insecure - docker-compose2.yml)
```
Your App → Ollama:11434 (no auth)
Your App → ChromaDB:8000 (no auth)
Your App → Neo4j:7474 (basic auth only)
Your App → Redis:6379 (password only)
```

### After (Secure - docker-compose-secure.yml)
```
Your App → Caddy:${REMOTE_PORT}/ollama/* (HTTPS + API key) → Ollama (internal network)
Your App → Caddy:${REMOTE_PORT}/chroma/* (HTTPS + API key) → ChromaDB (token auth)
Your App → Caddy:${REMOTE_PORT}/neo4j/* (HTTPS + API key) → Neo4j (basic auth)
Your App → Redis:6379 (password - direct connection)
```

**Security Features**:
- ✅ TLS/SSL encryption (HTTPS)
- ✅ API key authentication
- ✅ Network isolation
- ✅ Service-level authentication

## Setup Steps

### 1. Environment Configuration

```bash
# Copy example
cp .env.example .env

# Generate strong API key
API_KEY=$(openssl rand -hex 32)

# Add to .env
cat >> .env << EOF
API_KEY=${API_KEY}
NEO4J_PASSWORD=$(openssl rand -base64 24)
REDIS_PASSWORD=$(openssl rand -base64 24)
EOF
```

### 2. Start Services

```bash
# Stop current services if running
docker-compose -f docker-compose2.yml down

# Start secure stack
docker-compose -f docker-compose-secure.yml up -d

# Check status
docker-compose -f docker-compose-secure.yml ps
```

### 3. Update Application Code

**Option A: Use Secure Client Manager (Recommended)**

```python
# src/your_app.py
from src.utils.secure_clients import SecureClientManager

# Initialize (automatically reads .env)
clients = SecureClientManager(use_caddy=True)

# Get clients
ollama_session = clients.get_ollama_session()
chroma = clients.get_chroma_client()
neo4j = clients.get_neo4j_driver()
redis = clients.get_redis_client()

# Use them
response = ollama_session.post(
    f"{clients.ollama_url}/api/generate",
    json={"model": "llama3.3:70b", "prompt": "Hello!"}
)
```

**Option B: Manual Configuration**

```python
import os
import requests
import chromadb
from neo4j import GraphDatabase
import redis as redis_lib

API_KEY = os.getenv("API_KEY")

# Ollama
session = requests.Session()
session.headers.update({"X-API-Key": API_KEY})
response = session.get("http://localhost:8080/ollama/api/tags")

# ChromaDB
chroma = chromadb.HttpClient(
    host="localhost",
    port=8080,
    headers={"X-API-Key": API_KEY}
)

# Neo4j (uses Bolt - no Caddy)
neo4j = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", os.getenv("NEO4J_PASSWORD"))
)

# Redis (direct - no Caddy)
redis = redis_lib.Redis(
    host="localhost",
    port=6379,
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)
```

### 4. Test Connections

```python
# Test script
from src.utils.secure_clients import get_client_manager

manager = get_client_manager()
results = manager.test_connections()

for service, status in results.items():
    print(f"{service}: {'✓' if status is True else '✗'} {status}")
```

Or via CLI:

```bash
# Test Ollama
curl -H "X-API-Key: $(grep API_KEY .env | cut -d= -f2)" \
  http://localhost:8080/ollama/api/tags

# Test ChromaDB
curl -H "X-API-Key: $(grep API_KEY .env | cut -d= -f2)" \
  http://localhost:8080/chroma/api/v1/heartbeat

# Test Neo4j
curl -H "X-API-Key: $(grep API_KEY .env | cut -d= -f2)" \
  -u neo4j:$(grep NEO4J_PASSWORD .env | cut -d= -f2) \
  http://localhost:8080/neo4j/db/data/

# Test Redis
redis-cli -a $(grep REDIS_PASSWORD .env | cut -d= -f2) ping
```

## Migration Checklist

- [ ] Backup data volumes
- [ ] Generate API key and passwords
- [ ] Update .env file
- [ ] Switch to docker-compose-secure.yml
- [ ] Update application code to use Caddy URLs
- [ ] Add X-API-Key headers to requests
- [ ] Test all service connections
- [ ] Update CI/CD pipelines
- [ ] Configure firewall (optional)
- [ ] Monitor logs for errors

## Firewall Configuration (Optional)

```bash
# Allow only Caddy
sudo ufw allow 8080/tcp

# Block direct access to services
sudo ufw deny 11434/tcp  # Ollama
sudo ufw deny 8000/tcp   # ChromaDB
sudo ufw deny 7474/tcp   # Neo4j HTTP

# Redis and Neo4j Bolt can stay open for localhost
# or be blocked if you only need HTTP access

sudo ufw enable
```

## Troubleshooting

### "Unauthorized" Errors

```bash
# Check API key is set
echo $API_KEY

# Check Caddy can see it
docker exec caddy-proxy env | grep API_KEY

# Verify key in request
curl -v -H "X-API-Key: wrong-key" http://localhost:8080/ollama/api/tags
# Should return 401
```

### Service Connection Issues

```bash
# Check services are running
docker-compose -f docker-compose-secure.yml ps

# Check Caddy can reach services
docker exec caddy-proxy wget -qO- http://ollama:11434/api/tags
docker exec caddy-proxy wget -qO- http://chromadb:8000/api/v1/heartbeat

# Check Caddy logs
docker logs caddy-proxy -f
```

### Client Library Issues

If your client library doesn't support custom headers:

1. **Wrap with requests**: Use requests/httpx to make HTTP calls with headers
2. **Update library**: Check for newer version with header support
3. **Proxy wrapper**: Create a thin wrapper that adds headers

Example wrapper:

```python
import requests


class AuthenticatedOllamaClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def generate(self, model, prompt):
        return self.session.post(
            f"{self.base_url}/api/generate",
            json={"model": model, "prompt": prompt}
        ).json()


# Use it
client = AuthenticatedOllamaClient(
    "http://localhost:8080/ollama",
    os.getenv("API_KEY")
)
```

## Switching Back to Development Mode

```bash
# Stop secure stack
docker-compose -f docker-compose-secure.yml down

# Start development stack
docker-compose -f docker-compose2.yml up -d

# Update .env URLs back to direct access
# OLLAMA_URL=http://localhost:11434
# CHROMA_URL=http://localhost:8000
```

## Additional Resources

- Full security guide: [docs/SECURITY.md](docs/SECURITY.md)
- Caddy configuration: [Caddyfile](Caddyfile)
- Secure client code: [src/utils/secure_clients.py](src/utils/secure_clients.py)
- Docker compose: [docker-compose-secure.yml](docker-compose-secure.yml)

## Best Practices

1. **Never commit .env** - Already in .gitignore
2. **Rotate keys regularly** - Generate new API key monthly
3. **Use different passwords** - Don't reuse passwords across services
4. **Enable HTTPS in production** - Update Caddyfile with domain
5. **Monitor access logs** - Check for suspicious activity
6. **Backup regularly** - Especially before making changes

## Support

For issues or questions:
1. Check [docs/SECURITY.md](docs/SECURITY.md) for detailed info
2. Review Caddy logs: `docker logs caddy-proxy`
3. Test individual services: Use curl commands above
4. Check network: `docker network inspect secret-agent_agent-network`
