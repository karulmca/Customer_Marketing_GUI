#!/usr/bin/env python3
"""
Fix file_upload table schema - add missing updated_at column
"""

import os
import sys

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'database_config'))

from db_utils import get_database_connection

def fix_file_upload_schema():
    """Add missing updated_at column to file_upload table"""
    print("🔧 FIXING FILE_UPLOAD TABLE SCHEMA")
    print("=" * 50)
    
    db_connection = get_database_connection("postgresql")
    db_connection.connect()
    
    print("\n🔍 Checking current file_upload table structure...")
    
    # Check if updated_at column exists
    check_column_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'file_upload' 
        AND column_name = 'updated_at'
    """
    
    existing_column = db_connection.query_to_dataframe(check_column_query)
    
    if existing_column is not None and not existing_column.empty:
        print("✅ updated_at column already exists")
        return
    
    print("❌ updated_at column missing - adding it now...")
    
    # Add the missing column
    add_column_query = """
        ALTER TABLE file_upload 
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """
    
    try:
        success = db_connection.execute_query(add_column_query)
        
        if success:
            print("✅ Successfully added updated_at column to file_upload table")
            
            # Update existing records to have updated_at = upload_date
            update_existing_query = """
                UPDATE file_upload 
                SET updated_at = upload_date 
                WHERE updated_at IS NULL
            """
            
            update_success = db_connection.execute_query(update_existing_query)
            
            if update_success:
                print("✅ Updated existing records with initial updated_at values")
            else:
                print("⚠️ Warning: Could not update existing records")
            
        else:
            print("❌ Failed to add updated_at column")
            
    except Exception as e:
        print(f"❌ Error adding column: {e}")
    
    print("\n🔍 Verifying schema fix...")
    
    # Verify the column was added
    verify_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'file_upload' 
        AND column_name = 'updated_at'
    """
    
    verification = db_connection.query_to_dataframe(verify_query)
    
    if verification is not None and not verification.empty:
        col_info = verification.iloc[0]
        print(f"✅ Column verified: {col_info['column_name']} ({col_info['data_type']})")
        print(f"   Nullable: {col_info['is_nullable']} | Default: {col_info['column_default']}")
    else:
        print("❌ Column verification failed")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    fix_file_upload_schema()