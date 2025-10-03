@echo off
:: File Upload & PostgreSQL Database Manager GUI
:: Handles file uploads and saves data to PostgreSQL database

echo ========================================
echo File Upload and PostgreSQL Manager
echo ========================================
echo Features:
echo - File Upload (Excel/CSV)
echo - PostgreSQL Database Integration
echo - Data Preview and Validation
echo - Export and Data Management
echo - Upload History Tracking
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

:: Check if required packages are installed
echo Checking required packages...
python -c "import pandas, psycopg2, sqlalchemy, tkinter" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pandas openpyxl psycopg2-binary sqlalchemy tkinter python-dotenv
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
    echo Required packages installed successfully!
)

echo Starting File Upload and PostgreSQL Manager GUI...
echo Window will appear with PostgreSQL integration...
python gui\file_upload_postgresql_gui.py

if errorlevel 1 (
    echo ERROR: Failed to start File Upload and PostgreSQL GUI
    echo.
    echo Troubleshooting:
    echo 1. Make sure you're in the CompanyDataScraper directory
    echo 2. Check that gui\file_upload_postgresql_gui.py exists
    echo 3. Verify Python and packages are installed correctly
    echo 4. Ensure PostgreSQL server is running
    echo 5. Check database connection in database_config\.env
    echo 6. Try running: python gui\file_upload_postgresql_gui.py
    echo.
    pause
    exit /b 1
)

echo File Upload and PostgreSQL GUI closed successfully.
pause