"""
Database Schema Update for Single Job Per User Implementation
Adds missing columns to processing_jobs table
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'database_config'))

from database_config.db_utils import get_database_connection

def update_processing_jobs_schema():
    """Add missing columns to processing_jobs table"""
    print("🔧 Updating processing_jobs table schema...")
    
    try:
        db = get_database_connection("postgresql")
        if not db:
            print("❌ Failed to connect to database")
            return False
        
        db.connect()
        
        # Check which columns are missing
        existing_columns_query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'processing_jobs'
        """
        existing_columns_df = db.query_to_dataframe(existing_columns_query)
        existing_columns = existing_columns_df['column_name'].tolist() if existing_columns_df is not None else []
        
        print(f"📋 Existing columns: {existing_columns}")
        
        # Define required columns and their types
        required_columns = {
            'uploaded_by': 'VARCHAR(255)',
            'updated_at': 'TIMESTAMP DEFAULT NOW()',
            'processed_records': 'INTEGER DEFAULT 0'
        }
        
        # Add missing columns
        columns_added = []
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                alter_query = f"ALTER TABLE processing_jobs ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                success = db.execute_query(alter_query)
                if success:
                    print(f"✅ Added column: {column_name}")
                    columns_added.append(column_name)
                else:
                    print(f"❌ Failed to add column: {column_name}")
            else:
                print(f"ℹ️ Column already exists: {column_name}")
        
        # Update existing records to have default values
        if columns_added:
            print("🔄 Updating existing records with default values...")
            
            update_queries = []
            if 'uploaded_by' in columns_added:
                update_queries.append("UPDATE processing_jobs SET uploaded_by = 'legacy_user' WHERE uploaded_by IS NULL")
            
            if 'updated_at' in columns_added:
                update_queries.append("UPDATE processing_jobs SET updated_at = created_at WHERE updated_at IS NULL")
            
            if 'processed_records' in columns_added:
                update_queries.append("UPDATE processing_jobs SET processed_records = processed_items WHERE processed_records IS NULL")
            
            for query in update_queries:
                success = db.execute_query(query)
                if success:
                    print(f"✅ Updated existing records: {query[:50]}...")
                else:
                    print(f"❌ Failed to update records: {query[:50]}...")
        
        print("🎉 Schema update completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False

def verify_schema_update():
    """Verify that all required columns are now present"""
    print("\n🔍 Verifying schema update...")
    
    try:
        db = get_database_connection("postgresql")
        db.connect()
        
        # Get updated column list
        columns_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'processing_jobs'
            ORDER BY ordinal_position
        """
        columns_df = db.query_to_dataframe(columns_query)
        
        if columns_df is not None:
            print("📋 Updated processing_jobs table structure:")
            for _, row in columns_df.iterrows():
                print(f"   {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']})")
            
            # Check for required columns
            required_columns = ['uploaded_by', 'updated_at', 'processed_records']
            existing_columns = columns_df['column_name'].tolist()
            
            missing_columns = [col for col in required_columns if col not in existing_columns]
            if missing_columns:
                print(f"❌ Still missing columns: {missing_columns}")
                return False
            else:
                print("✅ All required columns are present!")
                return True
        else:
            print("❌ Failed to retrieve column information")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying schema: {e}")
        return False

def main():
    """Main function to update database schema"""
    print("🚀 Database Schema Update for Single Job Per User")
    print("=" * 60)
    
    # Update schema
    update_success = update_processing_jobs_schema()
    
    if update_success:
        # Verify update
        verify_success = verify_schema_update()
        
        if verify_success:
            print("\n🎉 Database schema update completed successfully!")
            print("The system now supports single job per user functionality.")
        else:
            print("\n⚠️ Schema update completed but verification failed.")
    else:
        print("\n❌ Schema update failed. Please check the errors above.")

if __name__ == "__main__":
    main()