@echo off
REM Run both React frontend and FastAPI backend concurrently

echo 🚀 Starting Company Data Scraper React + FastAPI Application
echo.

REM Start FastAPI backend in a new window
echo 📡 Starting FastAPI backend...
start "FastAPI Backend" cmd /c "python backend_api/main.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start React frontend
echo 🌐 Starting React frontend...
cd frontend
npm start

pause