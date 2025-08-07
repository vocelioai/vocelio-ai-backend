# Smart Campaigns Service Dockerfile
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

# Copy all apps and shared folders
COPY ../../apps /app/apps
COPY ../../shared /app/shared

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH so all apps and shared modules are importable
ENV PYTHONPATH="/app"

# Expose port
EXPOSE 8003

# Run the Smart Campaigns Service
CMD ["uvicorn", "apps.smart-campaigns.src.main:app", "--host", "0.0.0.0", "--port", "8003"]