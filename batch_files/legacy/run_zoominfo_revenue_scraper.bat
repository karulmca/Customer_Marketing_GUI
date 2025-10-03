@echo off
echo ZoomInfo Revenue Scraper
echo ========================

REM Check if input file is provided
if "%1"=="" (
    echo Usage: run_zoominfo_revenue_scraper.bat input_file.xlsx [options]
    echo.
    echo Examples:
    echo   run_zoominfo_revenue_scraper.bat companies.xlsx
    echo   run_zoominfo_revenue_scraper.bat companies.xlsx --wait-min 3 --wait-max 8
    echo.
    echo Required Excel columns:
    echo   - Company_Name: Name of the company
    echo   - Website_URL: Company website URL
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

echo Starting ZoomInfo Revenue Scraper...
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
python zoominfo_revenue_scraper.py "%INPUT_FILE%" %ARGS%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ ZoomInfo Revenue Scraper completed successfully!
    echo Check the output Excel file for results.
) else (
    echo.
    echo ✗ ZoomInfo Revenue Scraper failed with error code %ERRORLEVEL%
    echo Check the log file: zoominfo_revenue_scraper.log
)

echo.
pause