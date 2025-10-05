"""
Database Flow Diagnostic Script
Checks the status consistency across file_upload, processing_jobs, and company_data tables
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'database_config'))

try:
    from database_config.file_upload_processor import FileUploadProcessor
    from database_config.db_utils import get_database_connection
    from database_config.config_loader import ConfigLoader
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    IMPORTS_SUCCESSFUL = False

def check_recent_uploads():
    """Check recent uploads and their status across all tables"""
    print("🔍 Checking Recent Uploads Status...")
    print("=" * 80)
    
    if not IMPORTS_SUCCESSFUL:
        print("❌ Cannot proceed - imports failed")
        return
    
    try:
        db_connection = get_database_connection("postgresql")
        if not db_connection:
            print("❌ Database connection failed")
            return
        
        db_connection.connect()
        
        # Query to get comprehensive status
        query = """
        SELECT 
            fu.id as file_id,
            fu.file_name,
            fu.processing_status as file_status,
            fu.uploaded_by,
            fu.upload_date,
            fu.records_count as file_records,
            pj.id as job_id,
            pj.job_status,
            pj.job_type,
            pj.started_at,
            pj.completed_at,
            pj.processed_records as job_processed_records,
            COUNT(cd.id) as actual_data_records,
            MIN(cd.processing_status) as min_data_status,
            MAX(cd.processing_status) as max_data_status
        FROM file_upload fu
        LEFT JOIN processing_jobs pj ON fu.id = pj.file_upload_id
        LEFT JOIN company_data cd ON fu.id = cd.file_upload_id
        WHERE fu.upload_date >= CURRENT_DATE - INTERVAL '1 day'
        GROUP BY fu.id, fu.file_name, fu.processing_status, fu.uploaded_by, fu.upload_date, 
                 fu.records_count, pj.id, pj.job_status, pj.job_type, pj.started_at, pj.completed_at, pj.processed_records
        ORDER BY fu.upload_date DESC
        """
        
        result = db_connection.query_to_dataframe(query)
        
        if result is None or result.empty:
            print("ℹ️ No recent uploads found")
            return
        
        print(f"📊 Found {len(result)} recent upload(s):")
        print()
        
        for _, row in result.iterrows():
            print(f"📁 File: {row['file_name']} (ID: {row['file_id']})")
            print(f"   👤 Uploaded by: {row['uploaded_by']}")
            print(f"   📅 Upload date: {row['upload_date']}")
            print(f"   📊 File records: {row['file_records']}")
            print()
            
            # File status
            print(f"   📄 FILE_UPLOAD Status: {row['file_status']}")
            
            # Job status
            if row['job_id']:
                print(f"   🔧 PROCESSING_JOBS:")
                print(f"      Job ID: {row['job_id']}")
                print(f"      Job Status: {row['job_status']}")
                print(f"      Job Type: {row['job_type']}")
                print(f"      Started: {row['started_at']}")
                print(f"      Completed: {row['completed_at']}")
                print(f"      Processed Records: {row['job_processed_records']}")
            else:
                print(f"   🔧 PROCESSING_JOBS: No job found")
            
            # Company data status
            print(f"   🏢 COMPANY_DATA:")
            print(f"      Actual Records: {row['actual_data_records']}")
            if row['actual_data_records'] > 0:
                print(f"      Status Range: {row['min_data_status']} - {row['max_data_status']}")
            else:
                print(f"      Status: No data records found")
            
            # Consistency check
            issues = []
            if row['file_status'] == 'completed' and row['job_status'] != 'completed':
                issues.append("File marked completed but job not completed")
            if row['job_status'] == 'completed' and row['actual_data_records'] == 0:
                issues.append("Job completed but no company data records")
            if row['file_status'] == 'completed' and row['actual_data_records'] == 0:
                issues.append("File completed but no scraped data")
            
            if issues:
                print(f"   ⚠️ ISSUES:")
                for issue in issues:
                    print(f"      - {issue}")
            else:
                print(f"   ✅ Status appears consistent")
            
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error checking uploads: {e}")

def check_pending_jobs():
    """Check what jobs are pending processing"""
    print("\n🕐 Checking Pending Jobs...")
    print("=" * 50)
    
    if not IMPORTS_SUCCESSFUL:
        print("❌ Cannot proceed - imports failed")
        return
    
    try:
        processor = FileUploadProcessor()
        config = ConfigLoader()
        
        print(f"🔒 Single job per user enabled: {config.is_single_job_per_user_enabled()}")
        print(f"⏱️ Scheduler interval: {config.get_scheduler_interval()} minutes")
        print()
        
        # Check all pending uploads
        all_pending = processor.get_pending_uploads()
        if all_pending is not None and not all_pending.empty:
            print(f"📋 All pending uploads: {len(all_pending)}")
            for _, upload in all_pending.iterrows():
                print(f"   - {upload['file_name']} (User: {upload['uploaded_by']}, ID: {upload['id']})")
        else:
            print("📋 No pending uploads found")
        
        # Check queue-based processing
        queue_jobs = processor.get_pending_uploads_by_user_queue()
        if queue_jobs is not None and not queue_jobs.empty:
            print(f"\n🎯 Queue-eligible jobs: {len(queue_jobs)}")
            for _, job in queue_jobs.iterrows():
                print(f"   - {job['file_name']} (User: {job['uploaded_by']}, ID: {job['id']})")
        else:
            print(f"\n🎯 No queue-eligible jobs")
        
        # Check users with active jobs
        users = processor.get_all_users_with_pending_jobs()
        if users:
            print(f"\n👥 Users with pending jobs: {users}")
            for user in users:
                active = processor.get_user_active_jobs(user)
                if active is not None and not active.empty:
                    print(f"   {user}: {len(active)} active job(s)")
                    for _, job in active.iterrows():
                        print(f"      - {job['file_name']} (Status: {job['job_status']})")
                else:
                    print(f"   {user}: No active jobs")
        
    except Exception as e:
        print(f"❌ Error checking pending jobs: {e}")

def check_scheduler_status():
    """Check if scheduler is running"""
    print("\n⚙️ Checking Scheduler Status...")
    print("=" * 40)
    
    try:
        # Check if backend is running by trying to connect
        import requests
        try:
            response = requests.get("http://localhost:8000/api/jobs/scheduler/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ Backend API is running")
                print(f"   Scheduler running: {data.get('running', 'Unknown')}")
                print(f"   Job added: {data.get('job_added', 'Unknown')}")
                print(f"   Last run: {data.get('last_run', 'Never')}")
                print(f"   Last result: {data.get('last_result', 'None')}")
            else:
                print(f"⚠️ Backend API responded with status: {response.status_code}")
        except requests.exceptions.RequestException:
            print("❌ Backend API is not running or not accessible")
            print("   Start it with: python backend_api/main.py")
        
    except Exception as e:
        print(f"❌ Error checking scheduler: {e}")

def suggest_fixes():
    """Suggest fixes based on common issues"""
    print("\n🔧 Suggested Fixes:")
    print("=" * 30)
    print("1. Start Backend API:")
    print("   python backend_api/main.py")
    print()
    print("2. Start Scheduler (if backend not available):")
    print("   python scheduled_processor.py")
    print()
    print("3. Manual processing:")
    print("   python enhanced_scheduled_processor.py --mode single")
    print()
    print("4. Check logs:")
    print("   logs/scheduled_processor.log")
    print("   logs/enhanced_scheduled_processor.log")
    print()
    print("5. Reset stuck jobs:")
    print("   UPDATE processing_jobs SET job_status = 'queued' WHERE job_status = 'processing';")

def main():
    """Run all diagnostics"""
    print("🚀 Database Flow Diagnostic")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    check_recent_uploads()
    check_pending_jobs() 
    check_scheduler_status()
    suggest_fixes()

if __name__ == "__main__":
    main()