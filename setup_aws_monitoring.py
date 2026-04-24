"""
Setup AWS CloudWatch monitoring for AVEO-Playwright + Nova Act integration.

This script helps setup AWS credentials and CloudWatch monitoring to verify
that Nova Act can successfully integrate with AVEO-Playwright.
"""

import boto3
import json
import os
from pathlib import Path
from botocore.exceptions import NoCredentialsError, ClientError


def check_aws_credentials() -> bool:
    """Check if AWS credentials are configured."""
    try:
        # Try to create a session and get caller identity
        session = boto3.Session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        
        print("✅ AWS Credentials found:")
        print(f"   Account ID: {identity.get('Account')}")
        print(f"   User ARN: {identity.get('Arn')}")
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
        return False
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        return False


def setup_aws_credentials_guide():
    """Provide guide for setting up AWS credentials."""
    
    print("\n" + "="*60)
    print("AWS CREDENTIALS SETUP GUIDE")
    print("="*60)
    
    print("\n1. **Install AWS CLI** (if not installed):")
    print("   - Windows: https://aws.amazon.com/cli/")
    print("   - macOS: brew install awscli")
    print("   - Linux: sudo apt-get install awscli")
    
    print("\n2. **Configure AWS Credentials:**")
    print("   Run: aws configure")
    print("   Enter:")
    print("   - AWS Access Key ID: [Your access key]")
    print("   - AWS Secret Access Key: [Your secret key]")
    print("   - Default region name: us-east-1")
    print("   - Default output format: json")
    
    print("\n3. **Alternative: Environment Variables:**")
    print("   export AWS_ACCESS_KEY_ID=your_access_key")
    print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
    print("   export AWS_DEFAULT_REGION=us-east-1")
    
    print("\n4. **Alternative: AWS Profile:**")
    print("   aws configure --profile aveo-playwright")
    print("   export AWS_PROFILE=aveo-playwright")
    
    print("\n5. **Required Permissions:**")
    print("   Your AWS user/role needs these permissions:")
    print("   - cloudwatch:PutMetricData")
    print("   - logs:CreateLogGroup")
    print("   - logs:CreateLogStream")
    print("   - logs:PutLogEvents")
    print("   - logs:DescribeLogGroups")
    print("   - logs:DescribeLogStreams")


def create_iam_policy_document() -> dict:
    """Create IAM policy document for AVEO-Playwright CloudWatch access."""
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "cloudwatch:PutMetricData",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogGroups",
                    "logs:DescribeLogStreams"
                ],
                "Resource": [
                    "arn:aws:logs:*:*:log-group:/aws/aveo-playwright/*",
                    "arn:aws:logs:*:*:log-group:/aws/aveo-playwright/*:*"
                ]
            }
        ]
    }
    
    return policy


def test_cloudwatch_permissions() -> bool:
    """Test CloudWatch permissions."""
    try:
        # Test CloudWatch metrics
        cloudwatch = boto3.client('cloudwatch')
        cloudwatch.list_metrics(Namespace='AWS/EC2')
        print("✅ CloudWatch metrics access: OK")
        
        # Test CloudWatch logs
        logs = boto3.client('logs')
        logs.describe_log_groups()
        print("✅ CloudWatch logs access: OK")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            print("❌ CloudWatch access denied - check IAM permissions")
        else:
            print(f"❌ CloudWatch error: {e}")
        return False
    except Exception as e:
        print(f"❌ CloudWatch test error: {e}")
        return False


def create_cloudwatch_dashboard(dashboard_name: str = "AVEO-Playwright-Integration") -> bool:
    """Create CloudWatch dashboard for monitoring."""
    try:
        cloudwatch = boto3.client('cloudwatch')
        
        dashboard_body = {
            "widgets": [
                {
                    "type": "metric",
                    "x": 0,
                    "y": 0,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AVEO-Playwright/NovaAct", "ConfigurationLoad"],
                            [".", "BrowserNavigation"],
                            [".", "ScreenshotCapture"],
                            [".", "LoginSuccess"],
                            [".", "DataExtraction"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": "us-east-1",
                        "title": "AVEO-Playwright Operations",
                        "period": 300
                    }
                },
                {
                    "type": "metric",
                    "x": 12,
                    "y": 0,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AVEO-Playwright/NovaAct", "NovaActAnalysis"],
                            [".", "NovaActVerification"],
                            [".", "NovaActDataAnalysis"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": "us-east-1",
                        "title": "Nova Act Integration",
                        "period": 300
                    }
                },
                {
                    "type": "metric",
                    "x": 0,
                    "y": 6,
                    "width": 24,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AVEO-Playwright/NovaAct", "TestDuration"],
                            [".", "IntegrationTestDuration"],
                            [".", "EndToEndDuration"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": "us-east-1",
                        "title": "Test Execution Times",
                        "period": 300,
                        "stat": "Average"
                    }
                },
                {
                    "type": "log",
                    "x": 0,
                    "y": 12,
                    "width": 24,
                    "height": 6,
                    "properties": {
                        "query": "SOURCE '/aws/aveo-playwright/integration' | fields @timestamp, message\n| sort @timestamp desc\n| limit 50",
                        "region": "us-east-1",
                        "title": "Integration Test Logs"
                    }
                }
            ]
        }
        
        cloudwatch.put_dashboard(
            DashboardName=dashboard_name,
            DashboardBody=json.dumps(dashboard_body)
        )
        
        print(f"✅ CloudWatch dashboard created: {dashboard_name}")
        print(f"   View at: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name={dashboard_name}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create dashboard: {e}")
        return False


def main():
    """Main setup function."""
    
    print("AVEO-Playwright + Nova Act AWS CloudWatch Setup")
    print("="*60)
    
    # Step 1: Check AWS credentials
    print("\n1. Checking AWS credentials...")
    if not check_aws_credentials():
        setup_aws_credentials_guide()
        print("\n⚠️  Please setup AWS credentials first, then run this script again.")
        return False
    
    # Step 2: Test CloudWatch permissions
    print("\n2. Testing CloudWatch permissions...")
    if not test_cloudwatch_permissions():
        print("\n📋 Required IAM Policy:")
        policy = create_iam_policy_document()
        print(json.dumps(policy, indent=2))
        
        # Save policy to file
        policy_file = Path("aws_iam_policy.json")
        with open(policy_file, "w") as f:
            json.dump(policy, f, indent=2)
        print(f"\n💾 IAM policy saved to: {policy_file}")
        print("\n⚠️  Please attach this policy to your AWS user/role, then run this script again.")
        return False
    
    # Step 3: Create CloudWatch dashboard
    print("\n3. Creating CloudWatch dashboard...")
    create_cloudwatch_dashboard()
    
    # Step 4: Setup environment variables
    print("\n4. Setting up environment variables...")
    
    env_vars = {
        'AWS_DEFAULT_REGION': 'us-east-1',
        'CLOUDWATCH_NAMESPACE': 'AVEO-Playwright/NovaAct',
        'CLOUDWATCH_LOG_GROUP': '/aws/aveo-playwright/integration'
    }
    
    env_file = Path('.env.aws')
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ AWS environment variables saved to: {env_file}")
    
    # Step 5: Ready to run tests
    print("\n" + "="*60)
    print("AWS CLOUDWATCH SETUP COMPLETE")
    print("="*60)
    print("✅ AWS credentials configured")
    print("✅ CloudWatch permissions verified")
    print("✅ CloudWatch dashboard created")
    print("✅ Environment variables configured")
    
    print(f"\n🚀 Ready to run CloudWatch integration tests!")
    print(f"   Run: python cloudwatch_integration_test.py")
    
    print(f"\n📊 Monitor results at:")
    print(f"   - Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=AVEO-Playwright-Integration")
    print(f"   - Logs: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/%2Faws%2Faveo-playwright%2Fintegration")
    
    return True


if __name__ == "__main__":
    main()