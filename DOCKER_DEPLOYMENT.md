# Docker Production Deployment Guide

This guide explains how to deploy the Company Data Scraper application using Docker containers for production environments.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM
- 10GB free disk space

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repository-url>
cd CompanyDataScraper
```

### 2. Configure Environment

Copy the production environment template:
```bash
cp .env.production.template .env.production
```

Edit `.env.production` and set your values:
```bash
# Database Configuration
POSTGRES_DB=company_scraper
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_db_password

# Redis Configuration  
REDIS_PASSWORD=your_redis_password

# Application Security
SECRET_KEY=your_very_long_random_secret_key

# Environment
ENVIRONMENT=production
```

### 3. Deploy

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```cmd
deploy.bat
```

### 4. Verify Deployment

Check if all services are running:
```bash
docker-compose -f docker-compose.prod.yml ps
```

Access the application:
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🏗️ Architecture

The Docker setup includes:

- **Frontend**: React app served by Nginx (Port 80/443)
- **Backend**: FastAPI application (Port 8000)
- **Database**: PostgreSQL 15 (Port 5432)
- **Cache**: Redis (Port 6379)

## 📁 Docker Files

- `docker-compose.yml` - Development environment
- `docker-compose.prod.yml` - Production environment
- `backend_api/Dockerfile` - Backend container
- `frontend/Dockerfile` - Frontend container
- `frontend/nginx.conf` - Nginx configuration
- `.dockerignore` - Files to exclude from build

## 🔧 Management Commands

### Start Services
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Scale Services
```bash
# Scale backend to 3 instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Update Application
```bash
# Rebuild and restart
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Security Considerations

### SSL/TLS Setup

1. Place SSL certificates in `ssl/` directory:
   ```
   ssl/
   ├── certificate.crt
   └── private.key
   ```

2. Update `frontend/nginx.conf` for HTTPS:
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /etc/nginx/ssl/certificate.crt;
       ssl_certificate_key /etc/nginx/ssl/private.key;
       # ... rest of config
   }
   ```

### Environment Security

- Use strong, unique passwords
- Never commit `.env.production` to version control
- Regularly rotate secrets
- Use Docker secrets for sensitive data in production

## 📊 Monitoring

### Health Checks

All services include health checks:
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:80`
- Database: PostgreSQL ready check
- Redis: Ping command

### Resource Monitoring

```bash
# Container resource usage
docker stats

# Service-specific stats
docker stats company_scraper_backend_prod
```

## 🗄️ Data Persistence

Persistent volumes:
- `postgres_data_prod` - Database data
- `redis_data_prod` - Redis cache
- `backend_logs_prod` - Application logs
- `file_uploads_prod` - Uploaded files

### Backup Database

```bash
docker exec company_scraper_db_prod pg_dump -U postgres company_scraper > backup.sql
```

### Restore Database

```bash
docker exec -i company_scraper_db_prod psql -U postgres company_scraper < backup.sql
```

## 🚨 Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check system resources
docker system df
```

**Database connection errors:**
```bash
# Verify database is running
docker-compose -f docker-compose.prod.yml exec database pg_isready

# Check connection from backend
docker-compose -f docker-compose.prod.yml exec backend curl http://localhost:8000/health
```

**Frontend not loading:**
```bash
# Check nginx logs
docker-compose -f docker-compose.prod.yml logs frontend

# Verify backend connectivity
curl http://localhost:8000/api/health
```

### Performance Tuning

**Increase backend workers:**
```yaml
# In docker-compose.prod.yml
command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Database optimization:**
```yaml
environment:
  - POSTGRES_SHARED_BUFFERS=256MB
  - POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
```

## 🔄 Updates and Maintenance

### Application Updates

1. Pull latest code
2. Rebuild containers: `docker-compose -f docker-compose.prod.yml build --no-cache`
3. Rolling update: `docker-compose -f docker-compose.prod.yml up -d`

### Container Cleanup

```bash
# Remove unused containers
docker system prune

# Remove unused volumes
docker volume prune

# Remove unused images
docker image prune -a
```

## 📞 Support

For issues and questions:
1. Check application logs
2. Verify environment configuration
3. Review Docker container status
4. Check network connectivity between services