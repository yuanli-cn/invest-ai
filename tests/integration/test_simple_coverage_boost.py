"""
Simple integration tests to boost coverage of low-coverage modules.
Focus: Call actual public methods directly to exercise uncovered code paths.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import date

from invest_ai.reporting.templates import (
    AnnualReportTemplate,
    HistoryReportTemplate,
    DetailedReportTemplate,
    MarkdownReportTemplate,
    ReportTemplate,
)
from invest_ai.reporting.tables import TableFormatter, FinancialTableBuilder
from invest_ai.reporting.errors import (
    ErrorHandler,
    ErrorCollector,
    ReportingError,
    DataValidationError,
    FormattingError,
)
from invest_ai.transaction.models import TransactionType


class TestTemplatesSimpleCoverage:
    """Test templates.py module with simple direct method calls."""

    def test_annual_report_template_basic(self):
        """Test AnnualReportTemplate with minimal data."""
        template = AnnualReportTemplate()
        result = template.generate_text_report({
            "investment_type": "stock",
            "year": 2023,
            "start_value": 0.0,
            "end_value": 0.0,
            "net_gain": 0.0,
            "return_rate": 0.0,
        })
        assert result is not None
        assert "2023" in result

    def test_annual_report_template_with_dividends(self):
        """Test AnnualReportTemplate with dividends."""
        template = AnnualReportTemplate()
        result = template.generate_text_report({
            "investment_type": "stock",
            "year": 2023,
            "start_value": 1000.0,
            "end_value": 1500.0,
            "net_gain": 500.0,
            "return_rate": 50.0,
            "dividends": 100.0,
        })
        assert result is not None
        assert "100.00" in result  # Dividend amount

    def test_history_report_template_basic(self):
        """Test HistoryReportTemplate with minimal data."""
        template = HistoryReportTemplate()
        result = template.generate_text_report({
            "code": "000001",
            "investment_type": "stock",
            "total_invested": 0.0,
            "current_value": 0.0,
            "total_gain": 0.0,
        })
        assert result is not None
        assert "000001" in result

    def test_history_report_template_without_code(self):
        """Test HistoryReportTemplate without specific code."""
        template = HistoryReportTemplate()
        result = template.generate_text_report({
            "investment_type": "stock",
            "total_invested": 0.0,
            "current_value": 0.0,
            "total_gain": 0.0,
        })
        assert result is not None

    def test_detailed_report_template_basic(self):
        """Test DetailedReportTemplate with summary."""
        template = DetailedReportTemplate()
        result = template.generate_text_report({
            "summary": {
                "total_invested": 1000.0,
                "current_value": 1500.0,
                "total_gain": 500.0,
                "return_rate": 50.0,
            }
        })
        assert result is not None
        assert "Overall Summary" in result

    def test_detailed_report_template_with_investments(self):
        """Test DetailedReportTemplate with investments."""
        template = DetailedReportTemplate()
        result = template.generate_text_report({
            "summary": {},
            "investments": [
                {
                    "code": "000001",
                    "investment_type": "stock",
                    "total_invested": 1000.0,
                    "current_value": 1500.0,
                    "total_gain": 500.0,
                }
            ],
        })
        assert result is not None
        assert "Individual Investments" in result

    def test_markdown_report_template_annual(self):
        """Test MarkdownReportTemplate for annual reports."""
        template = MarkdownReportTemplate()
        result = template.generate_markdown_report({
            "investment_type": "stock",
            "year": 2023,
        }, "annual")
        assert result is not None
        assert "#" in result  # Markdown header

    def test_markdown_report_template_history(self):
        """Test MarkdownReportTemplate for history reports."""
        template = MarkdownReportTemplate()
        result = template.generate_markdown_report({
            "code": "000001",
            "investment_type": "stock",
        }, "history")
        assert result is not None

    def test_markdown_report_template_detailed(self):
        """Test MarkdownReportTemplate for detailed reports."""
        template = MarkdownReportTemplate()
        result = template.generate_markdown_report({
            "summary": {"total_invested": 1000.0},
        }, "detailed")
        assert result is not None

    def test_base_template_formatters(self):
        """Test ReportTemplate formatter methods."""
        template = ReportTemplate()

        # Test all formatters
        assert "¥1,000.00" == template.format_currency(1000.0)
        assert "+¥1,000.00" == template.format_gain_loss(1000.0)
        assert "-¥1,000.00" == template.format_gain_loss(-1000.0)
        assert "¥0.00" == template.format_gain_loss(0)
        assert "50.00%" == template.format_percentage(50.0)

        # Test date formatting
        test_date = date(2023, 1, 15)
        formatted = template.format_date(test_date)
        assert "2023-01-15" in formatted


class TestTablesSimpleCoverage:
    """Test tables.py module with direct method calls."""

    def test_table_formatter_currency_formatter(self):
        """Test TableFormatter.currency_formatter static method."""
        assert "¥1,000.00" == TableFormatter.currency_formatter(1000.0)
        assert "¥0.00" == TableFormatter.currency_formatter(0)
        assert "N/A" == TableFormatter.currency_formatter(None)

    def test_table_formatter_gain_loss_formatter(self):
        """Test TableFormatter.gain_loss_formatter static method."""
        assert "+¥1,000.00" == TableFormatter.gain_loss_formatter(1000.0)
        assert "-¥1,000.00" == TableFormatter.gain_loss_formatter(-1000.0)
        assert "¥0.00" == TableFormatter.gain_loss_formatter(0)

    def test_table_formatter_percentage_formatter(self):
        """Test TableFormatter.percentage_formatter static method."""
        assert "50.00%" == TableFormatter.percentage_formatter(50.0)
        assert "0.00%" == TableFormatter.percentage_formatter(0)

    def test_financial_table_builder_basic(self):
        """Test FinancialTableBuilder basic usage."""
        builder = FinancialTableBuilder()

        # Set properties
        result = builder.with_title("Test")
        assert result is builder  # Should return self

        result = builder.with_columns(["col1", "col2"])
        assert result is builder

        result = builder.with_data([{"col1": "val1", "col2": "val2"}])
        assert result is builder

        result = builder.with_header(True)
        assert result is builder

        result = builder.with_border_style("rounded")
        assert result is builder

        # Build should not fail
        table = builder.build()
        assert table is not None

    def test_financial_table_builder_with_formatting(self):
        """Test FinancialTableBuilder with column formatting."""
        builder = FinancialTableBuilder()

        builder.with_formatting("amount", formatter=str)
        table = builder.build()
        assert table is not None


class TestErrorsSimpleCoverage:
    """Test errors.py module with direct method calls."""

    def test_error_handler_format_error(self):
        """Test ErrorHandler.format_error_message."""
        handler = ErrorHandler()
        error = ValueError("Test error")
        result = handler.format_error_message(error, "test_context")
        assert result is not None
        assert "test_context" in result

    def test_error_handler_format_warning(self):
        """Test ErrorHandler.format_warning_message."""
        handler = ErrorHandler()
        result = handler.format_warning_message("Test warning", "test_context")
        assert result is not None
        assert "Warning" in result

    def test_error_handler_format_info(self):
        """Test ErrorHandler.format_info_message."""
        handler = ErrorHandler()
        result = handler.format_info_message("Test info", "test_context")
        assert result is not None
        assert "Information" in result

    def test_error_handler_format_error_content(self):
        """Test ErrorHandler._format_error_content for different error types."""
        handler = ErrorHandler()

        # Test ValueError
        result = handler._format_error_content("Invalid value", "ValueError")
        assert "Invalid value" in result

        # Test KeyError
        result = handler._format_error_content("Missing key", "KeyError")
        assert "Required data is missing" in result

        # Test ValidationError
        result = handler._format_error_content("Validation failed", "ValidationError")
        assert "Validation failed" in result

    def test_error_collector_basic(self):
        """Test ErrorCollector basic operations."""
        collector = ErrorCollector()

        # Initially no errors
        assert not collector.has_errors()
        assert not collector.has_warnings()

        # Add error
        collector.add_error(ValueError("Test error"), "context1")
        assert collector.has_errors()
        assert len(collector.errors) == 1

        # Add warning
        collector.add_warning("Test warning", "context2")
        assert collector.has_warnings()
        assert len(collector.warnings) == 1

        # Clear
        collector.clear()
        assert not collector.has_errors()
        assert not collector.has_warnings()

    def test_error_collector_summaries(self):
        """Test ErrorCollector summary methods."""
        collector = ErrorCollector()

        # No errors summary
        summary = collector.get_error_summary()
        assert "No errors occurred" in summary

        # Add errors and get summary
        collector.add_error(ValueError("Error 1"), "ctx1")
        collector.add_error(KeyError("Error 2"), "ctx2")

        summary = collector.get_error_summary()
        assert "Found 2 error(s)" in summary

        # Warnings summary
        collector.add_warning("Warning 1", "ctx3")
        summary = collector.get_warning_summary()
        assert "Found 1 warning(s)" in summary

    def test_error_collector_format_all(self):
        """Test ErrorCollector.format_all_messages."""
        collector = ErrorCollector()
        handler = ErrorHandler()

        collector.add_error(ValueError("Test error"), "ctx")
        collector.add_warning("Test warning", "ctx")

        result = collector.format_all_messages(handler)
        assert result is not None

    def test_reporting_errors(self):
        """Test custom error classes."""
        assert issubclass(ReportingError, Exception)
        assert issubclass(DataValidationError, ReportingError)
        assert issubclass(FormattingError, ReportingError)

        # Test raising errors
        try:
            raise DataValidationError("Test")
        except DataValidationError as e:
            assert str(e) == "Test"


class TestTransactionModelsSimpleCoverage:
    """Test transaction/models.py module."""

    def test_transaction_type_values(self):
        """Test TransactionType enum values."""
        assert TransactionType.BUY.value == "buy"
        assert TransactionType.SELL.value == "sell"
        assert TransactionType.DIVIDEND.value == "dividend"


class TestIntegratedRealUsage:
    """Test real-world usage patterns."""

    @pytest.mark.asyncio
    async def test_templates_with_real_calculation_result(self):
        """Test templates with actual calculation result structure."""
        from invest_ai.models import AnnualResult

        result = AnnualResult(
            code="000001",
            year=2023,
            start_value=1000.0,
            end_value=1250.0,
            net_gain=250.0,
            return_rate=25.0,
            dividends=50.0,
            capital_gain=200.0,
        )

        template = AnnualReportTemplate()
        report = template.generate_text_report(result.__dict__)

        assert report is not None
        assert "2023" in report
        assert "25.00%" in report
        assert "1,250.00" in report

    def test_error_handling_in_templates(self):
        """Test template handling of edge cases."""
        template = AnnualReportTemplate()

        # Test with missing optional fields
        report = template.generate_text_report({
            "investment_type": "stock",
            "year": 2023,
            "start_value": 0,
            "end_value": 0,
            "net_gain": 0,
            "return_rate": 0,
        })
        assert report is not None

    def test_table_formatter_with_various_values(self):
        """Test table formatter with various numeric values."""
        formatter = TableFormatter()

        # Test edge cases for formatters
        assert "N/A" == TableFormatter.currency_formatter(None)
        assert "0.00%" == TableFormatter.percentage_formatter(0)
        # Zero returns "¥0.00" (no sign), not "-¥0.00"
        assert "¥0.00" == TableFormatter.gain_loss_formatter(0)