# AWS Setup Guide for AVEO-Playwright

This guide walks you through setting up AWS services for AVEO-Playwright integration including S3, CloudWatch, and Bedrock.

## 🔐 **Step 1: Configure AWS Credentials**

### **Option A: Update .env File (Recommended)**

1. **Get your AWS credentials** from AWS Console:
   - Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
   - Click "Users" → Your username → "Security credentials"
   - Click "Create access key" → "Command Line Interface (CLI)"
   - Copy the Access Key ID and Secret Access Key

2. **Update .env file** with your credentials:
   ```env
   # Replace 'isi_disini' with your actual credentials
   AWS_ACCESS_KEY_ID=AKIA...your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
   AWS_REGION=us-east-1
   ```

### **Option B: AWS CLI Configuration**

```bash
aws configure
# Enter your credentials when prompted
```

## 🔒 **Step 2: Setup IAM Permissions**

Your AWS user needs specific permissions. Apply this IAM policy:

### **Attach IAM Policy**

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click "Users" → Your username → "Permissions"
3. Click "Add permissions" → "Attach policies directly"
4. Click "Create policy" → "JSON"
5. Copy and paste the policy from `aws_iam_policy.json`
6. Name it: `AVEO-Playwright-Policy`
7. Attach to your user

### **Required Permissions Summary**

- **CloudWatch**: Metrics and logging
- **S3**: Upload/download to `aveo-playwright-output` bucket
- **Bedrock**: AI model access (Nova Pro, Claude)
- **STS**: Identity verification

## 🗄️ **Step 3: Verify S3 Bucket**

Ensure the S3 bucket exists:

1. Go to [S3 Console](https://s3.console.aws.amazon.com/s3/)
2. Verify bucket `aveo-playwright-output` exists in `us-east-1`
3. If not, create it:
   ```bash
   aws s3 mb s3://aveo-playwright-output --region us-east-1
   ```

## 🧠 **Step 4: Enable Bedrock Models**

Enable access to Bedrock models:

1. Go to [Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click "Model access" in left sidebar
3. Click "Enable specific models"
4. Enable these models:
   - ✅ **Amazon Nova Pro** (`amazon.nova-pro-v1:0`)
   - ✅ **Claude 3 Sonnet** (`anthropic.claude-3-sonnet-20240229-v1:0`)
   - ✅ **Titan Text Express** (`amazon.titan-text-express-v1`)

## 🧪 **Step 5: Test Configuration**

Run the configuration test:

```bash
python test_bedrock_config.py
```

### **Expected Output (Success)**

```
🧪 AVEO-Playwright AWS Configuration Test
============================================================
🔐 Testing AWS Credentials...
✅ AWS_ACCESS_KEY_ID: AKIA1234...
✅ AWS_SECRET_ACCESS_KEY: abcd1234...
✅ AWS_REGION: us-east-1
✅ AWS Account ID: 123456789012
✅ User ARN: arn:aws:iam::123456789012:user/your-username

🧠 Testing Bedrock Access...
✅ Bedrock Region: us-east-1
✅ Model ID: amazon.nova-pro-v1:0
📋 Listing available models...
✅ Found 5 relevant models:
   - amazon.nova-pro-v1:0
   - anthropic.claude-3-sonnet-20240229-v1:0
   - amazon.titan-text-express-v1
✅ Target model 'amazon.nova-pro-v1:0' is available

🚀 Testing Bedrock Runtime...
📤 Sending test request to amazon.nova-pro-v1:0...
✅ Bedrock Response: Bedrock integration test successful
📊 Token Usage:
   - Input tokens: 25
   - Output tokens: 8

🗄️ Testing S3 Access...
✅ S3 Bucket: aveo-playwright-output
✅ S3 Region: us-east-1
✅ S3 bucket 'aveo-playwright-output' is accessible
✅ Found 3 objects in bucket

============================================================
CONFIGURATION TEST SUMMARY
============================================================
✅ Aws Credentials: PASS
✅ Bedrock Access: PASS
✅ Bedrock Runtime: PASS
✅ S3 Access: PASS

🎉 All tests passed! AWS services are ready for use.

🚀 You can now run:
   - python bedrock_integration.py
   - python s3_integration_test.py
   - python cloudwatch_integration_test.py
```

## 🚀 **Step 6: Run Full Integration**

Once all tests pass, run the complete integration:

### **S3 + CloudWatch Integration**
```bash
python s3_integration_test.py
```

### **Bedrock AI Analysis**
```bash
python bedrock_integration.py
```

### **Complete Workflow with All Services**
```python
from vendor_automator.vendor_automator import run_all
from bedrock_integration import BedrockIntegrator

# Run automation with S3 upload
result = await run_all(headless=True, upload_to_s3=True)

# Analyze with Bedrock AI
bedrock = BedrockIntegrator()
analysis = await bedrock.comprehensive_analysis(
    result['screenshot_info']['local_path'],
    result['transactions']
)

print("🎉 Complete integration successful!")
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Credentials Not Configured**
   ```
   ❌ AWS_ACCESS_KEY_ID not configured
   ```
   **Solution**: Update `.env` file with real AWS credentials

2. **Access Denied to Bedrock**
   ```
   ❌ Access denied to Bedrock - check IAM permissions
   ```
   **Solution**: Apply the IAM policy from `aws_iam_policy.json`

3. **Model Not Available**
   ```
   ⚠️ Target model 'amazon.nova-pro-v1:0' not found
   ```
   **Solution**: Enable model access in Bedrock Console

4. **S3 Bucket Not Found**
   ```
   ❌ S3 bucket 'aveo-playwright-output' not found
   ```
   **Solution**: Create bucket or update bucket name in `.env`

5. **Region Mismatch**
   ```
   ❌ Bedrock error: Could not connect to the endpoint
   ```
   **Solution**: Ensure all services use `us-east-1` region

### **Debug Commands**

```bash
# Test AWS credentials
aws sts get-caller-identity

# List S3 buckets
aws s3 ls

# List Bedrock models
aws bedrock list-foundation-models --region us-east-1

# Test Bedrock access
python test_bedrock_config.py
```

## 💰 **Cost Estimation**

### **Monthly Costs (Estimated)**

| Service | Usage | Cost |
|---------|-------|------|
| **S3 Storage** | 1GB data | $0.023 |
| **CloudWatch** | Basic metrics | $3.00 |
| **Bedrock Nova Pro** | 100 requests | $5.00 |
| **Bedrock Claude** | 50 requests | $3.00 |
| **Total** | | **~$11/month** |

*Costs may vary based on usage patterns*

## 📚 **Environment Variables Reference**

```env
# AVEO-Playwright Configuration
USERNAME=testuser
PASSWORD=testpass
BASE_URL=file:///path/to/dummy_site/login.html
HEADLESS=true
TIMEOUT=30

# AWS Credentials (REQUIRED)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# AWS Services
AWS_DEFAULT_REGION=us-east-1
CLOUDWATCH_NAMESPACE=AVEO-Playwright/NovaAct
CLOUDWATCH_LOG_GROUP=/aws/aveo-playwright/integration

# S3 Storage
S3_BUCKET_NAME=aveo-playwright-output
S3_REGION=us-east-1
S3_UPLOAD_ENABLED=true

# Bedrock AI
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
BEDROCK_REGION=us-east-1
```

## 🎯 **Next Steps**

1. ✅ **Configure AWS credentials** in `.env` file
2. ✅ **Apply IAM policy** for required permissions
3. ✅ **Enable Bedrock models** in AWS Console
4. ✅ **Run configuration test** to verify setup
5. ✅ **Test individual integrations** (S3, Bedrock, CloudWatch)
6. ✅ **Run complete workflow** with all services

---

**AWS integration is now ready for production use!** 🚀

For support, check the troubleshooting section or run `python test_bedrock_config.py` for detailed diagnostics.