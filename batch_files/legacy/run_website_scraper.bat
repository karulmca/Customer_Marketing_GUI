@echo off
:: Company Website Scraper - Alternative to LinkedIn
:: Often more successful than LinkedIn scraping

echo ========================================
echo Company Website Scraper
echo ========================================
echo.
echo This tool scrapes company websites instead of LinkedIn
echo Generally has higher success rates (30-60%%)
echo.

:: Set the script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Check if required packages are installed
echo Checking required Python packages...
python -c "import pandas, requests, bs4" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pandas requests beautifulsoup4 openpyxl lxml
)

:: Check if input file is provided
if "%~1"=="" (
    echo.
    echo Usage: %0 ^<excel_file^> [company_column] [website_column] [size_column]
    echo.
    echo Parameters:
    echo   excel_file      : Path to Excel file containing company names
    echo   company_column  : Column name containing company names (default: Company_Name)
    echo   website_column  : Column name containing websites (optional)
    echo   size_column     : Column name for company sizes (default: Company_Size)
    echo.
    echo Example:
    echo   %0 "companies.xlsx"
    echo   %0 "companies.xlsx" "Company_Name" "Website" "Company_Size"
    echo.
    pause
    exit /b 1
)

:: Set parameters
set INPUT_FILE=%~1
set COMPANY_COLUMN=%~2
set WEBSITE_COLUMN=%~3
set SIZE_COLUMN=%~4

:: Set defaults
if "%COMPANY_COLUMN%"=="" set COMPANY_COLUMN=Company_Name
if "%SIZE_COLUMN%"=="" set SIZE_COLUMN=Company_Size

:: Check if input file exists
if not exist "%INPUT_FILE%" (
    echo ERROR: Input file "%INPUT_FILE%" does not exist
    pause
    exit /b 1
)

:: Create backup
echo Creating backup...
copy "%INPUT_FILE%" "%INPUT_FILE%.backup" >nul

:: Build command
set PYTHON_CMD=python company_website_scraper.py "%INPUT_FILE%" --company-column "%COMPANY_COLUMN%" --size-column "%SIZE_COLUMN%"

if not "%WEBSITE_COLUMN%"=="" (
    set PYTHON_CMD=%PYTHON_CMD% --website-column "%WEBSITE_COLUMN%"
)

:: Display configuration
echo.
echo Configuration:
echo   Input File       : %INPUT_FILE%
echo   Company Column   : %COMPANY_COLUMN%
if not "%WEBSITE_COLUMN%"=="" (
    echo   Website Column   : %WEBSITE_COLUMN%
) else (
    echo   Website Column   : Auto-detect from company name
)
echo   Size Column      : %SIZE_COLUMN%
echo.
echo Expected Success Rate: 30-60%% (much better than LinkedIn!)
echo.

:: Confirm
set /p CONFIRM="Proceed with website scraping? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Operation cancelled
    pause
    exit /b 0
)

:: Run scraper
echo.
echo Starting company website scraping...
echo.
%PYTHON_CMD%

:: Check results
if errorlevel 1 (
    echo.
    echo ERROR: Script execution failed
    echo Check company_website_scraper.log for details
) else (
    echo.
    echo ========================================
    echo Website scraping completed!
    echo ========================================
    echo.
    echo Check the following files:
    echo   - Updated Excel file
    echo   - company_website_scraper.log
    echo   - %INPUT_FILE%.backup
)

pause