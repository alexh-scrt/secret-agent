"""Main entry point for Secret Agent application."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.app import create_app
from src.utils.logging_config import setup_logging


def main():
    """Run the Secret Agent application."""
    # Setup logging
    setup_logging(level="INFO")

    # Create and launch the Gradio app
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )


if __name__ == "__main__":
    main()
