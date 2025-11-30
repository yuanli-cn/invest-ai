"""Tests for transaction loader module."""

import pytest
from datetime import date
import tempfile
import os

from invest_ai.transaction.loader import TransactionLoader
from invest_ai.models import TransactionType


class TestTransactionLoader:
    """Tests for TransactionLoader class."""

    def test_init(self):
        """Test initialization."""
        loader = TransactionLoader()
        assert loader is not None

    @pytest.mark.asyncio
    async def test_load_simple_yaml(self, tmp_path):
        """Test loading simple YAML file."""
        yaml_content = """
transactions:
  - code: "000001"
    date: "2023-01-15"
    type: buy
    quantity: 100
    unit_price: 10.0
    total_amount: 1000
"""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(yaml_content)
        
        loader = TransactionLoader()
        result = await loader.load_transactions(str(yaml_file))
        
        assert result is not None
        assert len(result.transactions) == 1
        assert result.transactions[0].code == "000001"

    @pytest.mark.asyncio
    async def test_load_yaml_with_dividends(self, tmp_path):
        """Test loading YAML with dividend transactions."""
        yaml_content = """
transactions:
  - code: "000001"
    date: "2023-01-15"
    type: buy
    quantity: 100
    unit_price: 10.0
    total_amount: 1000
  - code: "000001"
    date: "2023-06-15"
    type: dividend
    quantity: 0
    unit_price: 0
    total_amount: 50
    dividend_type: cash
"""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(yaml_content)
        
        loader = TransactionLoader()
        result = await loader.load_transactions(str(yaml_file))
        
        assert result is not None
        assert len(result.transactions) == 2
        assert result.transactions[1].type == TransactionType.DIVIDEND

    @pytest.mark.asyncio
    async def test_load_yaml_not_found(self):
        """Test loading non-existent file."""
        loader = TransactionLoader()
        
        with pytest.raises(FileNotFoundError):
            await loader.load_transactions("/nonexistent/file.yaml")

    @pytest.mark.asyncio
    async def test_load_yaml_not_a_file(self, tmp_path):
        """Test loading a directory instead of file."""
        loader = TransactionLoader()
        
        with pytest.raises(ValueError, match="not a file"):
            await loader.load_transactions(str(tmp_path))

    @pytest.mark.asyncio
    async def test_load_yaml_empty(self, tmp_path):
        """Test loading empty YAML file."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")
        
        loader = TransactionLoader()
        result = await loader.load_transactions(str(yaml_file))
        
        # Should return empty list or raise error
        assert result is not None

    @pytest.mark.asyncio
    async def test_load_yaml_list_format(self, tmp_path):
        """Test loading YAML with list format."""
        yaml_content = """
- code: "000001"
  date: "2023-01-15"
  type: buy
  quantity: 100
  unit_price: 10.0
  total_amount: 1000
"""
        yaml_file = tmp_path / "list.yaml"
        yaml_file.write_text(yaml_content)
        
        loader = TransactionLoader()
        result = await loader.load_transactions(str(yaml_file))
        
        assert result is not None
        assert len(result.transactions) >= 1

    @pytest.mark.asyncio
    async def test_load_yaml_with_sell(self, tmp_path):
        """Test loading YAML with sell transaction."""
        yaml_content = """
transactions:
  - code: "000001"
    date: "2023-01-15"
    type: buy
    quantity: 100
    unit_price: 10.0
    total_amount: 1000
  - code: "000001"
    date: "2023-06-15"
    type: sell
    quantity: 50
    unit_price: 12.0
    total_amount: 600
"""
        yaml_file = tmp_path / "sell.yaml"
        yaml_file.write_text(yaml_content)
        
        loader = TransactionLoader()
        result = await loader.load_transactions(str(yaml_file))
        
        assert result is not None
        assert len(result.transactions) == 2
        assert result.transactions[1].type == TransactionType.SELL
