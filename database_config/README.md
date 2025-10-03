# PostgreSQL Database Configuration Files

This folder contains configuration and connection management for PostgreSQL database integration.

## Files:

### 📄 `.env`
Environment configuration file with database connection details:
- Database URL and connection parameters
- Pool settings and timeouts
- SSL and security configurations

### 🐍 `postgresql_config.py`
Main PostgreSQL configuration and connection manager:
- `PostgreSQLConfig`: Configuration loading and management
- `DatabaseManager`: Database operations and table creation
- Connection pooling and SQLAlchemy integration

### 🔧 `db_utils.py`
Database utility functions and helpers:
- `DatabaseConnection`: Unified database interface
- DataFrame insertion and querying
- Connection testing and statistics

### ⚙️ `setup_database.py`
Database setup and testing script:
- Requirement checking and installation
- Database initialization and table creation
- Connection testing and troubleshooting

## Connection Details:

```
Database: FileUpload
Host: localhost
Port: 5432
Username: postgres
Password: Neha2713
URL: postgresql://postgres:Neha2713@localhost:5432/FileUpload
```

## Quick Start:

1. **Install Requirements:**
   ```bash
   pip install psycopg2-binary sqlalchemy pandas
   ```

2. **Setup Database:**
   ```bash
   python database_config/setup_database.py
   ```

3. **Test Connection:**
   ```bash
   python database_config/postgresql_config.py
   ```

## Tables Created:

### `company_data`
- id (SERIAL PRIMARY KEY)
- company_name (VARCHAR)
- linkedin_url (TEXT)
- company_website (TEXT)
- company_size (VARCHAR)
- industry (VARCHAR)
- revenue (VARCHAR)
- upload_date (TIMESTAMP)
- file_source (VARCHAR)
- created_by (VARCHAR)
- updated_at (TIMESTAMP)

### `upload_history`
- id (SERIAL PRIMARY KEY)
- file_name (VARCHAR)
- file_path (TEXT)
- upload_date (TIMESTAMP)
- records_count (INTEGER)
- status (VARCHAR)
- error_message (TEXT)
- uploaded_by (VARCHAR)

## Security Notes:

⚠️ **Important:** The `.env` file contains sensitive database credentials. 
- Keep it secure and never commit to version control
- Consider using environment variables in production
- Update default passwords before deployment

## Usage in Applications:

```python
from database_config.db_utils import get_database_connection

# Get database connection
db = get_database_connection("postgresql")

# Test connection
if db.test_connection():
    print("Connected!")
    
    # Connect and create tables
    if db.connect():
        db.create_tables()
        
        # Insert DataFrame
        db.insert_dataframe(your_dataframe)
        
        # Query data
        results = db.get_all_records()
        
    db.close()
```