#!/bin/bash
# Railway startup script - handles dynamic PORT environment variable
set -e

# Debug information
echo "Starting Vocelio API Gateway..."
echo "Working directory: $(pwd)"
echo "Port: ${PORT:-8000}"
echo "Python version: $(python --version)"

# Set port with fallback
PORT=${PORT:-8000}

# Start the application
echo "Starting uvicorn server on port $PORT..."
exec uvicorn src.main:app --host 0.0.0.0 --port $PORT
