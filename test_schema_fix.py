#!/usr/bin/env python3
"""
Test the fixed schema with a simple status update
"""

import os
import sys

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'database_config'))

from file_upload_processor import FileUploadProcessor
from db_utils import get_database_connection

def test_schema_fix():
    """Test that status updates work correctly with fixed schema"""
    print("🧪 TESTING FIXED SCHEMA")
    print("=" * 40)
    
    db_connection = get_database_connection("postgresql")
    db_connection.connect()
    
    # Get the most recent file to test with
    test_query = """
        SELECT id, file_name, processing_status
        FROM file_upload 
        ORDER BY upload_date DESC 
        LIMIT 1
    """
    
    result = db_connection.query_to_dataframe(test_query)
    
    if result is None or result.empty:
        print("❌ No files found to test with")
        return
    
    file_id = result.iloc[0]['id']
    file_name = result.iloc[0]['file_name']
    current_status = result.iloc[0]['processing_status']
    
    print(f"📄 Testing with: {file_name}")
    print(f"   Current status: {current_status}")
    
    # Test a simple status update
    processor = FileUploadProcessor()
    
    try:
        # Try updating status to same value (should work now)
        success = processor.update_processing_status(file_id, current_status, "Schema test")
        
        if success:
            print("✅ Status update successful - schema is fixed!")
        else:
            print("❌ Status update failed")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    test_schema_fix()