import psycopg2
from database_config.postgresql_config import PostgreSQLConfig

cfg = PostgreSQLConfig()
conn = psycopg2.connect(**cfg.get_connection_params())
cur = conn.cursor()

# Check file_upload table
print("\n=== Checking file_upload table ===")
cur.execute("""
    SELECT id, file_name, processing_status 
    FROM file_upload 
    WHERE file_name LIKE '%Testing3%' 
    ORDER BY upload_date DESC 
    LIMIT 1
""")
fu_row = cur.fetchone()
if fu_row:
    print(f"file_upload.id: {fu_row[0]}")
    print(f"file_name: {fu_row[1]}")
    print(f"processing_status: {fu_row[2]}")
    file_id = fu_row[0]
else:
    print("No file found")
    cur.close()
    conn.close()
    exit()

# Check processing_jobs table
print("\n=== Checking processing_jobs columns ===")
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'processing_jobs' 
    ORDER BY ordinal_position
""")
columns = [row[0] for row in cur.fetchall()]
print("Columns:", ", ".join(columns))

print("\n=== Checking processing_jobs table ===")
cur.execute("""
    SELECT id, file_upload_id, status
    FROM processing_jobs 
    ORDER BY created_at DESC 
    LIMIT 5
""")
pj_rows = cur.fetchall()
print(f"Found {len(pj_rows)} recent processing jobs:")
for i, pj in enumerate(pj_rows, 1):
    print(f"\n{i}. pj.id: {pj[0]}")
    print(f"   pj.file_upload_id: {pj[1]} (type: {type(pj[1])})")
    print(f"   status: {pj[2]}")

# Check JOIN with our file
print(f"\n=== Testing JOIN for file_id: {file_id} ===")
print(f"file_id type: {type(file_id)}")

# Try different JOIN approaches - simplified without progress columns
print("\n1. JOIN with ::text cast:")
cur.execute("""
    SELECT fu.id, fu.file_name, pj.status
    FROM file_upload fu 
    LEFT JOIN processing_jobs pj ON pj.file_upload_id::text = fu.id
    WHERE fu.id = %s
""", (file_id,))
row1 = cur.fetchone()
if row1:
    print(f"   Result: status={row1[2]}")
else:
    print("   No result")

print("\n2. JOIN with UUID cast on fu.id:")
cur.execute("""
    SELECT fu.id, fu.file_name, pj.status
    FROM file_upload fu 
    LEFT JOIN processing_jobs pj ON pj.file_upload_id = fu.id::uuid
    WHERE fu.id = %s
""", (file_id,))
row2 = cur.fetchone()
if row2:
    print(f"   Result: status={row2[2]}")
else:
    print("   No result")

print("\n3. Direct comparison:")
cur.execute("""
    SELECT fu.id, fu.file_name, pj.status
    FROM file_upload fu 
    LEFT JOIN processing_jobs pj ON pj.file_upload_id = fu.id
    WHERE fu.id = %s
""", (file_id,))
row3 = cur.fetchone()
if row3:
    print(f"   Result: status={row3[2]}")
else:
    print("   No result")

cur.close()
conn.close()
