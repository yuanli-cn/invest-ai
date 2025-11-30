"""Tests for CLI arguments module."""

import pytest
from unittest.mock import patch
import sys

from invest_ai.cli.arguments import (
    parse_arguments,
    create_argument_parser,
    validate_arguments,
    get_usage_examples,
    print_help_summary,
)


class TestParseArguments:
    """Tests for parse_arguments function."""

    def test_parse_basic_args(self):
        """Test parsing basic arguments."""
        args = parse_arguments(["--type", "stock", "--data", "test.yaml"])
        assert args.type == "stock"
        assert args.data == "test.yaml"

    def test_parse_with_code(self):
        """Test parsing with code argument."""
        args = parse_arguments(["--type", "stock", "--data", "test.yaml", "--code", "000001"])
        assert args.code == "000001"

    def test_parse_with_year(self):
        """Test parsing with year argument."""
        args = parse_arguments(["--type", "stock", "--data", "test.yaml", "--year", "2023"])
        assert args.year == 2023

    def test_parse_with_format(self):
        """Test parsing with format argument."""
        args = parse_arguments(["--type", "fund", "--data", "test.yaml", "--format", "json"])
        assert args.format == "json"

    def test_parse_default_format(self):
        """Test default format is table."""
        args = parse_arguments(["--type", "stock", "--data", "test.yaml"])
        assert args.format == "table"

    def test_parse_verbose(self):
        """Test parsing verbose flag."""
        args = parse_arguments(["--type", "stock", "--data", "test.yaml", "--verbose"])
        assert args.verbose is True


class TestCreateArgumentParser:
    """Tests for create_argument_parser function."""

    def test_parser_description(self):
        """Test parser has description."""
        parser = create_argument_parser()
        assert "investment profit and loss" in parser.description.lower()


class TestValidateArguments:
    """Tests for validate_arguments function."""

    def test_valid_arguments(self, tmp_path):
        """Test validation with valid arguments."""
        # Create a temp file
        test_file = tmp_path / "test.yaml"
        test_file.write_text("transactions: []")
        
        args = parse_arguments(["--type", "stock", "--data", str(test_file)])
        result = validate_arguments(args)
        assert result is True

    def test_invalid_file_not_exists(self):
        """Test validation with non-existent file."""
        args = parse_arguments(["--type", "stock", "--data", "/nonexistent/file.yaml"])
        result = validate_arguments(args)
        assert result is False

    def test_invalid_code_format(self, tmp_path):
        """Test validation with invalid code format."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("transactions: []")
        
        # Special characters in code
        args = parse_arguments(["--type", "stock", "--data", str(test_file), "--code", "abc123"])
        result = validate_arguments(args)
        # abc123 contains letters and numbers which is caught
        assert result is False

    def test_invalid_year_too_old(self, tmp_path):
        """Test validation with year too old."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("transactions: []")
        
        args = parse_arguments(["--type", "stock", "--data", str(test_file), "--year", "1985"])
        result = validate_arguments(args)
        assert result is False

    def test_invalid_year_future(self, tmp_path):
        """Test validation with future year."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("transactions: []")
        
        args = parse_arguments(["--type", "stock", "--data", str(test_file), "--year", "2099"])
        result = validate_arguments(args)
        assert result is False


class TestGetUsageExamples:
    """Tests for get_usage_examples function."""

    def test_returns_list(self):
        """Test returns a list of examples."""
        examples = get_usage_examples()
        assert isinstance(examples, list)
        assert len(examples) > 0

    def test_examples_have_invest_ai(self):
        """Test examples contain invest-ai."""
        examples = get_usage_examples()
        for example in examples:
            assert "invest-ai" in example


class TestPrintHelpSummary:
    """Tests for print_help_summary function."""

    def test_prints_output(self, capsys):
        """Test that it prints output."""
        print_help_summary()
        captured = capsys.readouterr()
        assert "invest-ai" in captured.out
        assert "--type" in captured.out
