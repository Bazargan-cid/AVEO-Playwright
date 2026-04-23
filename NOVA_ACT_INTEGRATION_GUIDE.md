# AVEO-Playwright + Nova Act Integration Guide

## Overview

This guide demonstrates how to integrate AVEO-Playwright (our AI-powered robot for legacy website automation) with Amazon Nova Act (AI vision and web automation service).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Integration Architecture                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Nova Act (AI Vision)                 │   │
│  │  - Visual understanding of web pages                 │   │
│  │  - Decision making based on visual context           │   │
│  │  - Natural language task interpretation              │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            AVEO-Playwright (Execution)               │   │
│  │  - Atomic functions for browser automation           │   │
│  │  - Robust error handling and retry logic             │   │
│  │  - Screenshot capture and data extraction            │   │
│  │  - Legacy website compatibility                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Legacy Website Target                   │   │
│  │  - Login forms and authentication                    │   │
│  │  - Transaction tables and data                       │   │
│  │  - Complex navigation structures                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Integration Patterns

### Pattern 1: Nova Act as Decision Maker

Nova Act analyzes screenshots and decides which AVEO-Playwright functions to call:

```python
import asyncio
from nova_act import NovaAct
from vendor_automator.vendor_automator import (
    BrowserContext,
    navigate_to_page,
    capture_screenshot,
    login_to_website,
    extract_transaction_data
)

async def nova_act_guided_automation():
    """Nova Act guides AVEO-Playwright execution based on visual analysis."""
    
    # Initialize AVEO-Playwright browser
    async with BrowserContext(headless=False) as (browser, page):
        
        # Navigate to target website
        await navigate_to_page(page, "https://legacy-vendor-site.com")
        
        # Capture initial screenshot for Nova Act analysis
        screenshot_path = await capture_screenshot(page)
        
        # Initialize Nova Act with the screenshot
        with NovaAct(starting_page=f"file://{screenshot_path}") as nova:
            
            # Nova Act analyzes the page and decides next action
            decision = nova.act_get(
                "Analyze this webpage screenshot. What type of page is this? "
                "Is it a login page, dashboard, or something else? "
                "What should be the next action?",
                schema={
                    "type": "object",
                    "properties": {
                        "page_type": {"type": "string"},
                        "next_action": {"type": "string"},
                        "confidence": {"type": "number"}
                    }
                }
            )
            
            # Execute AVEO-Playwright functions based on Nova Act decision
            if decision.parsed_response["page_type"] == "login":
                await login_to_website(page, "username", "password")
                
            elif decision.parsed_response["page_type"] == "dashboard":
                transactions = await extract_transaction_data(page)
                return transactions
                
            # Continue with more Nova Act guided decisions...
```

### Pattern 2: AVEO-Playwright as Nova Act Tool

AVEO-Playwright functions exposed as tools for Nova Act:

```python
from nova_act import NovaAct
from vendor_automator.vendor_automator import run_all
import json

class AVEOPlaywrightTool:
    """AVEO-Playwright tool for Nova Act integration."""
    
    @staticmethod
    async def execute_automation(task_description: str, target_url: str) -> dict:
        """
        Execute AVEO-Playwright automation based on task description.
        
        Args:
            task_description: Natural language description of the task
            target_url: Target website URL
            
        Returns:
            Dictionary with results (screenshot_path, transactions, etc.)
        """
        # Map task description to AVEO-Playwright workflow
        if "login" in task_description.lower():
            # Execute login workflow
            result = await run_all(headless=True)
            return {
                "status": "success",
                "action": "login_and_extract",
                "screenshot": result["screenshot_path"],
                "data": result["transactions"]
            }
        
        # Add more task mappings as needed
        return {"status": "error", "message": "Task not recognized"}

async def nova_act_with_aveo_tool():
    """Nova Act using AVEO-Playwright as a tool."""
    
    with NovaAct(starting_page="https://nova.amazon.com/act") as nova:
        
        # Nova Act can call AVEO-Playwright functions
        task = "Login to the legacy vendor website and extract transaction data"
        
        # This would be implemented as a proper Nova Act tool
        result = await AVEOPlaywrightTool.execute_automation(
            task_description=task,
            target_url="https://legacy-vendor-site.com"
        )
        
        # Nova Act can then analyze the results
        analysis = nova.act_get(
            f"Analyze this automation result: {json.dumps(result)}. "
            "What insights can you provide about the extracted data?",
            schema={
                "type": "object",
                "properties": {
                    "insights": {"type": "array", "items": {"type": "string"}},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                    "data_quality": {"type": "string"}
                }
            }
        )
        
        return analysis.parsed_response
```

### Pattern 3: Hybrid Approach - Visual Verification

AVEO-Playwright executes, Nova Act verifies visually:

```python
async def hybrid_automation_with_verification():
    """Hybrid approach: AVEO-Playwright executes, Nova Act verifies."""
    
    async with BrowserContext(headless=False) as (browser, page):
        
        # Step 1: AVEO-Playwright executes login
        await navigate_to_page(page, "https://legacy-vendor-site.com/login")
        await login_to_website(page, "testuser", "testpass")
        
        # Step 2: Capture screenshot for Nova Act verification
        screenshot_path = await capture_screenshot(page)
        
        # Step 3: Nova Act verifies login success
        with NovaAct(starting_page=f"file://{screenshot_path}") as nova:
            verification = nova.act_get(
                "Look at this screenshot. Did the login succeed? "
                "Are we now on a dashboard or still on login page?",
                schema={
                    "type": "object",
                    "properties": {
                        "login_successful": {"type": "boolean"},
                        "current_page": {"type": "string"},
                        "error_messages": {"type": "array", "items": {"type": "string"}}
                    }
                }
            )
            
            if verification.parsed_response["login_successful"]:
                # Continue with data extraction
                transactions = await extract_transaction_data(page)
                
                # Nova Act can analyze the extracted data
                data_analysis = nova.act_get(
                    f"Analyze this transaction data: {json.dumps(transactions)}. "
                    "Are there any anomalies or patterns?",
                    schema={
                        "type": "object",
                        "properties": {
                            "total_transactions": {"type": "number"},
                            "anomalies": {"type": "array", "items": {"type": "string"}},
                            "patterns": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                )
                
                return {
                    "transactions": transactions,
                    "analysis": data_analysis.parsed_response
                }
            else:
                # Handle login failure
                return {
                    "error": "Login failed",
                    "details": verification.parsed_response
                }
```

## MCP (Model Context Protocol) Integration

For standardized integration with Claude Desktop and other AI tools:

```python
# nova_act_aveo_mcp_server.py
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
from vendor_automator.vendor_automator import run_all, BrowserContext
import json

app = Server("aveo-playwright-mcp")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available AVEO-Playwright tools."""
    return [
        Tool(
            name="aveo_login_and_extract",
            description="Login to legacy website and extract transaction data",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                    "website_url": {"type": "string"}
                },
                "required": ["username", "password", "website_url"]
            }
        ),
        Tool(
            name="aveo_capture_screenshot",
            description="Capture screenshot of current page state",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute AVEO-Playwright tools."""
    
    if name == "aveo_login_and_extract":
        # Execute AVEO-Playwright automation
        result = await run_all(headless=True)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "screenshot_path": result["screenshot_path"],
                "transactions_count": len(result["transactions"]),
                "transactions": result["transactions"]
            }, indent=2)
        )]
    
    elif name == "aveo_capture_screenshot":
        async with BrowserContext(headless=True) as (browser, page):
            await page.goto(arguments["url"])
            screenshot_path = await page.screenshot(path="screenshot.png")
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "screenshot_path": str(screenshot_path)
                }, indent=2)
            )]
    
    return [TextContent(type="text", text="Tool not found")]

if __name__ == "__main__":
    import mcp
    mcp.run_server(app)
```

## Configuration

### Environment Variables

Create a `.env` file with both AVEO-Playwright and Nova Act configuration:

```bash
# AVEO-Playwright Configuration
USERNAME=testuser
PASSWORD=testpass
BASE_URL=file:///path/to/dummy_site/login.html
HEADLESS=true
TIMEOUT=30

# Nova Act Configuration
NOVA_ACT_API_KEY=your_nova_act_api_key

# AWS Configuration (for Nova Act workflows)
AWS_REGION=us-east-1
AWS_PROFILE=default
```

### Dependencies

Add Nova Act to your requirements.txt:

```txt
# Existing AVEO-Playwright dependencies
playwright>=1.40.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
hypothesis>=6.88.0

# Nova Act integration
nova-act>=3.0.0
boto3>=1.26.0
pydantic>=2.0.0
```

## Usage Examples

### Example 1: Simple Integration

```python
import asyncio
from integration_examples import nova_act_guided_automation

async def main():
    result = await nova_act_guided_automation()
    print(f"Automation completed: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Claude Desktop Integration

1. Install the MCP server:
```bash
pip install -r requirements.txt
```

2. Configure Claude Desktop to use the AVEO-Playwright MCP server:
```json
{
  "mcpServers": {
    "aveo-playwright": {
      "command": "python",
      "args": ["nova_act_aveo_mcp_server.py"],
      "env": {
        "NOVA_ACT_API_KEY": "your_api_key"
      }
    }
  }
}
```

3. Use in Claude Desktop:
```
Can you help me login to the legacy vendor website and extract transaction data using AVEO-Playwright?
```

## Best Practices

### 1. Error Handling
- Always wrap Nova Act calls in try-catch blocks
- Use AVEO-Playwright's built-in retry logic for transient failures
- Implement fallback strategies when Nova Act analysis fails

### 2. Performance Optimization
- Use headless mode for production workflows
- Cache screenshots when possible
- Implement parallel execution for multiple tasks

### 3. Security
- Never log credentials in Nova Act prompts
- Use environment variables for sensitive configuration
- Implement proper session management

### 4. Monitoring
- Log all Nova Act decisions and AVEO-Playwright actions
- Capture screenshots at key decision points
- Monitor success rates and failure patterns

## Troubleshooting

### Common Issues

1. **Nova Act API Key Issues**
   - Verify API key is set correctly
   - Check API key permissions and quotas

2. **Screenshot Analysis Failures**
   - Ensure screenshots are high quality
   - Provide clear context in prompts
   - Use structured schemas for responses

3. **Integration Timing Issues**
   - Add appropriate delays between operations
   - Use AVEO-Playwright's wait conditions
   - Implement proper async/await patterns

### Debug Mode

Enable debug logging for both systems:

```python
import logging

# Enable AVEO-Playwright debug logging
logging.getLogger("vendor_automator").setLevel(logging.DEBUG)

# Enable Nova Act debug logging
logging.getLogger("nova_act").setLevel(logging.DEBUG)
```

## Next Steps

1. **Implement Custom Tools**: Create specific Nova Act tools for your use cases
2. **Add More Integration Patterns**: Explore other ways to combine visual AI with automation
3. **Scale to Production**: Deploy using AWS services and proper monitoring
4. **Extend MCP Server**: Add more AVEO-Playwright functions as MCP tools

## Resources

- [Nova Act Documentation](https://nova.amazon.com/act)
- [AVEO-Playwright Repository](https://github.com/Bazargan-cid/AVEO-Playwright)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

## Support

For issues related to:
- **AVEO-Playwright**: Check the [GitHub repository](https://github.com/Bazargan-cid/AVEO-Playwright/issues)
- **Nova Act**: Refer to the [official documentation](https://nova.amazon.com/act)
- **Integration**: Create an issue in the AVEO-Playwright repository with the "integration" label