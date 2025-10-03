"""
Add Missing Tables for GUI Compatibility
Creates file_upload and company_data tables that the GUI expects
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

def get_connection():
    """Get database connection"""
    try:
        load_dotenv('database_config/.env')
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            print("❌ DATABASE_URL not found")
            return None
            
        conn = psycopg2.connect(database_url)
        return conn
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def create_gui_tables(conn):
    """Create the tables that the GUI expects"""
    cursor = conn.cursor()
    
    print("🏗️ Creating GUI-Expected Tables...")
    
    try:
        # 1. file_upload table (what the GUI expects)
        file_upload_table = '''
        CREATE TABLE IF NOT EXISTS file_upload (
            id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            file_name VARCHAR(500) NOT NULL,
            original_filename VARCHAR(500),
            file_path TEXT,
            file_size BIGINT,
            file_hash VARCHAR(255),
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processing_status VARCHAR(50) DEFAULT 'pending',
            uploaded_by VARCHAR(255),
            records_count INTEGER DEFAULT 0,
            json_data JSONB,
            user_id VARCHAR(255) REFERENCES users(id) ON DELETE SET NULL
        );
        '''
        
        # 2. company_data table (what the GUI expects)
        company_data_table = '''
        CREATE TABLE IF NOT EXISTS company_data (
            id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            file_upload_id VARCHAR(255) REFERENCES file_upload(id) ON DELETE CASCADE,
            company_name VARCHAR(500),
            linkedin_url TEXT,
            company_website TEXT,
            company_size VARCHAR(100),
            industry VARCHAR(200),
            revenue VARCHAR(100),
            headquarters VARCHAR(200),
            founded_year INTEGER,
            company_type VARCHAR(100),
            specialties TEXT,
            about_company TEXT,
            employee_count VARCHAR(50),
            file_source VARCHAR(100) DEFAULT 'excel',
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processing_status VARCHAR(50) DEFAULT 'pending',
            scraped_at TIMESTAMP,
            data_source VARCHAR(100) DEFAULT 'linkedin',
            raw_data JSONB
        );
        '''
        
        # Execute table creation
        cursor.execute(file_upload_table)
        print("  ✅ file_upload table created")
        
        cursor.execute(company_data_table)
        print("  ✅ company_data table created")
        
        # Fix the processing_jobs table - add missing columns and fix index
        processing_jobs_fixes = [
            "ALTER TABLE processing_jobs ADD COLUMN IF NOT EXISTS file_upload_id VARCHAR(255);",
            "ALTER TABLE processing_jobs ADD COLUMN IF NOT EXISTS job_status VARCHAR(255) DEFAULT 'pending';",
            "UPDATE processing_jobs SET job_status = status WHERE job_status IS NULL;",
            "CREATE INDEX IF NOT EXISTS idx_processing_jobs_job_status ON processing_jobs(job_status);",
            "CREATE INDEX IF NOT EXISTS idx_processing_jobs_file_upload ON processing_jobs(file_upload_id);"
        ]
        
        for fix in processing_jobs_fixes:
            try:
                cursor.execute(fix)
                print(f"  ✅ Applied fix: {fix.split()[0:4]}")
            except Exception as e:
                if "already exists" in str(e) or "duplicate" in str(e).lower():
                    continue
                print(f"  ⚠️ Fix warning: {e}")
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_file_upload_hash ON file_upload(file_hash);",
            "CREATE INDEX IF NOT EXISTS idx_file_upload_status ON file_upload(processing_status);",
            "CREATE INDEX IF NOT EXISTS idx_file_upload_user ON file_upload(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_company_data_file ON company_data(file_upload_id);",
            "CREATE INDEX IF NOT EXISTS idx_company_data_status ON company_data(processing_status);"
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        print("  ✅ Database indexes created")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating tables: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def verify_gui_tables(conn):
    """Verify the GUI tables exist"""
    cursor = conn.cursor()
    
    print("\\n🔍 Verifying GUI Tables...")
    
    try:
        # Check tables exist
        cursor.execute('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('file_upload', 'company_data', 'processing_jobs')
            ORDER BY table_name
        ''')
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  📊 GUI tables found: {tables}")
        
        # Check columns in processing_jobs
        cursor.execute('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'processing_jobs' 
            AND column_name IN ('file_upload_id', 'job_status', 'status')
            ORDER BY column_name
        ''')
        
        columns = [row[0] for row in cursor.fetchall()]
        print(f"  📋 processing_jobs columns: {columns}")
        
        # Test basic operations
        cursor.execute("SELECT COUNT(*) FROM file_upload")
        file_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM company_data")
        company_count = cursor.fetchone()[0]
        
        print(f"  ✅ file_upload: {file_count} records")
        print(f"  ✅ company_data: {company_count} records")
        
        return len(tables) >= 3
        
    except Exception as e:
        print(f"  ❌ Verification error: {e}")
        return False
    finally:
        cursor.close()

def main():
    """Main setup function"""
    print("🔧 FIXING GUI TABLE COMPATIBILITY")
    print("=" * 40)
    print(f"📅 Started at: {datetime.now()}")
    
    # Connect to database
    conn = get_connection()
    if not conn:
        return False
    
    try:
        print("✅ Connected to production database")
        
        # Create GUI tables
        tables_success = create_gui_tables(conn)
        
        # Verify setup
        verification_success = verify_gui_tables(conn)
        
        # Summary
        print("\\n🎯 FIX SUMMARY")
        print("=" * 20)
        print(f"GUI tables: {'✅ SUCCESS' if tables_success else '❌ FAILED'}")
        print(f"Verification: {'✅ SUCCESS' if verification_success else '❌ FAILED'}")
        
        overall_success = tables_success and verification_success
        
        if overall_success:
            print("\\n🎉 GUI COMPATIBILITY: FIXED!")
            print("\\n📋 What's been added:")
            print("   ✅ file_upload table (for GUI file operations)")
            print("   ✅ company_data table (for GUI results)")
            print("   ✅ processing_jobs fixes (job_status, file_upload_id)")
            print("   ✅ Required indexes for performance")
            print("\\n🚀 GUI should now work correctly!")
        else:
            print("\\n⚠️ FIXES INCOMPLETE - Please check errors above")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False
    finally:
        conn.close()
        print(f"\\n📅 Completed at: {datetime.now()}")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)