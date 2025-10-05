"""
Database Setup and Testing Script
Run this to set up and test your PostgreSQL database connection
"""

import os
import sys

def main():
    print("🗄️ PostgreSQL Database Setup")
    print("=" * 50)
    
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        from db_utils import check_database_requirements, get_database_connection, install_requirements
        
        # Check requirements
        print("1️⃣ Checking Requirements...")
        requirements = check_database_requirements()
        
        all_good = True
        for key, value in requirements.items():
            status = "✅" if value else "❌"
            print(f"   {status} {key.replace('_', ' ').title()}")
            if not value:
                all_good = False
        
        # Install missing requirements
        if not requirements.get("postgresql_available", False):
            print("\n2️⃣ Installing PostgreSQL packages...")
            if install_requirements():
                print("✅ Requirements installed! Please restart the script.")
                return
            else:
                print("❌ Failed to install requirements")
                return
        
        # Test connection
        print("\n3️⃣ Testing Database Connection...")
        db = get_database_connection("postgresql")
        
        if not db:
            print("❌ Failed to create database connection object")
            return
        
        if not db.test_connection():
            print("❌ Database connection failed!")
            print("\n🔧 Troubleshooting:")
            print("   • Check if PostgreSQL server is running")
            print("   • Verify connection details in .env file")
            print("   • Ensure database 'FileUpload' exists")
            print("   • Check username and password")
            return
        
        print("✅ Database connection successful!")
        
        # Initialize database
        print("\n4️⃣ Initializing Database...")
        if not db.connect():
            print("❌ Failed to initialize database manager")
            return
        
        print("✅ Database manager initialized!")
        
        # Create tables
        print("\n5️⃣ Creating Tables...")
        if db.create_tables():
            print("✅ Tables created successfully!")
        else:
            print("❌ Failed to create tables")
            return
        
        # Get database statistics
        print("\n6️⃣ Database Statistics:")
        stats = db.get_table_stats()
        if stats:
            for table_name, info in stats.items():
                print(f"   📋 {table_name}:")
                print(f"      • Records: {info['row_count']}")
                print(f"      • Columns: {len(info['columns'])}")
                for col in info['columns']:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    print(f"        - {col['name']} ({col['type']}) {nullable}")
        else:
            print("   ℹ️ No tables found or error retrieving stats")
        
        print("\n🎉 Database setup completed successfully!")
        print("\n📋 Next Steps:")
        print("   • Your database is ready to use")
        print("   • Run the file upload GUI to start uploading data")
        print("   • Connection details are stored in database_config/.env")
        
        db.close()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required packages are installed")
    except Exception as e:
        print(f"❌ Setup failed: {e}")

if __name__ == "__main__":
    main()