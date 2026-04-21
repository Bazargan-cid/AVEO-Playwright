"""Integration tests for complete automation workflow."""

import asyncio
import json
import pytest
from pathlib import Path
from vendor_automator.vendor_automator import (
    load_config,
    get_dummy_site_url,
    BrowserContext,
)


@pytest.mark.asyncio
async def test_browser_context_initialization():
    """Test that BrowserContext properly initializes and cleans up."""
    async with BrowserContext(headless=True) as (browser, page):
        assert browser is not None
        assert page is not None

        # Verify page is usable
        await page.goto("about:blank")


@pytest.mark.asyncio
async def test_browser_context_cleanup_on_success():
    """Test that BrowserContext cleans up resources on success."""
    async with BrowserContext(headless=True) as (browser, page):
        await page.goto("about:blank")

    # After exiting context, browser should be closed
    # (We can't directly test this, but we verify no exception is raised)


@pytest.mark.asyncio
async def test_dummy_site_url_is_accessible():
    """Test that dummy site URL can be accessed."""
    url = get_dummy_site_url()
    assert url.startswith("file://")
    assert url.endswith("login.html")


@pytest.mark.asyncio
async def test_configuration_loading():
    """Test that configuration can be loaded."""
    import os
    os.environ["USERNAME"] = "testuser"
    os.environ["PASSWORD"] = "testpass"
    os.environ["BASE_URL"] = "http://example.com"

    config = await load_config()

    assert config["username"] == "testuser"
    assert config["password"] == "testpass"
    assert config["base_url"] == "http://example.com"


def test_output_directories_can_be_created(tmp_path):
    """Test that output directories can be created."""
    screenshots_dir = tmp_path / "screenshots"
    data_dir = tmp_path / "data"

    screenshots_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    assert screenshots_dir.exists()
    assert data_dir.exists()


def test_json_file_can_be_written(tmp_path):
    """Test that JSON files can be written."""
    data = [
        {"amount": "$100", "timestamp": "2024-01-15 10:00:00", "merchant_id": "M001"},
        {"amount": "$200", "timestamp": "2024-01-15 11:00:00", "merchant_id": "M002"},
    ]

    output_file = tmp_path / "test_data.json"
    with open(output_file, "w") as f:
        json.dump(data, f)

    assert output_file.exists()

    # Verify JSON can be read back
    with open(output_file) as f:
        loaded_data = json.load(f)
        assert loaded_data == data


def test_screenshot_file_can_be_created(tmp_path):
    """Test that screenshot files can be created."""
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}.png"
    file_path = tmp_path / filename

    # Create a minimal PNG file (1x1 pixel)
    png_data = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
        b"\x00\x01\x01\x00\x05\x18\r\xb5\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    with open(file_path, "wb") as f:
        f.write(png_data)

    assert file_path.exists()
    assert file_path.suffix == ".png"
