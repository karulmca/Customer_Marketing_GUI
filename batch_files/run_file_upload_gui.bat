@echo off
:: File Upload & Database Manager GUI
:: Handles file uploads and saves data to backend database

echo ========================================
echo File Upload and Database Manager
echo ========================================
echo Features:
echo - File Upload (Excel/CSV)
echo - Database Integration (SQLite)
echo - Data Preview and Validation
echo - Export and Backup Functions
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
python -c "import pandas, sqlite3, tkinter" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pandas openpyxl tkinter
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
    echo Required packages installed successfully!
)

echo Starting File Upload and Database Manager GUI...
echo Window will appear with database integration...
python gui\file_upload_database_gui.py

if errorlevel 1 (
    echo ERROR: Failed to start File Upload and Database GUI
    echo.
    echo Troubleshooting:
    echo 1. Make sure you're in the CompanyDataScraper directory
    echo 2. Check that gui\file_upload_database_gui.py exists
    echo 3. Verify Python and packages are installed correctly
    echo 4. Try running: python gui\file_upload_database_gui.py
    echo.
    pause
    exit /b 1
)

echo File Upload and Database GUI closed successfully.
pause