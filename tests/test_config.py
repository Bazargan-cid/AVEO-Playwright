"""Tests for configuration management."""

import os
import pytest
from pathlib import Path
from vendor_automator.vendor_automator import (
    load_config,
    ConfigurationError,
)


@pytest.mark.asyncio
async def test_load_config_with_valid_env(tmp_path, monkeypatch):
    """Test loading valid configuration from .env file."""
    # Set environment variables directly
    monkeypatch.setenv("USERNAME", "testuser")
    monkeypatch.setenv("PASSWORD", "testpass")
    monkeypatch.setenv("BASE_URL", "http://example.com")
    monkeypatch.setenv("HEADLESS", "true")
    monkeypatch.setenv("TIMEOUT", "30")

    config = await load_config()

    assert config["username"] == "testuser"
    assert config["password"] == "testpass"
    assert config["base_url"] == "http://example.com"
    assert config["headless"] is True
    assert config["timeout"] == 30


@pytest.mark.asyncio
async def test_load_config_missing_username(monkeypatch):
    """Test that ConfigurationError is raised when USERNAME is missing."""
    monkeypatch.delenv("USERNAME", raising=False)
    monkeypatch.setenv("PASSWORD", "testpass")
    monkeypatch.setenv("BASE_URL", "http://example.com")

    with pytest.raises(ConfigurationError):
        await load_config()


@pytest.mark.asyncio
async def test_load_config_missing_password(monkeypatch):
    """Test that ConfigurationError is raised when PASSWORD is missing."""
    monkeypatch.setenv("USERNAME", "testuser")
    monkeypatch.delenv("PASSWORD", raising=False)
    monkeypatch.setenv("BASE_URL", "http://example.com")

    with pytest.raises(ConfigurationError):
        await load_config()


@pytest.mark.asyncio
async def test_load_config_missing_base_url(monkeypatch):
    """Test that ConfigurationError is raised when BASE_URL is missing."""
    monkeypatch.setenv("USERNAME", "testuser")
    monkeypatch.setenv("PASSWORD", "testpass")
    monkeypatch.delenv("BASE_URL", raising=False)

    with pytest.raises(ConfigurationError):
        await load_config()


@pytest.mark.asyncio
async def test_load_config_default_headless(monkeypatch):
    """Test that HEADLESS defaults to true."""
    monkeypatch.setenv("USERNAME", "testuser")
    monkeypatch.setenv("PASSWORD", "testpass")
    monkeypatch.setenv("BASE_URL", "http://example.com")
    monkeypatch.delenv("HEADLESS", raising=False)

    config = await load_config()

    assert config["headless"] is True


@pytest.mark.asyncio
async def test_load_config_headless_false(monkeypatch):
    """Test that HEADLESS can be set to false."""
    monkeypatch.setenv("USERNAME", "testuser")
    monkeypatch.setenv("PASSWORD", "testpass")
    monkeypatch.setenv("BASE_URL", "http://example.com")
    monkeypatch.setenv("HEADLESS", "false")

    config = await load_config()

    assert config["headless"] is False


@pytest.mark.asyncio
async def test_load_config_default_timeout(monkeypatch):
    """Test that TIMEOUT defaults to 30."""
    monkeypatch.setenv("USERNAME", "testuser")
    monkeypatch.setenv("PASSWORD", "testpass")
    monkeypatch.setenv("BASE_URL", "http://example.com")
    monkeypatch.delenv("TIMEOUT", raising=False)

    config = await load_config()

    assert config["timeout"] == 30


@pytest.mark.asyncio
async def test_load_config_custom_timeout(monkeypatch):
    """Test that TIMEOUT can be customized."""
    monkeypatch.setenv("USERNAME", "testuser")
    monkeypatch.setenv("PASSWORD", "testpass")
    monkeypatch.setenv("BASE_URL", "http://example.com")
    monkeypatch.setenv("TIMEOUT", "60")

    config = await load_config()

    assert config["timeout"] == 60
