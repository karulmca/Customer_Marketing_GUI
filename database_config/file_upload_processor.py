"""
File Upload Processing Utilities
Handles JSON storage of uploaded files and scheduled processing
"""

import os
import sys
import json
import hashlib
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from db_utils import get_database_connection

class FileUploadProcessor:
    """Handles file upload processing and JSON storage"""
    
    def __init__(self):
        self.db_connection = get_database_connection("postgresql")
        # Ensure connection is established
        if self.db_connection:
            self.db_connection.connect()
        
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file content"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"Error calculating file hash: {e}")
            return ""
    
    def upload_file_as_json(self, file_path: str, uploaded_by: str = "GUI_User") -> Optional[int]:
        """
        Upload file content as JSON to file_upload table
        Returns file_upload_id if successful, None if failed
        """
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return None
                
            # Read file into DataFrame
            if file_path.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            elif file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                print(f"Unsupported file format: {file_path}")
                return None
            
            # Convert DataFrame to JSON
            # Handle NaN values by converting to None/null for proper JSON
            df_clean = df.fillna('')  # Replace NaN with empty string
            
            # Convert to records and ensure proper JSON serialization
            data_records = []
            for _, row in df_clean.iterrows():
                record = {}
                for col in df_clean.columns:
                    value = row[col]
                    # Convert various null-like values to proper null
                    if pd.isna(value) or value == 'nan' or value == 'NaN' or str(value).strip() == '':
                        record[col] = None
                    else:
                        record[col] = str(value) if not isinstance(value, (int, float, bool)) else value
                data_records.append(record)
            
            raw_data = {
                "columns": list(df.columns),
                "data": data_records,
                "metadata": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "upload_timestamp": datetime.now().isoformat(),
                    "file_extension": os.path.splitext(file_path)[1].lower()
                }
            }
            
            # Calculate file hash
            file_hash = self.calculate_file_hash(file_path)
            
            # Check if file already exists
            existing_file = self.check_duplicate_file(file_hash)
            if existing_file:
                print(f"File already uploaded with ID: {existing_file}")
                return existing_file
            
            # Get file info
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Insert into database - Check and reconnect if needed
            if not self.db_connection or not self.db_connection.test_connection():
                print("❌ Database not connected - attempting to reconnect...")
                self.db_connection = get_database_connection("postgresql")
                
                if self.db_connection:
                    self.db_connection.connect()  # Initialize the connection
                
                if not self.db_connection or not self.db_connection.test_connection():
                    print("❌ Failed to reconnect to database")
                    return None
                else:
                    print("✅ Database reconnected successfully")
                
            # Create DataFrame for insertion
            upload_data = pd.DataFrame([{
                'file_name': file_name,
                'file_path': file_path,
                'file_size': file_size,
                'original_columns': list(df.columns),
                'raw_data': json.dumps(raw_data),
                'uploaded_by': uploaded_by,
                'processing_status': 'pending',
                'records_count': len(df),
                'file_hash': file_hash
            }])
            
            # Insert and get the ID
            print(f"🔄 Attempting to insert file data into database...")
            success = self.db_connection.insert_dataframe(upload_data, "file_upload")
            
            if success:
                print("✅ Database insertion successful")
                # Get the inserted record ID
                file_upload_id = self.get_latest_upload_id(file_hash)
                
                # Create processing job
                if file_upload_id:
                    self.create_processing_job(file_upload_id, "data_extraction")
                    print(f"✅ Processing job created for file ID: {file_upload_id}")
                    
                print(f"✅ File uploaded successfully with ID: {file_upload_id}")
                return file_upload_id
            else:
                print("❌ Failed to upload file to database - insertion failed")
                return None
                
        except Exception as e:
            print(f"❌ Error uploading file: {str(e)}")
            return None
    
    def check_duplicate_file(self, file_hash: str) -> Optional[int]:
        """Check if file with same hash already exists"""
        try:
            if not self.db_connection:
                return None
                
            query = f"SELECT id FROM file_upload WHERE file_hash = '{file_hash}' LIMIT 1"
            result = self.db_connection.query_to_dataframe(query)
            
            if result is not None and not result.empty:
                return int(result.iloc[0]['id'])
            return None
            
        except Exception as e:
            print(f"Error checking duplicate file: {e}")
            return None
    
    def get_latest_upload_id(self, file_hash: str) -> Optional[int]:
        """Get the ID of the latest uploaded file"""
        try:
            if not self.db_connection:
                return None
                
            query = f"""
                SELECT id FROM file_upload 
                WHERE file_hash = '{file_hash}' 
                ORDER BY upload_date DESC 
                LIMIT 1
            """
            result = self.db_connection.query_to_dataframe(query)
            
            if result is not None and not result.empty:
                return int(result.iloc[0]['id'])
            return None
            
        except Exception as e:
            print(f"Error getting latest upload ID: {e}")
            return None
    
    def create_processing_job(self, file_upload_id: int, job_type: str = "data_extraction") -> bool:
        """Create a processing job for the uploaded file"""
        try:
            if not self.db_connection:
                return False
                
            job_data = pd.DataFrame([{
                'job_type': job_type,
                'file_upload_id': file_upload_id,
                'job_status': 'queued',
                'job_config': json.dumps({
                    'auto_column_mapping': True,
                    'data_validation': True,
                    'duplicate_detection': True
                }),
                'retry_count': 0,
                'max_retries': 3
            }])
            
            success = self.db_connection.insert_dataframe(job_data, "processing_jobs")
            if success:
                print(f"✅ Processing job created for file_upload_id: {file_upload_id}")
            return success
            
        except Exception as e:
            print(f"Error creating processing job: {e}")
            return False
    
    def get_pending_uploads(self) -> Optional[pd.DataFrame]:
        """Get all pending file uploads"""
        try:
            if not self.db_connection:
                return None
                
            query = """
                SELECT id, file_name, upload_date, records_count, uploaded_by
                FROM file_upload 
                WHERE processing_status = 'pending'
                ORDER BY upload_date ASC
            """
            return self.db_connection.query_to_dataframe(query)
            
        except Exception as e:
            print(f"Error getting pending uploads: {e}")
            return None
    
    def get_upload_data(self, file_upload_id: int) -> Optional[Dict[str, Any]]:
        """Get raw JSON data from a file upload"""
        try:
            if not self.db_connection:
                return None
                
            query = f"""
                SELECT raw_data, original_columns, file_name
                FROM file_upload 
                WHERE id = {file_upload_id}
            """
            result = self.db_connection.query_to_dataframe(query)
            
            if result is not None and not result.empty:
                raw_data_str = result.iloc[0]['raw_data']
                raw_data = json.loads(raw_data_str) if isinstance(raw_data_str, str) else raw_data_str
                
                return {
                    'raw_data': raw_data,
                    'original_columns': result.iloc[0]['original_columns'],
                    'file_name': result.iloc[0]['file_name']
                }
            return None
            
        except Exception as e:
            print(f"Error getting upload data: {e}")
            return None
    
    def process_uploaded_file(self, file_upload_id: int) -> bool:
        """Process an uploaded file and move data to company_data table"""
        try:
            # Get upload data
            upload_info = self.get_upload_data(file_upload_id)
            if not upload_info:
                print(f"No data found for file_upload_id: {file_upload_id}")
                return False
            
            raw_data = upload_info['raw_data']
            file_name = upload_info['file_name']
            
            # Convert JSON data back to DataFrame
            df = pd.DataFrame(raw_data['data'])
            
            # Apply column mapping
            mapped_df = self.apply_column_mapping(df)
            
            # Add metadata
            mapped_df['file_source'] = file_name
            mapped_df['file_upload_id'] = file_upload_id
            mapped_df['created_by'] = 'scheduled_processor'
            
            # Insert into company_data table
            success = self.db_connection.insert_dataframe(mapped_df, "company_data")
            
            if success:
                # Update file_upload status
                self.update_processing_status(file_upload_id, 'completed')
                print(f"✅ Successfully processed file_upload_id: {file_upload_id}")
                return True
            else:
                self.update_processing_status(file_upload_id, 'failed', 'Database insertion failed')
                return False
                
        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            self.update_processing_status(file_upload_id, 'failed', error_msg)
            print(f"❌ {error_msg}")
            return False
    
    def apply_column_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply intelligent column mapping to DataFrame"""
        mapped_df = pd.DataFrame()
        
        # Define mapping patterns
        patterns = {
            'company_name': ['company', 'name', 'company_name', 'business'],
            'linkedin_url': ['linkedin', 'linkedin_url', 'linkedin_link'],
            'company_website': ['website', 'url', 'web', 'site'],
            'company_size': ['size', 'employees', 'company_size'],
            'industry': ['industry', 'sector', 'business_type'],
            'revenue': ['revenue', 'sales', 'turnover', 'income']
        }
        
        # Map columns
        for db_column, keywords in patterns.items():
            mapped_column = None
            for col in df.columns:
                if any(keyword in col.lower() for keyword in keywords):
                    mapped_column = col
                    break
            
            if mapped_column:
                mapped_df[db_column] = df[mapped_column].astype(str)
            else:
                mapped_df[db_column] = ""
        
        return mapped_df
    
    def update_processing_status(self, file_upload_id: int, status: str, error_message: str = None):
        """Update processing status of a file upload"""
        try:
            if not self.db_connection:
                return False
                
            update_fields = {
                'processing_status': status,
                'processed_date': datetime.now().isoformat()
            }
            
            if error_message:
                update_fields['processing_error'] = error_message
            
            # Create update query
            set_clause = ", ".join([f"{k} = '{v}'" for k, v in update_fields.items()])
            query = f"UPDATE file_upload SET {set_clause} WHERE id = {file_upload_id}"
            
            self.db_connection.query_to_dataframe(query)
            return True
            
        except Exception as e:
            print(f"Error updating processing status: {e}")
            return False
    
    def get_upload_statistics(self) -> Dict[str, Any]:
        """Get statistics about file uploads"""
        try:
            if not self.db_connection:
                return {}
                
            stats = {}
            
            # Total uploads
            result = self.db_connection.query_to_dataframe("SELECT COUNT(*) as count FROM file_upload")
            stats['total_uploads'] = int(result.iloc[0]['count']) if result is not None and not result.empty else 0
            
            # Pending uploads
            result = self.db_connection.query_to_dataframe("SELECT COUNT(*) as count FROM file_upload WHERE processing_status = 'pending'")
            stats['pending_uploads'] = int(result.iloc[0]['count']) if result is not None and not result.empty else 0
            
            # Completed uploads
            result = self.db_connection.query_to_dataframe("SELECT COUNT(*) as count FROM file_upload WHERE processing_status = 'completed'")
            stats['completed_uploads'] = int(result.iloc[0]['count']) if result is not None and not result.empty else 0
            
            # Failed uploads
            result = self.db_connection.query_to_dataframe("SELECT COUNT(*) as count FROM file_upload WHERE processing_status = 'failed'")
            stats['failed_uploads'] = int(result.iloc[0]['count']) if result is not None and not result.empty else 0
            
            # Total records processed
            result = self.db_connection.query_to_dataframe("SELECT COUNT(*) as count FROM company_data")
            stats['total_processed_records'] = int(result.iloc[0]['count']) if result is not None and not result.empty else 0
            
            return stats
            
        except Exception as e:
            print(f"Error getting upload statistics: {e}")
            return {}

def process_all_pending_files():
    """Process all pending file uploads - for scheduled jobs"""
    processor = FileUploadProcessor()
    
    print("🔄 Starting batch processing of pending uploads...")
    
    pending_uploads = processor.get_pending_uploads()
    if pending_uploads is None or pending_uploads.empty:
        print("ℹ️ No pending uploads found")
        return
    
    print(f"📋 Found {len(pending_uploads)} pending uploads")
    
    success_count = 0
    failure_count = 0
    
    for _, upload in pending_uploads.iterrows():
        file_upload_id = upload['id']
        file_name = upload['file_name']
        
        print(f"🔄 Processing: {file_name} (ID: {file_upload_id})")
        
        if processor.process_uploaded_file(file_upload_id):
            success_count += 1
            print(f"✅ Completed: {file_name}")
        else:
            failure_count += 1
            print(f"❌ Failed: {file_name}")
    
    print(f"\n📊 Batch processing complete:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {failure_count}")
    print(f"   📋 Total: {len(pending_uploads)}")

if __name__ == "__main__":
    # Test the file upload processor
    processor = FileUploadProcessor()
    
    print("🧪 Testing File Upload Processor...")
    
    # Get statistics
    stats = processor.get_upload_statistics()
    print(f"📊 Upload Statistics: {stats}")
    
    # Get pending uploads
    pending = processor.get_pending_uploads()
    if pending is not None and not pending.empty:
        print(f"📋 Pending uploads: {len(pending)}")
        print(pending)
    else:
        print("ℹ️ No pending uploads")
    
    # Process all pending files
    process_all_pending_files()