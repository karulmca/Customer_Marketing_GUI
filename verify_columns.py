import psycopg2
from database_config.postgresql_config import PostgreSQLConfig

cfg = PostgreSQLConfig()
conn = psycopg2.connect(**cfg.get_connection_params())
cur = conn.cursor()

# Check if progress columns exist in file_upload
print("\n=== Checking file_upload table columns ===")
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'file_upload'
    ORDER BY ordinal_position
""")
columns = [row[0] for row in cur.fetchall()]
print(f"All columns: {', '.join(columns)}")

print("\n=== Checking for progress-related columns ===")
progress_cols = ['total_records', 'processed_records', 'progress_percentage']
for col in progress_cols:
    exists = col in columns
    print(f"{col}: {'✅ EXISTS' if exists else '❌ MISSING'}")

# Check actual data
print("\n=== Checking actual data for recently processed file ===")
cur.execute("""
    SELECT id, file_name, processing_status, 
           total_records, processed_records, progress_percentage
    FROM file_upload 
    WHERE file_name LIKE '%Test%' OR file_name LIKE '%Size%'
    ORDER BY upload_date DESC
    LIMIT 3
""")
rows = cur.fetchall()
for row in rows:
    print(f"\nFile: {row[1]}")
    print(f"  Status: {row[2]}")
    print(f"  Total: {row[3]}")
    print(f"  Processed: {row[4]}")
    print(f"  Progress %: {row[5]}")

cur.close()
conn.close()
