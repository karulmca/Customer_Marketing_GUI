"""
File Data Controller
Handles HTTP requests for file data operations
"""

from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import Response
from typing import Optional, Dict, Any
import logging
from ..services.file_data_service import FileDataService
from ..models.data_models import FileDataResponse

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/file-data", tags=["File Data"])

# Service instance
file_service = FileDataService()

def verify_session(session_id: str):
    """Verify session - placeholder for actual session verification"""
    # Import here to avoid circular imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from auth.user_auth import UserAuthenticator
    
    authenticator = UserAuthenticator()
    return authenticator.verify_session(session_id)

@router.get("/statistics/{file_id}")
async def get_file_statistics(
    file_id: str = Path(..., description="File ID to get statistics for"),
    session_id: str = Query(..., description="Session ID for authentication")
) -> Dict[str, Any]:
    """
    Get processing statistics for a specific file
    """
    try:
        # Verify session
        verify_session(session_id)
        
        # Get file statistics
        result = await file_service.get_file_statistics(file_id)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file statistics for {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@router.get("/export/{file_id}")
async def export_processed_data(
    file_id: str = Path(..., description="File ID to export data for"),
    session_id: str = Query(..., description="Session ID for authentication")
):
    """
    Export processed data as Excel file
    """
    try:
        # Verify session
        verify_session(session_id)
        
        # Export data
        result = await file_service.export_processed_data(file_id)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        # Return Excel file
        return Response(
            content=result["data"],
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={result['filename']}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting data for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")

@router.post("/reprocess/{file_id}", response_model=FileDataResponse)
async def reprocess_file_data(
    file_id: str = Path(..., description="File ID to reprocess"),
    session_id: str = Query(..., description="Session ID for authentication")
):
    """
    Mark file data for reprocessing
    """
    try:
        # Verify session
        verify_session(session_id)
        
        # Reprocess file data
        result = await file_service.reprocess_file_data(file_id)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reprocessing file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error reprocessing file: {str(e)}")

@router.delete("/{file_id}", response_model=FileDataResponse)
async def delete_file_data(
    file_id: str = Path(..., description="File ID to delete"),
    session_id: str = Query(..., description="Session ID for authentication")
):
    """
    Delete file and all associated data
    """
    try:
        # Verify session
        verify_session(session_id)
        
        # Delete file data
        result = await file_service.delete_file_data(file_id)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file data {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting file data: {str(e)}")