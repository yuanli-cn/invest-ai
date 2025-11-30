"""Tests for reporting modules."""

import pytest
from datetime import date

from invest_ai.models import AnnualResult, HistoryResult
from invest_ai.reporting.errors import (
    ErrorHandler,
    ErrorCollector,
    ReportingError,
    DataValidationError,
    FormattingError,
)
from invest_ai.reporting.tables import TableFormatter, FinancialTableBuilder
from invest_ai.reporting.templates import (
    AnnualReportTemplate,
    HistoryReportTemplate,
)


class TestErrorHandler:
    """Tests for ErrorHandler class."""

    def test_init(self):
        """Test initialization."""
        handler = ErrorHandler()
        assert handler is not None
        assert handler.console is not None

    def test_format_error_message(self):
        """Test format_error_message method."""
        handler = ErrorHandler()
        result = handler.format_error_message(ValueError("test error"))
        assert result is not None
        assert "test error" in result.lower() or "error" in result.lower()

    def test_format_warning_message(self):
        """Test format_warning_message method."""
        handler = ErrorHandler()
        result = handler.format_warning_message("test warning")
        assert result is not None


class TestErrorCollector:
    """Tests for ErrorCollector class."""

    def test_init(self):
        """Test initialization."""
        collector = ErrorCollector()
        assert collector.errors is not None
        assert collector.warnings is not None

    def test_add_error(self):
        """Test add_error method."""
        collector = ErrorCollector()
        collector.add_error(ValueError("Test error"))
        assert len(collector.errors) == 1

    def test_add_warning(self):
        """Test add_warning method."""
        collector = ErrorCollector()
        collector.add_warning("Test warning")
        assert len(collector.warnings) == 1

    def test_has_errors(self):
        """Test has_errors method."""
        collector = ErrorCollector()
        assert collector.has_errors() is False
        
        collector.add_error(ValueError("Test error"))
        assert collector.has_errors() is True

    def test_has_warnings(self):
        """Test has_warnings method."""
        collector = ErrorCollector()
        assert collector.has_warnings() is False
        
        collector.add_warning("Test warning")
        assert collector.has_warnings() is True

    def test_clear(self):
        """Test clear method."""
        collector = ErrorCollector()
        collector.add_error(ValueError("Test error"))
        collector.add_warning("Test warning")
        
        collector.clear()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

    def test_get_error_summary(self):
        """Test get_error_summary method."""
        collector = ErrorCollector()
        collector.add_error(ValueError("Test error"))
        summary = collector.get_error_summary()
        assert "error" in summary.lower()

    def test_get_warning_summary(self):
        """Test get_warning_summary method."""
        collector = ErrorCollector()
        collector.add_warning("Test warning")
        summary = collector.get_warning_summary()
        assert "warning" in summary.lower()


class TestReportingError:
    """Tests for ReportingError exception."""

    def test_init(self):
        """Test initialization."""
        error = ReportingError("Test error")
        assert str(error) == "Test error"


class TestDataValidationError:
    """Tests for DataValidationError exception."""

    def test_init(self):
        """Test initialization."""
        error = DataValidationError("Validation failed")
        assert str(error) == "Validation failed"


class TestFormattingError:
    """Tests for FormattingError exception."""

    def test_init(self):
        """Test initialization."""
        error = FormattingError("Format error")
        assert str(error) == "Format error"


class TestTableFormatter:
    """Tests for TableFormatter class."""

    def test_init(self):
        """Test initialization."""
        formatter = TableFormatter()
        assert formatter is not None


class TestFinancialTableBuilder:
    """Tests for FinancialTableBuilder class."""

    def test_init(self):
        """Test initialization."""
        builder = FinancialTableBuilder()
        assert builder is not None


class TestAnnualReportTemplate:
    """Tests for AnnualReportTemplate class."""

    def test_init(self):
        """Test initialization."""
        template = AnnualReportTemplate()
        assert template is not None

    def test_generate_text_report(self):
        """Test generate_text_report method."""
        template = AnnualReportTemplate()
        data = {
            "investment_type": "stock",
            "year": 2023,
            "start_value": 10000.0,
            "end_value": 12000.0,
            "net_gain": 2000.0,
            "return_rate": 20.0,
        }
        result = template.generate_text_report(data)
        assert result is not None
        assert "2023" in result

    def test_generate_text_report_with_dividends(self):
        """Test generate_text_report with dividends."""
        template = AnnualReportTemplate()
        data = {
            "investment_type": "stock",
            "year": 2023,
            "start_value": 10000.0,
            "end_value": 12000.0,
            "net_gain": 2000.0,
            "return_rate": 20.0,
            "dividends": 500.0,
        }
        result = template.generate_text_report(data)
        assert result is not None


class TestHistoryReportTemplate:
    """Tests for HistoryReportTemplate class."""

    def test_init(self):
        """Test initialization."""
        template = HistoryReportTemplate()
        assert template is not None

    def test_generate_text_report(self):
        """Test generate_text_report method."""
        template = HistoryReportTemplate()
        data = {
            "investment_type": "stock",
            "total_invested": 10000.0,
            "current_value": 12000.0,
            "total_gain": 2000.0,
            "return_rate": 20.0,
        }
        result = template.generate_text_report(data)
        assert result is not None
