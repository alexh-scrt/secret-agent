# TLS Quick Start

Quick reference for enabling HTTPS with your existing certificates.

## Files Modified

✅ **Caddyfile** - Now uses TLS with your certificates
✅ **docker-compose-secure.yml** - Mounts `/mnt/secure/cert` → `/app/cert`
✅ **src/utils/secure_clients.py** - Supports HTTPS and SSL verification
✅ **.env.example** - Updated with HTTPS URLs and SSL settings

## Certificate Locations

**Host**: `/mnt/secure/cert/`
- `fullchain.pem` - Certificate chain
- `privkey.pem` - Private key

**Container**: `/app/cert/`
- Automatically mapped by Docker volume

## Quick Setup

```bash
# 1. Verify certificates
ls -l /mnt/secure/cert/fullchain.pem /mnt/secure/cert/privkey.pem

# 2. Set permissions (if needed)
sudo chmod 644 /mnt/secure/cert/fullchain.pem
sudo chmod 600 /mnt/secure/cert/privkey.pem

# 3. Configure .env
cat >> .env << 'EOF'
# API Authentication
API_KEY=$(openssl rand -hex 32)

# TLS Configuration
SSL_CERT_PATH=/mnt/secure/cert/fullchain.pem
VERIFY_SSL=true

# Service URLs (HTTPS)
OLLAMA_URL=https://localhost:${REMOTE_PORT}/ollama
CHROMA_URL=https://localhost:${REMOTE_PORT}/chroma
NEO4J_URL=https://localhost:${REMOTE_PORT}/neo4j
EOF

# 4. Start services
docker-compose -f docker-compose-secure.yml up -d

# 5. Test HTTPS
curl -k -H "X-API-Key: your-api-key" https://localhost:${REMOTE_PORT}/health
```

## Python Client Usage

### Basic Usage

```python
from src.utils.secure_clients import SecureClientManager

# With SSL verification (recommended)
manager = SecureClientManager(
    use_caddy=True,
    verify_ssl=True,
    ssl_cert_path="/mnt/secure/cert/fullchain.pem"
)

# Get clients
ollama = manager.get_ollama_session()
chroma = manager.get_chroma_client()
neo4j = manager.get_neo4j_driver()
redis = manager.get_redis_client()
```

### Environment-Based (Recommended)

```python
# Just set in .env:
# SSL_CERT_PATH=/mnt/secure/cert/fullchain.pem
# VERIFY_SSL=true

from src.utils.secure_clients import get_client_manager

manager = get_client_manager()  # Uses .env settings
ollama = manager.get_ollama_session()
```

### Self-Signed Certificates

```python
# If using self-signed certs, disable verification
manager = SecureClientManager(
    use_caddy=True,
    verify_ssl=False  # Not recommended for production
)
```

## Testing

```bash
# Health check (no auth)
curl -k https://localhost:${REMOTE_PORT}/health

# Test Ollama
curl -k -H "X-API-Key: your-api-key" \
  https://localhost:${REMOTE_PORT}/ollama/api/tags

# Test with certificate verification
curl --cacert /mnt/secure/cert/fullchain.pem \
  -H "X-API-Key: your-api-key" \
  https://localhost:${REMOTE_PORT}/ollama/api/tags
```

## Common Issues

### 1. Certificate Errors

**Problem**: `SSL certificate verify failed`

**Solution**:
```python
# Option A: Use certificate
manager = SecureClientManager(
    verify_ssl=True,
    ssl_cert_path="/mnt/secure/cert/fullchain.pem"
)

# Option B: Disable verification (dev only)
manager = SecureClientManager(verify_ssl=False)
```

### 2. Permission Denied

**Problem**: Caddy can't read certificates

**Solution**:
```bash
# Fix permissions
sudo chmod 644 /mnt/secure/cert/fullchain.pem
sudo chmod 600 /mnt/secure/cert/privkey.pem

# Verify Docker can access
docker exec caddy-proxy ls -l /app/cert/
```

### 3. Connection Refused

**Problem**: Can't connect to port ${REMOTE_PORT}

**Solution**:
```bash
# Check Caddy is running
docker ps | grep caddy-proxy

# Check logs
docker logs caddy-proxy

# Verify port mapping
docker port caddy-proxy
```

## URLs Summary

| Service | HTTP (dev) | HTTPS (secure) |
|---------|------------|----------------|
| Ollama | http://localhost:11434 | https://localhost:${REMOTE_PORT}/ollama |
| ChromaDB | http://localhost:8000 | https://localhost:${REMOTE_PORT}/chroma |
| Neo4j | http://localhost:7474 | https://localhost:${REMOTE_PORT}/neo4j |
| Redis | localhost:6379 (direct) | localhost:6379 (direct) |

## Configuration Files

- **Caddyfile**: TLS config and routing
- **docker-compose-secure.yml**: Volume mounts for certs
- **.env**: API keys and SSL settings
- **src/utils/secure_clients.py**: Client library with SSL support

## Next Steps

For detailed information, see:
- [TLS Setup Guide](docs/TLS_SETUP.md) - Complete TLS documentation
- [Security Setup](SECURITY_SETUP.md) - Overall security guide
- [Security Documentation](docs/SECURITY.md) - Advanced security topics

## Support

Common certificate commands:
```bash
# Check certificate
openssl x509 -in /mnt/secure/cert/fullchain.pem -text -noout

# Verify expiration
openssl x509 -in /mnt/secure/cert/fullchain.pem -noout -enddate

# Test TLS connection
openssl s_client -connect localhost:${REMOTE_PORT} -showcerts

# Verify key matches cert
openssl x509 -noout -modulus -in /mnt/secure/cert/fullchain.pem | openssl md5
openssl rsa -noout -modulus -in /mnt/secure/cert/privkey.pem | openssl md5
```
