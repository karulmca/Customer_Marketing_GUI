"""
Production Database Schema Update Script
Updates existing production database to support authentication and complete functionality
Works with existing schema (VARCHAR IDs, different column names)
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from datetime import datetime
from dotenv import load_dotenv

def get_production_connection():
    """Get production database connection"""
    try:
        # Load environment variables
        load_dotenv(os.path.join('database_config', '.env'))
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found in environment")
            return None, None
            
        print("🔗 Connecting to production database...")
        conn = psycopg2.connect(database_url)
        
        # Get connection info
        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), current_user")
        db_info = cursor.fetchone()
        cursor.close()
        
        print(f"✅ Connected to database: {db_info[0]} as user: {db_info[1]}")
        return conn, {'database': db_info[0], 'user': db_info[1]}
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None, None

def update_users_table(conn):
    """Update existing users table to support authentication"""
    cursor = conn.cursor()
    
    print("\\n👤 Updating Users Table for Authentication...")
    
    try:
        # Add missing columns to existing users table
        columns_to_add = [
            ("role", "VARCHAR(50) DEFAULT 'user'"),
            ("last_login", "TIMESTAMP"),
            ("password_hash", "VARCHAR(255)"),  # Alternative to hashed_password
            ("session_token", "VARCHAR(255)"),
            ("session_expires", "TIMESTAMP")
        ]
        
        for column_name, column_def in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column_name} {column_def}")
                print(f"  ✅ Added column: {column_name}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"  ℹ️ Column {column_name} already exists")
                else:
                    print(f"  ⚠️ Error adding column {column_name}: {e}")
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username_prod ON users(username);",
            "CREATE INDEX IF NOT EXISTS idx_users_email_prod ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_users_session_token ON users(session_token);"
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        print("  ✅ User table indexes created/verified")
        conn.commit()
        return True
        
    except Exception as e:
        print(f"  ❌ Error updating users table: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def create_missing_tables(conn):
    """Create missing authentication and logging tables"""
    cursor = conn.cursor()
    
    print("\\n🔐 Creating Missing Authentication Tables...")
    
    # User sessions table (compatible with existing VARCHAR ID schema)
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
    
    # Login attempts table
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
    
    # Company data table (for scraped results)
    company_data_table = '''
    CREATE TABLE IF NOT EXISTS company_scraped_data (
        id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
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
        employee_count_range VARCHAR(50),
        revenue_estimate VARCHAR(100),
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_source VARCHAR(100) DEFAULT 'linkedin',
        raw_data JSONB,
        processing_status VARCHAR(50) DEFAULT 'completed'
    );
    '''
    
    # Processing logs table
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
    
    # File uploads tracking table
    file_uploads_table = '''
    CREATE TABLE IF NOT EXISTS file_uploads_tracking (
        id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
        user_id VARCHAR(255) REFERENCES users(id) ON DELETE SET NULL,
        original_filename VARCHAR(500) NOT NULL,
        stored_filename VARCHAR(500) NOT NULL,
        file_path TEXT NOT NULL,
        file_size BIGINT,
        mime_type VARCHAR(255),
        upload_status VARCHAR(50) DEFAULT 'uploaded',
        processing_job_id VARCHAR(255) REFERENCES processing_jobs(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
    
    tables_to_create = [
        ("user_sessions", sessions_table),
        ("login_attempts", login_attempts_table),
        ("company_scraped_data", company_data_table),
        ("processing_logs", processing_logs_table),
        ("file_uploads_tracking", file_uploads_table)
    ]
    
    try:
        for table_name, table_sql in tables_to_create:
            cursor.execute(table_sql)
            print(f"  ✅ {table_name} table created/verified")
        
        # Create performance indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_login_attempts_username ON login_attempts(username);",
            "CREATE INDEX IF NOT EXISTS idx_company_data_job_id ON company_scraped_data(processing_job_id);",
            "CREATE INDEX IF NOT EXISTS idx_processing_logs_job_id ON processing_logs(processing_job_id);",
            "CREATE INDEX IF NOT EXISTS idx_file_uploads_user_id ON file_uploads_tracking(user_id);"
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        print("  ✅ Performance indexes created/verified")
        conn.commit()
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating tables: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def setup_default_users(conn):
    """Setup default admin and user accounts"""
    cursor = conn.cursor()
    
    print("\\n🔑 Setting up Default User Accounts...")
    
    try:
        import bcrypt
        
        # Check if admin user has proper authentication setup
        cursor.execute("SELECT id, username, hashed_password, password_hash, role FROM users WHERE username = %s", ('admin',))
        admin_user = cursor.fetchone()
        
        if admin_user:
            admin_id, username, hashed_password, password_hash, role = admin_user
            print(f"  ℹ️ Admin user found: {username}")
            
            # Update admin user with proper authentication
            if not password_hash:  # No password_hash column set
                admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("""
                    UPDATE users 
                    SET password_hash = %s, role = %s 
                    WHERE id = %s
                """, (admin_password, 'admin', admin_id))
                print("  ✅ Admin password updated for authentication")
            
            if not role or role != 'admin':
                cursor.execute("UPDATE users SET role = %s WHERE id = %s", ('admin', admin_id))
                print("  ✅ Admin role updated")
                
        else:
            # Create admin user
            admin_id = str(uuid.uuid4())
            admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("""
                INSERT INTO users (id, username, email, hashed_password, password_hash, role, is_active, full_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (admin_id, 'admin', 'admin@company.com', admin_password, admin_password, 'admin', True, 'Administrator'))
            print("  ✅ Admin user created (username: admin, password: admin123)")
        
        # Check if regular user exists
        cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = %s", ('user',))
        regular_user = cursor.fetchone()
        
        if regular_user:
            user_id, username, password_hash, role = regular_user
            print(f"  ℹ️ Regular user found: {username}")
            
            # Update regular user with proper authentication
            if not password_hash:
                user_password = bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("""
                    UPDATE users 
                    SET password_hash = %s, role = %s 
                    WHERE id = %s
                """, (user_password, 'user', user_id))
                print("  ✅ User password updated for authentication")
                
        else:
            # Create regular user
            user_id = str(uuid.uuid4())
            user_password = bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("""
                INSERT INTO users (id, username, email, hashed_password, password_hash, role, is_active, full_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, 'user', 'user@company.com', user_password, user_password, 'user', True, 'Regular User'))
            print("  ✅ Regular user created (username: user, password: user123)")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"  ❌ Error setting up users: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def verify_production_setup(conn):
    """Verify the production database setup"""
    cursor = conn.cursor()
    
    print("\\n🔍 Verifying Production Database Setup...")
    
    try:
        # Check all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        # Expected tables for full functionality
        expected_tables = [
            'users', 'user_sessions', 'login_attempts',
            'processing_jobs', 'company_scraped_data', 'processing_logs',
            'file_uploads_tracking'
        ]
        
        print(f"  📊 Total tables: {len(tables)}")
        
        missing_tables = []
        for table in expected_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  ✅ {table}: {count} records")
            else:
                print(f"  ❌ {table}: MISSING")
                missing_tables.append(table)
        
        # Check authentication setup
        cursor.execute("SELECT COUNT(*) FROM users WHERE password_hash IS NOT NULL AND role IS NOT NULL")
        auth_users = cursor.fetchone()[0]
        print(f"  🔐 Users with authentication setup: {auth_users}")
        
        # Check admin user
        cursor.execute("SELECT username, role FROM users WHERE role = 'admin'")
        admin_users = cursor.fetchall()
        if admin_users:
            print(f"  👑 Admin users: {', '.join([u[0] for u in admin_users])}")
        
        success = len(missing_tables) == 0 and auth_users > 0
        return success, missing_tables
        
    except Exception as e:
        print(f"  ❌ Verification error: {e}")
        return False, []
    finally:
        cursor.close()

def main():
    """Main setup function"""
    print("🚀 PRODUCTION DATABASE SCHEMA UPDATE")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now()}")
    
    # Connect to production
    conn, params = get_production_connection()
    if not conn:
        return False
    
    try:
        # Update existing users table
        users_success = update_users_table(conn)
        
        # Create missing tables
        tables_success = create_missing_tables(conn)
        
        # Setup default users
        auth_success = setup_default_users(conn)
        
        # Verify setup
        verification_success, missing_tables = verify_production_setup(conn)
        
        # Summary
        print("\\n🎯 PRODUCTION UPDATE SUMMARY")
        print("=" * 35)
        print(f"Users table update: {'✅ SUCCESS' if users_success else '❌ FAILED'}")
        print(f"Missing tables created: {'✅ SUCCESS' if tables_success else '❌ FAILED'}")
        print(f"Authentication setup: {'✅ SUCCESS' if auth_success else '❌ FAILED'}")
        print(f"Verification: {'✅ SUCCESS' if verification_success else '❌ FAILED'}")
        
        if missing_tables:
            print(f"Missing tables: {', '.join(missing_tables)}")
        
        overall_success = users_success and tables_success and auth_success and verification_success
        
        if overall_success:
            print("\\n🎉 PRODUCTION DATABASE: READY FOR TESTING!")
            print("\\n🔐 Authentication Credentials:")
            print("   Admin: admin / admin123")
            print("   User:  user / user123")
            print("\\n📋 Ready to test all functionality:")
            print("   ✅ User authentication and registration")
            print("   ✅ File upload and processing")
            print("   ✅ LinkedIn data scraping")
            print("   ✅ Job management and tracking")
        else:
            print("\\n⚠️ PRODUCTION DATABASE: SETUP INCOMPLETE")
            print("📋 Please review errors above")
        
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