# 🔐 SecretAgent

### Your Privacy-First Blockchain AI Assistant

[![Gradio](https://img.shields.io/badge/Gradio-6.0-orange)](https://gradio.app)
[![MCP](https://img.shields.io/badge/MCP-Enabled-blue)](https://modelcontextprotocol.io)
[![Secret Network](https://img.shields.io/badge/Secret%20Network-Testnet-purple)](https://scrt.network)
[![Python](https://img.shields.io/badge/Python-3.13-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**SecretAgent** is the first AI assistant that both educates you about privacy-preserving blockchain technology AND autonomously executes confidential operations on Secret Network. Built for the [MCP's 1st Birthday Hackathon](https://huggingface.co/MCP-1st-Birthday).

🎥 **[Watch Demo Video](#)** | 🚀 **[Try Live Demo](#)** | 💻 **[View Code](https://github.com/alexh-scrt/secretagent)**

---

## 🌟 **What Makes SecretAgent Special?**

### **Education Meets Execution**
Most blockchain tools either teach OR execute. SecretAgent does both:
- 💡 **Ask Questions**: "What is Secret Network?" → Get comprehensive, sourced answers
- ⚡ **Execute Operations**: "Stake 100 SCRT to best validator" → Autonomous execution with smart recommendations
- 🔄 **Hybrid Mode**: "Explain staking and stake 50 SCRT" → Learn while you do

### **Privacy-First, Always**
Built on Secret Network, the confidential computing layer of Web3:
- 🔐 Encrypted transactions (input, state, output)
- 🛡️ MEV-resistant by design
- 🎭 Programmable privacy for smart contracts

### **Autonomous Intelligence**
Powered by Llama 3.3 70B and advanced RAG:
- 🤖 Multi-step planning and execution
- 🎯 Smart validator analysis and recommendations
- 📊 Autonomous portfolio optimization
- 🗳️ Governance proposal summarization

---

## ✨ **Key Features**

### 🧠 **Intelligent Conversational Interface**
- Natural language interaction with Secret Network blockchain
- Streaming AI responses with real-time thinking
- Context-aware conversation history
- Educational explanations with source citations

### 📚 **Comprehensive Knowledge Base**
7 expertly curated topics covering:
- **Fundamentals**: What is Secret Network? TEE, architecture, use cases
- **Privacy Technology**: Intel SGX, encryption mechanisms, MEV resistance
- **Tokens**: SCRT, SNIP-20, wrapping, viewing keys, query permits
- **Staking**: Delegation, validator selection, rewards, unbonding
- **Smart Contracts**: Secret Contracts, CosmWasm, lifecycle, privacy patterns
- **Security**: Best practices, wallet safety, scam prevention
- **FAQ**: 25+ common questions with clear answers

Powered by:
- **ChromaDB**: Vector embeddings for semantic search
- **Redis**: Intelligent caching for fast responses
- **Hybrid Retrieval**: Vector similarity + keyword matching + re-ranking

### ⚡ **60+ Blockchain Operations**
Complete MCP-SCRT integration with 11 tool categories:

| Category            | Operations                          | Examples                                |
| ------------------- | ----------------------------------- | --------------------------------------- |
| **Network** (4)     | Configuration, health checks        | Switch networks, check gas prices       |
| **Wallet** (6)      | Create, import, manage              | HD wallet creation with BIP44           |
| **Bank** (5)        | Balance, transfers                  | Check balance, send SCRT tokens         |
| **Blockchain** (5)  | Block queries, node info            | Query latest blocks, sync status        |
| **Account** (3)     | Account info, transactions          | Get account details, tx history         |
| **Transaction** (5) | Query, search, simulate             | Estimate gas, simulate before execution |
| **Staking** (8)     | Delegate, undelegate, redelegate    | Smart validator selection               |
| **Rewards** (4)     | Check, withdraw, configure          | Compound rewards automatically          |
| **Governance** (6)  | Proposals, voting                   | AI-powered proposal summaries           |
| **Contracts** (10)  | Upload, instantiate, execute, query | Full contract lifecycle                 |
| **IBC** (4)         | Cross-chain transfers               | Privacy across Cosmos chains            |

### 🎯 **Autonomous Decision-Making**

#### **Smart Validator Selection**
```
You: "Stake 100 SCRT to the best validator"

Agent: 
→ Analyzes all validators
→ Scores by: decentralization, commission, uptime, reputation
→ Recommends: "SecretNodes" (Score: 9.2/10)
→ Explains: "5% commission, 99.9% uptime, good decentralization"
→ Confirms with you
→ Executes delegation
✅ Transaction: secret1tx...
```

**Scoring Algorithm**:
- ✅ **Decentralization**: Penalizes high voting power (>5%)
- ✅ **Commission**: Favors 5-10% range (not too high, not suspiciously low)
- ✅ **Uptime**: Requires 99%+ uptime
- ✅ **Community**: Factors in delegator count and reputation

#### **Multi-Step Planning**
```
You: "Maximize my staking rewards"

Agent Plans:
1. Check current delegations
2. Calculate rewards across validators  
3. Identify underperforming validators
4. Recommend redelegation strategy
5. Execute rebalancing
6. Set up auto-compound
```

#### **Governance Intelligence**
```
You: "What proposals should I vote on?"

Agent:
→ Fetches active proposals
→ Summarizes each in plain language using LLM
→ Analyzes potential impact
→ Shows your voting power
→ Suggests informed vote
→ Executes vote with confirmation
```

### 📊 **Portfolio Dashboard**

**Overview Cards**:
- 💰 Total Value (SCRT)
- 💵 Available Balance
- 🏛️ Staked Amount
- 🎁 Pending Rewards

**Delegations Table**:
| Validator   | Amount (SCRT) | Rewards | Status | Actions                |
| ----------- | ------------- | ------- | ------ | ---------------------- |
| SecretNodes | 5,000         | 12.34   | Active | Redelegate, Undelegate |
| Validator X | 3,000         | 8.21    | Active | Redelegate, Undelegate |

**Rewards Breakdown**:
- Per-validator rewards tracking
- Estimated APR calculations
- One-click withdraw all rewards
- Auto-compound options (coming soon)

### 🏛️ **Validator Intelligence**

**Comparison Table** with real-time data:
| Validator   | Voting Power | Commission | APR   | Score | Status |
| ----------- | ------------ | ---------- | ----- | ----- | ------ |
| SecretNodes | 3.2%         | 5.0%       | 18.5% | 9.2   | Active |
| Validator X | 8.1%         | 7.5%       | 17.8% | 7.8   | Active |

**Smart Filtering & Sorting**:
- Filter by status (Active/Inactive)
- Sort by: Score, Voting Power, Commission, APR
- Search by name or address

**Quick Delegation**:
- Click validator → Enter amount → Delegate
- Automatic validation and confirmation

### ⚙️ **Wallet & Settings Management**

#### **Multi-Wallet Support**
- 🆕 **Create**: HD wallets with BIP32/BIP44/SLIP10
- 📥 **Import**: From 12/24-word mnemonic
- 🔄 **Switch**: Seamlessly between multiple wallets
- 🔐 **Security**: Encrypted in-memory storage only

#### **Network Configuration**
- 🧪 **Testnet**: pulsar-3 (for development)
- 🌐 **Mainnet**: secret-4 (coming soon)
- ⚙️ **Custom**: Configure custom endpoints

#### **Appearance**
- 🌙 **Dark Mode**: Privacy-focused default theme
- ☀️ **Light Mode**: For daytime use
- 🎨 **Custom Theme**: Purple/Cyan privacy aesthetic

---

## 🏗️ **Architecture**

### **System Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                  GRADIO 6 WEB INTERFACE                     │
│                    (Mobile-Responsive)                      │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │   ChatBot   │  │  Portfolio  │  │  Validators         ││
│  │  (Primary)  │  │  Dashboard  │  │  Settings           ││
│  └─────────────┘  └─────────────┘  └─────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              AGENT ORCHESTRATION LAYER                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Intent Classifier (Llama 3.3:70B via Ollama)       │  │
│  │  → question | command | hybrid                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────┐           ┌──────────────────────┐  │
│  │  Multi-Step      │           │  Response Formatter  │  │
│  │  Planner         │           │  (Markdown, Citations)│  │
│  └──────────────────┘           └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
            ↙                                    ↘
┌──────────────────────────┐         ┌─────────────────────────┐
│  KNOWLEDGE BASE SYSTEM   │         │  MCP-SCRT SERVER        │
│                          │         │  (60 Blockchain Tools)  │
│  ┌────────────────────┐  │         │                         │
│  │  ChromaDB          │  │         │  • Network (4)          │
│  │  (Vector Search)   │  │         │  • Wallet (6)           │
│  │                    │  │         │  • Bank (5)             │
│  │  7 Topics          │  │         │  • Blockchain (5)       │
│  │  ~5,000 words      │  │         │  • Account (3)          │
│  │  Semantic Search   │  │         │  • Transaction (5)      │
│  └────────────────────┘  │         │  • Staking (8)          │
│                          │         │  • Rewards (4)          │
│  ┌────────────────────┐  │         │  • Governance (6)       │
│  │  Redis Cache       │  │         │  • Contracts (10)       │
│  │  (5 min TTL)       │  │         │  • IBC (4)              │
│  └────────────────────┘  │         │                         │
└──────────────────────────┘         │  637 Tests Passing ✅   │
                                     └─────────────────────────┘
                                                ↓
                        ┌─────────────────────────────────────┐
                        │  SECRET NETWORK BLOCKCHAIN          │
                        │  (Testnet: pulsar-3)                │
                        │                                     │
                        │  • Encrypted Transactions           │
                        │  • TEE (Intel SGX)                  │
                        │  • IBC Interoperability             │
                        │  • MEV Resistance                   │
                        └─────────────────────────────────────┘
```

### **Technology Stack**

| Layer          | Technology             | Purpose                                      |
| -------------- | ---------------------- | -------------------------------------------- |
| **Frontend**   | Gradio 6               | Modern, mobile-first web UI with PWA support |
| **LLM**        | Llama 3.3 70B (Ollama) | Intent classification, response generation   |
| **Vector DB**  | ChromaDB               | Knowledge base semantic search               |
| **Cache**      | Redis                  | Response caching, session management         |
| **Graph DB**   | Neo4j                  | Future: Relationship mapping (not yet used)  |
| **MCP Server** | mcp-scrt               | 60 blockchain operation tools                |
| **Blockchain** | Secret Network         | Privacy-preserving smart contracts           |
| **Backend**    | Python 3.13            | Application logic, orchestration             |

### **Data Flow**

**Knowledge Query Flow**:
```
User Message
    ↓
Intent Classifier (LLM) → "question"
    ↓
Knowledge Retriever
    ↓
Redis Cache Check → Cache Hit? → Return
    ↓ Cache Miss
ChromaDB Vector Search (top 5 chunks)
    ↓
Re-ranking & Context Assembly
    ↓
LLM Response Generation (RAG)
    ↓
Response Formatter (Markdown + Citations)
    ↓
Gradio UI (Streaming Display)
```

**Command Execution Flow**:
```
User Message
    ↓
Intent Classifier (LLM) → "command"
    ↓
Entity Extraction (amount, address, action)
    ↓
Tool Mapper → Identify MCP tool(s)
    ↓
Multi-Step Planner (if complex)
    ↓
Confirmation Check → Risk assessment
    ↓
Tool Executor → MCP Bridge → MCP-SCRT
    ↓
Secret Network (Transaction)
    ↓
Result Formatter
    ↓
Gradio UI (Success message + next steps)
```

**Hybrid Flow**:
```
User Message: "Explain staking and stake 50 SCRT"
    ↓
Intent Classifier → "hybrid"
    ↓
    ├─→ Knowledge Retriever (Explain)
    │       ↓
    │   Generate Explanation
    │       ↓
    │   Display to User
    │
    └─→ Tool Executor (Execute)
            ↓
        Stake 50 SCRT
            ↓
        Display Result
            ↓
    Combine Both Responses
```

---

## 🚀 **Getting Started**

### **Prerequisites**

- **Python**: 3.13 or higher
- **Remote Services** (already configured):
  - Ollama server with llama3.3:70b
  - ChromaDB server
  - Redis server
  - (Optional) Neo4j server
- **Secret Network**: Testnet access (faucet available)

### **Installation**

#### **1. Clone Repository**
```bash
git clone https://github.com/alexh-scrt/secret-agent.git
cd secret-agent
```

#### **2. Set Up Environment**
```bash
# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install MCP-SCRT (production-ready POC)
cd mcp-scrt
pip install -e ".[dev]"
cd ..
```

#### **3. Configure Environment**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
# Secret Network
SECRET_NETWORK=testnet
SECRET_TESTNET_URL=https://lcd.testnet.secretsaturn.net
SECRET_TESTNET_CHAIN_ID=pulsar-3

# Remote Services (update with your server IPs)
OLLAMA_URL=http://your-ollama-server:11434
OLLAMA_MODEL=llama3.3:70b
CHROMADB_URL=http://your-chromadb-server:8000
REDIS_URL=redis://your-redis-server:6379

# Gradio
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
```

#### **4. Test Connections**
```bash
python scripts/test_connections.py
```

Expected output:
```
Testing Ollama at http://your-server:11434...
✅ Ollama connected - Model: llama3.3:70b

Testing ChromaDB at http://your-server:8000...
✅ ChromaDB connected

Testing Redis at redis://your-server:6379...
✅ Redis connected

=== Connection Test Summary ===
ollama: ✅ PASS
chromadb: ✅ PASS
redis: ✅ PASS
```

#### **5. Initialize Knowledge Base**
```bash
python scripts/setup_knowledge.py
```

This will:
- Parse all 7 knowledge markdown files
- Generate embeddings using sentence-transformers
- Store in ChromaDB with metadata
- Verify retrieval quality

Expected output:
```
Setting up knowledge base...
Parsing fundamentals.md... ✅ (15 chunks)
Parsing privacy.md... ✅ (18 chunks)
Parsing tokens.md... ✅ (12 chunks)
Parsing staking.md... ✅ (16 chunks)
Parsing contracts.md... ✅ (20 chunks)
Parsing security.md... ✅ (10 chunks)
Parsing faq.md... ✅ (25 chunks)

Total chunks: 116
Embedding complete!

Test query: "What is Secret Network?"
Top result: Secret Network Fundamentals - What is Secret Network

✅ Knowledge base ready!
```

#### **6. Launch SecretAgent**
```bash
python app.py
```

or use Gradio's hot-reload mode for development:
```bash
gradio app.py
```

Access at: **http://localhost:7860**

### **Quick Start Guide**

#### **First-Time User Flow**

1. **Learn About Secret Network**
   ```
   Ask: "What is Secret Network?"
   ```
   → Get comprehensive explanation with sources

2. **Create Your Wallet**
   - Go to Settings tab
   - Click "Create New Wallet"
   - Enter wallet name (e.g., "my-wallet")
   - **CRITICAL**: Save your mnemonic phrase (shown once!)
   - Wallet created with address shown

3. **Get Testnet Tokens**
   - Visit [Testnet Faucet](https://faucet.pulsar.scrttestnet.com)
   - Enter your wallet address
   - Receive 10 SCRT for testing

4. **Check Your Balance**
   ```
   Ask: "What's my balance?"
   ```
   → See available SCRT

5. **Start Staking**
   ```
   Say: "Stake 5 SCRT to the best validator"
   ```
   → Agent analyzes validators, recommends, and executes

6. **View Portfolio**
   - Go to Portfolio tab
   - See delegations, rewards, and total value
   - Track your staking performance

#### **Example Conversations**

**Learning Mode**:
```
You: "How does staking work on Secret Network?"

Agent: "Staking on Secret Network allows you to delegate your SCRT 
tokens to validators who secure the network. Here's how it works:

🏛️ **Delegation Process**:
You delegate SCRT to a validator of your choice. Your tokens remain 
yours but are "bonded" to help secure the network.

💰 **Earning Rewards**:
You earn rewards proportional to your stake. Typical APR is 15-20% 
depending on validator commission and network inflation.

⏰ **Unbonding Period**:
If you want your tokens back, there's a 21-day unbonding period for 
network security. During this time, you don't earn rewards.

🎯 **Choosing Validators**:
Consider: voting power (lower is more decentralized), commission 
(5-10% is reasonable), and uptime (99%+ required).

Would you like me to:
- Show you the top validators?
- Stake some SCRT for you?
- Explain more about rewards?"

Sources: Staking Guide, Secret Network Fundamentals
```

**Execution Mode**:
```
You: "Send 1 SCRT to secret1test..."

Agent: "I'll send 1 SCRT to secret1test...

Checking balance... ✅ Sufficient funds
Preparing transaction...
Estimated gas: 0.025 SCRT

Confirm transaction?
- Amount: 1 SCRT
- Recipient: secret1test...
- Gas: 0.025 SCRT
- Total: 1.025 SCRT

[Confirm] [Cancel]

(After confirmation)

✅ Transaction successful!
Tx Hash: A1B2C3D4...

Your new balance: 8.975 SCRT

Next steps:
- Check transaction on explorer
- View transaction history
- Send more tokens"
```

**Autonomous Mode**:
```
You: "Optimize my staking to maximize rewards"

Agent: "I'll analyze your current staking and optimize for maximum 
rewards. Let me plan the strategy:

📊 **Current Analysis**:
- Total Staked: 10 SCRT across 2 validators
- Current APR: 16.2% average
- Validator A: 5 SCRT @ 15% APR, 8% commission
- Validator B: 5 SCRT @ 17.5% APR, 5% commission

🎯 **Optimization Strategy**:
1. Redelegate from Validator A to Validator C (higher APR, lower commission)
2. No unbonding needed (instant redelegate)
3. Projected new APR: 18.1% (+1.9%)
4. Estimated increase: +0.19 SCRT/year

📋 **Execution Plan**:
Step 1: Redelegate 5 SCRT from Validator A to Validator C
        (No unbonding period for redelegation)

Proceed with optimization?
[Yes, Optimize] [Show Me Validator C First] [Cancel]

(After confirmation)

✅ Optimization complete!
- Redelegated 5 SCRT to Validator C
- New APR: 18.1%
- Transaction: TX123...

Your staking is now optimized for maximum rewards! 🎉"
```

---

## 🎨 **User Interface**

### **Chat Tab (Primary Interface)**

![Chat Interface](assets/screenshots/chat.png)

**Features**:
- 💬 Natural language conversation
- 🌊 Streaming AI responses (see thinking in real-time)
- 📜 Persistent conversation history
- ⚡ Quick action buttons for common tasks
- 🔍 Source citations for knowledge answers
- 💡 Smart follow-up suggestions

### **Portfolio Tab**

![Portfolio Dashboard](assets/screenshots/portfolio.png)

**Features**:
- 📊 Visual overview cards (Total, Available, Staked, Rewards)
- 📋 Delegations table with per-validator details
- 🎁 Rewards breakdown by validator
- 🔄 One-click refresh
- ⚡ Quick actions (Withdraw, Manage)

### **Validators Tab**

![Validators Table](assets/screenshots/validators.png)

**Features**:
- 🏛️ Complete validator comparison table
- 🎯 Smart scoring algorithm (0-10 scale)
- 🔍 Filter by status (Active/Inactive)
- 📊 Sort by: Score, Voting Power, Commission, APR
- ⚡ Quick delegation from table

### **Settings Tab**

![Settings Panel](assets/screenshots/settings.png)

**Features**:
- 🔑 Multi-wallet management (Create, Import, Switch)
- 🌐 Network configuration (Testnet/Mainnet)
- 🎨 Theme toggle (Dark/Light)
- ℹ️ About and version info

---

## 🧪 **Testing**

### **Test Coverage**

```
MCP-SCRT (Foundation): 637 tests ✅
├── Unit Tests: 601
│   ├── Types & Config: 42 tests
│   ├── Utils (Errors, Logging): 38 tests
│   ├── Core (Cache, Session, Security): 142 tests
│   ├── SDK (Client, Wallet): 150 tests
│   └── Tools (11 categories): 229 tests
│
└── Integration Tests: 36
    ├── Transfer Workflow: 5 tests
    ├── Staking Workflow: 4 tests
    ├── Contract Workflow: 6 tests
    ├── Error Scenarios: 11 tests
    └── Caching Behavior: 10 tests

SecretAgent (New Code): 45+ tests
├── Knowledge Base: 12 tests
├── Agent Core: 18 tests
├── UI Components: 10 tests
└── Integration: 5 tests

Total: 682+ tests passing
```

### **Run Tests**

```bash
# All tests
pytest

# MCP-SCRT tests only
cd mcp-scrt
pytest

# SecretAgent tests only
pytest tests/

# With coverage
pytest --cov=src --cov-report=html

# Specific module
pytest tests/test_knowledge.py -v
```

### **Quality Checks**

```bash
# Code formatting
black src/ tests/

# Linting
ruff check src/ tests/

# Type checking
mypy src/

# Security scan
bandit -r src/
```

---

## 📚 **Documentation**

### **Additional Docs**

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Technical deep-dive into system design
- **[KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md)**: How the knowledge system works
- **[MCP_INTEGRATION.md](MCP_INTEGRATION.md)**: Integrating with MCP-SCRT
- **[API.md](API.md)**: API reference for developers
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Deployment guide for Hugging Face Spaces

### **MCP-SCRT Documentation**

The foundation MCP server has extensive documentation:
- [Get Started Guide](mcp-scrt/Get-Started.md)
- [Architecture](mcp-scrt/Architecture.md)
- [MCP Integration](mcp-scrt/MCP-INTEGRATION.md)
- [Implementation Plan](mcp-scrt/Implementation-Plan.md)
- [Progress Tracking](mcp-scrt/Progress.md)

---

## 🔐 **Security**

### **Security Features**

- ✅ **Wallet Encryption**: Fernet symmetric encryption with PBKDF2 (600,000 iterations)
- ✅ **In-Memory Only**: Mnemonics and private keys never persisted to disk
- ✅ **Confirmation Prompts**: Required for sensitive operations (large transfers, voting)
- ✅ **Spending Limits**: Configurable per-transaction limits
- ✅ **Input Validation**: Strict validation for all parameters (addresses, amounts)
- ✅ **Rate Limiting**: Protection against abuse
- ✅ **HTTPS**: All RPC communications encrypted

### **Best Practices**

**DO**:
- ✅ Always save your mnemonic phrase securely
- ✅ Use testnet first for learning
- ✅ Verify addresses before sending
- ✅ Start with small amounts
- ✅ Review confirmation prompts carefully

**DON'T**:
- ❌ Share your mnemonic phrase with anyone
- ❌ Store mnemonics in plain text files
- ❌ Skip confirmation dialogs
- ❌ Use the same wallet for testing and mainnet
- ❌ Click suspicious links in the UI

### **Responsible Disclosure**

Found a security issue? Please email: a13x.h.cc@gmail.com (or submit via GitHub Security Advisories)

---

## 🗺️ **Roadmap**

### **Phase 1: MVP** ✅ (Current - Hackathon Submission)
- [x] Knowledge base (7 topics, RAG)
- [x] Chat interface with streaming
- [x] 60 blockchain operations via MCP
- [x] Autonomous staking with validator analysis
- [x] Portfolio dashboard
- [x] Validator comparison table
- [x] Wallet management
- [x] Privacy-focused theme

### **Phase 2: Enhanced Intelligence** (Post-Hackathon)
- [ ] **Advanced RAG**: Multi-query retrieval, hypothetical document embeddings
- [ ] **Fine-tuned Models**: Custom LLM fine-tuned on Secret Network
- [ ] **Predictive Analytics**: APR forecasting, validator performance predictions
- [ ] **Natural Language Contracts**: Generate Secret Contracts from descriptions
- [ ] **Voice Interface**: Voice commands for accessibility

### **Phase 3: DeFi Features** (Q1 2026)
- [ ] **SecretSwap Integration**: DEX trading via natural language
- [ ] **Lending Protocols**: Integration with Sienna Lend
- [ ] **Liquidity Provision**: Automated liquidity management
- [ ] **Yield Optimization**: Auto-compound and rebalancing strategies
- [ ] **Portfolio Analytics**: Advanced charts, P&L tracking

### **Phase 4: Advanced Privacy** (Q2 2026)
- [ ] **Private Voting**: Zero-knowledge governance participation
- [ ] **Confidential NFTs**: SecretNFT management and trading
- [ ] **Private Messaging**: Encrypted agent-to-agent communication
- [ ] **Secret Contracts Builder**: Visual contract creation tool
- [ ] **Privacy Mixer**: Enhanced transaction privacy

### **Phase 5: Ecosystem & Scale** (Q3 2026)
- [ ] **Multi-Chain**: Support for IBC-connected chains
- [ ] **Mobile App**: Native iOS/Android with full agent functionality
- [ ] **Agent Marketplace**: Community-created specialized agents
- [ ] **Developer SDK**: Build custom agents on SecretAgent
- [ ] **Enterprise**: White-label solutions for businesses

---

## 🤝 **Contributing**

We welcome contributions! SecretAgent is open-source and community-driven.

### **How to Contribute**

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow our code style and add tests
4. **Commit**: `git commit -m 'Add amazing feature'`
5. **Push**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**: Describe your changes and why they're awesome

### **Contribution Guidelines**

- **Code Style**: Follow PEP 8, use `black` for formatting
- **Tests**: Add tests for new features (maintain >90% coverage)
- **Documentation**: Update relevant docs (README, docstrings)
- **Commits**: Use clear, descriptive commit messages
- **Issues**: Check existing issues before creating new ones

### **Areas We Need Help**

- 🐛 Bug fixes and testing
- 📚 Documentation improvements
- 🎨 UI/UX enhancements
- 🌍 Internationalization (i18n)
- 🔌 New integrations (DEX, lending, NFTs)
- 🧠 ML/AI improvements (better retrieval, fine-tuning)

---

## 🏆 **Hackathon Info**

**Built for**: [MCP's 1st Birthday Hackathon](https://huggingface.co/MCP-1st-Birthday)  
**Track**: Track 2 - MCP in Action  
**Category**: Productivity  
**Dates**: November 14-30, 2025  
**Team**: Solo Developer

### **Why SecretAgent Stands Out**

✅ **Unique Domain**: First and only Secret Network AI agent in hackathon  
✅ **Production-Ready Foundation**: Built on 637 tests, 22.5k LOC proven codebase  
✅ **Dual Value**: Education + Execution in one seamless experience  
✅ **True Autonomy**: Multi-step planning and intelligent decision-making  
✅ **Privacy Focus**: Aligns with critical Web3 need (privacy)  
✅ **Complete Experience**: Full-stack solution (MCP server + Gradio app + knowledge)  
✅ **Real-World Impact**: Onboards non-technical users to privacy blockchain  

### **Technical Highlights**

- **MCP Integration**: Leverages MCP protocol with 60 production-ready tools
- **Advanced RAG**: Hybrid retrieval (vector + keyword) with re-ranking
- **Streaming UI**: Real-time response generation for better UX
- **Autonomous Planning**: Multi-step execution with dependency resolution
- **Privacy-First**: Built on Secret Network, the only confidential compute blockchain
- **Mobile-Ready**: PWA-enabled Gradio 6 interface

---

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 SecretAgent Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 **Acknowledgments**

### **Built With**
- **[Secret Network](https://scrt.network)**: Privacy-preserving blockchain infrastructure
- **[MCP-SCRT](https://github.com/alexh-scrt/mcp-scrt)**: Production-ready MCP server (637 tests ✅)
- **[Gradio](https://gradio.app)**: Beautiful, mobile-first UI framework
- **[Anthropic MCP](https://modelcontextprotocol.io)**: Model Context Protocol standard
- **[Ollama](https://ollama.ai)**: Local LLM inference with Llama 3.3 70B
- **[ChromaDB](https://www.trychroma.com)**: Vector database for embeddings
- **[Redis](https://redis.io)**: High-performance caching layer

### **Inspired By**
- **Secret Network Community**: For building the future of privacy in Web3
- **MCP Community**: For pioneering agent-tool interaction standards
- **Gradio Team**: For making ML demos accessible and beautiful

### **Special Thanks**
- **Anthropic**: For hosting this incredible hackathon
- **Hugging Face**: For Spaces hosting and community support
- **Secret Network Foundation**: For supporting privacy innovation
- **Early Testers**: For feedback and bug reports

---

## 📞 **Contact & Links**

### **Live Demo & Resources**
- 🚀 **Live Demo**: [Try SecretAgent on Hugging Face Spaces](#)
- 🎥 **Demo Video**: [Watch on YouTube](#)
- 💻 **Source Code**: [GitHub Repository](https://github.com/alexh-scrt/secret-agent)
- 📚 **Documentation**: [Full Docs](#)

### **Secret Network Resources**
- 🌐 **Website**: [scrt.network](https://scrt.network)
- 📖 **Docs**: [docs.scrt.network](https://docs.scrt.network)
- 🧪 **Testnet Faucet**: [faucet.pulsar.scrttestnet.com](https://faucet.pulsar.scrttestnet.com)
- 🔍 **Explorer**: [testnet.ping.pub/secret](https://testnet.ping.pub/secret)
- 💬 **Discord**: [Secret Network Discord](https://discord.gg/secret-network)
- 🐦 **Twitter**: [@SecretNetwork](https://twitter.com/SecretNetwork)

### **Connect With Us**
- 🐦 **Twitter/X**: [@SecretAgentAI](#)
- 💼 **LinkedIn**: [SecretAgent](#)
- 📧 **Email**: a13x.h.cc@gmail.com
- 💬 **Discord**: [Join our server](#)

---

## 🌟 **Star History**

If you find SecretAgent useful, please consider starring the repository! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=alexh-scrt/secret-agent&type=Date)](https://star-history.com/#alexh-scrt/secret-agent&Date)

---

<div align="center">

### Built with ❤️ for the Secret Network ecosystem

**SecretAgent** - Making privacy-preserving blockchain accessible to everyone

🔐 Privacy First | 🤖 AI-Powered | 🚀 Open Source

[Get Started](#getting-started) • [Documentation](#documentation) • [Contribute](#contributing)

---

*Made with passion for [MCP's 1st Birthday Hackathon](https://huggingface.co/MCP-1st-Birthday)*

</div>