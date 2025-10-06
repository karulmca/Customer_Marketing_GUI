"""
Company Data Controller
Handles HTTP requests for company data operations
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
import logging
from ..services.company_data_service import CompanyDataService
from ..models.data_models import CompanyDataUpdateModel, CompanyDataListResponse, CompanyDataResponse

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/company-data", tags=["Company Data"])

# Service instance
company_service = CompanyDataService()

def verify_session(session_id: str):
    """Verify session - placeholder for actual session verification"""
    # Import here to avoid circular imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from auth.user_auth import UserAuthenticator
    
    authenticator = UserAuthenticator()
    return authenticator.verify_session(session_id)

@router.get("/view/{file_id}", response_model=CompanyDataListResponse)
async def view_company_data(
    file_id: str = Path(..., description="File ID to view data for"),
    session_id: str = Query(..., description="Session ID for authentication"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip")
):
    """
    View company data for a specific file with pagination
    """
    try:
        # Verify session
        verify_session(session_id)
        
        # Get company data
        result = await company_service.get_company_data_by_file(file_id, limit, offset)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing company data for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")

@router.get("/record/{record_id}", response_model=CompanyDataResponse)
async def get_company_record(
    record_id: str = Path(..., description="Company record ID"),
    session_id: str = Query(..., description="Session ID for authentication")
):
    """
    Get a single company record by ID
    """
    try:
        # Verify session
        verify_session(session_id)
        
        # Get company record
        result = await company_service.get_company_record(record_id)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company record {record_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving record: {str(e)}")

@router.put("/record/{record_id}", response_model=CompanyDataResponse)
async def update_company_record(
    record_id: str = Path(..., description="Company record ID to update"),
    update_data: CompanyDataUpdateModel = ...,
    session_id: str = Query(..., description="Session ID for authentication")
):
    """
    Update a company data record
    """
    try:
        # Verify session
        verify_session(session_id)
        
        # Update company record
        result = await company_service.update_company_record(record_id, update_data)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating company record {record_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating record: {str(e)}")

@router.delete("/record/{record_id}", response_model=CompanyDataResponse)
async def delete_company_record(
    record_id: str = Path(..., description="Company record ID to delete"),
    session_id: str = Query(..., description="Session ID for authentication")
):
    """
    Delete a company data record
    """
    try:
        # Verify session
        verify_session(session_id)
        
        # Delete company record
        result = await company_service.delete_company_record(record_id)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting company record {record_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting record: {str(e)}")