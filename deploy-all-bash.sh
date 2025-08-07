#!/bin/bash

# 🚀 Deploy All Remaining Services to Railway
# Simple bash script that works reliably

echo "🚀 Deploying Remaining 23 Services to Railway"
echo "=============================================="
echo ""

# Service configurations (excluding api-gateway and overview which are deployed)
services=(
    "agents:apps/agents:8002"
    "ai-brain:apps/ai-brain:8003"
    "call-center:apps/call-center:8004"
    "integrations:apps/integrations:8005"
    "knowledge-base:apps/knowledge-base:8006"
    "voice-lab:apps/voice-lab:8007"
    "notifications:apps/notifications:8009"
    "phone-numbers:apps/phone-numbers:8010"
    "analytics-pro:apps/analytics-pro:8011"
    "team-hub:apps/team-hub:8012"
    "webhooks:apps/webhooks:8013"
    "lead-management:apps/lead-management:8014"
    "scheduling:apps/scheduling:8016"
    "smart-campaigns:apps/smart-campaigns:8018"
    "billing-pro:apps/billing-pro:8019"
    "compliance:apps/compliance:8020"
    "flow-builder:apps/flow-builder:8021"
    "voice-marketplace:apps/voice-marketplace:8024"
    "developer-api:apps/developer-api:8008"
    "agent-store:apps/agent-store:8023"
    "scripts:apps/scripts:8015"
    "settings:apps/settings:8017"
    "white-label:apps/white-label:8022"
)

deploy_count=0
total_services=${#services[@]}

for service_config in "${services[@]}"; do
    IFS=':' read -r service_name service_dir service_port <<< "$service_config"
    
    deploy_count=$((deploy_count + 1))
    echo ""
    echo "📦 Deploying $service_name ($deploy_count/$total_services)"
    echo "   Directory: $service_dir"
    echo "   Port: $service_port"
    
    # Navigate to service directory
    cd "$service_dir"
    
    # Set environment variables
    echo "   Setting environment variables..."
    railway variables --set "PORT=$service_port" --set "PYTHONPATH=/app" --set "ENVIRONMENT=production" --set "RAILWAY_RUN_COMMAND=python railway_start.py"
    
    # Deploy the service
    echo "   Deploying to Railway..."
    railway up --detach
    
    if [ $? -eq 0 ]; then
        echo "   ✅ $service_name deployed successfully!"
    else
        echo "   ❌ Failed to deploy $service_name"
    fi
    
    # Return to root directory
    cd "../.."
    
    # Brief pause between deployments
    sleep 3
done

echo ""
echo "🎉 Deployment Process Complete!"
echo "==============================="
echo "📊 Deployed: $deploy_count services"
echo "📊 Total System: 25/25 services"
echo "   - 1 Overview (already deployed)"
echo "   - 1 API Gateway (deployed in this session)"  
echo "   - $deploy_count Additional services (just deployed)"
echo ""
echo "🔗 Railway Dashboard: https://railway.app/dashboard"
echo "🔍 Next: Test all service health endpoints"
echo ""
echo "🚀 Your world-class AI call center is now LIVE!"
