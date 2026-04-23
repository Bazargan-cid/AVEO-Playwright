"""
AVEO-Playwright + Nova Act Integration Example

This script demonstrates how to integrate AVEO-Playwright with Amazon Nova Act
for intelligent web automation with AI vision capabilities.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# AVEO-Playwright imports
from vendor_automator.vendor_automator import (
    BrowserContext,
    navigate_to_page,
    capture_screenshot,
    login_to_website,
    extract_transaction_data,
    load_config,
    get_dummy_site_url,
)

# Nova Act imports (commented out for now since Nova Act might not be installed)
# from nova_act import NovaAct
# from nova_act.asyncio import NovaAct as AsyncNovaAct


class NovaActAVEOIntegration:
    """Integration class for Nova Act and AVEO-Playwright."""
    
    def __init__(self, nova_act_api_key: Optional[str] = None):
        """
        Initialize the integration.
        
        Args:
            nova_act_api_key: Nova Act API key (optional, can use env var)
        """
        self.nova_act_api_key = nova_act_api_key or os.getenv("NOVA_ACT_API_KEY")
        if not self.nova_act_api_key:
            print("⚠️  Nova Act API key not found. Some features will be disabled.")
    
    async def pattern_1_nova_guided_automation(self) -> Dict[str, Any]:
        """
        Pattern 1: Nova Act as Decision Maker
        
        Nova Act analyzes screenshots and decides which AVEO-Playwright 
        functions to call based on visual understanding.
        """
        print("\n" + "="*60)
        print("PATTERN 1: Nova Act Guided Automation")
        print("="*60)
        
        # Load AVEO-Playwright configuration
        config = await load_config()
        
        # Initialize browser with AVEO-Playwright
        async with BrowserContext(headless=False) as (browser, page):
            
            # Step 1: Navigate to target website
            print("📍 Navigating to target website...")
            await navigate_to_page(page, config["base_url"])
            
            # Step 2: Capture screenshot for Nova Act analysis
            print("📸 Capturing screenshot for Nova Act analysis...")
            screenshot_path = await capture_screenshot(page)
            
            # Step 3: Simulate Nova Act analysis (since Nova Act might not be installed)
            print("🤖 Analyzing page with Nova Act (simulated)...")
            
            # This would be the actual Nova Act integration:
            """
            with NovaAct(starting_page=f"file://{screenshot_path}") as nova:
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
            """
            
            # Simulated Nova Act decision
            simulated_decision = {
                "page_type": "login",
                "next_action": "perform_login",
                "confidence": 0.95
            }
            
            print(f"🎯 Nova Act Decision: {json.dumps(simulated_decision, indent=2)}")
            
            # Step 4: Execute AVEO-Playwright functions based on decision
            if simulated_decision["page_type"] == "login":
                print("🔐 Executing login based on Nova Act decision...")
                await login_to_website(
                    page, 
                    config["username"], 
                    config["password"]
                )
                
                # Capture post-login screenshot
                post_login_screenshot = await capture_screenshot(page)
                print(f"📸 Post-login screenshot: {post_login_screenshot}")
                
                # Extract transaction data
                print("📊 Extracting transaction data...")
                transactions = await extract_transaction_data(page)
                
                return {
                    "pattern": "nova_guided",
                    "decision": simulated_decision,
                    "screenshots": [screenshot_path, post_login_screenshot],
                    "transactions": transactions,
                    "status": "success"
                }
            
            return {
                "pattern": "nova_guided",
                "decision": simulated_decision,
                "status": "no_action_taken"
            }
    
    async def pattern_2_aveo_as_tool(self, task_description: str) -> Dict[str, Any]:
        """
        Pattern 2: AVEO-Playwright as Nova Act Tool
        
        AVEO-Playwright functions are exposed as tools that Nova Act can call
        to perform specific automation tasks.
        """
        print("\n" + "="*60)
        print("PATTERN 2: AVEO-Playwright as Nova Act Tool")
        print("="*60)
        
        print(f"📝 Task Description: {task_description}")
        
        # Analyze task description and map to AVEO-Playwright functions
        task_lower = task_description.lower()
        
        if "login" in task_lower and "extract" in task_lower:
            print("🔧 Mapping task to: login_and_extract workflow")
            
            # Execute AVEO-Playwright automation
            from vendor_automator.vendor_automator import run_all
            result = await run_all(headless=True)
            
            # This would be returned to Nova Act for further analysis:
            """
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
            """
            
            # Simulated Nova Act analysis
            simulated_analysis = {
                "insights": [
                    f"Extracted {len(result['transactions'])} transactions",
                    "All transactions have valid timestamps",
                    "Transaction amounts range from $50 to $2,500"
                ],
                "recommendations": [
                    "Monitor transactions above $2,000 for anomalies",
                    "Set up automated alerts for failed transactions"
                ],
                "data_quality": "high"
            }
            
            return {
                "pattern": "aveo_as_tool",
                "task": task_description,
                "execution_result": result,
                "nova_analysis": simulated_analysis,
                "status": "success"
            }
        
        return {
            "pattern": "aveo_as_tool",
            "task": task_description,
            "status": "task_not_recognized"
        }
    
    async def pattern_3_hybrid_verification(self) -> Dict[str, Any]:
        """
        Pattern 3: Hybrid Approach with Visual Verification
        
        AVEO-Playwright executes automation tasks, Nova Act provides
        visual verification and analysis of the results.
        """
        print("\n" + "="*60)
        print("PATTERN 3: Hybrid Automation with Visual Verification")
        print("="*60)
        
        config = await load_config()
        
        async with BrowserContext(headless=False) as (browser, page):
            
            # Step 1: AVEO-Playwright executes login
            print("🔐 AVEO-Playwright executing login...")
            await navigate_to_page(page, config["base_url"])
            await login_to_website(
                page, 
                config["username"], 
                config["password"]
            )
            
            # Step 2: Capture screenshot for Nova Act verification
            print("📸 Capturing screenshot for Nova Act verification...")
            verification_screenshot = await capture_screenshot(page)
            
            # Step 3: Simulate Nova Act verification
            print("👁️  Nova Act verifying login success (simulated)...")
            
            # This would be actual Nova Act verification:
            """
            with NovaAct(starting_page=f"file://{verification_screenshot}") as nova:
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
            """
            
            # Simulated verification result
            simulated_verification = {
                "login_successful": True,
                "current_page": "dashboard",
                "error_messages": []
            }
            
            print(f"✅ Verification Result: {json.dumps(simulated_verification, indent=2)}")
            
            if simulated_verification["login_successful"]:
                # Continue with data extraction
                print("📊 Login verified! Proceeding with data extraction...")
                transactions = await extract_transaction_data(page)
                
                # Simulate Nova Act data analysis
                print("🔍 Nova Act analyzing extracted data (simulated)...")
                
                simulated_data_analysis = {
                    "total_transactions": len(transactions),
                    "anomalies": [
                        "Transaction TXN-005 has unusually high amount"
                    ],
                    "patterns": [
                        "Most transactions occur during business hours",
                        "Average transaction amount is $1,250"
                    ]
                }
                
                return {
                    "pattern": "hybrid_verification",
                    "verification": simulated_verification,
                    "transactions": transactions,
                    "analysis": simulated_data_analysis,
                    "screenshot": verification_screenshot,
                    "status": "success"
                }
            else:
                return {
                    "pattern": "hybrid_verification",
                    "verification": simulated_verification,
                    "status": "login_failed"
                }


async def demonstrate_integration_patterns():
    """Demonstrate all three integration patterns."""
    
    print("🚀 AVEO-Playwright + Nova Act Integration Demo")
    print("=" * 60)
    
    # Initialize integration
    integration = NovaActAVEOIntegration()
    
    try:
        # Pattern 1: Nova Act Guided Automation
        result1 = await integration.pattern_1_nova_guided_automation()
        print(f"\n✅ Pattern 1 Result: {result1['status']}")
        
        # Pattern 2: AVEO-Playwright as Tool
        result2 = await integration.pattern_2_aveo_as_tool(
            "Login to the legacy vendor website and extract transaction data"
        )
        print(f"\n✅ Pattern 2 Result: {result2['status']}")
        
        # Pattern 3: Hybrid Verification
        result3 = await integration.pattern_3_hybrid_verification()
        print(f"\n✅ Pattern 3 Result: {result3['status']}")
        
        # Summary
        print("\n" + "="*60)
        print("INTEGRATION DEMO SUMMARY")
        print("="*60)
        print("✅ Pattern 1 (Nova Guided): Nova Act analyzes screenshots and guides AVEO-Playwright")
        print("✅ Pattern 2 (AVEO as Tool): AVEO-Playwright functions exposed as Nova Act tools")
        print("✅ Pattern 3 (Hybrid): AVEO-Playwright executes, Nova Act verifies visually")
        print("\n🎯 All integration patterns demonstrated successfully!")
        
        return {
            "pattern_1": result1,
            "pattern_2": result2,
            "pattern_3": result3
        }
        
    except Exception as e:
        print(f"\n❌ Integration demo failed: {str(e)}")
        return {"error": str(e)}


async def setup_integration_environment():
    """Setup and verify integration environment."""
    
    print("🔧 Setting up AVEO-Playwright + Nova Act integration environment...")
    
    # Check AVEO-Playwright setup
    try:
        config = await load_config()
        print("✅ AVEO-Playwright configuration loaded")
    except Exception as e:
        print(f"❌ AVEO-Playwright configuration error: {e}")
        return False
    
    # Check Nova Act API key
    nova_act_key = os.getenv("NOVA_ACT_API_KEY")
    if nova_act_key:
        print("✅ Nova Act API key found")
    else:
        print("⚠️  Nova Act API key not found (demo will use simulated responses)")
    
    # Check dummy site
    try:
        dummy_url = get_dummy_site_url()
        print(f"✅ Dummy site available: {dummy_url}")
    except Exception as e:
        print(f"❌ Dummy site error: {e}")
        return False
    
    # Create output directories
    Path("output/screenshots").mkdir(parents=True, exist_ok=True)
    Path("output/data").mkdir(parents=True, exist_ok=True)
    print("✅ Output directories created")
    
    print("🎯 Integration environment setup complete!")
    return True


async def main():
    """Main integration demo function."""
    
    # Setup environment
    if not await setup_integration_environment():
        print("❌ Environment setup failed. Exiting.")
        return
    
    # Run integration demo
    results = await demonstrate_integration_patterns()
    
    # Save results
    results_file = Path("output/data/integration_demo_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Demo results saved to: {results_file}")


if __name__ == "__main__":
    asyncio.run(main())