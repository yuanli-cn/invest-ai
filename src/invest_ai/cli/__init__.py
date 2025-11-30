"""CLI module for invest-ai."""

from .arguments import parse_arguments, validate_arguments

__all__ = [
    "parse_arguments",
    "validate_arguments",
]


def __getattr__(name: str):
    """Lazy import for main module to avoid RuntimeWarning when using python -m."""
    if name in ("main", "CLIController"):
        from .main import CLIController, main
        return main if name == "main" else CLIController
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
