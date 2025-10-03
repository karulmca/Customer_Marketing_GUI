@echo off
:: LinkedIn Company Size Scraper Batch File
:: This script processes Excel files to extract company sizes from LinkedIn URLs

echo ========================================
echo LinkedIn Company Size Scraper
echo ========================================
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
python -c "import pandas, requests, bs4" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pandas requests beautifulsoup4 openpyxl lxml
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

:: Check if input file is provided as argument
if "%~1"=="" (
    echo.
    echo Usage: %0 ^<excel_file^> [url_column] [size_column] [output_file]
    echo.
    echo Parameters:
    echo   excel_file    : Path to Excel file containing LinkedIn URLs
    echo   url_column    : Column name containing LinkedIn URLs (default: LinkedIn_URL)
    echo   size_column   : Column name for company sizes (default: Company_Size)
    echo   output_file   : Output Excel file path (optional, defaults to input file)
    echo.
    echo Example:
    echo   %0 "companies.xlsx"
    echo   %0 "companies.xlsx" "LinkedIn_URL" "Company_Size" "output.xlsx"
    echo.
    pause
    exit /b 1
)

:: Set parameters
set INPUT_FILE=%~1
set URL_COLUMN=%~2
set SIZE_COLUMN=%~3
set OUTPUT_FILE=%~4

:: Set defaults if not provided
if "%URL_COLUMN%"=="" set URL_COLUMN=LinkedIn_URL
if "%SIZE_COLUMN%"=="" set SIZE_COLUMN=Company_Size

:: Check if input file exists
if not exist "%INPUT_FILE%" (
    echo ERROR: Input file "%INPUT_FILE%" does not exist
    pause
    exit /b 1
)

:: Create backup of input file
echo Creating backup of input file...
copy "%INPUT_FILE%" "%INPUT_FILE%.backup" >nul
if errorlevel 1 (
    echo WARNING: Could not create backup file
) else (
    echo Backup created: %INPUT_FILE%.backup
)

:: Build Python command
set PYTHON_CMD=python linkedin_company_scraper.py "%INPUT_FILE%" --url-column "%URL_COLUMN%" --size-column "%SIZE_COLUMN%"

if not "%OUTPUT_FILE%"=="" (
    set PYTHON_CMD=%PYTHON_CMD% --output-file "%OUTPUT_FILE%"
)

:: Display configuration
echo.
echo Configuration:
echo   Input File    : %INPUT_FILE%
echo   URL Column    : %URL_COLUMN%
echo   Size Column   : %SIZE_COLUMN%
if not "%OUTPUT_FILE%"=="" (
    echo   Output File   : %OUTPUT_FILE%
) else (
    echo   Output File   : %INPUT_FILE% (same as input)
)
echo.

:: Confirm before proceeding
set /p CONFIRM="Do you want to proceed? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Operation cancelled
    pause
    exit /b 0
)

:: Run the scraper
echo.
echo Starting LinkedIn company size extraction...
echo.
%PYTHON_CMD%

:: Check if script was successful
if errorlevel 1 (
    echo.
    echo ERROR: Script execution failed
    echo Check the log file 'linkedin_scraper.log' for details
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo Processing completed successfully!
    echo ========================================
    echo.
    echo Check the following files:
    echo   - Updated Excel file
    echo   - linkedin_scraper.log (for detailed logs)
    echo   - %INPUT_FILE%.backup (backup of original file)
    echo.
)

pause