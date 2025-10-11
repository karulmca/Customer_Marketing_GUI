
import os
import sys
from datetime import datetime
import pytz
import pandas as pd
import json
import hashlib
from typing import Optional, Dict, Any, List
from database_config.db_utils import get_database_connection
from config_loader import ConfigLoader

# LinkedIn scraper import (optional)
try:
    # from linkedin_company_complete_scraper import CompleteCompanyScraper
    LINKEDIN_SCRAPER_AVAILABLE = True
    print("✅ LinkedIn scraper imported successfully")
except ImportError as e:
    print(f"⚠️ LinkedIn scraper not available: {e}")
    LINKEDIN_SCRAPER_AVAILABLE = False

class FileUploadProcessor:
    def get_ist_now(self):
        """Return current time in IST as formatted string"""
        ist = pytz.timezone('Asia/Kolkata')
        return datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

    def apply_column_mapping(self, df):
        """Stub for column mapping. Returns df unchanged. Implement your mapping logic here."""
        return df
    def process_uploaded_file_manual(self, file_upload_id: str, user_id: int) -> bool:
        """Process an uploaded file manually, updating user_id and status for manual jobs only."""
        try:
            # Set job type to 'Manual' in processing_jobs
            self.update_processing_status(file_upload_id, 'processing', user_id=user_id)
            self.mark_job_as_started(file_upload_id, user_id=user_id)
            print(f"🔄 [Manual] Started processing file_upload_id: {file_upload_id} for user {user_id}")
            upload_info = self.get_upload_data(file_upload_id)
            if not upload_info:
                self.mark_job_as_failed(file_upload_id, 'No data found in database', user_id=user_id)
                self.update_processing_status(file_upload_id, 'failed', 'No data found in database', user_id=user_id)
                return False
            raw_data = upload_info['raw_data']
            file_name = upload_info['file_name']
            df = pd.DataFrame(raw_data['data'])
            mapped_df = self.apply_column_mapping(df)
            # Standardize column names to match database schema
            column_rename_map = {
                'Company Name': 'company_name',
                'LinkedIn_URL': 'linkedin_url',
                'Website_URL': 'company_website',
                'Company_Size': 'company_size',
                'Industry': 'industry',
                'Revenue': 'revenue',
            }
            mapped_df = mapped_df.rename(columns=column_rename_map)
            if 'industry' in mapped_df.columns:
                mapped_df['industry'] = mapped_df['industry'].astype(str).str.slice(0, 200)
            mapped_df['file_source'] = file_name
            mapped_df['file_upload_id'] = file_upload_id
            mapped_df['created_by'] = f'user_{user_id}'
            # Drop columns not present in company_data table
            valid_columns = [
                'file_upload_id', 'file_source', 'created_by', 'industry', 'company_name', 'company_size',
                'company_website', 'linkedin_url', 'revenue', 'processing_status', 'processed_date'
            ]
            # Remove user_id if present
            if 'user_id' in mapped_df.columns:
                mapped_df = mapped_df.drop(columns=['user_id'])
            mapped_df = mapped_df[[col for col in mapped_df.columns if col in valid_columns]]
            # Retry logic for database insertion
            max_db_retries = 3
            for db_attempt in range(max_db_retries):
                success = self.db_connection.insert_dataframe(mapped_df, "company_data")
                if success:
                    break
                print(f"[WARN] Database insertion failed (attempt {db_attempt+1}/{max_db_retries})")
                if db_attempt == max_db_retries - 1:
                    self.sync_processing_completion(file_upload_id, 'failed', 0, 'Database insertion failed', user_id=user_id)
                    return False

            self.update_processing_status(file_upload_id, 'processing', 'LinkedIn scraping in progress', user_id=user_id)

            # Retry logic for LinkedIn scraping
            scraped_count = 0
            if LINKEDIN_SCRAPER_AVAILABLE:
                max_scraper_retries = 3
                for scraper_attempt in range(max_scraper_retries):
                    try:
                        import threading
                        result = {}
                        def run_scraper():
                            result['count'] = self._perform_linkedin_scraping(file_upload_id, mapped_df)
                        scraper_thread = threading.Thread(target=run_scraper)
                        scraper_thread.start()
                        scraper_thread.join(timeout=30)
                        if scraper_thread.is_alive():
                            print(f"[WARN] Scraper timeout (attempt {scraper_attempt+1}/{max_scraper_retries}) - retrying...")
                            continue
                        scraped_count = result.get('count', 0)
                        break
                    except Exception as e:
                        print(f"[WARN] Scraper error (attempt {scraper_attempt+1}/{max_scraper_retries}): {e}")
                        if scraper_attempt == max_scraper_retries - 1:
                            self.sync_processing_completion(file_upload_id, 'failed', len(mapped_df), f'Scraper failed: {e}', user_id=user_id)
                            return False

            self.mark_job_as_completed(file_upload_id, len(mapped_df), user_id=user_id)
            self.sync_processing_completion(file_upload_id, 'completed', len(mapped_df), f'Successfully processed and scraped {scraped_count} companies', user_id=user_id)
            print(f"✅ [Manual] Successfully processed file_upload_id: {file_upload_id} (scraped: {scraped_count})")
            return True
        except Exception as e:
            error_msg = f"[Manual] Processing error: {str(e)}"
            self.mark_job_as_failed(file_upload_id, error_msg, user_id=user_id)
            self.sync_processing_completion(file_upload_id, 'failed', 0, error_msg, user_id=user_id)
            print(f"❌ {error_msg}")
            return False

    def mark_job_as_started(self, file_upload_id: str, user_id=None) -> bool:
        """Mark processing job as started and sync across all tables"""
        try:
            if not self.db_connection:
                return False
            current_time = self.get_ist_now()
            valid_user_id = user_id if user_id not in [None, 'None', ''] else '1'  # Default to '1' or another valid user
            job_query = f"""
                UPDATE processing_jobs 
                SET job_status = 'processing',
                    started_at = '{current_time}',
                    updated_at = '{current_time}',
                    user_id = '{valid_user_id}'
                WHERE file_upload_id = '{file_upload_id}'
            """
            job_success = self.db_connection.execute_query(job_query)
            try:
                file_query = f"""
                    UPDATE file_upload 
                    SET processing_status = 'processing',
                        updated_at = '{current_time}',
                        user_id = '{valid_user_id}'
                    WHERE id = '{file_upload_id}'
                """
                file_success = self.db_connection.execute_query(file_query)
            except Exception as e:
                if "updated_at" in str(e):
                    file_query = f"""
                        UPDATE file_upload 
                        SET processing_status = 'processing',
                            user_id = '{valid_user_id}'
                        WHERE id = '{file_upload_id}'
                    """
                    file_success = self.db_connection.execute_query(file_query)
                else:
                    raise e
            data_query = f"""
                UPDATE company_data 
                SET processing_status = 'processing',
                    processed_date = '{current_time}'
                WHERE file_upload_id = '{file_upload_id}'
            """
            data_success = self.db_connection.execute_query(data_query)
            if job_success and file_success:
                print(f"✅ Job started and synced across all tables for file: {file_upload_id}")
                return True
            else:
                print(f"⚠️ Partial sync for job start - Job:{job_success}, File:{file_success}, Data:{data_success}")
                return False
        except Exception as e:
            print(f"Error marking job as started: {e}")
            return False

    def mark_job_as_completed(self, file_upload_id: str, processed_records: int = 0, user_id=None) -> bool:
        """Mark processing job as completed and sync across all tables"""
        try:
            if not self.db_connection:
                return False
            current_time = self.get_ist_now()
            valid_user_id = user_id if user_id not in [None, 'None', ''] else '1'  # Default to '1' or another valid user
            job_query = f"""
                UPDATE processing_jobs 
                SET job_status = 'completed',
                    completed_at = '{current_time}',
                    updated_at = '{current_time}',
                    processed_records = {processed_records},
                    user_id = '{valid_user_id}'
                WHERE file_upload_id = '{file_upload_id}'
            """
            job_success = self.db_connection.execute_query(job_query)
            try:
                file_query = f"""
                    UPDATE file_upload 
                    SET processing_status = 'completed',
                        processed_date = '{current_time}',
                        processed_records = {processed_records},
                        updated_at = '{current_time}',
                        user_id = '{valid_user_id}'
                    WHERE id = '{file_upload_id}'
                """
                file_success = self.db_connection.execute_query(file_query)
            except Exception as e:
                if "updated_at" in str(e):
                    file_query = f"""
                        UPDATE file_upload 
                        SET processing_status = 'completed',
                            processed_date = '{current_time}',
                            processed_records = {processed_records},
                            user_id = '{valid_user_id}'
                        WHERE id = '{file_upload_id}'
                    """
                    file_success = self.db_connection.execute_query(file_query)
                else:
                    raise e
            data_query = f"""
                UPDATE company_data 
                SET processing_status = 'completed',
                    processed_date = '{current_time}'
                WHERE file_upload_id = '{file_upload_id}'
            """
            data_success = self.db_connection.execute_query(data_query)
            if job_success and file_success and data_success:
                print(f"✅ Job completed and synced across all tables for file: {file_upload_id} ({processed_records} records)")
                return True
            else:
                print(f"⚠️ Partial sync for job completion - Job:{job_success}, File:{file_success}, Data:{data_success}")
                return False
        except Exception as e:
            print(f"Error marking job as completed: {e}")
            return False

    def mark_job_as_failed(self, file_upload_id: str, error_message: str = "", user_id=None) -> bool:
        """Mark processing job as failed and sync across all tables"""
        try:
            if not self.db_connection:
                return False
            current_time = self.get_ist_now()
            safe_error_message = error_message.replace("'", "''")[:500]
            job_query = f"""
                UPDATE processing_jobs 
                SET job_status = 'failed',
                    error_message = '{safe_error_message}',
                    updated_at = '{current_time}',
                    completed_at = '{current_time}',
                    user_id = '{user_id}'
                WHERE file_upload_id = '{file_upload_id}'
            """
            job_success = self.db_connection.execute_query(job_query)
            try:
                file_query = f"""
                    UPDATE file_upload 
                    SET processing_status = 'failed',
                        processing_error = '{safe_error_message}',
                        processed_date = '{current_time}',
                        updated_at = '{current_time}',
                        user_id = '{user_id}'
                    WHERE id = '{file_upload_id}'
                """
                file_success = self.db_connection.execute_query(file_query)
            except Exception as e:
                if "updated_at" in str(e):
                    file_query = f"""
                        UPDATE file_upload 
                        SET processing_status = 'failed',
                            processing_error = '{safe_error_message}',
                            processed_date = '{current_time}',
                            user_id = '{user_id}'
                        WHERE id = '{file_upload_id}'
                    """
                    file_success = self.db_connection.execute_query(file_query)
                else:
                    raise e
            data_query = f"""
                UPDATE company_data 
                SET processing_status = 'failed',
                    processed_date = '{current_time}'
                WHERE file_upload_id = '{file_upload_id}'
            """
            data_success = self.db_connection.execute_query(data_query)
            if job_success and file_success and data_success:
                print(f"✅ Job failed and synced across all tables for file: {file_upload_id}")
                print(f"📝 Error: {error_message}")
                return True
            else:
                print(f"⚠️ Partial sync for job failure - Job:{job_success}, File:{file_success}, Data:{data_success}")
                return False
        except Exception as e:
            print(f"Error marking job as failed: {e}")
            return False

    def sync_processing_completion(self, file_upload_id: str, status: str, processed_records: int = 0, error_message: str = None, user_id=None):
        """Synchronize processing completion across all three tables"""
        try:
            if not self.db_connection:
                print(f"❌ No database connection for syncing status of file: {file_upload_id}")
                return False
            current_time = self.get_ist_now()
            # Ensure user_id is valid (not None or 'None')
            valid_user_id = user_id if user_id not in [None, 'None', ''] else '1'  # Default to '1' or another valid user
            file_update_fields = {
                'processing_status': status,
                'processed_date': current_time,
                'processed_records': processed_records,
                'user_id': valid_user_id
            }
            if error_message:
                file_update_fields['processing_error'] = error_message[:500]
            file_set_clause = ", ".join([f"{k} = '{v}'" for k, v in file_update_fields.items()])
            file_query = f"UPDATE file_upload SET {file_set_clause} WHERE id = '{file_upload_id}'"
            print(f"🔄 Syncing status across all tables for file {file_upload_id} to '{status}'")
            file_success = self.db_connection.execute_query(file_query)
            job_status = 'completed' if status == 'completed' else 'failed'
            job_update_fields = {
                'job_status': job_status,
                'completed_date': current_time,
                'processed_records': processed_records,
                'user_id': valid_user_id
            }
            if error_message:
                job_update_fields['error_message'] = error_message[:500]
            job_set_clause = ", ".join([f"{k} = '{v}'" for k, v in job_update_fields.items()])
            job_query = f"UPDATE processing_jobs SET {job_set_clause} WHERE file_upload_id = '{file_upload_id}'"
            job_success = self.db_connection.execute_query(job_query)
            data_status = 'completed' if status == 'completed' else 'pending'
            # Remove user_id from company_data update (column does not exist)
            data_query = f"UPDATE company_data SET processing_status = '{data_status}', processed_date = '{current_time}' WHERE file_upload_id = '{file_upload_id}'"
            data_success = self.db_connection.execute_query(data_query)
            if file_success and job_success and data_success:
                print(f"✅ Successfully synced status across all tables for file: {file_upload_id}")
                return True
            else:
                print(f"⚠️ Partial sync completed for file: {file_upload_id} - File:{file_success}, Job:{job_success}, Data:{data_success}")
                return False
        except Exception as e:
            print(f"Error syncing processing completion: {e}")
            return False

    def update_processing_status(self, file_upload_id: str, status: str, error_message: str = None, user_id=None):
        """Update processing status of a file upload (legacy method - use sync_processing_completion for full sync)"""
        try:
            if not self.db_connection:
                print(f"❌ No database connection for updating status of file: {file_upload_id}")
                return False
            current_time = self.get_ist_now()
            # Always set user_id to 1 if None (for automated jobs)
            if user_id is None:
                user_id = 1
            update_fields = {
                'processing_status': status,
                'processed_date': current_time,
                'user_id': user_id
            }
            if error_message:
                update_fields['processing_error'] = error_message[:500]
            set_clause = ", ".join([f"{k} = '{v}'" for k, v in update_fields.items()])
            query = f"UPDATE file_upload SET {set_clause} WHERE id = '{file_upload_id}'"
            print(f"🔄 Updating database status for file {file_upload_id} to '{status}'")
            success = self.db_connection.execute_query(query)
            if success:
                print(f"✅ Database status updated successfully for file: {file_upload_id}")
                return True
            else:
                print(f"❌ Failed to update database status for file: {file_upload_id}")
                return False
        except Exception as e:
            print(f"Error updating processing status: {e}")
            return False
    """Handles file upload processing and JSON storage with single job per user support"""
    
    def __init__(self):
        self.db_connection = get_database_connection("postgresql")
        self.config = ConfigLoader()
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
    
    def upload_file_as_json(self, file_path: str, uploaded_by: str = "GUI_User", original_filename: str = None, user_id: int = None) -> Optional[str]:
        """
        Upload file content as JSON to file_upload table
        Returns file_upload_id if successful, None if failed
        """
        try:
            print(f"[DEBUG] Starting upload_file_as_json for: {file_path}, uploaded_by: {uploaded_by}, original_filename: {original_filename}, user_id: {user_id}")
            if not os.path.exists(file_path):
                print(f"[ERROR] File not found: {file_path}")
                return None

            # Read file into DataFrame
            try:
                if file_path.lower().endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file_path)
                elif file_path.lower().endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    print(f"[ERROR] Unsupported file format: {file_path}")
                    return None
            except Exception as e:
                print(f"[ERROR] Failed to read file into DataFrame: {e}")
                return None

            print(f"[DEBUG] DataFrame loaded: {df.shape[0]} rows, {df.shape[1]} columns")

            # Convert DataFrame to JSON
            try:
                df_clean = df.fillna('')  # Replace NaN with empty string
                data_records = []
                for _, row in df_clean.iterrows():
                    record = {}
                    for col in df_clean.columns:
                        value = row[col]
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
            except Exception as e:
                print(f"[ERROR] Failed to convert DataFrame to JSON: {e}")
                return None

            print(f"[DEBUG] JSON conversion complete. Rows: {len(data_records)}")

            # Calculate file hash
            try:
                file_hash = self.calculate_file_hash(file_path)
            except Exception as e:
                print(f"[ERROR] Failed to calculate file hash: {e}")
                return None

            print(f"[DEBUG] File hash: {file_hash}")

            # Check if file already exists
            try:
                existing_file = self.check_duplicate_file(file_hash)
            except Exception as e:
                print(f"[ERROR] Failed to check duplicate file: {e}")
                existing_file = None
            if existing_file:
                print(f"[INFO] File already uploaded with ID: {existing_file}")
                return existing_file

            # Get file info
            try:
                file_name = original_filename if original_filename else os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
            except Exception as e:
                print(f"[ERROR] Failed to get file info: {e}")
                return None

            # Insert into database - Check and reconnect if needed
            try:
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
            except Exception as e:
                print(f"[ERROR] Database connection error: {e}")
                return None

            # Create DataFrame for insertion
            try:
                upload_data = pd.DataFrame([{
                    'file_name': file_name,
                    'file_path': file_path,
                    'file_size': file_size,
                    'original_columns': json.dumps(list(df.columns)),
                    'raw_data': json.dumps(raw_data),
                    'uploaded_by': uploaded_by,
                    'user_id': user_id,
                    'processing_status': 'pending',
                    'records_count': len(df),
                    'file_hash': file_hash
                }])
            except Exception as e:
                print(f"[ERROR] Failed to create upload DataFrame: {e}")
                return None

            # Insert and get the ID
            print(f"[DEBUG] Attempting to insert file data into database...")
            try:
                success = self.db_connection.insert_dataframe(upload_data, "file_upload")
            except Exception as e:
                print(f"[ERROR] Database insertion failed: {e}")
                return None

            if success:
                print("✅ Database insertion successful")
                # Get the inserted record ID
                try:
                    file_upload_id = self.get_latest_upload_id(file_hash)
                except Exception as e:
                    print(f"[ERROR] Failed to get latest upload ID: {e}")
                    return None
                # Create processing job
                if file_upload_id:
                    try:
                        self.create_processing_job(file_upload_id, "data_extraction")
                        print(f"✅ Processing job created for file ID: {file_upload_id}")
                    except Exception as e:
                        print(f"[ERROR] Failed to create processing job: {e}")
                return file_upload_id
                    
                print(f"✅ File uploaded successfully with ID: {file_upload_id}")
                return file_upload_id
            else:
                print("❌ Failed to upload file to database - insertion failed")
                return None
                
        except Exception as e:
            print(f"❌ Error uploading file: {str(e)}")
            return None
    
    def check_duplicate_file(self, file_hash: str) -> Optional[str]:
        """Check if file with same hash already exists"""
        try:
            if not self.db_connection:
                return None
                
            query = f"SELECT id FROM file_upload WHERE file_hash = '{file_hash}' LIMIT 1"
            result = self.db_connection.query_to_dataframe(query)
            
            if result is not None and not result.empty:
                return result.iloc[0]['id']
            return None
            
        except Exception as e:
            print(f"Error checking duplicate file: {e}")
            return None
    
    def get_latest_upload_id(self, file_hash: str) -> Optional[str]:
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
                return result.iloc[0]['id']
            return None
            
        except Exception as e:
            print(f"Error getting latest upload ID: {e}")
            return None
    
    def create_processing_job(self, file_upload_id: str, job_type: str = "data_extraction", uploaded_by: str = None) -> bool:
        """Create a processing job for the uploaded file and sync status"""
        try:
            if not self.db_connection:
                return False
            
            # Get uploaded_by from file_upload table if not provided
            if not uploaded_by:
                upload_info_query = f"SELECT uploaded_by FROM file_upload WHERE id = '{file_upload_id}'"
                upload_info = self.db_connection.query_to_dataframe(upload_info_query)
                if upload_info is not None and not upload_info.empty:
                    uploaded_by = upload_info.iloc[0]['uploaded_by']
                else:
                    uploaded_by = 'unknown_user'
                
            # Use consistent timestamp format
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            job_data = pd.DataFrame([{
                'job_type': job_type,
                'file_upload_id': file_upload_id,
                'job_status': 'queued',
                'uploaded_by': uploaded_by,
                'scheduled_at': current_time,
                'job_config': json.dumps({
                    'auto_column_mapping': True,
                    'data_validation': True,
                    'duplicate_detection': True,
                    'single_job_per_user': self.config.is_single_job_per_user_enabled(),
                    'max_processing_time_minutes': self.config.get_max_processing_time_minutes()
                }),
                'retry_count': 0,
                'max_retries': self.config.get_max_retries()
            }])
            
            job_success = self.db_connection.insert_dataframe(job_data, "processing_jobs")
            
            if job_success:
                # Ensure file_upload table is also marked as pending (should already be, but ensure sync)
                try:
                    file_query = f"""
                        UPDATE file_upload 
                        SET processing_status = 'pending',
                            updated_at = '{current_time}'
                        WHERE id = '{file_upload_id}' AND processing_status != 'pending'
                    """
                    self.db_connection.execute_query(file_query)
                except Exception as e:
                    # Fallback if updated_at column doesn't exist
                    if "updated_at" in str(e):
                        file_query = f"""
                            UPDATE file_upload 
                            SET processing_status = 'pending'
                            WHERE id = '{file_upload_id}' AND processing_status != 'pending'
                        """
                        self.db_connection.execute_query(file_query)
                
                print(f"✅ Processing job created and status synced for file_upload_id: {file_upload_id} (user: {uploaded_by})")
                return True
            else:
                print(f"❌ Failed to create processing job for file_upload_id: {file_upload_id}")
                return False
            
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
    
    def get_user_active_jobs(self, uploaded_by: str) -> Optional[pd.DataFrame]:
        """Get currently processing jobs for a specific user"""
        try:
            if not self.db_connection:
                return None
                
            query = f"""
                SELECT fu.id, fu.file_name, fu.uploaded_by, fu.processing_status,
                       pj.job_status, pj.started_at, pj.updated_at
                FROM file_upload fu
                LEFT JOIN processing_jobs pj ON fu.id = pj.file_upload_id
                WHERE fu.uploaded_by = '{uploaded_by}' 
                AND fu.processing_status IN ('processing', 'queued')
                ORDER BY fu.upload_date ASC
            """
            return self.db_connection.query_to_dataframe(query)
            
        except Exception as e:
            print(f"Error getting user active jobs: {e}")
            return None
    
    def get_next_pending_job_for_user(self, uploaded_by: str) -> Optional[Dict[str, Any]]:
        """Get the next pending job for a user (single job per user logic)"""
        try:
            if not self.db_connection:
                return None
            
            # Check if user has any active jobs if single job per user is enabled
            if self.config.is_single_job_per_user_enabled():
                active_jobs = self.get_user_active_jobs(uploaded_by)
                if active_jobs is not None and not active_jobs.empty:
                    print(f"⏳ User {uploaded_by} has active jobs, skipping new job assignment")
                    return None
            
            # Get the oldest pending upload for this user
            query = f"""
                SELECT id, file_name, upload_date, records_count, uploaded_by
                FROM file_upload 
                WHERE processing_status = 'pending' 
                AND uploaded_by = '{uploaded_by}'
                ORDER BY upload_date ASC
                LIMIT 1
            """
            result = self.db_connection.query_to_dataframe(query)
            
            if result is not None and not result.empty:
                return result.iloc[0].to_dict()
            return None
            
        except Exception as e:
            print(f"Error getting next pending job for user: {e}")
            return None
    
    def get_all_users_with_pending_jobs(self) -> List[str]:
        """Get list of all users who have pending jobs"""
        try:
            if not self.db_connection:
                return []
                
            query = """
                SELECT DISTINCT uploaded_by
                FROM file_upload 
                WHERE processing_status = 'pending'
                ORDER BY uploaded_by
            """
            result = self.db_connection.query_to_dataframe(query)
            
            if result is not None and not result.empty:
                return result['uploaded_by'].tolist()
            return []
            
        except Exception as e:
            print(f"Error getting users with pending jobs: {e}")
            return []
    
    def get_pending_uploads_by_user_queue(self) -> Optional[pd.DataFrame]:
        """Get pending uploads respecting single job per user constraint"""
        try:
            if not self.db_connection:
                return None
            
            if not self.config.is_single_job_per_user_enabled():
                # If single job per user is disabled, return all pending uploads
                return self.get_pending_uploads()
            
            # Get all users with pending jobs
            users_with_pending = self.get_all_users_with_pending_jobs()
            
            if not users_with_pending:
                return pd.DataFrame()  # Empty DataFrame
            
            eligible_jobs = []
            
            for user in users_with_pending:
                # Check if user has any active jobs
                active_jobs = self.get_user_active_jobs(user)
                
                if active_jobs is None or active_jobs.empty:
                    # User has no active jobs, get their next pending job
                    next_job = self.get_next_pending_job_for_user(user)
                    if next_job:
                        eligible_jobs.append(next_job)
                else:
                    print(f"⏳ Skipping user {user} - has {len(active_jobs)} active job(s)")
            
            if eligible_jobs:
                return pd.DataFrame(eligible_jobs)
            else:
                return pd.DataFrame()  # Empty DataFrame
                
        except Exception as e:
            print(f"Error getting pending uploads by user queue: {e}")
            return None
    
    def get_upload_data(self, file_upload_id: int) -> Optional[Dict[str, Any]]:
        """Get raw JSON data from a file upload"""
        try:
            if not self.db_connection:
                return None
                
            query = f"""
                SELECT raw_data, original_columns, file_name
                FROM file_upload 
                WHERE id = '{file_upload_id}'
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
    
    def _perform_linkedin_scraping(self, file_upload_id: str, df: pd.DataFrame) -> int:
        """Perform LinkedIn scraping on the companies and update database"""
        try:
            print(f"🔍 Starting LinkedIn scraping for {len(df)} companies")
            
            # Initialize the LinkedIn scraper
            #scraper = CompleteCompanyScraper(self.config.config if hasattr(self.config, 'config') else None)
            
            # Create a copy of the dataframe for scraping
            scraping_df = df.copy()
            
            # Map our column names to what the scraper expects
            if 'linkedin_url' in scraping_df.columns:
                scraping_df['LinkedIn_URL'] = scraping_df['linkedin_url']
            if 'company_website' in scraping_df.columns:
                scraping_df['Company_Website'] = scraping_df['company_website']
            if 'company_name' in scraping_df.columns:
                scraping_df['Company_Name'] = scraping_df['company_name']
            
            # Perform the scraping
            # Define or import 'scraper' before using. Example:
            # from linkedin_company_complete_scraper import CompleteCompanyScraper
            # scraper = CompleteCompanyScraper()
            if LINKEDIN_SCRAPER_AVAILABLE:
                try:
                    from scrapers.linkedin_company_complete_scraper import CompleteCompanyScraper
                    scraper = CompleteCompanyScraper()
                except Exception as e:
                    raise RuntimeError(f"LinkedIn scraper import failed: {e}")
                enhanced_df = scraper.process_companies(
                    scraping_df,
                    linkedin_column='LinkedIn_URL',
                    website_column='Company_Website',
                    company_name_column='Company_Name'
                )
            else:
                raise RuntimeError("LinkedIn scraper is not available. Cannot process companies.")
            
            # Update database with scraped data
            scraped_count = 0
            for index, row in enhanced_df.iterrows():
                # Debug print for each row
                print(f"[DEBUG] Row {index}: LinkedIn_URL={row.get('LinkedIn_URL', '')}, Company_Name={row.get('Company_Name', '')}, ExtractionResult={{'Company_Size_Enhanced': {row.get('Company_Size_Enhanced')}, 'Industry_Enhanced': {row.get('Industry_Enhanced')}, 'LinkedIn_Status': {row.get('LinkedIn_Status')}}}")

                company_id = row.get('id')  # Assuming we have the company_data ID

                # Prepare update data
                update_data = {}

                # Map enhanced data back to our database columns
                if row.get('Company_Size_Enhanced') and row.get('Company_Size_Enhanced') != 'Not Processed':
                    update_data['company_size'] = row['Company_Size_Enhanced']

                if row.get('Industry_Enhanced') and row.get('Industry_Enhanced') != 'Not Processed':
                    update_data['industry'] = row['Industry_Enhanced']

                if row.get('Revenue_Enhanced') and row.get('Revenue_Enhanced') != 'Not Processed':
                    update_data['revenue'] = row['Revenue_Enhanced']

                # Update the database if we have data to update
                if update_data and company_id:
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    update_fields = []
                    for field, value in update_data.items():
                        update_fields.append(f"{field} = '{str(value).replace(chr(39), chr(39)+chr(39))}'")  # Escape single quotes

                    if update_fields:
                        update_query = f"""
                        UPDATE company_data 
                        SET {', '.join(update_fields)}, processing_status = 'completed', processed_date = '{current_time}'
                        WHERE id = '{company_id}'
                        """

                        try:
                            self.db_connection.execute_query(update_query)
                            scraped_count += 1
                        except Exception as e:
                            print(f"Error updating company {company_id}: {e}")

                # Also try to update by file_upload_id and company name if no ID
                elif update_data:
                    company_name = row.get('company_name', row.get('Company_Name', ''))
                    if company_name:
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        update_fields = []
                        for field, value in update_data.items():
                            update_fields.append(f"{field} = '{str(value).replace(chr(39), chr(39)+chr(39))}'")

                        if update_fields:
                            update_query = f"""
                            UPDATE company_data 
                            SET {', '.join(update_fields)}, processing_status = 'completed', processed_date = '{current_time}'
                            WHERE file_upload_id = '{file_upload_id}' 
                            AND company_name = '{company_name.replace(chr(39), chr(39)+chr(39))}'
                            """

                            try:
                                self.db_connection.execute_query(update_query)
                                scraped_count += 1
                            except Exception as e:
                                print(f"Error updating company {company_name}: {e}")
            
            print(f"✅ LinkedIn scraping completed. Updated {scraped_count} companies")
            return scraped_count
            
        except Exception as e:
            print(f"❌ LinkedIn scraping error: {e}")
            return 0
    
    def process_uploaded_file(self, file_upload_id: str) -> bool:
        """Process an uploaded file and move data to company_data table with LinkedIn scraping"""
        try:
            # Update status to processing at start and mark job as started
            self.update_processing_status(file_upload_id, 'processing')
            self.mark_job_as_started(file_upload_id)
            print(f"🔄 Started processing file_upload_id: {file_upload_id}")
            
            # Get upload data
            upload_info = self.get_upload_data(file_upload_id)
            if not upload_info:
                print(f"No data found for file_upload_id: {file_upload_id}")
                self.mark_job_as_failed(file_upload_id, 'No data found in database')
                self.update_processing_status(file_upload_id, 'failed', 'No data found in database')
                return False
            
            raw_data = upload_info['raw_data']
            file_name = upload_info['file_name']
            
            # Convert JSON data back to DataFrame
            df = pd.DataFrame(raw_data['data'])
            
            # Apply column mapping
            mapped_df = self.apply_column_mapping(df)
            # Standardize column names to match database schema
            column_rename_map = {
                'Company Name': 'company_name',
                'LinkedIn_URL': 'linkedin_url',
                'Website_URL': 'company_website',
                'Company_Size': 'company_size',
                'Industry': 'industry',
                'Revenue': 'revenue',
            }
            mapped_df = mapped_df.rename(columns=column_rename_map)
            # Drop columns not present in company_data table
            table_columns = [
                'file_upload_id', 'file_source', 'created_by', 'industry', 'company_name', 'company_size',
                'company_website', 'linkedin_url', 'revenue', 'processing_status', 'processed_date'
            ]
            missing_cols = [col for col in mapped_df.columns if col not in table_columns]
            if missing_cols:
                mapped_df = mapped_df.drop(columns=missing_cols)
                print(f"[INFO] Dropped columns not in company_data: {missing_cols}")

            # Truncate 'industry' column to 200 characters if present
            if 'industry' in mapped_df.columns:
                mapped_df['industry'] = mapped_df['industry'].astype(str).str.slice(0, 200)

            # Add metadata
            mapped_df['file_source'] = file_name
            mapped_df['file_upload_id'] = file_upload_id
            mapped_df['created_by'] = 'scheduled_processor'


            # Debug print: show DataFrame columns and first few rows before insert
            print("[DEBUG] DataFrame columns before insert:", mapped_df.columns.tolist())
            print("[DEBUG] DataFrame sample data before insert:")
            print(mapped_df.head())

            # Insert into company_data table first
            success = self.db_connection.insert_dataframe(mapped_df, "company_data")
            
            if not success:
                self.sync_processing_completion(file_upload_id, 'failed', 0, 'Database insertion failed')
                return False
            
            # Update status to scraping
            self.update_processing_status(file_upload_id, 'processing', 'LinkedIn scraping in progress')
            print(f"🔍 Starting LinkedIn scraping for file_upload_id: {file_upload_id}")
            
            # Perform LinkedIn scraping if available
            scraped_count = 0
            if LINKEDIN_SCRAPER_AVAILABLE:
                scraped_count = self._perform_linkedin_scraping(file_upload_id, mapped_df)
            else:
                print("⚠️ LinkedIn scraper not available, skipping scraping step")
            
            # Update all three tables for complete sync and mark job as completed
            self.mark_job_as_completed(file_upload_id, len(mapped_df))
            self.sync_processing_completion(file_upload_id, 'completed', len(mapped_df), f'Successfully processed and scraped {scraped_count} companies')
            print(f"✅ Successfully processed file_upload_id: {file_upload_id} (scraped: {scraped_count})")
            return True
                
        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            self.mark_job_as_failed(file_upload_id, error_msg)
            self.sync_processing_completion(file_upload_id, 'failed', 0, error_msg)
            print(f"❌ {error_msg}")
            return False
    
    def mark_job_as_started(self, file_upload_id: str, user_id=None) -> bool:
        """Mark processing job as started and sync across all tables"""
        try:
            if not self.db_connection:
                return False
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            job_query = f"""
                UPDATE processing_jobs 
                SET job_status = 'processing',
                    started_at = '{current_time}',
                    updated_at = '{current_time}',
                    user_id = '{user_id}'
                WHERE file_upload_id = '{file_upload_id}'
            """
            job_success = self.db_connection.execute_query(job_query)
            try:
                file_query = f"""
                    UPDATE file_upload 
                    SET processing_status = 'processing',
                        updated_at = '{current_time}',
                        user_id = '{user_id}'
                    WHERE id = '{file_upload_id}'
                """
                file_success = self.db_connection.execute_query(file_query)
            except Exception as e:
                if "updated_at" in str(e):
                    file_query = f"""
                        UPDATE file_upload 
                        SET processing_status = 'processing',
                            user_id = '{user_id}'
                        WHERE id = '{file_upload_id}'
                    """
                    file_success = self.db_connection.execute_query(file_query)
                else:
                    raise e
            data_query = f"""
                UPDATE company_data 
                SET processing_status = 'processing',
                    processed_date = '{current_time}'
                WHERE file_upload_id = '{file_upload_id}'
            """
            data_success = self.db_connection.execute_query(data_query)
            if job_success and file_success:
                print(f"✅ Job started and synced across all tables for file: {file_upload_id}")
                return True
            else:
                print(f"⚠️ Partial sync for job start - Job:{job_success}, File:{file_success}, Data:{data_success}")
                return False
        except Exception as e:
            print(f"Error marking job as started: {e}")
            return False
		
def mark_job_as_completed(self, file_upload_id: str, processed_records: int = 0, user_id=None) -> bool:
    """Mark processing job as completed and sync across all tables"""
    try:
        if not self.db_connection:
            return False
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        job_query = f"""
            UPDATE processing_jobs 
            SET job_status = 'completed',
                completed_at = '{current_time}',
                updated_at = '{current_time}',
                processed_records = {processed_records},
                user_id = '{user_id}'
            WHERE file_upload_id = '{file_upload_id}'
        """
        job_success = self.db_connection.execute_query(job_query)
        try:
            file_query = f"""
                UPDATE file_upload 
                SET processing_status = 'completed',
                    processed_date = '{current_time}',
                    processed_records = {processed_records},
                    updated_at = '{current_time}',
                    user_id = '{user_id}'
                WHERE id = '{file_upload_id}'
            """
            file_success = self.db_connection.execute_query(file_query)
        except Exception as e:
            if "updated_at" in str(e):
                file_query = f"""
                    UPDATE file_upload 
                    SET processing_status = 'completed',
                        processed_date = '{current_time}',
                        processed_records = {processed_records},
                        user_id = '{user_id}'
                    WHERE id = '{file_upload_id}'
                """
                file_success = self.db_connection.execute_query(file_query)
            else:
                raise e
            data_query = f"""
                UPDATE company_data 
                SET processing_status = 'completed',
                    processed_date = '{current_time}'
                WHERE file_upload_id = '{file_upload_id}'
            """
            data_success = self.db_connection.execute_query(data_query)
        if job_success and file_success and data_success:
            print(f"✅ Job completed and synced across all tables for file: {file_upload_id} ({processed_records} records)")
            return True
        else:
            print(f"⚠️ Partial sync for job completion - Job:{job_success}, File:{file_success}, Data:{data_success}")
            return False
    except Exception as e:
        print(f"Error marking job as completed: {e}")
        return False		
    
    
    def mark_job_as_failed(self, file_upload_id: str, error_message: str = "", user_id=None) -> bool:
        """Mark processing job as failed and sync across all tables"""
        try:
            if not self.db_connection:
                return False
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            safe_error_message = error_message.replace("'", "''")[:500]
            job_query = f"""
                UPDATE processing_jobs 
                SET job_status = 'failed',
                    error_message = '{safe_error_message}',
                    updated_at = '{current_time}',
                    completed_at = '{current_time}',
                    user_id = '{user_id}'
                WHERE file_upload_id = '{file_upload_id}'
            """
            job_success = self.db_connection.execute_query(job_query)
            try:
                file_query = f"""
                    UPDATE file_upload 
                    SET processing_status = 'failed',
                        processing_error = '{safe_error_message}',
                        processed_date = '{current_time}',
                        updated_at = '{current_time}',
                        user_id = '{user_id}'
                    WHERE id = '{file_upload_id}'
                """
                file_success = self.db_connection.execute_query(file_query)
            except Exception as e:
                if "updated_at" in str(e):
                    file_query = f"""
                        UPDATE file_upload 
                        SET processing_status = 'failed',
                            processing_error = '{safe_error_message}',
                            processed_date = '{current_time}',
                            user_id = '{user_id}'
                        WHERE id = '{file_upload_id}'
                    """
                    file_success = self.db_connection.execute_query(file_query)
                else:
                    raise e
            data_query = f"""
                UPDATE company_data 
                SET processing_status = 'failed',
                    processed_date = '{current_time}'
                WHERE file_upload_id = '{file_upload_id}'
            """
            data_success = self.db_connection.execute_query(data_query)
            if job_success and file_success and data_success:
                print(f"✅ Job failed and synced across all tables for file: {file_upload_id}")
                print(f"📝 Error: {error_message}")
                return True
            else:
                print(f"⚠️ Partial sync for job failure - Job:{job_success}, File:{file_success}, Data:{data_success}")
                return False
        except Exception as e:
            print(f"Error marking job as failed: {e}")
            return False
    
    def apply_column_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply intelligent column mapping to DataFrame"""
        mapped_df = pd.DataFrame()
        
        # Define mapping patterns - prioritizing standardized template format
        patterns = {
            'company_name': ['Company Name', 'company_name', 'company', 'name', 'business'],
            'linkedin_url': ['LinkedIn_URL', 'linkedin_url', 'Company Linkedin', 'linkedin', 'linkedin_link'],
            'company_website': ['Website_URL', 'website', 'company_website', 'url', 'web', 'site'],
            'company_size': ['Company_Size', 'company_size', 'Size', 'size', 'employees'],
            'industry': ['Industry', 'industry', 'sector', 'business_type'],
            'revenue': ['Revenue', 'revenue', 'sales', 'turnover', 'income']
        }
        
        # Map columns with priority: exact match > case-insensitive > fuzzy match
        for db_column, keywords in patterns.items():
            mapped_column = None
            
            # First priority: exact match (standardized format)
            for keyword in keywords:
                if keyword in df.columns:
                    mapped_column = keyword
                    break
            
            # Second priority: case-insensitive exact match
            if not mapped_column:
                for col in df.columns:
                    for keyword in keywords:
                        if col.lower() == keyword.lower():
                            mapped_column = col
                            break
                    if mapped_column:
                        break
            
            # Third priority: fuzzy match (contains keyword)
            if not mapped_column:
                for col in df.columns:
                    for keyword in keywords:
                        if keyword.lower() in col.lower():
                            mapped_column = col
                            break
                    if mapped_column:
                        break
            
            if mapped_column:
                mapped_df[db_column] = df[mapped_column].astype(str)
                print(f"Mapped '{mapped_column}' -> '{db_column}'")
            else:
                mapped_df[db_column] = ""
                print(f"No match found for '{db_column}' - setting empty")
        
        return mapped_df
    
    def sync_processing_completion(self, file_upload_id: str, status: str, processed_records: int = 0, error_message: str = None, user_id=None):
        """Synchronize processing completion across all three tables"""
        try:
            if not self.db_connection:
                print(f"❌ No database connection for syncing status of file: {file_upload_id}")
                return False
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file_update_fields = {
                'processing_status': status,
                'processed_date': current_time,
                'processed_records': processed_records,
                'user_id': user_id
            }
            if error_message:
                file_update_fields['processing_error'] = error_message[:500]
            file_set_clause = ", ".join([f"{k} = '{v}'" for k, v in file_update_fields.items()])
            file_query = f"UPDATE file_upload SET {file_set_clause} WHERE id = '{file_upload_id}'"
            print(f"🔄 Syncing status across all tables for file {file_upload_id} to '{status}'")
            file_success = self.db_connection.execute_query(file_query)
            job_status = 'completed' if status == 'completed' else 'failed'
            job_update_fields = {
                'job_status': job_status,
                'completed_date': current_time,
                'processed_records': processed_records,
                'user_id': user_id
            }
            if error_message:
                job_update_fields['error_message'] = error_message[:500]
            job_set_clause = ", ".join([f"{k} = '{v}'" for k, v in job_update_fields.items()])
            job_query = f"UPDATE processing_jobs SET {job_set_clause} WHERE file_upload_id = '{file_upload_id}'"
            job_success = self.db_connection.execute_query(job_query)
            data_status = 'completed' if status == 'completed' else 'pending'
            data_query = f"UPDATE company_data SET processing_status = '{data_status}', processed_date = '{current_time}', user_id = '{user_id}' WHERE file_upload_id = '{file_upload_id}'"
            data_success = self.db_connection.execute_query(data_query)
            if file_success and job_success and data_success:
                print(f"✅ Successfully synced status across all tables for file: {file_upload_id}")
                return True
            else:
                print(f"⚠️ Partial sync completed for file: {file_upload_id} - File:{file_success}, Job:{job_success}, Data:{data_success}")
                return False
        except Exception as e:
            print(f"Error syncing processing completion: {e}")
            return False

    def update_processing_status(self, file_upload_id: str, status: str, error_message: str = None, user_id=None):
    # ...existing code...
    
        if not self.db_connection:
            print(f"❌ No database connection for updating status of file: {file_upload_id}")
            return False
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_fields = {
            'processing_status': status,
            'processed_date': current_time,
            'user_id': user_id
        }
        if error_message:
            update_fields['processing_error'] = error_message[:500]
        set_clause = ", ".join([f"{k} = '{v}'" for k, v in update_fields.items()])
        query = f"UPDATE file_upload SET {set_clause} WHERE id = '{file_upload_id}'"
        print(f"🔄 Updating database status for file {file_upload_id} to '{status}'")
        success = self.db_connection.execute_query(query)
        if success:
            print(f"✅ Database status updated successfully for file: {file_upload_id}")
            return True
        else:
            print(f"❌ Failed to update database status for file: {file_upload_id}")
            return False
    # ...existing code...
    
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
    
    # ...existing code...