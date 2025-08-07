FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    gcc \
    python3-pip \
    libpq-dev \
    python3-dev \
    libsndfile1 \
    libsndfile1-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy the project structure
COPY ../../apps /app/apps
COPY ../../shared /app/shared

# Copy requirements and install Python dependencies
COPY apps/voice-lab/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8015

# Run the voice-lab service
CMD ["python", "-m", "apps.voice-lab.src.main"]
