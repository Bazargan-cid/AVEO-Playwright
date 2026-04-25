# S3 Integration Guide for AVEO-Playwright

This guide explains how to configure and use S3 storage integration with AVEO-Playwright for automatic upload of screenshots and transaction data.

## 🗄️ **S3 Bucket Setup**

### **Bucket Configuration**
- **Bucket Name**: `aveo-playwright-output`
- **Region**: `us-east-1`
- **Access**: Private (uses IAM permissions)
- **Folder Structure**:
  ```
  aveo-playwright-output/
  ├── screenshots/
  │   └── YYYY/MM/DD/
  │       └── timestamp.png
  ├── data/
  │   └── YYYY/MM/DD/
  │       └── transactions_timestamp.json
  └── test/
      └── permission_test_files.txt
  ```

## 🔐 **IAM Permissions Required**

Your AWS user/role needs these S3 permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::aveo-playwright-output",
        "arn:aws:s3:::aveo-playwright-output/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:HeadBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::aveo-playwright-output"
    }
  ]
}
```

## ⚙️ **Configuration**

### **Environment Variables**

Add these to your `.env` file:

```env
# S3 Configuration
S3_BUCKET_NAME=aveo-playwright-output
S3_REGION=us-east-1
S3_UPLOAD_ENABLED=true
```

### **AWS Credentials**

Configure AWS credentials using one of these methods:

1. **AWS CLI** (Recommended):
   ```bash
   aws configure
   ```

2. **Environment Variables**:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   ```

3. **IAM Role** (for EC2/Lambda):
   - Attach IAM role with required permissions

## 🚀 **Usage**

### **Basic Usage with S3 Upload**

```python
from vendor_automator.vendor_automator import run_all

# Run automation with S3 upload (default)
result = await run_all(headless=True, upload_to_s3=True)

# Check results
print(f"Screenshot: {result['screenshot_info']['local_path']}")
if 's3_upload' in result['screenshot_info']:
    s3_info = result['screenshot_info']['s3_upload']
    if s3_info['status'] == 'success':
        print(f"S3 URL: {s3_info['s3_url']}")

print(f"Transactions: {len(result['transactions'])} extracted")
if 's3_upload' in result['transaction_info']:
    s3_info = result['transaction_info']['s3_upload']
    if s3_info['status'] == 'success':
        print(f"S3 URL: {s3_info['s3_url']}")
```

### **Local Storage Only**

```python
# Disable S3 upload (local storage only)
result = await run_all(headless=True, upload_to_s3=False)
```

### **Direct S3 Storage Manager Usage**

```python
from s3_storage import S3StorageManager

# Initialize S3 manager
s3_manager = S3StorageManager()

# Upload file
upload_result = await s3_manager.upload_file_to_s3(
    local_path="output/screenshots/screenshot.png",
    s3_key="screenshots/2026/04/25/screenshot.png",
    content_type="image/png"
)

# List recent files
recent_files = s3_manager.list_s3_objects(prefix="screenshots/", max_keys=10)

# Generate presigned URL (1 hour expiry)
presigned_url = s3_manager.generate_presigned_url(
    s3_key="screenshots/2026/04/25/screenshot.png",
    expiration=3600
)
```

## 📊 **Result Structure**

When S3 upload is enabled, the result structure includes S3 information:

```python
{
    "screenshot_info": {
        "local_path": "output/screenshots/2026-04-25_19-40-10.png",
        "filename": "2026-04-25_19-40-10.png",
        "timestamp": "2026-04-25_19-40-10",
        "s3_upload": {
            "status": "success",
            "local_path": "output/screenshots/2026-04-25_19-40-10.png",
            "s3_key": "screenshots/2026/04/25/2026-04-25_19-40-10.png",
            "s3_url": "https://aveo-playwright-output.s3.us-east-1.amazonaws.com/screenshots/2026/04/25/2026-04-25_19-40-10.png",
            "bucket": "aveo-playwright-output",
            "size_bytes": 26336
        }
    },
    "transaction_info": {
        "transactions": [...],
        "local_path": "output/data/transactions_2026-04-25_19-40-12.json",
        "filename": "transactions_2026-04-25_19-40-12.json",
        "count": 5,
        "timestamp": "2026-04-25_19-40-12",
        "s3_upload": {
            "status": "success",
            "s3_url": "https://aveo-playwright-output.s3.us-east-1.amazonaws.com/data/2026/04/25/transactions_2026-04-25_19-40-12.json",
            ...
        }
    },
    "s3_summary": {
        "total_uploads": 2,
        "successful_uploads": 2,
        "success_rate": 1.0,
        "s3_available": true,
        "uploads": {
            "screenshot": {...},
            "transaction_data": {...}
        }
    }
}
```

## 🧪 **Testing S3 Integration**

### **Run S3 Integration Test**

```bash
python s3_integration_test.py
```

This test will:
1. ✅ Check S3 connectivity and permissions
2. ✅ Run complete automation workflow with S3 upload
3. ✅ Verify files are uploaded correctly
4. ✅ Test presigned URL generation
5. ✅ Generate comprehensive test report

### **Expected Output**

```
🎉 All S3 uploads successful!
✅ Automation completed successfully
✅ Local files created and accessible
✅ S3 bucket: s3://aveo-playwright-output
✅ AWS Console: https://s3.console.aws.amazon.com/s3/buckets/aveo-playwright-output
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **S3 Not Available**
   ```
   ❌ S3 not available - check credentials and bucket access
   ```
   - **Solution**: Configure AWS credentials and verify bucket exists

2. **Access Denied**
   ```
   ❌ Access denied to S3 bucket 'aveo-playwright-output'
   ```
   - **Solution**: Check IAM permissions and bucket policy

3. **ACL Not Supported**
   ```
   AccessControlListNotSupported: The bucket does not allow ACLs
   ```
   - **Solution**: Already fixed in code - ACLs are not set

4. **Bucket Not Found**
   ```
   ❌ S3 bucket 'aveo-playwright-output' not found
   ```
   - **Solution**: Create bucket or update bucket name in configuration

### **Fallback Behavior**

- If S3 is not available, files are stored locally only
- No errors are thrown - graceful degradation
- S3 status is reported in results for monitoring

## 📈 **Monitoring**

### **CloudWatch Integration**

S3 uploads are monitored via CloudWatch metrics:
- `S3Upload` metric with dimensions:
  - `FileType`: "Screenshot" or "TransactionData"
  - `SessionId`: Unique session identifier

### **S3 Console**

Monitor uploads in AWS S3 Console:
- **URL**: https://s3.console.aws.amazon.com/s3/buckets/aveo-playwright-output
- **Folder Structure**: Organized by date (YYYY/MM/DD)
- **File Types**: PNG screenshots and JSON transaction data

## 💰 **Cost Considerations**

### **S3 Storage Costs** (us-east-1):
- **Standard Storage**: $0.023 per GB/month
- **PUT Requests**: $0.0005 per 1,000 requests
- **GET Requests**: $0.0004 per 1,000 requests

### **Estimated Monthly Costs**:
- **100 automation runs/month**: ~$0.10-0.50
- **1,000 automation runs/month**: ~$1.00-5.00
- **10,000 automation runs/month**: ~$10.00-50.00

*Costs depend on file sizes and retention period*

## 🔗 **Integration with Other Services**

### **CloudWatch Integration**

S3 uploads are automatically logged to CloudWatch:

```python
from cloudwatch_integration_test import CloudWatchIntegrationTester

# Run with both CloudWatch and S3 monitoring
tester = CloudWatchIntegrationTester()
results = await tester.run_comprehensive_test_suite()
```

### **Bedrock Integration**

S3 URLs can be used with Bedrock for AI analysis:

```python
from bedrock_integration import BedrockIntegrator

# Analyze S3-stored results with Bedrock
bedrock = BedrockIntegrator()
analysis = await bedrock.analyze_with_claude(
    screenshot_path=result['screenshot_info']['s3_upload']['s3_url'],
    transactions=result['transactions']
)
```

## 📚 **API Reference**

### **S3StorageManager Class**

```python
class S3StorageManager:
    def __init__(self, bucket_name: str = "aveo-playwright-output", region_name: str = "us-east-1")
    
    async def upload_file_to_s3(self, local_path: str, s3_key: str, content_type: str = None) -> Dict[str, Any]
    async def upload_screenshot(self, screenshot_path: str, session_id: str = None) -> Dict[str, Any]
    async def upload_json_data(self, json_path: str, session_id: str = None) -> Dict[str, Any]
    async def upload_automation_results(self, result: Dict[str, Any], session_id: str = None) -> Dict[str, Any]
    
    def list_s3_objects(self, prefix: str = "", max_keys: int = 100) -> List[Dict[str, Any]]
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]
```

### **Updated Functions**

```python
# Updated function signatures with S3 support
async def capture_screenshot(page: Page, output_dir: str = "output/screenshots", upload_to_s3: bool = True) -> Dict[str, Any]
async def extract_transaction_data(page: Page, output_dir: str = "output/data", upload_to_s3: bool = True) -> Dict[str, Any]
async def run_all(headless: bool = False, upload_to_s3: bool = True) -> Dict[str, Any]
```

## 🎯 **Next Steps**

1. **Verify S3 bucket exists**: `aveo-playwright-output` in `us-east-1`
2. **Configure AWS credentials**: Use `aws configure` or environment variables
3. **Update IAM permissions**: Apply the policy from `aws_iam_policy.json`
4. **Test integration**: Run `python s3_integration_test.py`
5. **Monitor uploads**: Check S3 console and CloudWatch metrics

---

**S3 Integration is now fully configured and ready for production use!** 🚀