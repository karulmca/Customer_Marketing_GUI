#!/usr/bin/env python3
"""
Complete End-to-End Test Script
Tests the entire workflow from file upload to processing completion
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
database_config_path = os.path.join(current_dir, 'database_config')
if database_config_path not in sys.path:
    sys.path.insert(0, database_config_path)

def test_end_to_end_workflow():
    """Complete end-to-end workflow test"""
    print("🚀 Starting Complete End-to-End Workflow Test")
    print("=" * 60)
    
    try:
        # Step 1: Test Database Connection
        print("\n📋 Step 1: Testing Database Connection")
        from db_utils import get_database_connection, check_database_requirements
        from file_upload_processor import FileUploadProcessor
        from enhanced_scheduled_processor import EnhancedScheduledProcessor
        
        db_connection = get_database_connection()
        if not db_connection:
            print("❌ Database connection failed!")
            return False
        print("✅ Database connection successful")
        
        # Step 2: Upload Test File
        print("\n📋 Step 2: Uploading Test File")
        test_file_path = "test_data/end_to_end_test.csv"
        
        if not os.path.exists(test_file_path):
            print(f"❌ Test file not found: {test_file_path}")
            return False
            
        processor = FileUploadProcessor()
        upload_result = processor.upload_file_as_json(
            file_path=test_file_path,
            uploaded_by="end_to_end_test"
        )
        
        if not upload_result:
            print("❌ File upload failed!")
            return False
            
        print(f"✅ File uploaded successfully with ID: {upload_result}")
        file_upload_id = upload_result
        
        # Step 3: Check Upload Status
        print("\n📋 Step 3: Verifying File Upload Status")
        upload_data = processor.get_upload_data(file_upload_id)
        if not upload_data:
            print("❌ Could not retrieve uploaded file data!")
            return False
            
        print(f"✅ File found in database: {upload_data['file_name']}")
        print(f"   Available keys: {list(upload_data.keys())}")
        print(f"   Records: {len(upload_data['raw_data'])}")
        
        # Step 4: Process the File
        print("\n📋 Step 4: Processing File with LinkedIn Scraper")
        enhanced_processor = EnhancedScheduledProcessor()
        
        # Show initial statistics
        print("\n📊 Initial Statistics:")
        enhanced_processor.get_processing_statistics()
        
        # Process the file
        processed_count = enhanced_processor.process_pending_files("complete")
        
        if processed_count == 0:
            print("❌ No files were processed!")
            return False
            
        print(f"✅ Successfully processed {processed_count} file(s)")
        
        # Step 5: Verify Final Results
        print("\n📋 Step 5: Verifying Final Results")
        
        # Check final statistics
        print("\n📊 Final Statistics:")
        enhanced_processor.get_processing_statistics()
        
        # Check company data was created
        company_data_query = """
        SELECT 
            company_name, 
            company_size, 
            industry, 
            revenue,
            file_upload_id
        FROM company_data 
        WHERE file_upload_id = %s
        """
        
        # Use direct database query for verification
        import psycopg2
        conn = psycopg2.connect('postgresql://postgres:Neha2713@localhost:5432/FileUpload')
        company_df = pd.read_sql(company_data_query, conn, params=[file_upload_id])
        conn.close()
        
        if company_df.empty:
            print("❌ No company data found in database!")
            return False
            
        print(f"✅ Found {len(company_df)} companies in database")
        print("📊 Company Data Sample:")
        print(company_df[['company_name', 'company_size', 'industry', 'revenue']].to_string(index=False))
        
        # Step 6: Final Validation
        print("\n📋 Step 6: Final Validation")
        
        # Check file status was updated
        file_status_query = "SELECT processing_status, processed_date FROM file_upload WHERE id = %s"
        conn = psycopg2.connect('postgresql://postgres:Neha2713@localhost:5432/FileUpload')
        status_df = pd.read_sql(file_status_query, conn, params=[file_upload_id])
        conn.close()
        
        if not status_df.empty:
            final_status = status_df.iloc[0]['processing_status']
            processed_date = status_df.iloc[0]['processed_date']
            print(f"✅ File status: {final_status}")
            print(f"✅ Processed date: {processed_date}")
        else:
            print("❌ Could not verify file status!")
            return False
            
        print("\n🎉 END-TO-END TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ All components working correctly:")
        print("   • File upload system")
        print("   • JSON storage and retrieval")
        print("   • LinkedIn scraper integration")
        print("   • Database storage with traceability")
        print("   • Status tracking and updates")
        
        return True
        
    except Exception as e:
        print(f"\n❌ End-to-end test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_end_to_end_workflow()
    sys.exit(0 if success else 1)