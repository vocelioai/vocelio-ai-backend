#!/bin/bash

# 🚀 Railway Deployment Automation Script
# Deploys all 25 Vocelio AI Call Center services to Railway

echo "🚀 Deploying World-Class AI Call Center to Railway"
echo "=================================================="
echo "Target: 25 microservices across 3 deployment phases"
echo ""

# Current 25 services with correct ports
SERVICES=(
    "1-api-gateway:8001:API Gateway - Main entry point and routing"
    "2-agents:8002:AI Agents - Intelligent call handling"
    "3-ai-brain:8003:AI Brain - Core AI processing engine"
    "4-call-center:8004:Call Center - Voice communication hub"
    "5-integrations:8005:Integrations - External system connections"
    "6-analytics:8006:Analytics - Call performance metrics"
    "7-appointments:8007:Appointments - Scheduling management"
    "8-developer-api:8008:Developer API - Third-party integration"
    "9-notifications:8009:Notifications - Real-time alerts"
    "10-pricing:8010:Pricing - Dynamic pricing engine"
    "11-queue-management:8011:Queue Management - Call queue optimization"
    "12-reports:8012:Reports - Business intelligence"
    "13-user-management:8013:User Management - Account administration"
    "14-workflows:8014:Workflows - Process automation"
    "15-scripts:8015:Scripts - Call script management"
    "scripts:8015:main"
    "smart-campaigns:8016:main"
    "settings:8017:main"
    "team-hub:8018:main"
    "voice-lab:8019:main"
    "overview:8020:main"
    "voice-marketplace:8021:main"
    "white-label:8022:main"
    "agent-store:8023:main"
    "webhooks:8024:main"
)

# Priority deployment order
PRIORITY_ORDER=(
    "api-gateway"     # 1. Main entry point
    "agents"          # 2. Core agent management
    "ai-brain"        # 3. AI processing engine
    "call-center"     # 4. Call operations
    "integrations"    # 5. External APIs
    "scheduling"      # 6. Calendar integration
    "notifications"   # 7. Alert system
    "webhooks"        # 8. Event handling
    "developer-api"   # 9. API management
    "knowledge-base"  # 10. Knowledge system
)

# Railway deployment commands for each service
echo "Railway Deployment Commands:"
echo "==========================="

for service in "${SERVICES[@]}"; do
    IFS=':' read -r name port entry <<< "$service"
    echo ""
    echo "# Deploy $name service"
    echo "railway service create $name"
    echo "railway service connect $name"
    echo "railway up --service $name"
    echo "railway env set PORT=$port --service $name"
done
