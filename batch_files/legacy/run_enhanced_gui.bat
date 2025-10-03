@echo off
:: Run LinkedIn Company Data Scraper - Enhanced GUI (Size + Industry)

echo ========================================
echo LinkedIn Company Data Scraper - Enhanced
echo ========================================
echo This version extracts BOTH:
echo • Company Size: "201-500 employees"
echo • Industry: "Financial Services"
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

:: Run the Enhanced GUI
echo Starting LinkedIn Company Data Scraper - Enhanced GUI...
python linkedin_data_scraper_gui.py

if errorlevel 1 (
    echo ERROR: Failed to start Enhanced GUI
    pause
    exit /b 1
)

echo Enhanced GUI closed.
pause