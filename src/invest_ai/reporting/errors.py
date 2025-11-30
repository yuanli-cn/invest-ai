"""Error handling and error reporting for the reporting module."""

from collections.abc import Callable
from typing import Any

import rich.console
import rich.panel
import rich.text


class ReportingError(Exception):
    """Base class for reporting errors."""

    pass


class DataValidationError(ReportingError):
    """Error raised when data validation fails."""

    pass


class FormattingError(ReportingError):
    """Error raised when formatting fails."""

    pass


class IncompleteDataError(ReportingError):
    """Error raised when required data is missing."""

    pass


class ErrorHandler:
    """Handles error reporting for the reporting module."""

    def __init__(self) -> None:
        """Initialize error handler."""
        self.console = rich.console.Console()

    def format_error_message(self, error: Exception, context: str | None = None) -> str:
        """Format error message for display."""
        error_name = error.__class__.__name__
        error_message = str(error)

        if context:
            title_text = f"Error in {context} ({error_name})"
        else:
            title_text = f"Error ({error_name})"

        # Create error panel
        panel = rich.panel.Panel(
            self._format_error_content(error_message, error_name),
            title=title_text,
            border_style="red",
            padding=(1, 2),
        )

        # Capture as string
        import io

        string_buffer = io.StringIO()
        string_console = rich.console.Console(file=string_buffer, legacy_windows=False)
        string_console.print(panel)
        return string_buffer.getvalue()

    def format_warning_message(self, message: str, context: str | None = None) -> str:
        """Format warning message for display."""
        if context:
            title_text = f"Warning in {context}"
        else:
            title_text = "Warning"

        panel = rich.panel.Panel(
            message, title=title_text, border_style="yellow", padding=(1, 2)
        )

        # Capture as string
        import io

        string_buffer = io.StringIO()
        string_console = rich.console.Console(file=string_buffer, legacy_windows=False)
        string_console.print(panel)
        return string_buffer.getvalue()

    def format_info_message(self, message: str, context: str | None = None) -> str:
        """Format info message for display."""
        if context:
            title_text = f"Information: {context}"
        else:
            title_text = "Information"

        panel = rich.panel.Panel(
            message, title=title_text, border_style="blue", padding=(1, 2)
        )

        # Capture as string
        import io

        string_buffer = io.StringIO()
        string_console = rich.console.Console(file=string_buffer, legacy_windows=False)
        string_console.print(panel)
        return string_buffer.getvalue()

    def _format_error_content(self, message: str, error_name: str) -> str:
        """Format the content of an error message."""
        content_lines = []

        # Main error message
        content_lines.append(f"[bold red]{message}[/bold red]")

        # Add error details for known error types
        if error_name == "ValidationError":
            content_lines.append("")
            content_lines.append(
                "[italic]This appears to be a validation error.[/italic]"
            )
            content_lines.append(
                "[italic]Please check that your transaction data is properly formatted.[/italic]"
            )

        elif error_name == "KeyError":
            content_lines.append("")
            content_lines.append("[italic]Required data is missing.[/italic]")
            content_lines.append(
                "[italic]Please ensure all required fields are present.[/italic]"
            )

        elif error_name == "ValueError":
            content_lines.append("")
            content_lines.append(
                "[italic]Invalid data values were encountered.[/italic]"
            )

        elif error_name == "IndexError":
            content_lines.append("")
            content_lines.append("[italic]Data structure issue detected.[/italic]")

        # Add general suggestion
        content_lines.append("")
        content_lines.append(
            "[dim]💡 Tip: Check the data format and ensure all required values are provided.[/dim]"
        )

        return "\n".join(content_lines)


class ErrorCollector:
    """Collects multiple errors during report generation."""

    def __init__(self) -> None:
        """Initialize error collector."""
        self.errors: list[tuple[Exception, str | None]] = []
        self.warnings: list[tuple[str, str | None]] = []

    def add_error(self, error: Exception, context: str | None = None) -> None:
        """Add an error to the collection."""
        self.errors.append((error, context))

    def add_warning(self, message: str, context: str | None = None) -> None:
        """Add a warning to the collection."""
        self.warnings.append((message, context))

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0

    def clear(self) -> None:
        """Clear all errors and warnings."""
        self.errors.clear()
        self.warnings.clear()

    def get_error_summary(self) -> str:
        """Get a summary of all errors."""
        if not self.errors:
            return "No errors occurred."

        lines = [f"[bold red]Found {len(self.errors)} error(s):[/bold red]"]
        lines.append("")

        for i, (error, context) in enumerate(self.errors, 1):
            context_str = f" (in {context})" if context else ""
            lines.append(
                f"  {i}. {error.__class__.__name__}: {str(error)}{context_str}"
            )

        return "\n".join(lines)

    def get_warning_summary(self) -> str:
        """Get a summary of all warnings."""
        if not self.warnings:
            return ""

        lines = [f"[yellow]Found {len(self.warnings)} warning(s):[/yellow]"]
        lines.append("")

        for i, (message, context) in enumerate(self.warnings, 1):
            context_str = f" (in {context})" if context else ""
            lines.append(f"  {i}. {message}{context_str}")

        return "\n".join(lines)

    def format_all_messages(self, handler: ErrorHandler) -> str:
        """Format all errors and warnings."""
        all_messages = []

        if self.has_errors():
            all_messages.append(self.get_error_summary())
            all_messages.append("\n")

        if self.has_warnings():
            all_messages.append(self.get_warning_summary())

        return "\n".join(all_messages)


def safe_execution(
    default_value: Any = None, error_context: str = ""
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for safe execution of formatting functions."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the error but don't fail the entire report
                handler = ErrorHandler()
                error_message = handler.format_error_message(e, error_context)
                print(error_message)
                return default_value

        return wrapper

    return decorator
