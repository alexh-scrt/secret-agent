"""Script to embed knowledge content to ChromaDB."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Embed knowledge content to ChromaDB."""
    print("Setting up knowledge base...")

    # TODO: Implement knowledge embedding
    # 1. Read markdown files from src/knowledge/content/
    # 2. Parse and chunk the content
    # 3. Embed using ChromaDB
    # 4. Store embeddings

    print("Knowledge base setup complete!")


if __name__ == "__main__":
    main()
