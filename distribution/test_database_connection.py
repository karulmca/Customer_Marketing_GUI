"""
Database Connection Test for Executable
Quick test to verify database connectivity
"""
import os
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def test_database_connection():
    """Test database connection from executable environment"""
    try:
        print("🔍 Testing database connection...")
        print(f"📍 Current directory: {current_dir}")
        
        # Check for .env file
        env_file = current_dir / ".env"
        print(f"🔍 Looking for .env at: {env_file}")
        
        if env_file.exists():
            print("✅ .env file found")
            
            # Try to load and test database connection
            from database_config.postgresql_config import PostgreSQLConfig
            
            config = PostgreSQLConfig()
            print("✅ PostgreSQL config loaded")
            
            # Test connection
            if config.test_connection():
                print("✅ Database connection successful!")
                return True
            else:
                print("❌ Database connection failed")
                return False
                
        else:
            print("❌ .env file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_database_connection()
    input("Press Enter to exit...")