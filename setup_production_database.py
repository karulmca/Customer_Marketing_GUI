"""
Production Database Setup Script
This script creates all necessary tables in the production PostgreSQL database
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlalchemy
from sqlalchemy import create_engine, text
from datetime import datetime

# Add project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, 'database_config'))

def get_production_connection():
    """Get production database connection using environment variables"""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv(os.path.join(current_dir, 'database_config', '.env'))
        
        # Get connection parameters from environment
        params = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'sslmode': os.getenv('DB_SSL_MODE', 'prefer')
        }
        
        print("🔗 Connecting to production database...")
        print(f"📊 Host: {params.get('host', 'Not specified')}")
        print(f"📊 Database: {params.get('database', 'Not specified')}")
        print(f"📊 User: {params.get('user', 'Not specified')}")
        print(f"📊 SSL Mode: {params.get('sslmode', 'Not specified')}")
        
        # Alternative: try using DATABASE_URL if individual params fail
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            print(f"📊 Using DATABASE_URL connection")
            conn = psycopg2.connect(database_url)
        else:
            conn = psycopg2.connect(**params)
        
        return conn, params
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        # Try direct connection with DATABASE_URL as fallback
        try:
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                print("🔄 Trying DATABASE_URL fallback...")
                conn = psycopg2.connect(database_url)
                return conn, {'database_url': database_url}
        except Exception as e2:
            print(f"❌ Fallback connection error: {e2}")
        return None, None

def create_authentication_tables(conn):
    """Create user authentication tables"""
    cursor = conn.cursor()
    
    print("\n🔐 Creating Authentication Tables...")
    
    # Users table
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(50) DEFAULT 'user',
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    );
    """
    
    # User sessions table
    sessions_table = """
    CREATE TABLE IF NOT EXISTS user_sessions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        session_token VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address INET,
        user_agent TEXT
    );
    """
    
    # Login attempts table (for security)
    login_attempts_table = """
    CREATE TABLE IF NOT EXISTS login_attempts (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255),
        ip_address INET,
        success BOOLEAN DEFAULT FALSE,
        attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_agent TEXT,
        failure_reason VARCHAR(255)
    );
    """
    
    # Create indexes for performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);",
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
        "CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);",
        "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_login_attempts_username ON login_attempts(username);",
        "CREATE INDEX IF NOT EXISTS idx_login_attempts_ip ON login_attempts(ip_address);"
    ]
    
    # Execute table creation
    try:
        cursor.execute(users_table)
        print("  ✅ Users table created/verified")
        
        cursor.execute(sessions_table)
        print("  ✅ User sessions table created/verified")
        
        cursor.execute(login_attempts_table)
        print("  ✅ Login attempts table created/verified")
        
        # Create indexes
        for index in indexes:
            cursor.execute(index)
        print("  ✅ Database indexes created/verified")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating authentication tables: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def create_file_processing_tables(conn):
    """Create file processing and job management tables"""
    cursor = conn.cursor()
    
    print("\n📁 Creating File Processing Tables...")
    
    # File uploads table
    file_uploads_table = """
    CREATE TABLE IF NOT EXISTS file_uploads (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        original_filename VARCHAR(500) NOT NULL,
        stored_filename VARCHAR(500) NOT NULL,
        file_path TEXT NOT NULL,
        file_size BIGINT,
        mime_type VARCHAR(255),
        upload_status VARCHAR(50) DEFAULT 'uploaded',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Processing jobs table
    processing_jobs_table = """
    CREATE TABLE IF NOT EXISTS processing_jobs (
        id SERIAL PRIMARY KEY,
        file_upload_id INTEGER REFERENCES file_uploads(id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        job_type VARCHAR(100) NOT NULL DEFAULT 'linkedin_scraping',
        status VARCHAR(50) DEFAULT 'pending',
        progress INTEGER DEFAULT 0,
        total_records INTEGER DEFAULT 0,
        processed_records INTEGER DEFAULT 0,
        failed_records INTEGER DEFAULT 0,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        error_message TEXT,
        result_file_path TEXT,
        configuration JSONB
    );
    """
    
    # Company data table (scraped results)
    company_data_table = """
    CREATE TABLE IF NOT EXISTS company_data (
        id SERIAL PRIMARY KEY,
        processing_job_id INTEGER REFERENCES processing_jobs(id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
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
        employee_count_range VARCHAR(50),
        revenue_estimate VARCHAR(100),
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_source VARCHAR(100) DEFAULT 'linkedin',
        raw_data JSONB,
        processing_status VARCHAR(50) DEFAULT 'completed'
    );
    """
    
    # Processing logs table
    processing_logs_table = """
    CREATE TABLE IF NOT EXISTS processing_logs (
        id SERIAL PRIMARY KEY,
        processing_job_id INTEGER REFERENCES processing_jobs(id) ON DELETE CASCADE,
        log_level VARCHAR(20) DEFAULT 'INFO',
        message TEXT NOT NULL,
        details JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Create indexes for performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_file_uploads_user_id ON file_uploads(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_processing_jobs_user_id ON processing_jobs(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);",
        "CREATE INDEX IF NOT EXISTS idx_company_data_job_id ON company_data(processing_job_id);",
        "CREATE INDEX IF NOT EXISTS idx_company_data_user_id ON company_data(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_processing_logs_job_id ON processing_logs(processing_job_id);"
    ]
    
    # Execute table creation
    try:
        cursor.execute(file_uploads_table)
        print("  ✅ File uploads table created/verified")
        
        cursor.execute(processing_jobs_table)
        print("  ✅ Processing jobs table created/verified")
        
        cursor.execute(company_data_table)
        print("  ✅ Company data table created/verified")
        
        cursor.execute(processing_logs_table)
        print("  ✅ Processing logs table created/verified")
        
        # Create indexes
        for index in indexes:
            cursor.execute(index)
        print("  ✅ File processing indexes created/verified")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating file processing tables: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def create_default_users(conn):
    """Create default admin and user accounts if they don't exist"""
    cursor = conn.cursor()
    
    print("\n👤 Creating Default User Accounts...")
    
    try:
        # Import bcrypt for password hashing
        import bcrypt
        
        # Check if admin user exists
        cursor.execute("SELECT id FROM users WHERE username = %s", ('admin',))
        if not cursor.fetchone():
            admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, is_active)
                VALUES (%s, %s, %s, %s, %s)
            """, ('admin', 'admin@company.com', admin_password, 'admin', True))
            print("  ✅ Admin user created (username: admin, password: admin123)")
        else:
            print("  ℹ️ Admin user already exists")
        
        # Check if regular user exists
        cursor.execute("SELECT id FROM users WHERE username = %s", ('user',))
        if not cursor.fetchone():
            user_password = bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, is_active)
                VALUES (%s, %s, %s, %s, %s)
            """, ('user', 'user@company.com', user_password, 'user', True))
            print("  ✅ Regular user created (username: user, password: user123)")
        else:
            print("  ℹ️ Regular user already exists")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating default users: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def verify_tables(conn):
    """Verify all tables were created successfully"""
    cursor = conn.cursor()
    
    print("\n🔍 Verifying Table Creation...")
    
    # List of expected tables
    expected_tables = [
        'users', 'user_sessions', 'login_attempts',
        'file_uploads', 'processing_jobs', 'company_data', 'processing_logs'
    ]
    
    try:
        # Get list of existing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"  📊 Total tables found: {len(existing_tables)}")
        
        # Check each expected table
        all_tables_exist = True
        for table in expected_tables:
            if table in existing_tables:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  ✅ {table}: EXISTS ({count} records)")
            else:
                print(f"  ❌ {table}: MISSING")
                all_tables_exist = False
        
        # Show any additional tables
        additional_tables = [t for t in existing_tables if t not in expected_tables]
        if additional_tables:
            print(f"  ℹ️ Additional tables: {', '.join(additional_tables)}")
        
        return all_tables_exist
        
    except Exception as e:
        print(f"  ❌ Error verifying tables: {e}")
        return False
    finally:
        cursor.close()

def main():
    """Main setup function"""
    print("🚀 PRODUCTION DATABASE SETUP")
    print("=" * 50)
    print(f"📅 Setup started at: {datetime.now()}")
    
    # Connect to production database
    conn, params = get_production_connection()
    if not conn:
        print("❌ Failed to connect to production database")
        return False
    
    try:
        print(f"✅ Connected to production database: {params.get('database')}")
        
        # Create authentication tables
        auth_success = create_authentication_tables(conn)
        
        # Create file processing tables
        processing_success = create_file_processing_tables(conn)
        
        # Create default users
        users_success = create_default_users(conn)
        
        # Verify all tables
        verification_success = verify_tables(conn)
        
        # Final status
        print("\n🎯 SETUP SUMMARY")
        print("=" * 30)
        print(f"Authentication tables: {'✅ SUCCESS' if auth_success else '❌ FAILED'}")
        print(f"File processing tables: {'✅ SUCCESS' if processing_success else '❌ FAILED'}")
        print(f"Default users: {'✅ SUCCESS' if users_success else '❌ FAILED'}")
        print(f"Table verification: {'✅ SUCCESS' if verification_success else '❌ FAILED'}")
        
        overall_success = auth_success and processing_success and users_success and verification_success
        
        if overall_success:
            print("\n🎉 PRODUCTION DATABASE SETUP: COMPLETED SUCCESSFULLY!")
            print("📋 Ready for testing all functionality")
            print("\n🔐 Default Login Credentials:")
            print("   Admin: admin / admin123")
            print("   User:  user / user123")
        else:
            print("\n⚠️ PRODUCTION DATABASE SETUP: COMPLETED WITH ISSUES")
            print("📋 Please review the errors above")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        return False
    finally:
        conn.close()
        print(f"\n📅 Setup completed at: {datetime.now()}")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)