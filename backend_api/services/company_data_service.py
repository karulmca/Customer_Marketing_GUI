"""
Company Data Service
Handles business logic for company data operations
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from database_config.postgresql_config import PostgreSQLConfig
import psycopg2
import pandas as pd
from ..models.data_models import (
    CompanyDataModel, 
    CompanyDataUpdateModel, 
    CompanyDataListResponse,
    CompanyDataResponse,
    ProcessingStatus
)

logger = logging.getLogger(__name__)

class CompanyDataService:
    """Service class for company data operations"""
    
    def __init__(self):
        self.db_config = PostgreSQLConfig()
        
    def _get_connection(self):
        """Get database connection"""
        try:
            connection_params = self.db_config.get_connection_params()
            return psycopg2.connect(**connection_params)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def get_company_data_by_file(self, file_id: str, limit: int = 100, offset: int = 0) -> CompanyDataListResponse:
        """Get all company data for a specific file"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Get file info first
            cursor.execute(
                """SELECT file_name, uploaded_by, upload_date, processing_status 
                   FROM file_upload WHERE id = %s""",
                (file_id,)
            )
            file_info = cursor.fetchone()
            
            if not file_info:
                return CompanyDataListResponse(
                    success=False, 
                    data=[], 
                    total_records=0, 
                    message="File not found"
                )
            
            # Get total count
            cursor.execute(
                "SELECT COUNT(*) FROM company_data WHERE file_upload_id = %s",
                (file_id,)
            )
            total_count = cursor.fetchone()[0]
            
            # Get paginated company data
            cursor.execute(
                """SELECT id, company_name, linkedin_url, company_website, 
                          company_size, industry, revenue, file_upload_id,
                          processing_status, created_at, updated_at
                   FROM company_data 
                   WHERE file_upload_id = %s 
                   ORDER BY created_at DESC
                   LIMIT %s OFFSET %s""",
                (file_id, limit, offset)
            )
            
            records = cursor.fetchall()
            company_data = []
            
            for record in records:
                company_data.append(CompanyDataModel(
                    id=record[0],
                    company_name=record[1],
                    linkedin_url=record[2],
                    company_website=record[3],
                    company_size=record[4],
                    industry=record[5],
                    revenue=record[6],
                    file_upload_id=record[7],
                    processing_status=record[8] or ProcessingStatus.PENDING,
                    created_at=record[9],
                    updated_at=record[10]
                ))
            
            cursor.close()
            connection.close()
            
            return CompanyDataListResponse(
                success=True,
                data=company_data,
                total_records=total_count,
                file_info={
                    "file_name": file_info[0],
                    "uploaded_by": file_info[1],
                    "upload_date": file_info[2],
                    "processing_status": file_info[3]
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting company data for file {file_id}: {e}")
            return CompanyDataListResponse(
                success=False,
                data=[],
                total_records=0,
                message=f"Error retrieving data: {str(e)}"
            )
    
    async def get_company_record(self, record_id: str) -> CompanyDataResponse:
        """Get a single company data record"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """SELECT id, company_name, linkedin_url, company_website, 
                          company_size, industry, revenue, file_upload_id,
                          processing_status, created_at, updated_at
                   FROM company_data 
                   WHERE id = %s""",
                (record_id,)
            )
            
            record = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if not record:
                return CompanyDataResponse(
                    success=False,
                    message="Company record not found"
                )
            
            company_data = CompanyDataModel(
                id=record[0],
                company_name=record[1],
                linkedin_url=record[2],
                company_website=record[3],
                company_size=record[4],
                industry=record[5],
                revenue=record[6],
                file_upload_id=record[7],
                processing_status=record[8] or ProcessingStatus.PENDING,
                created_at=record[9],
                updated_at=record[10]
            )
            
            return CompanyDataResponse(
                success=True,
                data=company_data
            )
            
        except Exception as e:
            logger.error(f"Error getting company record {record_id}: {e}")
            return CompanyDataResponse(
                success=False,
                message=f"Error retrieving record: {str(e)}"
            )
    
    async def update_company_record(self, record_id: str, update_data: CompanyDataUpdateModel) -> CompanyDataResponse:
        """Update a company data record"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Build dynamic update query
            update_fields = []
            update_values = []
            
            for field, value in update_data.dict(exclude_unset=True).items():
                if value is not None:
                    update_fields.append(f"{field} = %s")
                    update_values.append(value)
            
            if not update_fields:
                return CompanyDataResponse(
                    success=False,
                    message="No fields to update"
                )
            
            # Add updated_at timestamp
            update_fields.append("updated_at = %s")
            update_values.append(datetime.now())
            update_values.append(record_id)
            
            query = f"""
                UPDATE company_data 
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING id, company_name, linkedin_url, company_website, 
                         company_size, industry, revenue, file_upload_id,
                         processing_status, created_at, updated_at
            """
            
            cursor.execute(query, update_values)
            updated_record = cursor.fetchone()
            
            if not updated_record:
                cursor.close()
                connection.close()
                return CompanyDataResponse(
                    success=False,
                    message="Company record not found"
                )
            
            connection.commit()
            cursor.close()
            connection.close()
            
            company_data = CompanyDataModel(
                id=updated_record[0],
                company_name=updated_record[1],
                linkedin_url=updated_record[2],
                company_website=updated_record[3],
                company_size=updated_record[4],
                industry=updated_record[5],
                revenue=updated_record[6],
                file_upload_id=updated_record[7],
                processing_status=updated_record[8] or ProcessingStatus.PENDING,
                created_at=updated_record[9],
                updated_at=updated_record[10]
            )
            
            return CompanyDataResponse(
                success=True,
                data=company_data,
                message="Company record updated successfully"
            )
            
        except Exception as e:
            logger.error(f"Error updating company record {record_id}: {e}")
            return CompanyDataResponse(
                success=False,
                message=f"Error updating record: {str(e)}"
            )
    
    async def delete_company_record(self, record_id: str) -> CompanyDataResponse:
        """Delete a company data record"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                "DELETE FROM company_data WHERE id = %s RETURNING company_name",
                (record_id,)
            )
            
            deleted_record = cursor.fetchone()
            
            if not deleted_record:
                cursor.close()
                connection.close()
                return CompanyDataResponse(
                    success=False,
                    message="Company record not found"
                )
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return CompanyDataResponse(
                success=True,
                message=f"Company record '{deleted_record[0]}' deleted successfully"
            )
            
        except Exception as e:
            logger.error(f"Error deleting company record {record_id}: {e}")
            return CompanyDataResponse(
                success=False,
                message=f"Error deleting record: {str(e)}"
            )