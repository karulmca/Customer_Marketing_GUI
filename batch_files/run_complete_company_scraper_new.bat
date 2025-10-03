@echo off
:: Complete Company Scraper - Updated for organized structure  
:: LinkedIn + Traditional Website Revenue

echo ========================================
echo Complete Company Data Scraper
echo ========================================
echo LinkedIn Data: Company Size + Industry
echo Website Data: Revenue Information
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
echo Checking required Python packages...
python -c "import pandas, requests, bs4, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pandas requests beautifulsoup4 openpyxl lxml
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
    echo Required packages installed successfully.
)

:: Check if input file is provided
if "%~1"=="" (
    echo.
    echo Usage: %0 ^<excel_file^> [options]
    echo.
    echo Parameters:
    echo   excel_file          : Path to Excel file containing company data
    echo.
    echo Required Columns:
    echo   - LinkedIn_URL      : LinkedIn company page URLs
    echo   - Company_Website   : Company website URLs  
    echo   - Company_Name      : Company names (optional)
    echo.
    echo Options:
    echo   --linkedin-column   : LinkedIn URL column (default: LinkedIn_URL)
    echo   --website-column    : Website URL column (default: Company_Website)
    echo   --company-column    : Company name column (default: Company_Name)
    echo   --output-file       : Output Excel file path (optional)
    echo.
    echo Examples:
    echo   %0 "test_data\Test5.xlsx"
    echo   %0 "test_data\Test5.xlsx" --website-column "Website" --company-column "Company Name"
    echo.
    pause
    exit /b 1
)

:: Set parameters
set INPUT_FILE=%~1
shift
set OPTIONS=%1 %2 %3 %4 %5 %6 %7 %8 %9

:: Check if input file exists
if not exist "%INPUT_FILE%" (
    echo ERROR: Input file "%INPUT_FILE%" does not exist
    echo Please check the file path and try again.
    pause
    exit /b 1
)

:: Build Python command with correct path
set PYTHON_CMD=python scrapers\linkedin_company_complete_scraper.py "%INPUT_FILE%" %OPTIONS%

:: Show configuration
echo Configuration:
echo   Input File: %INPUT_FILE%
echo   Options: %OPTIONS%
echo   Working Directory: %CD%
echo   Command: %PYTHON_CMD%
echo.

:: Confirm before proceeding
set /p CONFIRM="Do you want to proceed with complete data extraction? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Operation cancelled by user.
    pause
    exit /b 0
)

echo.
echo ========================================
echo PROCESSING STARTED
echo ========================================
echo LinkedIn: Company Size + Industry extraction
echo Website: Traditional revenue extraction
echo.

:: Run the scraper
%PYTHON_CMD%

:: Check results
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Processing failed
    echo ========================================
    echo Check logs\ folder for detailed error information
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo SUCCESS: Processing completed!
    echo ========================================
    echo Results saved to: results\ folder
    echo Logs saved to: logs\ folder
    echo.
)

pause