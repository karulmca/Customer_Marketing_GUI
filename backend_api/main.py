"""
FastAPI Backend for Company Data Scraper
Exposes existing Python functionality as REST APIs for React frontend
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import sys
import json

# Add parent directory to path for imports  
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database_config'))
from file_upload_processor import FileUploadProcessor
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import uuid
import logging
import threading as _threading

# APScheduler for background scheduled jobs
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    APSCHEDULER_AVAILABLE = True
except Exception as _apex:
    APSCHEDULER_AVAILABLE = False
    print(f"⚠️ APScheduler not available: {_apex}")

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import existing functionality  
from auth.user_auth import UserAuthenticator
from database_config.db_utils import get_database_connection, check_database_requirements
from database_config.file_upload_processor import FileUploadProcessor
from database_config.config_loader import get_scheduler_interval, is_single_job_per_user_enabled

app = FastAPI(
    title="Company Data Scraper API",
    description="REST API for file upload and data processing",
    version="1.0.0"
)

# CORS middleware for React frontend
# Configure CORS origins based on environment
cors_origins = [
    "http://localhost:3000", 
    "http://localhost:3001", 
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001"
]

# Add production origins
environment = os.getenv("ENVIRONMENT", "development")
if environment == "production":
    cors_origins.extend([
        "https://company-scraper-frontend.onrender.com",
        # Add any additional production domains here
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log CORS configuration for debugging
logger.info(f"🌐 CORS configured for origins: {cors_origins}")
logger.info(f"🔧 Environment: {environment}")

# Mount static files from React build
static_dir = os.path.join(parent_dir, "frontend", "build")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(static_dir, "static")), name="static")

# Security
security = HTTPBearer()

# Health check endpoint for Docker
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker containers and load balancers"""
    try:
        # Check database connection
        conn = get_database_connection()
        if conn:
            conn.close()
            db_status = "healthy"
        else:
            db_status = "unhealthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database": db_status,
        "scheduler": "active" if APSCHEDULER_AVAILABLE else "unavailable"
    }

# Global variables
auth_system = UserAuthenticator()
active_sessions = {}  # Store active user sessions
processing_jobs = {}  # Store background processing jobs

# Scheduler globals
scheduler = None
SCHEDULER_JOB_ID = "process_pending_uploads_job"
scheduler_state = {
    "running": False,
    "job_added": False,
    "last_run": None,
    "last_result": None,
    "last_error": None,
}
_scheduler_lock = _threading.Lock()

def _ensure_scheduler():
    """Create the background scheduler if available and not yet created."""
    global scheduler
    if not APSCHEDULER_AVAILABLE:
        raise HTTPException(status_code=500, detail="APScheduler is not installed on the server")
    if scheduler is None:
        scheduler = BackgroundScheduler(timezone="UTC")
    if not scheduler.running:
        scheduler.start()
    return scheduler

def _process_pending_uploads():
    """Job: process pending uploads in file_upload table (no overlap)."""
    # Prevent overlapping runs at the function level as well
    if getattr(_process_pending_uploads, "_busy", False):
        logger.info("⏳ Skipping run; previous job still in progress")
        return
    setattr(_process_pending_uploads, "_busy", True)
    try:
        scheduler_state["running"] = True
        scheduler_state["last_error"] = None
        logger.info("🚀 Scheduler job started: processing pending file uploads")

        # Use existing FileUploadProcessor from database_config
        processor = FileUploadProcessor()

        # Get pending uploads with single job per user logic
        try:
            if is_single_job_per_user_enabled():
                pending_df = processor.get_pending_uploads_by_user_queue()
                logger.info("🔒 Using single job per user processing")
            else:
                pending_df = processor.get_pending_uploads()
                logger.info("🔓 Using multi-job processing")
        except Exception as e:
            logger.error(f"Failed to fetch pending uploads: {e}")
            scheduler_state["last_error"] = str(e)
            scheduler_state["last_run"] = datetime.now().isoformat()
            scheduler_state["last_result"] = {"success": False, "processed": 0, "error": str(e)}
            return

        if pending_df is None or pending_df.empty:
            logger.info("ℹ️ No eligible jobs found for processing")
            scheduler_state["last_run"] = datetime.now().isoformat()
            scheduler_state["last_result"] = {"success": True, "processed": 0}
            return

        logger.info(f"📋 Found {len(pending_df)} eligible job(s) for processing")
        success_count = 0
        failure_count = 0
        for _, row in pending_df.iterrows():
            file_upload_id = row.get("id")
            file_name = row.get("file_name")
            try:
                logger.info(f"🔄 Processing pending file: {file_name} (ID: {file_upload_id})")
                ok = processor.process_uploaded_file(file_upload_id)
                if ok:
                    logger.info(f"✅ Processed: {file_name} (ID: {file_upload_id})")
                    success_count += 1
                else:
                    logger.error(f"❌ Processing failed: {file_name} (ID: {file_upload_id})")
                    failure_count += 1
            except Exception as e:
                logger.error(f"❌ Error processing ID {file_upload_id}: {e}")
                failure_count += 1

        total = success_count + failure_count
        logger.info(f"📊 Scheduler batch done. Success: {success_count}, Failed: {failure_count}, Total: {total}")
        scheduler_state["last_run"] = datetime.now().isoformat()
        scheduler_state["last_result"] = {
            "success": True,
            "processed": total,
            "successful": success_count,
            "failed": failure_count,
        }
    finally:
        scheduler_state["running"] = False
        setattr(_process_pending_uploads, "_busy", False)

def _clean_for_json_serialization(obj):
    """Clean data to ensure it can be JSON serialized without encoding errors"""
    if isinstance(obj, dict):
        return {k: _clean_for_json_serialization(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_clean_for_json_serialization(item) for item in obj]
    elif isinstance(obj, bytes):
        # Convert bytes to string with error handling
        try:
            return obj.decode('utf-8')
        except UnicodeDecodeError:
            return obj.decode('utf-8', errors='replace')
    elif isinstance(obj, str):
        # Ensure string is valid UTF-8
        try:
            obj.encode('utf-8')
            return obj
        except UnicodeEncodeError:
            return obj.encode('utf-8', errors='replace').decode('utf-8')
    else:
        return obj

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    file_id: Optional[str] = None
    preview_data: Optional[Dict] = None

class ProcessingStatus(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: int
    message: str
    result: Optional[Dict] = None

class FileUploadResponse(BaseModel):
    success: bool
    file_upload_id: Optional[str] = None
    message: str
    filename: str
    status: str

class UploadedFile(BaseModel):
    id: str
    filename: str
    uploaded_by: str
    upload_date: Optional[str]
    status: str
    rows_count: Optional[int]
    processing_status: Optional[str]
    processed_at: Optional[str]

class UploadedFilesResponse(BaseModel):
    files: List[UploadedFile]
    count: int

# Authentication endpoints
@app.post("/api/auth/login")
async def login(request: LoginRequest, req: Request):
    """Login endpoint"""
    try:
        # Get client IP address
        client_ip = req.client.host if req.client else "unknown"
        
        result = auth_system.authenticate_user(request.username, request.password, client_ip)
        
        if result['success']:
            session_id = str(uuid.uuid4())
            session_data = {
                'user_info': result.get('user', result.get('user_info', {})),
                'session_token': result.get('session_token', session_id),
                'login_time': datetime.now().isoformat()
            }
            
            # Store in memory
            active_sessions[session_id] = session_data
            
            # Also store in database for persistence
            try:
                from database_config.postgresql_config import PostgreSQLConfig
                import psycopg2
                import json
                
                db_config = PostgreSQLConfig()
                connection_params = db_config.get_connection_params()
                connection = psycopg2.connect(**connection_params)
                cursor = connection.cursor()
                
                # Get user ID for the session
                user_info = session_data.get('user_info', {})
                username = user_info.get('username', 'unknown')
                
                # Find user ID
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user_result = cursor.fetchone()
                user_id = user_result[0] if user_result else None
                
                cursor.execute("""
                    INSERT INTO user_sessions (user_id, session_token, created_at, expires_at)
                    VALUES (%s, %s, NOW(), NOW() + INTERVAL '24 hours')
                    ON CONFLICT (session_token) 
                    DO UPDATE SET 
                        expires_at = EXCLUDED.expires_at,
                        last_accessed = NOW()
                """, (user_id, session_id))
                
                connection.commit()
                cursor.close()
                connection.close()
                
                print(f"✅ Session stored in database: {session_id}")
                
            except Exception as db_error:
                print(f"⚠️ Warning: Could not store session in database: {str(db_error)}")
                # Continue anyway - memory session still works
            
            return {
                "success": True,
                "message": "Login successful",
                "session_id": session_id,
                "user_info": result.get('user', result.get('user_info', {}))
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get('message', 'Login failed')
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """Register new user endpoint"""
    try:
        result = auth_system.register(request.username, request.password, request.email)
        
        if result['success']:
            return {
                "success": True,
                "message": "User registered successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Registration failed')
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration error: {str(e)}"
        )

@app.post("/api/auth/logout")
async def logout(session_id: str):
    """Logout endpoint"""
    if session_id in active_sessions:
        del active_sessions[session_id]
    
    return {"success": True, "message": "Logged out successfully"}

@app.get("/api/debug/sessions")
async def debug_sessions():
    """Debug endpoint to check active sessions"""
    return {
        "active_sessions": list(active_sessions.keys()),
        "session_count": len(active_sessions)
    }

# Helper function to verify session
def verify_session(session_id: str):
    """Verify active session - check database first, then memory"""
    print(f"DEBUG: Verifying session_id: {session_id}")
    print(f"DEBUG: Active sessions in memory: {list(active_sessions.keys())}")
    
    # First check memory (fast path)
    if session_id in active_sessions:
        return active_sessions[session_id]
    
    # If not in memory, check database (slow path but persistent)
    try:
        from database_config.postgresql_config import PostgreSQLConfig
        import psycopg2
        
        db_config = PostgreSQLConfig()
        connection_params = db_config.get_connection_params()
        connection = psycopg2.connect(**connection_params)
        cursor = connection.cursor()
        
        # Check if session exists in database and is still valid
        cursor.execute("""
            SELECT us.user_id, us.created_at, u.username, u.email, u.role
            FROM user_sessions us
            JOIN users u ON us.user_id = u.id
            WHERE us.session_token = %s 
            AND us.expires_at > NOW()
        """, (session_id,))
        
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if result:
            user_id, created_at, username, email, role = result
            session_data = {
                'user_info': {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'role': role
                },
                'session_token': session_id,
                'login_time': created_at.isoformat()
            }
            
            # Restore session to memory
            active_sessions[session_id] = session_data
            print(f"✅ Session restored from database: {session_id}")
            return session_data
        else:
            print(f"❌ Session not found in database: {session_id}")
            
    except Exception as e:
        print(f"❌ Error checking database session: {str(e)}")
    
    # Session not found anywhere
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired session. Please login again."
    )

# File upload endpoints
@app.post("/api/files/upload")
async def upload_file(
    session_id: str,
    file: UploadFile = File(...)
):
    """Upload Excel file for processing"""
    try:
        # Verify session
        session = verify_session(session_id)
        
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only Excel files (.xlsx, .xls) are supported"
            )
        
        # Read file content directly into memory (NO local storage)
        file_id = str(uuid.uuid4())
        content = await file.read()
        
        # Read and preview file directly from memory
        try:
            import io
            df = pd.read_excel(io.BytesIO(content))
            
            # Clean the data for JSON serialization with robust handling
            def clean_value(value):
                """Clean a single value for JSON serialization"""
                if value is None:
                    return None
                elif pd.isna(value):
                    return None
                elif isinstance(value, (int, np.integer)):
                    return int(value)
                elif isinstance(value, (float, np.floating)):
                    if np.isfinite(value):
                        return float(value)
                    else:
                        return None
                elif isinstance(value, str):
                    return str(value)
                elif hasattr(value, 'isoformat'):  # datetime objects
                    return value.isoformat()
                else:
                    return str(value)
            
            # Get sample data with robust cleaning
            sample_records = []
            if len(df) > 0:
                for _, row in df.head(5).iterrows():
                    clean_record = {}
                    for col in df.columns:
                        clean_record[str(col)] = clean_value(row[col])
                    sample_records.append(clean_record)
            
            preview_data = {
                "filename": file.filename,
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "column_names": [str(col) for col in df.columns.tolist()],
                "sample_data": sample_records
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading Excel file: {str(e)}"
            )
        
        # Save file to database directly
        db_file_id = None
        try:
            from database_config.postgresql_config import PostgreSQLConfig
            import psycopg2
            import json
            
            db_config = PostgreSQLConfig()
            connection_params = db_config.get_connection_params()
            connection = psycopg2.connect(**connection_params)
            
            cursor = connection.cursor()
            
            # Prepare data for database insertion
            username = session['user_info'].get('username', 'API_User')
            raw_data = {
                "columns": [str(col) for col in df.columns.tolist()],
                "data": sample_records[:100],  # Store first 100 records as sample
                "metadata": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "upload_timestamp": datetime.now().isoformat(),
                    "file_extension": os.path.splitext(file.filename)[1].lower()
                }
            }
            
            # Insert file record
            cursor.execute("""
                INSERT INTO file_upload 
                (file_name, file_path, file_size, original_columns, raw_data, 
                 uploaded_by, processing_status, records_count, file_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                file.filename,
                "database_storage",  # No file path, stored in database
                len(content),  # File size from content length
                json.dumps([str(col) for col in df.columns.tolist()]),
                json.dumps(raw_data),
                username,
                'uploaded',
                len(df),
                str(hash(str(content) + str(datetime.now())))  # Hash from content
            ))
            
            db_file_id = cursor.fetchone()[0]
            connection.commit()
            cursor.close()
            connection.close()
            
            print(f"✅ File saved to database with ID: {db_file_id}")
            
        except Exception as db_error:
            print(f"❌ Database save error: {str(db_error)}")
            db_file_id = None
        
        # Store file info for processing (NO local storage)
        processing_jobs[file_id] = {
            "file_content": content,  # Store content in memory instead of file path
            "filename": file.filename,
            "user_info": session['user_info'],
            "session_token": session['session_token'],
            "status": "uploaded",
            "progress": 0,
            "message": f"File uploaded successfully{' and saved to database' if db_file_id else ' (database save failed)'}",
            "db_file_id": db_file_id  # Link to database record
        }
        
        return FileUploadResponse(
            success=True,
            message="File uploaded successfully",
            file_id=file_id,
            preview_data=preview_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload error: {str(e)}"
        )

@app.post("/api/files/process/{file_id}")
async def process_file(
    file_id: str,
    session_id: str,
    scraping_enabled: bool = True,
    ai_analysis_enabled: bool = False
):
    """Start file processing in background"""
    try:
        # Verify session
        session = verify_session(session_id)
        
        if file_id not in processing_jobs:
            # Try to reconstruct job from database if not in memory
            print(f"🔍 File {file_id} not in memory, checking database...")
            try:
                from database_config.postgresql_config import PostgreSQLConfig
                import psycopg2
                
                db_config = PostgreSQLConfig()
                connection_params = db_config.get_connection_params()
                connection = psycopg2.connect(**connection_params)
                cursor = connection.cursor()
                
                # Find the file in database by checking if db_file_id matches our file_id
                cursor.execute("SELECT file_name, file_path FROM file_upload WHERE id = %s", (file_id,))
                result = cursor.fetchone()
                
                if result:
                    # Reconstruct job from database info - create temp file from database content
                    cursor.execute("SELECT raw_data FROM file_upload WHERE id = %s", (file_id,))
                    raw_data_result = cursor.fetchone()
                    
                    if raw_data_result and raw_data_result[0]:
                        import json
                        import io
                        
                        # Reconstruct file content from database (NO temporary files)
                        raw_data = raw_data_result[0]  # Already a dict/object, no need to parse
                        if isinstance(raw_data, str):
                            raw_data = json.loads(raw_data)  # Only parse if it's a string
                        df_reconstructed = pd.DataFrame(raw_data['data'])
                        
                        # Convert DataFrame back to Excel content in memory
                        excel_buffer = io.BytesIO()
                        df_reconstructed.to_excel(excel_buffer, index=False)
                        excel_content = excel_buffer.getvalue()
                        excel_buffer.close()
                        
                        # Reconstruct job from database info (NO file paths)
                        processing_jobs[file_id] = {
                            "file_content": excel_content,  # Store content in memory
                            "filename": result[0],
                            "user_info": session['user_info'],
                            "session_token": session['session_token'],
                            "status": "uploaded",
                            "progress": 0,
                            "message": "File reconstructed from database",
                            "db_file_id": file_id
                        }
                        print(f"✅ Reconstructed job for file: {result[0]}")
                    else:
                        cursor.close()
                        connection.close()
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="File data not found in database"
                        )
                else:
                    cursor.close()
                    connection.close()
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="File not found in database"
                    )
                    
                cursor.close()
                connection.close()
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"❌ Error reconstructing job: {str(e)}")
                print(f"🔍 Full error details: {error_details}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"File reconstruction failed: {str(e)}"
                )
        
        job = processing_jobs[file_id]
        
        if job["status"] == "processing":
            return {"message": "File is already being processed"}
        
        # Update job status
        job["status"] = "processing"
        job["progress"] = 10
        job["message"] = "Starting file processing..."
        
        # Update database status to processing
        try:
            file_processor = FileUploadProcessor()
            file_processor.update_processing_status(file_id, 'processing')
            print(f"✅ Database status updated to 'processing' for file: {file_id}")
        except Exception as db_error:
            print(f"❌ Failed to update database status to processing: {db_error}")
        
        # Start background processing
        def background_process():
            try:
                print(f"🔄 Starting background processing for file: {job['filename']}")
                
                # Import the company processor with proper path
                sys.path.insert(0, os.path.dirname(__file__))
                from company_processor import CompanyDataProcessor
                
                print("✅ CompanyDataProcessor imported successfully")
                
                # Initialize processor
                processor = CompanyDataProcessor()
                print("✅ Processor initialized")
                
                # Progress callback to update job status
                def update_progress(percent: int, message: str):
                    job["progress"] = percent
                    job["message"] = message
                
                # Process the file (using content from memory, NO file paths)
                print(f"🔄 Starting file processing with scraping_enabled={scraping_enabled}")
                result = processor.process_file(
                    file_content=job.get("file_content"),  # Use content from memory
                    filename=job["filename"],
                    scraping_enabled=scraping_enabled,
                    ai_analysis_enabled=ai_analysis_enabled,
                    progress_callback=update_progress
                )
                print(f"✅ Processing completed with result: {result['success']}")
                
                if result["success"]:
                    job["progress"] = 100
                    job["status"] = "completed"
                    job["message"] = result["summary"]
                    job["result"] = result
                    
                    # Update database status
                    try:
                        file_processor = FileUploadProcessor()
                        processed_count = result.get('processed_rows', 0)
                        file_processor.sync_processing_completion(file_id, 'completed', processed_count)
                        print(f"✅ Database status synced to 'completed' for file: {file_id} ({processed_count} records)")
                    except Exception as db_error:
                        print(f"❌ Failed to sync database status: {db_error}")
                        
                else:
                    job["status"] = "failed"
                    job["message"] = f"Processing failed: {result.get('error', 'Unknown error')}"
                    job["progress"] = 0
                    job["result"] = result
                    
                    # Update database status
                    try:
                        file_processor = FileUploadProcessor()
                        error_msg = result.get('error', 'Unknown error')
                        file_processor.sync_processing_completion(file_id, 'failed', 0, error_msg)
                        print(f"✅ Database status synced to 'failed' for file: {file_id}")
                    except Exception as db_error:
                        print(f"❌ Failed to sync database status: {db_error}")
                
            except Exception as e:
                print(f"❌ Background processing error: {str(e)}")
                print(f"❌ Error type: {type(e)}")
                import traceback
                print(f"❌ Full traceback: {traceback.format_exc()}")
                job["status"] = "failed"
                job["message"] = f"Processing failed: {str(e)}"
                job["progress"] = 0
                
                # Update database status for processing errors
                try:
                    file_processor = FileUploadProcessor()
                    file_processor.sync_processing_completion(file_id, 'failed', 0, str(e))
                    print(f"✅ Database status synced to 'failed' for file: {file_id}")
                except Exception as db_error:
                    print(f"❌ Failed to sync database status: {db_error}")
        
        # Start background thread
        threading.Thread(target=background_process, daemon=True).start()
        
        return {"success": True, "message": "Processing started", "job_id": file_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing error: {str(e)}"
        )

@app.get("/api/files/status/{file_id}")
async def get_processing_status(file_id: str, session_id: str):
    """Get file processing status"""
    try:
        # Verify session
        verify_session(session_id)
        
        if file_id not in processing_jobs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        job = processing_jobs[file_id]
        
        # Clean the result data to ensure UTF-8 compatibility
        result_data = job.get("result")
        if result_data:
            # Convert any bytes or non-UTF-8 strings to safe UTF-8 strings
            result_data = _clean_for_json_serialization(result_data)
        
        # Also clean the message field
        message = _clean_for_json_serialization(job["message"])
        
        return ProcessingStatus(
            job_id=file_id,
            status=job["status"],
            progress=job["progress"],
            message=message,
            result=result_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check error: {str(e)}"
        )

@app.get("/api/files/download/{file_id}")
async def download_processed_file(file_id: str, session_id: str):
    """Download processed file"""
    from fastapi.responses import FileResponse
    try:
        # Verify session
        verify_session(session_id)
        
        if file_id not in processing_jobs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        job = processing_jobs[file_id]
        
        if job["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File processing not completed"
            )
        
        result = job.get("result", {})
        output_content = result.get("output_content")
        
        if not output_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processed file content not found"
            )
        
        # Return file content directly from memory (NO local files)
        from fastapi.responses import Response
        return Response(
            content=output_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={result.get('output_file', 'processed_file.xlsx')}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download error: {str(e)}"
        )

@app.get("/api/files/download-processed/{file_id}")
async def download_processed_file_with_linkedin(file_id: str, session_id: str):
    """Download processed file with LinkedIn enrichment data in Excel format"""
    try:
        # Verify session
        verify_session(session_id)
        
        # Get database connection
        db_connection = get_database_connection("postgresql")
        if not db_connection:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection failed"
            )
        
        # Ensure database connection is established
        if not db_connection.connect():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to connect to database"
            )
        
        # Connect to database
        if not db_connection.connect():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to establish database connection"
            )
        
        # Query processed company data with LinkedIn enrichment
        query = f"""
        SELECT 
            company_name as "Company Name",
            linkedin_url as "LinkedIn_URL",
            company_website as "Website_URL", 
            company_size as "Company_Size",
            industry as "Industry",
            revenue as "Revenue"
        FROM company_data 
        WHERE file_upload_id = '{file_id}' 
        AND processing_status = 'completed'
        ORDER BY company_name
        """
        
        logger.info(f"Executing query for file_id: {file_id}")
        result_df = db_connection.query_to_dataframe(query)
        
        if result_df is None or result_df.empty:
            logger.warning(f"No processed data found for file_id: {file_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No processed data found for this file"
            )
        
        logger.info(f"Found {len(result_df)} processed records for file_id: {file_id}")
        
        # Create Excel file in memory
        from io import BytesIO
        import openpyxl
        from openpyxl.utils.dataframe import dataframe_to_rows
        from openpyxl.styles import Font, PatternFill, Alignment
        
        # Create workbook and worksheet
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Processed Company Data"
        
        # Add data to worksheet
        for r in dataframe_to_rows(result_df, index=False, header=True):
            ws.append(r)
        
        # Style the header row
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to BytesIO
        excel_buffer = BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        
        # Get original filename for the processed file name
        file_query = f"SELECT original_filename FROM file_upload WHERE id = '{file_id}'"
        file_result = db_connection.query_to_dataframe(file_query)
        original_filename = "processed_data.xlsx"
        if file_result is not None and not file_result.empty:
            original_name = file_result.iloc[0]['original_filename']
            if original_name and isinstance(original_name, str):
                name_parts = original_name.rsplit('.', 1)
                original_filename = f"processed_{name_parts[0]}.xlsx"
            else:
                logger.warning(f"Original filename is None or invalid for file_id: {file_id}")
        else:
            logger.warning(f"No file upload record found for file_id: {file_id}")
        
        # Return Excel file
        from fastapi.responses import Response
        return Response(
            content=excel_buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={original_filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download processed file error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download error: {str(e)}"
        )

@app.get("/api/database/status")
async def database_status(session_id: str):
    """Check database connection status with detailed information"""
    try:
        # Verify session
        verify_session(session_id)
        
        # Get database configuration details
        from database_config.postgresql_config import PostgreSQLConfig
        db_config = PostgreSQLConfig()
        config_data = db_config.get_connection_params()
        
        # Check database connection
        try:
            # Get a direct database connection using psycopg2
            import psycopg2
            connection_params = db_config.get_connection_params()
            connection = psycopg2.connect(**connection_params)
            
            if connection:
                # Get database version info
                cursor = connection.cursor()
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()[0]
                cursor.close()
                connection.close()
                
                return {
                    "status": "connected",
                    "message": "Database connection successful",
                    "details": {
                        "host": config_data.get("host", "Unknown"),
                        "port": config_data.get("port", "Unknown"),
                        "database": config_data.get("database", "Unknown"),
                        "user": config_data.get("user", "Unknown"),
                        "version": db_version.split(" on ")[0] if " on " in db_version else db_version,
                        "connection_type": "PostgreSQL"
                    }
                }
            else:
                return {
                    "status": "disconnected",
                    "message": "Database connection failed",
                    "details": {
                        "host": config_data.get("host", "Unknown"),
                        "port": config_data.get("port", "Unknown"),
                        "database": config_data.get("database", "Unknown"),
                        "connection_type": "PostgreSQL"
                    }
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Database error: {str(e)}",
                "details": {
                    "host": config_data.get("host", "Unknown"),
                    "port": config_data.get("port", "Unknown"),
                    "database": config_data.get("database", "Unknown"),
                    "connection_type": "PostgreSQL",
                    "error": str(e)
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database status error: {str(e)}"
        )

@app.get("/api/files/list")
async def list_uploaded_files(session_id: str):
    """List files uploaded to the database"""
    try:
        # Verify session
        verify_session(session_id)
        
        # Get database connection
        from database_config.postgresql_config import PostgreSQLConfig
        import psycopg2
        
        db_config = PostgreSQLConfig()
        connection_params = db_config.get_connection_params()
        connection = psycopg2.connect(**connection_params)
        
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, file_name, upload_date, uploaded_by, processing_status, 
                   records_count, file_size, processing_error
            FROM file_upload 
            ORDER BY upload_date DESC 
            LIMIT 50
        """)
        
        files = cursor.fetchall()
        cursor.close()
        connection.close()
        
        file_list = []
        for file_row in files:
            file_list.append({
                "id": file_row[0],
                "file_name": file_row[1],
                "upload_date": file_row[2].isoformat() if file_row[2] else None,
                "uploaded_by": file_row[3],
                "processing_status": file_row[4],
                "records_count": file_row[5],
                "file_size": file_row[6],
                "processing_error": file_row[7]
            })
        
        return {
            "success": True,
            "files": file_list,
            "total_files": len(file_list)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving files: {str(e)}"
        )

@app.get("/api/debug/jobs")
async def debug_jobs(session_id: str):
    """Debug endpoint to check processing jobs"""
    verify_session(session_id)
    return {
        "total_jobs": len(processing_jobs),
        "job_ids": list(processing_jobs.keys()),
        "jobs": {k: {
            "status": v.get("status"),
            "progress": v.get("progress"),
            "message": v.get("message"),
            "filename": v.get("filename")
        } for k, v in processing_jobs.items()}
    }

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the React app"""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "build")
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read(), status_code=200)
    else:
        return HTMLResponse(content="<h1>Company Data Scraper API</h1><p>React frontend not built. Run 'npm run build' in the frontend directory.</p>", status_code=200)

def validate_file_headers(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Validate that uploaded file has correct headers matching our template"""
    try:
        import io
        
        # Expected headers (standardized format - preferred)
        required_headers = ['Company Name', 'LinkedIn_URL']
        optional_headers = ['Website_URL', 'Company_Size', 'Industry', 'Revenue']
        all_expected_headers = required_headers + optional_headers
        
        # Alternative naming conventions (for backward compatibility)
        header_alternatives = {
            'Company Name': ['Company_Name', 'company_name'],
            'LinkedIn_URL': ['Company Linkedin', 'linkedin_url', 'Company_Linkedin'],
            'Website_URL': ['Website', 'Company_Website', 'company_website'],
            'Company_Size': ['Size', 'company_size'],
            'Industry': ['industry', 'Company_Industry'],
            'Revenue': ['company_revenue', 'Company_Revenue']
        }
        
        # Read file headers
        if filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file_content))
        elif filename.lower().endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            return {"valid": False, "error": "Unsupported file format"}
        
        file_headers = list(df.columns)
        
        # Check for required headers
        missing_required = []
        found_headers = {}
        
        for required in required_headers:
            found = False
            if required in file_headers:
                found_headers[required] = required
                found = True
            else:
                # Check alternatives
                alternatives = header_alternatives.get(required, [])
                for alt in alternatives:
                    if alt in file_headers:
                        found_headers[required] = alt
                        found = True
                        break
            
            if not found:
                missing_required.append(required)
        
        # Check for optional headers
        found_optional = []
        for optional in optional_headers:
            if optional in file_headers:
                found_optional.append(optional)
            else:
                alternatives = header_alternatives.get(optional, [])
                for alt in alternatives:
                    if alt in file_headers:
                        found_optional.append(optional)
                        break
        
        # Check for unexpected headers
        recognized_headers = set()
        for expected in all_expected_headers:
            if expected in file_headers:
                recognized_headers.add(expected)
            alternatives = header_alternatives.get(expected, [])
            for alt in alternatives:
                if alt in file_headers:
                    recognized_headers.add(alt)
        
        unexpected_headers = [h for h in file_headers if h not in recognized_headers]
        
        if missing_required:
            return {
                "valid": False,
                "error": f"Missing required columns: {', '.join(missing_required)}. For best results, please download and use our standardized Excel template which includes the exact column names expected by the system.",
                "missing_required": missing_required,
                "found_headers": file_headers,
                "expected_headers": all_expected_headers,
                "recommendation": "Download the standardized template for optimal compatibility"
            }
        
        return {
            "valid": True,
            "found_required": list(found_headers.keys()),
            "found_optional": found_optional,
            "unexpected_headers": unexpected_headers,
            "total_rows": len(df),
            "header_mapping": found_headers
        }
        
    except Exception as e:
        return {"valid": False, "error": f"Error validating file: {str(e)}"}

@app.post("/api/files/validate-headers")
async def validate_file_headers_endpoint(file: UploadFile = File(...), session_id: str = ""):
    """Validate file headers without uploading - for immediate user feedback"""
    try:
        # Verify session
        verify_session(session_id)
        
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="Only Excel and CSV files are supported")
        
        # Read file content for validation
        file_content = await file.read()
        
        # Validate headers
        validation_result = validate_file_headers(file_content, file.filename)
        
        return {
            "success": True,
            "validation": validation_result,
            "filename": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Validation error: {str(e)}"
        )

@app.post("/api/files/upload-json")
async def upload_file_as_json(file: UploadFile = File(...), session_id: str = ""):
    """Upload file as JSON to file_upload table (matches original GUI workflow)"""
    try:
        # Verify session
        verify_session(session_id)
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="Only Excel and CSV files are supported")
        
        # Read file content for validation
        file_content = await file.read()
        
        # Validate headers before processing
        validation_result = validate_file_headers(file_content, file.filename)
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file format: {validation_result['error']}"
            )
        
        # File content already read for validation, continue with processing
        # Initialize file processor (from original GUI logic)
        try:
            file_processor = FileUploadProcessor()
            
            # Create temporary file for processing (like original GUI)
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Upload as JSON using original logic
                uploaded_by = active_sessions.get(session_id, {}).get("username", "Web_User")
                file_upload_id = file_processor.upload_file_as_json(temp_file_path, uploaded_by, original_filename=file.filename)
                
                if file_upload_id:
                    return {
                        "success": True,
                        "file_upload_id": file_upload_id,
                        "message": f"File uploaded as JSON successfully (ID: {file_upload_id})",
                        "filename": file.filename,
                        "status": "pending_processing"
                    }
                else:
                    raise HTTPException(status_code=500, detail="Failed to upload file as JSON")
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except ImportError as e:
            raise HTTPException(status_code=500, detail=f"File processor not available: {e}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/files/upload-and-process")
async def upload_and_process_file(file: UploadFile = File(...), session_id: str = ""):
    """Upload file as JSON and immediately process it (matches original GUI workflow)"""
    try:
        # Verify session
        verify_session(session_id)
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="Only Excel and CSV files are supported")
        
        # Read file content
        file_content = await file.read()
        
        # Validate headers before processing
        validation_result = validate_file_headers(file_content, file.filename)
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file format: {validation_result['error']}"
            )
        
        # Initialize file processor (from original GUI logic)
        try:
            file_processor = FileUploadProcessor()
            
            # Create temporary file for processing (like original GUI)
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Upload as JSON using original logic
                uploaded_by = active_sessions.get(session_id, {}).get("username", "Web_User")
                file_upload_id = file_processor.upload_file_as_json(temp_file_path, uploaded_by, original_filename=file.filename)
                
                if file_upload_id:
                    # Immediately process it (like original GUI's "Upload & Process Now")
                    success = file_processor.process_uploaded_file(file_upload_id)
                    
                    if success:
                        return {
                            "success": True,
                            "file_upload_id": file_upload_id,
                            "message": f"File uploaded and processed successfully (ID: {file_upload_id})",
                            "filename": file.filename,
                            "status": "completed"
                        }
                    else:
                        return {
                            "success": False,
                            "file_upload_id": file_upload_id,
                            "message": f"File uploaded but processing failed (ID: {file_upload_id})",
                            "filename": file.filename,
                            "status": "processing_failed"
                        }
                else:
                    raise HTTPException(status_code=500, detail="Failed to upload file as JSON")
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except ImportError as e:
            raise HTTPException(status_code=500, detail=f"File processor not available: {e}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload and processing failed: {str(e)}")

@app.get("/api/files/uploads")
async def get_uploaded_files(session_id: str):
    """Get list of uploaded files from file_upload table (matches original GUI workflow)"""
    try:
        # Verify session
        verify_session(session_id)

        # Query real uploaded files from database and adapt to UI's expected shape
        try:
            from database_config.postgresql_config import PostgreSQLConfig
            import psycopg2

            db_config = PostgreSQLConfig()
            connection_params = db_config.get_connection_params()
            connection = psycopg2.connect(**connection_params)

            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, file_name, upload_date, uploaded_by, processing_status, 
                       records_count
                FROM file_upload 
                ORDER BY upload_date DESC 
                LIMIT 50
                """
            )

            rows = cursor.fetchall()
            cursor.close()
            connection.close()

            files = []
            for r in rows:
                files.append({
                    "id": r[0],
                    "filename": r[1],
                    "upload_date": r[2].isoformat() if r[2] else None,
                    "uploaded_by": r[3],
                    "status": r[4],
                    "processing_status": r[4],
                    "total_rows": r[5]
                })

            return {"files": files, "count": len(files)}

        except ImportError as e:
            # If database layer isn't available, return an empty list rather than mock data
            logger.warning(f"Database module not available for uploads list: {e}")
            return {"files": [], "count": 0, "error": str(e)}
        except Exception as e:
            # On any DB error, return empty list so UI reflects no data when DB is empty/unreachable
            logger.exception("Failed to query uploaded files from database")
            return {"files": [], "count": 0, "error": str(e)}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get uploaded files: {str(e)}")


# -------------------- Scheduler control endpoints --------------------
@app.post("/api/jobs/process-pending")
async def run_process_pending_now(session_id: str = ""):
    """Run processing of pending uploads immediately in background (one-shot)."""
    # Verify session (optional: could enforce admin)
    if session_id:
        try:
            verify_session(session_id)
        except Exception:
            # proceed even if session invalid; comment to enforce
            pass

    # Fire-and-forget thread to run the job once
    _threading.Thread(target=_process_pending_uploads, daemon=True).start()
    return {"success": True, "message": "Pending uploads processing started"}


@app.post("/api/jobs/scheduler/start")
async def start_scheduler(session_id: str = "", mode: str = "cron", interval_minutes: int = 2):
    """Start APScheduler job that processes pending uploads periodically.

    mode: 'cron' (default, runs every 2 minutes) or 'interval' (every N minutes)
    interval_minutes: used only for interval mode
    """
    if session_id:
        try:
            verify_session(session_id)
        except Exception:
            pass

    with _scheduler_lock:
        sched = _ensure_scheduler()

        # Remove existing job if present to avoid duplicates
        try:
            existing = sched.get_job(SCHEDULER_JOB_ID)
            if existing:
                sched.remove_job(SCHEDULER_JOB_ID)
        except Exception:
            pass

        if mode == "interval":
            trigger = IntervalTrigger(minutes=max(1, int(interval_minutes)))
            schedule_desc = f"every {max(1, int(interval_minutes))} minutes"
        else:
            # Default cron every 2 minutes
            scheduler_interval = get_scheduler_interval()
            trigger = CronTrigger(minute=f"*/{scheduler_interval}")
            schedule_desc = "every 2 minutes"

        sched.add_job(
            _process_pending_uploads,
            trigger=trigger,
            id=SCHEDULER_JOB_ID,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,
            replace_existing=True,
        )
        scheduler_state["job_added"] = True

        next_run = sched.get_job(SCHEDULER_JOB_ID).next_run_time.isoformat() if sched.get_job(SCHEDULER_JOB_ID) and sched.get_job(SCHEDULER_JOB_ID).next_run_time else None

    return {
        "success": True,
        "message": f"Scheduler started ({schedule_desc})",
        "next_run": next_run,
    }


@app.post("/api/jobs/scheduler/stop")
async def stop_scheduler(session_id: str = ""):
    """Stop the periodic scheduler job (does not stop a currently running run)."""
    if session_id:
        try:
            verify_session(session_id)
        except Exception:
            pass

    with _scheduler_lock:
        if scheduler and scheduler.running:
            try:
                if scheduler.get_job(SCHEDULER_JOB_ID):
                    scheduler.remove_job(SCHEDULER_JOB_ID)
                    scheduler_state["job_added"] = False
                # Keep scheduler alive; do not shutdown to avoid uvicorn reload issues
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {e}")
        else:
            scheduler_state["job_added"] = False

    return {"success": True, "message": "Scheduler stopped"}


@app.get("/api/jobs/scheduler/status")
async def scheduler_status():
    """Return scheduler and job status for UI diagnostics."""
    job_info = None
    if scheduler and scheduler.running:
        try:
            job = scheduler.get_job(SCHEDULER_JOB_ID)
            if job:
                job_info = {
                    "id": job.id,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                }
        except Exception:
            job_info = None
    return {
        "scheduler_running": bool(scheduler and scheduler.running),
        "job_present": bool(job_info is not None),
        "job": job_info,
        "state": scheduler_state,
    }



@app.get("/api/sample-template")
async def download_sample_template():
    """Download sample Excel template for company data upload"""
    try:
        sample_file_path = os.path.join(parent_dir, "assets", "sample_company_data.xlsx")
        
        if not os.path.exists(sample_file_path):
            # Create sample file if it doesn't exist with standardized columns
            import pandas as pd
            sample_data = {
                'Company Name': [
                    'Acme Corporation',
                    'Tech Solutions Ltd', 
                    'Global Industries',
                    'StartupXYZ',
                    'Enterprise Corp'
                ],
                'LinkedIn_URL': [
                    'https://www.linkedin.com/company/acme-corp',
                    'https://www.linkedin.com/company/tech-solutions',
                    'https://www.linkedin.com/company/global-industries',
                    'https://www.linkedin.com/company/startupxyz',
                    'https://www.linkedin.com/company/enterprise-corp'
                ],
                'Website_URL': [
                    'https://www.acme.com',
                    'https://www.techsolutions.com',
                    'https://www.globalind.com',
                    'https://www.startupxyz.com',
                    'https://www.enterprise.com'
                ],
                'Company_Size': [
                    '51-200 employees',
                    '11-50 employees',
                    '201-500 employees', 
                    '1-10 employees',
                    '1001-5000 employees'
                ],
                'Industry': [
                    'Technology',
                    'Software Development',
                    'Manufacturing',
                    'Fintech',
                    'Consulting'
                ],
                'Revenue': [
                    '$5M',
                    '$2M',
                    '$50M',
                    '$500K', 
                    '$200M'
                ]
            }
            df = pd.DataFrame(sample_data)
            
            # Ensure assets directory exists
            assets_dir = os.path.join(parent_dir, "assets")
            os.makedirs(assets_dir, exist_ok=True)
            
            df.to_excel(sample_file_path, index=False, sheet_name='Company Data')
            logger.info("Sample template file created with standardized columns")
        
        return FileResponse(
            path=sample_file_path,
            filename="company_data_template.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        logger.error(f"Error creating sample template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sample template: {str(e)}"
        )

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting up application services...")
    
    # Auto-start scheduler with config settings
    try:
        interval_minutes = get_scheduler_interval()
        logger.info(f"📅 Auto-starting scheduler with {interval_minutes} minute interval")
        
        # Start the scheduler automatically
        _ensure_scheduler()
        if scheduler and not scheduler.running:
            scheduler.start()
            logger.info("✅ Scheduler started successfully")
        
        # Add the job with config-based interval
        with _scheduler_lock:
            global scheduler_state
            if APSCHEDULER_AVAILABLE and scheduler:
                try:
                    # Remove existing job if any
                    try:
                        scheduler.remove_job(SCHEDULER_JOB_ID)
                    except:
                        pass
                    
                    # Add job with interval from config
                    scheduler.add_job(
                        _process_pending_uploads,
                        IntervalTrigger(minutes=interval_minutes),
                        id=SCHEDULER_JOB_ID,
                        replace_existing=True,
                        max_instances=1
                    )
                    
                    scheduler_state["running"] = True
                    scheduler_state["job_added"] = True
                    logger.info(f"✅ Scheduled job added: process pending uploads every {interval_minutes} minutes")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to add scheduled job: {e}")
                    scheduler_state["last_error"] = str(e)
            else:
                logger.warning("⚠️ APScheduler not available - jobs will need to be processed manually")
                
    except Exception as e:
        logger.error(f"❌ Failed to auto-start scheduler: {e}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "scheduler_running": scheduler_state.get("running", False) if APSCHEDULER_AVAILABLE else False
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)