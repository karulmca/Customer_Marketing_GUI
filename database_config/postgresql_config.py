"""
PostgreSQL Database Configuration and Connection Manager
Handles database connections and configuration loading
"""

import os
import sys
import psycopg2
from psycopg2 import pool
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLConfig:
    """PostgreSQL Database Configuration Manager"""
    
    def __init__(self, config_file: str = None):
        """Initialize with configuration file or environment variables"""
        if config_file:
            self.config_file = config_file
        else:
            # Detect if running as executable
            is_executable = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
            
            if is_executable:
                # Running as PyInstaller executable
                logger.info("Detected executable environment")
                exe_dir = os.path.dirname(sys.executable)
                possible_locations = [
                    os.path.join(exe_dir, '.env'),  # Same directory as .exe
                    os.path.join(os.getcwd(), '.env'),  # Current working directory
                    '.env',  # Current directory
                ]
            else:
                # Running as Python script
                logger.debug("Detected Python script environment")
                possible_locations = [
                    os.path.join(os.path.dirname(__file__), '.env'),  # database_config/.env
                    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),  # root/.env
                    '.env',  # current directory .env
                ]
            
            self.config_file = None
            for location in possible_locations:
                logger.debug(f"Checking: {location}")
                if os.path.exists(location):
                    self.config_file = location
                    logger.debug(f"Found .env file at: {location}")
                    break
            
            if not self.config_file:
                # Only show warnings if no environment variables are set
                if not os.getenv('DATABASE_URL') and not os.getenv('DB_HOST'):
                    logger.warning("No .env file found in any expected location")
                    logger.warning(f"Searched locations: {possible_locations}")
                else:
                    logger.debug("Using environment variables for database configuration")
                self.config_file = possible_locations[0]  # Use default as fallback
        
        self.config = self.load_config()
        self.connection_pool = None
        self.engine = None
        self.Session = None
        
    def load_config(self) -> Dict[str, str]:
        """Load configuration from .env file or environment variables"""
        config = {}
        
        # Try to load from .env file first
        if self.config_file and os.path.exists(self.config_file):
            try:
                logger.debug(f"Loading configuration from: {self.config_file}")
                with open(self.config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
                logger.debug(f"Loaded {len(config)} configuration items")
            except Exception as e:
                logger.error(f"Failed to load .env file: {e}")
        else:
            # Only warn if no environment variables are available
            if not os.getenv('DATABASE_URL') and not os.getenv('DB_HOST'):
                logger.warning(f".env file not found at: {self.config_file}")
            else:
                logger.debug("Using environment variables instead of .env file")
        
        # Override with environment variables if they exist
        env_vars = [
            'DATABASE_URL', 'DB_HOST', 'DB_PORT', 'DB_NAME', 
            'DB_USER', 'DB_PASSWORD', 'DB_DRIVER', 'DB_POOL_SIZE',
            'DB_MAX_OVERFLOW', 'DB_POOL_TIMEOUT', 'DB_POOL_RECYCLE',
            'DB_SSL_MODE', 'DB_CHARSET', 'DB_TIMEZONE',
            'DB_CONNECT_TIMEOUT', 'DB_COMMAND_TIMEOUT'
        ]
        
        for var in env_vars:
            if os.getenv(var):
                config[var] = os.getenv(var)
                
        return config
    
    def get_database_url(self) -> str:
        """Get the complete database URL"""
        if 'DATABASE_URL' in self.config:
            return self.config['DATABASE_URL']
        
        # Build URL from individual components
        host = self.config.get('DB_HOST', 'localhost')
        port = self.config.get('DB_PORT', '5432')
        database = self.config.get('DB_NAME', 'FileUpload')
        username = self.config.get('DB_USER', 'postgres')
        password = self.config.get('DB_PASSWORD', '')
        driver = self.config.get('DB_DRIVER', 'postgresql')
        
        return f"{driver}://{username}:{password}@{host}:{port}/{database}"
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters for psycopg2"""
        return {
            'host': self.config.get('DB_HOST', 'localhost'),
            'port': int(self.config.get('DB_PORT', 5432)),
            'database': self.config.get('DB_NAME', 'FileUpload'),
            'user': self.config.get('DB_USER', 'postgres'),
            'password': self.config.get('DB_PASSWORD', ''),
            'sslmode': self.config.get('DB_SSL_MODE', 'prefer'),
            'connect_timeout': int(self.config.get('DB_CONNECT_TIMEOUT', 10))
        }
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            params = self.get_connection_params()
            conn = psycopg2.connect(**params)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {str(e)}")
            return False
    
    def create_connection_pool(self) -> Optional[psycopg2.pool.ThreadedConnectionPool]:
        """Create a connection pool"""
        try:
            params = self.get_connection_params()
            pool_size = int(self.config.get('DB_POOL_SIZE', 5))
            max_overflow = int(self.config.get('DB_MAX_OVERFLOW', 10))
            
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=pool_size + max_overflow,
                **params
            )
            
            logger.info(f"✅ Connection pool created with {pool_size} connections")
            return self.connection_pool
            
        except Exception as e:
            logger.error(f"❌ Failed to create connection pool: {str(e)}")
            return None
    
    def get_sqlalchemy_engine(self):
        """Create SQLAlchemy engine"""
        try:
            database_url = self.get_database_url()
            
            # Engine configuration
            engine_config = {
                'pool_size': int(self.config.get('DB_POOL_SIZE', 5)),
                'max_overflow': int(self.config.get('DB_MAX_OVERFLOW', 10)),
                'pool_timeout': int(self.config.get('DB_POOL_TIMEOUT', 30)),
                'pool_recycle': int(self.config.get('DB_POOL_RECYCLE', 3600)),
                'echo': False  # Set to True for SQL logging
            }
            
            self.engine = create_engine(database_url, **engine_config)
            
            # Test the connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
            
            # Create session factory
            self.Session = sessionmaker(bind=self.engine)
            
            return self.engine
            
        except Exception as e:
            logger.error(f"❌ Failed to create SQLAlchemy engine: {str(e)}")
            return None
    
    def get_session(self):
        """Get a new database session"""
        if not self.Session:
            self.get_sqlalchemy_engine()
        
        return self.Session() if self.Session else None
    
    def close_connections(self):
        """Close all connections and cleanup"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("🔒 Connection pool closed")
        
        if self.engine:
            self.engine.dispose()
            logger.info("🔒 SQLAlchemy engine disposed")

class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self, config: PostgreSQLConfig = None):
        self.config = config or PostgreSQLConfig()
        self.engine = None
        
    def initialize(self) -> bool:
        """Initialize database connection"""
        if not self.config.test_connection():
            return False
            
        self.engine = self.config.get_sqlalchemy_engine()
        return self.engine is not None
    
    def create_tables(self):
        """Create required tables for file upload system"""
        if not self.engine:
            raise Exception("Database not initialized")
            
        try:
            with self.engine.connect() as conn:
                # Create file_upload table - stores raw uploaded data as JSON
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS file_upload (
                        id SERIAL PRIMARY KEY,
                        file_name VARCHAR(255) NOT NULL,
                        file_path TEXT,
                        file_size INTEGER,
                        original_columns TEXT[],
                        raw_data JSONB NOT NULL,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        uploaded_by VARCHAR(100),
                        processing_status VARCHAR(50) DEFAULT 'pending',
                        processed_date TIMESTAMP NULL,
                        processing_error TEXT,
                        records_count INTEGER,
                        file_hash VARCHAR(64)
                    )
                """))
                
                # Create company_data table - stores processed data
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS company_data (
                        id SERIAL PRIMARY KEY,
                        company_name VARCHAR(255),
                        linkedin_url TEXT,
                        company_website TEXT,
                        company_size VARCHAR(100),
                        industry VARCHAR(255),
                        revenue VARCHAR(100),
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        file_source VARCHAR(255),
                        created_by VARCHAR(100),
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        file_upload_id INTEGER,
                        FOREIGN KEY (file_upload_id) REFERENCES file_upload(id)
                    )
                """))
                
                # Create upload_history table - tracks upload activities
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS upload_history (
                        id SERIAL PRIMARY KEY,
                        file_name VARCHAR(255),
                        file_path TEXT,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        records_count INTEGER,
                        status VARCHAR(50),
                        error_message TEXT,
                        uploaded_by VARCHAR(100),
                        file_upload_id INTEGER,
                        processing_duration_seconds INTEGER
                    )
                """))
                
                # Create processing_jobs table - for scheduled job tracking
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS processing_jobs (
                        id SERIAL PRIMARY KEY,
                        job_type VARCHAR(100) NOT NULL,
                        file_upload_id INTEGER,
                        job_status VARCHAR(50) DEFAULT 'queued',
                        scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        started_at TIMESTAMP NULL,
                        completed_at TIMESTAMP NULL,
                        error_message TEXT,
                        job_config JSONB,
                        retry_count INTEGER DEFAULT 0,
                        max_retries INTEGER DEFAULT 3
                    )
                """))
                
                # Create indexes for better performance
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_file_upload_status 
                    ON file_upload(processing_status)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_file_upload_date 
                    ON file_upload(upload_date)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_file_upload_hash 
                    ON file_upload(file_hash)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_company_data_name 
                    ON company_data(company_name)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_company_data_upload_date 
                    ON company_data(upload_date)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_company_data_file_upload_id
                    ON company_data(file_upload_id)
                """))

                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_upload_history_date 
                    ON upload_history(upload_date)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_processing_jobs_status 
                    ON processing_jobs(job_status)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_processing_jobs_scheduled 
                    ON processing_jobs(scheduled_at)
                """))
                
                conn.commit()
                logger.info("✅ Database tables created successfully")
                
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {str(e)}")
            raise
    
    def get_table_info(self) -> Dict[str, Any]:
        """Get information about existing tables"""
        if not self.engine:
            raise Exception("Database not initialized")
            
        try:
            with self.engine.connect() as conn:
                # Get table names
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result]
                
                table_info = {}
                for table in tables:
                    # Get column information
                    result = conn.execute(text(f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = '{table}'
                        ORDER BY ordinal_position
                    """))
                    
                    columns = []
                    for row in result:
                        columns.append({
                            'name': row[0],
                            'type': row[1],
                            'nullable': row[2] == 'YES'
                        })
                    
                    # Get row count
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    row_count = count_result.fetchone()[0]
                    
                    table_info[table] = {
                        'columns': columns,
                        'row_count': row_count
                    }
                
                return table_info
                
        except Exception as e:
            logger.error(f"❌ Failed to get table info: {str(e)}")
            return {}

def get_database_config() -> PostgreSQLConfig:
    """Get a configured database instance"""
    return PostgreSQLConfig()

def test_database_connection() -> bool:
    """Test database connection with current configuration"""
    config = get_database_config()
    return config.test_connection()

if __name__ == "__main__":
    # Test the configuration
    print("🔧 Testing PostgreSQL Configuration...")
    
    config = get_database_config()
    print(f"📋 Database URL: {config.get_database_url()}")
    
    if test_database_connection():
        print("✅ Database connection successful!")
        
        # Test database manager
        manager = DatabaseManager(config)
        if manager.initialize():
            print("✅ Database manager initialized!")
            
            try:
                manager.create_tables()
                print("✅ Tables created successfully!")
                
                table_info = manager.get_table_info()
                print(f"📊 Found {len(table_info)} tables:")
                for table_name, info in table_info.items():
                    print(f"  • {table_name}: {info['row_count']} rows, {len(info['columns'])} columns")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                
    else:
        print("❌ Database connection failed!")
        print("💡 Please check your PostgreSQL server and connection details.")