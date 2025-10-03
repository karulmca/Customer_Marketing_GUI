@echo off
:: File Upload & PostgreSQL Manager - JSON Storage GUI
:: Uploads files as JSON for scheduled processing

echo ========================================
echo File Upload PostgreSQL Manager - JSON Storage
echo ========================================
echo Features:
echo - File Upload stored as JSON data
echo - Scheduled processing jobs
echo - Processing status monitoring  
echo - Job management and statistics
echo - Separate staging and processing workflow
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
python -c "import pandas, psycopg2, sqlalchemy, tkinter, json" >nul 2>&1
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

echo Starting File Upload JSON Storage GUI...
echo Window will appear with JSON storage workflow...
python gui\file_upload_json_gui.py

if errorlevel 1 (
    echo ERROR: Failed to start File Upload JSON GUI
    echo.
    echo Troubleshooting:
    echo 1. Make sure you're in the CompanyDataScraper directory
    echo 2. Check that gui\file_upload_json_gui.py exists
    echo 3. Verify Python and packages are installed correctly
    echo 4. Ensure PostgreSQL server is running
    echo 5. Check database connection in database_config\.env
    echo 6. Try running: python gui\file_upload_json_gui.py
    echo.
    pause
    exit /b 1
)

echo File Upload JSON Storage GUI closed successfully.
pause