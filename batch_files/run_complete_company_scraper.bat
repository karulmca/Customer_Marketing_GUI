@echo off
:: Enhanced LinkedIn + Website Revenue Scraper
:: Extracts: Company Size & Industry (LinkedIn) + Revenue (Company Websites)

echo ========================================
echo Complete Company Data Scraper
echo ========================================
echo LinkedIn Data: Company Size + Industry
echo Website Data: Revenue Information
echo ========================================
echo.
echo This scraper combines:
echo 1. LinkedIn company size and industry (existing working logic)
echo 2. Revenue extraction from company websites (open source)
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
    echo Usage: %0 ^<excel_file^> [options]
    echo.
    echo Parameters:
    echo   excel_file          : Path to Excel file containing company data
    echo.
    echo Required Columns in Excel:
    echo   - LinkedIn_URL      : LinkedIn company page URLs
    echo   - Company_Website   : Company website URLs  
    echo   - Company_Name      : Company names (optional)
    echo.
    echo Options:
    echo   --linkedin-column   : LinkedIn URL column name (default: LinkedIn_URL)
    echo   --website-column    : Website URL column name (default: Company_Website)
    echo   --company-column    : Company name column (default: Company_Name)
    echo   --output-file       : Output Excel file path (optional)
    echo   --wait-min N        : Minimum wait time between requests (default: 10)
    echo   --wait-max N        : Maximum wait time between requests (default: 20)
    echo.
    echo Examples:
    echo   %0 "companies.xlsx"
    echo   %0 "companies.xlsx" --output-file "results.xlsx"
    echo   %0 "companies.xlsx" --wait-min 15 --wait-max 25
    echo.
    echo Output Columns Added:
    echo   LinkedIn Data:
    echo   - Company_Size_Enhanced  : Employee count from LinkedIn
    echo   - Industry_Enhanced      : Industry from LinkedIn
    echo   - LinkedIn_Status        : LinkedIn scraping status
    echo.
    echo   Revenue Data:
    echo   - Revenue_Enhanced       : Revenue from company website
    echo   - Revenue_Source         : Source page where revenue was found
    echo   - Revenue_Status         : Website scraping status
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

:: Show configuration
echo Configuration:
echo   Input File: %INPUT_FILE%
echo   Additional Options: %OPTIONS%
echo.

:: Build the Python command
set PYTHON_CMD=python linkedin_company_complete_scraper.py "%INPUT_FILE%" %OPTIONS%

:: Show the command that will be executed
echo Command to execute:
echo %PYTHON_CMD%
echo.

:: Confirm before proceeding
set /p CONFIRM="Do you want to proceed with complete data scraping? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Operation cancelled by user.
    pause
    exit /b 0
)

:: Show important information
echo.
echo ========================================
echo PROCESSING INFORMATION:
echo ========================================
echo LinkedIn Extraction:
echo • Company Size: Employee ranges (e.g., "51-200 employees")
echo • Industry: Business sector (e.g., "Financial Services")
echo • Uses existing working LinkedIn logic
echo.
echo Website Revenue Extraction:
echo • Searches company websites for revenue information
echo • Checks: Main page, About, Investor Relations, Financial pages
echo • Patterns: Annual revenue, sales figures, financial reports
echo • Open source methods only - no paid APIs
echo.
echo Expected Success Rates:
echo • LinkedIn (Size/Industry): 10-30%%
echo • Website Revenue: 15-25%% (higher for public companies)
echo.
echo Starting complete data extraction...
echo This may take several minutes depending on dataset size.
echo.

:: Run the complete scraper
%PYTHON_CMD%

:: Check if script was successful
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Script execution failed
    echo ========================================
    echo.
    echo Troubleshooting:
    echo 1. Check 'linkedin_complete_scraper.log' for detailed errors
    echo 2. Verify column names in your Excel file:
    echo    - LinkedIn_URL (LinkedIn company pages)
    echo    - Company_Website (company websites)
    echo    - Company_Name (company names)
    echo 3. Check internet connection
    echo 4. Try increasing wait times if getting blocked
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo SUCCESS: Complete processing finished!
    echo ========================================
    echo.
    echo Data Extracted:
    echo LinkedIn Information:
    echo   - Company_Size_Enhanced: Employee counts
    echo   - Industry_Enhanced: Business sectors  
    echo   - LinkedIn_Status: Extraction status
    echo.
    echo Revenue Information:
    echo   - Revenue_Enhanced: Revenue figures
    echo   - Revenue_Source: Where revenue was found
    echo   - Revenue_Status: Extraction status
    echo.
    echo Files created:
    echo   - %INPUT_FILE% (updated with new columns)
    echo   - linkedin_complete_scraper.log (detailed logs)
    echo.
    echo Next Steps:
    echo 1. Review results in Excel
    echo 2. Check success rates for each data type
    echo 3. For missing data, consider:
    echo    - Manual research for important companies
    echo    - Alternative data sources
    echo    - Paid business intelligence tools
    echo.
    echo Note: Revenue extraction uses open source methods only.
    echo Public companies typically have higher success rates.
    echo.
)

echo Press any key to exit...
pause >nul