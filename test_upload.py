#!/usr/bin/env python3
"""
Test script to verify file upload functionality
"""

import sys
import os

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
database_config_path = os.path.join(current_dir, 'database_config')
if database_config_path not in sys.path:
    sys.path.insert(0, database_config_path)

from database_config.file_upload_processor import FileUploadProcessor

def test_upload():
    """Test file upload functionality"""
    print("🧪 Testing File Upload Functionality...")
    
    # Check if test file exists
    test_file = "test_data/json_test.xlsx"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        print("💡 Run: python -c \"import pandas as pd; pd.DataFrame([{'Company Name': 'Test Corp', 'LinkedIn URL': 'https://linkedin.com/company/test'}]).to_excel('test_data/json_test.xlsx', index=False)\"")
        return
    
    print(f"✅ Test file found: {test_file}")
    
    # Initialize processor
    print("🔄 Initializing file processor...")
    processor = FileUploadProcessor()
    
    # Test database connection
    if not processor.db_connection or not processor.db_connection.test_connection():
        print("❌ Database connection failed")
        return
    
    print("✅ Database connection successful")
    
    # Test upload
    print("🔄 Testing file upload...")
    file_upload_id = processor.upload_file_as_json(test_file, "Test_User")
    
    if file_upload_id:
        print(f"✅ Upload successful! File ID: {file_upload_id}")
        
        # Query uploaded files
        try:
            query = "SELECT id, file_name, upload_date, processing_status, records_count FROM file_upload ORDER BY id DESC LIMIT 5"
            results = processor.db_connection.query_to_dataframe(query)
            
            if results is not None and not results.empty:
                print("\n📋 Recent uploads:")
                print(results.to_string(index=False))
            else:
                print("❌ No upload records found")
                
        except Exception as e:
            print(f"❌ Error querying uploads: {e}")
            
    else:
        print("❌ Upload failed")

if __name__ == "__main__":
    test_upload()