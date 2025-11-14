# Service Test Scripts

Test scripts for Secret Agent infrastructure on `secretai-yyzz.scrtlabs.com:18343`

## Available Test Scripts

### 1. Bash Test Script (Automated)

**File**: [test_services.sh](test_services.sh)

Comprehensive bash script that tests all services automatically.

**Usage**:
```bash
./scripts/test_services.sh
```

**Features**:
- ✓ Tests all services (Ollama, ChromaDB, Neo4j, Redis)
- ✓ Tests authentication (API key validation)
- ✓ Tests SSL/TLS configuration
- ✓ Color-coded output
- ✓ Summary report

**Requirements**:
- curl
- openssl
- redis-cli (optional, for Redis tests)

---

### 2. Python Test Script (Automated)

**File**: [test_services.py](test_services.py)

Python-based test suite with detailed reporting.

**Usage**:
```bash
# Basic usage
python scripts/test_services.py

# With custom host
HOST=myhost.com python scripts/test_services.py

# Install dependencies
pip install requests redis
```

**Features**:
- ✓ Comprehensive test coverage
- ✓ Detailed error reporting
- ✓ Exit codes for CI/CD integration
- ✓ JSON-friendly output option

**Requirements**:
- Python 3.6+
- requests library
- redis library (optional)

---

### 3. cURL Command Reference

**File**: [curl_tests.md](curl_tests.md)

Quick reference guide with individual curl commands for manual testing.

**Usage**:
```bash
# Set environment variables
export HOST="secretai-yyzz.scrtlabs.com"
export API_KEY="sa-a3769c5072e3ae1c4d609601b11c0c75310bfa351efbe1593188a26b0071f012"

# Then copy-paste commands from curl_tests.md
```

**Included Tests**:
- Health checks
- Ollama (model listing, generation, chat)
- ChromaDB (CRUD operations, queries)
- Neo4j (Cypher queries, graph operations)
- Redis (direct connection tests)
- SSL/TLS verification
- Performance measurements

---

## Quick Start

### Option 1: Run Automated Tests (Bash)

```bash
cd /home/quaisx/workspace/secret-agent
./scripts/test_services.sh
```

### Option 2: Run Python Tests

```bash
cd /home/quaisx/workspace/secret-agent
python scripts/test_services.py
```

### Option 3: Manual Testing

See [curl_tests.md](curl_tests.md) for individual commands.

---

## Test Coverage

All scripts test the following:

### Services
- ✓ **Caddy** - Reverse proxy with HTTPS
- ✓ **Ollama** - LLM service (llama3.3:70b)
- ✓ **ChromaDB** - Vector database
- ✓ **Neo4j** - Graph database
- ✓ **Redis** - Cache and message broker

### Security
- ✓ API key authentication (X-API-Key header)
- ✓ Neo4j basic authentication
- ✓ Redis password authentication
- ✓ SSL/TLS encryption
- ✓ Certificate validation
- ✓ Unauthorized access rejection

### Functionality
- ✓ CRUD operations
- ✓ Query operations
- ✓ Data persistence
- ✓ Error handling
- ✓ Response validation

---

## Configuration

### Environment Variables

```bash
# Host configuration
export HOST="secretai-yyzz.scrtlabs.com"
export PORT="18343"

# API credentials
export API_KEY="sa-a3769c5072e3ae1c4d609601b11c0c75310bfa351efbe1593188a26b0071f012"
export NEO4J_PASSWORD="A9nspVlpN7apAjALDRJM7bmMYRMd9t6b"
export REDIS_PASSWORD="rVjZruAcJD6mfpTIZYTInUuRATpObfOb"
```

### Using .env File

```bash
# Create .env.test
cat > .env.test << 'EOF'
HOST=secretai-yyzz.scrtlabs.com
PORT=18343
API_KEY=sa-a3769c5072e3ae1c4d609601b11c0c75310bfa351efbe1593188a26b0071f012
NEO4J_PASSWORD=A9nspVlpN7apAjALDRJM7bmMYRMd9t6b
REDIS_PASSWORD=rVjZruAcJD6mfpTIZYTInUuRATpObfOb
EOF

# Source it
source .env.test
```

---

## Common Test Scenarios

### 1. Quick Health Check

```bash
curl -k https://secretai-yyzz.scrtlabs.com:18343/health
```

### 2. Test Ollama

```bash
curl -k -H "X-API-Key: $API_KEY" \
  https://secretai-yyzz.scrtlabs.com:18343/ollama/api/tags
```

### 3. Test ChromaDB

```bash
curl -k -H "X-API-Key: $API_KEY" \
  https://secretai-yyzz.scrtlabs.com:18343/chroma/api/v1/heartbeat
```

### 4. Test Neo4j

```bash
export NEO4J_AUTH=$(echo -n "neo4j:$NEO4J_PASSWORD" | base64)

curl -k -H "X-API-Key: $API_KEY" \
  -H "Authorization: Basic $NEO4J_AUTH" \
  https://secretai-yyzz.scrtlabs.com:18343/neo4j/
```

### 5. Test Redis

```bash
redis-cli -h secretai-yyzz.scrtlabs.com -p 6379 -a "$REDIS_PASSWORD" PING
```

---

## Troubleshooting

### Connection Refused

```bash
# Check if services are running
curl -k https://secretai-yyzz.scrtlabs.com:18343/health

# Check with verbose output
curl -v -k https://secretai-yyzz.scrtlabs.com:18343/health
```

### Authentication Errors

```bash
# Verify API key
echo $API_KEY

# Test without API key (should fail with 401)
curl -k -w "HTTP %{http_code}\n" \
  https://secretai-yyzz.scrtlabs.com:18343/ollama/api/tags
```

### SSL Errors

```bash
# Test SSL certificate
openssl s_client -connect secretai-yyzz.scrtlabs.com:18343 \
  -servername secretai-yyzz.scrtlabs.com

# Use -k flag to bypass SSL verification
curl -k https://...
```

### Service-Specific Issues

**Ollama not responding**:
```bash
# Check if model is loaded
curl -k -H "X-API-Key: $API_KEY" \
  https://secretai-yyzz.scrtlabs.com:18343/ollama/api/tags
```

**ChromaDB connection timeout**:
```bash
# Increase timeout
curl -k -H "X-API-Key: $API_KEY" \
  --max-time 60 \
  https://secretai-yyzz.scrtlabs.com:18343/chroma/api/v1/heartbeat
```

**Neo4j authentication failed**:
```bash
# Verify password
echo $NEO4J_PASSWORD

# Test basic auth
export NEO4J_AUTH=$(echo -n "neo4j:$NEO4J_PASSWORD" | base64)
echo $NEO4J_AUTH
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Service Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install requests redis

      - name: Run tests
        env:
          HOST: secretai-yyzz.scrtlabs.com
          API_KEY: ${{ secrets.API_KEY }}
          NEO4J_PASSWORD: ${{ secrets.NEO4J_PASSWORD }}
          REDIS_PASSWORD: ${{ secrets.REDIS_PASSWORD }}
        run: |
          python scripts/test_services.py
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any

    environment {
        HOST = 'secretai-yyzz.scrtlabs.com'
        API_KEY = credentials('api-key')
        NEO4J_PASSWORD = credentials('neo4j-password')
        REDIS_PASSWORD = credentials('redis-password')
    }

    stages {
        stage('Test Services') {
            steps {
                sh './scripts/test_services.sh'
            }
        }
    }
}
```

---

## Performance Testing

Add to test scripts for load testing:

```bash
# Test response time
for i in {1..10}; do
  curl -k -H "X-API-Key: $API_KEY" \
    -w "Time: %{time_total}s\n" \
    -o /dev/null -s \
    https://secretai-yyzz.scrtlabs.com:18343/health
done

# Concurrent requests
for i in {1..10}; do
  curl -k -H "X-API-Key: $API_KEY" \
    https://secretai-yyzz.scrtlabs.com:18343/chroma/api/v1/heartbeat &
done
wait
```

---

## Additional Resources

- [Security Setup Guide](../SECURITY_SETUP.md)
- [TLS Setup Guide](../docs/TLS_SETUP.md)
- [TLS Quick Start](../TLS_QUICKSTART.md)
- [Security Documentation](../docs/SECURITY.md)
