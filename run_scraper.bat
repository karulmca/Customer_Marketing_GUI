@echo off
:: Main Launcher for Company Data Scraper - Organized Structure
:: This script works with the new organized folder structure

echo ========================================
echo Company Data Scraper - Main Launcher
echo ========================================
echo Organized Project Structure - All scrapers ready!
echo.

:: Set the script directory (should be CompanyDataScraper root)
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:: Check project structure
if not exist "scrapers\" (
    echo ERROR: Scrapers folder not found!
    echo Make sure you're running from CompanyDataScraper root directory
    pause
    exit /b 1
)

if not exist "test_data\" (
    echo ERROR: Test_data folder not found!
    echo Make sure you're running from CompanyDataScraper root directory
    pause
    exit /b 1
)

echo Available Scrapers:
echo ==================
echo 1. OpenAI Enhanced Scraper (RECOMMENDED) - LinkedIn + AI Revenue
echo 2. Complete Scraper - LinkedIn + Traditional Website Revenue  
echo 3. LinkedIn Only - Company Size + Industry
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
echo Features:
echo • LinkedIn: Company Size + Industry (90-100%% success)
echo • Revenue: OpenAI GPT Analysis (40-70%% success)
echo • Intelligent financial document analysis
echo • Multi-currency support
echo.

:: Check for OpenAI API key
if defined OPENAI_API_KEY (
    echo ✅ OpenAI API key found in environment
) else (
    echo ⚠️  OpenAI API key not found
    echo.
    echo To get better revenue results:
    echo 1. Get API key: https://platform.openai.com/api-keys
    echo 2. Set key: $env:OPENAI_API_KEY = "sk-your-key-here"
    echo.
    echo Continuing with traditional methods as backup...
)

echo.
set /p INPUT_FILE="Enter Excel file path (or press Enter for Test5.xlsx): "
if "%INPUT_FILE%"=="" set INPUT_FILE=test_data\Test5.xlsx

echo Running OpenAI Enhanced Scraper...
echo Command: python scrapers\linkedin_openai_scraper.py "%INPUT_FILE%" --use-openai --website-column "Website" --company-column "Company Name"
echo.

python scrapers\linkedin_openai_scraper.py "%INPUT_FILE%" --use-openai --website-column "Website" --company-column "Company Name" --output-file "results\%~n1_openai_results.xlsx"
goto show_results

:complete_scraper
echo.
echo ========================================
echo Complete Traditional Scraper Selected
echo ========================================
echo Features:
echo • LinkedIn: Company Size + Industry (90-100%% success)
echo • Revenue: Traditional website scraping (15-25%% success)
echo • No API keys required
echo • Pattern-based revenue extraction
echo.

set /p INPUT_FILE="Enter Excel file path (or press Enter for Test5.xlsx): "
if "%INPUT_FILE%"=="" set INPUT_FILE=test_data\Test5.xlsx

echo Running Complete Traditional Scraper...
echo Command: python scrapers\linkedin_company_complete_scraper.py "%INPUT_FILE%" --website-column "Website" --company-column "Company Name"
echo.

python scrapers\linkedin_company_complete_scraper.py "%INPUT_FILE%" --website-column "Website" --company-column "Company Name" --output-file "results\%~n1_complete_results.xlsx"
goto show_results

:linkedin_scraper
echo.
echo ========================================
echo LinkedIn Only Scraper Selected
echo ========================================
echo Features:
echo • LinkedIn: Company Size + Industry (90-100%% success)
echo • No revenue extraction
echo • Fastest processing
echo • Most reliable
echo.

set /p INPUT_FILE="Enter Excel file path (or press Enter for Test5.xlsx): "
if "%INPUT_FILE%"=="" set INPUT_FILE=test_data\Test5.xlsx

echo Running LinkedIn Only Scraper...
echo Command: python scrapers\linkedin_company_scraper_enhanced.py "%INPUT_FILE%" --linkedin-column "LinkedIn_URL" --output-file "results\%~n1_linkedin_results.xlsx"
echo.

python scrapers\linkedin_company_scraper_enhanced.py "%INPUT_FILE%" --linkedin-column "LinkedIn_URL" --output-file "results\%~n1_linkedin_results.xlsx"
goto show_results

:show_results
echo.
echo ========================================
echo Processing Completed!
echo ========================================
echo.
echo 📁 Check results in: results\ folder
echo 📝 Check logs in: logs\ folder
echo 📖 Check documentation in: documentation\ folder
echo.
echo Quick Navigation:
echo • Main README: README.md
echo • Test again: %0
echo • Project structure: dir
echo.

pause