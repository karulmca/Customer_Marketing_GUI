#!/bin/bash

# Production deployment script for Company Data Scraper

set -e

echo "🚀 Starting production deployment..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ .env.production file not found. Please create it from .env.production template."
    exit 1
fi

# Create necessary directories
mkdir -p ssl
mkdir -p database_config

# Build and start services
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🗄️ Starting database..."
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d database

echo "⏳ Waiting for database to be ready..."
sleep 30

echo "🌐 Starting backend services..."
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d backend redis

echo "⏳ Waiting for backend to be ready..."
sleep 20

echo "🖥️ Starting frontend..."
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d frontend

echo "🔍 Checking service health..."
docker-compose -f docker-compose.prod.yml ps

echo "✅ Production deployment complete!"
echo ""
echo "Services are running on:"
echo "- Frontend: http://localhost (port 80)"
echo "- Backend API: http://localhost:8000"
echo "- Database: localhost:5432"
echo ""
echo "To view logs: docker-compose -f docker-compose.prod.yml logs -f [service_name]"
echo "To stop services: docker-compose -f docker-compose.prod.yml down"