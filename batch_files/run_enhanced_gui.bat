@echo off
:: Enhanced LinkedIn Company Data Scraper - Updated for organized structure
:: Extracts both company size AND industry from LinkedIn URLs

echo ========================================
echo LinkedIn Company Data Scraper - Enhanced
echo ========================================
echo This version extracts BOTH:
echo • Company Size: "201-500 employees"
echo • Industry: "Financial Services"
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
python -c "import pandas, requests, bs4, tkinter" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pandas requests beautifulsoup4 openpyxl tkinter
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
    echo Required packages installed successfully!
)

echo Starting LinkedIn Company Data Scraper - Enhanced GUI...
python gui\linkedin_data_scraper_gui_fixed.py

if errorlevel 1 (
    echo ERROR: Failed to start Enhanced GUI
    echo.
    echo Troubleshooting:
    echo 1. Make sure you're in the CompanyDataScraper directory
    echo 2. Check that gui\linkedin_data_scraper_gui.py exists
    echo 3. Verify Python and packages are installed correctly
    echo.
    pause
    exit /b 1
)

echo Enhanced GUI closed successfully.
pause