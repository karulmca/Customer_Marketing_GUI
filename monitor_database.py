#!/usr/bin/env python3
"""
Test the database saving functionality after processing
"""

from database_config.postgresql_config import PostgreSQLConfig
import psycopg2
import time

def monitor_database_changes():
    """Monitor database for new company data entries"""
    try:
        db_config = PostgreSQLConfig()
        connection = psycopg2.connect(**db_config.get_connection_params())
        cursor = connection.cursor()
        
        # Get initial counts
        cursor.execute("SELECT COUNT(*) FROM company_data")
        initial_company_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM processing_jobs")
        initial_jobs_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM file_upload WHERE processing_status = 'completed'")
        initial_completed_files = cursor.fetchone()[0]
        
        print(f"Initial state:")
        print(f"  - company_data records: {initial_company_count}")
        print(f"  - processing_jobs records: {initial_jobs_count}")
        print(f"  - completed file uploads: {initial_completed_files}")
        print()
        print("Monitoring for changes... (checking every 5 seconds)")
        print("Press Ctrl+C to stop")
        
        while True:
            time.sleep(5)
            
            # Check for changes
            cursor.execute("SELECT COUNT(*) FROM company_data")
            current_company_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM processing_jobs")
            current_jobs_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM file_upload WHERE processing_status = 'completed'")
            current_completed_files = cursor.fetchone()[0]
            
            # Report changes
            if (current_company_count != initial_company_count or 
                current_jobs_count != initial_jobs_count or
                current_completed_files != initial_completed_files):
                
                print(f"CHANGES DETECTED at {time.strftime('%H:%M:%S')}:")
                
                if current_company_count != initial_company_count:
                    change = current_company_count - initial_company_count
                    print(f"  + company_data: {initial_company_count} -> {current_company_count} (+{change})")
                    
                    # Show recent company data
                    cursor.execute("""
                        SELECT company_name, linkedin_url, company_website, created_by, updated_at
                        FROM company_data 
                        ORDER BY updated_at DESC 
                        LIMIT 3
                    """)
                    recent_companies = cursor.fetchall()
                    print(f"    Recent companies:")
                    for company_name, linkedin, website, created_by, updated in recent_companies:
                        print(f"      - {company_name} | {website} | by {created_by} at {updated}")
                
                if current_jobs_count != initial_jobs_count:
                    change = current_jobs_count - initial_jobs_count
                    print(f"  + processing_jobs: {initial_jobs_count} -> {current_jobs_count} (+{change})")
                
                if current_completed_files != initial_completed_files:
                    change = current_completed_files - initial_completed_files
                    print(f"  + completed files: {initial_completed_files} -> {current_completed_files} (+{change})")
                
                print()
                
                # Update baseline
                initial_company_count = current_company_count
                initial_jobs_count = current_jobs_count
                initial_completed_files = current_completed_files
        
        cursor.close()
        connection.close()
        
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_database_changes()