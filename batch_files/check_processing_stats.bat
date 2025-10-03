@echo off
echo =====================================
echo   Quick Processing Statistics
echo =====================================

REM Change to the project directory
cd /d "c:\Viji\Automation\NewCode\CompanyDataScraper"

echo.
echo Fetching current processing statistics...
echo.

python -c "import sys; sys.path.append('database_config'); from enhanced_scheduled_processor import EnhancedScheduledProcessor; processor = EnhancedScheduledProcessor(); processor.get_processing_statistics(); print('✅ Statistics retrieved successfully!')"

echo.
echo =====================================
pause