# AVEO-Playwright

AI-powered robot for automating legacy website interactions using Playwright. Serves as the "body" component for integration with Nova Act (AI vision) and AWS Bedrock.

## Features

- **Async-First Architecture**: Built on Python's asyncio and Playwright's async API
- **Atomic Functions**: Single-responsibility functions for login, navigation, screenshot, and data extraction
- **Robust Error Handling**: Exponential backoff retry logic (1s, 2s, 4s) for transient failures
- **Comprehensive Logging**: Structured logging with sensitive data masking
- **Production-Grade Code**: Full type hints, docstrings, and PEP 8 compliance
- **Local Testing**: Dummy website with login and dashboard for development
- **Integration Ready**: JSON-serializable outputs for Nova Act and AWS Bedrock
- **S3 Storage**: Automatic upload of screenshots and data to S3 bucket
- **CloudWatch Monitoring**: Comprehensive metrics and logging

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or download the project**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   playwright install
   ```

4. **Create .env file**
   ```bash
   cp .env.example .env
   ```

5. **Configure credentials in .env**
   ```
   USERNAME=testuser
   PASSWORD=testpass
   BASE_URL=file:///path/to/dummy_site/login.html
   HEADLESS=true
   TIMEOUT=30
   S3_BUCKET_NAME=aveo-playwright-output
   S3_UPLOAD_ENABLED=true
   ```

## Quick Start

```python
from vendor_automator.vendor_automator import run_all

# Run complete automation workflow with S3 upload
result = await run_all(headless=True, upload_to_s3=True)

print(f"Screenshot: {result['screenshot_path']}")
print(f"Transactions: {len(result['transactions'])}")

# Check S3 upload status
if 's3_summary' in result:
    s3_summary = result['s3_summary']
    print(f"S3 uploads: {s3_summary['successful_uploads']}/{s3_summary['total_uploads']}")
```

## Usage

### Running the Robot

```bash
python vendor_automator.py
```

### Using as a Module

```python
import asyncio
from vendor_automator import (
    load_config,
    login_to_website,
    navigate_to_page,
    capture_screenshot,
    extract_transaction_data,
    run_all,
    BrowserContext
)

# Run complete workflow
result = asyncio.run(run_all(headless=True))
print(f"Screenshot: {result['screenshot_path']}")
print(f"Transactions: {result['transactions']}")
```

### Individual Function Usage

```python
import asyncio
from playwright.async_api import async_playwright
from vendor_automator import login_to_website, navigate_to_page

async def example():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to login page
        await navigate_to_page(page, "http://example.com/login")
        
        # Login
        await login_to_website(page, "username", "password")
        
        # Continue with other operations...
        
        await browser.close()

asyncio.run(example())
```

## Project Structure

```
vendor_automator/
├── __init__.py                  # Module initialization
├── vendor_automator.py          # Main module with atomic functions
├── dummy_site/
│   ├── login.html               # Legacy login form
│   └── dashboard.html           # Transaction dashboard
├── output/
│   ├── screenshots/             # PNG screenshots (auto-created)
│   └── data/                    # JSON data files (auto-created)
├── tests/
│   ├── test_config.py           # Configuration tests
│   ├── test_path_detection.py   # Path auto-detection tests
│   ├── test_retry_logic.py      # Retry logic tests
│   ├── test_login.py            # Login flow tests
│   ├── test_navigation.py       # Navigation tests
│   ├── test_screenshot.py       # Screenshot capture tests
│   ├── test_extraction.py       # Data extraction tests
│   ├── test_logging.py          # Logging tests
│   ├── test_error_handling.py   # Error handling tests
│   ├── test_integration.py      # End-to-end tests
│   └── test_properties.py       # Property-based tests
├── .env.example                 # Configuration template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| USERNAME | Yes | - | Username for login |
| PASSWORD | Yes | - | Password for login |
| BASE_URL | Yes | - | Base URL of target website |
| HEADLESS | No | true | Browser mode (true/false) |
| TIMEOUT | No | 30 | Operation timeout in seconds |

### .env File

Create a `.env` file in the project root with your configuration:

```
USERNAME=testuser
PASSWORD=testpass
BASE_URL=file:///path/to/dummy_site/login.html
HEADLESS=true
TIMEOUT=30
```

**Important**: Never commit `.env` to version control. Use `.env.example` as a template.

## Atomic Functions

### login_to_website(page, username, password, timeout=30)

Authenticate to the website with provided credentials.

**Parameters:**
- `page`: Playwright page object
- `username`: Username for authentication
- `password`: Password for authentication
- `timeout`: Maximum wait time in seconds (default: 30)

**Returns:** `True` if login successful

**Raises:** `LoginError` if login fails or times out

### navigate_to_page(page, url, wait_condition="networkidle", timeout=30)

Navigate to a specific URL with wait conditions.

**Parameters:**
- `page`: Playwright page object
- `url`: URL to navigate to (absolute or relative)
- `wait_condition`: "load", "domcontentloaded", or "networkidle" (default: "networkidle")
- `timeout`: Maximum wait time in seconds (default: 30)

**Returns:** Page object after navigation

**Raises:** `NavigationError` if navigation fails or times out

### capture_screenshot(page, output_dir="output/screenshots")

Capture full-page screenshot and save to file.

**Parameters:**
- `page`: Playwright page object
- `output_dir`: Directory to save screenshot (default: "output/screenshots")

**Returns:** Full file path of saved screenshot

**Raises:** `ScreenshotError` if capture or save fails

### extract_transaction_data(page, output_dir="output/data")

Extract transaction data from table and save as JSON.

**Parameters:**
- `page`: Playwright page object
- `output_dir`: Directory to save extracted data (default: "output/data")

**Returns:** List of dictionaries with keys: amount, timestamp, merchant_id

**Raises:** `DataExtractionError` if extraction fails

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Suite

```bash
pytest tests/test_login.py -v
pytest tests/test_properties.py -v
```

### Run with Coverage

```bash
pytest --cov=vendor_automator tests/
```

## Troubleshooting

### Playwright Browsers Not Found

```bash
playwright install
```

### .env File Not Found

Ensure `.env` file exists in the project root:

```bash
cp .env.example .env
```

### Configuration Error

Check that all required variables are set in `.env`:
- USERNAME
- PASSWORD
- BASE_URL

### Timeout Errors

Increase the TIMEOUT value in `.env` if the website is slow:

```
TIMEOUT=60
```

### Browser Process Not Closing

The system uses async context managers to ensure proper cleanup. If processes remain:

```bash
# Kill any remaining browser processes
pkill -f chromium
```

## Integration with Nova Act and AWS Bedrock

AVEO-Playwright is designed to integrate seamlessly with Amazon Nova Act (AI vision) and AWS Bedrock for intelligent web automation workflows.

### Nova Act Integration

Nova Act provides AI vision capabilities that can analyze screenshots and make intelligent decisions about web automation tasks. AVEO-Playwright serves as the execution engine.

**Pattern 1: Nova Act as Decision Maker**
```python
from nova_act import NovaAct
from vendor_automator.vendor_automator import BrowserContext, capture_screenshot

async with BrowserContext(headless=False) as (browser, page):
    # Capture screenshot for Nova Act analysis
    screenshot_path = await capture_screenshot(page)
    
    # Nova Act analyzes and decides next action
    with NovaAct(starting_page=f"file://{screenshot_path}") as nova:
        decision = nova.act_get(
            "What type of page is this? What should be the next action?",
            schema={"type": "object", "properties": {"page_type": {"type": "string"}}}
        )
        
        # Execute AVEO-Playwright functions based on Nova Act decision
        if decision.parsed_response["page_type"] == "login":
            await login_to_website(page, username, password)
```

**Pattern 2: AVEO-Playwright as Nova Act Tool**
```python
# AVEO-Playwright functions exposed as tools for Nova Act
class AVEOPlaywrightTool:
    @staticmethod
    async def execute_automation(task_description: str) -> dict:
        result = await run_all(headless=True)
        return {
            "screenshot": result["screenshot_path"],
            "transactions": result["transactions"]
        }
```

**Pattern 3: Hybrid Verification**
```python
# AVEO-Playwright executes, Nova Act verifies
await login_to_website(page, username, password)
screenshot = await capture_screenshot(page)

with NovaAct(starting_page=f"file://{screenshot}") as nova:
    verification = nova.act_get("Did the login succeed?")
    if verification.parsed_response:
        transactions = await extract_transaction_data(page)
```

### AWS Bedrock Integration

```python
import json

result = await run_all(headless=True)
bedrock_input = json.dumps({
    "screenshot": result['screenshot_path'],
    "transactions": result['transactions']
})
# Send to Bedrock API for further AI processing
```

### Quick Start with Integration

```bash
# Install Nova Act
pip install nova-act

# Set Nova Act API key
export NOVA_ACT_API_KEY="your_api_key"

# Run integration example
python nova_act_integration_example.py
```

For detailed integration patterns and examples, see:
- `NOVA_ACT_INTEGRATION_GUIDE.md` - Comprehensive integration guide
- `nova_act_integration_example.py` - Working integration examples

## Development

### Code Quality

The project follows PEP 8 guidelines and includes:
- Full type hints for all functions
- Comprehensive docstrings
- Structured logging with timestamps
- Sensitive data masking
- Proper error handling with context information

### Adding New Features

1. Add new atomic function to `vendor_automator.py`
2. Add type hints and docstring
3. Add unit tests in `tests/`
4. Add property-based tests if applicable
5. Update this README with usage examples

## License

[Add your license here]

## Support

For issues or questions, please refer to the troubleshooting section or contact the development team.
