"""
Integration tests for reporting module.
Target: Boost coverage of reporting/tables.py and reporting/templates.py
"""

import pytest
from datetime import date
from unittest.mock import MagicMock

from invest_ai.reporting.tables import TableFormatter, FinancialTableBuilder
from invest_ai.reporting.templates import (
    AnnualReportTemplate,
    HistoryReportTemplate,
    DetailedReportTemplate,
    MarkdownReportTemplate,
)
from invest_ai.reporting.errors import ErrorHandler, ErrorCollector


class TestTableFormatterCoverage:
    """Test TableFormatter to boost coverage."""

    def test_create_simple_table(self):
        """Test creating a simple table."""
        formatter = TableFormatter()

        headers = ["Metric", "Value"]
        rows = [["Start Value", "1000.00"]]

        table = formatter.create_simple_table(
            headers=headers,
            rows=rows,
            title="Test Table",
            show_header=True,
        )

        assert table is not None

    def test_create_metric_table(self):
        """Test creating a metric table."""
        formatter = TableFormatter()

        metrics = {
            "Start Value": 1000.0,
            "End Value": 1250.0,
            "Net Gain": 250.0,
        }

        table = formatter.create_metric_table(metrics, title="Metrics")
        assert table is not None

    def test_create_financial_table(self):
        """Test creating a financial table."""
        formatter = TableFormatter()

        data = [
            {"code": "000001", "total_invested": 10000.0, "current_value": 12500.0},
        ]
        columns = ["code", "total_invested", "current_value"]

        table = formatter.create_financial_table(
            data=data,
            columns=columns,
            title="Financial Data",
        )

        assert table is not None

    def test_create_summary_table(self):
        """Test creating a summary table."""
        formatter = TableFormatter()

        data = {
            "Total Invested": 10000.0,
            "Current Value": 12500.0,
        }

        table = formatter.create_summary_table(title="Summary", data=data)
        assert table is not None

    def test_currency_formatter(self):
        """Test currency formatter."""
        assert "¥1,000.00" == TableFormatter.currency_formatter(1000.0)
        assert "N/A" == TableFormatter.currency_formatter(None)

    def test_gain_loss_formatter(self):
        """Test gain/loss formatter."""
        assert "+¥1,000.00" == TableFormatter.gain_loss_formatter(1000.0)
        assert "-¥1,000.00" == TableFormatter.gain_loss_formatter(-1000.0)
        assert "¥0.00" == TableFormatter.gain_loss_formatter(0)

    def test_percentage_formatter(self):
        """Test percentage formatter."""
        assert "25.00%" == TableFormatter.percentage_formatter(25.0)
        assert "0.00%" == TableFormatter.percentage_formatter(0)

    def test_bold_formatter(self):
        """Test bold formatter."""
        text = TableFormatter.bold_formatter("Test")
        assert str(text) == "Test"

    def test_color_formatter(self):
        """Test color formatter."""
        text = TableFormatter.color_formatter("Test", color="red")
        assert str(text) == "Test"


class TestFinancialTableBuilder:
    """Test FinancialTableBuilder."""

    def test_builder_with_title(self):
        """Test builder with title."""
        builder = FinancialTableBuilder()

        result = builder.with_title("Test Title")
        assert result is builder
        assert builder.title == "Test Title"

    def test_builder_with_columns(self):
        """Test builder with columns."""
        builder = FinancialTableBuilder()

        result = builder.with_columns(["col1", "col2"])
        assert result is builder
        assert builder.columns == ["col1", "col2"]

    def test_builder_with_data(self):
        """Test builder with data."""
        builder = FinancialTableBuilder()

        data = [{"col1": "val1"}]
        result = builder.with_data(data)
        assert result is builder
        assert builder.data == data

    def test_builder_with_formatting(self):
        """Test builder with formatting."""
        builder = FinancialTableBuilder()

        result = builder.with_formatting("amount", formatter=str)
        assert result is builder
        assert "amount" in builder.formatting

    def test_builder_with_header(self):
        """Test builder with header."""
        builder = FinancialTableBuilder()

        result = builder.with_header(False)
        assert result is builder
        assert builder.show_header is False

    def test_builder_with_border_style(self):
        """Test builder with border style."""
        builder = FinancialTableBuilder()

        result = builder.with_border_style("square")
        assert result is builder
        assert builder.border_style == "square"

    def test_builder_build(self):
        """Test building the table."""
        builder = FinancialTableBuilder()

        data = [{"code": "000001", "value": 1000.0}]
        table = (
            builder.with_title("Test")
            .with_columns(["code", "value"])
            .with_data(data)
            .build()
        )

        assert table is not None

    def test_builder_context_manager(self):
        """Test builder as context manager."""
        builder = FinancialTableBuilder()

        data = [{"code": "000001", "value": 1000.0}]
        with builder as b:
            b.with_columns(["code", "value"]).with_data(data)

        assert builder.columns == ["code", "value"]


class TestReportTemplates:
    """Test report templates."""

    def test_annual_report_template(self):
        """Test AnnualReportTemplate."""
        template = AnnualReportTemplate()

        data = {
            "investment_type": "stock",
            "year": 2023,
            "start_value": 1000.0,
            "end_value": 1250.0,
            "net_gain": 250.0,
            "return_rate": 25.0,
            "dividends": 50.0,
        }

        result = template.generate_text_report(data)
        assert result is not None
        assert "2023" in result
        assert "25.00%" in result

    def test_annual_report_template_no_dividends(self):
        """Test AnnualReportTemplate without dividends."""
        template = AnnualReportTemplate()

        data = {
            "investment_type": "stock",
            "year": 2023,
            "start_value": 1000.0,
            "end_value": 1100.0,
            "net_gain": 100.0,
            "return_rate": 10.0,
        }

        result = template.generate_text_report(data)
        assert result is not None
        assert "2023" in result

    def test_history_report_template_with_code(self):
        """Test HistoryReportTemplate with code."""
        template = HistoryReportTemplate()

        data = {
            "code": "000001",
            "investment_type": "stock",
            "total_invested": 10000.0,
            "current_value": 12500.0,
            "total_gain": 2500.0,
            "return_rate": 25.0,
            "realized_gains": 1000.0,
            "unrealized_gains": 1500.0,
            "dividend_income": 500.0,
            "transaction_count": 5,
        }

        result = template.generate_text_report(data)
        assert result is not None
        assert "000001" in result
        assert "10,000.00" in result

    def test_history_report_template_portfolio(self):
        """Test HistoryReportTemplate for portfolio (no code)."""
        template = HistoryReportTemplate()

        data = {
            "investment_type": "stock",
            "total_invested": 20000.0,
            "current_value": 25000.0,
            "total_gain": 5000.0,
        }

        result = template.generate_text_report(data)
        assert result is not None
        assert "Portfolio" in result

    def test_detailed_report_template(self):
        """Test DetailedReportTemplate."""
        template = DetailedReportTemplate()

        data = {
            "summary": {
                "total_invested": 20000.0,
                "current_value": 25000.0,
                "total_gain": 5000.0,
                "return_rate": 25.0,
            },
            "investments": [
                {
                    "code": "000001",
                    "investment_type": "stock",
                    "total_invested": 10000.0,
                    "current_value": 12500.0,
                    "total_gain": 2500.0,
                    "return_rate": 25.0,
                }
            ],
        }

        result = template.generate_text_report(data)
        assert result is not None
        assert "Overall Summary" in result
        assert "Individual Investments" in result

    def test_detailed_report_template_empty_investments(self):
        """Test DetailedReportTemplate with no investments."""
        template = DetailedReportTemplate()

        data = {
            "summary": {
                "total_invested": 0.0,
                "current_value": 0.0,
                "total_gain": 0.0,
            },
            "investments": [],
        }

        result = template.generate_text_report(data)
        assert result is not None

    def test_markdown_report_annual(self):
        """Test MarkdownReportTemplate for annual reports."""
        template = MarkdownReportTemplate()

        data = {
            "investment_type": "stock",
            "year": 2023,
            "start_value": 1000.0,
            "end_value": 1250.0,
            "net_gain": 250.0,
            "return_rate": 25.0,
            "dividends": 50.0,
        }

        result = template.generate_markdown_report(data, report_type="annual")
        assert result is not None
        assert "#" in result  # Markdown header
        assert "2023" in result

    def test_markdown_report_history(self):
        """Test MarkdownReportTemplate for history reports."""
        template = MarkdownReportTemplate()

        data = {
            "code": "000001",
            "investment_type": "stock",
            "total_invested": 10000.0,
        }

        result = template.generate_markdown_report(data, report_type="history")
        assert result is not None

    def test_markdown_report_detailed(self):
        """Test MarkdownReportTemplate for detailed reports."""
        template = MarkdownReportTemplate()

        data = {
            "summary": {"total_invested": 10000.0},
            "investments": [],
        }

        result = template.generate_markdown_report(data, report_type="detailed")
        assert result is not None


class TestErrorHandler:
    """Test ErrorHandler for coverage."""

    def test_format_error_message(self):
        """Test error message formatting."""
        handler = ErrorHandler()

        error = ValueError("Test error")
        result = handler.format_error_message(error, "test_context")
        assert result is not None
        assert "test_context" in result
        assert "Test error" in result

    def test_format_warning_message(self):
        """Test warning message formatting."""
        handler = ErrorHandler()

        result = handler.format_warning_message("Test warning", "context")
        assert result is not None
        assert "Warning" in result

    def test_format_info_message(self):
        """Test info message formatting."""
        handler = ErrorHandler()

        result = handler.format_info_message("Test info", "context")
        assert result is not None
        assert "Information" in result

    def test_format_error_content_value_error(self):
        """Test error content formatting for ValueError."""
        handler = ErrorHandler()

        result = handler._format_error_content("Invalid value", "ValueError")
        assert "Invalid value" in result
        assert "Invalid data values" in result

    def test_format_error_content_key_error(self):
        """Test error content formatting for KeyError."""
        handler = ErrorHandler()

        result = handler._format_error_content("Missing key", "KeyError")
        assert "Missing key" in result
        assert "Required data is missing" in result

    def test_format_error_content_validation_error(self):
        """Test error content formatting for ValidationError."""
        handler = ErrorHandler()

        result = handler._format_error_content("Validation failed", "ValidationError")
        assert "Validation failed" in result
        assert "properly formatted" in result


class TestErrorCollector:
    """Test ErrorCollector for coverage."""

    def test_add_error(self):
        """Test adding error."""
        collector = ErrorCollector()

        collector.add_error(ValueError("test error"), "context")
        assert collector.has_errors()
        assert len(collector.errors) == 1

    def test_add_warning(self):
        """Test adding warning."""
        collector = ErrorCollector()

        collector.add_warning("test warning", "context")
        assert collector.has_warnings()
        assert len(collector.warnings) == 1

    def test_clear(self):
        """Test clearing errors and warnings."""
        collector = ErrorCollector()

        collector.add_error(ValueError("test"), "ctx")
        collector.add_warning("test", "ctx")

        collector.clear()
        assert not collector.has_errors()
        assert not collector.has_warnings()

    def test_get_error_summary(self):
        """Test error summary."""
        collector = ErrorCollector()

        summary = collector.get_error_summary()
        assert "No errors occurred" in summary

        collector.add_error(ValueError("Error 1"), "ctx1")
        summary = collector.get_error_summary()
        assert "Found 1 error(s)" in summary

    def test_get_warning_summary(self):
        """Test warning summary."""
        collector = ErrorCollector()

        collector.add_warning("Warning 1", "ctx1")
        summary = collector.get_warning_summary()
        assert "Found 1 warning(s)" in summary

    def test_format_all_messages(self):
        """Test formatting all messages."""
        collector = ErrorCollector()
        handler = ErrorHandler()

        collector.add_error(ValueError("Error"), "ctx")
        collector.add_warning("Warning", "ctx")

        result = collector.format_all_messages(handler)
        assert result is not None