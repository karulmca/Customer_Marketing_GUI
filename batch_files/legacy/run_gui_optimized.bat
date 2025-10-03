@echo off
:: Run LinkedIn Company Size Scraper - Optimized GUI

echo ========================================
echo LinkedIn Company Size Scraper - Optimized GUI
echo ========================================
echo This version extracts EXACT LinkedIn ranges:
echo "1-10 employees", "11-50 employees", "201-500 employees"
echo ========================================
echo.

:: Set the script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run setup.bat first
    pause
    exit /b 1
)

:: Check if required packages are installed
echo Checking required packages...
python -c "import pandas, requests, bs4, tkinter" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pandas requests beautifulsoup4 openpyxl lxml
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        echo Please run setup.bat first
        pause
        exit /b 1
    )
)

:: Run the Optimized GUI
echo Starting LinkedIn Company Size Scraper - Optimized GUI...
python linkedin_scraper_gui_optimized.py

if errorlevel 1 (
    echo ERROR: Failed to start GUI
    pause
    exit /b 1
)

echo GUI closed.
pause