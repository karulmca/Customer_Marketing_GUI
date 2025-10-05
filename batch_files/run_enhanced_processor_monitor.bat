@echo off
echo =====================================
echo   Enhanced Processor Monitor
echo =====================================

REM Change to the project directory
cd /d "c:\Viji\Automation\NewCode\CompanyDataScraper"

echo.
echo Select Processing Mode:
echo 1. Single Run (process once and exit)
echo 2. Continuous Mode (process every 2 minutes)
echo 3. Statistics Only (show current stats)
echo 4. Custom Interval Continuous
echo.

set /p mode="Enter your choice (1-4): "

if "%mode%"=="1" (
    echo.
    echo Starting Single Run Mode...
    echo.
    python enhanced_scheduled_processor.py --mode single
) else if "%mode%"=="2" (
    echo.
    echo Starting Continuous Mode (2 minutes interval)...
    echo Press Ctrl+C to stop
    echo.
    python enhanced_scheduled_processor.py --mode continuous --interval 2
) else if "%mode%"=="3" (
    echo.
    echo Showing Processing Statistics...
    echo.
    python -c "
import sys
import os
sys.path.append('database_config')
from enhanced_scheduled_processor import EnhancedScheduledProcessor
processor = EnhancedScheduledProcessor()
processor.get_processing_statistics()
    "
) else if "%mode%"=="4" (
    set /p interval="Enter interval in minutes: "
    echo.
    echo Starting Continuous Mode with %interval% minutes interval...
    echo Press Ctrl+C to stop
    echo.
    python enhanced_scheduled_processor.py --mode continuous --interval %interval%
) else (
    echo Invalid choice. Exiting...
    goto end
)

:end
echo.
echo Processing completed or stopped.
pause