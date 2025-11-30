"""Main entry point for Invest AI."""

import sys

from invest_ai.cli.main import main as cli_main


def main() -> int:
    """Main entry point."""
    return cli_main()


if __name__ == "__main__":
    sys.exit(main())
