"""
Automated job runner

This script queries the database for `file_upload` rows with processing_status = 'pending',
reconstructs the uploaded data, runs the automated scraper wrappers in sequence (LinkedIn -> Revenue -> AI),
and then marks the job completed (or failed) via FileUploadProcessor.sync_processing_completion.

This runner is intentionally separate from the manual upload/process endpoints.
Run manually or wire into a scheduler.
"""
import io
import json
import base64
import logging
import os
import sys
from typing import Any

import pandas as pd

from database_config.postgresql_config import PostgreSQLConfig

logger = logging.getLogger("automated_job.runner")
logging.basicConfig(level=logging.INFO)

# Make sure scrapers path will resolve as in wrappers
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def normalize_raw_data_to_df(raw_data: Any) -> pd.DataFrame:
    """Normalize various stored raw_data formats into a pandas DataFrame.

    Accepts: bytes, dict, JSON string, base64-encoded bytes, CSV/text
    Returns: DataFrame
    Raises: ValueError on failure
    """
    import io as _io

    # Bytes (assume Excel)
    if isinstance(raw_data, (bytes, bytearray)):
        try:
            return pd.read_excel(_io.BytesIO(bytes(raw_data)))
        except Exception as e:
            # try CSV
            try:
                return pd.read_csv(_io.BytesIO(bytes(raw_data)))
            except Exception:
                raise ValueError(f"Unable to read bytes raw_data as Excel/CSV: {e}")

    # Dict (expect {'data': [...]} or records)
    if isinstance(raw_data, dict):
        if 'data' in raw_data and isinstance(raw_data['data'], list):
            return pd.DataFrame(raw_data['data'])
        # try to coerce
        return pd.DataFrame(raw_data)

    # String
    if isinstance(raw_data, str):
        # Try JSON
        try:
            parsed = json.loads(raw_data)
            return normalize_raw_data_to_df(parsed)
        except Exception:
            pass

        # Try base64 decode
        try:
            decoded = base64.b64decode(raw_data)
            return normalize_raw_data_to_df(decoded)
        except Exception:
            pass

        # Try to parse as CSV text
        try:
            return pd.read_csv(_io.StringIO(raw_data))
        except Exception as e:
            raise ValueError(f"Unable to parse string raw_data: {e}")

    # Unknown
    raise ValueError("Unsupported raw_data type for reconstruction")


def run_once(limit: int = 10):
    """
    Process pending files ONE AT A TIME to ensure proper status transitions.
    Only moves to the next file after the current one completes (success or failure).
    This prevents multiple files from being marked as 'processing' simultaneously.
    """
    cfg = PostgreSQLConfig()
    params = cfg.get_connection_params()
    import psycopg2

    conn = psycopg2.connect(**params)
    cursor = conn.cursor()

    # Use the existing FileUploadProcessor to perform the canonical processing flow
    from database_config.file_upload_processor import FileUploadProcessor

    success_count = 0
    failure_count = 0
    processed_count = 0

    # Process files ONE AT A TIME up to the limit
    for iteration in range(limit):
        # Re-query to get the next pending file (ensures we get the latest state)
        cursor.execute("""
            SELECT id, raw_data, file_name 
            FROM file_upload 
            WHERE processing_status = 'pending' 
            ORDER BY upload_date ASC 
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        
        # If no more pending files, we're done
        if not row:
            if iteration == 0:
                logger.info("No pending uploads to process.")
            else:
                logger.info(f"No more pending uploads. Processed {processed_count} file(s).")
            break
        
        file_id = row[0]
        filename = row[2] or f"file_{file_id}"
        processed_count += 1

        logger.info(f"🔄 Processing file {processed_count}/{limit}: id={file_id} filename={filename}")

        try:
            fup = FileUploadProcessor()
            # This will mark the job as started (pending -> processing), 
            # insert rows into company_data, perform scraping, 
            # and sync completion (processing -> completed/failed)
            ok = fup.process_uploaded_file(file_id)
            
            if ok:
                success_count += 1
                logger.info(f"✅ Successfully processed file {file_id} ({filename})")
            else:
                failure_count += 1
                logger.error(f"❌ Processing failed for file {file_id} ({filename})")

        except Exception as e:
            logger.exception(f"❌ Processing error for file {file_id} ({filename}): {e}")
            failure_count += 1
            # Attempt to mark failed
            try:
                fup = FileUploadProcessor()
                fup.sync_processing_completion(file_id, 'failed', 0, str(e))
            except Exception as e2:
                logger.error(f"Also failed to mark file {file_id} failed: {e2}")
        
        # Important: After each file completes, we loop back and fetch the next pending file
        # This ensures only ONE file is in 'processing' status at any time

    cursor.close()
    conn.close()

    logger.info(f"📊 Batch processing summary: Processed={processed_count}, Successful={success_count}, Failed={failure_count}")
    
    return {"success": True, "processed": processed_count, "successful": success_count, "failed": failure_count}

    cursor.close()
    conn.close()


if __name__ == '__main__':
    # Run once by default; a scheduler (cron/apscheduler) can import and call run_once()
    run_once()
