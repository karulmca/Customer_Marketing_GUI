"""
Data models for Company Data Scraper API
Pydantic models for request/response validation
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class CompanyDataModel(BaseModel):
    """Model for company data records"""
    id: Optional[str] = None
    company_name: str
    linkedin_url: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    revenue: Optional[str] = None
    file_upload_id: str
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CompanyDataUpdateModel(BaseModel):
    """Model for updating company data"""
    company_name: Optional[str] = None
    linkedin_url: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    revenue: Optional[str] = None

class FileUploadModel(BaseModel):
    """Model for file upload records"""
    id: Optional[str] = None
    file_name: str
    file_path: Optional[str] = None
    uploaded_by: str
    upload_date: Optional[datetime] = None
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    total_records: Optional[int] = None
    processed_records: Optional[int] = None
    failed_records: Optional[int] = None

class CompanyDataListResponse(BaseModel):
    """Response model for company data list"""
    success: bool
    data: List[CompanyDataModel]
    total_records: int
    file_info: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class CompanyDataResponse(BaseModel):
    """Response model for single company data record"""
    success: bool
    data: Optional[CompanyDataModel] = None
    message: Optional[str] = None

class FileDataResponse(BaseModel):
    """Response model for file data operations"""
    success: bool
    message: str
    file_id: Optional[str] = None
    total_records: Optional[int] = None
    processed_records: Optional[int] = None
    failed_records: Optional[int] = None

class UserModel(BaseModel):
    """Model for user data"""
    id: Optional[int] = None
    username: str
    email: Optional[str] = None
    role: str = "user"
    created_at: Optional[datetime] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'admin']:
            raise ValueError('Role must be either "user" or "admin"')
        return v

class UserCreateModel(BaseModel):
    """Model for creating new users"""
    username: str
    email: str
    password: str
    role: str = "user"
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'admin']:
            raise ValueError('Role must be either "user" or "admin"')
        return v

class UserUpdateModel(BaseModel):
    """Model for updating user data"""
    username: Optional[str] = None
    email: Optional[str] = None  
    role: Optional[str] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None and v not in ['user', 'admin']:
            raise ValueError('Role must be either "user" or "admin"')
        return v
        
class APIResponse(BaseModel):
    """Generic API response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
class SessionModel(BaseModel):
    """Model for session data"""
    session_id: str
    user_id: int
    username: str
    created_at: datetime
    last_accessed: datetime
    is_active: bool = True