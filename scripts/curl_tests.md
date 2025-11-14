# cURL Test Commands

Quick reference for testing services on `secretai-yyzz.scrtlabs.com:18343`

## Credentials

```bash
export HOST="secretai-yyzz.scrtlabs.com"
export PORT="18343"
export API_KEY="sa-a3769c5072e3ae1c4d609601b11c0c75310bfa351efbe1593188a26b0071f012"
export NEO4J_PASSWORD="A9nspVlpN7apAjALDRJM7bmMYRMd9t6b"
export REDIS_PASSWORD="rVjZruAcJD6mfpTIZYTInUuRATpObfOb"
export BASE_URL="https://${HOST}:${PORT}"
```

## Health Check (No Auth)

```bash
# Basic health check
curl -k "$BASE_URL/health"

# Should return: OK
```

## Ollama Tests

```bash
# List available models
curl -k -H "X-API-Key: $API_KEY" \
  "$BASE_URL/ollama/api/tags"

# Get model information
curl -k -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"llama3.3:70b"}' \
  "$BASE_URL/ollama/api/show"

# Generate text (non-streaming)
curl -k -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.3:70b",
    "prompt": "Say hello in one sentence",
    "stream": false
  }' \
  "$BASE_URL/ollama/api/generate"

# Chat completion
curl -k -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.3:70b",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "stream": false
  }' \
  "$BASE_URL/ollama/api/chat"
```

## ChromaDB Tests (API v2)

**Note**: ChromaDB v1 API is deprecated. Use v2 endpoints.

```bash
# Heartbeat
curl -k -H "X-API-Key: $API_KEY" \
  "$BASE_URL/chroma/api/v2/heartbeat"

# Get version
curl -k -H "X-API-Key: $API_KEY" \
  "$BASE_URL/chroma/api/v2/version"

# List collections
curl -k -H "X-API-Key: $API_KEY" \
  "$BASE_URL/chroma/api/v2/collections"

# Create a collection
curl -k -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"test_collection","metadata":{}}' \
  "$BASE_URL/chroma/api/v2/collections"

# Get collection
curl -k -H "X-API-Key: $API_KEY" \
  "$BASE_URL/chroma/api/v2/collections/test_collection"

# Add documents
curl -k -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": ["doc1", "doc2"],
    "documents": ["First document", "Second document"],
    "metadatas": [{"source": "test"}, {"source": "test"}]
  }' \
  "$BASE_URL/chroma/api/v2/collections/test_collection/add"

# Query collection
curl -k -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query_texts": ["document"],
    "n_results": 2
  }' \
  "$BASE_URL/chroma/api/v2/collections/test_collection/query"

# Count documents
curl -k -H "X-API-Key: $API_KEY" \
  "$BASE_URL/chroma/api/v2/collections/test_collection/count"

# Get documents
curl -k -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ids":["doc1","doc2"]}' \
  "$BASE_URL/chroma/api/v2/collections/test_collection/get"

# Update documents
curl -k -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": ["doc1"],
    "documents": ["Updated document"],
    "metadatas": [{"source": "test_updated"}]
  }' \
  "$BASE_URL/chroma/api/v2/collections/test_collection/update"

# Delete collection
curl -k -H "X-API-Key: $API_KEY" \
  -X DELETE \
  "$BASE_URL/chroma/api/v2/collections/test_collection"
```

## Neo4j Tests

Neo4j requires both API Key (for Caddy) and Basic Auth (for Neo4j).

```bash
# Create Basic Auth header
export NEO4J_AUTH=$(echo -n "neo4j:$NEO4J_PASSWORD" | base64)

# Get service root
curl -k -H "X-API-Key: $API_KEY" \
  -H "Authorization: Basic $NEO4J_AUTH" \
  "$BASE_URL/neo4j/"

# Get database info
curl -k -H "X-API-Key: $API_KEY" \
  -H "Authorization: Basic $NEO4J_AUTH" \
  "$BASE_URL/neo4j/db/data/"

# Execute Cypher query
curl -k -H "X-API-Key: $API_KEY" \
  -H "Authorization: Basic $NEO4J_AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "statements": [
      {"statement": "RETURN 1 AS number"}
    ]
  }' \
  "$BASE_URL/neo4j/db/data/transaction/commit"

# Create a node
curl -k -H "X-API-Key: $API_KEY" \
  -H "Authorization: Basic $NEO4J_AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "statements": [
      {
        "statement": "CREATE (n:TestNode {name: $name}) RETURN n",
        "parameters": {"name": "Test"}
      }
    ]
  }' \
  "$BASE_URL/neo4j/db/data/transaction/commit"

# Query nodes
curl -k -H "X-API-Key: $API_KEY" \
  -H "Authorization: Basic $NEO4J_AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "statements": [
      {"statement": "MATCH (n:TestNode) RETURN n LIMIT 10"}
    ]
  }' \
  "$BASE_URL/neo4j/db/data/transaction/commit"

# Delete test nodes
curl -k -H "X-API-Key: $API_KEY" \
  -H "Authorization: Basic $NEO4J_AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "statements": [
      {"statement": "MATCH (n:TestNode) DELETE n"}
    ]
  }' \
  "$BASE_URL/neo4j/db/data/transaction/commit"
```

## Redis Tests (Direct Connection)

Redis uses a direct connection on port 6379, not through Caddy.

```bash
# PING test
redis-cli -h $HOST -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning PING

# Set a key
redis-cli -h $HOST -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning \
  SET mykey "Hello World"

# Get a key
redis-cli -h $HOST -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning \
  GET mykey

# Check key existence
redis-cli -h $HOST -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning \
  EXISTS mykey

# Delete a key
redis-cli -h $HOST -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning \
  DEL mykey

# Get server info
redis-cli -h $HOST -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning \
  INFO server

# Get database size
redis-cli -h $HOST -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning \
  DBSIZE

# List keys (use with caution in production)
redis-cli -h $HOST -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning \
  KEYS "*" | head -10
```

## Authentication Tests

```bash
# Test without API key (should return 401)
curl -k -w "\nHTTP Status: %{http_code}\n" \
  "$BASE_URL/ollama/api/tags"

# Test with wrong API key (should return 401)
curl -k -w "\nHTTP Status: %{http_code}\n" \
  -H "X-API-Key: wrong-key" \
  "$BASE_URL/ollama/api/tags"

# Test with correct API key (should return 200)
curl -k -w "\nHTTP Status: %{http_code}\n" \
  -H "X-API-Key: $API_KEY" \
  "$BASE_URL/ollama/api/tags"
```

## SSL/TLS Tests

```bash
# Check certificate
openssl s_client -connect "$HOST:$PORT" -servername "$HOST" </dev/null 2>/dev/null | \
  openssl x509 -noout -text

# Check certificate validity dates
openssl s_client -connect "$HOST:$PORT" -servername "$HOST" </dev/null 2>/dev/null | \
  openssl x509 -noout -dates

# Check TLS version
openssl s_client -connect "$HOST:$PORT" -servername "$HOST" </dev/null 2>&1 | \
  grep "Protocol"

# Test TLS 1.2
openssl s_client -tls1_2 -connect "$HOST:$PORT" -servername "$HOST" </dev/null 2>&1 | \
  grep "Protocol"

# Test TLS 1.3
openssl s_client -tls1_3 -connect "$HOST:$PORT" -servername "$HOST" </dev/null 2>&1 | \
  grep "Protocol"
```

## Performance Tests

```bash
# Measure response time
curl -k -H "X-API-Key: $API_KEY" \
  -w "\nTime: %{time_total}s\n" \
  -o /dev/null -s \
  "$BASE_URL/chroma/api/v1/heartbeat"

# Measure DNS + Connect + TLS + Transfer
curl -k -H "X-API-Key: $API_KEY" \
  -w "DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTLS: %{time_appconnect}s\nTotal: %{time_total}s\n" \
  -o /dev/null -s \
  "$BASE_URL/health"
```

## Batch Testing

```bash
# Test all endpoints quickly
for endpoint in health ollama/api/tags chroma/api/v1/heartbeat; do
  echo -n "Testing /$endpoint... "
  status=$(curl -k -H "X-API-Key: $API_KEY" -o /dev/null -w "%{http_code}" -s "$BASE_URL/$endpoint")
  if [ "$status" = "200" ]; then
    echo "✓ OK ($status)"
  else
    echo "✗ FAIL ($status)"
  fi
done
```

## Debugging

```bash
# Verbose output
curl -v -k -H "X-API-Key: $API_KEY" \
  "$BASE_URL/health"

# Show headers only
curl -I -k -H "X-API-Key: $API_KEY" \
  "$BASE_URL/health"

# Save response to file
curl -k -H "X-API-Key: $API_KEY" \
  "$BASE_URL/ollama/api/tags" \
  -o ollama_models.json

# Follow redirects
curl -L -k -H "X-API-Key: $API_KEY" \
  "$BASE_URL/some/endpoint"

# Set timeout
curl -k -H "X-API-Key: $API_KEY" \
  --max-time 30 \
  "$BASE_URL/ollama/api/generate" \
  -d '{"model":"llama3.3:70b","prompt":"test","stream":false}'
```

## Notes

- `-k` flag disables SSL certificate verification (use for self-signed certs)
- Remove `-k` if using a valid CA-signed certificate
- All HTTP services require the `X-API-Key` header
- Neo4j requires both `X-API-Key` and `Authorization: Basic` headers
- Redis uses direct connection (not HTTP), requires password authentication
