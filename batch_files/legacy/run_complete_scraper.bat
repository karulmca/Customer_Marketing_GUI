@echo off
echo Complete Company Data Scraper (LinkedIn + ZoomInfo Revenue)
echo ===========================================================

REM Check if input file is provided
if "%1"=="" (
    echo Usage: run_complete_scraper.bat input_file.xlsx [options]
    echo.
    echo Examples:
    echo   run_complete_scraper.bat companies.xlsx
    echo   run_complete_scraper.bat companies.xlsx --wait-min 15 --wait-max 25
    echo.
    echo Required Excel columns:
    echo   - Company_Name: Name of the company (REQUIRED)
    echo   - LinkedIn_URL: LinkedIn company page URL (optional)
    echo   - Website_URL: Company website URL (optional)
    echo.
    echo The scraper will extract:
    echo   - Company size and industry from LinkedIn
    echo   - Revenue information from ZoomInfo
    echo.
    pause
    exit /b 1
)

REM Set the input file
set INPUT_FILE=%1

REM Check if the input file exists
if not exist "%INPUT_FILE%" (
    echo Error: Input file "%INPUT_FILE%" not found!
    pause
    exit /b 1
)

echo Starting Complete Company Data Scraper...
echo Input file: %INPUT_FILE%
echo.

REM Shift to get additional arguments
shift
set ARGS=
:loop
if "%1"=="" goto endloop
set ARGS=%ARGS% %1
shift
goto loop
:endloop

REM Run the Python script with all arguments
python complete_company_scraper.py "%INPUT_FILE%" %ARGS%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Complete Company Data Scraper completed successfully!
    echo Check the output Excel file for LinkedIn and ZoomInfo revenue data.
) else (
    echo.
    echo ✗ Complete Company Data Scraper failed with error code %ERRORLEVEL%
    echo Check the log file: complete_company_scraper.log
)

echo.
pause