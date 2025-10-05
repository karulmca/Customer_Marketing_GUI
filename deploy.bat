@echo off

REM Production deployment script for Company Data Scraper (Windows)

echo 🚀 Starting production deployment...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Check if .env.production exists
if not exist ".env.production" (
    echo ❌ .env.production file not found. Please create it from .env.production template.
    exit /b 1
)

REM Create necessary directories
if not exist "ssl" mkdir ssl
if not exist "database_config" mkdir database_config

REM Build and start services
echo 🔨 Building Docker images...
docker-compose -f docker-compose.prod.yml build --no-cache

echo 🗄️ Starting database...
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d database

echo ⏳ Waiting for database to be ready...
timeout /t 30 /nobreak >nul

echo 🌐 Starting backend services...
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d backend redis

echo ⏳ Waiting for backend to be ready...
timeout /t 20 /nobreak >nul

echo 🖥️ Starting frontend...
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d frontend

echo 🔍 Checking service health...
docker-compose -f docker-compose.prod.yml ps

echo ✅ Production deployment complete!
echo.
echo Services are running on:
echo - Frontend: http://localhost (port 80)
echo - Backend API: http://localhost:8000
echo - Database: localhost:5432
echo.
echo To view logs: docker-compose -f docker-compose.prod.yml logs -f [service_name]
echo To stop services: docker-compose -f docker-compose.prod.yml down

pause