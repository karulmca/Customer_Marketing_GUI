@echo off
echo 🚀 Starting JSON File Upload GUI...
echo.

REM Change to the correct directory
cd /d "C:\Viji\Automation\NewCode\CompanyDataScraper"

REM Check if PostgreSQL is running
echo 🔍 Checking PostgreSQL connection...

REM Run the GUI
echo 📋 Launching GUI...
python gui\file_upload_json_gui.py

echo.
echo ✅ GUI session completed.
pause