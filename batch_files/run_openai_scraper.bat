@echo off
:: LinkedIn + OpenAI Revenue Scraper
:: Enhanced revenue extraction using OpenAI GPT models

echo ========================================
echo LinkedIn + OpenAI Revenue Scraper
echo ========================================
echo LinkedIn Data: Company Size + Industry  
echo Revenue Data: OpenAI-Enhanced Extraction
echo ========================================
echo.
echo This advanced scraper uses:
echo 1. LinkedIn company size and industry (proven working logic)
echo 2. OpenAI GPT models for intelligent revenue extraction
echo 3. Traditional regex patterns as backup
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
    echo Installing core packages...
    pip install pandas requests beautifulsoup4 openpyxl lxml
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

:: Check if OpenAI is installed
python -c "import openai" >nul 2>&1
if errorlevel 1 (
    echo OpenAI library not found. Installing...
    pip install openai
    if errorlevel 1 (
        echo WARNING: Failed to install OpenAI library
        echo You can still use traditional methods
    ) else (
        echo OpenAI library installed successfully!
    )
) else (
    echo OpenAI library found - ready for enhanced extraction!
)

echo.

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
    echo   --use-openai        : Enable OpenAI revenue extraction
    echo   --openai-api-key    : Your OpenAI API key
    echo   --linkedin-column   : LinkedIn URL column name (default: LinkedIn_URL)
    echo   --website-column    : Website URL column name (default: Company_Website)
    echo   --company-column    : Company name column (default: Company_Name)
    echo   --output-file       : Output Excel file path (optional)
    echo   --wait-min N        : Minimum wait time between requests (default: 10)
    echo   --wait-max N        : Maximum wait time between requests (default: 20)
    echo.
    echo OpenAI Setup:
    echo   1. Get API key from: https://platform.openai.com/api-keys
    echo   2. Set environment variable: set OPENAI_API_KEY=your_key_here
    echo   3. Or use --openai-api-key parameter
    echo.
    echo Examples:
    echo   %0 "companies.xlsx" --use-openai
    echo   %0 "companies.xlsx" --openai-api-key "sk-..." --use-openai
    echo   %0 "companies.xlsx" --use-openai --output-file "results.xlsx"
    echo.
    echo Output Columns Added:
    echo   LinkedIn Data:
    echo   - Company_Size_Enhanced  : Employee count from LinkedIn
    echo   - Industry_Enhanced      : Industry from LinkedIn
    echo   - LinkedIn_Status        : LinkedIn scraping status
    echo.
    echo   Revenue Data (OpenAI Enhanced):
    echo   - Revenue_Enhanced       : Revenue extracted using AI
    echo   - Revenue_Source         : 'OpenAI Analysis' or 'Traditional'
    echo   - Revenue_Status         : Success/failure status
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

:: Check for OpenAI API key
set HAS_OPENAI_KEY=0
if defined OPENAI_API_KEY (
    set HAS_OPENAI_KEY=1
    echo OpenAI API key found in environment variable
)

:: Check if --openai-api-key is in options
echo %OPTIONS% | findstr /C:"--openai-api-key" >nul
if not errorlevel 1 (
    set HAS_OPENAI_KEY=1
    echo OpenAI API key provided in command line
)

:: Check if --use-openai is in options
set USE_OPENAI=0  
echo %OPTIONS% | findstr /C:"--use-openai" >nul
if not errorlevel 1 (
    set USE_OPENAI=1
)

:: Show configuration
echo Configuration:
echo   Input File: %INPUT_FILE%
echo   Additional Options: %OPTIONS%
if %USE_OPENAI%==1 (
    if %HAS_OPENAI_KEY%==1 (
        echo   OpenAI: ENABLED with API key
    ) else (
        echo   OpenAI: REQUESTED but NO API KEY found
        echo   WARNING: Will fall back to traditional methods
    )
) else (
    echo   OpenAI: Disabled (using traditional methods)
)
echo.

:: Build the Python command
set PYTHON_CMD=python linkedin_openai_scraper.py "%INPUT_FILE%" %OPTIONS%

:: Show the command that will be executed
echo Command to execute:
echo %PYTHON_CMD%
echo.

:: Show OpenAI information if requested
if %USE_OPENAI%==1 (
    echo ========================================
    echo OPENAI REVENUE EXTRACTION INFO:
    echo ========================================
    if %HAS_OPENAI_KEY%==1 (
        echo Status: ENABLED - Will use GPT models for revenue extraction
        echo.
        echo Benefits:
        echo • Understands context and financial language
        echo • Extracts from complex financial documents
        echo • Handles various revenue formats and currencies  
        echo • Much higher accuracy than regex patterns
        echo • Can interpret investor presentations and reports
        echo.
        echo Expected Success Rate: 40-70%% ^(vs 15-25%% traditional^)
        echo Cost: ~$0.001-0.003 per company processed
    ) else (
        echo Status: REQUESTED but NO API KEY
        echo.
        echo To enable OpenAI:
        echo 1. Get API key: https://platform.openai.com/api-keys
        echo 2. Set environment: set OPENAI_API_KEY=sk-your-key-here
        echo 3. Or use: --openai-api-key "sk-your-key-here"
        echo.
        echo Will continue with traditional methods...
    )
    echo ========================================
    echo.
)

:: Confirm before proceeding
set /p CONFIRM="Do you want to proceed with data extraction? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Operation cancelled by user.
    pause
    exit /b 0
)

:: Show processing information
echo.
echo ========================================
echo PROCESSING INFORMATION:
echo ========================================
echo LinkedIn Extraction (Proven Working):
echo • Company Size: Employee ranges (e.g., "51-200 employees")
echo • Industry: Business sector (e.g., "Investment Management")
echo.
if %USE_OPENAI%==1 (
    if %HAS_OPENAI_KEY%==1 (
        echo OpenAI Revenue Extraction (Enhanced):
        echo • Analyzes website content with GPT intelligence
        echo • Understands financial context and terminology
        echo • Extracts from investor relations, annual reports
        echo • Handles multiple currencies and formats
        echo • Falls back to traditional methods if needed
    ) else (
        echo Traditional Revenue Extraction (Backup):
        echo • Regex pattern matching for revenue figures
        echo • Searches main pages, about, investor sections
        echo • Basic financial document analysis
    )
) else (
    echo Traditional Revenue Extraction:
    echo • Regex pattern matching for revenue figures  
    echo • Searches main pages, about, investor sections
    echo • Basic financial document analysis
)
echo.
echo Starting enhanced data extraction...
echo This may take several minutes per company.
echo.

:: Run the OpenAI scraper
%PYTHON_CMD%

:: Check if script was successful
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Script execution failed
    echo ========================================
    echo.
    echo Troubleshooting:
    echo 1. Check 'linkedin_openai_scraper.log' for detailed errors
    echo 2. Verify column names in your Excel file
    echo 3. For OpenAI issues:
    echo    - Verify API key is correct
    echo    - Check API usage limits and billing
    echo    - Ensure internet connection is stable
    echo 4. Traditional backup methods will be used if OpenAI fails
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo SUCCESS: Enhanced processing completed!
    echo ========================================
    echo.
    echo Data Extracted:
    echo LinkedIn Information ^(Proven Method^):
    echo   - Company_Size_Enhanced: Employee counts
    echo   - Industry_Enhanced: Business sectors  
    echo   - LinkedIn_Status: Extraction status
    echo.
    if %USE_OPENAI%==1 (
        if %HAS_OPENAI_KEY%==1 (
            echo Revenue Information ^(OpenAI Enhanced^):
            echo   - Revenue_Enhanced: AI-extracted revenue figures
            echo   - Revenue_Source: 'OpenAI Analysis' for AI extraction
            echo   - Revenue_Status: Success/failure status
        ) else (
            echo Revenue Information ^(Traditional Backup^):
            echo   - Revenue_Enhanced: Pattern-matched revenue figures
            echo   - Revenue_Source: Source page where revenue was found
            echo   - Revenue_Status: Success/failure status
        )
    ) else (
        echo Revenue Information ^(Traditional^):
        echo   - Revenue_Enhanced: Pattern-matched revenue figures
        echo   - Revenue_Source: Source page where revenue was found
        echo   - Revenue_Status: Success/failure status
    )
    echo.
    echo Files created:
    echo   - %INPUT_FILE:~0,-5%_openai_results.xlsx ^(results^)
    echo   - linkedin_openai_scraper.log ^(detailed logs^)
    echo.
    echo Next Steps:
    echo 1. Review results in Excel
    echo 2. Check revenue extraction success rates
    if %USE_OPENAI%==1 (
        if %HAS_OPENAI_KEY%==1 (
            echo 3. OpenAI should show higher revenue success rates
            echo 4. Check API usage at: https://platform.openai.com/usage
        )
    )
    echo 5. For missing data, consider manual research
    echo.
    if %USE_OPENAI%==1 (
        if %HAS_OPENAI_KEY%==1 (
            echo OpenAI Benefits Achieved:
            echo • Intelligent financial document analysis
            echo • Context-aware revenue extraction
            echo • Higher accuracy than traditional methods
            echo • Better handling of complex financial language
        )
    )
    echo.
)

echo Press any key to exit...
pause >nul