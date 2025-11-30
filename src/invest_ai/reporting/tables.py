"""Table formatting utilities for reports."""

from collections.abc import Callable
from typing import Any

import rich.table
import rich.text
from rich.table import Table


class TableFormatter:
    """Utility class for creating formatted tables."""

    def __init__(self) -> None:
        """Initialize table formatter."""
        self.default_style = "rounded"
        self.default_header_style = "bold cyan"
        self.default_title_style = "bold yellow"

    def create_simple_table(
        self,
        headers: list[str],
        rows: list[list[Any]],
        title: str | None = None,
        show_header: bool = True,
        border_style: str | None = None,
    ) -> rich.table.Table:
        """Create a simple formatted table."""
        table = Table(
            title=title,
            show_header=show_header,
            box=None,  # Use default
            header_style=self.default_header_style,
            title_style=self.default_title_style if title else None,
        )

        # Add columns
        for header in headers:
            table.add_column(header)

        # Add rows
        for row in rows:
            table.add_row(*row)

        return table

    def create_metric_table(
        self,
        metrics: dict[str, Any],
        title: str | None = None,
        show_header: bool = False,
    ) -> rich.table.Table:
        """Create a table for displaying metrics."""
        table = self.create_simple_table(
            headers=["Metric", "Value"],
            rows=[[key, str(value)] for key, value in metrics.items()],
            title=title,
            show_header=show_header,
        )
        return table

    def create_financial_table(
        self,
        data: list[dict[str, Any]],
        columns: list[str],
        title: str | None = None,
        format_functions: dict[str, Callable[[Any], str]] | None = None,
    ) -> rich.table.Table:
        """Create a financial data table with formatting."""
        if not format_functions:
            format_functions = {}

        # Add columns
        table = rich.table.Table(
            title=title,
            show_header=True,
            box=rich.table.box.ROUNDED,
            header_style="bold cyan",
        )

        for column in columns:
            # Simple default formatting since format_functions stores Callables
            table.add_column(column, justify="left")

        # Add rows
        for row_data in data:
            formatted_row = []
            for column in columns:
                value = row_data.get(column, "")
                formatter = format_functions.get(column)
                if formatter and callable(formatter):
                    value = formatter(value)
                formatted_row.append(str(value))
            table.add_row(*formatted_row)

        return table

    def create_summary_table(
        self,
        title: str,
        data: dict[str, Any],
        formatting: dict[str, dict] | None = None,
    ) -> rich.table.Table:
        """Create a summary table from data dictionary."""
        if not formatting:
            formatting = {}

        rows = []
        for key, value in data.items():
            style = formatting.get(key, {}).get("style", "bold cyan")
            formatter = formatting.get(key, {}).get("formatter", str)
            rows.append([rich.text.Text(f"{key}:", style=style), formatter(value)])

        table = rich.table.Table(title=title, show_header=False, box=None)
        table.add_column("Metric", width=25, style="bold cyan")
        table.add_column("Value", width=20, justify="right")

        for row in rows:
            table.add_row(*row)

        return table

    @staticmethod
    def currency_formatter(value: float | None) -> str:
        """Format currency values."""
        return f"¥{abs(value):,.2f}" if value is not None else "N/A"

    @staticmethod
    def gain_loss_formatter(value: float | None) -> str:
        """Format gain/loss with sign."""
        if value is None:
            return "N/A"
        if value > 0:
            return f"+¥{value:,.2f}"
        elif value < 0:
            return f"-¥{abs(value):,.2f}"
        else:
            return "¥0.00"

    @staticmethod
    def percentage_formatter(value: float) -> str:
        """Format percentage values."""
        return f"{value:.2f}%" if value is not None else "N/A"

    @staticmethod
    def bold_formatter(value: Any) -> rich.text.Text:
        """Format bold text."""
        return rich.text.Text(str(value), style="bold")

    @staticmethod
    def color_formatter(value: Any, color: str = "cyan") -> rich.text.Text:
        """Format colored text."""
        return rich.text.Text(str(value), style=color)


class FinancialTableBuilder:
    """Builder for financial tables with predefined formatting."""

    def __init__(self) -> None:
        """Initialize the builder."""
        self.title: str | None = None
        self.columns: list[str] = []
        self.data: list[dict[str, Any]] = []
        self.formatting: dict[str, dict] = {
            "amount": {
                "formatter": TableFormatter.currency_formatter,
                "justify": "right",
            },
            "value": {
                "formatter": TableFormatter.currency_formatter,
                "justify": "right",
            },
            "gain_loss": {
                "formatter": TableFormatter.gain_loss_formatter,
                "justify": "right",
            },
            "return_rate": {
                "formatter": TableFormatter.percentage_formatter,
                "justify": "right",
            },
            "percent": {
                "formatter": TableFormatter.percentage_formatter,
                "justify": "right",
            },
            "code": {"style": "bold", "header_style": "bold cyan"},
            "name": {"style": "italic"},
            "type": {"style": "italic"},
        }
        self.show_header: bool = True
        self.border_style: str = "rounded"

    def with_title(self, title: str) -> "FinancialTableBuilder":
        """Set table title."""
        self.title = title
        return self

    def with_columns(self, columns: list[str]) -> "FinancialTableBuilder":
        """Set table columns."""
        self.columns = columns
        return self

    def with_data(self, data: list[dict[str, Any]]) -> "FinancialTableBuilder":
        """Set table data."""
        self.data = data
        return self

    def with_formatting(self, column: str, **kwargs: Any) -> "FinancialTableBuilder":
        """Add formatting for a specific column."""
        if column not in self.formatting:
            self.formatting[column] = {}
        self.formatting[column].update(kwargs)
        return self

    def with_header(self, show: bool = True) -> "FinancialTableBuilder":
        """Set header visibility."""
        self.show_header = show
        return self

    def with_border_style(self, style: str) -> "FinancialTableBuilder":
        """Set border style."""
        self.border_style = style
        return self

    def build(self) -> rich.table.Table:
        """Build the final table."""
        formatter = TableFormatter()
        # Extract only the formatter functions for each column
        format_functions: dict[str, Callable[[Any], str]] = {}
        for column, config in self.formatting.items():
            if "formatter" in config:
                format_functions[column] = config["formatter"]

        return formatter.create_financial_table(
            columns=self.columns,
            data=self.data,
            title=self.title,
            format_functions=format_functions,
        )

    def __enter__(self) -> "FinancialTableBuilder":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
