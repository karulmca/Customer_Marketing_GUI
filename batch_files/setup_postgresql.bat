@echo off
:: PostgreSQL Database Setup Script
:: Sets up database connection and creates required tables

echo ========================================
echo PostgreSQL Database Setup
echo ========================================
echo Database: FileUpload
echo Host: localhost:5432
echo User: postgres
echo ========================================
echo.

:: Set the script directory to project root
set SCRIPT_DIR=%~dp0..
cd /d "%SCRIPT_DIR%"

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

:: Install PostgreSQL requirements
echo Installing PostgreSQL requirements...
pip install psycopg2-binary sqlalchemy pandas python-dotenv
if errorlevel 1 (
    echo WARNING: Some packages may have failed to install
    echo Continuing with setup...
)

echo.
echo Running database setup script...
python database_config\setup_database.py

if errorlevel 1 (
    echo ERROR: Database setup failed
    echo.
    echo Troubleshooting:
    echo 1. Make sure PostgreSQL server is running
    echo 2. Check database connection details in database_config\.env
    echo 3. Ensure database 'FileUpload' exists
    echo 4. Verify username and password are correct
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Database setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Run file upload GUI to start using the database
echo 2. Connection details are stored in database_config\.env
echo 3. Tables have been created and are ready for use
echo.
pause