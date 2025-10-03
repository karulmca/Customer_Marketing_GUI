@echo off
:: Scheduled File Processor - Single Run
:: Processes all pending file uploads once

echo ========================================
echo Scheduled File Processor - Single Run
echo ========================================
echo Processing pending file uploads...
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

echo Starting scheduled file processing...
echo Check logs\scheduled_processor.log for detailed progress...
echo.

python scheduled_processor.py --mode single

if errorlevel 1 (
    echo ERROR: Scheduled processing failed
    echo Check logs\scheduled_processor.log for details
    pause
    exit /b 1
)

echo.
echo ========================================
echo Scheduled processing completed!
echo Check logs\scheduled_processor.log for details
echo ========================================
pause