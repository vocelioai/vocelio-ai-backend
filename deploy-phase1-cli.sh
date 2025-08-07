#!/bin/bash

# 🚀 Railway Phase 1 Services Deployment Script
# Deploy 5 core services to Railway via CLI (alternative to Dashboard)

echo "🚀 Deploying Phase 1 Core Services to Railway..."
echo "=============================================="

# Service configurations
services=(
    "1-api-gateway:api-gateway:8001"
    "2-agents:agents:8002"
    "3-ai-brain:ai-brain:8003"
    "4-call-center:call-center:8004"
    "5-integrations:integrations:8005"
)

deployed_urls=()

echo ""
echo "🎯 Phase 1: Deploying 5 Core Services"
echo "===================================="

for service_config in "${services[@]}"; do
    IFS=':' read -r directory service_name port <<< "$service_config"
    
    echo ""
    echo "📦 Deploying $service_name from $directory..."
    echo "   Port: $port"
    
    # Create service via Railway CLI
    echo "   Creating Railway service..."
    railway service create "$service_name"
    
    # Deploy the service
    echo "   Deploying from directory: $directory"
    cd "$directory"
    
    # Set environment variables
    railway variables set PORT="$port"
    railway variables set PYTHONPATH="/app"
    railway variables set ENVIRONMENT="production"
    
    # Deploy
    railway up
    
    # Get the service URL
    service_url=$(railway domain)
    deployed_urls+=("$service_name:$service_url")
    
    echo "   ✅ Deployed: $service_url"
    
    cd ..
done

echo ""
echo "🎉 Phase 1 Deployment Complete!"
echo "==============================="

echo ""
echo "📋 Deployed Services:"
for url_config in "${deployed_urls[@]}"; do
    IFS=':' read -r name url <<< "$url_config"
    echo "   $name: $url"
done

echo ""
echo "🔍 Testing all services..."
echo "========================="

all_healthy=true

# Test Overview service (already deployed)
echo -n "Testing Overview... "
if curl -s "https://vocelio-ai-backend-production.up.railway.app/health" > /dev/null 2>&1; then
    echo "✅ HEALTHY"
else
    echo "❌ FAILED"
    all_healthy=false
fi

# Test newly deployed services
for url_config in "${deployed_urls[@]}"; do
    IFS=':' read -r name url <<< "$url_config"
    echo -n "Testing $name... "
    
    if curl -s "$url/health" > /dev/null 2>&1; then
        echo "✅ HEALTHY"
    else
        echo "❌ FAILED"
        all_healthy=false
    fi
done

echo ""
if [ "$all_healthy" = true ]; then
    echo "🎉 ALL PHASE 1 SERVICES HEALTHY!"
    echo "Ready to proceed to Phase 2: Business Services"
else
    echo "⚠️  Some services failed health check"
    echo "Please check Railway logs and redeploy failed services"
fi

echo ""
echo "🔗 Next Steps:"
echo "1. Verify all services in Railway Dashboard"
echo "2. Update service URLs in deployment checklist"
echo "3. Proceed to Phase 2: Business Services (10 services)"
echo "4. Complete full system deployment (25 services total)"
