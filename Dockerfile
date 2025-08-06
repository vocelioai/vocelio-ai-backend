# Vocelio AI Backend Dockerfile
# Simple Python FastAPI deployment - Direct uvicorn startup

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-pip \
    libpq-dev \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change to API Gateway directory (not src subdirectory)
WORKDIR /app/apps/api-gateway

# Expose port (Railway will use $PORT environment variable)
EXPOSE 8000
# Start with minimal test application
CMD sh -c "echo 'Starting in directory:' && pwd && echo 'Files present:' && ls -la src/ && echo 'Testing with minimal app...' && uvicorn src.test_main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level debug"
