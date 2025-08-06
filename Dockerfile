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

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 8080

# Run FastAPI app with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
