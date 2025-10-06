"""
File Data Service
Handles business logic for file and data management operations
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from database_config.postgresql_config import PostgreSQLConfig
import psycopg2
from ..models.data_models import FileUploadModel, FileDataResponse, ProcessingStatus

logger = logging.getLogger(__name__)

class FileDataService:
    """Service class for file data operations"""
    
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
    
    async def get_file_statistics(self, file_id: str) -> Dict[str, Any]:
        """Get statistics for a specific file"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Get file info
            cursor.execute(
                """SELECT file_name, uploaded_by, upload_date, processing_status
                   FROM file_upload WHERE id = %s""",
                (file_id,)
            )
            file_info = cursor.fetchone()
            
            if not file_info:
                return {"success": False, "message": "File not found"}
            
            # Get processing statistics
            cursor.execute(
                """SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN processing_status = 'completed' THEN 1 END) as processed,
                    COUNT(CASE WHEN processing_status = 'failed' THEN 1 END) as failed,
                    COUNT(CASE WHEN processing_status = 'pending' THEN 1 END) as pending
                   FROM company_data WHERE file_upload_id = %s""",
                (file_id,)
            )
            
            stats = cursor.fetchone()
            cursor.close()
            connection.close()
            
            success_rate = 0.0
            if stats[0] > 0:  # total records
                success_rate = (stats[1] / stats[0]) * 100
            
            return {
                "success": True,
                "file_info": {
                    "file_name": file_info[0],
                    "uploaded_by": file_info[1],
                    "upload_date": file_info[2],
                    "processing_status": file_info[3]
                },
                "statistics": {
                    "total_records": stats[0],
                    "processed_records": stats[1],
                    "failed_records": stats[2],
                    "pending_records": stats[3],
                    "success_rate": round(success_rate, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting file statistics for {file_id}: {e}")
            return {
                "success": False,
                "message": f"Error retrieving statistics: {str(e)}"
            }
    
    async def export_processed_data(self, file_id: str) -> Dict[str, Any]:
        """Export processed data as Excel file"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Get processed company data
            cursor.execute(
                """SELECT 
                    company_name as "Company Name",
                    linkedin_url as "LinkedIn_URL",
                    company_website as "Website_URL", 
                    company_size as "Company_Size",
                    industry as "Industry",
                    revenue as "Revenue"
                   FROM company_data 
                   WHERE file_upload_id = %s 
                   AND processing_status = 'completed'
                   ORDER BY company_name""",
                (file_id,)
            )
            
            records = cursor.fetchall()
            
            if not records:
                cursor.close()
                connection.close()
                return {
                    "success": False,
                    "message": "No processed data found for this file"
                }
            
            # Create DataFrame
            columns = ["Company Name", "LinkedIn_URL", "Website_URL", "Company_Size", "Industry", "Revenue"]
            df = pd.DataFrame(records, columns=columns)
            
            # Create Excel file in memory
            from io import BytesIO
            excel_buffer = BytesIO()
            
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Processed Companies', index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Processed Companies']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            excel_buffer.seek(0)
            cursor.close()
            connection.close()
            
            return {
                "success": True,
                "data": excel_buffer.getvalue(),
                "filename": f"processed_data_{file_id}.xlsx",
                "records_count": len(records)
            }
            
        except Exception as e:
            logger.error(f"Error exporting data for file {file_id}: {e}")
            return {
                "success": False,
                "message": f"Error exporting data: {str(e)}"
            }
    
    async def reprocess_file_data(self, file_id: str) -> FileDataResponse:
        """Mark file data for reprocessing"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Reset processing status to pending
            cursor.execute(
                """UPDATE company_data 
                   SET processing_status = 'pending', updated_at = %s
                   WHERE file_upload_id = %s""",
                (datetime.now(), file_id)
            )
            
            updated_count = cursor.rowcount
            
            if updated_count == 0:
                cursor.close()
                connection.close()
                return FileDataResponse(
                    success=False,
                    message="No records found for reprocessing",
                    file_id=file_id
                )
            
            # Update file upload status
            cursor.execute(
                """UPDATE file_upload 
                   SET processing_status = 'pending'
                   WHERE id = %s""",
                (file_id,)
            )
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return FileDataResponse(
                success=True,
                message=f"Successfully marked {updated_count} records for reprocessing",
                file_id=file_id,
                total_records=updated_count
            )
            
        except Exception as e:
            logger.error(f"Error reprocessing file {file_id}: {e}")
            return FileDataResponse(
                success=False,
                message=f"Error reprocessing file: {str(e)}",
                file_id=file_id
            )
    
    async def delete_file_data(self, file_id: str) -> FileDataResponse:
        """Delete all data associated with a file"""
        try:
            connection = self._get_connection()
            connection.autocommit = False
            cursor = connection.cursor()
            
            # Get file info first
            cursor.execute(
                "SELECT file_name FROM file_upload WHERE id = %s",
                (file_id,)
            )
            file_info = cursor.fetchone()
            
            if not file_info:
                cursor.close()
                connection.close()
                return FileDataResponse(
                    success=False,
                    message="File not found",
                    file_id=file_id
                )
            
            file_name = file_info[0]
            
            # Delete from company_data table
            cursor.execute(
                "DELETE FROM company_data WHERE file_upload_id = %s",
                (file_id,)
            )
            company_data_deleted = cursor.rowcount
            
            # Delete from processing_jobs table
            cursor.execute(
                "DELETE FROM processing_jobs WHERE file_upload_id = %s",
                (file_id,)
            )
            processing_jobs_deleted = cursor.rowcount
            
            # Delete from file_upload table
            cursor.execute(
                "DELETE FROM file_upload WHERE id = %s",
                (file_id,)
            )
            file_upload_deleted = cursor.rowcount
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return FileDataResponse(
                success=True,
                message=f"Successfully deleted file '{file_name}' and all associated data",
                file_id=file_id,
                total_records=company_data_deleted
            )
            
        except Exception as e:
            logger.error(f"Error deleting file data {file_id}: {e}")
            if connection:
                connection.rollback()
                cursor.close()
                connection.close()
            return FileDataResponse(
                success=False,
                message=f"Error deleting file data: {str(e)}",
                file_id=file_id
            )