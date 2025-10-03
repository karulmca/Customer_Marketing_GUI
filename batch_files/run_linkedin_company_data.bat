@echo off
:: Enhanced LinkedIn Company Data Scraper (Size + Industry)
:: Extracts both company size and industry from LinkedIn URLs

echo ========================================
echo LinkedIn Company Data Scraper (Enhanced)
echo Extracts: Company Size AND Industry
echo ========================================
echo.
echo NOTE: LinkedIn actively blocks scraping attempts.
echo Expected success rate: 10-30%% for company size/industry
echo This version extracts BOTH size and industry data.
echo.

:: Set the script directory
set SCRIPT_DIR=%~dp0
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
    echo.
)

:: Check if input file is provided as argument
if "%~1"=="" (
    echo.
    echo Usage: %0 ^<excel_file^> [linkedin_column] [output_file] [options]
    echo.
    echo Parameters:
    echo   excel_file      : Path to Excel file containing LinkedIn URLs
    echo   linkedin_column : Column name with LinkedIn URLs (default: LinkedIn_URL)
    echo   output_file     : Output Excel file path (optional)
    echo.
    echo Options:
    echo   --wait-min N    : Minimum wait time between requests (default: 10)
    echo   --wait-max N    : Maximum wait time between requests (default: 20)
    echo   --company-col   : Company name column (default: Company_Name)
    echo.
    echo Examples:
    echo   %0 "companies.xlsx"
    echo   %0 "companies.xlsx" "LinkedIn_URL" "results.xlsx"
    echo   %0 "companies.xlsx" "LinkedIn_URL" "results.xlsx" --wait-min 15 --wait-max 25
    echo.
    echo Output Columns Added:
    echo   - Company_Size_Enhanced    : Company size from LinkedIn
    echo   - Industry_Enhanced        : Industry from LinkedIn  
    echo   - LinkedIn_Status          : Scraping status
    echo.
    pause
    exit /b 1
)

:: Set parameters with defaults
set INPUT_FILE=%~1
set LINKEDIN_COLUMN=%~2
set OUTPUT_FILE=%~3

:: Set defaults if not provided
if "%LINKEDIN_COLUMN%"=="" set LINKEDIN_COLUMN=LinkedIn_URL

:: Set remaining arguments for options
set OPTIONS=%4 %5 %6 %7 %8 %9

:: Check if input file exists
if not exist "%INPUT_FILE%" (
    echo ERROR: Input file "%INPUT_FILE%" does not exist
    echo Please check the file path and try again.
    pause
    exit /b 1
)

:: Show configuration
echo Configuration:
echo   Input File: %INPUT_FILE%
echo   LinkedIn Column: %LINKEDIN_COLUMN%
if not "%OUTPUT_FILE%"=="" (
    echo   Output File: %OUTPUT_FILE%
) else (
    echo   Output File: [Same as input file with timestamp]
)
echo   Additional Options: %OPTIONS%
echo.

:: Build the Python command
set PYTHON_CMD=python linkedin_company_scraper_enhanced.py "%INPUT_FILE%" --linkedin-column "%LINKEDIN_COLUMN%"

:: Add output file if specified
if not "%OUTPUT_FILE%"=="" (
    set PYTHON_CMD=%PYTHON_CMD% --output-file "%OUTPUT_FILE%"
)

:: Add additional options
if not "%OPTIONS%"=="" (
    set PYTHON_CMD=%PYTHON_CMD% %OPTIONS%
)

:: Show the command that will be executed
echo Command to execute:
echo %PYTHON_CMD%
echo.

:: Confirm before proceeding
set /p CONFIRM="Do you want to proceed with LinkedIn scraping? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Operation cancelled by user.
    pause
    exit /b 0
)

:: Show important warnings
echo.
echo ========================================
echo IMPORTANT WARNINGS:
echo ========================================
echo 1. LinkedIn may block or rate-limit requests
echo 2. Use reasonable delays between requests
echo 3. Success rate varies (10-30%% typical)
echo 4. Monitor linkedin_scraper.log for issues
echo 5. Consider using LinkedIn Sales Navigator for higher success rates
echo.
echo Starting LinkedIn data extraction...
echo Both Company Size AND Industry will be extracted.
echo.

:: Run the enhanced scraper
%PYTHON_CMD%

:: Check if script was successful
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Script execution failed
    echo ========================================
    echo.
    echo Troubleshooting:
    echo 1. Check 'linkedin_scraper.log' for detailed error messages
    echo 2. Verify LinkedIn URLs are valid in your Excel file
    echo 3. Try increasing wait times: --wait-min 15 --wait-max 30
    echo 4. Check if LinkedIn is blocking your IP address
    echo 5. Consider using a VPN or different network
    echo.
    echo Common issues:
    echo - Rate limiting: Use longer delays between requests
    echo - Blocked URLs: LinkedIn detected automated access
    echo - Network issues: Check internet connection
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo SUCCESS: Processing completed!
    echo ========================================
    echo.
    echo Results:
    echo   - Company Size data extracted to 'Company_Size_Enhanced' column
    echo   - Industry data extracted to 'Industry_Enhanced' column
    echo   - Status information in 'LinkedIn_Status' column
    echo   - Detailed logs in 'linkedin_scraper.log'
    echo.
    echo Files created/updated:
    if not "%OUTPUT_FILE%"=="" (
        echo   - %OUTPUT_FILE% (results file)
    ) else (
        echo   - %INPUT_FILE% (updated with new columns)
    )
    echo   - linkedin_scraper.log (execution log)
    echo.
    echo Next Steps:
    echo 1. Review the results in Excel
    echo 2. Check success rate and data quality
    echo 3. For companies without data, consider:
    echo    - Manual LinkedIn research
    echo    - Alternative data sources
    echo    - ZoomInfo or other business databases
    echo.
)

echo Press any key to exit...
pause >nul