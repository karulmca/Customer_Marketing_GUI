"""
Integration Bridge for Authenticated File Processing
Connects the authenticated GUI with the existing file processing system
"""

import sys
import os
import json
from datetime import datetime
import threading

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing components
try:
    from database_config.db_utils import get_database_connection
    from enhanced_scheduled_processor import EnhancedScheduledProcessor
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Database components not available: {e}")
    DATABASE_AVAILABLE = False

class AuthenticatedFileProcessor:
    """Bridge between authenticated GUI and existing file processing system"""
    
    def __init__(self, user_info=None):
        self.user_info = user_info
        self.db_connection = None
        self.processor = None
        
        if DATABASE_AVAILABLE:
            try:
                self.db_connection = get_database_connection("postgresql")
                self.db_connection.connect()
                self.processor = EnhancedScheduledProcessor()
                print(f"✅ Database connection established for user: {user_info['username']}")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
    
    def upload_file(self, file_path, auto_process=True, progress_callback=None):
        """
        Upload file with authentication context
        
        Args:
            file_path: Path to the Excel file
            auto_process: Whether to start processing automatically
            progress_callback: Function to call with progress updates
            
        Returns:
            dict: Upload result with success status and file_id
        """
        result = {
            "success": False,
            "message": "",
            "file_id": None,
            "job_id": None
        }
        
        try:
            if not os.path.exists(file_path):
                result["message"] = "File does not exist"
                return result
            
            # Read and process Excel file
            if progress_callback:
                progress_callback("Reading Excel file...", 0, 4)
            
            # Convert Excel to JSON (similar to existing logic)
            excel_data = self._convert_excel_to_json(file_path)
            
            if not excel_data:
                result["message"] = "Failed to read Excel file"
                return result
            
            if progress_callback:
                progress_callback("Inserting into database...", 1, 4)
            
            # Insert into database with user context
            file_id = self._insert_file_data(excel_data, file_path)
            
            if not file_id:
                result["message"] = "Failed to insert file data"
                return result
            
            if progress_callback:
                progress_callback("Creating processing job...", 2, 4)
            
            # Create processing job
            job_id = self._create_processing_job(file_id)
            
            if not job_id:
                result["message"] = "Failed to create processing job"
                return result
            
            result.update({
                "success": True,
                "message": "File uploaded successfully",
                "file_id": file_id,
                "job_id": job_id
            })
            
            # Start auto-processing if enabled
            if auto_process and self.processor:
                if progress_callback:
                    progress_callback("Starting auto-processing...", 3, 4)
                
                # Start processing in background thread
                threading.Thread(
                    target=self._start_auto_processing,
                    args=(job_id, progress_callback),
                    daemon=True
                ).start()
            
            if progress_callback:
                progress_callback("Upload completed", 4, 4)
            
        except Exception as e:
            result["message"] = f"Upload error: {str(e)}"
            print(f"❌ Upload error: {e}")
        
        return result
    
    def _convert_excel_to_json(self, file_path):
        """Convert Excel file to JSON format"""
        try:
            import pandas as pd
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Convert to JSON format expected by the system
            json_data = {
                "columns": df.columns.tolist(),
                "data": df.to_dict('records')
            }
            
            return json_data
            
        except Exception as e:
            print(f"❌ Excel conversion error: {e}")
            return None
    
    def _insert_file_data(self, excel_data, file_path):
        """Insert file data into database"""
        try:
            if not self.db_connection:
                return None
            
            from sqlalchemy import text
            
            # Prepare file data
            file_name = os.path.basename(file_path)
            raw_data = json.dumps(excel_data)
            uploaded_by = self.user_info.get('username', 'system') if self.user_info else 'system'
            
            # Insert into file_upload table
            with self.db_connection.manager.engine.connect() as conn:
                insert_query = text("""
                    INSERT INTO file_upload (file_name, raw_data, uploaded_by, processing_status, upload_date)
                    VALUES (:file_name, :raw_data, :uploaded_by, 'pending', CURRENT_TIMESTAMP)
                    RETURNING id
                """)
                
                result = conn.execute(insert_query, {
                    'file_name': file_name,
                    'raw_data': raw_data,
                    'uploaded_by': uploaded_by
                })
                
                conn.commit()
                file_id = result.fetchone()[0]
                print(f"✅ File inserted with ID: {file_id}")
                return file_id
                
        except Exception as e:
            print(f"❌ Database insert error: {e}")
            return None
    
    def _create_processing_job(self, file_id):
        """Create processing job for the uploaded file"""
        try:
            if not self.db_connection:
                return None
            
            from sqlalchemy import text
            
            with self.db_connection.manager.engine.connect() as conn:
                job_query = text("""
                    INSERT INTO processing_jobs (job_type, file_upload_id, job_status, scheduled_at)
                    VALUES ('data_extraction', :file_id, 'queued', CURRENT_TIMESTAMP)
                    RETURNING id
                """)
                
                result = conn.execute(job_query, {'file_id': file_id})
                conn.commit()
                job_id = result.fetchone()[0]
                print(f"✅ Processing job created with ID: {job_id}")
                return job_id
                
        except Exception as e:
            print(f"❌ Job creation error: {e}")
            return None
    
    def _start_auto_processing(self, job_id, progress_callback=None):
        """Start auto-processing in background"""
        try:
            if not self.processor:
                print("❌ Processor not available")
                return
            
            if progress_callback:
                progress_callback("LinkedIn scraping in progress...", -1, -1)
            
            # Start processing
            success = self.processor.process_pending_job(job_id, scraper_type="complete")
            
            if progress_callback:
                if success:
                    progress_callback("Processing completed successfully!", -1, -1)
                else:
                    progress_callback("Processing failed", -1, -1)
            
            print(f"{'✅' if success else '❌'} Auto-processing {'completed' if success else 'failed'} for job {job_id}")
            
        except Exception as e:
            print(f"❌ Auto-processing error: {e}")
            if progress_callback:
                progress_callback(f"Processing error: {str(e)}", -1, -1)
    
    def get_processing_status(self, limit=10):
        """Get recent processing status"""
        try:
            if not self.db_connection:
                return []
            
            status_query = """
                SELECT 
                    pj.id as job_id,
                    pj.job_status,
                    pj.scheduled_at,
                    pj.started_at,
                    pj.completed_at,
                    fu.file_name,
                    fu.uploaded_by,
                    COUNT(cd.id) as companies_processed
                FROM processing_jobs pj
                JOIN file_upload fu ON pj.file_upload_id = fu.id
                LEFT JOIN company_data cd ON cd.file_upload_id = fu.id
                GROUP BY pj.id, pj.job_status, pj.scheduled_at, pj.started_at, pj.completed_at, fu.file_name, fu.uploaded_by
                ORDER BY pj.scheduled_at DESC
                LIMIT %s
            """
            
            # Replace with proper parameterized query
            formatted_query = status_query.replace('%s', str(limit))
            result = self.db_connection.query_to_dataframe(formatted_query)
            
            if result is not None and not result.empty:
                return result.to_dict('records')
            
            return []
            
        except Exception as e:
            print(f"❌ Status query error: {e}")
            return []
    
    def get_user_statistics(self):
        """Get statistics for the current user"""
        try:
            if not self.db_connection or not self.user_info:
                return {}
            
            username = self.user_info['username']
            
            # Get user-specific statistics
            stats_query = f"""
                SELECT 
                    COUNT(DISTINCT fu.id) as files_uploaded,
                    COUNT(DISTINCT pj.id) as jobs_created,
                    COUNT(DISTINCT cd.id) as companies_processed,
                    COUNT(CASE WHEN pj.job_status = 'completed' THEN 1 END) as jobs_completed
                FROM file_upload fu
                LEFT JOIN processing_jobs pj ON pj.file_upload_id = fu.id
                LEFT JOIN company_data cd ON cd.file_upload_id = fu.id
                WHERE fu.uploaded_by = '{username}'
            """
            
            result = self.db_connection.query_to_dataframe(stats_query)
            
            if result is not None and not result.empty:
                return result.iloc[0].to_dict()
            
            return {}
            
        except Exception as e:
            print(f"❌ Statistics error: {e}")
            return {}

# Global processor instance
authenticated_processor = None

def get_authenticated_processor(user_info):
    """Get or create authenticated processor instance"""
    global authenticated_processor
    
    if not authenticated_processor:
        authenticated_processor = AuthenticatedFileProcessor(user_info)
    
    return authenticated_processor