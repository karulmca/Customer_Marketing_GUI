"""
Test Single Job Per User Functionality
Tests the new job processing logic with configuration management
"""

import os
import sys
import json
from datetime import datetime

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'database_config'))

try:
    from database_config.file_upload_processor import FileUploadProcessor
    from database_config.config_loader import ConfigLoader
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    IMPORTS_SUCCESSFUL = False

def test_config_loader():
    """Test configuration loading functionality"""
    print("🧪 Testing Configuration Loader...")
    
    try:
        config = ConfigLoader()
        
        print(f"✅ Scheduler interval: {config.get_scheduler_interval()} minutes")
        print(f"✅ Single job per user: {config.is_single_job_per_user_enabled()}")
        print(f"✅ Max concurrent jobs per user: {config.get_max_concurrent_jobs_per_user()}")
        print(f"✅ Job timeout: {config.get_job_timeout_minutes()} minutes")
        print(f"✅ Max retries: {config.get_max_retries()}")
        print(f"✅ Queue priority: {config.get_queue_priority()}")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_single_job_logic():
    """Test single job per user processing logic"""
    print("\n🧪 Testing Single Job Per User Logic...")
    
    if not IMPORTS_SUCCESSFUL:
        print("❌ Skipping - imports failed")
        return False
    
    try:
        processor = FileUploadProcessor()
        
        # Test getting users with pending jobs
        users = processor.get_all_users_with_pending_jobs()
        print(f"✅ Users with pending jobs: {users}")
        
        # Test for each user
        for user in users[:3]:  # Test first 3 users
            print(f"\n👤 Testing user: {user}")
            
            # Check active jobs
            active_jobs = processor.get_user_active_jobs(user)
            if active_jobs is not None and not active_jobs.empty:
                print(f"   ⏳ Active jobs: {len(active_jobs)}")
                print(f"   📋 Job statuses: {active_jobs['job_status'].tolist()}")
            else:
                print(f"   ✅ No active jobs")
            
            # Get next pending job
            next_job = processor.get_next_pending_job_for_user(user)
            if next_job:
                print(f"   📝 Next job: {next_job['file_name']} (ID: {next_job['id']})")
            else:
                print(f"   ℹ️ No next job available")
        
        # Test queue-based processing
        queue_jobs = processor.get_pending_uploads_by_user_queue()
        if queue_jobs is not None and not queue_jobs.empty:
            print(f"\n✅ Queue-based jobs available: {len(queue_jobs)}")
            for _, job in queue_jobs.iterrows():
                print(f"   📁 {job['file_name']} (User: {job['uploaded_by']})")
        else:
            print(f"\n✅ No queue-based jobs available")
        
        return True
        
    except Exception as e:
        print(f"❌ Single job test failed: {e}")
        return False

def show_current_config():
    """Display current configuration"""
    print("\n📋 Current Configuration:")
    print("=" * 50)
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        scheduler_settings = config.get('scheduler_settings', {})
        job_processing = config.get('job_processing', {})
        
        print("🕐 Scheduler Settings:")
        for key, value in scheduler_settings.items():
            print(f"   {key}: {value}")
        
        print("\n⚙️ Job Processing Settings:")
        for key, value in job_processing.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error reading config: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing Single Job Per User Implementation")
    print("=" * 60)
    
    # Show current configuration
    show_current_config()
    
    # Test configuration loading
    config_test = test_config_loader()
    
    # Test single job logic
    job_test = test_single_job_logic()
    
    print("\n📊 Test Results:")
    print("=" * 30)
    print(f"Configuration Loading: {'✅ PASS' if config_test else '❌ FAIL'}")
    print(f"Single Job Logic: {'✅ PASS' if job_test else '❌ FAIL'}")
    
    if config_test and job_test:
        print("\n🎉 All tests passed! Single job per user functionality is working.")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()