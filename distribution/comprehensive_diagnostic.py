"""
Comprehensive Database Connection Diagnostics for Executable
Detailed analysis of what's going wrong
"""
import os
import sys
from pathlib import Path

def comprehensive_diagnostic():
    """Run comprehensive diagnostic of the executable environment"""
    print("=" * 60)
    print("🔍 COMPREHENSIVE DATABASE CONNECTION DIAGNOSTIC")
    print("=" * 60)
    
    # Get current directory and execution context
    current_dir = Path(__file__).parent.absolute()
    print(f"📍 Current directory: {current_dir}")
    print(f"📍 Python executable: {sys.executable}")
    print(f"📍 Python path: {sys.path[:3]}...")  # Show first 3 paths
    
    # Check file structure
    print("\n📁 FILE STRUCTURE CHECK:")
    files_to_check = ['.env', 'database_config', 'CompanyDataScraper.exe']
    for file_name in files_to_check:
        file_path = current_dir / file_name
        if file_path.exists():
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"  ✅ {file_name} (file, {size:,} bytes)")
            else:
                print(f"  ✅ {file_name} (directory)")
        else:
            print(f"  ❌ {file_name} (missing)")
    
    # Check .env file contents
    print("\n📋 .ENV FILE CHECK:")
    env_file = current_dir / '.env'
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                lines = f.readlines()
            print(f"  ✅ .env file has {len(lines)} lines")
            
            # Look for key variables
            key_vars = ['DATABASE_URL', 'DB_HOST', 'DB_NAME']
            found_vars = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key = line.split('=')[0].strip()
                    if key in key_vars:
                        found_vars.append(key)
            
            print(f"  ✅ Found key variables: {found_vars}")
            
        except Exception as e:
            print(f"  ❌ Error reading .env: {e}")
    else:
        print("  ❌ .env file not found")
    
    # Test module imports
    print("\n📦 MODULE IMPORT CHECK:")
    modules_to_test = [
        'database_config',
        'database_config.postgresql_config',
        'database_config.db_utils'
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}")
        except ImportError as e:
            print(f"  ❌ {module_name}: {e}")
        except Exception as e:
            print(f"  ⚠️ {module_name}: {e}")
    
    # Test database connection with detailed error info
    print("\n🔗 DATABASE CONNECTION TEST:")
    try:
        from database_config.postgresql_config import PostgreSQLConfig
        print("  ✅ PostgreSQL config imported")
        
        config = PostgreSQLConfig()
        print("  ✅ Config object created")
        
        print(f"  📋 Config file used: {getattr(config, 'config_file', 'unknown')}")
        print(f"  📋 Config items loaded: {len(getattr(config, 'config', {}))}")
        
        # Test connection with detailed error
        if hasattr(config, 'test_connection'):
            result = config.test_connection()
            if result:
                print("  ✅ Database connection successful!")
            else:
                print("  ❌ Database connection failed")
        else:
            print("  ⚠️ test_connection method not available")
            
    except Exception as e:
        print(f"  ❌ Database connection error: {e}")
        import traceback
        print(f"  📄 Full traceback:")
        print("  " + "\n  ".join(traceback.format_exc().split('\n')))
    
    print("\n" + "=" * 60)
    print("🔍 DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    comprehensive_diagnostic()
    input("\nPress Enter to exit...")