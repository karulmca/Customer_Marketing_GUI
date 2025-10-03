@echo off
echo ====================================================
echo     Company Data Scraper - Secure Launch
echo ====================================================
echo.
echo Starting authenticated application...
echo.

cd /d "%~dp0"
python secure_app_launcher.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ====================================================
    echo Error: Application failed to start
    echo Please check your Python installation and dependencies
    echo ====================================================
    pause
)