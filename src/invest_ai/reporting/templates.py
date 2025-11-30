"""Report templates and formatting utilities."""

from datetime import date
from typing import Any


class ReportTemplate:
    """Base class for report templates."""

    def __init__(self) -> None:
        """Initialize template."""
        self.currency_symbol = "¥"
        self.date_format = "%Y-%m-%d"
        self.percentage_format = "{:.2f}%"
        self.currency_format = "{:,.2f}"
        self.gain_loss_format = "{:+,.2f}"

    def format_currency(self, value: float) -> str:
        """Format currency value."""
        return f"{self.currency_symbol}{self.currency_format.format(abs(value))}"

    def format_gain_loss(self, value: float) -> str:
        """Format gain/loss with sign and currency."""
        if value > 0:
            return f"+{self.currency_symbol}{self.currency_format.format(value)}"
        elif value < 0:
            return f"-{self.currency_symbol}{self.currency_format.format(abs(value))}"
        else:
            return f"{self.currency_symbol}{self.currency_format.format(0)}"

    def format_percentage(self, value: float) -> str:
        """Format percentage value."""
        return self.percentage_format.format(value)

    def format_date(self, date_obj: date) -> str:
        """Format date."""
        return date_obj.strftime(self.date_format)


class AnnualReportTemplate(ReportTemplate):
    """Template for annual performance reports."""

    def generate_text_report(self, data: dict[str, Any]) -> str:
        """Generate text-based annual report."""
        lines = []

        # Header
        lines.append(f"{'='*50}")
        lines.append(
            f"{data.get('investment_type', 'Investments').title()} - {data.get('year', 'N/A')} Performance"
        )
        lines.append(f"{'='*50}")
        lines.append("")

        # Summary
        lines.append("Summary:")
        lines.append(
            f"  Start Value:      {self.format_currency(data.get('start_value', 0))}"
        )
        lines.append(
            f"  End Value:        {self.format_currency(data.get('end_value', 0))}"
        )
        lines.append(
            f"  Net Gain/Loss:    {self.format_gain_loss(data.get('net_gain', 0))}"
        )
        lines.append(
            f"  Return Rate:      {self.format_percentage(data.get('return_rate', 0))}"
        )

        if data.get("dividends", 0) > 0:
            lines.append(
                f"  Dividend Income:  {self.format_currency(data.get('dividends', 0))}"
            )

        lines.append("")
        return "\n".join(lines)


class HistoryReportTemplate(ReportTemplate):
    """Template for complete history reports."""

    def generate_text_report(self, data: dict[str, Any]) -> str:
        """Generate text-based history report."""
        lines = []

        # Header
        code = data.get("code", "")
        investment_type = data.get("investment_type", "Investments")
        if code:
            lines.append(f"{'='*50}")
            lines.append(
                f"{investment_type.title()}: {code} - Complete Investment History"
            )
            lines.append(f"{'='*50}")
        else:
            lines.append(f"{'='*50}")
            lines.append(f"{investment_type.title()} Investments - Complete History")
            lines.append(f"{'='*50}")

        lines.append("")

        # Time period
        lines.append("Investment Period:")
        lines.append(f"  First Investment: {data.get('first_investment', 'N/A')}")
        lines.append(f"  Last Transaction:  {data.get('last_transaction', 'N/A')}")
        lines.append(f"  Current Date:     {date.today().strftime(self.date_format)}")
        lines.append("")

        # Summary
        lines.append("Portfolio Summary:")
        lines.append(
            f"  Total Invested:   {self.format_currency(data.get('total_invested', 0))}"
        )
        lines.append(
            f"  Current Value:    {self.format_currency(data.get('current_value', 0))}"
        )
        lines.append(
            f"  Total P&L:        {self.format_gain_loss(data.get('total_gain', 0))}"
        )
        lines.append(
            f"  Return Rate:      {self.format_percentage(data.get('return_rate', 0))}"
        )

        # Gains breakdown
        lines.append("")
        lines.append("Gains Breakdown:")
        lines.append(
            f"  Realized Gains:   {self.format_gain_loss(data.get('realized_gains', 0))}"
        )
        lines.append(
            f"  Unrealized Gains: {self.format_gain_loss(data.get('unrealized_gains', 0))}"
        )

        if data.get("dividend_income", 0) > 0:
            lines.append(
                f"  Dividend Income:  {self.format_currency(data.get('dividend_income', 0))}"
            )

        lines.append(f"  Total Transactions: {data.get('transaction_count', 0)}")
        lines.append("")

        return "\n".join(lines)


class DetailedReportTemplate(ReportTemplate):
    """Template for detailed reports with individual investments."""

    def generate_text_report(self, data: dict[str, Any]) -> str:
        """Generate detailed text report."""
        lines = []

        # Main summary
        summary = data.get("summary", {})
        if summary:
            lines.append("Overall Summary:")
            lines.append(
                f"  Total Invested:   {self.format_currency(summary.get('total_invested', 0))}"
            )
            lines.append(
                f"  Current Value:    {self.format_currency(summary.get('current_value', 0))}"
            )
            lines.append(
                f"  Total P&L:        {self.format_gain_loss(summary.get('total_gain', 0))}"
            )
            lines.append(
                f"  Return Rate:      {self.format_percentage(summary.get('return_rate', 0))}"
            )
            lines.append("")

        # Individual investments
        investments = data.get("investments", [])
        if investments:
            lines.append("Individual Investments:")
            lines.append("-" * 50)

            for i, inv in enumerate(investments, 1):
                lines.append(f"{i}. {inv.get('code', 'N/A')}")
                lines.append(f"   Type:           {inv.get('investment_type', 'N/A')}")
                lines.append(
                    f"   Invested:       {self.format_currency(inv.get('total_invested', 0))}"
                )

                current_value = inv.get("current_value")
                if current_value is not None:
                    lines.append(
                        f"   Current Value:  {self.format_currency(current_value)}"
                    )
                else:
                    lines.append("   Current Value:  N/A")

                lines.append(
                    f"   P&L:            {self.format_gain_loss(inv.get('total_gain', 0))}"
                )
                lines.append(
                    f"   Return Rate:    {self.format_percentage(inv.get('return_rate', 0))}"
                )

                if i < len(investments):
                    lines.append("")

        return "\n".join(lines)


class MarkdownReportTemplate(ReportTemplate):
    """Template for Markdown format reports."""

    def generate_markdown_report(
        self, data: dict[str, Any], report_type: str = "annual"
    ) -> str:
        """Generate Markdown format report."""
        if report_type == "annual":
            return self._markdown_annual(data)
        elif report_type == "history":
            return self._markdown_history(data)
        else:
            return self._markdown_detailed(data)

    def _markdown_annual(self, data: dict[str, Any]) -> str:
        """Generate Markdown annual report."""
        title = f"# {data.get('investment_type', 'Investments').title()} - {data.get('year', 'N/A')} Performance\n"

        summary = f"""
## Summary

| Metric | Value |
|--------|-------|
| Start Value | {self.format_currency(data.get('start_value', 0))} |
| End Value | {self.format_currency(data.get('end_value', 0))} |
| Net Gain/Loss | {self.format_gain_loss(data.get('net_gain', 0))} |
| Return Rate | {self.format_percentage(data.get('return_rate', 0))} |
"""
        if data.get("dividends", 0) > 0:
            summary += f"| Dividend Income | {self.format_currency(data.get('dividends', 0))} |\n"
        else:
            summary += "\n"

        return title + summary

    def _markdown_history(self, data: dict[str, Any]) -> str:
        """Generate Markdown history report."""
        code = f" - {data.get('code', '')}" if data.get("code") else ""
        title = f"# {data.get('investment_type', 'Investments').title()} - Complete Investment History{code}\n"

        period = f"""
## Investment Period

- **First Investment**: {data.get('first_investment', 'N/A')}
- **Last Transaction**: {data.get('last_transaction', 'N/A')}
- **Current Date**: {date.today().strftime(self.date_format)}

## Portfolio Summary

| Metric | Value |
|--------|-------|
| Total Invested | {self.format_currency(data.get('total_invested', 0))} |
| Current Value | {self.format_currency(data.get('current_value', 0))} |
| Total P&L | {self.format_gain_loss(data.get('total_gain', 0))} |
| Return Rate | {self.format_percentage(data.get('return_rate', 0))} |

## Gains Breakdown

| Category | Amount |
|----------|--------|
| Realized Gains | {self.format_gain_loss(data.get('realized_gains', 0))} |
| Unrealized Gains | {self.format_gain_loss(data.get('unrealized_gains', 0))} |
"""
        if data.get("dividend_income", 0) > 0:
            period += f"| Dividend Income | {self.format_currency(data.get('dividend_income', 0))} |\n"
        else:
            period += "\n"

        period += f"| Total Transactions | {data.get('transaction_count', 0)} |\n"

        return title + period

    def _markdown_detailed(self, data: dict[str, Any]) -> str:
        """Generate Markdown detailed report."""
        title = "# Detailed Investment Report\n"

        # Summary section
        summary = data.get("summary", {})
        summary_section = ""
        if summary:
            summary_section = f"""
## Overall Summary

| Metric | Value |
|--------|-------|
| Total Invested | {self.format_currency(summary.get('total_invested', 0))} |
| Current Value | {self.format_currency(summary.get('current_value', 0))} |
| Total P&L | {self.format_gain_loss(summary.get('total_gain', 0))} |
| Return Rate | {self.format_percentage(summary.get('return_rate', 0))} |

"""
        # Individual investments
        investments = data.get("investments", [])
        investments_section = ""
        if investments:
            investments_section = "## Individual Investments\n\n| Code | Type | Invested | Current Value | P&L | Return Rate |\n|------|------|----------|----------------|-----|-------------|\n"

            for inv in investments:
                current_value = inv.get("current_value")
                current_value_str = (
                    self.format_currency(current_value)
                    if current_value is not None
                    else "N/A"
                )

                investments_section += f"| {inv.get('code', 'N/A')} | {inv.get('investment_type', 'N/A')} | {self.format_currency(inv.get('total_invested', 0))} | {current_value_str} | {self.format_gain_loss(inv.get('total_gain', 0))} | {self.format_percentage(inv.get('return_rate', 0))} |\n"

        return title + summary_section + investments_section
