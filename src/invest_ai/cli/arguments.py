"""CLI argument parsing and validation."""

import argparse
import sys
from pathlib import Path

from invest_ai.models import InvestmentType


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace | None:
    """Parse command line arguments.

    Args:
        args: Optional list of arguments. If None, uses sys.argv.

    Returns:
        Parsed arguments, or None if help was shown (no arguments provided).
    """
    parser = create_argument_parser()

    # Handle no arguments case - show help summary
    if args is not None and len(args) == 0:
        print_help_summary()
        return None
    if args is None and len(sys.argv) == 1:
        print_help_summary()
        return None

    parsed = parser.parse_args(args)

    # Set default data path based on type if not provided
    if parsed.data is None and parsed.type:
        parsed.data = f"data/{parsed.type}.yaml"

    return parsed


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="invest-ai",
        description="Calculate investment profit and loss for Chinese stocks and mutual funds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calculate annual returns for all stocks in 2023
  invest-ai --type stock --year 2023 --data transactions.yaml

  # Calculate complete history for specific stock
  invest-ai --type stock --code 000001 --data transactions.yaml

  # Calculate annual returns for all funds
  invest-ai --type fund --year 2023 --data transactions.yaml

  # Full history for all investments
  invest-ai --type stock --data transactions.yaml
        """,
    )

    # Required arguments
    parser.add_argument(
        "--type",
        choices=[type.value for type in InvestmentType],
        required=True,
        help="Investment type (stock or fund)",
    )

    parser.add_argument(
        "--data",
        type=str,
        required=False,
        default=None,
        help="Path to YAML transaction file (default: data/<type>.yaml)",
    )

    # Optional arguments
    parser.add_argument(
        "--code",
        type=str,
        help="Specific investment code (6-digit number)",
    )

    parser.add_argument(
        "--year",
        type=int,
        help="Year for annual calculation (optional for full history)",
    )

    # Output formatting
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    # Debug options
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="invest-ai 0.1.0",
    )

    return parser


def validate_arguments(args: argparse.Namespace) -> bool:
    """Validate parsed arguments."""
    errors = []
    warnings = []

    # Validate data file exists
    data_path = Path(args.data)
    if not data_path.exists():
        errors.append(f"Data file does not exist: {args.data}")
    elif not data_path.is_file():
        errors.append(f"Data path is not a file: {args.data}")

    # Validate file extension
    if not args.data.lower().endswith((".yaml", ".yml")):
        warnings.append("Data file should have .yaml or .yml extension")

    # Validate investment code format
    if args.code:
        if not args.code.isdigit():
            # Allow alphabetic codes for international stocks
            if not args.code.isalpha():
                errors.append("Investment code must be numeric or alphabetic")
        elif (
            len(args.code) != 6
            and not (len(args.code) == 5 and args.code.startswith("0"))
            and args.code.isalpha()
        ):
            # Allow longer alphabetic codes for international stocks
            errors.append(
                "Investment code must be 6 digits (or 5 digits starting with 0 for Hong Kong stocks, or alphabetic for international stocks)"
            )

    # Validate year range
    if args.year:
        from datetime import datetime
        current_year = datetime.now().year
        if args.year < 1990 or args.year > current_year:
            errors.append(f"Year must be between 1990 and {current_year}")

    # Validate argument combinations
    if args.code and args.year and not args.type:
        warnings.append("Type is omitted, will infer from code pattern")

    # Report validation results
    if errors:
        print("Validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  ❌ {error}", file=sys.stderr)
    if warnings:
        print("Validation warnings:", file=sys.stderr)
        for warning in warnings:
            print(f"  ⚠️  {warning}", file=sys.stderr)

    return len(errors) == 0


def get_usage_examples() -> list[str]:
    """Get usage examples for help output."""
    return [
        "invest-ai --type stock --year 2023 --data transactions.yaml",
        "invest-ai --type fund --code 110022 --data transactions.yaml",
        "invest-ai --type stock --data transactions.yaml",
    ]


def print_help_summary() -> None:
    """Print a concise help summary."""
    print("invest-ai - Investment Profit & Loss Calculator")
    print()
    print("Basic usage:")
    print("  invest-ai --type <stock|fund> --data <file> [options]")
    print()
    print("Key options:")
    print("  --code <code>    Specific investment code")
    print("  --year <year>    Annual calculation")
    print("  --format <type>  Output format (table/json)")
    print("  --verbose        Enable verbose output")
    print()
    print("Use --help for detailed usage information")
    print("Use --version for version information")
