"""
S3 Integration Test for AVEO-Playwright

This script tests the S3 upload functionality and verifies that screenshots
and JSON data are properly uploaded to the S3 bucket.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# AVEO-Playwright imports
from vendor_automator.vendor_automator import run_all, load_config
from s3_storage import S3StorageManager


async def test_s3_integration():
    """Test complete S3 integration workflow."""
    
    print("🚀 AVEO-Playwright S3 Integration Test")
    print("=" * 60)
    
    # Initialize S3 storage manager
    s3_manager = S3StorageManager()
    
    # Test 1: Check S3 connectivity
    print("\n1. Testing S3 connectivity...")
    if s3_manager.s3_available:
        print(f"✅ S3 bucket '{s3_manager.bucket_name}' is accessible")
        
        # List recent objects
        recent_objects = s3_manager.list_s3_objects(max_keys=5)
        print(f"📁 Found {len(recent_objects)} recent objects in bucket")
        
        for obj in recent_objects[:3]:
            print(f"   - {obj['key']} ({obj['size']} bytes)")
    else:
        print("❌ S3 not available - check credentials and bucket access")
        print("⚠️  Continuing with local storage only...")
    
    # Test 2: Run automation with S3 upload
    print("\n2. Running automation with S3 upload...")
    
    start_time = time.time()
    
    try:
        # Run complete automation workflow
        result = await run_all(headless=True, upload_to_s3=True)
        
        duration = time.time() - start_time
        
        print(f"✅ Automation completed in {duration:.2f} seconds")
        
        # Test 3: Verify results
        print("\n3. Verifying results...")
        
        # Check screenshot
        screenshot_info = result['screenshot_info']
        print(f"📸 Screenshot: {screenshot_info['local_path']}")
        
        if 's3_upload' in screenshot_info:
            s3_upload = screenshot_info['s3_upload']
            if s3_upload['status'] == 'success':
                print(f"✅ Screenshot uploaded to S3: {s3_upload['s3_url']}")
            else:
                print(f"❌ Screenshot S3 upload failed: {s3_upload.get('error', 'Unknown error')}")
        else:
            print("ℹ️  Screenshot S3 upload skipped (S3 not available)")
        
        # Check transaction data
        transaction_info = result['transaction_info']
        print(f"📊 Transaction data: {transaction_info['local_path']} ({transaction_info['count']} transactions)")
        
        if 's3_upload' in transaction_info:
            s3_upload = transaction_info['s3_upload']
            if s3_upload['status'] == 'success':
                print(f"✅ Transaction data uploaded to S3: {s3_upload['s3_url']}")
            else:
                print(f"❌ Transaction data S3 upload failed: {s3_upload.get('error', 'Unknown error')}")
        else:
            print("ℹ️  Transaction data S3 upload skipped (S3 not available)")
        
        # Check S3 summary
        if 's3_summary' in result:
            s3_summary = result['s3_summary']
            print(f"\n📊 S3 Upload Summary:")
            print(f"   - Total uploads: {s3_summary['total_uploads']}")
            print(f"   - Successful uploads: {s3_summary['successful_uploads']}")
            print(f"   - Success rate: {s3_summary['success_rate']:.1%}")
            print(f"   - S3 available: {s3_summary['s3_available']}")
        
        # Test 4: Verify files exist in S3
        if s3_manager.s3_available:
            print("\n4. Verifying files in S3 bucket...")
            
            # List objects with today's prefix
            today_prefix = datetime.now().strftime("%Y/%m/%d")
            
            screenshot_objects = s3_manager.list_s3_objects(f"screenshots/{today_prefix}")
            data_objects = s3_manager.list_s3_objects(f"data/{today_prefix}")
            
            print(f"📸 Screenshots in S3 today: {len(screenshot_objects)}")
            for obj in screenshot_objects[-3:]:  # Show last 3
                print(f"   - {obj['key']} ({obj['size']} bytes)")
            
            print(f"📊 Data files in S3 today: {len(data_objects)}")
            for obj in data_objects[-3:]:  # Show last 3
                print(f"   - {obj['key']} ({obj['size']} bytes)")
        
        # Test 5: Generate presigned URLs
        if s3_manager.s3_available and 's3_upload' in screenshot_info and screenshot_info['s3_upload']['status'] == 'success':
            print("\n5. Testing presigned URL generation...")
            
            s3_key = screenshot_info['s3_upload']['s3_key']
            presigned_url = s3_manager.generate_presigned_url(s3_key, expiration=3600)
            
            if presigned_url:
                print(f"✅ Generated presigned URL (expires in 1 hour)")
                print(f"   URL: {presigned_url[:80]}...")
            else:
                print("❌ Failed to generate presigned URL")
        
        # Save test results
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'automation_result': result,
            's3_available': s3_manager.s3_available,
            'bucket_name': s3_manager.bucket_name,
            'region': s3_manager.region_name
        }
        
        results_file = Path("output/data/s3_integration_test_results.json")
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, "w") as f:
            json.dump(test_results, f, indent=2, default=str)
        
        print(f"\n💾 Test results saved to: {results_file}")
        
        # Final summary
        print("\n" + "=" * 60)
        print("S3 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        if s3_manager.s3_available:
            if 's3_summary' in result:
                s3_summary = result['s3_summary']
                if s3_summary['success_rate'] == 1.0:
                    print("🎉 All S3 uploads successful!")
                elif s3_summary['success_rate'] > 0:
                    print(f"⚠️  Partial S3 upload success: {s3_summary['success_rate']:.1%}")
                else:
                    print("❌ All S3 uploads failed")
            else:
                print("⚠️  S3 summary not available")
        else:
            print("ℹ️  S3 not available - local storage used")
        
        print(f"✅ Automation completed successfully")
        print(f"✅ Local files created and accessible")
        
        if s3_manager.s3_available:
            print(f"✅ S3 bucket: s3://{s3_manager.bucket_name}")
            print(f"✅ AWS Console: https://s3.console.aws.amazon.com/s3/buckets/{s3_manager.bucket_name}")
        
        return test_results
        
    except Exception as e:
        print(f"\n❌ S3 integration test failed: {str(e)}")
        return {"error": str(e)}


async def test_s3_permissions():
    """Test S3 permissions and bucket access."""
    
    print("\n🔐 Testing S3 Permissions")
    print("-" * 40)
    
    s3_manager = S3StorageManager()
    
    if not s3_manager.s3_available:
        print("❌ S3 not available")
        return False
    
    try:
        # Test 1: List objects (read permission)
        objects = s3_manager.list_s3_objects(max_keys=1)
        print("✅ List objects: OK")
        
        # Test 2: Upload test file (write permission)
        test_file = Path("output/test_s3_upload.txt")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(test_file, "w") as f:
            f.write(f"S3 test upload at {datetime.now().isoformat()}")
        
        upload_result = await s3_manager.upload_file_to_s3(
            str(test_file), 
            f"test/s3_permission_test_{int(time.time())}.txt",
            "text/plain"
        )
        
        if upload_result['status'] == 'success':
            print("✅ Upload file: OK")
            print(f"   Test file uploaded: {upload_result['s3_url']}")
        else:
            print(f"❌ Upload file: FAILED - {upload_result.get('error', 'Unknown error')}")
            return False
        
        # Clean up test file
        test_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ S3 permission test failed: {e}")
        return False


if __name__ == "__main__":
    async def main():
        # Test S3 permissions first
        permissions_ok = await test_s3_permissions()
        
        if permissions_ok:
            print("\n" + "=" * 60)
        
        # Run full integration test
        await test_s3_integration()
    
    asyncio.run(main())