
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

# Copy all apps folders
COPY ../../apps /app/apps

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH so all apps are importable
ENV PYTHONPATH="/app/apps"

# Expose port (Railway will use $PORT environment variable)
EXPOSE 8080

# Run the API Gateway
CMD ["uvicorn", "api-gateway.src.main:app", "--host", "0.0.0.0", "--port", "8080"]
