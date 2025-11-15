# 🚀 **SECRETAGENT - DETAILED IMPLEMENTATION PLAN**

## **Starting Point: Leveraging MCP-SCRT POC**

**POC Status**: ✅ **PRODUCTION-READY**
- 637 tests passing (100% pass rate)
- 60 MCP tools across 11 categories
- ~22,500 lines of code
- Complete infrastructure (session, cache, security, validation)
- 2 MCP prompts, 4 MCP resources already built

**Strategy**: Build on top of proven foundation, add Gradio UI + Knowledge Base + Agent layer

---

## 📁 **PROJECT STRUCTURE**

```
secret-agent/
├── mcp-scrt/                          # Submodule/Copy of POC
│   ├── src/mcp_scrt/                  # Existing MCP server (DO NOT MODIFY)
│   │   ├── types.py
│   │   ├── constants.py
│   │   ├── config.py
│   │   ├── utils/
│   │   ├── core/
│   │   ├── sdk/
│   │   ├── tools/                     # 60 tools ready to use
│   │   ├── prompts/                   # 2 existing prompts
│   │   └── resources/                 # 4 existing resources
│   └── tests/                         # 637 tests
│
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── orchestrator.py           # Main agent logic
│   │   ├── intent_classifier.py      # Classify user intent
│   │   ├── planner.py                # Multi-step planning
│   │   ├── executor.py               # Tool execution wrapper
│   │   └── response_formatter.py     # Format agent responses
│   │
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── embedder.py               # ChromaDB embedding
│   │   ├── retriever.py              # Hybrid retrieval
│   │   ├── cache.py                  # Redis caching
│   │   └── content/                  # Knowledge markdown files
│   │       ├── fundamentals.md
│   │       ├── privacy.md
│   │       ├── tokens.md
│   │       ├── staking.md
│   │       ├── contracts.md
│   │       ├── security.md
│   │       └── faq.md
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── ollama_client.py          # Ollama integration
│   │   └── prompt_templates.py       # System prompts
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py                    # Main Gradio app
│   │   ├── chat_tab.py               # Chat interface
│   │   ├── portfolio_tab.py          # Portfolio dashboard
│   │   ├── validators_tab.py         # Validator table
│   │   ├── settings_tab.py           # Settings panel
│   │   └── theme.py                  # Custom Gradio theme
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py                 # App configuration
│       ├── logging_config.py         # Logging setup
│       └── mcp_bridge.py             # Bridge to MCP-SCRT
│
├── assets/
│   ├── logo.png
│   ├── user_avatar.png
│   └── agent_avatar.png
│
├── tests/
│   ├── test_agent.py
│   ├── test_knowledge.py
│   └── test_integration.py
│
├── scripts/
│   ├── setup_knowledge.py            # Embed knowledge to ChromaDB
│   ├── test_connections.py           # Test remote services
│   └── demo_data.py                  # Load demo/test data
│
├── app.py                            # Main entry point
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── docker-compose.yml                # Optional: local services
```

---

## 📦 **DEPENDENCIES & REQUIREMENTS**

### **requirements.txt**
```txt
# Base MCP-SCRT dependencies (from POC)
# (All dependencies from mcp-scrt/requirements.txt)

# Gradio
gradio>=6.0.0

# LLM Integration
requests>=2.31.0           # For Ollama API
sseclient-py>=1.8.0       # For Ollama streaming

# Knowledge Base
chromadb>=0.4.0           # Vector database
sentence-transformers>=2.2.2  # Embeddings
markdown>=3.5.0           # Markdown parsing

# Caching
redis>=5.0.0              # Redis client

# Utilities
pydantic>=2.5.0           # Already in MCP-SCRT
python-dotenv>=1.0.0      # Already in MCP-SCRT
```

---

## 🔧 **CONFIGURATION**

### **.env.example**
```bash
# MCP-SCRT Configuration (from POC)
SECRET_NETWORK=testnet
SECRET_TESTNET_URL=https://lcd.testnet.secretsaturn.net
SECRET_TESTNET_CHAIN_ID=pulsar-3
SPENDING_LIMIT=10000000
CONFIRMATION_THRESHOLD=1000000

# Remote Services
OLLAMA_URL=http://remote-server:11434
OLLAMA_MODEL=llama3.3:70b
CHROMADB_URL=http://remote-server:8000
REDIS_URL=redis://remote-server:6379
NEO4J_URL=bolt://remote-server:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Gradio Configuration
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
GRADIO_SHARE=false

# Application Settings
LOG_LEVEL=INFO
ENABLE_CACHE=true
CACHE_TTL=300
```

---

## 📅 **REVISED IMPLEMENTATION PLAN**

Given the POC is production-ready, we can accelerate significantly.

---

## **PHASE 1: FOUNDATION** (Days 1-2)

### **Day 1 (Nov 14) - Setup & Knowledge Base Content**

**Total Effort**: 8 hours

#### **Task 1.1: Project Setup** (1.5 hours)
**Scope**:
- Clone/copy mcp-scrt POC as submodule or subdirectory
- Create new project structure around it
- Set up virtual environment
- Install all dependencies
- Run POC tests to verify (637 should pass)
- Configure .env with testnet + remote services

**Commands**:
```bash
# Option 1: Submodule
git init secret-agent
cd secret-agent
git submodule add https://github.com/alexh-scrt/mcp-scrt.git
git submodule update --init 

# Option 2: Copy
git clone https://github.com/alexh-scrt/mcp-scrt.git
cp -r mcp-scrt secret-agent/
cd secret-agent

# Setup
python3.13 -m venv venv
source venv/bin/activate
pip install -e ./mcp-scrt/
pip install -r requirements.txt

# Test POC
cd mcp-scrt
pytest
# Should see: 637 passed

# Configure
cp .env.example .env
# Edit .env with remote server IPs
```

**Deliverables**:
- ✅ MCP-SCRT POC verified working
- ✅ New project structure created
- ✅ Dependencies installed
- ✅ Configuration complete

---

#### **Task 1.2: Test Remote Services** (1.5 hours)
**Scope**:
- Write connection test script
- Test Ollama connection and inference
- Test ChromaDB connection and basic operations
- Test Redis connection and caching
- Document connection parameters
- Troubleshoot any issues

**Script**: `scripts/test_connections.py`
```python
"""Test all remote service connections."""

import requests
import redis
from chromadb import HttpClient
import sys

def test_ollama(url: str, model: str):
    """Test Ollama connection."""
    print(f"Testing Ollama at {url}...")
    try:
        response = requests.post(
            f"{url}/api/generate",
            json={"model": model, "prompt": "Hello", "stream": False},
            timeout=10
        )
        if response.status_code == 200:
            print(f"✅ Ollama connected - Model: {model}")
            return True
    except Exception as e:
        print(f"❌ Ollama failed: {e}")
        return False

def test_chromadb(url: str):
    """Test ChromaDB connection."""
    print(f"Testing ChromaDB at {url}...")
    try:
        client = HttpClient(host=url.split("://")[1].split(":")[0], 
                           port=int(url.split(":")[-1]))
        client.heartbeat()
        print("✅ ChromaDB connected")
        return True
    except Exception as e:
        print(f"❌ ChromaDB failed: {e}")
        return False

def test_redis(url: str):
    """Test Redis connection."""
    print(f"Testing Redis at {url}...")
    try:
        r = redis.from_url(url)
        r.ping()
        print("✅ Redis connected")
        return True
    except Exception as e:
        print(f"❌ Redis failed: {e}")
        return False

if __name__ == "__main__":
    # Load from .env or args
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    results = {
        "ollama": test_ollama(
            os.getenv("OLLAMA_URL"), 
            os.getenv("OLLAMA_MODEL")
        ),
        "chromadb": test_chromadb(os.getenv("CHROMADB_URL")),
        "redis": test_redis(os.getenv("REDIS_URL"))
    }
    
    print("\n=== Connection Test Summary ===")
    for service, status in results.items():
        print(f"{service}: {'✅ PASS' if status else '❌ FAIL'}")
    
    if not all(results.values()):
        sys.exit(1)
```

**Deliverables**:
- ✅ All remote services tested
- ✅ Connection script working
- ✅ Issues documented/resolved

---

#### **Task 1.3: Knowledge Base Content** (5 hours)
**Scope**: Write 7 markdown files (~5,000 words total)

**Content Creation Strategy**:
- Use official Secret Network docs as source
- Write in conversational, accessible tone
- Include examples and analogies
- Cross-reference between topics

**Files to Create**:

1. **fundamentals.md** (700 words, 45 min)
   - What is Secret Network
   - Architecture overview
   - SCRT token
   - Use cases
   - Getting started

2. **privacy.md** (800 words, 50 min)
   - TEE technology
   - Intel SGX
   - Encryption mechanisms
   - Privacy vs transparency
   - Comparison with other chains

3. **tokens.md** (600 words, 40 min)
   - SCRT token
   - SNIP-20 standard
   - Wrapping/unwrapping
   - Viewing keys
   - Query permits

4. **staking.md** (800 words, 50 min)
   - How staking works
   - Choosing validators
   - Delegation process
   - Rewards mechanics
   - Unbonding period
   - Risks and best practices

5. **contracts.md** (900 words, 60 min)
   - Secret Contracts explained
   - CosmWasm basics
   - Contract lifecycle
   - Privacy patterns
   - Common use cases
   - Examples

6. **security.md** (600 words, 40 min)
   - Wallet security
   - Mnemonic safety
   - Transaction verification
   - Common scams
   - Best practices

7. **faq.md** (600 words, 45 min)
   - 25+ Q&A pairs
   - Organized by category
   - Getting started
   - Operations
   - Technical
   - Troubleshooting

**Deliverables**:
- ✅ 7 markdown files created
- ✅ ~5,000 words of content
- ✅ Proofread and reviewed

---

### **Day 2 (Nov 15) - Knowledge System Implementation**

**Total Effort**: 8 hours

#### **Task 2.1: ChromaDB Embedder** (2 hours)

**File**: `src/knowledge/embedder.py`

**Scope**:
- Parse markdown files into semantic chunks
- Generate embeddings using sentence-transformers
- Store in ChromaDB with metadata
- Handle updates and versioning

**Key Functions**:
```python
class KnowledgeEmbedder:
    def __init__(self, chromadb_url: str):
        """Initialize ChromaDB client and embedding model."""
        
    def parse_markdown(self, filepath: str) -> list[dict]:
        """Parse markdown into semantic chunks."""
        # Split by headers (##)
        # Keep metadata (topic, section, subsection)
        # Return list of chunks with metadata
        
    def embed_content(self, content_dir: str):
        """Embed all markdown files to ChromaDB."""
        # For each .md file:
        #   - Parse into chunks
        #   - Generate embeddings
        #   - Store in collection
        
    def update_chunk(self, chunk_id: str, content: str):
        """Update a single chunk."""
        
    def delete_topic(self, topic: str):
        """Delete all chunks for a topic."""
```

**Collection Schema**:
```python
{
    "id": "fundamentals_section_1",
    "embedding": [0.123, -0.456, ...],  # Auto-generated
    "metadata": {
        "topic": "fundamentals",
        "section": "What is Secret Network",
        "subsection": None,
        "word_count": 150,
        "last_updated": "2025-11-15"
    },
    "document": "Secret Network is the first blockchain..."
}
```

**Deliverables**:
- ✅ Embedder module complete
- ✅ All knowledge embedded
- ✅ Tested with sample queries

---

#### **Task 2.2: Knowledge Retriever** (3 hours)

**File**: `src/knowledge/retriever.py`

**Scope**:
- Hybrid retrieval (vector + keyword)
- Re-ranking logic
- Context assembly
- Source attribution

**Key Functions**:
```python
class KnowledgeRetriever:
    def __init__(self, chromadb_url: str, redis_url: str):
        """Initialize retriever with ChromaDB and Redis."""
        
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5,
        min_score: float = 0.5
    ) -> list[dict]:
        """Retrieve relevant knowledge chunks."""
        # 1. Check Redis cache
        # 2. Vector search in ChromaDB
        # 3. Re-rank results
        # 4. Cache results
        # 5. Return top_k
        
    def retrieve_by_topic(self, topic: str) -> str:
        """Get full content for a specific topic."""
        
    def get_related_topics(self, query: str) -> list[str]:
        """Get related topic names for suggestions."""
```

**Retrieval Strategy**:
1. **Cache Check**: Redis (key: query_hash, TTL: 5 min)
2. **Vector Search**: ChromaDB similarity search (cosine)
3. **Keyword Boost**: Boost exact matches in metadata
4. **Re-ranking**: Consider recency, completeness
5. **Filtering**: Remove low-score results (<0.5)

**Deliverables**:
- ✅ Retriever module complete
- ✅ Redis caching working
- ✅ Quality tested on 20+ queries

---

#### **Task 2.3: Setup Script** (1 hour)

**File**: `scripts/setup_knowledge.py`

**Scope**:
- Automate knowledge embedding
- Clear and rebuild collection
- Verify embeddings

**Script**:
```python
"""Setup knowledge base in ChromaDB."""

from src.knowledge.embedder import KnowledgeEmbedder
from src.knowledge.retriever import KnowledgeRetriever
import os

def main():
    chromadb_url = os.getenv("CHROMADB_URL")
    redis_url = os.getenv("REDIS_URL")
    
    print("Setting up knowledge base...")
    
    # Embed knowledge
    embedder = KnowledgeEmbedder(chromadb_url)
    embedder.embed_content("src/knowledge/content")
    
    print("Knowledge embedded successfully!")
    
    # Test retrieval
    retriever = KnowledgeRetriever(chromadb_url, redis_url)
    results = retriever.retrieve("What is Secret Network?")
    
    print(f"\nTest query returned {len(results)} results")
    print(f"Top result: {results[0]['metadata']['section']}")
    
    print("\n✅ Knowledge base ready!")

if __name__ == "__main__":
    main()
```

**Run**:
```bash
python scripts/setup_knowledge.py
```

**Deliverables**:
- ✅ Setup script working
- ✅ Knowledge base initialized
- ✅ Test queries successful

---

#### **Task 2.4: Testing & Documentation** (2 hours)

**Scope**:
- Unit tests for embedder and retriever
- Integration tests
- Document knowledge system

**Tests**: `tests/test_knowledge.py`
```python
def test_embedder_parse_markdown():
    """Test markdown parsing."""
    
def test_embedder_create_chunks():
    """Test chunk creation."""
    
def test_retriever_vector_search():
    """Test vector search."""
    
def test_retriever_caching():
    """Test Redis caching."""
    
def test_retriever_quality():
    """Test retrieval quality on known queries."""
```

**Test Queries** (for quality testing):
- "What is Secret Network?" → Should return fundamentals
- "How do I stake SCRT?" → Should return staking guide
- "What is a viewing key?" → Should return tokens/privacy
- "Is my data encrypted?" → Should return privacy info
- "How to choose validator?" → Should return staking guide

**Deliverables**:
- ✅ Tests written and passing
- ✅ Knowledge system documented
- ✅ Quality benchmarks established

---

## **PHASE 2: AGENT CORE** (Days 3-5)

### **Day 3 (Nov 16) - LLM Integration**

**Total Effort**: 8 hours

#### **Task 3.1: Ollama Client** (3 hours)

**File**: `src/llm/ollama_client.py`

**Scope**:
- Wrapper for Ollama API
- Streaming and non-streaming modes
- Error handling and retries
- Response parsing

**Key Class**:
```python
class OllamaClient:
    def __init__(self, base_url: str, model: str):
        """Initialize Ollama client."""
        self.base_url = base_url
        self.model = model
        
    def generate(
        self, 
        prompt: str, 
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str | Iterator[str]:
        """Generate completion."""
        # POST to /api/generate
        # Handle streaming vs non-streaming
        # Parse response
        # Error handling
        
    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str | Iterator[str]:
        """Chat completion with message history."""
        # POST to /api/chat
        # Handle conversation context
        
    def _stream_response(self, response) -> Iterator[str]:
        """Stream response chunks."""
        # Parse SSE stream
        # Yield text chunks
```

**Error Handling**:
- Connection timeouts (retry 3x)
- Model not found (fail gracefully)
- Invalid response (log and retry)
- Rate limiting (exponential backoff)

**Deliverables**:
- ✅ Ollama client complete
- ✅ Streaming working
- ✅ Error handling robust
- ✅ Tested with llama3.3:70b

---

#### **Task 3.2: Prompt Templates** (2 hours)

**File**: `src/llm/prompt_templates.py`

**Scope**:
- System prompts for different modes
- Few-shot examples
- Output formatting instructions

**Templates**:

```python
INTENT_CLASSIFIER_PROMPT = """You are an intent classifier for SecretAgent, an AI assistant for Secret Network blockchain.

Analyze the user's message and classify it:
- "question": User wants to learn/understand
- "command": User wants to execute operation  
- "hybrid": User wants both explanation + action

Output JSON only:
{
    "type": "question|command|hybrid",
    "topic": "string or null",
    "action": "string or null",
    "entities": ["entity1", "entity2"],
    "confidence": 0.95
}

Examples:

User: "What is a validator?"
{"type": "question", "topic": "staking", "action": null, "entities": ["validator"], "confidence": 0.98}

User: "Stake 100 SCRT"
{"type": "command", "topic": "staking", "action": "delegate", "entities": ["100", "SCRT"], "confidence": 0.95}

User: "Explain staking and stake 50 SCRT to best validator"
{"type": "hybrid", "topic": "staking", "action": "delegate", "entities": ["50", "SCRT", "best validator"], "confidence": 0.92}
"""

KNOWLEDGE_ANSWER_PROMPT = """You are SecretAgent, an expert AI assistant for Secret Network.

Use the provided knowledge to answer the user's question.

Knowledge Context:
{context}

Guidelines:
- Be conversational and helpful
- Explain clearly without jargon (or define jargon)
- Use analogies when helpful
- Be concise (2-3 paragraphs max)
- If unsure, acknowledge uncertainty
- Suggest follow-up actions

User Question: {question}
"""

TOOL_PLANNING_PROMPT = """You are SecretAgent's planning module.

User wants to: {user_intent}

Available tools: {tools_list}

Create a step-by-step execution plan using available tools.

Output JSON only:
{
    "steps": [
        {
            "step_number": 1,
            "tool": "tool_name",
            "parameters": {"param1": "value1"},
            "description": "Human-readable description",
            "depends_on": []
        }
    ],
    "requires_confirmation": true,
    "estimated_time": "30 seconds",
    "risks": ["risk1", "risk2"]
}
"""

VALIDATOR_ANALYSIS_PROMPT = """Analyze these validators and recommend the best one for delegation.

Validators:
{validators_json}

Criteria:
- Decentralization (lower voting power = better)
- Commission (5-10% is reasonable)
- Uptime (99%+ required)
- Community reputation

Output JSON:
{
    "recommended": {
        "address": "secretvaloper...",
        "name": "Validator Name",
        "score": 9.2
    },
    "reasoning": "Brief explanation",
    "alternatives": [...]
}
"""
```

**Deliverables**:
- ✅ All prompt templates defined
- ✅ Examples included
- ✅ Output formats documented

---

#### **Task 3.3: Intent Classifier** (3 hours)

**File**: `src/agent/intent_classifier.py`

**Scope**:
- Classify user intent using LLM
- Extract entities (amounts, addresses, actions)
- Return structured intent object

**Key Class**:
```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Intent:
    type: str  # question, command, hybrid
    topic: Optional[str]
    action: Optional[str]
    entities: List[str]
    confidence: float
    raw_message: str

class IntentClassifier:
    def __init__(self, ollama_client: OllamaClient):
        self.llm = ollama_client
        
    async def classify(self, message: str) -> Intent:
        """Classify user intent."""
        # 1. Build prompt with examples
        # 2. Call LLM
        # 3. Parse JSON response
        # 4. Validate and return Intent object
        
    def _parse_llm_response(self, response: str) -> dict:
        """Parse LLM JSON response."""
        # Strip markdown code blocks
        # Parse JSON
        # Validate structure
        
    def _extract_entities(self, message: str) -> List[str]:
        """Extract key entities from message."""
        # Regex patterns for:
        # - Amounts (100 SCRT, 5.5 uscrt)
        # - Addresses (secret1...)
        # - Validator names
        # - Proposal IDs (#47)
```

**Entity Patterns**:
- Amount: `(\d+\.?\d*)\s*(SCRT|uscrt)`
- Address: `secret1[a-z0-9]{38}`
- Validator: `secretvaloper1[a-z0-9]{38}`
- Proposal: `#?\d+`

**Deliverables**:
- ✅ Intent classifier complete
- ✅ Entity extraction working
- ✅ JSON parsing robust
- ✅ Tested with 20+ examples

---

### **Day 4 (Nov 17) - MCP Bridge & Tool Execution**

**Total Effort**: 8 hours

#### **Task 4.1: MCP Bridge** (3 hours)

**File**: `src/utils/mcp_bridge.py`

**Scope**:
- Bridge between agent and MCP-SCRT tools
- Tool discovery and introspection
- Parameter mapping
- Result formatting

**Key Class**:
```python
from mcp_scrt.core.session import Session
from mcp_scrt.sdk.client import ClientPool
from mcp_scrt.tools.base import ToolExecutionContext
from mcp_scrt.types import NetworkType

class MCPBridge:
    """Bridge to MCP-SCRT server tools."""
    
    def __init__(self, network: NetworkType = NetworkType.TESTNET):
        self.session = Session(network=network)
        self.session.start()
        self.client_pool = ClientPool(network=network)
        self.context = ToolExecutionContext(
            session=self.session,
            client_pool=self.client_pool,
            network=network
        )
        self._tools_cache = self._discover_tools()
        
    def _discover_tools(self) -> dict:
        """Discover all available MCP tools."""
        # Import all tool modules
        # Build tool registry
        # Return {tool_name: tool_class}
        
    def list_tools(self) -> list[dict]:
        """Get list of available tools with descriptions."""
        # Return tool metadata for LLM
        
    async def execute_tool(
        self,
        tool_name: str,
        parameters: dict
    ) -> dict:
        """Execute an MCP tool."""
        # 1. Validate tool exists
        # 2. Validate parameters
        # 3. Instantiate tool
        # 4. Execute tool.run()
        # 5. Format result
        # 6. Handle errors
        
    def get_tool_info(self, tool_name: str) -> dict:
        """Get detailed info about a tool."""
        # Return schema, parameters, examples
```

**Tool Registry Format**:
```python
{
    "secret_get_balance": {
        "category": "bank",
        "description": "Get token balances for an address",
        "parameters": {
            "address": {"type": "string", "required": False}
        },
        "example": "Get my SCRT balance"
    },
    "secret_delegate": {
        "category": "staking",
        "description": "Delegate tokens to a validator",
        "parameters": {
            "validator_address": {"type": "string", "required": True},
            "amount": {"type": "string", "required": True}
        },
        "example": "Delegate 100 SCRT to validator"
    },
    # ... all 60 tools
}
```

**Deliverables**:
- ✅ MCP bridge complete
- ✅ All 60 tools accessible
- ✅ Tool registry built
- ✅ Error handling robust

---

#### **Task 4.2: Tool Executor** (3 hours)

**File**: `src/agent/executor.py`

**Scope**:
- Execute tools via MCP bridge
- Handle confirmations
- Progress tracking
- Result formatting

**Key Class**:
```python
from typing import Callable, Optional

class ToolExecutor:
    def __init__(self, mcp_bridge: MCPBridge):
        self.mcp = mcp_bridge
        self.execution_history = []
        
    async def execute(
        self,
        tool_name: str,
        parameters: dict,
        confirmation_callback: Optional[Callable] = None
    ) -> dict:
        """Execute a tool with confirmation if needed."""
        # 1. Check if confirmation needed
        # 2. Request confirmation if needed
        # 3. Execute tool via bridge
        # 4. Log execution
        # 5. Format result for user
        
    def _needs_confirmation(
        self,
        tool_name: str,
        parameters: dict
    ) -> bool:
        """Check if tool execution needs confirmation."""
        # Check spending limits
        # Check sensitive operations
        
    def _format_result(self, result: dict) -> str:
        """Format tool result for display."""
        # Convert technical result to user-friendly message
        # Extract key info (tx hash, amounts, etc.)
        
    def get_execution_history(self) -> list[dict]:
        """Get history of executed tools."""
```

**Confirmation Rules**:
- Send tokens: Confirm if amount > $100 equivalent
- Delegate: Confirm if amount > $500 equivalent
- Vote: Always confirm
- Undelegate: Always confirm (21-day lock)
- Contract execute: Always confirm

**Deliverables**:
- ✅ Tool executor complete
- ✅ Confirmations working
- ✅ History tracking
- ✅ Result formatting clear

---

#### **Task 4.3: Integration Testing** (2 hours)

**Scope**:
- Test complete flow: intent → tool → result
- Test error scenarios
- Verify testnet operations

**Test Scenarios**:
```python
# Scenario 1: Check Balance
user_msg = "What's my SCRT balance?"
intent = classifier.classify(user_msg)
result = executor.execute("secret_get_balance", {})
# Verify: Balance returned

# Scenario 2: Send Tokens
user_msg = "Send 1 SCRT to secret1test..."
intent = classifier.classify(user_msg)
result = executor.execute("secret_send_tokens", {
    "recipient": "secret1test...",
    "amount": "1000000",
    "denom": "uscrt"
})
# Verify: Tx hash returned

# Scenario 3: Query Validators
user_msg = "Show me the top validators"
intent = classifier.classify(user_msg)
result = executor.execute("secret_get_validators", {})
# Verify: Validator list returned
```

**Deliverables**:
- ✅ Integration tests passing
- ✅ Testnet operations verified
- ✅ Error handling confirmed

---

### **Day 5 (Nov 18) - Agent Orchestrator**

**Total Effort**: 8 hours

#### **Task 5.1: Response Formatter** (2 hours)

**File**: `src/agent/response_formatter.py`

**Scope**:
- Format agent responses for chat UI
- Add markdown formatting
- Include action buttons
- Add citations/sources

**Key Functions**:
```python
class ResponseFormatter:
    def format_knowledge_response(
        self,
        answer: str,
        sources: list[str],
        suggestions: list[str]
    ) -> str:
        """Format knowledge-based response."""
        # Add answer
        # Add source attribution
        # Add follow-up suggestions
        # Return markdown
        
    def format_tool_response(
        self,
        tool_name: str,
        result: dict,
        next_steps: list[str]
    ) -> str:
        """Format tool execution response."""
        # Success message
        # Key details (tx hash, amounts)
        # Next steps
        
    def format_error(
        self,
        error: Exception,
        suggestions: list[str]
    ) -> str:
        """Format error message."""
        # User-friendly error
        # Troubleshooting steps
        # Alternative actions
        
    def add_quick_actions(
        self,
        response: str,
        actions: list[dict]
    ) -> tuple[str, list]:
        """Add quick action buttons."""
        # Return (response, button_configs)
```

**Example Formatted Response**:
```markdown
### 💰 Balance Check

Your wallet has:
- **Available**: 1,234.56 SCRT
- **Staked**: 5,000.00 SCRT
- **Rewards**: 12.34 SCRT

**Next Steps**:
- Stake more tokens to earn rewards
- Withdraw your pending rewards
- Check validator performance

[Stake SCRT] [Withdraw Rewards] [View Validators]
```

**Deliverables**:
- ✅ Formatter module complete
- ✅ All response types handled
- ✅ Markdown rendering tested

---

#### **Task 5.2: Main Orchestrator** (4 hours)

**File**: `src/agent/orchestrator.py`

**Scope**:
- Main agent coordination logic
- Route requests to knowledge or tools
- Manage conversation context
- Coordinate multi-turn interactions

**Key Class**:
```python
class AgentOrchestrator:
    """Main agent coordinating all components."""
    
    def __init__(
        self,
        llm_client: OllamaClient,
        knowledge_retriever: KnowledgeRetriever,
        mcp_bridge: MCPBridge
    ):
        self.llm = llm_client
        self.knowledge = knowledge_retriever
        self.mcp = mcp_bridge
        self.classifier = IntentClassifier(llm_client)
        self.executor = ToolExecutor(mcp_bridge)
        self.formatter = ResponseFormatter()
        self.conversation_history = []
        
    async def process_message(
        self,
        message: str,
        stream: bool = True
    ) -> AsyncIterator[str] | str:
        """Process user message and return response."""
        # 1. Add to conversation history
        # 2. Classify intent
        # 3. Route to handler
        # 4. Format response
        # 5. Return (stream or complete)
        
    async def _handle_question(self, intent: Intent) -> str:
        """Handle knowledge question."""
        # 1. Retrieve relevant knowledge
        # 2. Build context
        # 3. Generate answer with LLM
        # 4. Add suggestions
        # 5. Format response
        
    async def _handle_command(self, intent: Intent) -> str:
        """Handle tool execution command."""
        # 1. Map intent to tool + params
        # 2. Request confirmation if needed
        # 3. Execute tool
        # 4. Format result
        # 5. Suggest next actions
        
    async def _handle_hybrid(self, intent: Intent) -> str:
        """Handle hybrid (question + command)."""
        # 1. Answer question first
        # 2. Then execute command
        # 3. Combine responses
        
    def _build_conversation_context(self) -> str:
        """Build context from conversation history."""
        # Keep last N messages
        # Summarize older context
        
    def reset_conversation(self):
        """Clear conversation history."""
```

**Conversation Context Management**:
- Keep full last 10 messages
- Summarize older messages
- Max context: 4000 tokens
- Implement sliding window

**Deliverables**:
- ✅ Orchestrator complete
- ✅ All routing working
- ✅ Context management functional
- ✅ Streaming responses working

---

#### **Task 5.3: End-to-End Testing** (2 hours)

**Scope**:
- Test complete agent workflows
- Verify all components integrated
- Test conversation flows

**Test Conversations**:

```python
# Test 1: Knowledge Flow
"What is Secret Network?"
→ Returns: Explanation with sources
"How do I get started?"
→ Returns: Getting started guide
"Create a wallet for me"
→ Returns: Wallet created, shows address

# Test 2: Tool Flow
"Check my balance"
→ Returns: Balance info
"Stake 50 SCRT"
→ Returns: Validator recommendation, confirms, executes
"Show my rewards"
→ Returns: Rewards amount

# Test 3: Hybrid Flow
"Explain staking and stake 100 SCRT to the best validator"
→ Returns: Staking explanation, then executes delegation
```

**Deliverables**:
- ✅ All workflows tested
- ✅ Agent responding correctly
- ✅ Ready for UI integration

---

## **PHASE 3: GRADIO UI** (Days 6-10)

### **Day 6 (Nov 19) - Chat Interface**

**Total Effort**: 8 hours

#### **Task 6.1: Custom Theme** (2 hours)

**File**: `src/ui/theme.py`

**Scope**:
- Create privacy-focused Gradio theme
- Dark and light mode support
- Custom colors and fonts
- Secret Network branding

**Theme Definition**:
```python
import gradio as gr

def create_secret_theme():
    """Create SecretAgent custom theme."""
    return gr.themes.Soft(
        primary_hue="purple",      # Deep purple
        secondary_hue="cyan",      # Cyan accent
        neutral_hue="slate",       # Dark backgrounds
        font=[
            gr.themes.GoogleFont("Inter"),
            "ui-sans-serif",
            "system-ui"
        ]
    ).set(
        # Dark mode colors
        body_background_fill="#0F172A",
        body_background_fill_dark="#020617",
        block_background_fill="#1E293B",
        block_background_fill_dark="#0F172A",
        
        # Primary colors
        button_primary_background_fill="#5B21B6",
        button_primary_background_fill_hover="#6D28D9",
        button_primary_text_color="#FFFFFF",
        
        # Chat colors
        chatbot_user_background_fill="#334155",
        chatbot_bot_background_fill="#1E293B",
        
        # Borders and shadows
        block_border_width="1px",
        block_border_color="#334155",
        block_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1)",
        
        # Fonts
        font_size="16px",
        text_size="14px"
    )
```

**Deliverables**:
- ✅ Custom theme created
- ✅ Dark/light modes working
- ✅ Brand consistent

---

#### **Task 6.2: Chat Tab** (4 hours)

**File**: `src/ui/chat_tab.py`

**Scope**:
- Main chat interface
- Streaming message display
- Quick action buttons
- Message history

**Component Structure**:
```python
def create_chat_tab(orchestrator: AgentOrchestrator):
    """Create main chat interface tab."""
    
    with gr.Tab("💬 Chat"):
        # Chatbot display
        chatbot = gr.Chatbot(
            label="SecretAgent",
            type="messages",
            height=600,
            avatar_images=[
                "assets/user_avatar.png",
                "assets/agent_avatar.png"
            ],
            show_copy_button=True,
            render_markdown=True
        )
        
        # Input area
        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Ask me anything about Secret Network or tell me what to do...",
                container=False,
                scale=9,
                show_label=False
            )
            submit_btn = gr.Button(
                "Send",
                variant="primary",
                scale=1
            )
        
        # Quick actions
        with gr.Row():
            gr.Button("💰 Check Balance", size="sm")
            gr.Button("🏛️ Stake SCRT", size="sm")
            gr.Button("🗳️ View Proposals", size="sm")
            gr.Button("❓ What is Secret Network?", size="sm")
        
        # Clear button
        clear_btn = gr.Button("Clear Conversation", size="sm")
        
        # Event handlers
        async def respond(message, history):
            """Handle user message and stream response."""
            # Add user message to history
            history.append({"role": "user", "content": message})
            
            # Stream agent response
            response_text = ""
            async for chunk in orchestrator.process_message(message, stream=True):
                response_text += chunk
                yield history + [{"role": "assistant", "content": response_text}]
            
            # Final update
            yield history + [{"role": "assistant", "content": response_text}]
        
        # Connect events
        msg_input.submit(respond, [msg_input, chatbot], [chatbot])
        submit_btn.click(respond, [msg_input, chatbot], [chatbot])
        clear_btn.click(lambda: None, None, chatbot)
```

**Deliverables**:
- ✅ Chat interface complete
- ✅ Streaming working
- ✅ Quick actions functional
- ✅ Message history persistent

---

#### **Task 6.3: Integration & Testing** (2 hours)

**Scope**:
- Connect chat UI to orchestrator
- Test streaming responses
- Test quick actions
- Test error display

**Test Cases**:
- Send message → receive streamed response
- Click quick action → auto-fill message
- Clear chat → history cleared
- Error message → displays gracefully
- Long response → scrolls correctly

**Deliverables**:
- ✅ Chat UI fully functional
- ✅ All interactions working
- ✅ Error handling tested

---

### **Day 7 (Nov 20) - Portfolio Dashboard**

**Total Effort**: 8 hours

#### **Task 7.1: Data Aggregator** (3 hours)

**File**: `src/ui/portfolio_tab.py` (data functions)

**Scope**:
- Aggregate portfolio data from MCP tools
- Calculate summary metrics
- Format for display

**Key Functions**:
```python
async def get_portfolio_data(mcp_bridge: MCPBridge) -> dict:
    """Aggregate portfolio data."""
    # Get balance
    balance = await mcp_bridge.execute_tool("secret_get_balance", {})
    
    # Get delegations
    delegations = await mcp_bridge.execute_tool("secret_get_delegations", {})
    
    # Get rewards
    rewards = await mcp_bridge.execute_tool("secret_get_rewards", {})
    
    # Calculate totals
    total_staked = sum(d['amount'] for d in delegations['delegations'])
    total_rewards = sum(r['amount'] for r in rewards['rewards'])
    
    return {
        "available": balance['balance'],
        "staked": total_staked,
        "rewards": total_rewards,
        "total": balance['balance'] + total_staked + total_rewards,
        "delegations": delegations['delegations'],
        "rewards_by_validator": rewards['rewards']
    }
```

**Deliverables**:
- ✅ Data aggregation working
- ✅ Metrics calculated correctly
- ✅ Error handling for missing data

---

#### **Task 7.2: Dashboard UI** (4 hours)

**File**: `src/ui/portfolio_tab.py`

**Scope**:
- Build portfolio overview tab
- Display summary cards
- Delegation table
- Rewards info

**Component Structure**:
```python
def create_portfolio_tab(mcp_bridge: MCPBridge):
    """Create portfolio dashboard tab."""
    
    with gr.Tab("📊 Portfolio"):
        # Refresh button
        refresh_btn = gr.Button("🔄 Refresh", size="sm")
        
        # Summary cards
        with gr.Row():
            total_value = gr.Number(
                label="💰 Total Value (SCRT)",
                precision=2,
                interactive=False
            )
            available = gr.Number(
                label="💵 Available (SCRT)",
                precision=2,
                interactive=False
            )
            staked = gr.Number(
                label="🏛️ Staked (SCRT)",
                precision=2,
                interactive=False
            )
            rewards = gr.Number(
                label="🎁 Rewards (SCRT)",
                precision=2,
                interactive=False
            )
        
        # Delegations table
        gr.Markdown("### Your Delegations")
        delegations_table = gr.Dataframe(
            headers=["Validator", "Amount (SCRT)", "Rewards", "Status"],
            datatype=["str", "number", "number", "str"],
            interactive=False
        )
        
        # Rewards by validator
        gr.Markdown("### Rewards Breakdown")
        rewards_table = gr.Dataframe(
            headers=["Validator", "Rewards (SCRT)", "APR"],
            datatype=["str", "number", "str"],
            interactive=False
        )
        
        # Actions
        with gr.Row():
            withdraw_rewards_btn = gr.Button(
                "Withdraw All Rewards",
                variant="primary"
            )
            manage_staking_btn = gr.Button(
                "Manage Staking"
            )
        
        # Load data function
        async def load_portfolio():
            """Load and format portfolio data."""
            data = await get_portfolio_data(mcp_bridge)
            
            # Format delegations
            delegations_data = []
            for d in data['delegations']:
                delegations_data.append([
                    d['validator_name'],
                    float(d['amount']) / 1_000_000,
                    float(d['rewards']) / 1_000_000,
                    d['status']
                ])
            
            # Format rewards
            rewards_data = []
            for r in data['rewards_by_validator']:
                rewards_data.append([
                    r['validator_name'],
                    float(r['amount']) / 1_000_000,
                    f"{r['apr']}%"
                ])
            
            return (
                data['total'] / 1_000_000,
                data['available'] / 1_000_000,
                data['staked'] / 1_000_000,
                data['rewards'] / 1_000_000,
                delegations_data,
                rewards_data
            )
        
        # Events
        refresh_btn.click(
            load_portfolio,
            outputs=[
                total_value,
                available,
                staked,
                rewards,
                delegations_table,
                rewards_table
            ]
        )
        
        # Auto-load on tab open
        gr.on("load", load_portfolio, outputs=[...])
```

**Deliverables**:
- ✅ Portfolio dashboard complete
- ✅ All data displaying correctly
- ✅ Refresh working
- ✅ Actions functional

---

#### **Task 7.3: Testing** (1 hour)

**Scope**:
- Test with testnet data
- Verify calculations
- Test edge cases (no delegations, no rewards)

**Deliverables**:
- ✅ Dashboard tested
- ✅ Edge cases handled
- ✅ UX smooth

---

### **Day 8 (Nov 21) - Validators Tab**

**Total Effort**: 7 hours

#### **Task 8.1: Validator Data** (2 hours)

**Scope**:
- Fetch validator list
- Calculate metrics (APR, score)
- Sort and filter

**Key Functions**:
```python
async def get_validators_data(mcp_bridge: MCPBridge) -> list[dict]:
    """Get and enrich validator data."""
    validators = await mcp_bridge.execute_tool("secret_get_validators", {})
    
    # Enrich with calculated metrics
    enriched = []
    for v in validators['validators']:
        enriched.append({
            "name": v['description']['moniker'],
            "address": v['operator_address'],
            "voting_power": float(v['tokens']) / 1_000_000,
            "voting_power_pct": calculate_percentage(v['tokens'], total_tokens),
            "commission": float(v['commission']['commission_rates']['rate']) * 100,
            "uptime": 99.9,  # Would need to fetch from chain
            "apr": estimate_apr(v),
            "delegator_count": v.get('delegator_shares', 0),
            "status": v['status'],
            "score": calculate_validator_score(v)
        })
    
    # Sort by score
    enriched.sort(key=lambda x: x['score'], reverse=True)
    return enriched

def calculate_validator_score(validator: dict) -> float:
    """Calculate validator quality score (0-10)."""
    score = 10.0
    
    # Penalize high voting power (centralization)
    if voting_power_pct > 5:
        score -= 2
    
    # Penalize high commission
    if commission > 10:
        score -= 1
    elif commission < 3:
        score -= 0.5  # Too low is suspicious
    
    # Reward high uptime
    if uptime < 99:
        score -= 2
    
    return max(0, score)
```

**Deliverables**:
- ✅ Validator data enriched
- ✅ Scoring algorithm working
- ✅ Sorting/filtering ready

---

#### **Task 8.2: Validators UI** (4 hours)

**File**: `src/ui/validators_tab.py`

**Scope**:
- Validator comparison table
- Sorting and filtering
- Delegation action

**Component Structure**:
```python
def create_validators_tab(mcp_bridge: MCPBridge):
    """Create validators tab."""
    
    with gr.Tab("🏛️ Validators"):
        # Refresh
        refresh_btn = gr.Button("🔄 Refresh", size="sm")
        
        # Filters
        with gr.Row():
            status_filter = gr.Radio(
                choices=["All", "Active", "Inactive"],
                label="Status",
                value="Active"
            )
            sort_by = gr.Dropdown(
                choices=["Score", "Voting Power", "Commission", "APR"],
                label="Sort By",
                value="Score"
            )
        
        # Validators table
        validators_table = gr.Dataframe(
            headers=[
                "Validator",
                "Voting Power (%)",
                "Commission (%)",
                "APR (%)",
                "Score",
                "Status"
            ],
            datatype=["str", "number", "number", "number", "number", "str"],
            interactive=False,
            wrap=True
        )
        
        # Selection and delegation
        with gr.Row():
            selected_validator = gr.Textbox(
                label="Selected Validator",
                interactive=False
            )
            delegate_amount = gr.Number(
                label="Amount to Delegate (SCRT)",
                minimum=1,
                value=100
            )
            delegate_btn = gr.Button(
                "Delegate",
                variant="primary"
            )
        
        # Load validators
        async def load_validators(status, sort):
            """Load validators with filters."""
            validators = await get_validators_data(mcp_bridge)
            
            # Apply status filter
            if status != "All":
                validators = [v for v in validators if v['status'] == status]
            
            # Apply sort
            if sort == "Voting Power":
                validators.sort(key=lambda x: x['voting_power'], reverse=True)
            elif sort == "Commission":
                validators.sort(key=lambda x: x['commission'])
            elif sort == "APR":
                validators.sort(key=lambda x: x['apr'], reverse=True)
            # Default is already sorted by score
            
            # Format for table
            table_data = []
            for v in validators:
                table_data.append([
                    v['name'],
                    round(v['voting_power_pct'], 2),
                    round(v['commission'], 2),
                    round(v['apr'], 2),
                    round(v['score'], 1),
                    v['status']
                ])
            
            return table_data
        
        # Events
        refresh_btn.click(
            load_validators,
            inputs=[status_filter, sort_by],
            outputs=[validators_table]
        )
        
        status_filter.change(
            load_validators,
            inputs=[status_filter, sort_by],
            outputs=[validators_table]
        )
        
        sort_by.change(
            load_validators,
            inputs=[status_filter, sort_by],
            outputs=[validators_table]
        )
        
        # Delegate action
        async def delegate_to_validator(amount):
            """Delegate to selected validator."""
            # Execute delegation
            # Return success message
        
        delegate_btn.click(
            delegate_to_validator,
            inputs=[delegate_amount],
            outputs=[gr.Textbox(label="Result")]
        )
```

**Deliverables**:
- ✅ Validators table complete
- ✅ Filtering/sorting working
- ✅ Delegation integrated

---

#### **Task 8.3: Testing** (1 hour)

**Scope**:
- Test with live testnet validators
- Verify scoring accuracy
- Test delegation flow

**Deliverables**:
- ✅ Validators tab tested
- ✅ All features working

---

### **Day 9 (Nov 22) - Settings Tab**

**Total Effort**: 6 hours

#### **Task 9.1: Wallet Management** (3 hours)

**File**: `src/ui/settings_tab.py`

**Scope**:
- Wallet creation UI
- Wallet import UI
- Wallet switching
- Display active wallet info

**Component Structure**:
```python
def create_settings_tab(mcp_bridge: MCPBridge):
    """Create settings tab."""
    
    with gr.Tab("⚙️ Settings"):
        # Active wallet display
        gr.Markdown("### 🔑 Active Wallet")
        with gr.Row():
            wallet_address = gr.Textbox(
                label="Address",
                interactive=False
            )
            wallet_balance = gr.Number(
                label="Balance (SCRT)",
                interactive=False
            )
        
        # Wallet actions
        with gr.Accordion("Wallet Management", open=False):
            # Create new wallet
            gr.Markdown("#### Create New Wallet")
            with gr.Row():
                new_wallet_name = gr.Textbox(
                    label="Wallet Name",
                    placeholder="my-wallet"
                )
                create_wallet_btn = gr.Button("Create", variant="primary")
            
            mnemonic_display = gr.Textbox(
                label="⚠️ SAVE THIS MNEMONIC (shown only once)",
                type="password",
                interactive=False,
                visible=False
            )
            
            # Import wallet
            gr.Markdown("#### Import Wallet")
            with gr.Row():
                import_wallet_name = gr.Textbox(
                    label="Wallet Name"
                )
                import_mnemonic = gr.Textbox(
                    label="Mnemonic (24 words)",
                    type="password"
                )
                import_wallet_btn = gr.Button("Import", variant="primary")
            
            # Switch wallet
            gr.Markdown("#### Switch Wallet")
            wallet_list = gr.Dropdown(
                label="Available Wallets",
                choices=[]
            )
            switch_wallet_btn = gr.Button("Switch")
        
        # Network settings
        gr.Markdown("### 🌐 Network")
        network_selector = gr.Radio(
            choices=["Testnet (pulsar-3)", "Mainnet (secret-4)"],
            label="Active Network",
            value="Testnet (pulsar-3)"
        )
        
        # Appearance
        gr.Markdown("### 🎨 Appearance")
        theme_selector = gr.Radio(
            choices=["Dark", "Light"],
            label="Theme",
            value="Dark"
        )
        
        # About
        gr.Markdown("### ℹ️ About")
        gr.Markdown("""
        **SecretAgent v1.0**
        
        The first AI agent for privacy-preserving blockchain operations.
        
        - Built with Gradio 6 & MCP
        - Powered by Secret Network
        - Created for MCP's 1st Birthday Hackathon
        
        [GitHub](https://github.com/your-repo) | [Documentation](https://your-docs)
        """)
        
        # Event handlers
        async def create_wallet(name):
            """Create new wallet."""
            result = await mcp_bridge.execute_tool("secret_create_wallet", {"name": name})
            return (
                result['address'],
                result['mnemonic'],
                gr.update(visible=True)
            )
        
        create_wallet_btn.click(
            create_wallet,
            inputs=[new_wallet_name],
            outputs=[wallet_address, mnemonic_display, mnemonic_display]
        )
```

**Deliverables**:
- ✅ Wallet management UI complete
- ✅ Create/import/switch working
- ✅ Network switching functional
- ✅ Theme toggle working

---

#### **Task 9.2: Integration** (2 hours)

**Scope**:
- Connect settings to app state
- Persist settings (localStorage via Gradio)
- Test all settings changes

**Deliverables**:
- ✅ Settings persistent
- ✅ Changes reflected across app

---

#### **Task 9.3: Testing** (1 hour)

**Scope**:
- Test wallet operations
- Test network switching
- Verify security (mnemonic handling)

**Deliverables**:
- ✅ Settings tab tested
- ✅ Security verified

---

### **Day 10 (Nov 23) - Main App Integration**

**Total Effort**: 8 hours

#### **Task 10.1: Main App File** (4 hours)

**File**: `app.py`

**Scope**:
- Integrate all tabs
- Initialize all components
- Setup event routing
- Add loading states

**Main App Structure**:
```python
import gradio as gr
from src.agent.orchestrator import AgentOrchestrator
from src.llm.ollama_client import OllamaClient
from src.knowledge.retriever import KnowledgeRetriever
from src.utils.mcp_bridge import MCPBridge
from src.ui.theme import create_secret_theme
from src.ui.chat_tab import create_chat_tab
from src.ui.portfolio_tab import create_portfolio_tab
from src.ui.validators_tab import create_validators_tab
from src.ui.settings_tab import create_settings_tab
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Initialize components
llm_client = OllamaClient(
    base_url=os.getenv("OLLAMA_URL"),
    model=os.getenv("OLLAMA_MODEL")
)

knowledge_retriever = KnowledgeRetriever(
    chromadb_url=os.getenv("CHROMADB_URL"),
    redis_url=os.getenv("REDIS_URL")
)

mcp_bridge = MCPBridge()

orchestrator = AgentOrchestrator(
    llm_client=llm_client,
    knowledge_retriever=knowledge_retriever,
    mcp_bridge=mcp_bridge
)

# Create Gradio app
with gr.Blocks(
    theme=create_secret_theme(),
    title="SecretAgent - Privacy-First Blockchain AI",
    css="""
    .gradio-container {
        max-width: 1400px !important;
    }
    """
) as demo:
    # Header
    gr.Markdown("""
    # 🔐 SecretAgent
    ### Your Privacy-First Blockchain AI Assistant
    
    Ask questions, execute operations, and manage your Secret Network portfolio with AI.
    """)
    
    # Tabs
    with gr.Tabs():
        create_chat_tab(orchestrator)
        create_portfolio_tab(mcp_bridge)
        create_validators_tab(mcp_bridge)
        create_settings_tab(mcp_bridge)
    
    # Footer
    gr.Markdown("""
    ---
    Built with ❤️ for Secret Network | Powered by Gradio 6 & MCP | [GitHub](https://github.com/your-repo)
    """)

# Launch
if __name__ == "__main__":
    demo.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", 7860)),
        share=os.getenv("GRADIO_SHARE", "false").lower() == "true"
    )
```

**Deliverables**:
- ✅ Main app integrated
- ✅ All tabs working together
- ✅ Launches successfully

---

#### **Task 10.2: Error Handling** (2 hours)

**Scope**:
- Global error handling
- User-friendly error messages
- Logging configuration
- Graceful degradation

**Error Handlers**:
```python
# In app.py

def handle_error(error: Exception) -> str:
    """Global error handler."""
    logger.error(f"Application error: {error}", exc_info=True)
    
    if isinstance(error, ConnectionError):
        return "Unable to connect to blockchain. Please check your network."
    elif isinstance(error, ValueError):
        return "Invalid input. Please check your parameters."
    else:
        return "An unexpected error occurred. Please try again."

# Wrap critical functions
try:
    result = await function()
except Exception as e:
    return handle_error(e)
```

**Deliverables**:
- ✅ Error handling comprehensive
- ✅ Logging configured
- ✅ User experience graceful

---

#### **Task 10.3: End-to-End Testing** (2 hours)

**Scope**:
- Test complete user journeys
- Test across all tabs
- Verify data consistency
- Performance testing

**Test Journeys**:
1. **New User Onboarding**
   - Open app
   - Chat: "What is Secret Network?"
   - Settings: Create wallet
   - Chat: "Check my balance"

2. **Staking Journey**
   - Portfolio: View current staking
   - Validators: Browse validators
   - Chat: "Stake 100 SCRT to top validator"
   - Portfolio: Verify delegation

3. **Portfolio Management**
   - Portfolio: View overview
   - Chat: "Withdraw all rewards"
   - Portfolio: Refresh and verify

**Deliverables**:
- ✅ All journeys tested
- ✅ No blocking bugs
- ✅ Performance acceptable (<3s responses)

---

## **PHASE 4: POLISH & SUBMISSION** (Days 11-17)

### **Day 11-12 (Nov 24-25) - Polish & Testing**

**Total Effort**: 14 hours

#### **Major Tasks**:
- **UI/UX Polish** (4 hours)
  - Improve loading states
  - Add tooltips and help text
  - Improve mobile responsiveness
  - Add keyboard shortcuts
  - Polish animations

- **Performance Optimization** (4 hours)
  - Profile slow operations
  - Implement caching strategy
  - Optimize knowledge retrieval
  - Reduce LLM latency

- **Comprehensive Testing** (4 hours)
  - Unit tests for new code
  - Integration tests for all flows
  - Browser compatibility testing
  - Mobile testing

- **Bug Fixes** (2 hours)
  - Fix any discovered bugs
  - Improve error handling
  - Edge case handling

**Deliverables**:
- ✅ App polished and professional
- ✅ Performance optimized
- ✅ All tests passing
- ✅ No critical bugs

---

### **Day 13 (Nov 26) - Documentation**

**Total Effort**: 8 hours

#### **Task 13.1: README** (4 hours)

Create comprehensive README.md covering:
- Project overview (500 words)
- Features list with screenshots
- Architecture diagram
- Setup instructions (step-by-step)
- Usage guide with examples
- MCP integration explanation
- Knowledge base documentation
- API documentation
- Troubleshooting guide
- Future roadmap
- Contributing guidelines
- License

**Deliverables**:
- ✅ Complete README (3,000+ words)
- ✅ Screenshots embedded
- ✅ Setup tested by following docs

---

#### **Task 13.2: Additional Docs** (2 hours)

- **ARCHITECTURE.md**: Technical deep-dive
- **KNOWLEDGE_BASE.md**: Knowledge system explanation
- **MCP_INTEGRATION.md**: How MCP-SCRT is integrated
- **API.md**: API documentation

**Deliverables**:
- ✅ All documentation complete
- ✅ Technical details covered

---

#### **Task 13.3: Code Comments** (2 hours)

- Add docstrings to all modules
- Add inline comments for complex logic
- Update type hints
- Verify code quality

**Deliverables**:
- ✅ Code well-documented
- ✅ Ready for review

---

### **Day 14 (Nov 27) - Demo Video**

**Total Effort**: 8 hours

#### **Task 14.1: Script & Planning** (2 hours)

**Video Script** (5 minutes):

```
[0:00-0:30] Introduction
- Hook: "Secret Network + AI = The Future of Private DeFi"
- Problem: Blockchain is complex, privacy is important
- Solution: SecretAgent - AI assistant for Secret Network

[0:30-1:30] Knowledge System Demo
- Ask: "What is Secret Network?"
- Show: Natural answer with sources
- Ask: "How does privacy work?"
- Highlight: Educational value

[1:30-3:00] Autonomous Operations Demo
- Say: "Stake 100 SCRT to the best validator"
- Show: Agent analyzes validators, recommends, executes
- Highlight: Autonomous decision-making
- Show: Transaction success

[3:00-4:00] Portfolio & Dashboard
- Show: Portfolio overview
- Show: Validator comparison
- Show: Rewards tracking
- Highlight: Complete DeFi management

[4:00-4:45] Privacy Focus
- Explain: Privacy-first design
- Show: Encrypted transactions
- Highlight: Secret Network benefits

[4:45-5:00] Conclusion & CTA
- Recap: Education + Execution + Privacy
- Built with: Gradio 6 & MCP
- CTA: Try it on Hugging Face Space
```

**Deliverables**:
- ✅ Script finalized
- ✅ Demo scenarios prepared
- ✅ Recording environment ready

---

#### **Task 14.2: Recording** (3 hours)

**Setup**:
- Clean desktop
- Browser in fullscreen
- Test audio levels
- Prepare demo data (testnet tokens)

**Recording**:
- Record in 1080p
- Use OBS Studio or SimpleScreenRecorder
- Record with narration
- Multiple takes if needed

**Deliverables**:
- ✅ Raw video footage
- ✅ Audio clear
- ✅ All features demonstrated

---

#### **Task 14.3: Editing & Upload** (3 hours)

**Editing** (Kdenlive or similar):
- Cut and trim clips
- Add intro slide (Title, logo)
- Add transitions between sections
- Add text overlays for key points
- Add outro slide (Links, CTA)
- Export in HD (1080p, H.264)

**Upload**:
- Upload to YouTube
- Set title: "SecretAgent - Privacy-First Blockchain AI Assistant | MCP Hackathon"
- Add description with links
- Add timestamps
- Make public

**Deliverables**:
- ✅ Professional demo video
- ✅ Uploaded to YouTube
- ✅ Link ready for submission

---

### **Day 15 (Nov 28) - Deployment**

**Total Effort**: 8 hours

#### **Task 15.1: Pre-Deployment Testing** (2 hours)

- Fresh install test
- Run through all demo scenarios
- Test on different browsers
- Test mobile responsiveness
- Verify all links work

**Deliverables**:
- ✅ All tests passing
- ✅ Ready for deployment

---

#### **Task 15.2: Hugging Face Space** (5 hours)

**Setup**:
- Create Hugging Face account (if needed)
- Create new Space
- Configure Space settings (Gradio SDK, Python 3.13)

**Deployment**:
```bash
# Add HF as remote
git remote add hf https://huggingface.co/spaces/username/secret-agent

# Push code
git push hf main

# Configure Space
# - Add secrets (environment variables)
# - Set hardware (CPU should be fine for UI)
# - Enable persistence if needed
```

**Configuration**:
- `README.md` with Space metadata
- Environment variables in Space settings
- Test remote service connectivity from HF

**Potential Issues**:
- Network connectivity to remote Ollama/ChromaDB
  - Solution: May need to deploy Ollama on HF Space or use public endpoint
- Environment variable configuration
- Gradio version compatibility

**Deliverables**:
- ✅ Live Hugging Face Space
- ✅ All features functional
- ✅ Public URL available

---

#### **Task 15.3: Troubleshooting** (1 hour)

- Fix any deployment issues
- Optimize for HF environment
- Verify all features working

**Deliverables**:
- ✅ Deployment stable
- ✅ No critical issues

---

### **Day 16 (Nov 29) - Final Polish**

**Total Effort**: 6 hours

#### **Major Tasks**:
- **Final Review** (2 hours)
  - Review all documentation
  - Test all links
  - Check for typos
  - Verify completeness

- **Last-Minute Fixes** (2 hours)
  - Fix any issues found
  - Update documentation
  - Final commit

- **Social Media Prep** (2 hours)
  - Create engaging post
  - Record demo GIF (30 seconds)
  - Write post copy
  - Prepare hashtags

**Deliverables**:
- ✅ All polish complete
- ✅ Documentation finalized
- ✅ Social media ready

---

### **Day 17 (Nov 30) - SUBMISSION DAY** 🚀

**Total Effort**: 8 hours

#### **Task 17.1: Social Media** (2 hours)

**Post Template**:
```
🔐 Introducing SecretAgent - The first AI agent for privacy-preserving blockchain!

Built for #MCPHackathon, SecretAgent combines:
✨ Natural language blockchain operations
🧠 Autonomous decision-making (staking, governance)
📚 Interactive learning about Secret Network
🔒 Privacy-first DeFi portfolio management

🚀 Try it: [Space URL]
📺 Demo: [YouTube URL]
💻 Code: [GitHub URL]

Built with @Gradio 6 & Model Context Protocol
Powered by @SecretNetwork - the confidential computing layer of Web3

#SecretNetwork #Gradio #AI #Blockchain #Privacy #DeFi #MCP

What privacy-preserving dApps would you build with this?👇
```

**Platforms**:
- Twitter/X
- LinkedIn
- Discord (MCP Hackathon channel)

**Deliverables**:
- ✅ Posted on all platforms
- ✅ Links captured
- ✅ Engagement started

---

#### **Task 17.2: Official Submission** (3 hours)

**Checklist**:
- [ ] Join MCP-1st-Birthday organization (Request to join)
- [ ] Submit Space to organization
- [ ] Add track tag to Space README: `agent-app-track-productivity`
- [ ] Add social media post link to README
- [ ] Add demo video link to README
- [ ] Verify all requirements met
- [ ] Submit before 11:59 PM UTC
- [ ] Screenshot confirmation

**README Front Matter**:
```yaml
---
title: SecretAgent
emoji: 🔐
colorFrom: purple
colorTo: cyan
sdk: gradio
sdk_version: 6.0.0
app_file: app.py
pinned: false
tags:
  - agent-app-track-productivity
  - mcp
  - secret-network
  - blockchain
  - privacy
---
```

**Deliverables**:
- ✅ Submission complete
- ✅ All requirements met
- ✅ Confirmation received

---

#### **Task 17.3: Celebration & Monitoring** (3 hours)

- Monitor Space for issues
- Respond to early feedback
- Engage with community
- Celebrate! 🎉

**Deliverables**:
- ✅ Monitoring setup
- ✅ Ready to support users
- ✅ DONE! 🏆

---

## 📊 **FINAL EFFORT SUMMARY**

| Phase                        | Days   | Hours    |
| ---------------------------- | ------ | -------- |
| **Phase 1: Foundation**      | 2      | 16h      |
| **Phase 2: Agent Core**      | 3      | 24h      |
| **Phase 3: Gradio UI**       | 5      | 37h      |
| **Phase 4: Polish & Submit** | 7      | 52h      |
| **TOTAL**                    | **17** | **129h** |

**Average**: 7.6 hours/day  
**Buffer**: ~7 hours remaining for unexpected issues

---

## 🎯 **SUCCESS METRICS**

### **Completion Criteria**
- [ ] All 7 knowledge topics embedded
- [ ] Chat interface with streaming
- [ ] Portfolio dashboard functional
- [ ] Validator comparison working
- [ ] Wallet management complete
- [ ] Autonomous staking working
- [ ] Demo video published
- [ ] Documentation complete
- [ ] Deployed to Hugging Face
- [ ] Submitted before deadline

### **Quality Criteria**
- [ ] 637+ tests passing (from POC + new tests)
- [ ] Response time < 3s average
- [ ] Mobile-responsive
- [ ] No critical bugs
- [ ] Professional appearance

---

## 🚀 **READY TO BUILD!**

This plan leverages the production-ready MCP-SCRT POC and focuses effort on:
1. **Knowledge Base** (2 days)
2. **Agent Layer** (3 days)
3. **Gradio UI** (5 days)
4. **Polish & Submission** (7 days)

Total: **17 days**, **~130 hours**, **1 person**

**Next Step**: Confirm this plan, then execute Day 1! 🎯