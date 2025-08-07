#!/bin/bash

# 🚀 Fix and Deploy All Services Script
# Creates correct Procfiles and deploys all 24 remaining services

echo "🚀 Fixing and deploying all 24 services..."
echo "============================================"

# Services list with their directories
services=(
    "agents"
    "ai-brain"
    "call-center"
    "integrations"
    "knowledge-base"
    "voice-lab"
    "notifications"
    "phone-numbers"
    "analytics-pro"
    "team-hub"
    "webhooks"
    "lead-management"
    "scheduling"
    "smart-campaigns"
    "billing-pro"
    "compliance"
    "flow-builder"
    "voice-marketplace"
    "developer-api"
    "agent-store"
    "scripts"
    "settings"
    "white-label"
)

# Ports for each service
declare -A service_ports=(
    ["agents"]="8002"
    ["ai-brain"]="8003"
    ["call-center"]="8004"
    ["integrations"]="8005"
    ["knowledge-base"]="8006"
    ["voice-lab"]="8007"
    ["notifications"]="8009"
    ["phone-numbers"]="8010"
    ["analytics-pro"]="8011"
    ["team-hub"]="8012"
    ["webhooks"]="8013"
    ["lead-management"]="8014"
    ["scheduling"]="8016"
    ["smart-campaigns"]="8018"
    ["billing-pro"]="8019"
    ["compliance"]="8020"
    ["flow-builder"]="8021"
    ["voice-marketplace"]="8024"
    ["developer-api"]="8008"
    ["agent-store"]="8023"
    ["scripts"]="8015"
    ["settings"]="8017"
    ["white-label"]="8022"
)

cd apps

for service in "${services[@]}"; do
    echo ""
    echo "📦 Processing $service..."
    
    if [ -d "$service" ]; then
        cd "$service"
        
        # Create Procfile
        echo "web: python railway_start.py" > Procfile
        echo "   ✅ Created Procfile"
        
        # Deploy
        echo "   🚀 Deploying..."
        railway up --detach
        
        # Set environment variables
        port=${service_ports[$service]}
        railway variables --set "PORT=$port" --set "PYTHONPATH=/app" --set "ENVIRONMENT=production"
        echo "   ✅ Set environment variables (PORT=$port)"
        
        cd ..
    else
        echo "   ❌ Directory not found: $service"
    fi
    
    # Brief pause between deployments
    sleep 3
done

echo ""
echo "🎉 All services processed!"
echo "========================="
echo ""
echo "🔍 Checking deployment status..."

# Wait a bit for deployments to start
sleep 10

echo "🌐 Getting service URLs..."
for service in "${services[@]}"; do
    if [ -d "apps/$service" ]; then
        cd "apps/$service"
        url=$(railway domain 2>/dev/null || echo "Deploying...")
        echo "$service: $url"
        cd ../..
    fi
done

echo ""
echo "🎯 Next: Test all service health endpoints!"
