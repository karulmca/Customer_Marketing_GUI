"""
FastAPI Backend for Company Data Scraper
Exposes existing Python functionality as REST APIs for React frontend
"""

import os
import sys
import json
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import uuid
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend_api.models.data_models import LoginRequest, RegisterRequest
from typing import Optional, List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database_config'))
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from auth.user_auth import UserAuthenticator
from database_config.db_utils import get_database_connection, check_database_requirements
from database_config.config_loader import get_scheduler_interval, is_single_job_per_user_enabled

MVC_CONTROLLERS_AVAILABLE = False

app = FastAPI(
    title="Company Data Scraper API",
    description="REST API for file upload and data processing",
    version="1.0.0"
)

cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001"
]
environment = os.getenv("ENVIRONMENT", "development")
if environment == "production":
    cors_origins.extend([
        "https://company-scraper-frontend-nddn.onrender.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ])
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"🌐 CORS configured for origins: {cors_origins}")
logger.info(f"🔧 Environment: {environment}")

static_dir = os.path.join(parent_dir, "frontend", "build")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(static_dir, "static")), name="static")

security = HTTPBearer()

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker containers and load balancers"""
    try:
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
        "scheduler": "active" if 'APScheduler' in globals() else "unavailable"
    }

@app.get("/debug/pending-uploads")
async def debug_pending_uploads():
    """Debug endpoint to check pending uploads"""
    try:
        from database_config.file_upload_processor import FileUploadProcessor
        processor = FileUploadProcessor()
        all_uploads_query = (
            "SELECT id, file_name, processing_status, upload_date, uploaded_by "
            "FROM file_upload "
            "ORDER BY upload_date DESC "
            "LIMIT 10"
        )
        from database_config.postgresql_config import PostgreSQLConfig
        db_config = PostgreSQLConfig()
        all_uploads = db_config.query_to_dataframe(all_uploads_query)
        pending_df = processor.get_pending_uploads()
        return {
            "total_recent_uploads": len(all_uploads) if not all_uploads.empty else 0,
            "recent_uploads": all_uploads.to_dict('records') if not all_uploads.empty else [],
            "pending_uploads_count": len(pending_df) if pending_df is not None and not pending_df.empty else 0,
            "pending_uploads": pending_df.to_dict('records') if pending_df is not None and not pending_df.empty else []
        }
    except Exception as e:
        return {"error": str(e)}

# ...existing code...
# (You can request a full file replacement if you want all endpoints and helpers cleaned)
