# TLS/SSL Setup Guide

This guide explains how to configure TLS/SSL encryption for the Secret Agent infrastructure using your existing certificates.

## Overview

The secure configuration uses:
- **Certificate Location**: `/mnt/secure/cert` (host) → `/app/cert` (container)
- **Required Files**:
  - `fullchain.pem` - Full certificate chain
  - `privkey.pem` - Private key
- **Port**: 18343 (HTTPS)
- **Protocol**: TLS 1.2+

## Prerequisites

Ensure your certificates are in place:

```bash
# Check certificate files exist
ls -l /mnt/secure/cert/
# Should show:
# - fullchain.pem
# - privkey.pem
```

### Certificate Requirements

1. **fullchain.pem** - Must contain:
   - Your server certificate
   - Intermediate certificates (if any)
   - Root CA certificate

2. **privkey.pem** - Must contain:
   - Unencrypted private key
   - PEM format

### Verify Certificates

```bash
# Check certificate validity
openssl x509 -in /mnt/secure/cert/fullchain.pem -text -noout

# Verify private key matches certificate
openssl x509 -noout -modulus -in /mnt/secure/cert/fullchain.pem | openssl md5
openssl rsa -noout -modulus -in /mnt/secure/cert/privkey.pem | openssl md5
# The hashes should match

# Check certificate expiration
openssl x509 -in /mnt/secure/cert/fullchain.pem -noout -enddate
```

## Setup Steps

### 1. Configure Environment

```bash
# Add to .env
cat >> .env << 'EOF'
# SSL Configuration
SSL_CERT_PATH=/mnt/secure/cert/fullchain.pem
VERIFY_SSL=true

# Update service URLs to use HTTPS
OLLAMA_URL=https://localhost:18343/ollama
CHROMA_URL=https://localhost:18343/chroma
NEO4J_URL=https://localhost:18343/neo4j
EOF
```

### 2. Start Services

```bash
# Start with TLS enabled
docker-compose -f docker-compose-secure.yml up -d

# Check Caddy logs for TLS initialization
docker logs caddy-proxy

# Should see: "using provided certificate"
```

### 3. Test HTTPS Connection

```bash
# Health check (no auth required)
curl -k https://localhost:18343/health

# Test Ollama with API key
curl -k -H "X-API-Key: your-api-key" \
  https://localhost:18343/ollama/api/tags

# Test with certificate verification
curl --cacert /mnt/secure/cert/fullchain.pem \
  -H "X-API-Key: your-api-key" \
  https://localhost:18343/ollama/api/tags
```

## Client Configuration

### Python Requests

```python
import os
import requests

# Option 1: Verify with certificate
session = requests.Session()
session.headers.update({"X-API-Key": os.getenv("API_KEY")})
session.verify = "/mnt/secure/cert/fullchain.pem"

response = session.get("https://localhost:18343/ollama/api/tags")

# Option 2: Disable verification (not recommended for production)
session.verify = False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

### Using SecureClientManager

```python
from src.utils.secure_clients import SecureClientManager

# With SSL verification (recommended)
manager = SecureClientManager(
    use_caddy=True,
    verify_ssl=True,
    ssl_cert_path="/mnt/secure/cert/fullchain.pem"
)

# Without SSL verification (development only)
manager = SecureClientManager(
    use_caddy=True,
    verify_ssl=False
)

# Use clients normally
ollama = manager.get_ollama_session()
response = ollama.get(f"{manager.ollama_url}/api/tags")
```

### Environment-Based Configuration

```python
# Set in .env
# SSL_CERT_PATH=/mnt/secure/cert/fullchain.pem
# VERIFY_SSL=true

from src.utils.secure_clients import get_client_manager

# Automatically uses environment settings
manager = get_client_manager()
```

## Certificate Types

### Self-Signed Certificates

If using self-signed certificates:

```bash
# Generate self-signed certificate (for testing)
openssl req -x509 -newkey rsa:4096 \
  -keyout /mnt/secure/cert/privkey.pem \
  -out /mnt/secure/cert/fullchain.pem \
  -days 365 -nodes \
  -subj "/CN=localhost"

# In .env, either:
# 1. Point to the certificate
SSL_CERT_PATH=/mnt/secure/cert/fullchain.pem

# 2. Or disable verification (not recommended)
VERIFY_SSL=false
```

### Let's Encrypt Certificates

If using Let's Encrypt:

```bash
# Certificates are typically in:
# /etc/letsencrypt/live/yourdomain.com/

# Create symlinks or copy to /mnt/secure/cert/
ln -s /etc/letsencrypt/live/yourdomain.com/fullchain.pem /mnt/secure/cert/
ln -s /etc/letsencrypt/live/yourdomain.com/privkey.pem /mnt/secure/cert/

# Update Caddyfile if using domain name
# Change :18343 to your domain
```

### Custom CA Certificates

If using internal CA:

```bash
# Ensure fullchain.pem includes:
# 1. Server certificate
# 2. Intermediate CA (if any)
# 3. Root CA

# Verify chain
openssl verify -CAfile /mnt/secure/cert/fullchain.pem \
  /mnt/secure/cert/fullchain.pem
```

## Security Best Practices

### 1. File Permissions

```bash
# Secure certificate files
sudo chown root:root /mnt/secure/cert/*.pem
sudo chmod 600 /mnt/secure/cert/privkey.pem
sudo chmod 644 /mnt/secure/cert/fullchain.pem

# Verify permissions
ls -l /mnt/secure/cert/
# privkey.pem should be -rw-------
# fullchain.pem should be -rw-r--r--
```

### 2. Certificate Rotation

```bash
# When updating certificates:
# 1. Copy new certificates to /mnt/secure/cert/
# 2. Reload Caddy (no restart needed)
docker exec caddy-proxy caddy reload --config /etc/caddy/Caddyfile

# Or restart the container
docker restart caddy-proxy
```

### 3. Monitor Expiration

```bash
# Check expiration date
openssl x509 -in /mnt/secure/cert/fullchain.pem -noout -enddate

# Set up monitoring
# Add to cron: check_cert_expiry.sh
#!/bin/bash
DAYS=$(openssl x509 -in /mnt/secure/cert/fullchain.pem -noout -enddate | \
  cut -d= -f2 | xargs -I {} date -d {} +%s | \
  awk -v now=$(date +%s) '{print int(($1-now)/86400)}')

if [ $DAYS -lt 30 ]; then
  echo "Certificate expires in $DAYS days!"
fi
```

## Troubleshooting

### Certificate Errors

**"certificate verify failed"**

```bash
# Check certificate chain
openssl s_client -connect localhost:18343 -showcerts

# Verify certificate is valid
openssl x509 -in /mnt/secure/cert/fullchain.pem -text -noout

# Check if fullchain includes all intermediates
openssl crl2pkcs7 -nocrl -certfile /mnt/secure/cert/fullchain.pem | \
  openssl pkcs7 -print_certs -noout
```

**"private key does not match certificate"**

```bash
# Compare modulus
openssl x509 -noout -modulus -in /mnt/secure/cert/fullchain.pem | openssl md5
openssl rsa -noout -modulus -in /mnt/secure/cert/privkey.pem | openssl md5
# If different, you have mismatched files
```

### Permission Errors

**"permission denied"**

```bash
# Check Docker can read files
docker exec caddy-proxy cat /app/cert/fullchain.pem
docker exec caddy-proxy cat /app/cert/privkey.pem

# If errors, check host permissions
ls -l /mnt/secure/cert/

# Fix permissions
sudo chmod 644 /mnt/secure/cert/fullchain.pem
sudo chmod 600 /mnt/secure/cert/privkey.pem
```

### Connection Issues

**"connection refused"**

```bash
# Check Caddy is running
docker ps | grep caddy-proxy

# Check port is exposed
docker port caddy-proxy

# Check Caddy logs
docker logs caddy-proxy

# Test locally
docker exec caddy-proxy wget -O- https://localhost:18343/health
```

### SSL Verification in Python

**If getting SSL errors in Python:**

```python
# Option 1: Use certificate bundle
import requests
session = requests.Session()
session.verify = "/mnt/secure/cert/fullchain.pem"

# Option 2: Disable verification (development only)
session.verify = False

# Option 3: Use system CA bundle
session.verify = True  # Uses system certificates
```

## Advanced Configuration

### Custom TLS Settings

Edit [Caddyfile](../Caddyfile):

```caddyfile
:18343 {
    tls /app/cert/fullchain.pem /app/cert/privkey.pem {
        protocols tls1.2 tls1.3
        ciphers TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 \
                TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        curves x25519 secp384r1 secp256r1
    }
}
```

### Client Certificate Authentication (mTLS)

For even higher security:

```caddyfile
:18343 {
    tls /app/cert/fullchain.pem /app/cert/privkey.pem {
        client_auth {
            mode require_and_verify
            trusted_ca_cert_file /app/cert/client_ca.pem
        }
    }
}
```

### Multiple Domains

```caddyfile
localhost:18343, yourdomain.com:18343 {
    tls /app/cert/fullchain.pem /app/cert/privkey.pem
    # ... rest of configuration
}
```

## Testing Checklist

- [ ] Certificates exist at `/mnt/secure/cert/`
- [ ] Permissions are correct (600 for privkey, 644 for fullchain)
- [ ] Certificate and key match (modulus check)
- [ ] Certificate is not expired
- [ ] Certificate chain is complete
- [ ] Caddy starts without errors
- [ ] Health check accessible via HTTPS
- [ ] API endpoints respond with valid auth
- [ ] Python clients can connect
- [ ] SSL verification works (if using proper CA)

## Migration from HTTP

If migrating from HTTP configuration:

1. **Update URLs in .env**
   ```bash
   # Change from:
   OLLAMA_URL=http://localhost:8080/ollama
   # To:
   OLLAMA_URL=https://localhost:18343/ollama
   ```

2. **Update application code**
   - Add SSL verification settings
   - Handle certificate errors gracefully

3. **Update firewall**
   ```bash
   sudo ufw allow 18343/tcp
   sudo ufw delete allow 8080/tcp
   ```

4. **Test thoroughly**
   - All endpoints
   - All client libraries
   - SSL verification

## References

- [Caddy TLS Documentation](https://caddyserver.com/docs/caddyfile/directives/tls)
- [OpenSSL Commands](https://www.openssl.org/docs/man1.1.1/man1/)
- [Python Requests SSL](https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification)
- [Let's Encrypt](https://letsencrypt.org/)
