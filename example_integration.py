"""
Example integration script showing how to use AVEO-Playwright atomic functions.

This script demonstrates:
1. Importing atomic functions from the vendor_automator module
2. Using individual functions for custom workflows
3. Integration with Nova Act and AWS Bedrock
"""

import asyncio
import json
from vendor_automator.vendor_automator import (
    load_config,
    get_dummy_site_url,
    navigate_to_page,
    login_to_website,
    capture_screenshot,
    extract_transaction_data,
    run_all,
    BrowserContext,
)


async def example_individual_functions():
    """Example: Using individual atomic functions."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Using Individual Atomic Functions")
    print("=" * 60)

    # Load configuration
    config = await load_config()
    print(f"Configuration loaded: {config['base_url']}")

    # Initialize browser
    async with BrowserContext(headless=True) as (browser, page):
        # Navigate to login page
        await navigate_to_page(page, config["base_url"])
        print("Navigated to login page")

        # Login
        await login_to_website(
            page, config["username"], config["password"]
        )
        print("Login successful")

        # Capture screenshot
        screenshot_path = await capture_screenshot(page)
        print(f"Screenshot saved: {screenshot_path}")

        # Extract data
        transactions = await extract_transaction_data(page)
        print(f"Extracted {len(transactions)} transactions")

        # Print first transaction
        if transactions:
            print(f"First transaction: {transactions[0]}")


async def example_complete_workflow():
    """Example: Using the complete workflow function."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Using Complete Workflow Function")
    print("=" * 60)

    result = await run_all(headless=True)

    print(f"Screenshot: {result['screenshot_path']}")
    print(f"Transactions: {len(result['transactions'])}")

    # Print all transactions
    for i, transaction in enumerate(result["transactions"], 1):
        print(f"  {i}. {transaction}")


async def example_nova_act_integration():
    """Example: Integration with Nova Act (AI vision)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Nova Act Integration")
    print("=" * 60)

    config = await load_config()

    async with BrowserContext(headless=True) as (browser, page):
        # Navigate to page
        await navigate_to_page(page, config["base_url"])

        # Login
        await login_to_website(
            page, config["username"], config["password"]
        )

        # Capture screenshot for Nova Act to analyze
        screenshot_path = await capture_screenshot(page)
        print(f"Screenshot for Nova Act: {screenshot_path}")

        # Nova Act would analyze the screenshot and determine next actions
        # For example: "Click on the transaction with amount $1,250.00"

        # Extract data for Nova Act to process
        transactions = await extract_transaction_data(page)
        print(f"Transactions for Nova Act: {json.dumps(transactions, indent=2)}")


async def example_bedrock_integration():
    """Example: Integration with AWS Bedrock."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: AWS Bedrock Integration")
    print("=" * 60)

    result = await run_all(headless=True)

    # Prepare data for Bedrock
    bedrock_input = {
        "screenshot": result["screenshot_path"],
        "transactions": result["transactions"],
        "task": "Analyze the transactions and identify any anomalies",
    }

    # Convert to JSON for Bedrock API
    bedrock_json = json.dumps(bedrock_input, indent=2)
    print("Data prepared for Bedrock:")
    print(bedrock_json)

    # In a real scenario, you would call:
    # bedrock_response = await bedrock_client.invoke(bedrock_json)


async def example_custom_workflow():
    """Example: Custom workflow combining multiple operations."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Custom Workflow")
    print("=" * 60)

    config = await load_config()

    async with BrowserContext(headless=True) as (browser, page):
        # Step 1: Navigate and login
        await navigate_to_page(page, config["base_url"])
        await login_to_website(
            page, config["username"], config["password"]
        )
        print("Step 1: Login completed")

        # Step 2: Capture initial state
        screenshot1 = await capture_screenshot(page)
        print(f"Step 2: Initial screenshot: {screenshot1}")

        # Step 3: Extract data
        transactions = await extract_transaction_data(page)
        print(f"Step 3: Extracted {len(transactions)} transactions")

        # Step 4: Process transactions
        total_amount = 0
        for transaction in transactions:
            # Parse amount (remove $ and commas)
            amount_str = (
                transaction["amount"]
                .replace("$", "")
                .replace(",", "")
            )
            try:
                amount = float(amount_str)
                total_amount += amount
            except ValueError:
                pass

        print(f"Step 4: Total transaction amount: ${total_amount:,.2f}")

        # Step 5: Capture final state
        screenshot2 = await capture_screenshot(page)
        print(f"Step 5: Final screenshot: {screenshot2}")


async def main():
    """Run all examples."""
    try:
        # Example 1: Individual functions
        await example_individual_functions()

        # Example 2: Complete workflow
        await example_complete_workflow()

        # Example 3: Nova Act integration
        await example_nova_act_integration()

        # Example 4: Bedrock integration
        await example_bedrock_integration()

        # Example 5: Custom workflow
        await example_custom_workflow()

        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    asyncio.run(main())
