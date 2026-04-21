"""Tests for retry logic and exponential backoff."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from vendor_automator.vendor_automator import retry


@pytest.mark.asyncio
async def test_retry_succeeds_on_first_attempt():
    """Test that function succeeds on first attempt without retry."""

    @retry(max_attempts=3, base_delay=0.01, backoff_factor=2)
    async def successful_function():
        return "success"

    result = await successful_function()
    assert result == "success"


@pytest.mark.asyncio
async def test_retry_succeeds_after_timeout_error():
    """Test that function retries on TimeoutError."""
    call_count = 0

    @retry(max_attempts=3, base_delay=0.01, backoff_factor=2)
    async def failing_then_succeeding():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise TimeoutError("Timeout")
        return "success"

    result = await failing_then_succeeding()
    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_succeeds_after_connection_error():
    """Test that function retries on ConnectionError."""
    call_count = 0

    @retry(max_attempts=3, base_delay=0.01, backoff_factor=2)
    async def failing_then_succeeding():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ConnectionError("Connection failed")
        return "success"

    result = await failing_then_succeeding()
    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_fails_after_max_attempts():
    """Test that function fails after max retry attempts."""

    @retry(max_attempts=3, base_delay=0.01, backoff_factor=2)
    async def always_failing():
        raise TimeoutError("Always fails")

    with pytest.raises(TimeoutError):
        await always_failing()


@pytest.mark.asyncio
async def test_retry_fails_immediately_on_non_retriable_error():
    """Test that non-retriable errors fail immediately without retry."""
    call_count = 0

    @retry(max_attempts=3, base_delay=0.01, backoff_factor=2)
    async def non_retriable_error():
        nonlocal call_count
        call_count += 1
        raise ValueError("Non-retriable error")

    with pytest.raises(ValueError):
        await non_retriable_error()

    # Should only be called once (no retry)
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_exponential_backoff_timing():
    """Test that retry uses exponential backoff timing."""
    call_times = []

    @retry(max_attempts=3, base_delay=0.05, backoff_factor=2)
    async def failing_function():
        call_times.append(asyncio.get_event_loop().time())
        if len(call_times) < 3:
            raise TimeoutError("Timeout")
        return "success"

    result = await failing_function()
    assert result == "success"

    # Check that delays are approximately exponential
    if len(call_times) >= 2:
        delay1 = call_times[1] - call_times[0]
        assert delay1 >= 0.04  # ~0.05s with tolerance

    if len(call_times) >= 3:
        delay2 = call_times[2] - call_times[1]
        assert delay2 >= 0.09  # ~0.1s with tolerance


@pytest.mark.asyncio
async def test_retry_with_custom_max_attempts():
    """Test that custom max_attempts is respected."""
    call_count = 0

    @retry(max_attempts=5, base_delay=0.01, backoff_factor=2)
    async def failing_function():
        nonlocal call_count
        call_count += 1
        raise TimeoutError("Timeout")

    with pytest.raises(TimeoutError):
        await failing_function()

    assert call_count == 5
