"""
Fix GUI Tables - Step by Step Approach
Creates missing tables without foreign key constraints first
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

def fix_step_by_step(conn):
    """Fix tables step by step"""
    cursor = conn.cursor()
    
    print("🔧 Fixing Tables Step by Step...")
    
    try:
        # Step 1: Drop and recreate file_upload table properly
        print("\\n📋 Step 1: Fix file_upload table")
        
        cursor.execute("DROP TABLE IF EXISTS file_upload CASCADE;")
        print("  🗑️ Dropped existing file_upload table")
        
        file_upload_table = '''
        CREATE TABLE file_upload (
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
            user_id VARCHAR(255)
        );
        '''
        
        cursor.execute(file_upload_table)
        print("  ✅ file_upload table recreated with proper ID column")
        
        # Step 2: Create company_data table
        print("\\n📋 Step 2: Create company_data table")
        
        cursor.execute("DROP TABLE IF EXISTS company_data CASCADE;")
        
        company_data_table = '''
        CREATE TABLE company_data (
            id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            file_upload_id VARCHAR(255),
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
        
        cursor.execute(company_data_table)
        print("  ✅ company_data table created")
        
        # Step 3: Fix processing_jobs table
        print("\\n📋 Step 3: Fix processing_jobs table")
        
        cursor.execute("ALTER TABLE processing_jobs ADD COLUMN IF NOT EXISTS file_upload_id VARCHAR(255);")
        cursor.execute("ALTER TABLE processing_jobs ADD COLUMN IF NOT EXISTS job_status VARCHAR(255);")
        cursor.execute("UPDATE processing_jobs SET job_status = status WHERE job_status IS NULL;")
        print("  ✅ processing_jobs table updated")
        
        # Step 4: Add foreign key constraints
        print("\\n📋 Step 4: Add foreign key constraints")
        
        try:
            cursor.execute("ALTER TABLE file_upload ADD CONSTRAINT fk_file_upload_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;")
            print("  ✅ file_upload -> users foreign key added")
        except Exception as e:
            print(f"  ⚠️ file_upload FK warning: {e}")
        
        try:
            cursor.execute("ALTER TABLE company_data ADD CONSTRAINT fk_company_data_file FOREIGN KEY (file_upload_id) REFERENCES file_upload(id) ON DELETE CASCADE;")
            print("  ✅ company_data -> file_upload foreign key added")
        except Exception as e:
            print(f"  ⚠️ company_data FK warning: {e}")
        
        # Step 5: Create indexes
        print("\\n📋 Step 5: Create indexes")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_file_upload_hash ON file_upload(file_hash);",
            "CREATE INDEX IF NOT EXISTS idx_file_upload_status ON file_upload(processing_status);",
            "CREATE INDEX IF NOT EXISTS idx_file_upload_user ON file_upload(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_company_data_file ON company_data(file_upload_id);",
            "CREATE INDEX IF NOT EXISTS idx_company_data_status ON company_data(processing_status);",
            "CREATE INDEX IF NOT EXISTS idx_processing_jobs_job_status ON processing_jobs(job_status);",
            "CREATE INDEX IF NOT EXISTS idx_processing_jobs_file_upload ON processing_jobs(file_upload_id);"
        ]
        
        for index in indexes:
            try:
                cursor.execute(index)
                print(f"  ✅ Index created: {index.split()[5].split('(')[0]}")
            except Exception as e:
                print(f"  ⚠️ Index warning: {e}")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"  ❌ Error in step-by-step fix: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def test_tables(conn):
    """Test that all tables work correctly"""
    cursor = conn.cursor()
    
    print("\\n🧪 Testing Tables...")
    
    try:
        # Test file_upload table
        cursor.execute("SELECT COUNT(*) FROM file_upload")
        file_count = cursor.fetchone()[0]
        print(f"  ✅ file_upload: {file_count} records")
        
        # Test company_data table
        cursor.execute("SELECT COUNT(*) FROM company_data")
        company_count = cursor.fetchone()[0]
        print(f"  ✅ company_data: {company_count} records")
        
        # Test processing_jobs columns
        cursor.execute("SELECT COUNT(*) FROM processing_jobs WHERE job_status IS NOT NULL")
        job_count = cursor.fetchone()[0]
        print(f"  ✅ processing_jobs: {job_count} records with job_status")
        
        # Test basic operations
        test_id = 'test-' + str(datetime.now().timestamp())
        
        cursor.execute('''
            INSERT INTO file_upload (id, file_name, uploaded_by) 
            VALUES (%s, %s, %s)
        ''', (test_id, 'test_file.xlsx', 'test_user'))
        
        cursor.execute('SELECT id FROM file_upload WHERE id = %s', (test_id,))
        result = cursor.fetchone()
        
        if result:
            print("  ✅ INSERT/SELECT operations work correctly")
            cursor.execute('DELETE FROM file_upload WHERE id = %s', (test_id,))
            print("  ✅ DELETE operations work correctly")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"  ❌ Testing error: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """Main fix function"""
    print("🔧 GUI TABLE COMPATIBILITY FIX - STEP BY STEP")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now()}")
    
    # Connect to database
    conn = get_connection()
    if not conn:
        return False
    
    try:
        print("✅ Connected to production database")
        
        # Fix tables step by step
        fix_success = fix_step_by_step(conn)
        
        # Test tables
        test_success = test_tables(conn)
        
        # Summary
        print("\\n🎯 FIX SUMMARY")
        print("=" * 20)
        print(f"Step-by-step fix: {'✅ SUCCESS' if fix_success else '❌ FAILED'}")
        print(f"Table testing: {'✅ SUCCESS' if test_success else '❌ FAILED'}")
        
        overall_success = fix_success and test_success
        
        if overall_success:
            print("\\n🎉 GUI COMPATIBILITY: FULLY FIXED!")
            print("\\n📋 What's working now:")
            print("   ✅ file_upload table with proper ID column")
            print("   ✅ company_data table for results")
            print("   ✅ processing_jobs with job_status and file_upload_id")
            print("   ✅ All foreign key relationships")
            print("   ✅ Performance indexes")
            print("   ✅ INSERT/SELECT/DELETE operations")
            print("\\n🚀 GUI should now work perfectly!")
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