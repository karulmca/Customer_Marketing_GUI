import psycopg2
from database_config.postgresql_config import PostgreSQLConfig

cfg = PostgreSQLConfig()
conn = psycopg2.connect(**cfg.get_connection_params())
cur = conn.cursor()

# Check Test2.xlsx progress data
print("\n=== Test2.xlsx Progress Data ===")
cur.execute("""
    SELECT fu.id, fu.file_name, fu.processing_status,
           pj.total_items, pj.processed_items, pj.processed_records, 
           pj.progress, pj.status
    FROM file_upload fu 
    LEFT JOIN processing_jobs pj ON pj.file_upload_id::text = fu.id
    WHERE fu.file_name = 'Test2.xlsx'
""")
row = cur.fetchone()
if row:
    print(f"file_id: {row[0]}")
    print(f"file_name: {row[1]}")
    print(f"fu.processing_status: {row[2]}")
    print(f"pj.total_items: {row[3]}")
    print(f"pj.processed_items: {row[4]}")
    print(f"pj.processed_records: {row[5]}")
    print(f"pj.progress: {row[6]}")
    print(f"pj.status: {row[7]}")
else:
    print("No data found")

# Check what the API query returns
print("\n=== Simulating API Query ===")
cur.execute("""
    SELECT fu.id, fu.file_name, fu.upload_date, fu.uploaded_by, fu.processing_status, 
           fu.records_count, fu.file_size, fu.processing_error,
           COALESCE(pj.total_items, 0) as total_records,
           COALESCE(pj.processed_records, COALESCE(pj.processed_items, 0)) as processed_records,
           COALESCE(pj.progress, 0) as progress
    FROM file_upload fu
    LEFT JOIN processing_jobs pj ON pj.file_upload_id::text = fu.id
    WHERE fu.file_name = 'Test2.xlsx'
""")
row = cur.fetchone()
if row:
    print(f"API would return:")
    print(f"  total_records: {row[8]}")
    print(f"  processed_records: {row[9]}")
    print(f"  progress_percentage: {row[10]}")
else:
    print("No data found")

cur.close()
conn.close()
