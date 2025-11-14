"""Application configuration management."""

import os
from typing import Optional


class Config:
    """Application configuration."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        # MCP-SCRT configuration
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

        # Ollama configuration
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama2")

        # ChromaDB configuration
        self.chroma_host = os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port = int(os.getenv("CHROMA_PORT", "8001"))

        # Redis configuration
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        # Secret Network configuration
        self.rpc_url = os.getenv("SCRT_RPC_URL", "https://lcd.mainnet.secretsaturn.net")
        self.chain_id = os.getenv("SCRT_CHAIN_ID", "secret-4")
        self.wallet_address = os.getenv("SCRT_WALLET_ADDRESS", "")

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return getattr(self, key, default)


# Global config instance
config = Config()
