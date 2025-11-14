#!/bin/bash
# Test script for Secret Agent services on secretai-yyzz.scrtlabs.com
#
# Usage: ./scripts/test_services.sh
#
# This script tests all services through the Caddy reverse proxy with HTTPS

# set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color


# Credentials
. ../.env.remote

# Configuration
HOST=${REMOTE_HOST}
PORT=${REMOTE_PORT}
BASE_URL="https://${HOST}:${PORT}"

# Helper functions
print_header() {
    echo -e "\n${YELLOW}========================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "  $1"
}

# Test function
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="${4:-}"
    local extra_args="${5:-}"

    echo -n "Testing $name - $url "

    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "X-API-Key: $API_KEY" \
            -H "Content-Type: application/json" \
            -d "$data" \
            $extra_args \
            "$url" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "X-API-Key: $API_KEY" \
            $extra_args \
            "$url" 2>&1)
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        print_success "$name (HTTP $http_code)"
        if [ -n "$body" ] && [ "$body" != "OK" ]; then
            print_info "Response: ${body:0:100}$([ ${#body} -gt 100 ] && echo '...')"
        fi
        return 0
    else
        print_error "$name (HTTP $http_code)"
        print_info "Response: $body"
        return 1
    fi
}

# =============================================================================
# HEALTH CHECK
# =============================================================================

print_header "Health Check (No Auth Required)"

test_endpoint "Health endpoint" "$BASE_URL/health" "GET" "" "-k"

# =============================================================================
# OLLAMA TESTS
# =============================================================================

print_header "Testing Ollama Service"

# List models
test_endpoint "List Ollama models" "$BASE_URL/ollama/api/tags" "GET" "" "-k"

# Get model info (if llama3.3:70b exists)
test_endpoint "Get model info" "$BASE_URL/ollama/api/show" "POST" \
    '{"name":"llama3.3:70b"}' "-k"

# Test generation (simple)
test_endpoint "Test generation" "$BASE_URL/ollama/api/generate" "POST" \
    '{"model":"llama3.3:70b","prompt":"Say hello","stream":false}' "-k"

# =============================================================================
# CHROMADB TESTS (API v2)
# =============================================================================

print_header "Testing ChromaDB Service"

# Heartbeat
test_endpoint "ChromaDB heartbeat" "$BASE_URL/chroma/api/v2/heartbeat" "GET" "" "-k"

# Get version
test_endpoint "ChromaDB version" "$BASE_URL/chroma/api/v2/version" "GET" "" "-k"

# List collections
test_endpoint "List collections" "$BASE_URL/chroma/api/v2/collections" "GET" "" "-k"

# Create a test collection
COLLECTION_NAME="test_collection_$(date +%s)"
test_endpoint "Create collection" "$BASE_URL/chroma/api/v2/collections" "POST" \
    "{\"name\":\"$COLLECTION_NAME\",\"metadata\":{}}" "-k"

# Get collection
test_endpoint "Get collection" "$BASE_URL/chroma/api/v2/collections/$COLLECTION_NAME" "GET" "" "-k"

# Add documents
test_endpoint "Add documents" "$BASE_URL/chroma/api/v2/collections/$COLLECTION_NAME/add" "POST" \
    '{"ids":["id1"],"documents":["This is a test document"],"metadatas":[{"source":"test"}]}' "-k"

# Query collection
test_endpoint "Query collection" "$BASE_URL/chroma/api/v2/collections/$COLLECTION_NAME/query" "POST" \
    '{"query_texts":["test"],"n_results":1}' "-k"

# Count documents
test_endpoint "Count documents" "$BASE_URL/chroma/api/v2/collections/$COLLECTION_NAME/count" "GET" "" "-k"

# Delete collection (cleanup)
test_endpoint "Delete test collection" "$BASE_URL/chroma/api/v2/collections/$COLLECTION_NAME" "DELETE" "" "-k"

# =============================================================================
# NEO4J TESTS
# =============================================================================

print_header "Testing Neo4j Service"

# Note: Neo4j HTTP API requires both API key (Caddy) and Basic Auth (Neo4j)
NEO4J_AUTH=$(echo -n "neo4j:$NEO4J_PASSWORD" | base64)

# Get Neo4j info
test_endpoint "Neo4j service root" "$BASE_URL/neo4j/" "GET" "" "-k -H 'Authorization: Basic $NEO4J_AUTH'"

# Get database info
test_endpoint "Neo4j database info" "$BASE_URL/neo4j/db/data/" "GET" "" "-k -H 'Authorization: Basic $NEO4J_AUTH'"

# Execute Cypher query (returns 1)
test_endpoint "Execute Cypher query" "$BASE_URL/neo4j/db/data/transaction/commit" "POST" \
    '{"statements":[{"statement":"RETURN 1 AS number"}]}' "-k -H 'Authorization: Basic $NEO4J_AUTH'"

# =============================================================================
# REDIS TESTS (Direct Connection)
# =============================================================================

print_header "Testing Redis Service (Direct Connection)"

# Note: Redis uses direct connection on port 6379, not through Caddy
# We'll use redis-cli if available

if command -v redis-cli &> /dev/null; then
    echo -n "Testing Redis PING... "
    if redis-cli -h "$HOST" -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning PING | grep -q "PONG"; then
        print_success "Redis PING"
    else
        print_error "Redis PING failed"
    fi

    echo -n "Testing Redis SET/GET... "
    redis-cli -h "$HOST" -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning SET test_key "test_value" > /dev/null
    VALUE=$(redis-cli -h "$HOST" -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning GET test_key)
    if [ "$VALUE" = "test_value" ]; then
        print_success "Redis SET/GET"
        redis-cli -h "$HOST" -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning DEL test_key > /dev/null
    else
        print_error "Redis SET/GET failed"
    fi

    echo -n "Testing Redis INFO... "
    if redis-cli -h "$HOST" -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning INFO server | grep -q "redis_version"; then
        print_success "Redis INFO"
    else
        print_error "Redis INFO failed"
    fi
else
    print_info "redis-cli not found - skipping Redis tests"
    print_info "Install with: sudo apt-get install redis-tools"
fi

# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================

print_header "Testing Authentication"

# Test without API key (should fail)
echo -n "Testing Ollama without API key (should fail)... "
response=$(curl -s -w "\n%{http_code}" -k "$BASE_URL/ollama/api/tags" 2>&1)
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "401" ]; then
    print_success "Correctly rejected (HTTP 401)"
else
    print_error "Expected 401, got $http_code"
fi

# Test with wrong API key (should fail)
echo -n "Testing Ollama with wrong API key (should fail)... "
response=$(curl -s -w "\n%{http_code}" -k -H "X-API-Key: wrong-key" "$BASE_URL/ollama/api/tags" 2>&1)
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "401" ]; then
    print_success "Correctly rejected (HTTP 401)"
else
    print_error "Expected 401, got $http_code"
fi

# =============================================================================
# SSL/TLS TESTS
# =============================================================================

print_header "Testing SSL/TLS"

# Test SSL certificate
echo -n "Testing SSL certificate... "
if openssl s_client -connect "$HOST:$PORT" -servername "$HOST" </dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
    print_success "SSL certificate valid"
else
    print_info "SSL certificate verification failed (may be self-signed)"
    # Try to get certificate info
    echo "Certificate info:"
    openssl s_client -connect "$HOST:$PORT" -servername "$HOST" </dev/null 2>/dev/null | \
        openssl x509 -noout -subject -dates 2>/dev/null || true
fi

# Test TLS version
echo -n "Testing TLS version... "
tls_version=$(openssl s_client -connect "$HOST:$PORT" -servername "$HOST" </dev/null 2>/dev/null | \
    grep "Protocol" | awk '{print $3}')
if [ -n "$tls_version" ]; then
    print_success "TLS version: $tls_version"
else
    print_error "Could not determine TLS version"
fi

# =============================================================================
# SUMMARY
# =============================================================================

print_header "Test Summary"

echo "All tests completed!"
echo ""
echo "Services tested:"
echo "  - Caddy (HTTPS reverse proxy)"
echo "  - Ollama (LLM service)"
echo "  - ChromaDB (Vector database)"
echo "  - Neo4j (Graph database)"
echo "  - Redis (Cache - direct connection)"
echo ""
echo "Host: $HOST:$PORT"
echo "Protocol: HTTPS with TLS"
echo "Authentication: API Key + service-level auth"
