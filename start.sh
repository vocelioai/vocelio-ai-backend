#!/bin/bash
# Railway startup script for Vocelio AI Backend
# Ensures Python and pip are available

echo "🚀 Starting Vocelio AI Backend deployment..."

# Check if python3.11 is available
if command -v python3.11 &> /dev/null; then
    echo "✅ Python 3.11 found"
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    echo "✅ Python 3 found"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    echo "✅ Python found"
    PYTHON_CMD="python"
else
    echo "❌ No Python interpreter found!"
    exit 1
fi

# Ensure pip is available
echo "🔧 Ensuring pip is available..."
$PYTHON_CMD -m ensurepip --upgrade 2>/dev/null || echo "pip already available"

# Upgrade pip
echo "⬆️ Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip

# Install requirements
echo "📦 Installing Python packages..."
$PYTHON_CMD -m pip install -r requirements.txt

# Start the application
echo "🎯 Starting FastAPI application..."
cd apps/api-gateway
$PYTHON_CMD -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
