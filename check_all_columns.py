import psycopg2
from database_config.postgresql_config import PostgreSQLConfig

cfg = PostgreSQLConfig()
conn = psycopg2.connect(**cfg.get_connection_params())
cur = conn.cursor()

# Get all columns for Test2.xlsx
print("\n=== All processing_jobs columns for Test2.xlsx ===")
cur.execute("""
    SELECT * 
    FROM processing_jobs 
    WHERE file_upload_id = 'b40f933b-2136-41cf-b254-9c2f640eefbb'
""")
cols = [desc[0] for desc in cur.description]
row = cur.fetchone()

if row:
    for i in range(len(cols)):
        if row[i] is not None and row[i] != '':
            print(f"{cols[i]}: {row[i]}")
else:
    print("No data found")

# Check file_upload table columns too
print("\n=== file_upload columns for Test2.xlsx ===")
cur.execute("""
    SELECT * 
    FROM file_upload 
    WHERE file_name = 'Test2.xlsx'
""")
cols = [desc[0] for desc in cur.description]
row = cur.fetchone()

if row:
    for i in range(len(cols)):
        if row[i] is not None and row[i] != '':
            print(f"{cols[i]}: {row[i]}")
else:
    print("No data found")

cur.close()
conn.close()
