@echo off
echo =====================================
echo   Test Enhanced Processing Workflow
echo =====================================

REM Change to the project directory
cd /d "c:\Viji\Automation\NewCode\CompanyDataScraper"

echo.
echo This will test the complete enhanced processing workflow:
echo 1. Check database connection
echo 2. Show initial statistics
echo 3. Process any pending files
echo 4. Show final statistics
echo.

set /p confirm="Continue with test? (y/n): "

if /i "%confirm%" neq "y" (
    echo Test cancelled.
    goto end
)

echo.
echo =====================================
echo   Step 1: Database Connection Test
echo =====================================

python -c "import sys; sys.path.append('database_config'); from postgresql_config import PostgreSQLConfig; config = PostgreSQLConfig(); connection = config.get_connection(); print('✅ Database connection successful!'); connection.close()"

if errorlevel 1 (
    echo.
    echo Database connection failed. Please check PostgreSQL server.
    goto end
)

echo.
echo =====================================
echo   Step 2: Initial Statistics
echo =====================================

python -c "import sys; sys.path.append('database_config'); from enhanced_scheduled_processor import EnhancedScheduledProcessor; processor = EnhancedScheduledProcessor(); processor.get_processing_statistics()"

echo.
echo =====================================
echo   Step 3: Processing Pending Files
echo =====================================

python enhanced_scheduled_processor.py --mode single

echo.
echo =====================================
echo   Test Complete
echo =====================================

echo.
echo Workflow test completed!
echo Check the logs above for any issues.

:end
echo.
pause