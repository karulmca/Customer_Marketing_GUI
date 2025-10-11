# record_progress.py
from database_config.db_utils import get_database_connection

def get_processed_record_progress():
    conn = get_database_connection()
    cursor = conn.cursor()
    # Example: adjust table/column names as needed
    cursor.execute("SELECT COUNT(*) FROM company_data WHERE processing_status = 'completed'")
    processed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM company_data")
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {"processed": processed, "total": total}
