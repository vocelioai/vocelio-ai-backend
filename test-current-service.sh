#!/bin/bash

# 🔍 Test Railway Service Health
# Tests the current Railway deployment

echo "🔍 Testing Railway Service Health..."
echo "=================================="

SERVICE_URL="https://vocelio-ai-backend-production.up.railway.app"

echo ""
echo "🌐 Testing: $SERVICE_URL"
echo ""

# Test health endpoint
echo -n "Testing /health endpoint... "
if curl -s "$SERVICE_URL/health" > /dev/null 2>&1; then
    echo "✅ RESPONDING"
    echo ""
    echo "📋 Health Response:"
    curl -s "$SERVICE_URL/health" | python -m json.tool
else
    echo "❌ NOT RESPONDING"
    echo ""
    echo "🔍 Trying basic connection..."
    curl -v "$SERVICE_URL" 2>&1 | head -10
fi

echo ""
echo "🎯 If health endpoint works, the service is operational!"
echo "🔗 Service URL: $SERVICE_URL"
