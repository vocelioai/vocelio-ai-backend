#!/bin/bash

# 🔍 Phase 1 Services Health Check
# Tests the 5 core services deployed to Railway

echo "🔍 Testing Phase 1 Core Services on Railway..."
echo "========================================"

# Phase 1: Core Services (5 services)
phase1_services=(
    "Overview:https://vocelio-ai-backend-production.up.railway.app"
    "API-Gateway:TBD"
    "Agents:TBD"
    "AI-Brain:TBD"
    "Call-Center:TBD"
    "Integrations:TBD"
)

phase1_passed=0
phase1_total=6

echo ""
echo "🎯 Phase 1: Core Services"
echo "========================"

for service in "${phase1_services[@]}"; do
    IFS=':' read -r name url <<< "$service"
    
    if [[ "$url" == "TBD" ]]; then
        echo "⏳ $name: Pending deployment"
        continue
    fi
    
    echo -n "Testing $name... "
    
    if curl -s "$url/health" > /dev/null 2>&1; then
        echo "✅ HEALTHY"
        ((phase1_passed++))
    else
        echo "❌ FAILED"
    fi
done

echo ""
echo "📊 Phase 1 Results: $phase1_passed/$phase1_total services healthy"

if [ $phase1_passed -eq $phase1_total ]; then
    echo "🎉 Phase 1 COMPLETE! Ready for Phase 2"
else
    echo "⚠️  Phase 1 incomplete. Deploy remaining services."
fi

echo ""
echo "🔗 Next Steps:"
echo "1. Update this script with actual Railway URLs"
echo "2. Complete Phase 1 deployment (5 more services)"
echo "3. Proceed to Phase 2: Business Services (10 services)"
echo "4. Proceed to Phase 3: Advanced Services (9 services)"
