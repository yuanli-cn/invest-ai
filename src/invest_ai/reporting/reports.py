"""Report generation and formatting."""

import io as stringio
import json
from datetime import date

import rich.console
import rich.panel
import rich.table
import rich.text

from invest_ai.models import (
    AnnualResult,
    CalculationResult,
    HistoryResult,
)


class ReportGenerator:
    """Generates formatted reports for investment calculations."""

    def __init__(self) -> None:
        """Initialize the report generator."""
        self.console = rich.console.Console()

    async def format_annual_report(
        self,
        result: AnnualResult,
        investment_type: str,
        year: int,
        code: str | None = None,
    ) -> str:
        """Format annual performance report."""
        title = self._get_annual_report_title(investment_type, year, code)

        # Create main results section
        main_results = self._create_annual_results_table(result)

        # Add individual investments if available
        details = ""
        if hasattr(result, 'investments') and result.investments:
            details = self._create_individual_investments_table(result.investments)

        # Create panel content
        content = f"{main_results}\n\n{details}" if details else main_results

        panel = rich.panel.Panel(
            content, title=title, border_style="blue", padding=(1, 2)
        )

        # Capture console output as string

        import io as stringio

        from rich.console import Console

        string_buffer = stringio.StringIO()
        string_console = Console(file=string_buffer, legacy_windows=False)
        string_console.print(panel)
        return string_buffer.getvalue()

    async def format_portfolio_annual_report(
        self, result: AnnualResult, investment_type: str, year: int
    ) -> str:
        """Format portfolio annual report."""
        return await self.format_annual_report(result, investment_type, year)

    async def format_history_report(
        self, result: HistoryResult, investment_type: str, code: str | None = None
    ) -> str:
        """Format complete history report."""
        title = self._get_history_report_title(investment_type, code)

        # Create main summary
        main_summary = self._create_history_summary_table(result)

        # Add individual investments if available
        details = ""
        if hasattr(result, 'investments') and result.investments:
            details = self._create_individual_investments_table(result.investments)

        content = f"{main_summary}\n\n{details}" if details else main_summary

        panel = rich.panel.Panel(
            content, title=title, border_style="green", padding=(1, 2)
        )

        # Capture console output

        import io as stringio

        from rich.console import Console

        string_buffer = stringio.StringIO()
        string_console = Console(file=string_buffer, legacy_windows=False)
        string_console.print(panel)
        return string_buffer.getvalue()

    async def format_portfolio_history_report(
        self, result: HistoryResult, investment_type: str
    ) -> str:
        """Format portfolio history report."""
        return await self.format_history_report(result, investment_type)

    async def format_json_report(self, result: dict) -> str:
        """Format result as JSON."""
        return json.dumps(result, indent=2, default=str, ensure_ascii=False)

    def _get_annual_report_title(
        self, investment_type: str, year: int, code: str | None = None
    ) -> str:
        """Generate title for annual report."""
        if code:
            return f"{investment_type.title()} {code} - {year} Performance"
        else:
            return f"{investment_type.title()} Investments - {year} Performance"

    def _get_history_report_title(
        self, investment_type: str, code: str | None = None
    ) -> str:
        """Generate title for history report."""
        if code:
            return f"{investment_type.title()} {code} - Complete Investment History"
        else:
            return f"{investment_type.title()} Investments - Complete History"

    def _create_annual_results_table(self, result: AnnualResult) -> str:
        """Create table showing annual results."""
        table = rich.table.Table(show_header=False, box=None)
        table.add_column("Metric", style="bold cyan", width=20)
        table.add_column("Value", justify="right", width=15)

        table.add_row("Start Value:", f"¥{result.start_value:,.2f}")
        table.add_row("End Value:", f"¥{result.end_value:,.2f}")
        table.add_row("Net Gain/Loss:", self._format_gain_loss(result.net_gain))
        table.add_row("XIRR (Annual):", f"{result.return_rate:.2f}%")

        if result.dividends > 0:
            table.add_row("Dividend Income:", f"¥{result.dividends:,.2f}")

        # Capture table as string

        from rich.console import Console

        output = stringio.StringIO()
        string_console = Console(file=output, legacy_windows=False)
        string_console.print(table)
        return output.getvalue()

    def _create_history_summary_table(self, result: HistoryResult) -> str:
        """Create table showing history summary."""
        table = rich.table.Table(show_header=False, box=None)
        table.add_column("Metric", style="bold green", width=20)
        table.add_column("Value", justify="right", width=15)

        table.add_row("First Investment:", result.first_investment.strftime("%Y-%m-%d"))
        table.add_row("Current Date:", date.today().strftime("%Y-%m-%d"))
        table.add_row("Total Invested:", f"¥{result.total_invested:,.2f}")
        table.add_row("Current Value:", f"¥{result.current_value:,.2f}")
        table.add_row("Total P&L:", self._format_gain_loss(result.total_gain))
        table.add_row("XIRR (Annual):", f"{result.return_rate:.2f}%")
        table.add_row("Realized Gains:", f"¥{result.realized_gains:,.2f}")
        table.add_row("Unrealized Gains:", f"¥{result.unrealized_gains:,.2f}")

        if result.dividend_income > 0:
            table.add_row("Dividend Income:", f"¥{result.dividend_income:,.2f}")

        table.add_row("Total Transactions:", f"{result.transaction_count}")

        # Capture table as string

        from rich.console import Console

        output = stringio.StringIO()
        string_console = Console(file=output, legacy_windows=False)
        string_console.print(table)
        return output.getvalue()

    def _create_individual_investments_table(
        self, investments: list[CalculationResult]
    ) -> str:
        """Create table for individual investments."""
        if not investments:
            return ""

        # Create title
        title = rich.text.Text("Individual Investments", style="bold yellow")
        from rich.console import Console

        title_buffer = stringio.StringIO()
        title_console = Console(file=title_buffer, legacy_windows=False)
        title_console.print(title)
        title_str = title_buffer.getvalue()

        # Create table
        table = rich.table.Table(
            show_header=True, box=rich.table.box.ROUNDED, header_style="bold cyan"
        )
        table.add_column("Code", style="bold")
        table.add_column("Invested", justify="right")
        table.add_column("Current Value", justify="right")
        table.add_column("Total P&L", justify="right")
        table.add_column("Return Rate", justify="right")

        for investment in investments:
            table.add_row(
                investment.code,
                f"¥{investment.total_invested:,.2f}",
                (
                    f"¥{investment.current_value:,.2f}"
                    if investment.current_value
                    else "N/A"
                ),
                self._format_gain_loss(investment.total_gain),
                f"{investment.return_rate:.2f}%",
            )

        # Add summary row
        total_invested = sum(inv.total_invested for inv in investments)
        total_value = sum(inv.current_value or 0 for inv in investments)
        total_gain = sum(inv.total_gain for inv in investments)

        table.add_row("", "", "", "", "", style="dim")
        table.add_row(
            "TOTAL",
            f"¥{total_invested:,.2f}",
            f"¥{total_value:,.2f}",
            self._format_gain_loss(total_gain),
            "",
            style="bold",
        )

        # Capture as string
        from rich.console import Console

        output = stringio.StringIO()
        string_console = Console(file=output, legacy_windows=False)
        string_console.print(table)
        return title_str + output.getvalue()

    def _format_gain_loss(self, value: float) -> str:
        """Format gain/loss with appropriate color."""
        formatted = f"¥{abs(value):,.2f}"
        if value > 0:
            return f"+{formatted}"
        elif value < 0:
            return f"-{formatted}"
        else:
            return formatted

    def format_error_report(self, error: Exception, context: str) -> str:
        """Format error report."""
        panel = rich.panel.Panel(
            f"[bold red]Error in {context}:[/bold red]\n\n{str(error)}",
            title="Calculation Error",
            border_style="red",
            padding=(1, 2),
        )

        import io as stringio

        from rich.console import Console

        string_buffer = stringio.StringIO()
        string_console = Console(file=string_buffer, legacy_windows=False)
        string_console.print(panel)
        return string_buffer.getvalue()

    def format_summary_table(self, results: list[CalculationResult]) -> str:
        """Format summary table for multiple results."""
        if not results:
            return "No investment results available."

        table = rich.table.Table(
            title="Investment Summary",
            show_header=True,
            box=rich.table.box.ROUNDED,
            header_style="bold cyan",
        )
        table.add_column("Code", style="bold")
        table.add_column("Type", style="italic")
        table.add_column("Invested", justify="right")
        table.add_column("Current Value", justify="right")
        table.add_column("P&L", justify="right")
        table.add_column("Return Rate", justify="right")

        for result in results:
            table.add_row(
                result.code,
                result.investment_type.value,
                f"¥{result.total_invested:,.2f}",
                f"¥{result.current_value:,.2f}" if result.current_value else "N/A",
                self._format_gain_loss(result.total_gain),
                f"{result.return_rate:.2f}%",
            )

        # Summary row
        total_invested = sum(r.total_invested for r in results)
        total_value = sum(r.current_value or 0 for r in results)
        total_gain = sum(r.total_gain for r in results)

        table.add_row("", "", "", "", "", "", style="dim")
        table.add_row(
            "TOTAL",
            "",
            f"¥{total_invested:,.2f}",
            f"¥{total_value:,.2f}",
            self._format_gain_loss(total_gain),
            "",
            style="bold",
        )

        # Capture as string

        from rich.console import Console

        output = stringio.StringIO()
        string_console = Console(file=output, legacy_windows=False)
        string_console.print(table)
        return output.getvalue()
