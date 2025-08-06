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
# Copy startup script
COPY apps/api-gateway/start.py /app/apps/api-gateway/start.py

# Start the application using Python startup script
CMD ["python", "start.py"]
