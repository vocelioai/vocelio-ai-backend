FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-pip \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the project structure
COPY ../../apps /app/apps
COPY ../../shared /app/shared

# Copy requirements and install Python dependencies
COPY apps/voice-marketplace/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8020

# Run the voice-marketplace service
CMD ["python", "-m", "apps.voice-marketplace.src.main"]
