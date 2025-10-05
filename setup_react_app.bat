@echo off
REM Setup script for React + FastAPI architecture (Windows)

echo 🚀 Setting up Company Data Scraper React + FastAPI Architecture

REM Install FastAPI backend dependencies
echo 📦 Installing Python backend dependencies...
cd backend_api
pip install -r requirements.txt
cd ..

REM Install React frontend dependencies
echo 📦 Installing React frontend dependencies...
cd frontend
npm install
cd ..

echo ✅ Setup complete!
echo.
echo 🔧 To run the application:
echo 1. Start the FastAPI backend: python backend_api/main.py
echo 2. Start the React frontend: cd frontend ^&^& npm start
echo.
echo 📱 The React app will be available at: http://localhost:3000
echo 🔌 The FastAPI backend will be available at: http://localhost:8000

pause