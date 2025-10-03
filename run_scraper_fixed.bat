@echo off
:: Fixed Easy Launcher for Company Data Scraper - Works with organized structure

echo ========================================
echo Company Data Scraper - Easy Launcher
echo ========================================
echo Organized Structure - All scrapers ready!
echo Working Directory: %CD%
echo ========================================
echo.

:: Make sure we're in the right directory
if not exist "scrapers\" (
    echo ERROR: Not in CompanyDataScraper directory!
    echo Please navigate to: c:\Viji\Automation\NewCode\CompanyDataScraper
    echo Then run: .\run_scraper_fixed.bat
    pause
    exit /b 1
)

echo Available Test Files:
echo =====================
dir /b test_data\*.xlsx 2>nul
echo.

echo Available Scrapers:
echo ==================
echo 1. OpenAI Enhanced Scraper (RECOMMENDED)
echo    • LinkedIn: Company Size + Industry (90-100%% success)
echo    • Revenue: OpenAI GPT Analysis (40-70%% success)
echo    • Cost: ~$0.001-0.003 per company
echo.
echo 2. Complete Traditional Scraper
echo    • LinkedIn: Company Size + Industry (90-100%% success)  
echo    • Revenue: Traditional patterns (15-25%% success)
echo    • Free - no API required
echo.
echo 3. LinkedIn Only Scraper
echo    • LinkedIn: Company Size + Industry only
echo    • Fastest processing
echo    • Most reliable
echo.
echo 4. Exit
echo.

set /p CHOICE="Select scraper (1-4): "

if "%CHOICE%"=="1" goto openai_scraper
if "%CHOICE%"=="2" goto complete_scraper  
if "%CHOICE%"=="3" goto linkedin_scraper
if "%CHOICE%"=="4" exit /b 0

echo Invalid choice. Please select 1-4.
pause
goto :EOF

:openai_scraper
echo.
echo ========================================
echo OpenAI Enhanced Scraper Selected
echo ========================================

:: Check for OpenAI API key
if defined OPENAI_API_KEY (
    echo ✅ OpenAI API key found: %OPENAI_API_KEY:~0,20%...
    echo ✅ Ready for enhanced revenue extraction!
) else (
    echo ⚠️  OpenAI API key not found
    echo.
    echo To enable OpenAI (recommended):
    echo 1. Get API key: https://platform.openai.com/api-keys
    echo 2. Set in PowerShell: $env:OPENAI_API_KEY = "sk-your-key-here"
    echo.
    echo Continuing with traditional backup methods...
)

echo.
set /p INPUT_FILE="Enter Excel file path (or press Enter for test_data\Test5.xlsx): "
if "%INPUT_FILE%"=="" set INPUT_FILE=test_data\Test5.xlsx

echo.
echo Running OpenAI Enhanced Scraper...
echo File: %INPUT_FILE%
echo Command: python scrapers\linkedin_openai_scraper.py "%INPUT_FILE%" --use-openai --website-column "Website" --company-column "Company Name"
echo.

python scrapers\linkedin_openai_scraper.py "%INPUT_FILE%" --use-openai --website-column "Website" --company-column "Company Name"
goto show_results

:complete_scraper
echo.
echo ========================================
echo Complete Traditional Scraper Selected
echo ========================================
echo • LinkedIn: Company Size + Industry (90-100%% success)
echo • Revenue: Pattern matching (15-25%% success)
echo • No API keys required
echo.

set /p INPUT_FILE="Enter Excel file path (or press Enter for test_data\Test5.xlsx): "
if "%INPUT_FILE%"=="" set INPUT_FILE=test_data\Test5.xlsx

echo.
echo Running Complete Traditional Scraper...
echo File: %INPUT_FILE%
echo Command: python scrapers\linkedin_company_complete_scraper.py "%INPUT_FILE%" --website-column "Website" --company-column "Company Name"
echo.

python scrapers\linkedin_company_complete_scraper.py "%INPUT_FILE%" --website-column "Website" --company-column "Company Name"
goto show_results

:linkedin_scraper
echo.
echo ========================================
echo LinkedIn Only Scraper Selected
echo ========================================
echo • LinkedIn: Company Size + Industry only
echo • No revenue extraction
echo • Fastest and most reliable
echo.

set /p INPUT_FILE="Enter Excel file path (or press Enter for test_data\Test5.xlsx): "
if "%INPUT_FILE%"=="" set INPUT_FILE=test_data\Test5.xlsx

echo.
echo Running LinkedIn Only Scraper...
echo File: %INPUT_FILE%
echo Command: python scrapers\linkedin_company_scraper_enhanced.py "%INPUT_FILE%" --linkedin-column "LinkedIn_URL"
echo.

python scrapers\linkedin_company_scraper_enhanced.py "%INPUT_FILE%" --linkedin-column "LinkedIn_URL"
goto show_results

:show_results
echo.
echo ========================================
echo Processing Completed!
echo ========================================
echo.

:: Show results
echo 📊 Results Summary:
if exist "%INPUT_FILE:~0,-5%_openai_results.xlsx" (
    echo ✅ OpenAI results: %INPUT_FILE:~0,-5%_openai_results.xlsx
)
if exist "%INPUT_FILE:~0,-5%_complete_results.xlsx" (
    echo ✅ Complete results: %INPUT_FILE:~0,-5%_complete_results.xlsx  
)
if exist "%INPUT_FILE:~0,-5%_linkedin_results.xlsx" (
    echo ✅ LinkedIn results: %INPUT_FILE:~0,-5%_linkedin_results.xlsx
)

echo.
echo 📁 Check files in:
echo   • test_data\ folder (input files and results)
echo   • results\ folder (if output directed there)
echo   • logs\ folder (processing logs)
echo.
echo 🔄 Run again? Execute: .\run_scraper_fixed.bat
echo 📖 Documentation: .\documentation\ folder
echo.

pause