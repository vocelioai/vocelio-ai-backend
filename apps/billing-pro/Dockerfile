FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-pip \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy all source code
COPY ../../apps /app/apps
COPY ../../shared /app/shared

# Copy requirements and install dependencies
COPY apps/billing-pro/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8006

# Run the application
CMD ["python", "-m", "apps.billing-pro.src.main"]
