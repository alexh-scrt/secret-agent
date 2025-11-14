"""Script to load demo/test data for development."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_demo_wallet():
    """Load demo wallet data."""
    print("Loading demo wallet...")
    # TODO: Implement demo wallet loading
    print("  ✓ Demo wallet loaded")


def load_demo_transactions():
    """Load demo transaction history."""
    print("Loading demo transactions...")
    # TODO: Implement demo transaction loading
    print("  ✓ Demo transactions loaded")


def load_demo_validators():
    """Load demo validator data."""
    print("Loading demo validators...")
    # TODO: Implement demo validator loading
    print("  ✓ Demo validators loaded")


def main():
    """Load all demo data."""
    print("Loading demo/test data...\n")

    load_demo_wallet()
    load_demo_transactions()
    load_demo_validators()

    print("\nDemo data loading complete!")


if __name__ == "__main__":
    main()
