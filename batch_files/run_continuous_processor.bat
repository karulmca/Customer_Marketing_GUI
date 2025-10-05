@echo off
:: Scheduled File Processor - Continuous Mode
:: Uses interval from config.json

echo ========================================
echo Scheduled File Processor - Continuous Mode
echo ========================================
echo Using scheduler interval from config.json
echo Press Ctrl+C to stop
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

echo Starting continuous file processing...
echo Check logs\scheduled_processor.log for detailed progress...
echo.
echo Press Ctrl+C to stop continuous processing
echo.

python scheduled_processor.py --mode continuous --interval 2

echo.
echo ========================================
echo Continuous processing stopped
echo ========================================
pause