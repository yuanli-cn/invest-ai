"""Tests for config modules."""

import pytest
import os
from unittest.mock import patch

from invest_ai.config.settings import load_settings, Settings
from invest_ai.config.api_config import create_api_config


class TestSettings:
    """Tests for Settings class."""

    def test_load_settings(self):
        """Test loading settings."""
        settings = load_settings()
        assert settings is not None

    def test_settings_has_debug(self):
        """Test settings has debug attribute."""
        settings = load_settings()
        assert hasattr(settings, 'debug')

    def test_tushare_configured_property(self):
        """Test tushare_configured property reflects token state."""
        settings = load_settings()
        # tushare_configured should be True if token is set, False otherwise
        assert settings.tushare_configured == bool(settings.tushare_token)

    def test_tushare_configured_returns_bool(self):
        """Test tushare_configured returns a boolean."""
        settings = load_settings()
        assert isinstance(settings.tushare_configured, bool)


class TestApiConfig:
    """Tests for ApiConfig class."""

    def test_create_api_config(self):
        """Test creating API config."""
        config = create_api_config()
        assert config is not None

    def test_api_config_has_tushare(self):
        """Test API config has tushare settings."""
        config = create_api_config()
        assert hasattr(config, 'tushare')

    def test_api_config_has_eastmoney(self):
        """Test API config has eastmoney settings."""
        config = create_api_config()
        assert hasattr(config, 'eastmoney')
