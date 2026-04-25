"""
Complete AVEO-Playwright Workflow

This script runs the complete workflow:
1. Run vendor_automator (login, screenshot, extract data)
2. Upload hasil ke S3
3. Analisis screenshot dengan Bedrock Nova Pro
4. Simpan hasil analisis ke JSON di S3
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# AVEO-Playwright imports
from vendor_automator.vendor_automator import run_all
from bedrock_integration import BedrockIntegrator
from s3_storage import S3StorageManager


async def run_complete_workflow():
    """Run the complete AVEO-Playwright workflow with all integrations."""
    
    print("🚀 AVEO-Playwright Complete Workflow")
    print("=" * 60)
    
    workflow_start_time = time.time()
    session_id = f"workflow-{int(workflow_start_time)}"
    
    workflow_results = {
        'session_id': session_id,
        'start_time': datetime.now().isoformat(),
        'steps': {}
    }
    
    try:
        # Step 1: Run vendor_automator (login, screenshot, extract data)
        print("\n🤖 Step 1: Running AVEO-Playwright Automation...")
        print("-" * 40)
        
        step1_start = time.time()
        automation_result = await run_all(headless=True, upload_to_s3=True)
        step1_duration = time.time() - step1_start
        
        print(f"✅ Automation completed in {step1_duration:.2f} seconds")
        print(f"📸 Screenshot: {automation_result['screenshot_info']['local_path']}")
        print(f"📊 Transactions: {len(automation_result['transactions'])} extracted")
        
        # Check S3 upload status
        s3_summary = automation_result.get('s3_summary', {})
        print(f"📤 S3 Uploads: {s3_summary.get('successful_uploads', 0)}/{s3_summary.get('total_uploads', 0)}")
        
        workflow_results['steps']['automation'] = {
            'status': 'success',
            'duration': step1_duration,
            'screenshot_path': automation_result['screenshot_info']['local_path'],
            'transactions_count': len(automation_result['transactions']),
            's3_uploads': s3_summary
        }
        
        # Get S3 URLs if available
        screenshot_s3_url = None
        transactions_s3_url = None
        
        if 's3_upload' in automation_result['screenshot_info']:
            screenshot_upload = automation_result['screenshot_info']['s3_upload']
            if screenshot_upload['status'] == 'success':
                screenshot_s3_url = screenshot_upload['s3_url']
                print(f"✅ Screenshot uploaded to S3: {screenshot_s3_url}")
        
        if 's3_upload' in automation_result['transaction_info']:
            transactions_upload = automation_result['transaction_info']['s3_upload']
            if transactions_upload['status'] == 'success':
                transactions_s3_url = transactions_upload['s3_url']
                print(f"✅ Transaction data uploaded to S3: {transactions_s3_url}")
        
        # Step 2: Already done (S3 upload integrated in step 1)
        print(f"\n✅ Step 2: S3 Upload completed automatically")
        
        # Step 3: Analisis screenshot dengan Bedrock Nova Pro
        print(f"\n🧠 Step 3: Analyzing with Bedrock Nova Pro...")
        print("-" * 40)
        
        step3_start = time.time()
        
        # Initialize Bedrock integrator
        bedrock = BedrockIntegrator()
        
        # Run Nova Pro analysis
        analysis_result = await bedrock.analyze_with_nova_pro(
            automation_result['screenshot_info']['local_path'],
            automation_result['transactions']
        )
        
        step3_duration = time.time() - step3_start
        
        if analysis_result['status'] == 'success':
            print(f"✅ Bedrock analysis completed in {step3_duration:.2f} seconds")
            print(f"🤖 Model: {analysis_result['model']}")
            
            # Show analysis preview
            analysis_text = analysis_result['analysis']
            preview = analysis_text[:300] + "..." if len(analysis_text) > 300 else analysis_text
            print(f"📝 Analysis Preview: {preview}")
            
            # Show token usage if available
            if 'usage' in analysis_result:
                usage = analysis_result['usage']
                print(f"📊 Token Usage: Input={usage.get('inputTokens', 'N/A')}, Output={usage.get('outputTokens', 'N/A')}")
        else:
            print(f"❌ Bedrock analysis failed: {analysis_result.get('error', 'Unknown error')}")
        
        workflow_results['steps']['bedrock_analysis'] = {
            'status': analysis_result['status'],
            'duration': step3_duration,
            'model': analysis_result.get('model', 'N/A'),
            'analysis_length': len(analysis_result.get('analysis', '')),
            'usage': analysis_result.get('usage', {})
        }
        
        # Step 4: Simpan hasil analisis ke JSON di S3
        print(f"\n💾 Step 4: Saving Analysis Results to S3...")
        print("-" * 40)
        
        step4_start = time.time()
        
        # Prepare comprehensive results
        comprehensive_results = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'automation_results': {
                'screenshot_info': automation_result['screenshot_info'],
                'transaction_info': automation_result['transaction_info'],
                'transactions': automation_result['transactions'],
                's3_summary': automation_result.get('s3_summary', {})
            },
            'bedrock_analysis': analysis_result,
            'workflow_metadata': {
                'total_duration': time.time() - workflow_start_time,
                'steps_completed': 4,
                'success': analysis_result['status'] == 'success'
            }
        }
        
        # Save to local JSON file first
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        analysis_filename = f"complete_workflow_results_{timestamp}.json"
        local_analysis_path = f"output/data/{analysis_filename}"
        
        # Ensure directory exists
        Path(local_analysis_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write comprehensive results to JSON
        with open(local_analysis_path, 'w') as f:
            json.dump(comprehensive_results, f, indent=2, default=str)
        
        print(f"✅ Results saved locally: {local_analysis_path}")
        
        # Upload analysis results to S3
        s3_manager = S3StorageManager()
        
        if s3_manager.s3_available:
            s3_upload_result = await s3_manager.upload_json_data(
                local_analysis_path, 
                session_id
            )
            
            if s3_upload_result['status'] == 'success':
                analysis_s3_url = s3_upload_result['s3_url']
                print(f"✅ Analysis results uploaded to S3: {analysis_s3_url}")
                
                workflow_results['steps']['save_analysis'] = {
                    'status': 'success',
                    'duration': time.time() - step4_start,
                    'local_path': local_analysis_path,
                    's3_url': analysis_s3_url,
                    'file_size': Path(local_analysis_path).stat().st_size
                }
            else:
                print(f"⚠️ S3 upload failed: {s3_upload_result.get('error', 'Unknown error')}")
                workflow_results['steps']['save_analysis'] = {
                    'status': 'partial',
                    'duration': time.time() - step4_start,
                    'local_path': local_analysis_path,
                    's3_error': s3_upload_result.get('error', 'Unknown error')
                }
        else:
            print("⚠️ S3 not available - results saved locally only")
            workflow_results['steps']['save_analysis'] = {
                'status': 'local_only',
                'duration': time.time() - step4_start,
                'local_path': local_analysis_path
            }
        
        # Final Summary
        total_duration = time.time() - workflow_start_time
        workflow_results['end_time'] = datetime.now().isoformat()
        workflow_results['total_duration'] = total_duration
        workflow_results['overall_status'] = 'success' if analysis_result['status'] == 'success' else 'partial'
        
        print(f"\n" + "=" * 60)
        print("COMPLETE WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"🆔 Session ID: {session_id}")
        print(f"⏱️  Total Duration: {total_duration:.2f} seconds")
        print(f"📊 Overall Status: {workflow_results['overall_status'].upper()}")
        
        print(f"\n📋 Steps Completed:")
        for step_name, step_data in workflow_results['steps'].items():
            status_emoji = "✅" if step_data['status'] == 'success' else "⚠️" if step_data['status'] == 'partial' else "❌"
            duration = step_data.get('duration', 0)
            print(f"   {status_emoji} {step_name.replace('_', ' ').title()}: {step_data['status']} ({duration:.2f}s)")
        
        print(f"\n📁 Files Generated:")
        print(f"   📸 Screenshot: {automation_result['screenshot_info']['local_path']}")
        print(f"   📊 Transaction Data: {automation_result['transaction_info']['local_path']}")
        print(f"   🧠 Analysis Results: {local_analysis_path}")
        
        if s3_manager.s3_available:
            print(f"\n☁️  S3 Storage:")
            if screenshot_s3_url:
                print(f"   📸 Screenshot: {screenshot_s3_url}")
            if transactions_s3_url:
                print(f"   📊 Transactions: {transactions_s3_url}")
            if 'save_analysis' in workflow_results['steps'] and 's3_url' in workflow_results['steps']['save_analysis']:
                print(f"   🧠 Analysis: {workflow_results['steps']['save_analysis']['s3_url']}")
        
        print(f"\n🎯 Key Insights from Bedrock Analysis:")
        if analysis_result['status'] == 'success':
            # Extract key insights from analysis
            analysis_text = analysis_result['analysis']
            lines = analysis_text.split('\n')
            key_lines = [line.strip() for line in lines if line.strip() and (
                'recommendation' in line.lower() or 
                'insight' in line.lower() or 
                'analysis' in line.lower() or
                'quality' in line.lower()
            )][:3]  # Show first 3 key insights
            
            for i, insight in enumerate(key_lines, 1):
                print(f"   {i}. {insight}")
        else:
            print("   ❌ Analysis failed - check Bedrock configuration")
        
        print(f"\n🚀 Workflow completed successfully!")
        
        return workflow_results
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {str(e)}")
        
        workflow_results['end_time'] = datetime.now().isoformat()
        workflow_results['total_duration'] = time.time() - workflow_start_time
        workflow_results['overall_status'] = 'failed'
        workflow_results['error'] = str(e)
        
        return workflow_results


if __name__ == "__main__":
    asyncio.run(run_complete_workflow())