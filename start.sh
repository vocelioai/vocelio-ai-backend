#!/bin/bash
# Railway startup script for Vocelio AI Backend
# Fixed for Nix externally-managed Python environment

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

# Check if pip is available (should be with Nix python311Packages.pip)
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "❌ pip not available with $PYTHON_CMD"
    exit 1
fi

echo "✅ pip is available"

# Install requirements directly (no pip upgrade needed in Nix)
echo "📦 Installing Python packages..."
$PYTHON_CMD -m pip install -r requirements.txt

# Start the application
echo "🎯 Starting FastAPI application..."
cd apps/api-gateway
$PYTHON_CMD -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
