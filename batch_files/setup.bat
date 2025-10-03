@echo off
:: Setup script for LinkedIn Company Size Scraper

echo ========================================
echo LinkedIn Company Size Scraper Setup
echo ========================================
echo.

:: Set the script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:: Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
) else (
    echo Python is installed
    python --version
)

echo.
echo Installing required Python packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install required packages
    echo Try running as administrator or check your internet connection
    pause
    exit /b 1
) else (
    echo All packages installed successfully!
)

echo.
echo Creating sample Excel file...
python create_sample_excel.py

if errorlevel 1 (
    echo WARNING: Could not create sample Excel file
) else (
    echo Sample Excel file created: sample_companies.xlsx
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Files created:
echo   - sample_companies.xlsx (sample Excel file)
echo   - All required Python packages installed
echo.
echo To run the scraper:
echo   1. Prepare your Excel file with LinkedIn URLs
echo   2. Run: run_linkedin_scraper.bat "your_file.xlsx"
echo   3. Or double-click run_linkedin_scraper.bat and follow prompts
echo.
echo For help, see README.md
echo.

pause