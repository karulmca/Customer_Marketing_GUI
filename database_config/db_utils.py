"""
Database connection utilities and helpers
Provides easy-to-use functions for database operations
"""

import os
import sys
from typing import Optional, Dict, Any, List
import pandas as pd

# Add the database_config directory to the path
sys.path.append(os.path.dirname(__file__))

try:
    from postgresql_config import PostgreSQLConfig, DatabaseManager
    POSTGRESQL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  PostgreSQL dependencies not available: {e}")
    print("💡 Install with: pip install psycopg2-binary sqlalchemy")
    POSTGRESQL_AVAILABLE = False

class DatabaseConnection:
    """Unified database connection interface"""
    
    def __init__(self, db_type: str = "postgresql"):
        self.db_type = db_type
        self.config = None
        self.manager = None
        
        if db_type == "postgresql" and POSTGRESQL_AVAILABLE:
            self.config = PostgreSQLConfig()
            self.manager = DatabaseManager(self.config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def connect(self) -> bool:
        """Connect to the database"""
        if not self.manager:
            return False
            
        return self.manager.initialize()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        if not self.config:
            return False
            
        return self.config.test_connection()
    
    def create_tables(self) -> bool:
        """Create required tables"""
        try:
            if not self.manager:
                return False
                
            self.manager.create_tables()
            return True
        except Exception as e:
            print(f"❌ Failed to create tables: {str(e)}")
            return False
    
    def insert_dataframe(self, df: pd.DataFrame, table_name: str = "company_data") -> bool:
        """Insert pandas DataFrame into database table"""
        try:
            if not self.manager or not self.manager.engine:
                print("❌ Database not connected")
                return False

            from datetime import datetime
            import json
            from sqlalchemy import MetaData, Table
            from sqlalchemy.dialects.postgresql import JSONB
            from sqlalchemy.types import DateTime, JSON as SQLAlchemyJSON

            table = Table(table_name, MetaData(), autoload_with=self.manager.engine)
            records = df.astype(object).where(pd.notnull(df), None).to_dict(orient='records')

            for record in records:
                for column_name, value in record.items():
                    column = table.columns.get(column_name)
                    if column is None or value is None:
                        continue

                    if isinstance(column.type, (SQLAlchemyJSON, JSONB)) and isinstance(value, str):
                        try:
                            record[column_name] = json.loads(value)
                        except json.JSONDecodeError:
                            pass
                    elif isinstance(column.type, DateTime) and isinstance(value, str):
                        record[column_name] = pd.to_datetime(value).to_pydatetime()

            chunk_size = 500
            with self.manager.engine.begin() as conn:
                for i in range(0, len(records), chunk_size):
                    conn.execute(table.insert(), records[i:i + chunk_size])

            print(f"✅ Inserted {len(records)} records into {table_name} using SQLAlchemy Core")
            return True

        except Exception as e:
            import traceback
            print(f"❌ Failed to insert DataFrame: {str(e)}")
            print(traceback.format_exc())
            return False
    
    def query_to_dataframe(self, query: str) -> Optional[pd.DataFrame]:
        """Execute query and return results as DataFrame"""
        try:
            if not self.manager or not self.manager.engine:
                print("❌ Database not connected")
                return None
            
            df = pd.read_sql_query(query, self.manager.engine)
            return df
            
        except Exception as e:
            print(f"❌ Query failed: {str(e)}")
            return None
    
    def execute_query(self, query: str) -> bool:
        """Execute non-SELECT queries (INSERT, UPDATE, DELETE)"""
        try:
            if not self.manager or not self.manager.engine:
                print("❌ Database not connected")
                return False
            
            from sqlalchemy import text
            with self.manager.engine.connect() as connection:
                result = connection.execute(text(query))
                connection.commit()
                print(f"✅ Query executed successfully. Affected rows: {result.rowcount if hasattr(result, 'rowcount') else 'N/A'}")
                return True
            
        except Exception as e:
            print(f"❌ Query execution failed: {str(e)}")
            return False
    
    def get_all_records(self, table_name: str = "company_data") -> Optional[pd.DataFrame]:
        """Get all records from a table"""
        query = f"SELECT * FROM {table_name} ORDER BY upload_date DESC"
        return self.query_to_dataframe(query)
    
    def get_table_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            if not self.manager:
                return {}
            
            return self.manager.get_table_info()
            
        except Exception as e:
            print(f"❌ Failed to get table stats: {str(e)}")
            return {}
    
    def close(self):
        """Close database connections"""
        if self.config:
            self.config.close_connections()

def get_database_connection(db_type: str = "postgresql") -> Optional[DatabaseConnection]:
    """Get a database connection instance"""
    try:
        return DatabaseConnection(db_type)
    except Exception as e:
        print(f"❌ Failed to create database connection: {str(e)}")
        return None

def check_database_requirements() -> Dict[str, bool]:
    """Check if database requirements are met"""
    requirements = {
        "postgresql_available": POSTGRESQL_AVAILABLE,
        "config_file_exists": False,
        "connection_working": False
    }
    
    # Check if config file exists
    config_path = os.path.join(os.path.dirname(__file__), '.env')
    requirements["config_file_exists"] = os.path.exists(config_path)
    
    # Test connection if PostgreSQL is available
    if POSTGRESQL_AVAILABLE:
        try:
            config = PostgreSQLConfig()
            requirements["connection_working"] = config.test_connection()
        except:
            requirements["connection_working"] = False
    
    return requirements

def install_requirements():
    """Install required packages for PostgreSQL"""
    try:
        import subprocess
        import sys
        
        packages = ["psycopg2-binary", "sqlalchemy", "pandas"]
        
        print("📦 Installing PostgreSQL requirements...")
        for package in packages:
            print(f"  Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("✅ All requirements installed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to install requirements: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Database Configuration Test")
    print("=" * 50)
    
    # Check requirements
    req = check_database_requirements()
    
    print("📋 Requirements Check:")
    for key, value in req.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key.replace('_', ' ').title()}: {value}")
    
    if not req["postgresql_available"]:
        print("\n💡 Installing PostgreSQL requirements...")
        if install_requirements():
            print("🔄 Please restart and try again.")
        sys.exit(1)
    
    if not req["config_file_exists"]:
        print("\n❌ Configuration file not found!")
        print(f"📁 Expected: {os.path.join(os.path.dirname(__file__), '.env')}")
        sys.exit(1)
    
    # Test connection
    print("\n🔗 Testing Database Connection...")
    db = get_database_connection()
    
    if db and db.test_connection():
        print("✅ Database connection successful!")
        
        if db.connect():
            print("✅ Database manager initialized!")
            
            # Create tables
            if db.create_tables():
                print("✅ Tables created/verified!")
            
            # Get stats
            stats = db.get_table_stats()
            if stats:
                print(f"\n📊 Database Statistics:")
                for table, info in stats.items():
                    print(f"  📋 {table}: {info['row_count']} rows")
        
        db.close()
    else:
        print("❌ Database connection failed!")
        print("💡 Please check your PostgreSQL server and credentials.")