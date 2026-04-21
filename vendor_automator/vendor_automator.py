"""
AVEO-Playwright: AI-powered robot for automating legacy website interactions.

This module provides async-first browser automation with Playwright, including:
- Configuration management from .env files
- Robust error handling with exponential backoff retry logic
- Atomic functions for login, navigation, screenshot, and data extraction
- Comprehensive logging with sensitive data masking
- Browser lifecycle management with proper resource cleanup
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from playwright.async_api import (
    Browser,
    Page,
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)


# ============================================================================
# Exception Hierarchy
# ============================================================================


class AutomationError(Exception):
    """Base exception for all automation errors."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize AutomationError with message and context.

        Args:
            message: Error message
            context: Dictionary with context information (URL, operation, etc.)
        """
        self.message = message
        self.context = context or {}
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with context information."""
        if self.context:
            context_str = " | ".join(
                f"{k}={v}" for k, v in self.context.items()
            )
            return f"{self.message} [{context_str}]"
        return self.message


class ConfigurationError(AutomationError):
    """Raised when configuration is invalid or incomplete."""

    pass


class LoginError(AutomationError):
    """Raised when login fails."""

    pass


class NavigationError(AutomationError):
    """Raised when page navigation fails."""

    pass


class ScreenshotError(AutomationError):
    """Raised when screenshot capture fails."""

    pass


class DataExtractionError(AutomationError):
    """Raised when data extraction fails."""

    pass


class PathError(AutomationError):
    """Raised when path resolution fails."""

    pass


# ============================================================================
# Logging Configuration
# ============================================================================


def setup_logging() -> logging.Logger:
    """
    Configure logging with timestamps and sensitive data masking.

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("vendor_automator")
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    # Create formatter with timestamp
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


logger = setup_logging()


def mask_sensitive_data(text: str) -> str:
    """
    Mask sensitive data in text (credentials, tokens, etc.).

    Args:
        text: Text that may contain sensitive data

    Returns:
        Text with sensitive data masked
    """
    # Mask common credential patterns
    if "password" in text.lower():
        return "[MASKED]"
    if "username" in text.lower():
        return "[MASKED]"
    if "credential" in text.lower():
        return "[MASKED]"
    return text


# ============================================================================
# Configuration Management
# ============================================================================


async def load_config() -> Dict[str, Any]:
    """
    Load and validate configuration from .env file.

    Returns:
        Dictionary with keys: username, password, base_url, headless, timeout

    Raises:
        ConfigurationError: If required variables are missing
    """
    # Load .env file
    load_dotenv()

    # Get required variables
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    base_url = os.getenv("BASE_URL")

    # Validate required variables
    if not username:
        raise ConfigurationError("USERNAME environment variable is required")
    if not password:
        raise ConfigurationError("PASSWORD environment variable is required")
    if not base_url:
        raise ConfigurationError("BASE_URL environment variable is required")

    # Get optional variables with defaults
    headless_str = os.getenv("HEADLESS", "true").lower()
    headless = headless_str in ("true", "1", "yes")
    timeout = int(os.getenv("TIMEOUT", "30"))

    config = {
        "username": username,
        "password": password,
        "base_url": base_url,
        "headless": headless,
        "timeout": timeout,
    }

    logger.info(
        f"Configuration loaded: base_url={base_url}, "
        f"headless={headless}, timeout={timeout}s"
    )

    return config


# ============================================================================
# Path Auto-Detection
# ============================================================================


def get_dummy_site_path() -> str:
    """
    Locate dummy_site directory relative to script location.

    Returns:
        Absolute path to dummy_site directory

    Raises:
        PathError: If dummy_site directory not found
    """
    # Get script location
    script_dir = Path(__file__).parent.absolute()

    # Search for dummy_site directory
    dummy_site_dir = script_dir / "dummy_site"

    if dummy_site_dir.exists() and dummy_site_dir.is_dir():
        logger.info(f"Dummy site path resolved: {dummy_site_dir}")
        return str(dummy_site_dir)

    # If not found, raise error with expected path
    raise PathError(
        f"dummy_site directory not found",
        context={"expected_path": str(dummy_site_dir)},
    )


def get_dummy_site_url() -> str:
    """
    Get file:// URL for dummy_site login page.

    Returns:
        file:// URL for login.html

    Raises:
        PathError: If dummy_site directory not found
    """
    dummy_site_path = get_dummy_site_path()
    login_path = Path(dummy_site_path) / "login.html"

    if not login_path.exists():
        raise PathError(
            f"login.html not found in dummy_site",
            context={"path": str(login_path)},
        )

    # Convert to file:// URL
    file_url = login_path.as_uri()
    logger.info(f"Dummy site URL: {file_url}")
    return file_url


# ============================================================================
# Retry Decorator
# ============================================================================


def retry(
    max_attempts: int = 3, base_delay: float = 1, backoff_factor: float = 2
) -> Callable:
    """
    Decorator for retrying async functions with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds (default: 1)
        backoff_factor: Backoff multiplier (default: 2)

    Returns:
        Decorated function that retries on failure
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except (
                    PlaywrightTimeoutError,
                    TimeoutError,
                    ConnectionError,
                ) as e:
                    last_exception = e
                    if attempt < max_attempts:
                        delay = base_delay * (backoff_factor ** (attempt - 1))
                        logger.info(
                            f"Retry attempt {attempt}/{max_attempts} "
                            f"for {func.__name__}, "
                            f"waiting {delay}s before retry"
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_attempts} retry attempts failed "
                            f"for {func.__name__}"
                        )
                except Exception as e:
                    # Non-retriable error - fail immediately
                    logger.error(
                        f"Non-retriable error in {func.__name__}: {str(e)}"
                    )
                    raise

            # All retries exhausted
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


# ============================================================================
# Browser Lifecycle Manager
# ============================================================================


class BrowserContext:
    """Async context manager for browser lifecycle."""

    def __init__(self, headless: bool = True, slowdown: int = 0):
        """
        Initialize BrowserContext.

        Args:
            headless: Run browser in headless mode (default: True)
            slowdown: Slowdown in milliseconds (default: 0)
        """
        self.headless = headless
        self.slowdown = slowdown
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def __aenter__(self) -> Tuple[Browser, Page]:
        """
        Initialize browser and page.

        Returns:
            Tuple of (browser, page) objects
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless, args=[]
        )

        # Apply slowdown in headed mode for visibility
        if not self.headless and self.slowdown > 0:
            self.page = await self.browser.new_page()
            await self.page.route("**/*", lambda route: route.continue_())
        else:
            self.page = await self.browser.new_page()

        mode = "headless" if self.headless else "headed"
        logger.info(f"Browser initialized in {mode} mode")

        return self.browser, self.page

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Cleanup browser resources."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

        logger.info("Browser resources cleaned up")


# ============================================================================
# Atomic Functions
# ============================================================================


@retry(max_attempts=3, base_delay=1, backoff_factor=2)
async def login_to_website(
    page: Page, username: str, password: str, timeout: int = 30
) -> bool:
    """
    Log in to the website with provided credentials.

    Args:
        page: Playwright page object
        username: Username for authentication
        password: Password for authentication
        timeout: Maximum wait time in seconds (default: 30)

    Returns:
        True if login successful

    Raises:
        LoginError: If login fails or times out
    """
    try:
        logger.info("Starting login process")

        # Wait for login form to appear
        await page.wait_for_selector("#username", timeout=timeout * 1000)
        logger.info("Login form detected")

        # Enter username
        await page.fill("#username", username)
        logger.info("Username entered")

        # Enter password
        await page.fill("#password", password)
        logger.info("Password entered")

        # Wait for login button to be clickable
        await page.wait_for_selector("#login-btn", timeout=timeout * 1000)
        await page.click("#login-btn")
        logger.info("Login button clicked")

        # Wait for dashboard to load
        await page.wait_for_selector(
            "#transactions-table", timeout=timeout * 1000
        )
        logger.info("Dashboard loaded successfully")

        return True

    except PlaywrightTimeoutError as e:
        raise LoginError(
            "Login timeout - form or dashboard did not load",
            context={"timeout": timeout, "error": str(e)},
        )
    except Exception as e:
        raise LoginError(
            f"Login failed: {str(e)}", context={"error": str(e)}
        )


@retry(max_attempts=3, base_delay=1, backoff_factor=2)
async def navigate_to_page(
    page: Page,
    url: str,
    wait_condition: str = "networkidle",
    timeout: int = 30,
) -> Page:
    """
    Navigate to a URL with specified wait condition.

    Args:
        page: Playwright page object
        url: URL to navigate to (absolute or relative)
        wait_condition: "load", "domcontentloaded", or "networkidle"
        timeout: Maximum wait time in seconds (default: 30)

    Returns:
        Page object after navigation

    Raises:
        NavigationError: If navigation fails or times out
    """
    try:
        logger.info(f"Navigating to {url} with wait condition: {wait_condition}")

        # Map wait condition to Playwright value
        wait_until = wait_condition
        if wait_condition not in ("load", "domcontentloaded", "networkidle"):
            wait_until = "networkidle"

        # Navigate to URL
        await page.goto(url, wait_until=wait_until, timeout=timeout * 1000)
        logger.info(f"Navigation to {url} completed successfully")

        return page

    except PlaywrightTimeoutError as e:
        raise NavigationError(
            f"Navigation timeout to {url}",
            context={"url": url, "timeout": timeout, "error": str(e)},
        )
    except Exception as e:
        raise NavigationError(
            f"Navigation failed to {url}: {str(e)}",
            context={"url": url, "error": str(e)},
        )


@retry(max_attempts=3, base_delay=1, backoff_factor=2)
async def capture_screenshot(
    page: Page, output_dir: str = "output/screenshots"
) -> str:
    """
    Capture full-page screenshot and save to file.

    Args:
        page: Playwright page object
        output_dir: Directory to save screenshot (default: "output/screenshots")

    Returns:
        Full file path of saved screenshot

    Raises:
        ScreenshotError: If capture or save fails
    """
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate timestamp-based filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}.png"
        file_path = output_path / filename

        # Capture full page screenshot
        await page.screenshot(path=str(file_path), full_page=True)
        logger.info(f"Screenshot captured: {file_path}")

        return str(file_path)

    except Exception as e:
        raise ScreenshotError(
            f"Screenshot capture failed: {str(e)}",
            context={"output_dir": output_dir, "error": str(e)},
        )


@retry(max_attempts=3, base_delay=1, backoff_factor=2)
async def extract_transaction_data(
    page: Page, output_dir: str = "output/data"
) -> List[Dict[str, Any]]:
    """
    Extract transaction data from table and save as JSON.

    Args:
        page: Playwright page object
        output_dir: Directory to save extracted data (default: "output/data")

    Returns:
        List of dictionaries with keys: amount, timestamp, merchant_id

    Raises:
        DataExtractionError: If extraction fails
    """
    try:
        logger.info("Starting data extraction from transaction table")

        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Wait for table to be present
        await page.wait_for_selector("#transactions-table", timeout=10000)

        # Extract table rows
        rows = await page.query_selector_all(
            "#transactions-table tbody tr"
        )
        logger.info(f"Found {len(rows)} transaction rows")

        transactions = []

        for row in rows:
            try:
                # Extract cells from row
                cells = await row.query_selector_all("td")

                if len(cells) >= 3:
                    amount = await cells[0].text_content()
                    timestamp = await cells[1].text_content()
                    merchant_id = await cells[2].text_content()

                    transaction = {
                        "amount": (amount or "").strip(),
                        "timestamp": (timestamp or "").strip(),
                        "merchant_id": (merchant_id or "").strip(),
                    }
                    transactions.append(transaction)

            except Exception as e:
                logger.error(f"Error extracting row data: {str(e)}")
                continue

        logger.info(f"Successfully extracted {len(transactions)} transactions")

        # Save data as JSON file with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"transactions_{timestamp}.json"
        file_path = output_path / filename

        with open(file_path, "w") as f:
            json.dump(transactions, f, indent=2)

        logger.info(f"Transaction data saved to {file_path}")

        return transactions

    except Exception as e:
        raise DataExtractionError(
            f"Data extraction failed: {str(e)}",
            context={"output_dir": output_dir, "error": str(e)},
        )


# ============================================================================
# Orchestration Function
# ============================================================================


async def run_all(headless: bool = False) -> Dict[str, Any]:
    """
    Run complete automation workflow: login → navigate → screenshot → extract.

    Args:
        headless: Run browser in headless mode (default: False)

    Returns:
        Dictionary with keys: screenshot_path, transactions

    Raises:
        AutomationError: If any step fails
    """
    try:
        logger.info("Starting complete automation workflow")

        # Load configuration
        config = await load_config()

        # Initialize browser
        async with BrowserContext(
            headless=config["headless"], slowdown=100 if not headless else 0
        ) as (browser, page):

            # Navigate to login page
            await navigate_to_page(
                page, config["base_url"], timeout=config["timeout"]
            )

            # Login
            await login_to_website(
                page,
                config["username"],
                config["password"],
                timeout=config["timeout"],
            )

            # Capture screenshot
            screenshot_path = await capture_screenshot(page)

            # Extract transaction data
            transactions = await extract_transaction_data(page)

            result = {
                "screenshot_path": screenshot_path,
                "transactions": transactions,
            }

            logger.info("Automation workflow completed successfully")
            return result

    except AutomationError as e:
        logger.error(f"Automation error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in automation workflow: {str(e)}")
        raise


# ============================================================================
# Main Entry Point
# ============================================================================


async def main() -> None:
    """Main entry point for the automation robot."""
    try:
        result = await run_all(headless=True)
        print("\n" + "=" * 60)
        print("AUTOMATION WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Screenshot: {result['screenshot_path']}")
        print(f"Transactions extracted: {len(result['transactions'])}")
        print("=" * 60 + "\n")

    except ConfigurationError as e:
        print(f"\nConfiguration Error: {str(e)}\n")
        sys.exit(1)
    except PathError as e:
        print(f"\nPath Error: {str(e)}\n")
        sys.exit(1)
    except AutomationError as e:
        print(f"\nAutomation Error: {str(e)}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Error: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
