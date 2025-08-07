#!/bin/bash

# 🔍 Phase 1 Services Health Check
# Update the URLs below with your actual Railway URLs

echo "🔍 Testing Phase 1 Core Services..."
echo "=================================="

# UPDATE THESE URLS WITH YOUR ACTUAL RAILWAY URLS
services=(
    "Overview:https://vocelio-ai-backend-production.up.railway.app"
    "API-Gateway:UPDATE_WITH_YOUR_URL"
    "Agents:UPDATE_WITH_YOUR_URL"
    "AI-Brain:UPDATE_WITH_YOUR_URL"
    "Call-Center:UPDATE_WITH_YOUR_URL"
    "Integrations:UPDATE_WITH_YOUR_URL"
)

passed=0
total=6

echo ""
for service in "${services[@]}"; do
    IFS=':' read -r name url <<< "$service"
    
    if [[ "$url" == "UPDATE_WITH_YOUR_URL" ]]; then
        echo "⏳ $name: Please update URL in script"
        continue
    fi
    
    echo -n "Testing $name... "
    
    if curl -s "$url/health" > /dev/null 2>&1; then
        echo "✅ HEALTHY"
        ((passed++))
    else
        echo "❌ FAILED"
    fi
done

echo ""
echo "📊 Results: $passed/$total services healthy"

if [ $passed -eq $total ]; then
    echo "🎉 Phase 1 COMPLETE! All core services operational!"
else
    echo "⚠️  Some services need attention. Check Railway logs."
fi

echo ""
echo "🔗 Next: Deploy Phase 2 Business Services (10 more services)"
