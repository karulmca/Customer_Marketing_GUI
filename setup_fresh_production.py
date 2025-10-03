"""
Complete Production Database Setup - Fresh Installation
Creates all necessary tables for the Company Data Scraper application
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

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

def create_all_tables(conn):
    """Create all necessary tables for the application"""
    cursor = conn.cursor()
    
    print("🏗️ Creating All Application Tables...")
    
    # 1. Users table (authentication)
    users_table = '''
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        username VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        hashed_password VARCHAR(255),  -- For compatibility
        role VARCHAR(50) DEFAULT 'user',
        full_name VARCHAR(500),
        is_active BOOLEAN DEFAULT TRUE,
        is_superuser BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    );
    '''
    
    # 2. User sessions table
    sessions_table = '''
    CREATE TABLE IF NOT EXISTS user_sessions (
        id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
        session_token VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address INET,
        user_agent TEXT
    );
    '''
    
    # 3. Login attempts table
    login_attempts_table = '''
    CREATE TABLE IF NOT EXISTS login_attempts (
        id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        username VARCHAR(255),
        ip_address INET,
        success BOOLEAN DEFAULT FALSE,
        attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_agent TEXT,
        failure_reason VARCHAR(255)
    );
    '''
    
    # 4. Excel/File uploads table
    excel_files_table = '''
    CREATE TABLE IF NOT EXISTS excel_files (
        id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        user_id VARCHAR(255) REFERENCES users(id) ON DELETE SET NULL,
        filename VARCHAR(500) NOT NULL,
        original_filename VARCHAR(500),
        file_path TEXT,
        file_size BIGINT,
        upload_status VARCHAR(50) DEFAULT 'uploaded',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP
    );
    '''
    
    # 5. Processing jobs table
    processing_jobs_table = '''
    CREATE TABLE IF NOT EXISTS processing_jobs (
        id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        user_id VARCHAR(255) REFERENCES users(id) ON DELETE SET NULL,
        file_id VARCHAR(255) REFERENCES excel_files(id) ON DELETE CASCADE,
        job_type VARCHAR(255) NOT NULL DEFAULT 'linkedin_scraping',
        status VARCHAR(255) DEFAULT 'pending',
        total_items INTEGER DEFAULT 0,
        processed_items INTEGER DEFAULT 0,
        failed_items INTEGER DEFAULT 0,
        progress INTEGER DEFAULT 0,
        result_data TEXT,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        configuration JSONB
    );
    '''
    
    # 6. Companies table (input data)
    companies_table = '''
    CREATE TABLE IF NOT EXISTS companies (
        id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        processing_job_id VARCHAR(255) REFERENCES processing_jobs(id) ON DELETE CASCADE,
        user_id VARCHAR(255) REFERENCES users(id) ON DELETE SET NULL,
        company_name VARCHAR(500),
        website VARCHAR(1000),
        linkedin_url VARCHAR(1000),
        status VARCHAR(100) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
    
    # 7. Company results table (scraped data)
    company_results_table = '''
    CREATE TABLE IF NOT EXISTS company_results (
        id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        company_id VARCHAR(255) REFERENCES companies(id) ON DELETE CASCADE,
        processing_job_id VARCHAR(255) REFERENCES processing_jobs(id) ON DELETE CASCADE,
        user_id VARCHAR(255) REFERENCES users(id) ON DELETE SET NULL,
        company_name VARCHAR(500),
        website_url TEXT,
        linkedin_url TEXT,
        company_size VARCHAR(100),
        industry VARCHAR(200),
        headquarters VARCHAR(200),
        founded_year INTEGER,
        company_type VARCHAR(100),
        specialties TEXT,
        about_company TEXT,
        employee_count VARCHAR(50),
        revenue_estimate VARCHAR(100),
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_source VARCHAR(100) DEFAULT 'linkedin',
        raw_data JSONB,
        scraping_status VARCHAR(50) DEFAULT 'completed'
    );
    '''
    
    # 8. Processing logs table
    processing_logs_table = '''
    CREATE TABLE IF NOT EXISTS processing_logs (
        id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        processing_job_id VARCHAR(255) REFERENCES processing_jobs(id) ON DELETE CASCADE,
        log_level VARCHAR(20) DEFAULT 'INFO',
        message TEXT NOT NULL,
        details JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
    
    # 9. API usage tracking table
    api_usage_table = '''
    CREATE TABLE IF NOT EXISTS api_usage (
        id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        user_id VARCHAR(255) REFERENCES users(id) ON DELETE SET NULL,
        api_endpoint VARCHAR(200),
        method VARCHAR(20),
        status_code INTEGER,
        response_time INTEGER,
        request_size INTEGER,
        response_size INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
    
    # List of tables to create
    tables = [
        ("users", users_table),
        ("user_sessions", sessions_table),
        ("login_attempts", login_attempts_table),
        ("excel_files", excel_files_table),
        ("processing_jobs", processing_jobs_table),
        ("companies", companies_table),
        ("company_results", company_results_table),
        ("processing_logs", processing_logs_table),
        ("api_usage", api_usage_table)
    ]
    
    try:
        # Create tables
        for table_name, table_sql in tables:
            cursor.execute(table_sql)
            print(f"  ✅ {table_name} table created")
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);",
            "CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_login_attempts_username ON login_attempts(username);",
            "CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);",
            "CREATE INDEX IF NOT EXISTS idx_processing_jobs_user ON processing_jobs(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_companies_job ON companies(processing_job_id);",
            "CREATE INDEX IF NOT EXISTS idx_company_results_job ON company_results(processing_job_id);",
            "CREATE INDEX IF NOT EXISTS idx_logs_job ON processing_logs(processing_job_id);"
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

def create_default_users(conn):
    """Create default admin and user accounts"""
    cursor = conn.cursor()
    
    print("\\n👤 Creating Default User Accounts...")
    
    try:
        import bcrypt
        
        # Create admin user
        admin_id = str(uuid.uuid4())
        admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute('''
            INSERT INTO users (id, username, email, password_hash, hashed_password, role, full_name, is_active, is_superuser)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        ''', (admin_id, 'admin', 'admin@company.com', admin_password, admin_password, 'admin', 'Administrator', True, True))
        
        # Create regular user
        user_id = str(uuid.uuid4())
        user_password = bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute('''
            INSERT INTO users (id, username, email, password_hash, hashed_password, role, full_name, is_active, is_superuser)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        ''', (user_id, 'user', 'user@company.com', user_password, user_password, 'user', 'Regular User', True, False))
        
        print("  ✅ Admin user: admin / admin123")
        print("  ✅ Regular user: user / user123")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating users: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def verify_setup(conn):
    """Verify the database setup"""
    cursor = conn.cursor()
    
    print("\\n🔍 Verifying Database Setup...")
    
    try:
        # Get all tables
        cursor.execute('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        ''')
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  📊 Total tables created: {len(tables)}")
        
        # Check each important table
        important_tables = ['users', 'processing_jobs', 'companies', 'company_results', 'excel_files']
        
        for table in important_tables:
            if table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                print(f"  ✅ {table}: {count} records")
            else:
                print(f"  ❌ {table}: MISSING")
        
        # Check users
        cursor.execute("SELECT username, role FROM users ORDER BY role DESC")
        users = cursor.fetchall()
        if users:
            print(f"  👥 Users created: {', '.join([f'{u[0]} ({u[1]})' for u in users])}")
        
        return len(tables) >= 8  # Should have at least 8 tables
        
    except Exception as e:
        print(f"  ❌ Verification error: {e}")
        return False
    finally:
        cursor.close()

def main():
    """Main setup function"""
    print("🚀 COMPLETE PRODUCTION DATABASE SETUP")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now()}")
    
    # Connect to database
    conn = get_connection()
    if not conn:
        return False
    
    try:
        print("✅ Connected to production database")
        
        # Create all tables
        tables_success = create_all_tables(conn)
        
        # Create default users
        users_success = create_default_users(conn)
        
        # Verify setup
        verification_success = verify_setup(conn)
        
        # Summary
        print("\\n🎯 SETUP SUMMARY")
        print("=" * 25)
        print(f"Tables creation: {'✅ SUCCESS' if tables_success else '❌ FAILED'}")
        print(f"Default users: {'✅ SUCCESS' if users_success else '❌ FAILED'}")
        print(f"Verification: {'✅ SUCCESS' if verification_success else '❌ FAILED'}")
        
        overall_success = tables_success and users_success and verification_success
        
        if overall_success:
            print("\\n🎉 PRODUCTION DATABASE: READY!")
            print("\\n📋 What's been set up:")
            print("   ✅ User authentication system")
            print("   ✅ File upload tracking")
            print("   ✅ Processing job management")
            print("   ✅ Company data storage")
            print("   ✅ Results tracking")
            print("   ✅ Logging system")
            print("\\n🔐 Login Credentials:")
            print("   Admin: admin / admin123")
            print("   User:  user / user123")
            print("\\n🚀 Ready to test all functionality!")
        else:
            print("\\n⚠️ SETUP INCOMPLETE - Please check errors above")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False
    finally:
        conn.close()
        print(f"\\n📅 Completed at: {datetime.now()}")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)