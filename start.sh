#!/bin/bash
# Railway startup script for Vocelio AI Backend
# Minimal dependencies approach

echo "🚀 Starting Vocelio AI Backend deployment..."

# Check Python availability
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "✅ Using Python 3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Using Python 3"
else
    echo "❌ No Python found!"
    exit 1
fi

# Show Python and pip versions
echo "🔍 Python version:"
$PYTHON_CMD --version

echo "🔍 pip version:"
$PYTHON_CMD -m pip --version

# Install minimal requirements
echo "📦 Installing minimal FastAPI dependencies..."
$PYTHON_CMD -m pip install fastapi==0.104.1 uvicorn==0.24.0 pydantic==2.5.0

# Verify installation
echo "✅ Verifying installation..."
$PYTHON_CMD -c "import fastapi, uvicorn, pydantic; print('All dependencies installed successfully')"

# Start the application
echo "🎯 Starting FastAPI application..."
cd apps/api-gateway || exit 1
$PYTHON_CMD -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
