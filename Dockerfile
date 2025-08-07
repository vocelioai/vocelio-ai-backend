# Vocelio AI Microservice - Fixed uvicorn execution
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

# Install Python dependencies with explicit upgrade
RUN python3.11 -m pip install --upgrade pip && \
    python3.11 -m pip install --no-cache-dir -r requirements.txt && \
    python3.11 -m pip install uvicorn[standard]==0.24.0 fastapi==0.104.1

# Copy application code
COPY . .

# Change to Overview service directory
WORKDIR /app/apps/overview

# Expose port (Railway will use $PORT environment variable)
EXPOSE 8001

# Create a startup script to handle environment variables
RUN echo '#!/bin/bash\nport=${PORT:-8001}\nexport PYTHONPATH=/app:$PYTHONPATH\npython3.11 -m uvicorn src.main:app --host 0.0.0.0 --port $port' > /start.sh && chmod +x /start.sh

# Run the microservice
CMD ["/start.sh"]
