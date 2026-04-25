"""
Test Bedrock Configuration and API Access

This script tests the Bedrock configuration and verifies API access
before running the full integration.
"""

import asyncio
import json
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError

# Load environment variables
load_dotenv(override=True)


def test_aws_credentials():
    """Test AWS credentials configuration."""
    print("🔐 Testing AWS Credentials...")
    
    # Check environment variables
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION')
    
    if not access_key or access_key == 'isi_disini':
        print("❌ AWS_ACCESS_KEY_ID not configured")
        return False
    
    if not secret_key or secret_key == 'isi_disini':
        print("❌ AWS_SECRET_ACCESS_KEY not configured")
        return False
    
    if not region:
        print("❌ AWS_REGION not configured")
        return False
    
    print(f"✅ AWS_ACCESS_KEY_ID: {access_key[:8]}...")
    print(f"✅ AWS_SECRET_ACCESS_KEY: {secret_key[:8]}...")
    print(f"✅ AWS_REGION: {region}")
    
    # Test credentials with STS
    try:
        sts = boto3.client('sts', region_name=region)
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS Account ID: {identity.get('Account')}")
        print(f"✅ User ARN: {identity.get('Arn')}")
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found or invalid")
        return False
    except ClientError as e:
        print(f"❌ AWS credentials error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_bedrock_access():
    """Test Bedrock service access."""
    print("\n🧠 Testing Bedrock Access...")
    
    region = os.getenv('BEDROCK_REGION', 'us-east-1')
    model_id = os.getenv('BEDROCK_MODEL_ID', 'amazon.nova-pro-v1:0')
    
    print(f"✅ Bedrock Region: {region}")
    print(f"✅ Model ID: {model_id}")
    
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock', region_name=region)
        
        # List available models
        print("📋 Listing available models...")
        response = bedrock.list_foundation_models()
        
        available_models = []
        for model in response.get('modelSummaries', []):
            model_name = model.get('modelId', '')
            if 'nova' in model_name.lower() or 'claude' in model_name.lower():
                available_models.append(model_name)
        
        print(f"✅ Found {len(available_models)} relevant models:")
        for model in available_models[:5]:  # Show first 5
            print(f"   - {model}")
        
        # Check if our target model is available
        if model_id in [m.get('modelId') for m in response.get('modelSummaries', [])]:
            print(f"✅ Target model '{model_id}' is available")
            return True
        else:
            print(f"⚠️  Target model '{model_id}' not found in available models")
            print("Available Nova models:")
            for model in response.get('modelSummaries', []):
                if 'nova' in model.get('modelId', '').lower():
                    print(f"   - {model.get('modelId')}")
            return False
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("❌ Access denied to Bedrock - check IAM permissions")
        else:
            print(f"❌ Bedrock error: {e}")
        return False
    except Exception as e:
        print(f"❌ Bedrock test error: {e}")
        return False


async def test_bedrock_runtime():
    """Test Bedrock Runtime with a simple request."""
    print("\n🚀 Testing Bedrock Runtime...")
    
    region = os.getenv('BEDROCK_REGION', 'us-east-1')
    model_id = os.getenv('BEDROCK_MODEL_ID', 'amazon.nova-pro-v1:0')
    
    try:
        # Initialize Bedrock Runtime client
        bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
        
        # Simple test request
        test_request = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Hello! Please respond with 'Bedrock integration test successful' to confirm you're working."
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 100,
                "temperature": 0.1
            }
        }
        
        print(f"📤 Sending test request to {model_id}...")
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(test_request)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        if 'output' in response_body and 'message' in response_body['output']:
            response_text = response_body['output']['message']['content'][0]['text']
            print(f"✅ Bedrock Response: {response_text}")
            
            # Check usage info
            if 'usage' in response_body:
                usage = response_body['usage']
                print(f"📊 Token Usage:")
                print(f"   - Input tokens: {usage.get('inputTokens', 'N/A')}")
                print(f"   - Output tokens: {usage.get('outputTokens', 'N/A')}")
            
            return True
        else:
            print(f"⚠️  Unexpected response format: {response_body}")
            return False
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ValidationException':
            print(f"❌ Model validation error: {e}")
            print("💡 Try checking if the model ID is correct")
        elif error_code == 'AccessDeniedException':
            print("❌ Access denied to Bedrock Runtime - check IAM permissions")
        else:
            print(f"❌ Bedrock Runtime error: {e}")
        return False
    except Exception as e:
        print(f"❌ Runtime test error: {e}")
        return False


def test_s3_access():
    """Test S3 bucket access."""
    print("\n🗄️ Testing S3 Access...")
    
    bucket_name = os.getenv('S3_BUCKET_NAME', 'aveo-playwright-output')
    region = os.getenv('S3_REGION', 'us-east-1')
    
    print(f"✅ S3 Bucket: {bucket_name}")
    print(f"✅ S3 Region: {region}")
    
    try:
        s3 = boto3.client('s3', region_name=region)
        
        # Test bucket access
        s3.head_bucket(Bucket=bucket_name)
        print(f"✅ S3 bucket '{bucket_name}' is accessible")
        
        # List recent objects
        response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
        object_count = response.get('KeyCount', 0)
        print(f"✅ Found {object_count} objects in bucket")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ S3 bucket '{bucket_name}' not found")
        elif error_code == '403':
            print(f"❌ Access denied to S3 bucket '{bucket_name}'")
        else:
            print(f"❌ S3 error: {e}")
        return False
    except Exception as e:
        print(f"❌ S3 test error: {e}")
        return False


async def main():
    """Run all configuration tests."""
    print("🧪 AVEO-Playwright AWS Configuration Test")
    print("=" * 60)
    
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Test 1: AWS Credentials
    credentials_ok = test_aws_credentials()
    test_results['tests']['aws_credentials'] = credentials_ok
    
    if not credentials_ok:
        print("\n❌ AWS credentials test failed. Please configure your credentials first.")
        print("\n💡 To configure credentials:")
        print("1. Update .env file with your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        print("2. Or run: aws configure")
        return test_results
    
    # Test 2: Bedrock Access
    bedrock_access_ok = test_bedrock_access()
    test_results['tests']['bedrock_access'] = bedrock_access_ok
    
    # Test 3: Bedrock Runtime
    if bedrock_access_ok:
        bedrock_runtime_ok = await test_bedrock_runtime()
        test_results['tests']['bedrock_runtime'] = bedrock_runtime_ok
    else:
        print("⏭️  Skipping Bedrock Runtime test (access failed)")
        test_results['tests']['bedrock_runtime'] = False
    
    # Test 4: S3 Access
    s3_ok = test_s3_access()
    test_results['tests']['s3_access'] = s3_ok
    
    # Summary
    print("\n" + "=" * 60)
    print("CONFIGURATION TEST SUMMARY")
    print("=" * 60)
    
    all_tests_passed = all(test_results['tests'].values())
    
    for test_name, result in test_results['tests'].items():
        status_emoji = "✅" if result else "❌"
        print(f"{status_emoji} {test_name.replace('_', ' ').title()}: {'PASS' if result else 'FAIL'}")
    
    if all_tests_passed:
        print("\n🎉 All tests passed! AWS services are ready for use.")
        print("\n🚀 You can now run:")
        print("   - python bedrock_integration.py")
        print("   - python s3_integration_test.py")
        print("   - python cloudwatch_integration_test.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        
        if not credentials_ok:
            print("\n🔧 Next steps:")
            print("1. Get your AWS credentials from AWS Console")
            print("2. Update .env file with real values")
            print("3. Run this test again")
    
    return test_results


if __name__ == "__main__":
    asyncio.run(main())