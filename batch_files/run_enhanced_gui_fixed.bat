@echo off
:: Enhanced LinkedIn Company Data Scraper - FIXED VERSION
:: Extracts Company Size + Industry + Revenue from LinkedIn + Websites

echo ========================================
echo LinkedIn Company Data Scraper - FIXED Enhanced
echo ========================================
echo This FIXED version extracts:
echo • Company Size: "201-500 employees"  
echo • Industry: "Financial Services"
echo • Revenue: From company websites
echo • OpenAI Integration: Available
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
python -c "import pandas, requests, bs4, tkinter, subprocess" >nul 2>&1
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

echo Starting LinkedIn Company Data Scraper - FIXED Enhanced GUI...
echo 🚀 Window will appear with enhanced visibility...
python gui\linkedin_data_scraper_gui_fixed.py

if errorlevel 1 (
    echo ERROR: Failed to start FIXED Enhanced GUI
    echo.
    echo Troubleshooting:
    echo 1. Make sure you're in the CompanyDataScraper directory
    echo 2. Check that gui\linkedin_data_scraper_gui_fixed.py exists
    echo 3. Verify Python and packages are installed correctly
    echo 4. Try running: python gui\linkedin_data_scraper_gui_fixed.py
    echo.
    pause
    exit /b 1
)

echo FIXED Enhanced GUI closed successfully.
pause