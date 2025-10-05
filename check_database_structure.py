#!/usr/bin/env python3
"""
Check database table structures and data
"""

from database_config.postgresql_config import PostgreSQLConfig
import psycopg2

def check_database():
    try:
        db_config = PostgreSQLConfig()
        connection = psycopg2.connect(**db_config.get_connection_params())
        cursor = connection.cursor()
        
        print("🔍 Checking database tables and data...")
        print("=" * 60)
        
        # Get all tables
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Found {len(tables)} tables: {', '.join(tables)}")
        print()
        
        # Check each table
        for table in tables:
            print(f"🔍 Table: {table}")
            
            # Get column info
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table}' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            print(f"   Columns ({len(columns)}):")
            for col_name, data_type, nullable, default in columns:
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                print(f"     - {col_name}: {data_type} {nullable_str}{default_str}")
            
            # Get row count
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f"   Rows: {count}")
            
            # Show sample data for important tables
            if count > 0 and table in ['file_upload', 'company_data', 'processing_jobs']:
                cursor.execute(f'SELECT * FROM {table} LIMIT 2')
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                
                print(f"   Sample data:")
                for i, row in enumerate(rows):
                    print(f"     Row {i+1}:")
                    for col_name, value in zip(column_names, row):
                        print(f"       {col_name}: {value}")
            
            print()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_database()