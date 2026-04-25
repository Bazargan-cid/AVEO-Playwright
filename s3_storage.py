"""
S3 Storage Integration for AVEO-Playwright

This module provides S3 upload functionality for screenshots and JSON data
with fallback to local storage.
"""

import asyncio
import json
import boto3
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError, NoCredentialsError
import logging

logger = logging.getLogger(__name__)


class S3StorageManager:
    """Manages S3 uploads for AVEO-Playwright outputs."""
    
    def __init__(self, bucket_name: str = "aveo-playwright-output", region_name: str = "us-east-1"):
        """
        Initialize S3 storage manager.
        
        Args:
            bucket_name: S3 bucket name
            region_name: AWS region
        """
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.s3_client = None
        self.s3_available = False
        
        # Initialize S3 client
        self._initialize_s3_client()
    
    def _initialize_s3_client(self):
        """Initialize S3 client and check availability."""
        try:
            self.s3_client = boto3.client('s3', region_name=self.region_name)
            
            # Test S3 access by checking if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            self.s3_available = True
            logger.info(f"✅ S3 bucket '{self.bucket_name}' is accessible")
            
        except NoCredentialsError:
            logger.warning("❌ AWS credentials not found - using local storage only")
            self.s3_available = False
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"❌ S3 bucket '{self.bucket_name}' not found")
            elif error_code == '403':
                logger.error(f"❌ Access denied to S3 bucket '{self.bucket_name}'")
            else:
                logger.error(f"❌ S3 error: {e}")
            self.s3_available = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize S3: {e}")
            self.s3_available = False
    
    def generate_s3_key(self, file_type: str, filename: str, session_id: str = None) -> str:
        """
        Generate S3 key with organized folder structure.
        
        Args:
            file_type: Type of file ('screenshots', 'data', 'logs')
            filename: Original filename
            session_id: Optional session ID for grouping
            
        Returns:
            S3 key path
        """
        timestamp = datetime.now().strftime("%Y/%m/%d")
        
        if session_id:
            return f"{file_type}/{timestamp}/{session_id}/{filename}"
        else:
            return f"{file_type}/{timestamp}/{filename}"
    
    async def upload_file_to_s3(self, local_path: str, s3_key: str, 
                               content_type: str = None) -> Dict[str, Any]:
        """
        Upload file to S3 bucket.
        
        Args:
            local_path: Path to local file
            s3_key: S3 key (path) for the file
            content_type: MIME type of the file
            
        Returns:
            Upload result with S3 URL or error
        """
        if not self.s3_available:
            return {
                'status': 'skipped',
                'reason': 'S3 not available',
                'local_path': local_path
            }
        
        try:
            # Auto-detect content type if not provided
            if not content_type:
                if local_path.endswith('.png'):
                    content_type = 'image/png'
                elif local_path.endswith('.json'):
                    content_type = 'application/json'
                else:
                    content_type = 'binary/octet-stream'
            
            # Upload file
            extra_args = {'ContentType': content_type}
            
            # Note: Not setting ACL as bucket may not support ACLs
            # Files will use bucket's default permissions
            
            self.s3_client.upload_file(
                local_path, 
                self.bucket_name, 
                s3_key,
                ExtraArgs=extra_args
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_key}"
            
            logger.info(f"✅ Uploaded to S3: {s3_key}")
            
            return {
                'status': 'success',
                'local_path': local_path,
                's3_key': s3_key,
                's3_url': s3_url,
                'bucket': self.bucket_name,
                'size_bytes': Path(local_path).stat().st_size
            }
            
        except ClientError as e:
            logger.error(f"❌ S3 upload failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'local_path': local_path,
                's3_key': s3_key
            }
        except Exception as e:
            logger.error(f"❌ Upload error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'local_path': local_path
            }
    
    async def upload_screenshot(self, screenshot_path: str, session_id: str = None) -> Dict[str, Any]:
        """
        Upload screenshot to S3.
        
        Args:
            screenshot_path: Path to screenshot file
            session_id: Optional session ID
            
        Returns:
            Upload result
        """
        filename = Path(screenshot_path).name
        s3_key = self.generate_s3_key('screenshots', filename, session_id)
        
        return await self.upload_file_to_s3(screenshot_path, s3_key, 'image/png')
    
    async def upload_json_data(self, json_path: str, session_id: str = None) -> Dict[str, Any]:
        """
        Upload JSON data file to S3.
        
        Args:
            json_path: Path to JSON file
            session_id: Optional session ID
            
        Returns:
            Upload result
        """
        filename = Path(json_path).name
        s3_key = self.generate_s3_key('data', filename, session_id)
        
        return await self.upload_file_to_s3(json_path, s3_key, 'application/json')
    
    async def upload_automation_results(self, result: Dict[str, Any], 
                                      session_id: str = None) -> Dict[str, Any]:
        """
        Upload complete automation results (screenshot + transactions) to S3.
        
        Args:
            result: Automation result from run_all()
            session_id: Optional session ID
            
        Returns:
            Combined upload results
        """
        upload_results = {
            'session_id': session_id or f"session-{int(datetime.now().timestamp())}",
            'timestamp': datetime.now().isoformat(),
            'uploads': {}
        }
        
        # Upload screenshot
        if 'screenshot_path' in result:
            logger.info("📸 Uploading screenshot to S3...")
            screenshot_result = await self.upload_screenshot(
                result['screenshot_path'], 
                upload_results['session_id']
            )
            upload_results['uploads']['screenshot'] = screenshot_result
        
        # Create and upload transactions JSON
        if 'transactions' in result:
            logger.info("📊 Uploading transaction data to S3...")
            
            # Create temporary JSON file
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            temp_json_path = f"output/data/transactions_{timestamp}.json"
            
            # Ensure directory exists
            Path(temp_json_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write transactions to JSON file
            with open(temp_json_path, 'w') as f:
                json.dump(result['transactions'], f, indent=2)
            
            # Upload JSON file
            json_result = await self.upload_json_data(
                temp_json_path, 
                upload_results['session_id']
            )
            upload_results['uploads']['transactions'] = json_result
        
        # Calculate summary
        successful_uploads = [
            name for name, upload in upload_results['uploads'].items()
            if upload['status'] == 'success'
        ]
        
        upload_results['summary'] = {
            'total_files': len(upload_results['uploads']),
            'successful_uploads': len(successful_uploads),
            'success_rate': len(successful_uploads) / len(upload_results['uploads']) if upload_results['uploads'] else 0,
            's3_available': self.s3_available
        }
        
        return upload_results
    
    def list_s3_objects(self, prefix: str = "", max_keys: int = 100) -> List[Dict[str, Any]]:
        """
        List objects in S3 bucket.
        
        Args:
            prefix: S3 key prefix to filter objects
            max_keys: Maximum number of objects to return
            
        Returns:
            List of S3 objects
        """
        if not self.s3_available:
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            objects = []
            for obj in response.get('Contents', []):
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{obj['Key']}"
                })
            
            return objects
            
        except Exception as e:
            logger.error(f"❌ Failed to list S3 objects: {e}")
            return []
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for S3 object.
        
        Args:
            s3_key: S3 key of the object
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned URL or None if failed
        """
        if not self.s3_available:
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"❌ Failed to generate presigned URL: {e}")
            return None


# Global S3 storage manager instance
s3_storage = S3StorageManager()


async def upload_to_s3_with_fallback(local_path: str, file_type: str, 
                                    session_id: str = None) -> Dict[str, Any]:
    """
    Convenience function to upload file to S3 with local fallback.
    
    Args:
        local_path: Path to local file
        file_type: Type of file ('screenshots', 'data', 'logs')
        session_id: Optional session ID
        
    Returns:
        Upload result
    """
    filename = Path(local_path).name
    s3_key = s3_storage.generate_s3_key(file_type, filename, session_id)
    
    result = await s3_storage.upload_file_to_s3(local_path, s3_key)
    
    # Always keep local copy as backup
    result['local_backup'] = local_path
    
    return result


if __name__ == "__main__":
    # Test S3 connectivity
    async def test_s3():
        print("🧪 Testing S3 connectivity...")
        
        # Test bucket access
        if s3_storage.s3_available:
            print(f"✅ S3 bucket '{s3_storage.bucket_name}' is accessible")
            
            # List recent objects
            objects = s3_storage.list_s3_objects(max_keys=5)
            print(f"📁 Found {len(objects)} recent objects in bucket")
            
            for obj in objects[:3]:  # Show first 3
                print(f"   - {obj['key']} ({obj['size']} bytes)")
        else:
            print("❌ S3 not available - check credentials and bucket access")
    
    asyncio.run(test_s3())