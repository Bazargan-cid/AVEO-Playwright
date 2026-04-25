"""
AWS Bedrock Integration for AVEO-Playwright

This module provides active integration with AWS Bedrock for AI-powered analysis
of web automation results.
"""

import asyncio
import json
import boto3
import base64
from typing import Dict, Any, List
from pathlib import Path
from botocore.exceptions import ClientError

# AVEO-Playwright imports
from vendor_automator.vendor_automator import run_all


class BedrockIntegrator:
    """AWS Bedrock integration for AVEO-Playwright results analysis."""
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize Bedrock integrator.
        
        Args:
            region_name: AWS region for Bedrock
        """
        self.region_name = region_name
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=region_name)
        
        # Bedrock model configurations
        self.models = {
            'claude': 'anthropic.claude-3-sonnet-20240229-v1:0',
            'titan': 'amazon.titan-text-express-v1',
            'nova': 'amazon.nova-micro-v1:0'  # Nova Act model
        }
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image file to base64 for Bedrock."""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to encode image: {e}")
    
    async def analyze_with_claude(self, screenshot_path: str, transactions: List[Dict], 
                                 custom_prompt: str = None) -> Dict[str, Any]:
        """
        Analyze automation results using Claude via Bedrock.
        
        Args:
            screenshot_path: Path to screenshot file
            transactions: List of transaction data
            custom_prompt: Optional custom analysis prompt
            
        Returns:
            Analysis results from Claude
        """
        try:
            # Encode screenshot
            image_base64 = self.encode_image_to_base64(screenshot_path)
            
            # Default analysis prompt
            if not custom_prompt:
                custom_prompt = """
                Analyze this web automation result:
                1. Review the screenshot for any UI issues or anomalies
                2. Analyze the transaction data for patterns or anomalies
                3. Provide insights on data quality and completeness
                4. Suggest any improvements for the automation process
                """
            
            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{custom_prompt}\n\nTransaction Data:\n{json.dumps(transactions, indent=2)}"
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ]
            }
            
            # Call Bedrock
            response = self.bedrock_runtime.invoke_model(
                modelId=self.models['claude'],
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            return {
                'status': 'success',
                'model': 'claude-3-sonnet',
                'analysis': response_body['content'][0]['text'],
                'usage': response_body.get('usage', {}),
                'timestamp': asyncio.get_event_loop().time()
            }
            
        except ClientError as e:
            return {
                'status': 'error',
                'error': f"Bedrock API error: {e}",
                'error_code': e.response['Error']['Code']
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': f"Analysis failed: {e}"
            }
    
    async def analyze_with_nova(self, screenshot_path: str, transactions: List[Dict]) -> Dict[str, Any]:
        """
        Analyze automation results using Amazon Nova via Bedrock.
        
        Args:
            screenshot_path: Path to screenshot file
            transactions: List of transaction data
            
        Returns:
            Analysis results from Nova
        """
        try:
            # Encode screenshot
            image_base64 = self.encode_image_to_base64(screenshot_path)
            
            # Prepare request body for Nova
            request_body = {
                "inputText": f"""
                Analyze this web automation screenshot and transaction data:
                
                Transaction Data:
                {json.dumps(transactions, indent=2)}
                
                Please provide:
                1. Visual analysis of the screenshot
                2. Data quality assessment
                3. Anomaly detection results
                4. Recommendations for improvement
                """,
                "textGenerationConfig": {
                    "maxTokenCount": 2000,
                    "temperature": 0.1,
                    "topP": 0.9
                },
                "inferenceConfig": {
                    "max_new_tokens": 2000,
                    "temperature": 0.1
                }
            }
            
            # Add image if Nova supports it
            if image_base64:
                request_body["inputImage"] = image_base64
            
            # Call Bedrock with Nova
            response = self.bedrock_runtime.invoke_model(
                modelId=self.models['nova'],
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            return {
                'status': 'success',
                'model': 'amazon-nova',
                'analysis': response_body.get('results', [{}])[0].get('outputText', ''),
                'timestamp': asyncio.get_event_loop().time()
            }
            
        except ClientError as e:
            return {
                'status': 'error',
                'error': f"Nova Bedrock API error: {e}",
                'error_code': e.response['Error']['Code']
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': f"Nova analysis failed: {e}"
            }
    
    async def comprehensive_analysis(self, screenshot_path: str, transactions: List[Dict]) -> Dict[str, Any]:
        """
        Run comprehensive analysis using multiple Bedrock models.
        
        Args:
            screenshot_path: Path to screenshot file
            transactions: List of transaction data
            
        Returns:
            Combined analysis results
        """
        results = {
            'timestamp': asyncio.get_event_loop().time(),
            'screenshot_path': screenshot_path,
            'transaction_count': len(transactions),
            'analyses': {}
        }
        
        # Run Claude analysis
        print("🧠 Running Claude analysis...")
        claude_result = await self.analyze_with_claude(screenshot_path, transactions)
        results['analyses']['claude'] = claude_result
        
        # Run Nova analysis
        print("🤖 Running Nova analysis...")
        nova_result = await self.analyze_with_nova(screenshot_path, transactions)
        results['analyses']['nova'] = nova_result
        
        # Combine insights
        successful_analyses = [
            name for name, result in results['analyses'].items() 
            if result['status'] == 'success'
        ]
        
        results['summary'] = {
            'successful_models': successful_analyses,
            'total_models': len(results['analyses']),
            'success_rate': len(successful_analyses) / len(results['analyses'])
        }
        
        return results


async def run_bedrock_analysis():
    """Main function to run AVEO-Playwright with Bedrock analysis."""
    
    print("🚀 AVEO-Playwright + AWS Bedrock Integration")
    print("=" * 60)
    
    try:
        # Step 1: Run AVEO-Playwright automation
        print("1. Running AVEO-Playwright automation...")
        automation_result = await run_all(headless=True)
        
        print(f"✅ Automation completed:")
        print(f"   - Screenshot: {automation_result['screenshot_path']}")
        print(f"   - Transactions: {len(automation_result['transactions'])}")
        
        # Step 2: Initialize Bedrock integrator
        print("\n2. Initializing AWS Bedrock integration...")
        bedrock = BedrockIntegrator()
        
        # Step 3: Run comprehensive analysis
        print("\n3. Running AI analysis via Bedrock...")
        analysis_result = await bedrock.comprehensive_analysis(
            automation_result['screenshot_path'],
            automation_result['transactions']
        )
        
        # Step 4: Save results
        results_file = Path("output/data/bedrock_analysis_results.json")
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, "w") as f:
            json.dump(analysis_result, f, indent=2, default=str)
        
        # Step 5: Display summary
        print("\n" + "=" * 60)
        print("BEDROCK ANALYSIS SUMMARY")
        print("=" * 60)
        
        summary = analysis_result['summary']
        print(f"✅ Models analyzed: {summary['total_models']}")
        print(f"✅ Successful analyses: {len(summary['successful_models'])}")
        print(f"✅ Success rate: {summary['success_rate']:.1%}")
        print(f"✅ Results saved to: {results_file}")
        
        # Display individual results
        for model_name, result in analysis_result['analyses'].items():
            status_emoji = "✅" if result['status'] == 'success' else "❌"
            print(f"{status_emoji} {model_name.title()}: {result['status']}")
            
            if result['status'] == 'success' and 'analysis' in result:
                # Show first 200 characters of analysis
                analysis_preview = result['analysis'][:200] + "..." if len(result['analysis']) > 200 else result['analysis']
                print(f"   Preview: {analysis_preview}")
        
        return analysis_result
        
    except Exception as e:
        print(f"\n❌ Bedrock integration failed: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    asyncio.run(run_bedrock_analysis())