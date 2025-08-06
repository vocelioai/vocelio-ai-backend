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
# Test with simple Python HTTP server with debugging
CMD sh -c "echo 'Container started!' && pwd && ls -la && echo 'Looking for simple_server.py:' && ls -la simple_server.py && echo 'Starting Python server...' && python simple_server.py"
