# Part 3: Deployment Guide & Integration

## Overview

This final phase provides comprehensive deployment instructions, integration scripts, and production-ready configuration.

---

## Task 3.1: Main Integration Script

**Objective**: Create the main entry point that initializes all components and launches the application.

**Files to Create**:
```
main.py
config.yaml
requirements.txt
setup.py
.env.example
```

**Implementation Details**:

```python
# main.py

"""
SecretAgent - Privacy-First Blockchain AI Assistant

Main entry point for the application.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "mcp-scrt" / "src"))

# Import MCP server components
from mcp_scrt.server import MCPServer
from mcp_scrt.types import NetworkType

# Import integration components
from mcp_scrt.integrations.chromadb_client import ChromaDBClient
from mcp_scrt.integrations.neo4j_client import Neo4jClient
from mcp_scrt.integrations.redis_client import RedisClient
from mcp_scrt.integrations.ollama_client import OllamaClient

# Import services
from mcp_scrt.services.embedding_service import EmbeddingService
from mcp_scrt.services.knowledge_service import KnowledgeService
from mcp_scrt.services.graph_service import GraphService
from mcp_scrt.services.cache_service import CacheService

# Import agent components
from src.agent.orchestrator import AgentOrchestrator

# Import UI
from src.ui.app import SecretAgentUI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('secretagent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class SecretAgentApp:
    """
    Main application class that orchestrates all components.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize SecretAgent application.
        
        Args:
            config_path: Path to configuration file
        """
        logger.info("=" * 80)
        logger.info("SecretAgent - Privacy-First Blockchain AI Assistant")
        logger.info("=" * 80)
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.mcp_server = None
        self.orchestrator = None
        self.ui = None
        
        # Database clients
        self.chromadb = None
        self.neo4j = None
        self.redis = None
        self.ollama = None
        
        # Services
        self.embedding_service = None
        self.knowledge_service = None
        self.graph_service = None
        self.cache_service = None
    
    def _load_config(self, config_path: str) -> dict:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._default_config()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._default_config()
    
    def _default_config(self) -> dict:
        """Get default configuration."""
        return {
            "network": {
                "type": "testnet",
                "chain_id": "pulsar-3"
            },
            "chromadb": {
                "host": os.getenv("CHROMADB_HOST", "localhost"),
                "port": int(os.getenv("CHROMADB_PORT", 8000))
            },
            "neo4j": {
                "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                "username": os.getenv("NEO4J_USERNAME", "neo4j"),
                "password": os.getenv("NEO4J_PASSWORD", "password")
            },
            "redis": {
                "host": os.getenv("REDIS_HOST", "localhost"),
                "port": int(os.getenv("REDIS_PORT", 6379)),
                "db": int(os.getenv("REDIS_DB", 0))
            },
            "ollama": {
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                "model": os.getenv("OLLAMA_MODEL", "llama3.3:70b")
            },
            "ui": {
                "server_name": os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
                "server_port": int(os.getenv("GRADIO_SERVER_PORT", 7860)),
                "share": os.getenv("GRADIO_SHARE", "false").lower() == "true"
            },
            "features": {
                "knowledge": True,
                "graph": True,
                "cache": True
            }
        }
    
    async def initialize(self):
        """
        Initialize all application components.
        """
        logger.info("Initializing application components...")
        
        try:
            # 1. Initialize database clients
            await self._initialize_databases()
            
            # 2. Initialize services
            await self._initialize_services()
            
            # 3. Initialize MCP server
            await self._initialize_mcp_server()
            
            # 4. Initialize agent orchestrator
            await self._initialize_orchestrator()
            
            # 5. Initialize UI
            await self._initialize_ui()
            
            logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}", exc_info=True)
            raise
    
    async def _initialize_databases(self):
        """Initialize database clients."""
        logger.info("Initializing database clients...")
        
        # ChromaDB
        if self.config["features"]["knowledge"]:
            try:
                self.chromadb = ChromaDBClient(
                    host=self.config["chromadb"]["host"],
                    port=self.config["chromadb"]["port"]
                )
                self.chromadb.connect()
                logger.info("✅ ChromaDB connected")
            except Exception as e:
                logger.warning(f"⚠️  ChromaDB initialization failed: {e}")
                self.chromadb = None
        
        # Neo4j
        if self.config["features"]["graph"]:
            try:
                self.neo4j = Neo4jClient(
                    uri=self.config["neo4j"]["uri"],
                    username=self.config["neo4j"]["username"],
                    password=self.config["neo4j"]["password"]
                )
                self.neo4j.connect()
                logger.info("✅ Neo4j connected")
            except Exception as e:
                logger.warning(f"⚠️  Neo4j initialization failed: {e}")
                self.neo4j = None
        
        # Redis
        if self.config["features"]["cache"]:
            try:
                self.redis = RedisClient(
                    host=self.config["redis"]["host"],
                    port=self.config["redis"]["port"],
                    db=self.config["redis"]["db"]
                )
                self.redis.connect()
                logger.info("✅ Redis connected")
            except Exception as e:
                logger.warning(f"⚠️  Redis initialization failed: {e}")
                self.redis = None
        
        # Ollama
        try:
            self.ollama = OllamaClient(
                base_url=self.config["ollama"]["base_url"],
                model=self.config["ollama"]["model"]
            )
            health = self.ollama.health_check()
            if health["status"] == "healthy":
                logger.info("✅ Ollama connected")
            else:
                logger.warning("⚠️  Ollama health check failed")
                self.ollama = None
        except Exception as e:
            logger.warning(f"⚠️  Ollama initialization failed: {e}")
            self.ollama = None
    
    async def _initialize_services(self):
        """Initialize service layer."""
        logger.info("Initializing services...")
        
        # Embedding service
        if self.redis and self.config["features"]["knowledge"]:
            try:
                self.embedding_service = EmbeddingService(
                    redis_client=self.redis
                )
                logger.info("✅ Embedding service initialized")
            except Exception as e:
                logger.warning(f"⚠️  Embedding service failed: {e}")
        
        # Knowledge service
        if self.chromadb and self.redis and self.ollama and self.embedding_service:
            try:
                self.knowledge_service = KnowledgeService(
                    chromadb_client=self.chromadb,
                    redis_client=self.redis,
                    ollama_client=self.ollama,
                    embedding_service=self.embedding_service
                )
                logger.info("✅ Knowledge service initialized")
            except Exception as e:
                logger.warning(f"⚠️  Knowledge service failed: {e}")
        
        # Graph service
        if self.neo4j and self.redis and self.config["features"]["graph"]:
            try:
                self.graph_service = GraphService(
                    neo4j_client=self.neo4j,
                    redis_client=self.redis
                )
                logger.info("✅ Graph service initialized")
            except Exception as e:
                logger.warning(f"⚠️  Graph service failed: {e}")
        
        # Cache service
        if self.redis and self.config["features"]["cache"]:
            try:
                self.cache_service = CacheService(
                    redis_client=self.redis
                )
                logger.info("✅ Cache service initialized")
            except Exception as e:
                logger.warning(f"⚠️  Cache service failed: {e}")
    
    async def _initialize_mcp_server(self):
        """Initialize MCP server."""
        logger.info("Initializing MCP server...")
        
        try:
            network_type = NetworkType.TESTNET if self.config["network"]["type"] == "testnet" else NetworkType.MAINNET
            
            self.mcp_server = MCPServer(
                network=network_type,
                enable_knowledge=self.config["features"]["knowledge"],
                enable_graph=self.config["features"]["graph"],
                enable_cache=self.config["features"]["cache"]
            )
            
            logger.info("✅ MCP server initialized")
            logger.info(f"   Network: {network_type.value}")
            logger.info(f"   Total tools: 78")
            
        except Exception as e:
            logger.error(f"❌ MCP server initialization failed: {e}")
            raise
    
    async def _initialize_orchestrator(self):
        """Initialize agent orchestrator."""
        logger.info("Initializing agent orchestrator...")
        
        if not self.ollama:
            logger.error("❌ Ollama client required for orchestrator")
            raise RuntimeError("Ollama client not initialized")
        
        try:
            self.orchestrator = AgentOrchestrator(
                mcp_server=self.mcp_server,
                ollama_client=self.ollama,
                knowledge_service=self.knowledge_service,
                graph_service=self.graph_service,
                cache_service=self.cache_service
            )
            
            logger.info("✅ Agent orchestrator initialized")
            
        except Exception as e:
            logger.error(f"❌ Orchestrator initialization failed: {e}")
            raise
    
    async def _initialize_ui(self):
        """Initialize Gradio UI."""
        logger.info("Initializing UI...")
        
        try:
            self.ui = SecretAgentUI(
                orchestrator=self.orchestrator,
                mcp_server=self.mcp_server,
                knowledge_service=self.knowledge_service,
                graph_service=self.graph_service,
                cache_service=self.cache_service
            )
            
            logger.info("✅ UI initialized")
            
        except Exception as e:
            logger.error(f"❌ UI initialization failed: {e}")
            raise
    
    def launch(self):
        """
        Launch the application.
        """
        logger.info("=" * 80)
        logger.info("Launching SecretAgent...")
        logger.info("=" * 80)
        
        try:
            ui_config = self.config["ui"]
            
            logger.info(f"Server: http://{ui_config['server_name']}:{ui_config['server_port']}")
            logger.info("Press Ctrl+C to stop")
            logger.info("=" * 80)
            
            self.ui.launch(
                server_name=ui_config["server_name"],
                server_port=ui_config["server_port"],
                share=ui_config["share"]
            )
            
        except KeyboardInterrupt:
            logger.info("\nShutdown requested...")
            self.shutdown()
        except Exception as e:
            logger.error(f"❌ Launch failed: {e}", exc_info=True)
            self.shutdown()
            sys.exit(1)
    
    def shutdown(self):
        """
        Graceful shutdown of all components.
        """
        logger.info("=" * 80)
        logger.info("Shutting down SecretAgent...")
        logger.info("=" * 80)
        
        # Close database connections
        if self.chromadb:
            try:
                self.chromadb.close()
                logger.info("✅ ChromaDB connection closed")
            except Exception as e:
                logger.error(f"Error closing ChromaDB: {e}")
        
        if self.neo4j:
            try:
                self.neo4j.close()
                logger.info("✅ Neo4j connection closed")
            except Exception as e:
                logger.error(f"Error closing Neo4j: {e}")
        
        if self.redis:
            try:
                self.redis.close()
                logger.info("✅ Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis: {e}")
        
        if self.ollama:
            try:
                self.ollama.close()
                logger.info("✅ Ollama connection closed")
            except Exception as e:
                logger.error(f"Error closing Ollama: {e}")
        
        logger.info("=" * 80)
        logger.info("SecretAgent shutdown complete")
        logger.info("=" * 80)


async def main():
    """
    Main entry point.
    """
    # Create application
    app = SecretAgentApp()
    
    # Initialize all components
    await app.initialize()
    
    # Launch UI
    app.launch()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nApplication stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
```

```yaml
# config.yaml

# Network configuration
network:
  type: "testnet"  # or "mainnet"
  chain_id: "pulsar-3"

# ChromaDB configuration (Vector database)
chromadb:
  host: "localhost"
  port: 8000
  # Optional: Use HTTP client
  # http_client: true
  # http_url: "http://localhost:8000"

# Neo4j configuration (Graph database)
neo4j:
  uri: "bolt://localhost:7687"
  username: "neo4j"
  password: "password"
  # Optional: Database name
  database: "neo4j"

# Redis configuration (Cache)
redis:
  host: "localhost"
  port: 6379
  db: 0
  # Optional: Password
  # password: "your-redis-password"
  # Optional: Connection pool size
  max_connections: 10

# Ollama configuration (LLM)
ollama:
  base_url: "http://localhost:11434"
  model: "llama3.3:70b"
  # Alternative models:
  # model: "llama3.1:70b"
  # model: "mixtral:8x7b"
  
  # Generation options
  options:
    temperature: 0.7
    top_p: 0.9
    num_ctx: 8192  # Context window size

# Gradio UI configuration
ui:
  server_name: "0.0.0.0"
  server_port: 7860
  share: false  # Set to true for public sharing
  # Optional: Authentication
  # auth: ["username", "password"]

# Feature flags
features:
  knowledge: true  # Enable knowledge base features
  graph: true      # Enable graph analysis features
  cache: true      # Enable intelligent caching

# Logging configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "secretagent.log"
  max_bytes: 10485760  # 10 MB
  backup_count: 5

# Knowledge base configuration
knowledge:
  # Collections to initialize
  collections:
    - fundamentals
    - privacy_tech
    - tokens
    - staking
    - contracts
    - security
    - faq
  
  # Search configuration
  top_k: 5
  min_similarity: 0.6
  
  # LLM synthesis
  synthesis_enabled: true
  max_sources: 5

# Graph service configuration
graph:
  # Validator recommendation weights
  recommendation_weights:
    decentralization: 0.35
    commission: 0.25
    uptime: 0.25
    community: 0.15
  
  # Network analysis
  max_depth: 3
  cache_ttl: 3600  # 1 hour

# Cache configuration
cache:
  default_ttl: 300  # 5 minutes
  max_memory: "500mb"
  eviction_policy: "allkeys-lru"
  
  # TTL by key pattern
  ttl_patterns:
    "balance:*": 60      # 1 minute
    "validator:*": 300   # 5 minutes
    "block:*": 15        # 15 seconds
    "knowledge:*": 3600  # 1 hour

# Agent configuration
agent:
  # Intent classification
  intent_confidence_threshold: 0.7
  
  # Conversation
  max_history_turns: 10
  
  # Transaction confirmations
  require_confirmation: true
  confirmation_threshold: 1000000  # 1 SCRT in uscrt

# Development settings
development:
  debug: false
  hot_reload: false
  mock_blockchain: false
```

```bash
# .env.example

# Copy this file to .env and fill in your values
# cp .env.example .env

# Network
NETWORK_TYPE=testnet
CHAIN_ID=pulsar-3

# ChromaDB
CHROMADB_HOST=localhost
CHROMADB_PORT=8000

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password-here

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.3:70b

# Gradio
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
GRADIO_SHARE=false

# Optional: Authentication
# GRADIO_USERNAME=admin
# GRADIO_PASSWORD=your-secure-password

# Optional: API Keys (if needed)
# SECRET_LCD_API_KEY=
# SECRET_RPC_API_KEY=

# Logging
LOG_LEVEL=INFO

# Feature Flags
ENABLE_KNOWLEDGE=true
ENABLE_GRAPH=true
ENABLE_CACHE=true
```

```txt
# requirements.txt

# Core dependencies
python-dotenv==1.0.0
pyyaml==6.0.1

# Gradio
gradio==4.44.0

# Secret Network SDK
secret-sdk-python==0.1.0

# FastMCP (for MCP server)
fastmcp==0.2.0

# Database clients
chromadb==0.4.24
neo4j==5.14.1
redis==5.0.1

# Ollama
ollama==0.1.6

# ML/AI
sentence-transformers==2.2.2
transformers==4.36.2
torch==2.1.2

# Data processing
pandas==2.1.4
numpy==1.26.2

# Utilities
aiohttp==3.9.1
requests==2.31.0
pydantic==2.5.3

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Development
black==23.12.1
flake8==6.1.0
mypy==1.7.1
```

```python
# setup.py

"""
Setup script for SecretAgent.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="secretagent",
    version="1.0.0",
    author="SecretAgent Team",
    author_email="contact@secretagent.ai",
    description="Privacy-First Blockchain AI Assistant for Secret Network",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/secretagent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "secretagent=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
```

**Success Criteria**:
- ✅ Main integration script complete
- ✅ Configuration system implemented
- ✅ Component initialization orchestrated
- ✅ Graceful shutdown handling
- ✅ Error recovery and logging

---

## Task 3.2: Deployment Scripts

**Objective**: Create scripts for easy deployment, including Docker support and service management.

**Files to Create**:
```
docker-compose.yml
Dockerfile
deploy.sh
start.sh
stop.sh
install.sh
```

**Implementation Details**:

```yaml
# docker-compose.yml

version: '3.8'

services:
  # SecretAgent Application
  secretagent:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: secretagent
    ports:
      - "7860:7860"
    environment:
      - CHROMADB_HOST=chromadb
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USERNAME=neo4j
      - NEO4J_PASSWORD=secretpassword
      - REDIS_HOST=redis
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - chromadb
      - neo4j
      - redis
      - ollama
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - secretagent-network

  # ChromaDB (Vector Database)
  chromadb:
    image: chromadb/chroma:latest
    container_name: secretagent-chromadb
    ports:
      - "8000:8000"
    volumes:
      - chromadb-data:/chroma/chroma
    environment:
      - ALLOW_RESET=TRUE
      - ANONYMIZED_TELEMETRY=FALSE
    restart: unless-stopped
    networks:
      - secretagent-network

  # Neo4j (Graph Database)
  neo4j:
    image: neo4j:5.14-community
    container_name: secretagent-neo4j
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/secretpassword
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
    volumes:
      - neo4j-data:/data
      - neo4j-logs:/logs
    restart: unless-stopped
    networks:
      - secretagent-network

  # Redis (Cache)
  redis:
    image: redis:7-alpine
    container_name: secretagent-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - secretagent-network

  # Ollama (LLM Server)
  ollama:
    image: ollama/ollama:latest
    container_name: secretagent-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    restart: unless-stopped
    networks:
      - secretagent-network
    # Optional: GPU support (uncomment if you have NVIDIA GPU)
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

volumes:
  chromadb-data:
  neo4j-data:
  neo4j-logs:
  redis-data:
  ollama-data:

networks:
  secretagent-network:
    driver: bridge
```

```dockerfile
# Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Expose Gradio port
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Run application
CMD ["python", "main.py"]
```

```bash
#!/bin/bash
# install.sh - Installation script

set -e

echo "================================"
echo "SecretAgent Installation"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10 or higher is required (found $python_version)"
    exit 1
fi
echo "✅ Python $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip
echo "✅ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Install package in development mode
echo ""
echo "Installing SecretAgent..."
pip install -e .
echo "✅ SecretAgent installed"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data logs
echo "✅ Directories created"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env with your configuration"
fi

# Check for Docker
echo ""
echo "Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
    
    # Check if Docker Compose is available
    if docker compose version &> /dev/null; then
        echo "✅ Docker Compose is available"
    else
        echo "⚠️  Docker Compose not found (optional)"
    fi
else
    echo "⚠️  Docker not found (optional, for containerized deployment)"
fi

echo ""
echo "================================"
echo "Installation Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Start required services:"
echo "   - Option A (Docker): ./deploy.sh"
echo "   - Option B (Manual): Start ChromaDB, Neo4j, Redis, and Ollama"
echo "3. Pull Ollama model: ollama pull llama3.3:70b"
echo "4. Start SecretAgent: ./start.sh"
echo ""
echo "For more information, see README.md"
```

```bash
#!/bin/bash
# deploy.sh - Deploy with Docker Compose

set -e

echo "================================"
echo "SecretAgent Deployment"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are available"
echo ""

# Pull images
echo "Pulling Docker images..."
docker compose pull
echo "✅ Images pulled"
echo ""

# Start services
echo "Starting services..."
docker compose up -d
echo "✅ Services started"
echo ""

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
sleep 10

# Pull Llama model
echo "Pulling Llama 3.3 70B model (this may take a while)..."
docker exec secretagent-ollama ollama pull llama3.3:70b
echo "✅ Model pulled"
echo ""

# Show status
echo "================================"
echo "Deployment Complete!"
echo "================================"
echo ""
echo "Services status:"
docker compose ps
echo ""
echo "Access points:"
echo "- SecretAgent UI: http://localhost:7860"
echo "- ChromaDB: http://localhost:8000"
echo "- Neo4j Browser: http://localhost:7474"
echo "- Redis: localhost:6379"
echo "- Ollama: http://localhost:11434"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop: docker compose down"
```

```bash
#!/bin/bash
# start.sh - Start SecretAgent (local development)

set -e

echo "================================"
echo "Starting SecretAgent"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Please run ./install.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "Please copy .env.example to .env and configure"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required services
echo "Checking required services..."

# Check ChromaDB
if curl -s http://${CHROMADB_HOST:-localhost}:${CHROMADB_PORT:-8000}/api/v1/heartbeat > /dev/null 2>&1; then
    echo "✅ ChromaDB is running"
else
    echo "⚠️  ChromaDB is not accessible"
fi

# Check Neo4j
if curl -s http://localhost:7474 > /dev/null 2>&1; then
    echo "✅ Neo4j is running"
else
    echo "⚠️  Neo4j is not accessible"
fi

# Check Redis
if redis-cli -h ${REDIS_HOST:-localhost} -p ${REDIS_PORT:-6379} ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "⚠️  Redis is not accessible"
fi

# Check Ollama
if curl -s ${OLLAMA_BASE_URL:-http://localhost:11434}/api/version > /dev/null 2>&1; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Ollama is not accessible"
fi

echo ""
echo "Starting SecretAgent..."
echo ""

# Run main application
python main.py
```

```bash
#!/bin/bash
# stop.sh - Stop all services

set -e

echo "================================"
echo "Stopping SecretAgent"
echo "================================"
echo ""

# Check if using Docker
if [ -f "docker-compose.yml" ] && docker compose ps | grep -q "Up"; then
    echo "Stopping Docker services..."
    docker compose down
    echo "✅ Docker services stopped"
else
    echo "No Docker services running"
fi

# Kill any running Python processes (SecretAgent)
if pgrep -f "main.py" > /dev/null; then
    echo "Stopping SecretAgent process..."
    pkill -f "main.py"
    echo "✅ SecretAgent stopped"
else
    echo "No SecretAgent process found"
fi

echo ""
echo "================================"
echo "All services stopped"
echo "================================"
```

Make all scripts executable:

```bash
chmod +x install.sh deploy.sh start.sh stop.sh
```

**Success Criteria**:
- ✅ Docker Compose configuration complete
- ✅ Dockerfile for containerization
- ✅ Installation script
- ✅ Deployment automation
- ✅ Service management scripts

---

## Task 3.3: Documentation

**Objective**: Create comprehensive documentation for deployment, usage, and development.

**Files to Create**:
```
README.md
DEPLOYMENT.md
DEVELOPMENT.md
ARCHITECTURE.md
```

**Implementation Details**:

```markdown
# README.md

# 🔐 SecretAgent

**Privacy-First Blockchain AI Assistant for Secret Network**

SecretAgent is an intelligent AI assistant that makes interacting with Secret Network's privacy-preserving blockchain simple and intuitive. Powered by local LLMs, vector databases, and graph analytics, it provides natural language interactions with blockchain operations while maintaining complete privacy.

---

## ✨ Features

### 🤖 AI-Powered Assistant
- Natural language blockchain interactions
- LLM-synthesized knowledge base (Llama 3.3 70B)
- Intelligent intent classification and routing
- Multi-turn conversations with context

### 🏦 Complete Blockchain Integration
- **78 MCP Tools** covering all Secret Network operations
- Wallet management (create, import, manage)
- Token operations (send, delegate, vote)
- Portfolio tracking and analytics
- Real-time blockchain data

### 📊 Advanced Analytics
- Validator network analysis with graph algorithms
- AI-powered validator recommendations
- Portfolio insights and tracking
- Transaction history and patterns

### 🎨 Beautiful Interface
- Modern Gradio UI with privacy-focused dark theme
- Real-time updates and streaming responses
- Responsive design for all devices
- Intuitive navigation and controls

### 🔒 Privacy & Security
- Local LLM execution (no external API calls)
- Non-custodial wallet management
- Encrypted blockchain interactions
- Privacy-preserving analytics

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (for containerized deployment)
- 16GB+ RAM recommended for Llama 3.3 70B
- GPU optional but recommended for LLM

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/secretagent.git
cd secretagent

# 2. Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Deploy with Docker
./deploy.sh

# 4. Access the UI
# Open http://localhost:7860 in your browser
```

### Option 2: Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/secretagent.git
cd secretagent

# 2. Run installation
./install.sh

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Start required services
# - ChromaDB: docker run -p 8000:8000 chromadb/chroma
# - Neo4j: docker run -p 7474:7474 -p 7687:7687 neo4j:5.14
# - Redis: docker run -p 6379:6379 redis:7-alpine
# - Ollama: docker run -p 11434:11434 ollama/ollama

# 5. Pull LLM model
ollama pull llama3.3:70b

# 6. Start SecretAgent
./start.sh
```

---

## 📖 Usage

### Chat Interface

Ask SecretAgent anything about Secret Network:

```
You: What is Secret Network?
Agent: Secret Network is a privacy-preserving blockchain platform...

You: Show my balance
Agent: Your balance:
- 1,234.567890 SCRT

You: Recommend the best validators to stake with
Agent: Based on AI analysis, here are my top recommendations:
1. Validator A (Score: 9.2/10)
   - Low voting power (2.3%)
   - Excellent uptime (99.9%)
   - Low commission (5%)
```

### Quick Actions

Use quick action buttons for common tasks:
- 📚 Explain Staking
- 💰 Check Balance
- 🏛️ Show Validators
- ⭐ Recommend Validators

### Portfolio Dashboard

View comprehensive portfolio data:
- Token balances
- Active delegations
- Pending rewards
- Transaction history

### Validators Explorer

Explore and analyze validators:
- Search and filter validators
- View detailed metrics
- Get AI recommendations
- Analyze network patterns

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Gradio UI (Frontend)              │
│  Chat │ Portfolio │ Validators │ Settings   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│       Agent Orchestration Layer             │
│  Intent Classifier │ Handlers │ Context     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          MCP-SCRT Server (78 Tools)         │
│  Blockchain │ Knowledge │ Graph │ Cache     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│            Service Layer                    │
│  Knowledge │ Graph │ Cache │ Embedding      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Infrastructure Layer               │
│  ChromaDB │ Neo4j │ Redis │ Ollama          │
│  Llama 3.3 70B │ Secret Network SDK         │
└─────────────────────────────────────────────┘
```

**Key Components:**

1. **UI Layer**: Gradio interface with tabbed navigation
2. **Agent Layer**: LLM-powered orchestration and routing
3. **MCP Server**: 78 tools for blockchain and AI operations
4. **Services**: Knowledge base, graph analytics, caching
5. **Infrastructure**: Databases and LLM backend

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🛠️ Technology Stack

| Category       | Technologies                                    |
| -------------- | ----------------------------------------------- |
| **Frontend**   | Gradio 4.44, Custom CSS/Theme                   |
| **AI/ML**      | Ollama, Llama 3.3 70B, Sentence Transformers    |
| **Databases**  | ChromaDB (vector), Neo4j (graph), Redis (cache) |
| **Backend**    | Python 3.11, FastMCP, asyncio                   |
| **Blockchain** | Secret Network, secret-sdk-python               |

---

## 📚 Documentation

- [**Deployment Guide**](DEPLOYMENT.md) - Detailed deployment instructions
- [**Development Guide**](DEVELOPMENT.md) - Setup for contributors
- [**Architecture**](ARCHITECTURE.md) - System design and components
- [**API Reference**](docs/api.md) - MCP tools documentation

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install in development mode
./install.sh

# Run tests
pytest tests/

# Format code
black src/ tests/

# Lint
flake8 src/ tests/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- [Secret Network](https://scrt.network) - Privacy blockchain
- [Ollama](https://ollama.ai) - Local LLM hosting
- [Gradio](https://gradio.app) - UI framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Neo4j](https://neo4j.com/) - Graph database

---

## 📞 Support

- 💬 [Discord Community](https://discord.gg/secret-network)
- 🐛 [Report Issues](https://github.com/yourusername/secretagent/issues)
- 📖 [Documentation](https://docs.secretagent.ai)
- 🐦 [Twitter](https://twitter.com/secretagent)

---

**Built with ❤️ for the Secret Network community**
```

**Success Criteria**:
- ✅ Comprehensive README
- ✅ Clear quick start guide
- ✅ Architecture overview
- ✅ Usage examples
- ✅ Complete documentation structure

---

## Summary: Part 3 COMPLETE

You have successfully completed **Part 3: Deployment & Integration**!

### **Deliverables**:

✅ **Integration Scripts**:
- `main.py` - Complete application orchestrator
- `config.yaml` - Flexible configuration
- `.env.example` - Environment template
- `requirements.txt` - Python dependencies
- `setup.py` - Package installation

✅ **Deployment Tools**:
- `docker-compose.yml` - Multi-container orchestration
- `Dockerfile` - Application containerization
- `install.sh` - Local installation script
- `deploy.sh` - Docker deployment automation
- `start.sh` / `stop.sh` - Service management

✅ **Documentation**:
- `README.md` - Comprehensive project overview
- Quick start guides
- Architecture documentation
- Usage examples

### **Complete System Summary**:

🎉 **SecretAgent is now production-ready with:**

1. **78 MCP Tools** (60 blockchain + 18 AI/analytics)
2. **AI Agent** with LLM orchestration
3. **Beautiful Gradio UI** with 5 functional tabs
4. **Complete Infrastructure** (ChromaDB, Neo4j, Redis, Ollama)
5. **Docker Deployment** for easy setup
6. **Comprehensive Documentation**

The application is ready to:
- Deploy locally or with Docker
- Handle natural language blockchain interactions
- Provide intelligent validator recommendations
- Track portfolios with real-time data
- Maintain privacy with local LLM execution

