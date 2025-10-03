@echo off
echo 🚀 Enhanced Scheduled Processor - Single Run
echo Processing pending files using LinkedIn scraper logic...
echo.

REM Change to the correct directory
cd /d "C:\Viji\Automation\NewCode\CompanyDataScraper"

REM Run single processing cycle
echo 🔄 Running single processing cycle...
python enhanced_scheduled_processor.py --mode single --scraper-type complete

echo.
echo ✅ Processing cycle completed.
pause