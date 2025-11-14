"""Ollama integration - manages communication with Ollama LLM."""


class OllamaClient:
    """Client for interacting with Ollama."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        Initialize Ollama client.

        Args:
            base_url: Ollama server URL
            model: Model name to use
        """
        self.base_url = base_url
        self.model = model
        # TODO: Initialize Ollama client

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate a response from Ollama.

        Args:
            prompt: User prompt
            system_prompt: System prompt for context

        Returns:
            Generated response
        """
        # TODO: Implement Ollama generation
        pass

    def chat(self, messages: list) -> str:
        """
        Chat with Ollama using message history.

        Args:
            messages: List of message dictionaries

        Returns:
            Generated response
        """
        # TODO: Implement Ollama chat
        pass
