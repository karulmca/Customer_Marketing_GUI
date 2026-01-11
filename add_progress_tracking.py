#!/usr/bin/env python3
"""
Add Progress Tracking Fields to file_upload Table
Adds columns for real-time progress updates visible in the UI
"""

import sys
import os

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
database_config_path = os.path.join(current_dir, 'database_config')
if database_config_path not in sys.path:
    sys.path.insert(0, database_config_path)

from database_config.db_utils import get_database_connection

def add_progress_fields():
    """Add progress tracking fields to file_upload table"""
    
    db_connection = get_database_connection("postgresql")
    if not db_connection:
        print("❌ Failed to connect to database")
        return False
    
    try:
        conn = db_connection.connect()
        cursor = conn.cursor()
        
        print("🔄 Adding progress tracking fields to file_upload table...")
        
        # Add new columns for progress tracking
        alter_queries = [
            """
            ALTER TABLE file_upload 
            ADD COLUMN IF NOT EXISTS total_records INTEGER DEFAULT 0
            """,
            """
            ALTER TABLE file_upload 
            ADD COLUMN IF NOT EXISTS processed_records INTEGER DEFAULT 0
            """,
            """
            ALTER TABLE file_upload 
            ADD COLUMN IF NOT EXISTS progress_percentage DECIMAL(5,2) DEFAULT 0.00
            """,
            """
            ALTER TABLE file_upload 
            ADD COLUMN IF NOT EXISTS current_status_message TEXT DEFAULT ''
            """,
            """
            ALTER TABLE file_upload 
            ADD COLUMN IF NOT EXISTS processing_start_time TIMESTAMP NULL
            """,
            """
            ALTER TABLE file_upload 
            ADD COLUMN IF NOT EXISTS last_progress_update TIMESTAMP NULL
            """,
            """
            ALTER TABLE file_upload 
            ADD COLUMN IF NOT EXISTS success_count INTEGER DEFAULT 0
            """,
            """
            ALTER TABLE file_upload 
            ADD COLUMN IF NOT EXISTS error_count INTEGER DEFAULT 0
            """
        ]
        
        for query in alter_queries:
            try:
                cursor.execute(query)
                conn.commit()
                print(f"✅ Executed: {query.strip()[:60]}...")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"⏭️ Column already exists, skipping...")
                else:
                    print(f"⚠️ Error: {e}")
                conn.rollback()
        
        print("\n✅ Progress tracking fields added successfully!")
        print("\nNew fields:")
        print("  - total_records: Total number of records to process")
        print("  - processed_records: Number of records processed so far")
        print("  - progress_percentage: Current progress (0-100%)")
        print("  - current_status_message: Human-readable status message")
        print("  - processing_start_time: When processing started")
        print("  - last_progress_update: Last time progress was updated")
        print("  - success_count: Successfully processed records")
        print("  - error_count: Records that failed processing")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding progress fields: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Add Progress Tracking Fields to Database")
    print("=" * 60)
    
    success = add_progress_fields()
    
    if success:
        print("\n✅ Database schema updated successfully!")
        print("💡 Now restart your backend to use the new progress tracking")
    else:
        print("\n❌ Failed to update database schema")
        sys.exit(1)
