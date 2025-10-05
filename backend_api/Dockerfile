# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project (since backend needs parent directories)
COPY . .

# Install Python dependencies from backend requirements
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r backend_api/requirements.txt

# Set working directory to backend_api
WORKDIR /app/backend_api

# Create necessary directories
RUN mkdir -p /app/logs

# Expose port (Render uses dynamic port)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application (Render provides PORT environment variable)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]