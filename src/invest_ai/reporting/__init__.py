"""Reporting module for invest-ai."""

from .errors import (
    DataValidationError,
    ErrorCollector,
    ErrorHandler,
    FormattingError,
    IncompleteDataError,
    ReportingError,
    safe_execution,
)
from .reports import ReportGenerator
from .tables import FinancialTableBuilder, TableFormatter
from .templates import (
    AnnualReportTemplate,
    DetailedReportTemplate,
    HistoryReportTemplate,
    MarkdownReportTemplate,
    ReportTemplate,
)

__all__ = [
    "ReportGenerator",
    "ReportTemplate",
    "AnnualReportTemplate",
    "HistoryReportTemplate",
    "DetailedReportTemplate",
    "MarkdownReportTemplate",
    "TableFormatter",
    "FinancialTableBuilder",
    "ReportingError",
    "DataValidationError",
    "FormattingError",
    "IncompleteDataError",
    "ErrorHandler",
    "ErrorCollector",
    "safe_execution",
]
