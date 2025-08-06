#!/bin/bash
# start.sh - Railway startup script

echo "🚀 Starting Vocelio API Gateway on Railway..."
echo "📍 Current directory: $(pwd)"
echo "🔌 PORT: $PORT"
echo "🌍 RAILWAY_ENVIRONMENT: $RAILWAY_ENVIRONMENT"

# List files to debug
echo "📁 Files in current directory:"
ls -la

# Try to find and run the Python app
if [ -f "railway_app.py" ]; then
    echo "✅ Found railway_app.py - starting..."
    python railway_app.py
elif [ -f "railway_simple.py" ]; then
    echo "✅ Found railway_simple.py - starting..."
    python railway_simple.py
elif [ -f "apps/api-gateway/railway_app.py" ]; then
    echo "✅ Found railway_app.py in apps/api-gateway - starting..."
    cd apps/api-gateway
    python railway_app.py
elif [ -f "src/minimal_test.py" ]; then
    echo "✅ Found src/minimal_test.py - starting..."
    python -m src.minimal_test
else
    echo "❌ No suitable Python file found!"
    echo "📁 Directory contents:"
    find . -name "*.py" -type f
    exit 1
fi
