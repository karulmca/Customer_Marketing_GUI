"""
Check for Status Inconsistencies
Look for files where statuses don't match expected patterns
"""

import os
import sys

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'database_config'))

from database_config.db_utils import get_database_connection

def check_inconsistent_statuses():
    """Find files with inconsistent statuses"""
    print("🔍 Checking for Status Inconsistencies...")
    
    try:
        db_connection = get_database_connection("postgresql")
        db_connection.connect()
        
        # Check for files marked completed but no company data
        query1 = """
        SELECT 
            fu.id, fu.file_name, fu.processing_status, fu.uploaded_by,
            pj.job_status, pj.processed_records,
            COUNT(cd.id) as actual_records
        FROM file_upload fu
        LEFT JOIN processing_jobs pj ON fu.id = pj.file_upload_id
        LEFT JOIN company_data cd ON fu.id = cd.file_upload_id
        WHERE fu.processing_status = 'completed'
        GROUP BY fu.id, fu.file_name, fu.processing_status, fu.uploaded_by, pj.job_status, pj.processed_records
        HAVING COUNT(cd.id) = 0
        ORDER BY fu.upload_date DESC
        """
        
        result1 = db_connection.query_to_dataframe(query1)
        
        if result1 is not None and not result1.empty:
            print(f"❌ Found {len(result1)} files marked completed but no company data:")
            for _, row in result1.iterrows():
                print(f"   - {row['file_name']} (ID: {row['id']}, User: {row['uploaded_by']})")
                print(f"     File Status: {row['processing_status']}, Job Status: {row['job_status']}")
        else:
            print("✅ No files found with completed status but missing data")
        
        # Check for processing jobs marked completed but file not completed
        query2 = """
        SELECT 
            fu.id, fu.file_name, fu.processing_status as file_status,
            pj.job_status, pj.processed_records
        FROM file_upload fu
        JOIN processing_jobs pj ON fu.id = pj.file_upload_id
        WHERE pj.job_status = 'completed' AND fu.processing_status != 'completed'
        ORDER BY fu.upload_date DESC
        """
        
        result2 = db_connection.query_to_dataframe(query2)
        
        if result2 is not None and not result2.empty:
            print(f"\n❌ Found {len(result2)} jobs completed but file not marked completed:")
            for _, row in result2.iterrows():
                print(f"   - {row['file_name']} (ID: {row['id']})")
                print(f"     File Status: {row['file_status']}, Job Status: {row['job_status']}")
        else:
            print("\n✅ No jobs found completed with file not completed")
        
        # Check for pending processing jobs
        query3 = """
        SELECT 
            fu.id, fu.file_name, fu.processing_status as file_status, fu.uploaded_by,
            pj.job_status, pj.started_at, pj.completed_at
        FROM file_upload fu
        JOIN processing_jobs pj ON fu.id = pj.file_upload_id
        WHERE pj.job_status IN ('pending', 'queued', 'processing')
        ORDER BY fu.upload_date DESC
        """
        
        result3 = db_connection.query_to_dataframe(query3)
        
        if result3 is not None and not result3.empty:
            print(f"\n🕐 Found {len(result3)} jobs in pending/processing state:")
            for _, row in result3.iterrows():
                print(f"   - {row['file_name']} (ID: {row['id']}, User: {row['uploaded_by']})")
                print(f"     File Status: {row['file_status']}, Job Status: {row['job_status']}")
                print(f"     Started: {row['started_at']}, Completed: {row['completed_at']}")
        else:
            print("\n✅ No pending/processing jobs found")
        
        # Check the actual LinkedIn scraping - look for records without scraped data
        query4 = """
        SELECT 
            fu.id, fu.file_name, fu.processing_status,
            COUNT(cd.id) as total_records,
            COUNT(CASE WHEN cd.company_size IS NOT NULL AND cd.company_size != '' THEN 1 END) as scraped_records
        FROM file_upload fu
        LEFT JOIN company_data cd ON fu.id = cd.file_upload_id
        WHERE fu.processing_status = 'completed'
        GROUP BY fu.id, fu.file_name, fu.processing_status
        HAVING COUNT(cd.id) > 0
        ORDER BY fu.upload_date DESC
        """
        
        result4 = db_connection.query_to_dataframe(query4)
        
        if result4 is not None and not result4.empty:
            print(f"\n🔍 Scraping Results for Completed Files:")
            for _, row in result4.iterrows():
                scrape_percentage = (row['scraped_records'] / row['total_records']) * 100 if row['total_records'] > 0 else 0
                print(f"   - {row['file_name']} (ID: {row['id']})")
                print(f"     Total Records: {row['total_records']}, Scraped: {row['scraped_records']} ({scrape_percentage:.1f}%)")
                if scrape_percentage < 50:
                    print(f"     ⚠️ Low scraping success rate!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_inconsistent_statuses()