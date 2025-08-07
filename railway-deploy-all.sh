# Railway Deployment Configuration Generator
# This script creates optimized Dockerfiles for each service

# Service configurations with ports and dependencies
SERVICES=(
    "api-gateway:8000:main"
    "agents:8001:main" 
    "ai-brain:8002:main"
    "analytics-pro:8003:main"
    "billing-pro:8004:main"
    "call-center:8005:main"
    "compliance:8006:main"
    "flow-builder:8007:main"
    "developer-api:8008:main"
    "knowledge-base:8009:main"
    "integrations:8010:main"
    "lead-management:8011:main"
    "notifications:8012:main"
    "scheduling:8013:main"
    "phone-numbers:8014:main"
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
