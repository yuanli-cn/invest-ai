"""Tests for market client modules with mocking."""

import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock

from invest_ai.market.fund_client import EastMoneyClient
from invest_ai.market.price_fetcher import PriceFetcher


class TestEastMoneyClient:
    """Tests for EastMoneyClient class."""

    def test_init(self):
        """Test initialization."""
        client = EastMoneyClient()
        assert client is not None

    def test_session_created(self):
        """Test session is created."""
        client = EastMoneyClient()
        assert client.session is not None


class TestPriceFetcher:
    """Tests for PriceFetcher class."""

    def test_init(self):
        """Test initialization."""
        fetcher = PriceFetcher()
        assert fetcher is not None

    def test_eastmoney_client_created(self):
        """Test EastMoney client is created."""
        fetcher = PriceFetcher()
        assert fetcher.eastmoney_client is not None
