"""Tests for path auto-detection."""

import pytest
from pathlib import Path
from vendor_automator.vendor_automator import (
    get_dummy_site_path,
    get_dummy_site_url,
    PathError,
)


def test_get_dummy_site_path_exists():
    """Test that dummy_site path is correctly detected."""
    path = get_dummy_site_path()

    assert path is not None
    assert isinstance(path, str)
    assert Path(path).exists()
    assert Path(path).is_dir()
    assert Path(path).name == "dummy_site"


def test_get_dummy_site_path_is_absolute():
    """Test that returned path is absolute."""
    path = get_dummy_site_path()

    assert Path(path).is_absolute()


def test_get_dummy_site_url_returns_file_url():
    """Test that dummy_site URL is correctly formatted."""
    url = get_dummy_site_url()

    assert url.startswith("file://")
    assert url.endswith("login.html")


def test_get_dummy_site_url_is_valid():
    """Test that returned URL points to existing file."""
    url = get_dummy_site_url()

    # Convert file:// URL to path (handle Windows paths with drive letters)
    file_path = url.replace("file:///", "").replace("file://", "")
    # On Windows, file:///C:/path becomes C:/path, convert to backslashes
    file_path = file_path.replace("/", "\\")
    assert Path(file_path).exists()


def test_dummy_site_contains_login_html():
    """Test that dummy_site contains login.html."""
    path = get_dummy_site_path()
    login_file = Path(path) / "login.html"

    assert login_file.exists()
    assert login_file.is_file()


def test_dummy_site_contains_dashboard_html():
    """Test that dummy_site contains dashboard.html."""
    path = get_dummy_site_path()
    dashboard_file = Path(path) / "dashboard.html"

    assert dashboard_file.exists()
    assert dashboard_file.is_file()
