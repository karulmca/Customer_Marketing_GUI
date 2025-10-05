"""
Add missing columns for database synchronization
"""
import sys
import os

# Add database_config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'database_config'))

from db_utils import get_database_connection

def add_missing_columns():
    """Add missing columns for proper database synchronization"""
    
    db = get_database_connection()
    if not db:
        print("❌ Failed to get database connection")
        return
        
    # Connect to database
    if not db.connect():
        print("❌ Failed to connect to database")
        return
    
    # SQL commands to add missing columns
    alter_commands = [
        # Add processed_records to file_upload table
        """
        ALTER TABLE file_upload 
        ADD COLUMN IF NOT EXISTS processed_records INTEGER DEFAULT 0;
        """,
        
        # Add completed_date to processing_jobs table (though completed_at exists, sync method uses completed_date)
        """
        ALTER TABLE processing_jobs 
        ADD COLUMN IF NOT EXISTS completed_date TIMESTAMP DEFAULT NULL;
        """,
        
        # Add processed_date to company_data table
        """
        ALTER TABLE company_data 
        ADD COLUMN IF NOT EXISTS processed_date TIMESTAMP DEFAULT NULL;
        """
    ]
    
    print("🔧 Adding missing columns for database synchronization...")
    
    for i, command in enumerate(alter_commands, 1):
        try:
            success = db.execute_query(command.strip())
            if success:
                print(f"✅ Column addition {i}/3 completed successfully")
            else:
                print(f"❌ Column addition {i}/3 failed")
        except Exception as e:
            print(f"❌ Error adding column {i}: {e}")
    
    print("\n🔍 Verifying new columns...")
    
    # Verify the columns were added
    verification_queries = [
        ("file_upload", "SELECT column_name FROM information_schema.columns WHERE table_name = 'file_upload' AND column_name = 'processed_records'"),
        ("processing_jobs", "SELECT column_name FROM information_schema.columns WHERE table_name = 'processing_jobs' AND column_name = 'completed_date'"),
        ("company_data", "SELECT column_name FROM information_schema.columns WHERE table_name = 'company_data' AND column_name = 'processed_date'")
    ]
    
    for table_name, query in verification_queries:
        try:
            result = db.query_to_dataframe(query)
            if result is not None and not result.empty:
                print(f"✅ {table_name}: Column added successfully")
            else:
                print(f"❌ {table_name}: Column not found")
        except Exception as e:
            print(f"❌ Error verifying {table_name}: {e}")
    
    print("\n🎉 Database schema update completed!")

if __name__ == "__main__":
    add_missing_columns()