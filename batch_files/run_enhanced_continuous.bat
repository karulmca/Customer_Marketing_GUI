@echo off
echo 🔄 Enhanced Continuous Processor
echo Processing pending files every 30 minutes using LinkedIn scraper...
echo Press Ctrl+C to stop
echo.

REM Change to the correct directory
cd /d "C:\Viji\Automation\NewCode\CompanyDataScraper"

REM Run continuous processing
echo 🔄 Starting continuous processing mode...
python enhanced_scheduled_processor.py --mode continuous --interval 30 --scraper-type complete

echo.
echo ✅ Continuous processing stopped.
pause